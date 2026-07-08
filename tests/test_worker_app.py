from fastapi.testclient import TestClient
import time


def test_worker_processes_directive(tmp_path):
    import os
    # isolate per-test sqlite DB
    os.environ['EVENT_DB'] = str(tmp_path / 'events.db')
    from simulator.worker_app import app as worker_app
    from simulator.controller_app import controller
    from event_store import append_event, read_events

    # Create a directive signed by the controller and append
    directive = {'agent_id': 42, 'task': 'generate_profit', 'amount_target': 20, 'nonce': int(time.time()*1000), 'seq': 0}
    sig = controller.sign(directive)
    event = {'type': 'directive', 'directive': directive, 'signature': sig.hex(), 'pubkey': controller.pubhex(), 'ts': time.time()}
    append_event('simulator/event_store.ndjson', event)

    with TestClient(worker_app) as w:
        rv = w.post('/process', json={'pubkey': controller.pubhex()})
        assert rv.status_code == 200
        body = rv.json()
        assert body.get('processed') >= 1

    # Verify execution events appended
    recs = read_events('simulator/event_store.ndjson')
    execs = [r for r in recs if isinstance(r, dict) and 'event' in r and r['event'].get('type') == 'execution']
    assert len(execs) >= 1
