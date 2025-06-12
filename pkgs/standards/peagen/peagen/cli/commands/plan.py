from __future__ import annotations

import json
from pathlib import Path
from typing import Type

import typer

from peagen.gateway.db import Session
from peagen.models.plan import (
    DOEPlan,
    EvaluationPlan,
    EvolvePlan,
    AnalysisPlan,
)

local_plan_app = typer.Typer(help="Manage plan objects.")

_PLAN_MAP = {
    "doe": DOEPlan,
    "evaluation": EvaluationPlan,
    "evolve": EvolvePlan,
    "analysis": AnalysisPlan,
}


def _get_cls(kind: str) -> Type[_PLAN_MAP[str]]:
    cls = _PLAN_MAP.get(kind)
    if cls is None:
        raise typer.BadParameter(f"Unknown plan type '{kind}'.")
    return cls


@local_plan_app.command("create")
def create(
    kind: str = typer.Argument(..., help="Plan type"),
    file: Path = typer.Argument(..., exists=True, help="JSON file with plan data"),
) -> None:
    data = json.loads(file.read_text())
    cls = _get_cls(kind)

    async def _run() -> None:
        async with Session() as s:
            plan = cls(
                name=data.get("name", kind),
                description=data.get("description"),
                data=data,
            )
            s.add(plan)
            await s.commit()
            typer.echo(str(plan.id))

    typer.run(_run)


@local_plan_app.command("read")
def read(kind: str, plan_id: str) -> None:
    cls = _get_cls(kind)

    async def _run() -> None:
        async with Session() as s:
            plan = await s.get(cls, plan_id)
            if plan is None:
                raise typer.Exit(code=1)
            typer.echo(json.dumps({
                "id": str(plan.id),
                "name": plan.name,
                "description": plan.description,
                "data": plan.data,
                "locked": plan.locked,
            }, indent=2))

    typer.run(_run)


@local_plan_app.command("update")
def update(kind: str, plan_id: str, file: Path) -> None:
    cls = _get_cls(kind)
    data = json.loads(file.read_text())

    async def _run() -> None:
        async with Session() as s:
            plan = await s.get(cls, plan_id)
            if plan is None or plan.locked:
                raise typer.Exit(code=1)
            plan.name = data.get("name", plan.name)
            plan.description = data.get("description", plan.description)
            plan.data = data.get("data", plan.data)
            await s.commit()

    typer.run(_run)


@local_plan_app.command("lock")
def lock(kind: str, plan_id: str) -> None:
    cls = _get_cls(kind)

    async def _run() -> None:
        async with Session() as s:
            plan = await s.get(cls, plan_id)
            if plan is None:
                raise typer.Exit(code=1)
            plan.locked = True
            await s.commit()

    typer.run(_run)

