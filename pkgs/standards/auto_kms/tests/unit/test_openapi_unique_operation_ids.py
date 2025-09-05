import importlib
import warnings


def test_openapi_operation_ids_unique():
    app_module = importlib.reload(importlib.import_module("auto_kms.app"))
    with warnings.catch_warnings():
        warnings.simplefilter("error")
        schema = app_module.app.openapi()
    op_ids = [
        op["operationId"]
        for methods in schema["paths"].values()
        for op in methods.values()
    ]
    assert len(op_ids) == len(set(op_ids))
