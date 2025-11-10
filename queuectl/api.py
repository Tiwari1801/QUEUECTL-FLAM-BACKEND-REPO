# queuectl/api.py
from fastapi import FastAPI
from queuectl.models import list_jobs, get_job
from queuectl.db import init_db

app = FastAPI(title="queuectl API")

@app.on_event("startup")
def startup():
    init_db()

@app.get("/jobs")
def api_list(state: str = None):
    return list_jobs(state)

@app.get("/jobs/{job_id}")
def api_get(job_id: str):
    job = get_job(job_id)
    if not job:
        return {"error": "not found"}
    return job
