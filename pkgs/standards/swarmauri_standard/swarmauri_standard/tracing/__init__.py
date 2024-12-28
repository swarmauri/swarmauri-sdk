# from swarmauri.utils._lazy_import import _lazy_import

# # List of tracing names (file names without the ".py" extension) and corresponding class names
# tracing_files = [
#     ("swarmauri_standard.tracing.CallableTracer", "CallableTracer"),
#     ("swarmauri_standard.tracing.ChainTracer", "ChainTracer"),
#     ("swarmauri_standard.tracing.SimpleTraceContext", "SimpleTraceContext"),
#     ("swarmauri_standard.tracing.TracedVariable", "TracedVariable"),
#     ("swarmauri_standard.tracing.VariableTracer", "VariableTracer"),
# ]

# # Lazy loading of tracings, storing them in variables
# for module_name, class_name in tracing_files:
#     globals()[class_name] = _lazy_import(module_name, class_name)

# # Adding the lazy-loaded tracings to __all__
# __all__ = [class_name for _, class_name in tracing_files]
