# queuectl/worker.py
import threading
import time
import uuid
import subprocess
import signal
from queuectl.db import get_conn, init_db
from queuectl.utils import now_iso, add_seconds_iso
from datetime import datetime, timezone
from queuectl.config import Config
cfg = Config.load()

stop_event = threading.Event()

def compute_backoff(base, attempts):
    # delay = base ** attempts
    return base ** attempts

class Worker(threading.Thread):
    def __init__(self, worker_name=None):
        super().__init__()
        self.daemon = True
        self.worker_id = worker_name or str(uuid.uuid4())[:8]

    def run(self):
        init_db()
        print(f"[worker:{self.worker_id}] started")
        while not stop_event.is_set():
            job = self.claim_job()
            if not job:
                # no ready job, sleep a bit
                time.sleep(1)
                continue
            print(f"[worker:{self.worker_id}] picked job {job['id']}")
            self.execute_job(job)

        print(f"[worker:{self.worker_id}] shutting down")

    def claim_job(self):
        """Atomically claim a pending job whose next_run_at <= now."""
        with get_conn() as conn:
            cur = conn.cursor()
            now = datetime.now(timezone.utc).isoformat()
            # Try to atomically set state=processing for one job
            # We pick the oldest pending ready job
            cur.execute("""
                SELECT id FROM jobs
                WHERE state='pending' AND next_run_at <= ?
                ORDER BY created_at LIMIT 1
            """, (now,))
            row = cur.fetchone()
            if not row:
                return None
            job_id = row["id"]
            # Attempt to update only if still pending
            updated_at = datetime.now(timezone.utc).isoformat()
            res = cur.execute("""
                UPDATE jobs
                SET state='processing', worker_id=?, updated_at=?
                WHERE id=? AND state='pending'
            """, (self.worker_id, updated_at, job_id))
            if cur.rowcount == 0:
                conn.commit()
                return None
            conn.commit()
            # fetch job
            job = cur.execute("SELECT * FROM jobs WHERE id=?", (job_id,)).fetchone()
            return dict(job)

    def execute_job(self, job):
        # run the command; use shell to support simple shell commands
        try:
            proc = subprocess.run(job["command"], shell=True, capture_output=True, text=True)
            exit_code = proc.returncode
            output = proc.stdout + proc.stderr
        except Exception as e:
            exit_code = 1
            output = str(e)

        now = datetime.now(timezone.utc).isoformat()
        with get_conn() as conn:
            cur = conn.cursor()
            attempts = job["attempts"] + 1
            if exit_code == 0:
                cur.execute("""
                    UPDATE jobs
                    SET state='completed', attempts=?, exit_code=?, output=?, updated_at=?, worker_id=NULL
                    WHERE id=?
                """, (attempts, exit_code, output, now, job["id"]))
                print(f"[worker:{self.worker_id}] job {job['id']} completed")
            else:
                # failure path: retry or DLQ
                maxr = job["max_retries"]
                if attempts >= maxr:
                    # move to dead
                    cur.execute("""
                        UPDATE jobs
                        SET state='dead', attempts=?, exit_code=?, output=?, updated_at=?, worker_id=NULL
                        WHERE id=?
                    """, (attempts, exit_code, output, now, job["id"]))
                    print(f"[worker:{self.worker_id}] job {job['id']} dead after {attempts} attempts")
                else:
                    # schedule next run with exponential backoff
                    delay = compute_backoff(cfg.backoff_base, attempts)
                    next_run = add_seconds_iso(now, delay)
                    cur.execute("""
                        UPDATE jobs
                        SET state='pending', attempts=?, exit_code=?, output=?, updated_at=?, next_run_at=?, worker_id=NULL
                        WHERE id=?
                    """, (attempts, exit_code, output, now, next_run, job["id"]))
                    print(f"[worker:{self.worker_id}] job {job['id']} failed, retrying in {delay}s (attempt {attempts}/{maxr})")
            conn.commit()

def start_workers(count):
    # register signal handlers
    def sigterm(signum, frame):
        print("received shutdown signal; stopping workers gracefully...")
        stop_event.set()
    signal.signal(signal.SIGINT, sigterm)
    signal.signal(signal.SIGTERM, sigterm)

    threads = []
    for i in range(count):
        w = Worker(worker_name=f"w{i+1}")
        w.start()
        threads.append(w)
    return threads

def stop_workers():
    stop_event.set()
