"""
peagen.defaults
===============

Package-level **built-in configuration** for every Peagen component.

This module defines the absolute minimum set of settings required for Peagen
to start in an empty directory, even when no ``.peagen.toml`` is present:

* They provide **safe fall-backs** for local development and unit tests.
* They sit at the **lowest priority** in the config hierarchy:

      built-ins             <  
      .peagen.toml          <  
      task-group overrides  <  
      CLI/env flags         < 
      task overrides

* Gateways and workers still supply their own ``.peagen.toml``; these values
  are only used if a key is missing.

If you add a new setting elsewhere in the code-base, put its *most sensible
development default* here so nothing crashes when the file is absent.
"""


CONFIG = {
    # … existing keys …
    "gateway_url": "http://localhost:8000/rpc",   # ← lowest-priority default
    # Default Redis topics/queues used by the gateway & workers
    "control_queue": "control",      # worker ↔ gateway control messages
    "ready_queue": "queue",          # prefix for per-pool ready queues
    "pubsub": "task:update",         # channel for task event broadcasts
    "task_key": "task:{}",           # Redis hash per task
    # Sensible local defaults so `peagen local` works without a config file
    "queues": {"default_queue": "in_memory", "adapters": {"in_memory": {"maxsize": 0}}},
    "result_backends": {"default_backend": "local_fs", "adapters": {"local_fs": {"root_dir": "./task_runs"}}},
    "storage": {"default_filter": "file", "filters": {"file": {"output_dir": "./peagen_artifacts"}}},
    "secrets": {"default_secret": "env", "adapters": {"env": {"prefix": ""}}},
}
