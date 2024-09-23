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





if __name__ == '__main__':
    unittest.main()
