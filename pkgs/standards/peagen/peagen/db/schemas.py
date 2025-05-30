from __future__ import annotations

"""Pydantic models for CRUD operations on Peagen resources."""

from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel


# ---------------------------------------------------------------------------
# Project Schemas
# ---------------------------------------------------------------------------
class ProjectBase(BaseModel):
    """Shared attributes for projects."""

    name: str
    description: Optional[str] = None


class ProjectCreate(ProjectBase):
    """Schema for creating a project."""

    pass


class ProjectUpdate(BaseModel):
    """Schema for updating a project."""

    name: Optional[str] = None
    description: Optional[str] = None


class ProjectRead(ProjectBase):
    """Read schema for projects."""

    id: str
    date_created: datetime
    last_modified: datetime
    designs: List[DesignOfExperimentRead] = []
    render_runs: List[RenderRunRead] = []
    artifacts: List[ArtifactRead] = []
    evolution_candidates: List[EvolutionCandidateRead] = []

    class Config:
        orm_mode = True


# ---------------------------------------------------------------------------
# DesignOfExperiment Schemas
# ---------------------------------------------------------------------------
class DesignOfExperimentBase(BaseModel):
    """Shared attributes for DOE objects."""

    project_id: str
    name: str
    spec_path: Optional[str] = None


class DesignOfExperimentCreate(DesignOfExperimentBase):
    """Schema for creating a DOE entry."""

    pass


class DesignOfExperimentUpdate(BaseModel):
    """Schema for updating a DOE entry."""

    name: Optional[str] = None
    spec_path: Optional[str] = None


class DesignOfExperimentRead(DesignOfExperimentBase):
    """Read schema for design of experiments."""

    id: str
    date_created: datetime
    last_modified: datetime

    class Config:
        orm_mode = True


# ---------------------------------------------------------------------------
# RenderRun Schemas
# ---------------------------------------------------------------------------
class RenderRunBase(BaseModel):
    """Shared attributes for render runs."""

    project_id: str
    status: Optional[str] = None


class RenderRunCreate(RenderRunBase):
    """Schema for creating a render run."""

    pass


class RenderRunUpdate(BaseModel):
    """Schema for updating a render run."""

    status: Optional[str] = None


class RenderRunRead(RenderRunBase):
    """Read schema for render runs."""

    id: str
    date_created: datetime
    last_modified: datetime
    artifacts: List[ArtifactRead] = []

    class Config:
        orm_mode = True


# ---------------------------------------------------------------------------
# Artifact Schemas
# ---------------------------------------------------------------------------
class ArtifactBase(BaseModel):
    """Shared attributes for artifacts."""

    project_id: str
    path: str
    render_run_id: Optional[str] = None


class ArtifactCreate(ArtifactBase):
    """Schema for creating an artifact."""

    pass


class ArtifactUpdate(BaseModel):
    """Schema for updating an artifact."""

    path: Optional[str] = None
    render_run_id: Optional[str] = None


class ArtifactRead(ArtifactBase):
    """Read schema for artifacts."""

    id: str
    date_created: datetime

    class Config:
        orm_mode = True


# ---------------------------------------------------------------------------
# EvolutionCandidate Schemas
# ---------------------------------------------------------------------------
class EvolutionCandidateBase(BaseModel):
    """Shared attributes for evolution candidates."""

    project_id: str
    artifact_id: Optional[str] = None
    score: Optional[float] = None


class EvolutionCandidateCreate(EvolutionCandidateBase):
    """Schema for creating an evolution candidate."""

    pass


class EvolutionCandidateUpdate(BaseModel):
    """Schema for updating an evolution candidate."""

    artifact_id: Optional[str] = None
    score: Optional[float] = None


class EvolutionCandidateRead(EvolutionCandidateBase):
    """Read schema for evolution candidates."""

    id: str
    date_created: datetime

    class Config:
        orm_mode = True

