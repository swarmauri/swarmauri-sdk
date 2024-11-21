from swarmauri.utils._lazy_import import _lazy_import

# List of tracing names (file names without the ".py" extension) and corresponding class names
tracing_files = [
    ("swarmauri.tracing.concrete.CallableTracer", "CallableTracer"),
    ("from swarmauri.tracing.concrete.ChainTracer", "ChainTracer"),
    ("swarmauri.tracing.concrete.SimpleTraceContext", "SimpleTraceContext"),
    ("swarmauri.tracing.concrete.TracedVariable", "TracedVariable"),
    ("swarmauri.tracing.concrete.VariableTracer", "VariableTracer"),
]

# Lazy loading of tracings, storing them in variables
for module_name, class_name in tracing_files:
    globals()[class_name] = _lazy_import(module_name, class_name)

# Adding the lazy-loaded tracings to __all__
__all__ = [class_name for _, class_name in tracing_files]
