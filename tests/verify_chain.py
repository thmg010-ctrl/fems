#!/usr/bin/env python3
"""Verify the chained event store integrity.

Reads `simulator/event_store.ndjson` and verifies each record's `chain_hash`
matches the SHA-256 of `{prev, event}` as used by `simulator/event_store.py`.
"""

import sys
import json
import hashlib


def _hash_event(event: dict, prev_hash: str | None) -> str:
    payload = json.dumps({"prev": prev_hash, "event": event}, sort_keys=True).encode()
    return hashlib.sha256(payload).hexdigest()


def read_records(path: str):
    out = []
    with open(path) as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                out.append(json.loads(line))
            except Exception:
                continue
    return out


def verify(path: str) -> int:
    records = read_records(path)
    last_hash = None
    checked = 0
    for i, rec in enumerate(records):
        if isinstance(rec, dict) and 'chain_hash' in rec:
            chain_hash = rec.get('chain_hash')
            prev_hash = rec.get('prev_hash')
            event = rec.get('event')
        else:
            # skip legacy or malformed records
            continue

        if prev_hash != last_hash:
            print(f"Broken prev link at index {i}: expected prev {last_hash!r}, got {prev_hash!r}")
            return 2

        computed = _hash_event(event, prev_hash)
        if computed != chain_hash:
            print(f"Hash mismatch at index {i}: computed {computed}, recorded {chain_hash}")
            return 3

        last_hash = chain_hash
        checked += 1

    print(f"Chain verification passed: {checked} chained records checked.")
    return 0


if __name__ == '__main__':
    path = 'simulator/event_store.ndjson'
    sys.exit(verify(path))
