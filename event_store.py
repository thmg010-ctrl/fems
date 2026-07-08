"""Top-level shim that routes to file-based or SQLite event store.

If the `EVENT_DB` environment variable is set, the SQLite-backed store
(`simulator.event_store_sqlite`) will be used. Otherwise the original
NDJSON file-based store (`simulator.event_store`) is used for backward
compatibility.
"""
import os
from simulator.event_store import append_event as _append_ndjson, read_events as _read_ndjson, _hash_event


def append_event(path: str | None, event):
	"""Append an event. If `EVENT_DB` env var is set, write to SQLite DB.

	Otherwise, fall back to NDJSON file-based store.
	"""
	db_path = os.getenv('EVENT_DB')
	if db_path:
		from simulator.event_store_sqlite import append_event_db
		return append_event_db(db_path, event)
	return _append_ndjson(path, event)


def read_events(path: str | None):
	"""Read events. If `EVENT_DB` env var is set, read from SQLite DB."""
	db_path = os.getenv('EVENT_DB')
	if db_path:
		from simulator.event_store_sqlite import read_events_db
		return read_events_db(db_path)
	return _read_ndjson(path)


__all__ = ["append_event", "read_events", "_hash_event"]
