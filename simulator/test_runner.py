"""Test runner that uses Flask test clients to issue directives and trigger processing."""

import json
from fastapi.testclient import TestClient
from simulator.controller_app import app as controller_app
from simulator.worker_app import app as worker_app


def run_test():
    store = 'simulator/event_store.ndjson'
    open(store, 'w').close()
    with TestClient(controller_app) as c, TestClient(worker_app) as w:
        # issue a few directives
        for i in range(4):
            rv = c.post('/issue', json={'agent_id': i, 'seq': 0, 'amount_target': 10})
            print('issue:', rv.json())

        # find pubkey from last issued directive
        with open(store) as f:
            last = None
            for line in f:
                try:
                    rec = json.loads(line)
                    ev = rec.get('event') if isinstance(rec, dict) and 'event' in rec else rec
                    if isinstance(ev, dict) and ev.get('type') == 'directive':
                        last = ev
                except Exception:
                    continue
        pub = last.get('pubkey')
        rv = w.post('/process', json={'pubkey': pub})
        print('process:', rv.json())


if __name__ == '__main__':
    run_test()
