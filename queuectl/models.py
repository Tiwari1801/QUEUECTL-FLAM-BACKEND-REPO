# queuectl/models.py
from datetime import datetime, timezone
import json
from queuectl.db import get_conn, init_db
from queuectl.config import Config
cfg = Config.load()

ISO = lambda: datetime.now(timezone.utc).isoformat()

def create_job(job_obj: dict):
    # job_obj must include id and command, optional max_retries
    init_db()
    job = {
        "id": job_obj["id"],
        "command": job_obj["command"],
        "state": job_obj.get("state", "pending"),
        "attempts": int(job_obj.get("attempts", 0)),
        "max_retries": int(job_obj.get("max_retries", cfg.max_retries)),
        "created_at": job_obj.get("created_at", ISO()),
        "updated_at": job_obj.get("updated_at", ISO()),
        "next_run_at": job_obj.get("next_run_at", ISO()),
        "worker_id": None,
        "exit_code": None,
        "output": None
    }
    with get_conn() as conn:
        conn.execute("""
            INSERT INTO jobs (id,command,state,attempts,max_retries,created_at,updated_at,next_run_at)
            VALUES (?,?,?,?,?,?,?,?)
        """, (job["id"], job["command"], job["state"], job["attempts"], job["max_retries"],
              job["created_at"], job["updated_at"], job["next_run_at"]))
        conn.commit()
    return job

def list_jobs(state=None):
    init_db()
    with get_conn() as conn:
        if state:
            rows = conn.execute("SELECT * FROM jobs WHERE state=? ORDER BY created_at", (state,)).fetchall()
        else:
            rows = conn.execute("SELECT * FROM jobs ORDER BY created_at").fetchall()
        return [dict(r) for r in rows]

def get_job(job_id):
    init_db()
    with get_conn() as conn:
        row = conn.execute("SELECT * FROM jobs WHERE id=?", (job_id,)).fetchone()
        return dict(row) if row else None

def delete_job(job_id):
    init_db()
    with get_conn() as conn:
        conn.execute("DELETE FROM jobs WHERE id=?", (job_id,))
        conn.commit()
