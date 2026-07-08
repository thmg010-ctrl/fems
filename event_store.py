"""Top-level shim for the simulator event_store module."""
from simulator.event_store import append_event, read_events, _hash_event

__all__ = ["append_event", "read_events", "_hash_event"]
