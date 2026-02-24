import logging

from tigrbl.schema import collect as schema_collect


class _ListHandler(logging.Handler):
    def __init__(self, records):
        super().__init__()
        self._records = records

    def emit(self, record: logging.LogRecord) -> None:
        self._records.append(record)


def _set_uvicorn_level(level: int) -> int:
    logger = logging.getLogger("uvicorn")
    previous = logger.level
    logger.setLevel(level)
    return previous


def test_verbosity_level_does_not_force_debug() -> None:
    previous_level = _set_uvicorn_level(logging.INFO)
    try:
        assert schema_collect.logger.name == "uvicorn"
        assert logging.getLogger("uvicorn").level == logging.INFO
    finally:
        logging.getLogger("uvicorn").setLevel(previous_level)


def test_verbosity_situations_skip_debug_without_verbose() -> None:
    previous_level = _set_uvicorn_level(logging.INFO)
    logger = logging.getLogger("uvicorn")
    records: list[logging.LogRecord] = []
    handler = _ListHandler(records)
    logger.addHandler(handler)
    try:
        schema_collect.logger.debug("tigrbl verbosity debug")
        assert not records
    finally:
        logger.removeHandler(handler)
        logging.getLogger("uvicorn").setLevel(previous_level)


def test_verbosity_formatting_uses_uvicorn_logger() -> None:
    previous_level = _set_uvicorn_level(logging.DEBUG)
    logger = logging.getLogger("uvicorn")
    records: list[logging.LogRecord] = []
    handler = _ListHandler(records)
    logger.addHandler(handler)
    try:
        schema_collect.logger.debug("tigrbl formatting %s", "ok")
        record = next(
            record
            for record in records
            if record.getMessage() == "tigrbl formatting ok"
        )
        assert record.name == "uvicorn"
        assert record.levelname == "DEBUG"
    finally:
        logger.removeHandler(handler)
        logging.getLogger("uvicorn").setLevel(previous_level)
