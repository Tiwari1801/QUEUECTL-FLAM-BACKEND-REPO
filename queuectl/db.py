# queuectl/db.py
import sqlite3
from contextlib import contextmanager
from pathlib import Path
from queuectl.config import Config

cfg = Config.load()
DB_PATH = Path(cfg.db_path)

SCHEMA = """
CREATE TABLE IF NOT EXISTS jobs (
  id TEXT PRIMARY KEY,
  command TEXT NOT NULL,
  state TEXT NOT NULL,
  attempts INTEGER NOT NULL,
  max_retries INTEGER NOT NULL,
  created_at TEXT NOT NULL,
  updated_at TEXT NOT NULL,
  next_run_at TEXT NOT NULL,
  worker_id TEXT,
  exit_code INTEGER,
  output TEXT
);

CREATE INDEX IF NOT EXISTS idx_state_next ON jobs(state, next_run_at);
"""

def init_db():
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    with sqlite3.connect(DB_PATH) as conn:
        conn.executescript(SCHEMA)
        conn.commit()

@contextmanager
def get_conn():
    conn = sqlite3.connect(DB_PATH, timeout=30, isolation_level='EXCLUSIVE')
    conn.row_factory = sqlite3.Row
    try:
        yield conn
    finally:
        conn.close()
