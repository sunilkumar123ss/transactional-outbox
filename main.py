"""SQLite transactional outbox with explicit at-least-once delivery."""
import argparse
import json
import sqlite3

