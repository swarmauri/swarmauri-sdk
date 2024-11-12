import importlib
import sys

# Define a lazy loader function
def _lazy_import(module_name):
    try:
        return importlib.import_module(module_name)
    except ImportError:
        return None

# Lazy loading of tools based on available dependencies
AdditionTool = _lazy_import("swarmauri.tools.concrete.AdditionTool") 
AutomatedReadabilityIndexTool = _lazy_import("swarmauri.tools.concrete.AutomatedReadabilityIndexTool")
CalculatorTool = _lazy_import("swarmauri.tools.concrete.CalculatorTool")
CodeExtractorTool = _lazy_import("swarmauri.tools.concrete.CodeExtractorTool")
CodeInterpreterTool = _lazy_import("swarmauri.tools.concrete.CodeInterpreterTool")
ColemanLiauIndexTool = _lazy_import("swarmauri.tools.concrete.ColemanLiauIndexTool")
FleschKincaidTool = _lazy_import("swarmauri.tools.concrete.FleschKincaidTool")
FleschReadingEaseTool = _lazy_import("swarmauri.tools.concrete.FleschReadingEaseTool")
GunningFogTool = _lazy_import("swarmauri.tools.concrete.GunningFogTool")
ImportMemoryModuleTool = _lazy_import("swarmauri.tools.concrete.ImportMemoryModuleTool")
JSONRequestsTool = _lazy_import("swarmauri.tools.concrete.JSONRequestsTool")
MatplotlibCsvTool = _lazy_import("swarmauri.tools.concrete.MatplotlibCsvTool")
MatplotlibTool = _lazy_import("swarmauri.tools.concrete.MatplotlibTool")

Parameter = _lazy_import("swarmauri.tools.concrete.Parameter")
SentenceComplexityTool = _lazy_import("swarmauri.tools.concrete.SentenceComplexityTool")
SMOGIndexTool = _lazy_import("swarmauri.tools.concrete.SMOGIndexTool")
TemperatureConverterTool = _lazy_import("swarmauri.tools.concrete.TemperatureConverterTool")
TestTool = _lazy_import("swarmauri.tools.concrete.TestTool")
TextLengthTool = _lazy_import("swarmauri.tools.concrete.TextLengthTool")
WeatherTool = _lazy_import("swarmauri.tools.concrete.WeatherTool")


__all__ = [
    "AdditionTool",
    "AutomatedReadabilityIndexTool",
    "CalculatorTool",
    "CodeExtractorTool",
    "CodeInterpreterTool",
    "ColemanLiauIndexTool",
    "FleschKincaidTool",
    "FleschReadingEaseTool",
    "GunningFogTool",
    "ImportMemoryModuleTool",
    "JSONRequestsTool",
    "MatplotlibCsvTool",
    "MatplotlibTool",
    "Parameter",
    "SentenceComplexityTool",
    "SMOGIndexTool",
    "TemperatureConverterTool",
    "TestTool",
    "TextLengthTool",
    "WeatherTool",
]
