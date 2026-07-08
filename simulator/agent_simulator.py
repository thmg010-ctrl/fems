#!/usr/bin/env python3
"""Simple safe simulator for the agent network.

This simulator models agents producing profit (simulated), promotions, and decommissioning.
It does not interact with any real financial system and is intended for design and testing only.
"""

import argparse
import json
import random
import time
from dataclasses import dataclass, asdict


@dataclass
class Agent:
    id: int
    tier: int = 0
    total_profit: float = 0.0
    compliance_score: float = 1.0
    consecutive_failures: int = 0


def simulate(num_agents: int, steps: int, seed: int = None):
    if seed is not None:
        random.seed(seed)
    agents = [Agent(id=i) for i in range(num_agents)]
    logs = []

    for step in range(steps):
        for a in agents[:]:
            # Simulate profit: normal distribution scaled by tier
            base = random.gauss(1.0 + 0.2 * a.tier, 2.0)
            profit = max(0.0, base)
            # Compliance fluctuation
            a.compliance_score = max(0.0, min(1.0, a.compliance_score + random.uniform(-0.05, 0.02)))
            # Apply profit
            a.total_profit += profit
            if profit < 0.5:
                a.consecutive_failures += 1
            else:
                a.consecutive_failures = 0

            # Promotion
            if a.total_profit > 50.0 * (a.tier + 1) and a.compliance_score > 0.7:
                old = a.tier
                a.tier += 1
                logs.append({"event": "promote", "agent": a.id, "from": old, "to": a.tier, "step": step})

            # Decommission
            if a.consecutive_failures >= 5:
                logs.append({"event": "decommission", "agent": a.id, "tier": a.tier, "step": step})
                agents.remove(a)

        # Sample global summary
        if step % 10 == 0:
            summary = {"step": step, "active_agents": len(agents), "avg_tier": sum(x.tier for x in agents) / max(1, len(agents))}
            logs.append({"event": "summary", "data": summary})

    return agents, logs


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--agents", type=int, default=100, help="Number of agents to simulate")
    parser.add_argument("--steps", type=int, default=100, help="Simulation steps")
    parser.add_argument("--seed", type=int, default=42, help="Random seed")
    parser.add_argument("--out", type=str, default="sim_output.json", help="Output file")
    args = parser.parse_args()

    agents, logs = simulate(args.agents, args.steps, seed=args.seed)
    out = {"agents": [asdict(a) for a in agents], "logs": logs}
    with open(args.out, "w") as f:
        json.dump(out, f, indent=2)
    print(f"Simulation complete — {len(agents)} agents active. Output: {args.out}")


if __name__ == "__main__":
    main()
