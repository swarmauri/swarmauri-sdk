"""peagen.defaults
=================
Package-level built-in configuration and constants.
"""

from .abuse import BAN_THRESHOLD
from .events import CONTROL_QUEUE, READY_QUEUE, PUBSUB_CHANNEL, TASK_KEY
from .error_codes import ErrorCode

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
        "provider_params": {
            "path": ".",
            "mirror_git_url": "",
            "mirror_git_token": "",
            "owner": "",
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
    "ErrorCode",
]
