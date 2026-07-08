"""SQLite-backed event store with WAL mode.

Provides `append_event_db(path_or_uri, event)` and `read_events_db(path_or_uri)`.
The DB schema stores chain_hash, prev_hash, event_json, ts.
"""
import sqlite3
import json
import os
from typing import List, Dict


def _ensure_db(path: str):
    # Always connect and ensure the events table exists. Use IF NOT EXISTS
    # to avoid races when multiple threads/processes initialize concurrently.
    conn = sqlite3.connect(path, isolation_level=None, check_same_thread=False)
    # enable WAL for better concurrency
    conn.execute('PRAGMA journal_mode=WAL;')
    conn.execute('PRAGMA synchronous=NORMAL;')
    conn.execute('''CREATE TABLE IF NOT EXISTS events (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        chain_hash TEXT UNIQUE,
        prev_hash TEXT,
        event_json TEXT,
        ts REAL
    )''')
    return conn


def append_event_db(path: str, event: Dict) -> str:
    conn = _ensure_db(path)
    cur = conn.cursor()
    # find last chain_hash
    cur.execute('SELECT chain_hash FROM events ORDER BY id DESC LIMIT 1')
    row = cur.fetchone()
    prev = row[0] if row else None
    payload = json.dumps({"prev": prev, "event": event}, sort_keys=True).encode()
    import hashlib
    chain_hash = hashlib.sha256(payload).hexdigest()
    cur.execute('INSERT INTO events (chain_hash, prev_hash, event_json, ts) VALUES (?,?,?,?)', (chain_hash, prev, json.dumps(event), event.get('ts'))) 
    conn.commit()
    conn.close()
    return chain_hash


def read_events_db(path: str) -> List[Dict]:
    if not os.path.exists(path):
        return []
    conn = sqlite3.connect(path, check_same_thread=False)
    cur = conn.cursor()
    cur.execute('SELECT chain_hash, prev_hash, event_json, ts FROM events ORDER BY id')
    out = []
    for chain_hash, prev_hash, event_json, ts in cur.fetchall():
        try:
            event = json.loads(event_json)
        except Exception:
            event = event_json
        out.append({"chain_hash": chain_hash, "prev_hash": prev_hash, "event": event, "ts": ts})
    conn.close()
    return out
