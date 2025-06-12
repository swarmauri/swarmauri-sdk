from __future__ import annotations

import uuid

from sqlalchemy import Boolean, Column, JSON, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import declarative_base

Base = declarative_base()


class _BasePlan(Base):
    __abstract__ = True

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String, nullable=False)
    description = Column(String, nullable=True)
    data = Column(JSON, nullable=False, default=dict)
    locked = Column(Boolean, nullable=False, default=False)


class DOEPlan(_BasePlan):
    __tablename__ = "doe_plans"


class EvaluationPlan(_BasePlan):
    __tablename__ = "evaluation_plans"


class EvolvePlan(_BasePlan):
    __tablename__ = "evolve_plans"


class AnalysisPlan(_BasePlan):
    __tablename__ = "analysis_plans"

