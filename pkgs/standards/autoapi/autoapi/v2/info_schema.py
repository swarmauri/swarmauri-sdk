# autoapi/v2/info_schema.py
VALID_KEYS = {
    "disable_on",
    "write_only",
    "read_only",
    "default_factory",
    "examples",
    "hybrid",
    "py_type",
}
VALID_VERBS = {"create", "read", "update", "replace", "list", "delete", "clear"}


def check(meta: dict, attr: str, model: str):
    unknown = set(meta) - VALID_KEYS
    if unknown:
        raise RuntimeError(f"{model}.{attr}: bad autoapi keys {unknown}")
    for verb in meta.get("disable_on", []):
        if verb not in VALID_VERBS:
            raise RuntimeError(f"{model}.{attr}: invalid verb “{verb}”")
