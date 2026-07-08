FEMS — Design artifacts for the Utonomous Profit Network

This workspace contains design documents and a safe local simulator (no real financial integrations).

Quickstart
----------
Run the simulator locally (Python 3.10+):

```bash
python3 simulator/agent_simulator.py --agents 200 --steps 200 --out sim_output.json
```

Files of interest
- `docs/specification.md` — core refined specification
- `docs/compliance_checklist.md` — compliance controls
- `architecture/architecture.md` — architecture overview
- `security/security.md` — security, logging and auditing notes
- `simulator/agent_simulator.py` — safe local simulation tool

Docker / HTTP prototype
----------------------
You can run the minimal HTTP prototype (controller + worker) in-process or via Docker Compose.

In-process (no Docker):

```bash
python3 -m pip install -r requirements.txt --user
python3 simulator/test_runner.py
```

With Docker Compose (requires Docker):

```bash
docker compose build
docker compose up --build
```

Controller API: `POST /issue` on port 8000 — returns issued directive and `pubkey`.
Worker API: `POST /process` on port 8001 — accepts JSON `{ "pubkey": "<controller_pubhex>" }` to validate and process directives.

Local services (no Docker)
-------------------------
If Docker is unavailable, run both services locally using the included runner:

```bash
python3 -m pip install -r requirements.txt --user
python3 simulator/run_local.py
```

This starts the controller and worker as local Python processes, issues directives, processes them, and then shuts the services down.

Convenience scripts

CI Badge
--------
![CI](https://github.com/OWNER/REPO/actions/workflows/ci.yml/badge.svg)



