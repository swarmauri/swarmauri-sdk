import importlib
import logging

from tigrbl.bindings.rest import collection as rest_collection
from tigrbl.schema import collect as schema_collect


def _set_uvicorn_level(level: int) -> int:
    logger = logging.getLogger("uvicorn")
    previous = logger.level
    logger.setLevel(level)
    return previous


def test_verbosity_level_does_not_force_debug() -> None:
    previous_level = _set_uvicorn_level(logging.INFO)
    try:
        importlib.reload(schema_collect)
        assert logging.getLogger("uvicorn").level == logging.INFO
    finally:
        logging.getLogger("uvicorn").setLevel(previous_level)


def test_verbosity_situations_emit_debug_when_verbose(caplog) -> None:
    previous_level = _set_uvicorn_level(logging.DEBUG)
    try:
        caplog.clear()
        caplog.set_level(logging.DEBUG, logger="uvicorn")
        rest_collection.logger.debug("tigrbl verbosity debug")
        assert any(
            record.getMessage() == "tigrbl verbosity debug" for record in caplog.records
        )
    finally:
        logging.getLogger("uvicorn").setLevel(previous_level)


def test_verbosity_formatting_uses_uvicorn_logger(caplog) -> None:
    previous_level = _set_uvicorn_level(logging.DEBUG)
    try:
        caplog.clear()
        caplog.set_level(logging.DEBUG, logger="uvicorn")
        rest_collection.logger.debug("tigrbl formatting %s", "ok")
        record = next(
            record
            for record in caplog.records
            if record.getMessage() == "tigrbl formatting ok"
        )
        assert record.name == "uvicorn"
        assert record.levelname == "DEBUG"
    finally:
        logging.getLogger("uvicorn").setLevel(previous_level)
