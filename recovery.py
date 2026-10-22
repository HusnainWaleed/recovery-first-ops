"""Back up SQLite consistently and verify a candidate before restoring."""
import argparse
import sqlite3
from contextlib import closing
from pathlib import Path

def check(path):
    path = Path(path).resolve()
    if not path.is_file(): raise ValueError('database does not exist')
    with closing(sqlite3.connect(path.as_uri() + '?mode=ro', uri=True)) as db:
        if db.execute('PRAGMA integrity_check').fetchone()[0] != 'ok':
            raise ValueError('integrity check failed')
        count = db.execute('SELECT count(*) FROM assets').fetchone()[0]
    return count

def copy_database(source, destination):
    source, destination = Path(source).resolve(), Path(destination).resolve()
    check(source)
    # Reserve the target exclusively, preventing accidental overwrite.
    with destination.open('xb'): pass
    try:
        with closing(sqlite3.connect(source.as_uri() + '?mode=ro', uri=True)) as src:
            with closing(sqlite3.connect(destination)) as dst:
                src.backup(dst)
        return check(destination)
    except Exception:
        destination.unlink(missing_ok=True)
        raise

def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('operation', choices=['seed', 'backup', 'restore', 'verify'])
    p.add_argument('source', type=Path); p.add_argument('destination', type=Path, nargs='?')
    a = p.parse_args()
    try:
        if a.operation == 'seed':
            with a.source.open('xb'): pass
            with closing(sqlite3.connect(a.source)) as db:
                db.execute('CREATE TABLE assets (id INTEGER PRIMARY KEY, label TEXT NOT NULL)')
                db.executemany('INSERT INTO assets(label) VALUES (?)', [('lab-laptop-01',), ('lab-switch-01',)])
                db.commit()
            count = check(a.source)
        elif a.operation == 'verify': count = check(a.source)
        else:
            if a.destination is None: raise ValueError('destination is required')
            count = copy_database(a.source, a.destination)
        print(f'{a.operation}: integrity OK; assets={count}')
    except (ValueError, OSError, sqlite3.Error) as e:
        p.exit(2, str(e) + '\n')

if __name__ == '__main__': main()
