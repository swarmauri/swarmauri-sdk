from swarmauri.utils._lazy_import import _lazy_import

# List of llms names (file names without the ".py" extension) and corresponding class names
llms_files = [
    ("swarmauri_standard.llms.BlackForestImgGenModel", "BlackForestImgGenModel"),
    ("swarmauri_standard.llms.DeepInfraImgGenModel", "DeepInfraImgGenModel"),
    ("swarmauri_standard.llms.FalAIImgGenModel", "FalAIImgGenModel"),
    ("swarmauri_standard.llms.HyperbolicImgGenModel", "HyperbolicImgGenModel"),
    ("swarmauri_standard.llms.OpenAIImgGenModel", "OpenAIImgGenModel"),
]

# Lazy loading of llms classes, storing them in variables
for module_name, class_name in llms_files:
    globals()[class_name] = _lazy_import(module_name, class_name)

# Adding the lazy-loaded llms classes to __all__
__all__ = [class_name for _, class_name in llms_files]
