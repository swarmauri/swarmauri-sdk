from .AutomatedReadabilityIndexEvaluator import AutomatedReadabilityIndexEvaluator
from .ColemanLiauIndexEvaluator import ColemanLiauIndexEvaluator
from .FleschKincaidGradeEvaluator import FleschKincaidGradeEvaluator
from .FleschReadingEaseEvaluator import FleschReadingEaseEvaluator
from .GunningFogEvaluator import GunningFogEvaluator
from .AccessibilityEvaluatorPool import AccessibilityEvaluatorPool

__all__ = [
    "AutomatedReadabilityIndexEvaluator",
    "ColemanLiauIndexEvaluator",
    "FleschKincaidGradeEvaluator",
    "FleschReadingEaseEvaluator",
    "GunningFogEvaluator",
    "AccessibilityEvaluatorPool",
]

try:
    # For Python 3.8 and newer
    from importlib.metadata import version, PackageNotFoundError
except ImportError:
    # For older Python versions, use the backport
    from importlib_metadata import version, PackageNotFoundError

try:
    __version__ = version("swarmauri_evaluatorpool_accessibility")
except PackageNotFoundError:
    # If the package is not installed (for example, during development)
    __version__ = "0.0.0"
