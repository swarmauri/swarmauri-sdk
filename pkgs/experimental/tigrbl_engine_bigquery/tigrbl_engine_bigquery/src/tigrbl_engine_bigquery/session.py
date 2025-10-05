from __future__ import annotations
from typing import Any, Optional

class BigQuerySession:
    """Represents a logical unit of work against BigQuery.

    This wrapper is intentionally lightweight. It can be extended to integrate
    with your app's patterns (e.g., typed query helpers).

    Example
    -------
    >>> s = BigQuerySession(engine)
    >>> # rows = s.query("SELECT 1")   # requires google-cloud-bigquery installed & configured
    """
    def __init__(self, engine: Any) -> None:
        self.engine = engine
        self._client = None  # lazy

    # Optional: context manager
    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, tb):
        self.close()

    @property
    def client(self):
        """Lazily create a BigQuery client when first used."""
        if self._client is None:
            from google.cloud import bigquery  # heavy import delayed
            self._client = bigquery.Client(project=self.engine.project, **self.engine.kwargs)
        return self._client

    def query(self, sql: str, **job_config_kwargs):
        """Execute a SQL query and return the BigQuery ResultIterator.

        Notes
        -----
        - This method is a convenience for quick experiments. Production code
          should add schemas, timeouts, and retries as appropriate.
        """
        from google.cloud import bigquery
        job_config = bigquery.QueryJobConfig(**job_config_kwargs) if job_config_kwargs else None
        job = self.client.query(sql, job_config=job_config)
        return job.result()

    def close(self) -> None:
        try:
            if self._client is not None:
                self._client.close()
        finally:
            self._client = None
