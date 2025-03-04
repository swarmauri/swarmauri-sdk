from swarmauri.utils._lazy_import import _lazy_import

llms_files = [
    ("swarmauri_community.llms.concrete.LeptonAIImgGenModel", "LeptonAIImgGenModel"),
    ("swarmauri_community.llms.concrete.LeptonAIModel", "LeptonAIModel"),
    ("swarmauri_community.llms.concrete.PytesseractImg2TextModel", "PytesseractImg2TextModel"),
]

for module_name, class_name in llms_files:
    globals()[class_name] = _lazy_import(module_name, class_name)

__all__ = [class_name for _, class_name in llms_files]
