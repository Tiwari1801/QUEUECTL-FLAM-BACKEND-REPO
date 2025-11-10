# queuectl/utils.py
from datetime import datetime, timezone, timedelta

def now_iso():
    return datetime.now(timezone.utc).isoformat()

def iso_to_dt(s):
    from datetime import datetime
    return datetime.fromisoformat(s)

def dt_to_iso(dt):
    return dt.isoformat()

def add_seconds_iso(iso, seconds):
    d = iso_to_dt(iso)
    return dt_to_iso(d + timedelta(seconds=seconds))
