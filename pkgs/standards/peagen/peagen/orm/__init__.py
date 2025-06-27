"""
peagen.orm
==========

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
from .tenant.tenant import TenantModel, Tenant  # noqa: F401
from .tenant.user import UserModel, User  # noqa: F401
from .tenant.tenant_user_association import (  # noqa: F401
    TenantUserAssociationModel,
    TenantUserAssociation,
)

# ----------------------------------------------------------------------
# Repository domain
# ----------------------------------------------------------------------
from .repo.repository import RepositoryModel, Repository  # noqa: F401
from .repo.git_reference import GitReferenceModel, GitReference  # noqa: F401
from .repo.deploy_key import DeployKeyModel, DeployKey  # noqa: F401
from .repo.repository_deploy_key_association import (  # noqa: F401
    RepositoryDeployKeyAssociationModel,
    RepositoryDeployKeyAssociation,
)
from .repo.repository_user_association import (  # noqa: F401
    RepositoryUserAssociationModel,
    RepositoryUserAssociation,
)

# ----------------------------------------------------------------------
# Task / execution domain
# ----------------------------------------------------------------------
from .task.status import Status  # noqa: F401
from .task.task import TaskModel, Task  # noqa: F401
from .task.raw_blob import RawBlobModel, RawBlob  # noqa: F401
from .task.task_run import TaskRunModel, TaskRun  # noqa: F401
from .task.task_relation import TaskRelationModel, TaskRelation  # noqa: F401
from .task.task_run_relation_association import (  # noqa: F401
    TaskRunTaskRelationAssociationModel,
    TaskRunTaskRelationAssociation,
)

# ----------------------------------------------------------------------
# DOE / Render / Evolution domain
# ----------------------------------------------------------------------
from .specs.doe_spec import DoeSpecModel, DoeSpec  # noqa: F401
from .specs.evolve_spec import EvolveSpecModel, EvolveSpec  # noqa: F401
from .specs.project_payload import ProjectPayloadModel, ProjectPayload  # noqa: F401

# ----------------------------------------------------------------------
# Configuration / secrets
# ----------------------------------------------------------------------
from .config.peagen_toml_spec import PeagenTomlSpecModel, PeagenTomlSpec  # noqa: F401
from .config.secret import SecretModel, Secret  # noqa: F401

# ----------------------------------------------------------------------
# Infrastructure
# ----------------------------------------------------------------------
from .infra.pool import PoolModel, Pool  # noqa: F401
from .infra.worker import WorkerModel, Worker  # noqa: F401
from .infra.pool_worker_association import (  # noqa: F401
    PoolWorkerAssociationModel,
    PoolWorkerAssociation,
)

# ----------------------------------------------------------------------
# Result domain (evaluation & analysis)
# ----------------------------------------------------------------------
from .result.eval_result import EvalResultModel, EvalResult  # noqa: F401
from .result.analysis_result import AnalysisResultModel, AnalysisResult  # noqa: F401
from .git_mirror import GitMirror  # noqa: F401

# ----------------------------------------------------------------------
# Misc / security
# ----------------------------------------------------------------------
from .AbuseRecord import AbuseRecordModel, AbuseRecord  # noqa: F401
from .security.public_key import PublicKeyModel, PublicKey  # noqa: F401

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
    "GitMirror",
    # misc
    "AbuseRecordModel",
    "PublicKeyModel",
]
