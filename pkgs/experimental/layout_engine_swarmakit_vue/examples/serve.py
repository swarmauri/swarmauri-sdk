"""Run a FastAPI + Uvicorn demo that renders Swarmakit Vue components."""

from __future__ import annotations

import uvicorn

from layout_engine.authoring.ctx.builder import TableCtx

from layout_engine_swarmakit_vue import (
    SwarmakitAvatar,
    SwarmakitDataGrid,
    SwarmakitNotification,
    SwarmakitProgressBar,
    create_swarmakit_fastapi_app,
)


def build_table() -> TableCtx:
    table = TableCtx()
    hero = table.row()
    hero.col(size="s").add(
        SwarmakitAvatar(
            "avatar.ops", initials="OP", image_src="https://cdn.example/ops.png"
        ),
    )
    hero.col(size="m").add(
        SwarmakitNotification(
            "notification.ops",
            message="Swarmakit control plane is healthy.",
            notification_type="success",
        ),
        SwarmakitProgressBar("progress.ops", progress=72),
    )
    hero.col(size="l").add(
        SwarmakitDataGrid(
            "grid.ops",
            headers=["Service", "State"],
            data=[["Layout Compiler", "Ready"], ["Vue Runtime", "Ready"]],
        ),
    )
    return table


def run() -> None:
    app = create_swarmakit_fastapi_app(build_table(), title="Swarmakit Layout Demo")
    uvicorn.run(app, host="127.0.0.1", port=8899)


if __name__ == "__main__":  # pragma: no cover - manual entry point
    run()
