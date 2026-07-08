#!/usr/bin/env python3
"""Worker simulator that reads directives from a controller and verifies signatures before execution."""

import argparse
import json
import time
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PublicKey

from event_store import append_event, read_events


def process_event_store(path: str, pubkey_hex: str):
    events = read_events(path)
    # iterate and process directives; support both chained-records and legacy event dicts
    for rec in events:
        # rec may be a chained record with key 'event' or the raw event itself
        if isinstance(rec, dict) and "event" in rec:
            ev = rec.get("event")
        else:
            ev = rec
        if not isinstance(ev, dict) or ev.get("type") != "directive":
            continue
        directive = ev.get("directive")
        sig_hex = ev.get("signature")
        sig = bytes.fromhex(sig_hex)
        pub = Ed25519PublicKey.from_public_bytes(bytes.fromhex(pubkey_hex))
        payload = json.dumps(directive, sort_keys=True).encode()
        try:
            pub.verify(sig, payload)
            # append execution event
            result = {"agent": directive.get("agent_id"), "status": "executed", "directive": directive, "ts": time.time()}
            append_event(path, {"type": "execution", "result": result})
        except Exception as e:
            result = {"agent": directive.get("agent_id"), "status": "rejected", "error": str(e), "ts": time.time()}
            append_event(path, {"type": "execution", "result": result})


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--store", type=str, default="simulator/event_store.ndjson")
    parser.add_argument("--pub", type=str, required=True, help="Controller public key hex")
    args = parser.parse_args()
    process_event_store(args.store, args.pub)


if __name__ == "__main__":
    main()
