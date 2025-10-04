# tigrbl_engine_pyspark

A minimal PySpark engine plugin for **tigrbl**. It registers the `pyspark` engine
via the `tigrbl.engine` entry point, so tigrbl discovers it automatically on import.

## Install

```bash
pip install -e .
```

## Usage

```python
from tigrbl.engine import EngineSpec

spec = EngineSpec(kind="pyspark")
provider = spec.to_provider()
engine, session_factory = provider.build()

sess = session_factory()     # has .spark (SparkSession) and .close()
sess.spark.sql("SELECT 1").show()
```

## Notes

- Entry point group: `tigrbl.engine`
- Target: `tigrbl_engine_pyspark:register`
