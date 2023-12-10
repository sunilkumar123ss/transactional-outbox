"""SQLite transactional outbox with explicit at-least-once delivery."""
import argparse
import json
import sqlite3

def connect(path=':memory:'):
    db = sqlite3.connect(path)
    db.executescript('CREATE TABLE IF NOT EXISTS orders(id TEXT PRIMARY KEY, payload TEXT NOT NULL); CREATE TABLE IF NOT EXISTS outbox(id INTEGER PRIMARY KEY AUTOINCREMENT, order_id TEXT NOT NULL UNIQUE, event TEXT NOT NULL, sent INTEGER NOT NULL DEFAULT 0);')
    return db
