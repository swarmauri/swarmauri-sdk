# autoapi/v3/impl/schema/__init__.py
import warnings
warnings.warn(
    "autoapi.v3.impl.schema is deprecated; use autoapi.v3.schema",
    DeprecationWarning, stacklevel=2
)
from autoapi.v3.schema import *  # re-export
