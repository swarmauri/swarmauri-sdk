from __future__ import annotations

from layout_engine.authoring.ctx.builder import TableCtx

from layout_engine_swarmakit_vue import (
    SWARMAKIT_VUE_PRESETS,
    SwarmakitAvatar,
    SwarmakitDataGrid,
    SwarmakitNotification,
    SwarmakitProgressBar,
    SwarmakitTimeline,
    compile_swarmakit_table,
    create_swarmakit_registry,
)


def test_registry_uses_swarmakit_exports() -> None:
    registry = create_swarmakit_registry(["avatar", "progress", "table"])

    avatar_spec = registry.get("avatar")
    assert avatar_spec.module == "@swarmakit/vue"
    assert avatar_spec.export == SWARMAKIT_VUE_PRESETS["avatar"]["export"]
    assert avatar_spec.defaults == SWARMAKIT_VUE_PRESETS["avatar"]["defaults"]

    table_spec = registry.get("table")
    assert table_spec.module == "@swarmakit/vue"
    assert table_spec.export == "DataGrid"


def test_compile_table_populates_component_metadata() -> None:
    table = TableCtx()
    first_row = table.row()
    first_row.col(size="s").add(
        SwarmakitAvatar(
            "avatar.alice", initials="AL", image_src="https://cdn.example/alice.png"
        ),
    )
    first_row.col(size="m").add(
        SwarmakitNotification(
            "notification.system",
            message="System check complete.",
            notification_type="success",
        ),
    )

    second_row = table.row()
    second_row.col(size="m").add(SwarmakitProgressBar("progress.training", progress=87))
    second_row.col(size="l").add(
        SwarmakitDataGrid(
            "grid.metrics",
            headers=["Metric", "Value"],
            data=[["Throughput", "1.6k/s"], ["Latency", "120ms"]],
        ),
        SwarmakitTimeline(
            "timeline.release",
            items=[
                {"id": 1, "label": "Spec", "completed": True},
                {"id": 2, "label": "Prototype", "completed": True},
                {"id": 3, "label": "Launch", "completed": False},
            ],
            active_index=2,
        ),
    )

    manifest = compile_swarmakit_table(table, width=960, height=720)
    tiles = {tile["id"]: tile for tile in manifest.model_dump()["tiles"]}

    avatar_tile = tiles["avatar.alice"]
    assert avatar_tile["component"]["module"] == "@swarmakit/vue"
    assert avatar_tile["component"]["export"] == "Avatar"
    assert avatar_tile["props"]["initials"] == "AL"

    grid_tile = tiles["grid.metrics"]
    assert grid_tile["component"]["export"] == "DataGrid"
    assert grid_tile["props"]["headers"] == ["Metric", "Value"]

    timeline_tile = tiles["timeline.release"]
    assert timeline_tile["component"]["export"] == "TimelineList"
    assert timeline_tile["props"]["activeIndex"] == 2
