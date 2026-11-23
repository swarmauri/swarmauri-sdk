from pathlib import Path
import json
from swarmauri_tool_jupyterclearoutput import JupyterClearOutputTool

notebook_data = json.loads(Path("notebooks/example.ipynb").read_text())

cleaner = JupyterClearOutputTool()
clean_notebook = cleaner(notebook_data)

Path("notebooks/example-clean.ipynb").write_text(
    json.dumps(clean_notebook, indent=2)
)
