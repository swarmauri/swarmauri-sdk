from swarmauri_tool_qrcodegenerator import QrCodeGeneratorTool

tool = QrCodeGeneratorTool()
result = tool("https://docs.swarmauri.com")

print(result["image_b64"][:40])
