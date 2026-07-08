import os
from simulator.event_store_sqlite import append_event_db, read_events_db


def test_sqlite_append_and_read(tmp_path):
    db = tmp_path / "events.db"
    ev1 = {"type": "directive", "directive": {"agent_id": 1}, 'ts': 1.0}
    ev2 = {"type": "execution", "result": {"agent": 1, "status": "executed"}, 'ts': 2.0}
    h1 = append_event_db(str(db), ev1)
    h2 = append_event_db(str(db), ev2)
    recs = read_events_db(str(db))
    assert len(recs) == 2
    assert recs[0]['event']['type'] == 'directive'
    assert recs[1]['event']['type'] == 'execution'
