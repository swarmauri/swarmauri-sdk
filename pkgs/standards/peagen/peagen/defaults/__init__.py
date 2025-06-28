"""peagen.defaults
=================
Package-level built-in configuration and constants.
"""

import os
from pathlib import Path

from .abuse import BAN_THRESHOLD
from .events import CONTROL_QUEUE, READY_QUEUE, PUBSUB_CHANNEL, TASK_KEY
from .methods import *  # noqa: F401,F403 re-export rpc method names
from peagen.protocols.error_codes import Code as ErrorCode

# Default directory for repository lock files.
LOCK_DIR = "~/.cache/peagen/locks"


def lock_dir() -> Path:
    """Return the directory used for repository locks."""
    return Path(os.getenv("PEAGEN_LOCK_DIR", LOCK_DIR)).expanduser()


# Default worker pool used when none is specified via environment variables.
DEFAULT_POOL = "default"

# Base configuration used when no `.peagen.toml` is present.
CONFIG = {
    "gateway_url": "http://localhost:8000/rpc",
    "control_queue": CONTROL_QUEUE,
    "ready_queue": READY_QUEUE,
    "pubsub": PUBSUB_CHANNEL,
    "task_key": TASK_KEY,
    "queues": {"default_queue": "in_memory", "adapters": {"in_memory": {"maxsize": 0}}},
    "result_backends": {
        "default_backend": "local_fs",
        "adapters": {
            "local_fs": {"root_dir": "./task_runs"},
            "in_memory": {},
        },
    },
    "storage": {
        "default_filter": "file",
        "filters": {"file": {"output_dir": "./peagen_artifacts"}},
    },
    "mutation": {
        "mutators": {"default_mutator": "DefaultMutator"},
    },
    "vcs": {
        "default_vcs": "git",
        "adapters": {
            "git": {
                "mirror_git_url": "",
                "mirror_git_token": "",
                "owner": "",
                "remotes": {},
            }
        },
    },
    "secrets": {"default_secret": "env", "adapters": {"env": {"prefix": ""}}},
}

__all__ = [
    "CONFIG",
    "BAN_THRESHOLD",
    "CONTROL_QUEUE",
    "READY_QUEUE",
    "PUBSUB_CHANNEL",
    "TASK_KEY",
    "LOCK_DIR",
    "lock_dir",
    "DEFAULT_POOL",
    "ErrorCode",
]
