from swarmauri_tool_zapierhook import ZapierHookTool

tool = ZapierHookTool(zap_url="https://hooks.zapier.com/hooks/catch/...")
result = tool('{"event":"demo"}')

print(result["zap_response"])
