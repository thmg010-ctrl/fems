from fastapi import FastAPI
from pydantic import BaseModel
import time
import json
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
from cryptography.hazmat.primitives import serialization
from event_store import append_event
import uvicorn
import logging
import os
from logging.handlers import RotatingFileHandler

# ensure logs directory
os.makedirs('logs', exist_ok=True)
logger = logging.getLogger('controller')
if not logger.handlers:
    handler = RotatingFileHandler('logs/controller.log', maxBytes=1_000_000, backupCount=5)
    formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s')
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    logger.setLevel(logging.INFO)


class IssueRequest(BaseModel):
    agent_id: int | None = 0
    seq: int | None = 0
    amount_target: int | None = 10


app = FastAPI()


class Controller:
    def __init__(self):
        self._key = Ed25519PrivateKey.generate()
        self.pub = self._key.public_key()

    def sign(self, directive: dict) -> bytes:
        payload = json.dumps(directive, sort_keys=True).encode()
        return self._key.sign(payload)

    def pubhex(self) -> str:
        return self.pub.public_bytes(encoding=serialization.Encoding.Raw, format=serialization.PublicFormat.Raw).hex()


controller = Controller()


@app.post("/issue")
def issue(req: IssueRequest):
    directive = {
        'agent_id': req.agent_id,
        'task': 'generate_profit',
        'amount_target': req.amount_target,
        'nonce': int(time.time() * 1000),
        'seq': req.seq,
    }
    sig = controller.sign(directive)
    event = {'type': 'directive', 'directive': directive, 'signature': sig.hex(), 'pubkey': controller.pubhex(), 'ts': time.time()}
    chain = append_event('simulator/event_store.ndjson', event)
    logger.info('issued directive %s chain=%s', directive, chain)
    return {'status': 'issued', 'chain_hash': chain, 'directive': directive, 'pubkey': controller.pubhex()}


if __name__ == '__main__':
    uvicorn.run(app, host='0.0.0.0', port=8000)
