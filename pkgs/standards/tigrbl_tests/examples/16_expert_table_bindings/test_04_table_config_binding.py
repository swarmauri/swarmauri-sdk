"""Lesson 16: table configuration bindings.

This module demonstrates how table configuration metadata is captured on the
API instance. The configuration registry keeps engine settings close to the
model, providing a structured way to inspect runtime metadata without
searching the class hierarchy manually.
"""

from tigrbl import Base, TigrblRouter, engine_ctx
from tigrbl.engine.shortcuts import mem
from tigrbl.orm.mixins import GUIDPk
from tigrbl.types import Column, String


def test_table_binding_reads_table_config():
    """Engine configuration stored on a model appears in the API table config."""

    class Widget(Base, GUIDPk):
        __tablename__ = "lesson_table_config"
        __allow_unmapped__ = True

        name = Column(String, nullable=False)

    engine_ctx(kind="sqlite", mode="memory", async_=False)(Widget)

    router = TigrblRouter(engine=mem(async_=False))
    router.include_model(Widget)

    config = router.table_config[Widget.__name__]
    assert config["engine"]["kind"] == "sqlite"


def test_table_config_registry_is_model_specific():
    """Each model keeps its own configuration entry in the registry."""

    class Widget(Base, GUIDPk):
        __tablename__ = "lesson_table_config_primary"
        __allow_unmapped__ = True

        name = Column(String, nullable=False)

    engine_ctx(kind="sqlite", mode="memory", async_=False)(Widget)

    class Gadget(Base, GUIDPk):
        __tablename__ = "lesson_table_config_secondary"
        __allow_unmapped__ = True

        name = Column(String, nullable=False)

    engine_ctx(kind="sqlite", mode="memory", async_=False)(Gadget)

    router = TigrblRouter(engine=mem(async_=False))
    router.include_model(Widget)
    router.include_model(Gadget)

    assert router.table_config[Widget.__name__]["engine"]["kind"] == "sqlite"
    assert router.table_config[Gadget.__name__]["engine"]["kind"] == "sqlite"
