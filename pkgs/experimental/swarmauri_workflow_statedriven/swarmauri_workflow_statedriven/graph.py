# File: swarmauri/workflows/graph.py

import asyncio
from pathlib import Path
from typing import Any, Dict, Optional
from pyppeteer import launch

from swarmauri_workflow_statedriven.base import WorkflowBase


class WorkflowGraph(WorkflowBase):
    """
    File: workflows/graph.py
    Class: WorkflowGraph

    An executable workflow graph with DOT→text and headless PNG export.
    """

    def __init__(self):
        """
        File: workflows/graph.py
        Class: WorkflowGraph
        Method: __init__

        Initialize using the WorkflowBase constructor.
        """
        super().__init__()

    def execute(self, start: str, initial_input: Any) -> Dict[str, Any]:
        """
        File: workflows/graph.py
        Class: WorkflowGraph
        Method: execute

        Run the workflow from the given start state.
        """
        return self.run(start, initial_input)

    def to_dot(self) -> str:
        """
        File: workflows/graph.py
        Class: WorkflowGraph
        Method: to_dot

        Emit the workflow as a GraphViz DOT string.
        """
        lines = ["flowchart TD {"]
        # node declarations
        for name in self.nodes:
            lines.append(f'  "{name}";')
        # edges with condition labels
        for t in self.transitions:
            label = type(t.condition).__name__
            lines.append(f'  "{t.source}" -> "{t.target}" [label="{label}"];')
        lines.append("}")
        return "\n".join(lines)

    def visualize(self, filename: Optional[str] = None) -> str:
        """
        File: workflows/graph.py
        Class: WorkflowGraph
        Method: visualize

        Return the DOT source for the workflow. If `filename` is provided,
        write the DOT to `<filename>.dot`.

        Args:
            filename: Optional basename (no extension) for writing out a .dot file.

        Returns:
            The DOT source as a string.
        """
        dot_source = self.to_dot()
        if filename:
            dot_path = Path(f"{filename}.dot")
            dot_path.parent.mkdir(parents=True, exist_ok=True)
            dot_path.write_text(dot_source, encoding="utf-8")
        return dot_source

    def visualize_png_headless(
        self,
        output_path: str,
        width: int = 800,
        height: int = 600,
        vizjs_cdn: str = "https://cdn.jsdelivr.net/npm/viz.js@2.1.2/viz.js",
        wasm_cdn: str = "https://cdn.jsdelivr.net/npm/viz.js@2.1.2/full.render.js",
    ) -> str:
        """
        File: workflows/graph.py
        Class: WorkflowGraph
        Method: visualize_png_headless

        Render the DOT via Viz.js in a headless browser and capture PNG.

        Args:
            output_path: Path to write the PNG file.
            width, height: viewport dimensions.
            vizjs_cdn: URL to Viz.js core script.
            wasm_cdn: URL to Viz.js WASM renderer.

        Returns:
            The path to the generated PNG.
        """
        dot_source = self.to_dot()
        escaped_dot = dot_source.replace("`", "\\`")
        # Build minimal HTML page
        html = f"""
        <html>
          <head>
            <script src="{vizjs_cdn}"></script>
            <script src="{wasm_cdn}"></script>
            <style>body{{margin:0}}#container{{width:{width}px;height:{height}px}}</style>
          </head>
          <body>
            <div id="container"></div>
            <script>
              const {{ Viz }} = window;
              const viz = new Viz();
              viz.renderSVGElement(`{escaped_dot}`)
                 .then(el => document.getElementById("container").appendChild(el))
                 .catch(err => console.error(err));
            </script>
          </body>
        </html>
        """
        # Ensure output directory exists
        out_path = Path(output_path)
        out_path.parent.mkdir(parents=True, exist_ok=True)
        # Render & screenshot
        asyncio.get_event_loop().run_until_complete(
            self._render_html_to_png(html, str(out_path), width, height)
        )
        return str(out_path)

    async def _render_html_to_png(
        self, html: str, output_png: str, width: int, height: int
    ):
        """
        File: workflows/graph.py
        Class: WorkflowGraph
        Method: _render_html_to_png

        Internal helper: launches a headless browser, loads HTML, and captures a PNG.
        """
        browser = await launch(headless=True, args=["--no-sandbox"])
        page = await browser.newPage()
        await page.setViewport({"width": width, "height": height})
        await page.setContent(html, waitUntil="networkidle0")
        # Allow Viz.js to finish rendering
        await asyncio.sleep(0.5)
        element = await page.querySelector("#container")
        await element.screenshot({"path": output_png})
        await browser.close()
