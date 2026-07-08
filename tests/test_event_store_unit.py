import os
import json
from event_store import append_event, read_events


def test_append_and_read(tmp_path):
    p = tmp_path / "store.ndjson"
    ev1 = {"type": "directive", "directive": {"agent_id": 1}}
    ev2 = {"type": "execution", "result": {"agent": 1, "status": "executed"}}
    h1 = append_event(str(p), ev1)
    h2 = append_event(str(p), ev2)
    recs = read_events(str(p))
    assert isinstance(recs, list)
    # records should include two chained records
    chained = [r for r in recs if isinstance(r, dict) and 'chain_hash' in r]
    assert len(chained) == 2
