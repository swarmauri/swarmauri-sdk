from swarmauri_tool_jupyterdisplayhtml import JupyterDisplayHTMLTool

tool = JupyterDisplayHTMLTool()
result = tool("""
<h2>Swarmauri</h2>
<p>This HTML was rendered by JupyterDisplayHTMLTool.
</p>
""")
print(result)
