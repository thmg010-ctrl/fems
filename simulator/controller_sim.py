#!/usr/bin/env python3
"""Controller simulator: issues signed directives to agents and records events.

Safe, local-only simulation — no real financial integrations.
"""

import argparse
import json
import time
from dataclasses import dataclass, asdict
from typing import List

from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey, Ed25519PublicKey
from cryptography.hazmat.primitives import serialization
from event_store import append_event


@dataclass
class Agent:
    id: int
    tier: int = 0

    def verify_and_execute(self, directive: dict, signature: bytes, pubkey_bytes: bytes):
        # Verify signature
        pub = Ed25519PublicKey.from_public_bytes(pubkey_bytes)
        payload = json.dumps(directive, sort_keys=True).encode()
        try:
            pub.verify(signature, payload)
            # Simulate execution
            result = {"agent": self.id, "status": "executed", "directive": directive}
            return True, result
        except Exception as e:
            return False, {"agent": self.id, "status": "rejected", "error": str(e)}


class Controller:
    def __init__(self):
        self._key = Ed25519PrivateKey.generate()
        self.pub = self._key.public_key()

    def sign_directive(self, directive: dict) -> bytes:
        payload = json.dumps(directive, sort_keys=True).encode()
        sig = self._key.sign(payload)
        return sig

    def pubkey_bytes(self) -> bytes:
        return self.pub.public_bytes(encoding=serialization.Encoding.Raw, format=serialization.PublicFormat.Raw)


def append_event(path: str, event: dict):
    with open(path, "a") as f:
        f.write(json.dumps(event) + "\n")


def run_sim(num_agents: int, directives_per_agent: int, out: str):
    controller = Controller()
    agents: List[Agent] = [Agent(id=i) for i in range(num_agents)]
    pubbytes = controller.pubkey_bytes()

    for a in agents:
        for d in range(directives_per_agent):
            directive = {"agent_id": a.id, "task": "generate_profit", "amount_target": 10 * (a.tier + 1), "nonce": int(time.time()*1000), "seq": d}
            sig = controller.sign_directive(directive)
            # Append signed directive to event store (immutable chain)
            event = {"type": "directive", "directive": directive, "signature": sig.hex(), "pubkey": pubbytes.hex(), "ts": time.time()}
            chain_hash = append_event(out, event)

            # local verify (simulate worker)
            valid, res = a.verify_and_execute(directive, sig, pubbytes)
            res_event = {"type": "execution", "result": res, "ts": time.time()}
            append_event(out, res_event)

    print(f"Controller simulation complete — events appended to {out}")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--agents", type=int, default=10)
    parser.add_argument("--per", type=int, default=2)
    parser.add_argument("--out", type=str, default="event_store.ndjson")
    args = parser.parse_args()
    run_sim(args.agents, args.per, args.out)


if __name__ == "__main__":
    main()
