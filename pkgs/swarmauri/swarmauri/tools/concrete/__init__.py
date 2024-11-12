import importlib

# Define a lazy loader function with a warning message if the module is not found
def _lazy_import(module_name):
    try:
        return importlib.import_module(module_name)
    except ImportError:
        # If module is not available, print a warning message
        print(f"Warning: The module '{module_name}' is not available. "
              f"Please install the necessary dependencies to enable this functionality.")
        return None

# List of tool names (file names without the ".py" extension)
tool_files = [
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

# Lazy loading of tools, storing them in variables
for tool in tool_files:
    globals()[tool] = _lazy_import(f"swarmauri.tools.concrete.{tool}")

# Adding the lazy-loaded tools to __all__
__all__ = tool_files
