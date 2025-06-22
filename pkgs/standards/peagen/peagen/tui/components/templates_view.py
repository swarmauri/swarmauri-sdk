from __future__ import annotations

from pathlib import Path

from textual.widgets import Tree


class TemplatesView(Tree):
    """View template-set and prompt template files.

    🚧 editing/saving not yet supported
    """

    # 🚧 editing/saving not yet supported

    def __init__(self, *args, **kwargs) -> None:
        super().__init__("templates", *args, **kwargs)

    def on_mount(self) -> None:  # noqa: D401 – Textual hook
        """Populate the tree from the bundled template directory."""
        root = Path(__file__).resolve().parents[2] / "template_sets"
        self.root.expand()
        self._build_tree(root, self.root)

    def _build_tree(self, path: Path, node) -> None:
        for child in path.iterdir():
            if child.is_dir():
                sub = node.add(child.name, expand=True)
                self._build_tree(child, sub)
            else:
                node.add_leaf(child.name, data=child)
