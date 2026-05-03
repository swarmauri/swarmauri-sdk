![Tigrbl Logo](https://raw.githubusercontent.com/swarmauri/swarmauri-sdk/master/assets/tigrbl.brand.theme.svg)

<p align="center">
    <a href="https://pepy.tech/project/tigrbl_engine_pandas/">
        <img src="https://static.pepy.tech/badge/tigrbl_engine_pandas/month" alt="PyPI - Downloads"/></a>
    <a href="https://hits.sh/github.com/swarmauri/swarmauri-sdk/tree/master/pkgs/experimental/tigrbl_engine_pandas/tigrbl_engine_pandas/">
        <img alt="Hits" src="https://hits.sh/github.com/swarmauri/swarmauri-sdk/tree/master/pkgs/experimental/tigrbl_engine_pandas/tigrbl_engine_pandas.svg"/></a>
    <a href="https://pypi.org/project/tigrbl_engine_pandas/">
        <img src="https://img.shields.io/pypi/pyversions/tigrbl_engine_pandas" alt="PyPI - Python Version"/></a>
    <a href="https://pypi.org/project/tigrbl_engine_pandas/">
        <img src="https://img.shields.io/pypi/l/tigrbl_engine_pandas" alt="PyPI - License"/></a>
    <a href="https://pypi.org/project/tigrbl_engine_pandas/">
        <img src="https://img.shields.io/pypi/v/tigrbl_engine_pandas?label=tigrbl_engine_pandas&color=green" alt="PyPI - tigrbl_engine_pandas"/></a>
</p>
---

# Bind by kind using the plugin's engine
@engine_ctx({"kind": "pandas", "async": True, "tables": {"widgets": df}, "pks": {"widgets": "id"}})
class API:
    pass
```
