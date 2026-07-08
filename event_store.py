"""Top-level shim that routes to file-based or SQLite event store.

If the `EVENT_DB` environment variable is set, the SQLite-backed store
(`simulator.event_store_sqlite`) will be used. Otherwise the original
NDJSON file-based store (`simulator.event_store`) is used for backward
compatibility.
"""
import os
from simulator.event_store import append_event as _append_ndjson, read_events as _read_ndjson, _hash_event

EVENT_DB = os.getenv('EVENT_DB')

if EVENT_DB:
	from simulator.event_store_sqlite import append_event_db, read_events_db

	def append_event(path: str | None, event):
		db_path = EVENT_DB if EVENT_DB else path
		return append_event_db(db_path, event)

	def read_events(path: str | None):
		db_path = EVENT_DB if EVENT_DB else path
		return read_events_db(db_path)
else:
	def append_event(path: str, event):
		return _append_ndjson(path, event)

	def read_events(path: str):
		return _read_ndjson(path)

__all__ = ["append_event", "read_events", "_hash_event"]
