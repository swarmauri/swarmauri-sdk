import base64
from pathlib import Path
from swarmauri_tool_captchagenerator import CaptchaGeneratorTool

captcha_tool = CaptchaGeneratorTool()
result = captcha_tool("Verify42")

image_b64 = result["image_b64"]
image_bytes = base64.b64decode(image_b64)
Path("captcha.png").write_bytes(image_bytes)
