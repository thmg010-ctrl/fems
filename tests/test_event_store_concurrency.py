import threading
import time
from simulator.event_store_sqlite import append_event_db, read_events_db


def _worker(db_path, start, count):
    for i in range(count):
        ev = {'type': 'concurrent', 'i': start + i, 'ts': time.time()}
        append_event_db(db_path, ev)


def test_concurrent_writes(tmp_path):
    db = str(tmp_path / 'events.db')
    threads = []
    workers = 6
    per_worker = 20
    for w in range(workers):
        t = threading.Thread(target=_worker, args=(db, w * per_worker, per_worker))
        t.start()
        threads.append(t)
    for t in threads:
        t.join()
    recs = read_events_db(db)
    assert len(recs) == workers * per_worker
