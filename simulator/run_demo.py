#!/usr/bin/env python3
"""Run a demo: controller issues directives, then worker processes them end-to-end."""

import json
import subprocess
import sys
import time


def find_pubkey_from_store(path):
    with open(path) as f:
        for line in f:
            try:
                rec = json.loads(line)
                # Support both chained records and raw events
                ev = rec.get("event") if isinstance(rec, dict) and "event" in rec else rec
                if isinstance(ev, dict) and ev.get("type") == "directive":
                    return ev.get("pubkey")
            except Exception:
                continue
    return None


def main():
    store = "simulator/event_store.ndjson"
    # clear store
    open(store, "w").close()
    # run controller
    subprocess.check_call([sys.executable, "simulator/controller_sim.py", "--agents", "6", "--per", "2", "--out", store])
    time.sleep(0.2)
    pub = find_pubkey_from_store(store)
    if not pub:
        print("Could not find pubkey in event store")
        return 1
    # run worker
    subprocess.check_call([sys.executable, "simulator/worker_sim.py", "--store", store, "--pub", pub])
    print("Demo complete. Event store:", store)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
