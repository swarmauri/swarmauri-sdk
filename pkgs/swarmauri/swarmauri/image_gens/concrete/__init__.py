from swarmauri.utils.LazyLoader import LazyLoader

# List of image generators names (file names without the ".py" extension) and corresponding class names
image_gens_files = [
    ("swarmauri.image_gens.concrete.BlackForestImgGenModel", "BlackForestImgGenModel"),
    ("swarmauri.image_gens.concrete.DeepInfraImgGenModel", "DeepInfraImgGenModel"),
    ("swarmauri.image_gens.concrete.FalAIImgGenModel", "FalAIImgGenModel"),
    ("swarmauri.image_gens.concrete.HyperbolicImgGenModel", "HyperbolicImgGenModel"),
    ("swarmauri.image_gens.concrete.OpenAIImgGenModel", "OpenAIImgGenModel"),
]

# Lazy loading of image generators classes, storing them in variables
for module_name, class_name in image_gens_files:
    globals()[class_name] = LazyLoader(module_name, class_name)

# Adding the lazy-loaded image generators classes to __all__
__all__ = [class_name for _, class_name in image_gens_files]