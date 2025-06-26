"""
peagen.models
=============

• Aggregates **all** SQLAlchemy ORM classes.
• No engine/session helpers—those live elsewhere.
"""

from __future__ import annotations

# ----------------------------------------------------------------------
# Base (declarative metadata root)
# ----------------------------------------------------------------------
from .base import Base  # noqa: F401  (re-exported via __all__)

# ----------------------------------------------------------------------
# Tenant domain
# ----------------------------------------------------------------------
from .tenant.tenant import Tenant  # noqa: F401
from .tenant.user import User  # noqa: F401
from .tenant.tenant_user_association import TenantUserAssociation  # noqa: F401

# ----------------------------------------------------------------------
# Repository domain
# ----------------------------------------------------------------------
from .repo.repository import Repository  # noqa: F401
from .repo.git_reference import GitReference  # noqa: F401
from .repo.deploy_key import DeployKey  # noqa: F401
from .repo.repository_user_association import RepositoryUserAssociation  # noqa: F401

# ----------------------------------------------------------------------
# Task / execution domain
# ----------------------------------------------------------------------
from .task.status import Status  # noqa: F401
from .task.task_payload import TaskPayload  # noqa: F401
from .task.raw_blob import RawBlob  # noqa: F401
from .task.task_run import TaskRun  # noqa: F401
from .task.task_relation import TaskRelation  # noqa: F401
from .task.task_run_relation_association import (
    TaskRunTaskRelationAssociation,  # noqa: F401
)
from .task.project_task_association import ProjectTaskAssociation  # noqa: F401

# ----------------------------------------------------------------------
# DOE / Render / Evolution domain
# ----------------------------------------------------------------------
from .specs.doe_spec import DoeSpec  # noqa: F401
from .specs.evolve_spec import EvolveSpec  # noqa: F401
from .specs.project_payload import ProjectPayload  # noqa: F401

# ----------------------------------------------------------------------
# Configuration / secrets
# ----------------------------------------------------------------------
from .config.peagen_toml_spec import PeagenTomlSpec  # noqa: F401
from .config.secret import Secret  # noqa: F401

# ----------------------------------------------------------------------
# Infrastructure
# ----------------------------------------------------------------------
from .infra.pool import Pool  # noqa: F401
from .infra.worker import Worker  # noqa: F401
from .infra.pool_worker_association import PoolWorkerAssociation  # noqa: F401

# ----------------------------------------------------------------------
# Result domain (evaluation & analysis)
# ----------------------------------------------------------------------
from .result.eval_result import EvalResult  # noqa: F401
from .result.analysis_result import AnalysisResult  # noqa: F401

# ----------------------------------------------------------------------
# Misc / security
# ----------------------------------------------------------------------
from .abuse import AbuseRecord  # noqa: F401

# ----------------------------------------------------------------------
# Public re-exports
# ----------------------------------------------------------------------
__all__: list[str] = [
    # base
    "Base",
    # tenant
    "Tenant",
    "User",
    "TenantUserAssociation",
    # repo
    "Repository",
    "GitReference",
    "DeployKey",
    "RepositoryUserAssociation",
    # task
    "TaskPayload",
    "RawBlob",
    "Status",
    "TaskRun",
    "TaskRelation",
    "TaskRunTaskRelationAssociation",
    "ProjectTaskAssociation",
    # evolution
    "DoeSpec",
    "EvolveSpec",
    "ProjectPayload",
    # config
    "PeagenTomlSpec",
    "Secret",
    # infra
    "Pool",
    "Worker",
    "PoolWorkerAssociation",
    # result
    "EvalResult",
    "AnalysisResult",
    # misc
    "AbuseRecord",
]
