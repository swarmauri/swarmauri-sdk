from swarmauri.utils.LazyLoader import LazyLoader

# List of tool names (file names without the ".py" extension) and corresponding class names
tool_files = [
    ("swarmauri.tools.concrete.AdditionTool", "AdditionTool"),
    (
        "swarmauri.tools.concrete.AutomatedReadabilityIndexTool",
        "AutomatedReadabilityIndexTool",
    ),
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

# Lazy loading of tools using LazyLoader
for module_name, class_name in tool_files:
    globals()[class_name] = LazyLoader(module_name, class_name)

# Adding tools to __all__ (still safe because LazyLoader doesn't raise errors until accessed)
__all__ = [class_name for _, class_name in tool_files]
