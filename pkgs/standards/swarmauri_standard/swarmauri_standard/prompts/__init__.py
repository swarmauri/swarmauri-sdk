# from swarmauri.utils._lazy_import import _lazy_import

# # List of prompts names (file names without the ".py" extension) and corresponding class names
# prompts_files = [
#     ("swarmauri_standard.prompts.Prompt", "Prompt"),
#     ("swarmauri_standard.prompts.PromptGenerator", "PromptGenerator"),
#     ("swarmauri_standard.prompts.PromptMatrix", "PromptMatrix"),
#     ("swarmauri_standard.prompts.PromptTemplate", "PromptTemplate"),
# ]

# # Lazy loading of prompts classes, storing them in variables
# for module_name, class_name in prompts_files:
#     globals()[class_name] = _lazy_import(module_name, class_name)

# # Adding the lazy-loaded prompts classes to __all__
# __all__ = [class_name for _, class_name in prompts_files]
