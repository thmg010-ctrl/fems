#!/usr/bin/env python3
"""Start controller and worker locally (no Docker), issue directives, and process them.

Uses only Python stdlib so it runs on machines without Docker.
"""

import subprocess
import sys
import time
import json
import urllib.request
import urllib.error

CONTROLLER_URL = 'http://127.0.0.1:8000'
WORKER_URL = 'http://127.0.0.1:8001'
# Prefer SQLite-backed store when EVENT_DB is set; otherwise fall back to NDJSON.
import os
STORE = os.getenv('EVENT_DB', 'simulator/event_store.ndjson')


def wait_for(url, timeout=10.0):
    start = time.time()
    while time.time() - start < timeout:
        try:
            req = urllib.request.Request(url)
            with urllib.request.urlopen(req, timeout=1) as resp:
                return True
        except Exception as e:
            # If server responds with HTTP error (e.g., 404), treat as up.
            from urllib.error import HTTPError
            if isinstance(e, HTTPError):
                return True
            # Otherwise (connection refused, timeout), keep waiting
            time.sleep(0.2)
    return False


def post_json(url, data):
    b = json.dumps(data).encode()
    req = urllib.request.Request(url, data=b, headers={"Content-Type": "application/json"}, method='POST')
    with urllib.request.urlopen(req, timeout=5) as resp:
        return json.load(resp)


def main():
    # ensure simulator dir and SQLite DB exist when using DB
    os.makedirs('simulator', exist_ok=True)
    if STORE.endswith('.db'):
        # ensure DB file exists
        open(STORE, 'a').close()
    else:
        # clear event store (ndjson)
        open(STORE, 'w').close()

    ctrl = subprocess.Popen([sys.executable, 'simulator/controller_app.py'], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    worker = subprocess.Popen([sys.executable, 'simulator/worker_app.py'], stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    try:
        if not wait_for(CONTROLLER_URL):
            print('Controller did not start in time')
            return 1
        if not wait_for(WORKER_URL):
            print('Worker did not start in time')
            return 1

        # issue directives
        pubkey = None
        for i in range(6):
            res = post_json(CONTROLLER_URL + '/issue', {'agent_id': i, 'seq': 0, 'amount_target': 10})
            print('issued', res.get('directive'))
            pubkey = res.get('pubkey') or pubkey

        # process
        res = post_json(WORKER_URL + '/process', {'pubkey': pubkey})
        print('processed', res)
        return 0
    finally:
        for p in (ctrl, worker):
            if p.poll() is None:
                p.terminate()
                try:
                    p.wait(timeout=2)
                except Exception:
                    p.kill()


if __name__ == '__main__':
    raise SystemExit(main())
