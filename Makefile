PY=python3
PIP=$(PY) -m pip

.PHONY: install run-local test run-sim docker-build docker-up

install:
	$(PIP) install -r requirements.txt --user

run-local:
	$(PY) simulator/run_local.py

test:
	$(PY) tests/run_integration.py

run-sim:
	$(PY) simulator/agent_simulator.py --agents 200 --steps 200 --out sim_output.json

docker-build:
	docker compose build

docker-up:
	docker compose up --build
