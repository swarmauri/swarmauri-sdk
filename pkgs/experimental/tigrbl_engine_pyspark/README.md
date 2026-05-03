![Tigrbl Logo](https://raw.githubusercontent.com/swarmauri/swarmauri-sdk/master/assets/tigrbl.brand.theme.svg)

<p align="center">
    <a href="https://pepy.tech/project/tigrbl_engine_pyspark/">
        <img src="https://static.pepy.tech/badge/tigrbl_engine_pyspark/month" alt="PyPI - Downloads"/></a>
    <a href="https://hits.sh/github.com/swarmauri/swarmauri-sdk/tree/master/pkgs/experimental/tigrbl_engine_pyspark/">
        <img alt="Hits" src="https://hits.sh/github.com/swarmauri/swarmauri-sdk/tree/master/pkgs/experimental/tigrbl_engine_pyspark.svg"/></a>
    <a href="https://pypi.org/project/tigrbl_engine_pyspark/">
        <img src="https://img.shields.io/pypi/pyversions/tigrbl_engine_pyspark" alt="PyPI - Python Version"/></a>
    <a href="https://pypi.org/project/tigrbl_engine_pyspark/">
        <img src="https://img.shields.io/pypi/l/tigrbl_engine_pyspark" alt="PyPI - License"/></a>
    <a href="https://pypi.org/project/tigrbl_engine_pyspark/">
        <img src="https://img.shields.io/pypi/v/tigrbl_engine_pyspark?label=tigrbl_engine_pyspark&color=green" alt="PyPI - tigrbl_engine_pyspark"/></a>
</p>
---

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
