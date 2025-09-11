"""peagen.defaults
=================
Package-level built-in configuration and constants.
"""

import os
import uuid
from pathlib import Path


# ───────────────── CTX DEFAULT FALLBACKS ─────────────────────────
DEFAULT_GATEWAY = "http://localhost:8000/rpc"
GATEWAY_URL = DEFAULT_GATEWAY

# ───────────────────────── TIMEOUTS ──────────────────────────────
# Default timeout for JSON-RPC requests in seconds.
RPC_TIMEOUT = 30.0

# ───────────────────────── Root Paths ────────────────────────────
# Base directory Peagen uses for caches, mirrors, work-trees, etc.
# Can be overridden with the environment variable `PEAGEN_ROOT_DIR`.
ROOT_DIR = os.getenv("PEAGEN_ROOT_DIR", "~/.cache/peagen")

# ───────────────────────── Peagen Lock ───────────────────────────
# Directory for repository lock files, under the root path.
LOCK_DIR = os.path.join(ROOT_DIR, "locks")


def lock_dir() -> Path:
    """Return the directory used for repository locks."""
    return Path(os.getenv("PEAGEN_LOCK_DIR", LOCK_DIR)).expanduser()


# Convenience accessor for the root directory.
def root_dir() -> Path:
    """Return Peagen’s root working directory."""
    return Path(ROOT_DIR).expanduser()


# ─────────────────────────── GIT Shadow ─────────────────────────────

# Git Shadow Mirror
GIT_SHADOW_BASE = os.getenv("PEAGEN_GIT_SHADOW_URL", "https://git.peagen.com")
GIT_SHADOW_TOKEN = os.getenv("PEAGEN_GIT_SHADOW_PAT", None)


# ───────────────────────── Default Resources ────────────────────────

## DEFAULT RESOURCES UUIDS
DEFAULT_TENANT_ID = uuid.UUID("FFFFFFFF-0000-0000-0000-000000000000")
DEFAULT_TENANT_EMAIL = "tenant@example.com"
DEFAULT_TENANT_NAME = "Public"
DEFAULT_TENANT_SLUG = "public"

DEFAULT_POOL_ID = uuid.UUID("FFFFFFFF-0000-0000-0000-000000000001")
DEFAULT_POOL_NAME = "default"
DEFAULT_SUPER_USER_ID = uuid.UUID("FFFFFFFF-0000-0000-0000-000000000099")
DEFAULT_SUPER_USER_EMAIL = "admin@example.com"

DEFAULT_SUPER_USER_ID_2 = uuid.UUID("FFFFFFFF-0000-0000-0000-000000000100")
DEFAULT_SUPER_USER_EMAIL_2 = "admi2n@example.com"

# ──────────────────────── Plugin Config ────────────────────────────

# Base configuration used when no `.peagen.toml` is present.
CONFIG = {
    "queues": {"default_queue": "in_memory", "adapters": {"in_memory": {"maxsize": 0}}},
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


# ─────────────────────────── Pools ────────────────────────────
DEFAULT_POOL = "default"
"""Default worker pool used when none is specified via environment variables."""

# ─────────────────────────── Workers ────────────────────────────
# workers are stored as hashes:  queue.hset worker:<id> pool url advertises last_seen
WORKER_KEY = "worker:{}"  # format with workerId
WORKER_TTL = 15  # seconds before a worker is considered dead

# ─────────────────────────── Task ────────────────────────────
TASK_TTL = 24 * 3600  # 24 h, adjust as needed

TASK_KEY = "task:{}"
"""Redis key template for task metadata."""

# ─────────────────────────── Queue ────────────────────────────────

CONTROL_QUEUE = "control"
"""Worker ↔ gateway control messages queue."""

READY_QUEUE = "queue"
"""Prefix for per-pool ready queues."""

PUBSUB_CHANNEL = "task:update"
"""Channel name for task event broadcasts."""

# ─────────────────────────── Abuse ────────────────────────────

BAN_THRESHOLD = 10

# ─────────────────────────── Exports ────────────────────────────

__all__ = [
    "CONFIG",
    "ROOT_DIR",
    "LOCK_DIR",
    "root_dir",
    "lock_dir",
    "WORKER_KEY",
    "WORKER_TTL",
    "BAN_THRESHOLD",
    "CONTROL_QUEUE",
    "READY_QUEUE",
    "PUBSUB_CHANNEL",
    "TASK_KEY",
    "DEFAULT_POOL",
    "RPC_TIMEOUT",
]
