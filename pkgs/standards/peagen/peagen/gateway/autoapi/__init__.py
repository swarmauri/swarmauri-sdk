"""
AutoAPI integration for Peagen Gateway
"""

from peagen.gateway.db import Session
from peagen.orm import Base
from peagen.orm.infra.pool import PoolModel
from peagen.orm.infra.worker import WorkerModel
from peagen.orm.repo.deploy_key import DeployKeyModel  # Adjust import path as needed
from peagen.orm.task.task import TaskModel
from autoapi import AutoAPI

api = AutoAPI(
    base=Base,
    get_db=Session,
    include={TaskModel, PoolModel, WorkerModel, DeployKeyModel},
    prefix="/api/v1",
)

router = api.router

# Import all hooks to register them
from .hooks import *
