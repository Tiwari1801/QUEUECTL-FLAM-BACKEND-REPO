# queuectl/cli.py
import typer
import json
from queuectl.models import create_job, list_jobs, get_job
from queuectl.worker import start_workers, stop_workers
from queuectl.config import Config
from queuectl.db import init_db, get_conn
from queuectl.utils import now_iso
from datetime import datetime, timezone

app = typer.Typer()
worker_app = typer.Typer()
app.add_typer(worker_app, name="worker")
cfg = Config.load()

@app.command()
def enqueue(payload: str):
    """
    Enqueue a job:
    queuectl enqueue '{"id":"job1","command":"echo hello","max_retries":3}'
    """
    init_db()
    try:
        job_obj = json.loads(payload)
    except Exception as e:
        typer.echo("Payload must be valid JSON")
        raise typer.Exit(code=1)
    # Ensure created_at, next_run_at present
    job_obj.setdefault("created_at", now_iso())
    job_obj.setdefault("updated_at", now_iso())
    job_obj.setdefault("next_run_at", now_iso())
    create_job(job_obj)
    typer.echo(f"Enqueued job {job_obj['id']}")

@worker_app.command("start")
def worker_start(count: int = typer.Option(1, "--count", "-c")):
    """
    Start workers: queuectl worker start --count 3
    (This is blocking, use a terminal multiplexer to run in background)
    """
    typer.echo(f"Starting {count} worker(s). Press Ctrl+C to stop.")
    threads = start_workers(count)
    # join
    try:
        for t in threads:
            t.join()
    except KeyboardInterrupt:
        typer.echo("Stopping workers...")
        stop_workers()

@worker_app.command("stop")
def worker_stop():
    """
    Stop workers (if running in same process - otherwise stop_event won't reach other process)
    For multi-process/daemon setups you'd implement a PID file + signalling.
    """
    stop_workers()
    typer.echo("Stop signal sent to workers.")

@app.command()
def status():
    """
    Show a summary (counts by state)
    """
    init_db()
    with get_conn() as conn:
        rows = conn.execute("""
            SELECT state, COUNT(*) as cnt FROM jobs GROUP BY state
        """).fetchall()
        out = {r["state"]: r["cnt"] for r in rows}
        typer.echo(json.dumps(out, indent=2))

@app.command()
def list(state: str = typer.Option(None, "--state")):
    """
    List jobs optionally filtered by state
    """
    init_db()
    rows = list_jobs(state)
    typer.echo(json.dumps(rows, indent=2))

@app.command()
def dlq_list():
    """
    List jobs in the dead letter queue
    """
    init_db()
    rows = list_jobs("dead")
    typer.echo(json.dumps(rows, indent=2))

@app.command()
def dlq_retry(job_id: str):
    """
    Retry a DLQ job: moves it back to pending with attempts reset (or you can keep attempts).
    """
    init_db()
    job = get_job(job_id)
    if not job:
        typer.echo("Job not found")
        raise typer.Exit(code=1)
    if job["state"] != "dead":
        typer.echo("Job is not in DLQ")
        raise typer.Exit(code=1)
    # Reset attempts and next_run_at and state
    with get_conn() as conn:
        conn.execute("""
            UPDATE jobs
            SET state='pending', attempts=0, updated_at=?, next_run_at=?, worker_id=NULL
            WHERE id=?
        """, (now_iso(), now_iso(), job_id))
        conn.commit()
    typer.echo(f"Job {job_id} requeued from DLQ")

@app.command()
def config_set(key: str, value: str):
    """
    Set config key: queuectl config set max_retries 5
    """
    c = Config.load()
    if not hasattr(c, key):
        typer.echo("Unknown config key")
        raise typer.Exit(code=1)
    # cast to right type
    current = getattr(c, key)
    if isinstance(current, int):
        value = int(value)
    setattr(c, key, value)
    c.save()
    typer.echo(f"Set {key} = {value}")

def main():
    app()
