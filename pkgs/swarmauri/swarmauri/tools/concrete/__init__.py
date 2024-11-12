import importlib

# Define a lazy loader function with a warning message if the module or class is not found
def _lazy_import(module_name, class_name):
    try:
        # Import the module
        module = importlib.import_module(module_name)
        # Dynamically get the class from the module
        return getattr(module, class_name)
    except ImportError:
        # If module is not available, print a warning message
        print(f"Warning: The module '{module_name}' is not available. "
              f"Please install the necessary dependencies to enable this functionality.")
        return None
    except AttributeError:
        print(f"Warning: The class '{class_name}' was not found in module '{module_name}'.")
        return None

# List of tool names (file names without the ".py" extension) and corresponding class names
tool_files = [
    ("swarmauri.tools.concrete.AdditionTool", "AdditionTool"),
    ("swarmauri.tools.concrete.AutomatedReadabilityIndexTool", "AutomatedReadabilityIndexTool"),
    ("swarmauri.tools.concrete.CalculatorTool", "CalculatorTool"),
    ("swarmauri.tools.concrete.CodeExtractorTool", "CodeExtractorTool"),
    ("swarmauri.tools.concrete.CodeInterpreterTool", "CodeInterpreterTool"),
    ("swarmauri.tools.concrete.ColemanLiauIndexTool", "ColemanLiauIndexTool"),
    ("swarmauri.tools.concrete.FleschKincaidTool", "FleschKincaidTool"),
    ("swarmauri.tools.concrete.FleschReadingEaseTool", "FleschReadingEaseTool"),
    ("swarmauri.tools.concrete.GunningFogTool", "GunningFogTool"),
    ("swarmauri.tools.concrete.ImportMemoryModuleTool", "ImportMemoryModuleTool"),
    ("swarmauri.tools.concrete.JSONRequestsTool", "JSONRequestsTool"),
    ("swarmauri.tools.concrete.MatplotlibCsvTool", "MatplotlibCsvTool"),
    ("swarmauri.tools.concrete.MatplotlibTool", "MatplotlibTool"),
    ("swarmauri.tools.concrete.Parameter", "Parameter"),
    ("swarmauri.tools.concrete.SentenceComplexityTool", "SentenceComplexityTool"),
    ("swarmauri.tools.concrete.SMOGIndexTool", "SMOGIndexTool"),
    ("swarmauri.tools.concrete.TemperatureConverterTool", "TemperatureConverterTool"),
    ("swarmauri.tools.concrete.TestTool", "TestTool"),
    ("swarmauri.tools.concrete.TextLengthTool", "TextLengthTool"),
    ("swarmauri.tools.concrete.WeatherTool", "WeatherTool"),
]

# Lazy loading of tools, storing them in variables
for module_name, class_name in tool_files:
    globals()[class_name] = _lazy_import(module_name, class_name)

# Adding the lazy-loaded tools to __all__
__all__ = [class_name for _, class_name in tool_files]
