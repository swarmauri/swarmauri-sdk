"""
peagen.orm
==========

• Aggregates **all** SQLAlchemy ORM classes.
• No engine/session helpers—those live elsewhere.

`peagen.models` is deprecated and now forwards to this package.
"""

from __future__ import annotations

# ----------------------------------------------------------------------
# Base (declarative metadata root)
# ----------------------------------------------------------------------
from .base import Base  # noqa: F401  (re-exported via __all__)

# ----------------------------------------------------------------------
# Tenant domain
# ----------------------------------------------------------------------
from .tenant.tenant import TenantModel  # noqa: F401
from .tenant.user import UserModel  # noqa: F401
from .tenant.tenant_user_association import (  # noqa: F401
    TenantUserAssociationModel,
)

# ----------------------------------------------------------------------
# Repository domain
# ----------------------------------------------------------------------
from .repo.repository import RepositoryModel  # noqa: F401
from .repo.git_reference import GitReferenceModel  # noqa: F401
from .repo.git_mirror import GitMirrorModel  # noqa: F401
from .repo.deploy_key import DeployKeyModel  # noqa: F401
from .repo.repository_deploy_key_association import (  # noqa: F401
    RepositoryDeployKeyAssociationModel,
)
from .repo.repository_user_association import (  # noqa: F401
    RepositoryUserAssociationModel,
)

# ----------------------------------------------------------------------
# Task / execution domain
# ----------------------------------------------------------------------
from .status import Status  # noqa: F401
from .task import TaskModel  # noqa: F401
from .task.raw_blob import RawBlobModel  # noqa: F401
from .task_run import TaskRunModel  # noqa: F401
from .task.task_relation import TaskRelationModel  # noqa: F401
from .task.task_run_relation_association import (  # noqa: F401
    TaskRunTaskRelationAssociationModel,
)

# ----------------------------------------------------------------------
# DOE / Render / Evolution domain
# ----------------------------------------------------------------------
from .specs.doe_spec import DoeSpecModel  # noqa: F401
from .specs.evolve_spec import EvolveSpecModel  # noqa: F401
from .specs.project_payload import ProjectPayloadModel  # noqa: F401

# ----------------------------------------------------------------------
# Configuration / secrets
# ----------------------------------------------------------------------
from .config.peagen_toml_spec import PeagenTomlSpecModel  # noqa: F401
from .config.secret import SecretModel  # noqa: F401

# ----------------------------------------------------------------------
# Infrastructure
# ----------------------------------------------------------------------
from .infra.pool import PoolModel  # noqa: F401
from .infra.worker import WorkerModel  # noqa: F401
from .infra.pool_worker_association import (  # noqa: F401
    PoolWorkerAssociationModel,
)

# ----------------------------------------------------------------------
# Result domain (evaluation & analysis)
# ----------------------------------------------------------------------
from .result.eval_result import EvalResultModel  # noqa: F401
from .result.analysis_result import AnalysisResultModel  # noqa: F401

# ----------------------------------------------------------------------
# Misc / security
# ----------------------------------------------------------------------
from .AbuseRecord import AbuseRecordModel  # noqa: F401
from .security.public_key import PublicKeyModel  # noqa: F401

# ----------------------------------------------------------------------
# Public re-exports
# ----------------------------------------------------------------------
__all__: list[str] = [
    # base
    "Base",
    # tenant
    "TenantModel",
    "UserModel",
    "TenantUserAssociationModel",
    # repo
    "RepositoryModel",
    "GitReferenceModel",
    "DeployKeyModel",
    "RepositoryDeployKeyAssociationModel",
    "RepositoryUserAssociationModel",
    # task
    "TaskModel",
    "RawBlobModel",
    "Status",
    "TaskRunModel",
    "TaskRelationModel",
    "TaskRunTaskRelationAssociationModel",
    # evolution
    "DoeSpecModel",
    "EvolveSpecModel",
    "ProjectPayloadModel",
    # config
    "PeagenTomlSpecModel",
    "SecretModel",
    # infra
    "PoolModel",
    "WorkerModel",
    "PoolWorkerAssociationModel",
    # result
    "EvalResultModel",
    "AnalysisResultModel",
    # misc
    "AbuseRecordModel",
    "PublicKeyModel",
]

# Trigger Pydantic schema generation at import time
try:  # pragma: no cover - best effort
    import importlib

    importlib.import_module("peagen.schemas")
except Exception:  # noqa: BLE001
    pass
