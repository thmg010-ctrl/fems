import hashlib
import json
import os
from typing import Optional, Dict

try:
    import fcntl
except Exception:
    fcntl = None


def _hash_event(event: Dict, prev_hash: Optional[str]) -> str:
    payload = json.dumps({"prev": prev_hash, "event": event}, sort_keys=True).encode()
    return hashlib.sha256(payload).hexdigest()


def append_event(path: str, event: Dict) -> str:
    """Append an event to the ndjson event store and return the new hash (chain).

    Uses an advisory file lock on Unix (fcntl) to protect concurrent writers.
    """
    prev_hash = None
    # Ensure directory exists
    os.makedirs(os.path.dirname(path) or '.', exist_ok=True)

    # Open file for read/update and lock during read+append to protect concurrent writes
    mode = 'a+'
    with open(path, mode) as f:
        if fcntl is not None:
            try:
                fcntl.flock(f.fileno(), fcntl.LOCK_EX)
            except Exception:
                pass

        # Read entire file to find last chained record (robust approach)
        try:
            f.seek(0)
            data = f.read()
            lines = data.strip().splitlines()
            # find last record that looks like a chained record
            for ln in reversed(lines):
                try:
                    last = json.loads(ln)
                    if isinstance(last, dict) and 'chain_hash' in last:
                        prev_hash = last.get('chain_hash')
                        break
                except Exception:
                    continue
        except Exception:
            prev_hash = None

        chain_hash = _hash_event(event, prev_hash)
        record = {"chain_hash": chain_hash, "prev_hash": prev_hash, "event": event}
        # Append and flush
        f.seek(0, os.SEEK_END)
        f.write(json.dumps(record) + "\n")
        f.flush()
        os.fsync(f.fileno())

        if fcntl is not None:
            try:
                fcntl.flock(f.fileno(), fcntl.LOCK_UN)
            except Exception:
                pass

    return chain_hash


def read_events(path: str):
    if not os.path.exists(path):
        return []
    out = []
    # Use shared lock if available to allow concurrent readers
    with open(path, 'r') as f:
        if fcntl is not None:
            try:
                fcntl.flock(f.fileno(), fcntl.LOCK_SH)
            except Exception:
                pass
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                out.append(json.loads(line))
            except Exception:
                continue
        if fcntl is not None:
            try:
                fcntl.flock(f.fileno(), fcntl.LOCK_UN)
            except Exception:
                pass
    return out
