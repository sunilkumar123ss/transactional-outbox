"""SQLite transactional outbox with explicit at-least-once delivery."""
import argparse
import json
import sqlite3

def connect(path=':memory:'):
    db = sqlite3.connect(path)
    db.executescript('CREATE TABLE IF NOT EXISTS orders(id TEXT PRIMARY KEY, payload TEXT NOT NULL); CREATE TABLE IF NOT EXISTS outbox(id INTEGER PRIMARY KEY AUTOINCREMENT, order_id TEXT NOT NULL UNIQUE, event TEXT NOT NULL, sent INTEGER NOT NULL DEFAULT 0);')
    return db

def create_order(db, order_id, payload):
    if not isinstance(order_id, str) or not order_id or (not isinstance(payload, dict)):
        raise ValueError('A nonempty order ID and object payload are required')
    if db.in_transaction:
        raise ValueError('Caller transaction must be completed first')
    encoded = json.dumps(payload, sort_keys=True, allow_nan=False)
    event = json.dumps({'type': 'order.created', 'order_id': order_id, 'payload': payload}, sort_keys=True, allow_nan=False)
    with db:
        db.execute('INSERT INTO orders VALUES (?,?)', (order_id, encoded))
        db.execute('INSERT INTO outbox(order_id,event) VALUES (?,?)', (order_id, event))

def publish_pending(db, send):
    if db.in_transaction:
        raise ValueError('Caller transaction must be completed first')
    sent = []
    for (event_id, body) in db.execute('SELECT id,event FROM outbox WHERE sent=0 ORDER BY id').fetchall():
        send(event_id, json.loads(body))
        with db:
            db.execute('UPDATE outbox SET sent=1 WHERE id=?', (event_id,))
        sent.append(event_id)
    return sent
