from pathlib import Path

from textual.message import Message
from textual.widgets import Tree


class FileTree(Tree):
    class FileSelected(Message):
        def __init__(self, path: Path) -> None:
            self.path = path
            super().__init__()

    def on_mount(self):
        root = Path(".")
        self.root.expand()
        self.build_tree(root, self.root)

    def build_tree(self, path: Path, node):
        for p in path.iterdir():
            if p.is_dir():
                new_node = node.add(p.name, expand=True)
                self.build_tree(p, new_node)
            else:
                node.add_leaf(p.name, data=p)

    def on_tree_node_selected(self, event):
        if event.node.data:
            self.post_message(self.FileSelected(event.node.data))
