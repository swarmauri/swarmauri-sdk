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
    for key in ("disable_on", "read_only"):
        verbs = meta.get(key, [])
        if isinstance(verbs, (list, tuple, set)):
            for verb in verbs:
                if verb not in VALID_VERBS:
                    raise RuntimeError(f"{model}.{attr}: invalid verb “{verb}”")
