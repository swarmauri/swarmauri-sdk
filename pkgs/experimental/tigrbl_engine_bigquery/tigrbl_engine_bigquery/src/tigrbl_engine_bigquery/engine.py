from __future__ import annotations
from typing import Any, Callable, Tuple, Mapping, Optional
from .session import BigQuerySession

class BigQueryEngine:
    """Thin handle for BigQuery connectivity and defaults.

    Parameters
    ----------
    project : str | None
        Default GCP project to use for BigQuery.
    default_dataset : str | None
        Optional default dataset for unqualified table names.
    kwargs : Any
        Extra client kwargs (credentials, location, etc.).
    """
    def __init__(self, project: Optional[str] = None, default_dataset: Optional[str] = None, **kwargs: Any) -> None:
        self.project = project
        self.default_dataset = default_dataset
        self.kwargs = dict(kwargs)

def bigquery_engine(*, mapping: Optional[Mapping[str, object]] = None, spec: Any = None, dsn: Optional[str] = None, **kwargs: Any) -> Tuple[BigQueryEngine, Callable[[], Any]]:
    """Builder function used by tigrbl.

    tigrbl will call this as: build(mapping=mapping, spec=EngineSpec, dsn=dsn).
    Return a tuple of (engine_handle, session_factory).
    """
    m = dict(mapping or {})
    project = (m.get("project") or kwargs.get("project"))
    default_dataset = (m.get("default_dataset") or kwargs.get("default_dataset"))
    engine = BigQueryEngine(project=project, default_dataset=default_dataset, **kwargs)

    def session_factory() -> BigQuerySession:
        return BigQuerySession(engine)

    return engine, session_factory
