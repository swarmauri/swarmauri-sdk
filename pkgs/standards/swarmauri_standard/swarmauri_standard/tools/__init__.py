# from swarmauri.utils.LazyLoader import LazyLoader

# # List of tool names (file names without the ".py" extension) and corresponding class names
# tool_files = [
#     ("swarmauri_standard.tools.AdditionTool", "AdditionTool"),
#     (
#         "swarmauri_standard.tools.AutomatedReadabilityIndexTool",
#         "AutomatedReadabilityIndexTool",
#     ),
#     ("swarmauri_standard.tools.CalculatorTool", "CalculatorTool"),
#     ("swarmauri_standard.tools.CodeExtractorTool", "CodeExtractorTool"),
#     ("swarmauri_standard.tools.CodeInterpreterTool", "CodeInterpreterTool"),
#     ("swarmauri_standard.tools.ColemanLiauIndexTool", "ColemanLiauIndexTool"),
#     ("swarmauri_standard.tools.FleschKincaidTool", "FleschKincaidTool"),
#     ("swarmauri_standard.tools.FleschReadingEaseTool", "FleschReadingEaseTool"),
#     ("swarmauri_standard.tools.GunningFogTool", "GunningFogTool"),
#     ("swarmauri_standard.tools.ImportMemoryModuleTool", "ImportMemoryModuleTool"),
#     ("swarmauri_standard.tools.JSONRequestsTool", "JSONRequestsTool"),
#     ("swarmauri_standard.tools.MatplotlibCsvTool", "MatplotlibCsvTool"),
#     ("swarmauri_standard.tools.MatplotlibTool", "MatplotlibTool"),
#     ("swarmauri_standard.tools.Parameter", "Parameter"),
#     ("swarmauri_standard.tools.SentenceComplexityTool", "SentenceComplexityTool"),
#     ("swarmauri_standard.tools.SMOGIndexTool", "SMOGIndexTool"),
#     ("swarmauri_standard.tools.TemperatureConverterTool", "TemperatureConverterTool"),
#     ("swarmauri_standard.tools.TestTool", "TestTool"),
#     ("swarmauri_standard.tools.TextLengthTool", "TextLengthTool"),
#     ("swarmauri_standard.tools.WeatherTool", "WeatherTool"),
# ]

# # Lazy loading of tools using LazyLoader
# for module_name, class_name in tool_files:
#     globals()[class_name] = LazyLoader(module_name, class_name)

# # Adding tools to __all__ (still safe because LazyLoader doesn't raise errors until accessed)
# __all__ = [class_name for _, class_name in tool_files]
