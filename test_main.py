import importlib.util
from pathlib import Path
import sys
import unittest
_spec = importlib.util.spec_from_file_location('lab_' + Path(__file__).parent.name.replace('-', '_'), Path(__file__).with_name('main.py'))
m = importlib.util.module_from_spec(_spec)
sys.modules[_spec.name] = m
_spec.loader.exec_module(m)
import sqlite3

class OutboxTests(unittest.TestCase):

    def setUp(self):
        self.db = m.connect()

    def tearDown(self):
        self.db.close()

    def test_success_is_acknowledged(self):
        m.create_order(self.db, 'a', {'x': 1})
        seen = []
        self.assertEqual(m.publish_pending(self.db, lambda i, e: seen.append(e)), [1])
        self.assertEqual(seen[0]['order_id'], 'a')
        self.assertEqual(m.publish_pending(self.db, lambda *args: self.fail()), [])

    def test_duplicate_does_not_duplicate_event(self):
        m.create_order(self.db, 'a', {})
        with self.assertRaises(sqlite3.IntegrityError):
            m.create_order(self.db, 'a', {})
        self.assertEqual(self.db.execute('SELECT count(*) FROM outbox').fetchone()[0], 1)

    def test_failed_callback_remains_pending(self):
        m.create_order(self.db, 'a', {})

        def fail(*args):
            raise RuntimeError('transport failed')
        with self.assertRaises(RuntimeError):
            m.publish_pending(self.db, fail)
        self.assertEqual(m.publish_pending(self.db, lambda *args: None), [1])

    def test_outbox_insert_failure_rolls_back_order(self):
        with self.db:
            self.db.execute("INSERT INTO outbox(order_id,event) VALUES ('a','{}')")
        with self.assertRaises(sqlite3.IntegrityError):
            m.create_order(self.db, 'a', {})
        self.assertEqual(self.db.execute('SELECT count(*) FROM orders').fetchone()[0], 0)


if __name__ == '__main__':
    unittest.main()
