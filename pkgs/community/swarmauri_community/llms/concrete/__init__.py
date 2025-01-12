from swarmauri.utils.LazyLoader import LazyLoader

llms_files = [
    ("swarmauri_community.llms.concrete.LeptonAIImgGenModel", "LeptonAIImgGenModel"),
    ("swarmauri_community.llms.concrete.LeptonAIModel", "LeptonAIModel"),
    ("swarmauri_community.llms.concrete.PytesseractImg2TextModel", "PytesseractImg2TextModel"),
]

for module_name, class_name in llms_files:
    globals()[class_name] = LazyLoader(module_name, class_name)

__all__ = [class_name for _, class_name in llms_files]
