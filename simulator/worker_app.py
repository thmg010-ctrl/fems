from fastapi import FastAPI
from pydantic import BaseModel
import json
import time
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PublicKey

from event_store import read_events, append_event
import uvicorn
import logging
import os
from logging.handlers import RotatingFileHandler

os.makedirs('logs', exist_ok=True)
logger = logging.getLogger('worker')
if not logger.handlers:
    handler = RotatingFileHandler('logs/worker.log', maxBytes=1_000_000, backupCount=5)
    formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s')
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    logger.setLevel(logging.INFO)


class ProcessRequest(BaseModel):
    pubkey: str


app = FastAPI()


@app.post("/process")
def process(req: ProcessRequest):
    pubhex = req.pubkey
    if not pubhex:
        return {'error': 'pubkey required'}

    events = read_events('simulator/event_store.ndjson')
    processed = 0
    pub = Ed25519PublicKey.from_public_bytes(bytes.fromhex(pubhex))
    for rec in events:
        ev = rec.get('event') if isinstance(rec, dict) and 'event' in rec else rec
        if not isinstance(ev, dict) or ev.get('type') != 'directive':
            continue
        directive = ev.get('directive')
        sig = bytes.fromhex(ev.get('signature'))
        payload = json.dumps(directive, sort_keys=True).encode()
        try:
            pub.verify(sig, payload)
            result = {'agent': directive.get('agent_id'), 'status': 'executed', 'directive': directive, 'ts': time.time()}
            logger.info('executed directive %s', directive)
        except Exception as e:
            result = {'agent': directive.get('agent_id'), 'status': 'rejected', 'error': str(e), 'ts': time.time()}
            logger.warning('rejected directive %s error=%s', directive, str(e))
        append_event('simulator/event_store.ndjson', {'type': 'execution', 'result': result})
        processed += 1

    return {'processed': processed}


if __name__ == '__main__':
    uvicorn.run(app, host='0.0.0.0', port=8001)
