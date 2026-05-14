# queuectl/config.py
from dataclasses import dataclass, field
import json
import os
from pathlib import Path

CONFIG_PATH = Path.home() / ".queuectl_config.jso"

DEFAULTS = {
    "max_retries": 3,
    "backoff_base": 2,
    "db_path": str(Path.home() / ".queuectl.db"),
}

@dataclass
class Config:
    max_retries: int = 3
    backoff_base: int = 2
    db_path: str = DEFAULTS["db_path"]

    @classmethod
    def load(cls):
        if CONFIG_PATH.exists():
            try:
                data = json.loads(CONFIG_PATH.read_text())
                return cls(**{**DEFAULTS, **data})
            except Exception:
                pass
        return cls(**DEFAULTS)

    def save(self):
        CONFIG_PATH.write_text(json.dumps({
            "max_retries": self.max_retries,
            "backoff_base": self.backoff_base,
            "db_path": self.db_path
        }, indent=2))
