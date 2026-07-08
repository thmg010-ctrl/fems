"""Migration tool: convert NDJSON ledger to SQLite WAL-backed DB.

Usage:
    python3 simulator/migrate_ndjson_to_sqlite.py path/to/ndjson.db path/to/output.db
"""
import sys
import os
import json
from simulator.event_store_sqlite import append_event_db


def migrate(ndjson_path: str, sqlite_path: str):
    if not os.path.exists(ndjson_path):
        print('NDJSON file not found:', ndjson_path)
        return 1
    with open(ndjson_path, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                rec = json.loads(line)
            except Exception:
                continue
            # rec may already contain the chain/prev keys or be raw event
            # We migrate the event payload as-is into SQLite store.
            append_event_db(sqlite_path, rec.get('event') if 'event' in rec else rec)
    print('Migration complete')
    return 0


if __name__ == '__main__':
    if len(sys.argv) < 3:
        print('Usage: migrate_ndjson_to_sqlite.py <ndjson-file> <sqlite-db>')
        sys.exit(2)
    sys.exit(migrate(sys.argv[1], sys.argv[2]))
