import sqlite3
from contextlib import closing
import tempfile
import unittest
from pathlib import Path
from recovery import copy_database, check

class RecoveryTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(); self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name); self.source = self.root / 'source.db'
        with closing(sqlite3.connect(self.source)) as db:
            db.execute('CREATE TABLE assets(id INTEGER PRIMARY KEY, label TEXT)')
            db.execute("INSERT INTO assets VALUES (1, 'synthetic-laptop')")
            db.commit()
    def test_restore_preserves_actual_data(self):
        backup, restored = self.root/'backup.db', self.root/'restored.db'
        copy_database(self.source, backup); copy_database(backup, restored)
        with closing(sqlite3.connect(restored)) as db:
            self.assertEqual(db.execute('SELECT * FROM assets').fetchall(), [(1, 'synthetic-laptop')])
    def test_refuses_overwrite(self):
        with self.assertRaises(FileExistsError): copy_database(self.source, self.source)
        self.assertEqual(check(self.source), 1)
    def test_corrupt_backup_does_not_create_restore(self):
        bad = self.root/'bad.db'; bad.write_text('broken')
        dest = self.root/'restored.db'
        with self.assertRaises(sqlite3.DatabaseError): copy_database(bad, dest)
        self.assertFalse(dest.exists())
    def test_missing_source_is_not_created(self):
        missing = self.root/'missing.db'
        with self.assertRaises(ValueError): check(missing)
        self.assertFalse(missing.exists())
