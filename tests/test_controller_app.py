from fastapi.testclient import TestClient
from simulator.controller_app import app as controller_app, controller
from event_store import read_events


def test_issue_writes_directive(tmp_path, monkeypatch):
    store = 'simulator/event_store.ndjson'
    open(store, 'w').close()
    with TestClient(controller_app) as c:
        rv = c.post('/issue', json={'agent_id': 7, 'seq': 0, 'amount_target': 15})
        assert rv.status_code == 200
        body = rv.json()
        assert body.get('status') == 'issued'
        assert 'pubkey' in body

    # Verify event store has a directive
    recs = read_events(store)
    found = False
    for r in recs:
        ev = r.get('event') if isinstance(r, dict) and 'event' in r else r
        if isinstance(ev, dict) and ev.get('type') == 'directive':
            found = True
    assert found
