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
}

# Built-in Redis key patterns
WORKER_KEY = "worker:{}"        # format with workerId
DEP_SET = "task:deps:{}"        # deps for task X
CHILD_SET = "task:children:{}"  # children dependent on X
LABEL_SET = "label:{}"          # tasks under a label

# Default TTL values (seconds)
WORKER_TTL = 15
TASK_TTL = 24 * 3600

