Technical Architecture — High Level

Components
- Controller Plane: top-tier agents + schedulers that assign tasks and manage promotions.
- Worker Plane: large pools of stateless, ephemeral agents executing tasks.
- Control Services: identity, compliance, payments (simulated in this repo), telemetry, and event store.

Deployment
- Containerized agents on Kubernetes or Fargate-like platforms.
- Horizontal sharding of controllers and workers; regional deployment for latency and regulatory reasons.

Scalability
- Phased rollout with simulation testing (see simulator) before production scale.
- Autoscaling based on profit-per-agent and cost thresholds.

Security & Identity
- Cryptographic identities for agents; signed task directives and role-based access control.
