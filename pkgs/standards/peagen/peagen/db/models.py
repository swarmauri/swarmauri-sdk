from __future__ import annotations

"""Database models for Peagen resources."""

from datetime import datetime
import uuid

from sqlalchemy import Column, DateTime, Float, ForeignKey, String
from sqlalchemy.orm import declarative_base, relationship


Base = declarative_base()


def generate_uuid() -> str:
    """Return a new hexadecimal UUID string."""
    return uuid.uuid4().hex


class Project(Base):
    """SQLAlchemy model for project metadata."""

    __tablename__ = "projects"

    id = Column(String, primary_key=True, default=generate_uuid, unique=True, index=True)
    name = Column(String, nullable=False, unique=True)
    description = Column(String, nullable=True)
    date_created = Column(DateTime(timezone=True), default=datetime.utcnow)
    last_modified = Column(DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow)

    designs = relationship("DesignOfExperiment", back_populates="project")
    render_runs = relationship("RenderRun", back_populates="project")
    artifacts = relationship("Artifact", back_populates="project")
    evolution_candidates = relationship("EvolutionCandidate", back_populates="project")


class DesignOfExperiment(Base):
    """SQLAlchemy model for design of experiments specifications."""

    __tablename__ = "design_of_experiments"

    id = Column(String, primary_key=True, default=generate_uuid, unique=True, index=True)
    project_id = Column(String, ForeignKey("projects.id"), nullable=False)
    name = Column(String, nullable=False)
    spec_path = Column(String, nullable=True)
    date_created = Column(DateTime(timezone=True), default=datetime.utcnow)
    last_modified = Column(DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow)

    project = relationship("Project", back_populates="designs")


class RenderRun(Base):
    """SQLAlchemy model representing a render execution."""

    __tablename__ = "render_runs"

    id = Column(String, primary_key=True, default=generate_uuid, unique=True, index=True)
    project_id = Column(String, ForeignKey("projects.id"), nullable=False)
    status = Column(String, nullable=True)
    date_created = Column(DateTime(timezone=True), default=datetime.utcnow)
    last_modified = Column(DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow)

    project = relationship("Project", back_populates="render_runs")
    artifacts = relationship("Artifact", back_populates="render_run")


class Artifact(Base):
    """SQLAlchemy model for build or render artifacts."""

    __tablename__ = "artifacts"

    id = Column(String, primary_key=True, default=generate_uuid, unique=True, index=True)
    project_id = Column(String, ForeignKey("projects.id"), nullable=False)
    render_run_id = Column(String, ForeignKey("render_runs.id"), nullable=True)
    path = Column(String, nullable=False)
    date_created = Column(DateTime(timezone=True), default=datetime.utcnow)

    project = relationship("Project", back_populates="artifacts")
    render_run = relationship("RenderRun", back_populates="artifacts")


class EvolutionCandidate(Base):
    """SQLAlchemy model for potential iterations or optimizations."""

    __tablename__ = "evolution_candidates"

    id = Column(String, primary_key=True, default=generate_uuid, unique=True, index=True)
    project_id = Column(String, ForeignKey("projects.id"), nullable=False)
    artifact_id = Column(String, ForeignKey("artifacts.id"), nullable=True)
    score = Column(Float, nullable=True)
    date_created = Column(DateTime(timezone=True), default=datetime.utcnow)

    project = relationship("Project", back_populates="evolution_candidates")
    artifact = relationship("Artifact")

