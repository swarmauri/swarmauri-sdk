![Tigrbl Logo](https://raw.githubusercontent.com/swarmauri/swarmauri-sdk/master/assets/tigrbl.brand.theme.svg)

<p align="center">
    <a href="https://pepy.tech/project/tigrbl_engine_dataframe/">
        <img src="https://static.pepy.tech/badge/tigrbl_engine_dataframe/month" alt="PyPI - Downloads"/></a>
    <a href="https://hits.sh/github.com/swarmauri/swarmauri-sdk/tree/master/pkgs/experimental/tigrbl_engine_dataframe/">
        <img alt="Hits" src="https://hits.sh/github.com/swarmauri/swarmauri-sdk/tree/master/pkgs/experimental/tigrbl_engine_dataframe.svg"/></a>
    <a href="https://pypi.org/project/tigrbl_engine_dataframe/">
        <img src="https://img.shields.io/pypi/pyversions/tigrbl_engine_dataframe" alt="PyPI - Python Version"/></a>
    <a href="https://pypi.org/project/tigrbl_engine_dataframe/">
        <img src="https://img.shields.io/pypi/l/tigrbl_engine_dataframe" alt="PyPI - License"/></a>
    <a href="https://pypi.org/project/tigrbl_engine_dataframe/">
        <img src="https://img.shields.io/pypi/v/tigrbl_engine_dataframe?label=tigrbl_engine_dataframe&color=green" alt="PyPI - tigrbl_engine_dataframe"/></a>
</p>
---

# Bind by kind using the plugin's engine
@engine_ctx({"kind": "dataframe", "async": True, "tables": {"widgets": df}, "pks": {"widgets": "id"}})
class API:
    pass
```
