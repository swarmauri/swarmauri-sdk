"""Backward-compatible engine resolver exports."""

from ..mapping.engine_resolver import *  # noqa: F401,F403
from ..mapping import engine_resolver as _engine_resolver

_SECRET_KEYS = _engine_resolver._SECRET_KEYS
_hash_secret = _engine_resolver._hash_secret
_spec_key = _engine_resolver._spec_key
