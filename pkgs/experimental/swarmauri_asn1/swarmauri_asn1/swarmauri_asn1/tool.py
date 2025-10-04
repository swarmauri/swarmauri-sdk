from __future__ import annotations
from importlib import resources
from pathlib import Path
from lark import Lark
from .transformer import Asn1ToIR
from .ir import Schema

# swarmauri SDK optional base classes
try:
    from swarmauri_core.tools import ToolBase
    from swarmauri_base import ComponentBase
except Exception:
    class ToolBase: ...
    class ComponentBase:
        @staticmethod
        def register_type(base, name):
            def deco(cls): return cls
            return deco

GRAMMAR_PACKAGE = "swarmauri_asn1.grammar"
GRAMMAR_FILE = "asn1.lark"

def _load_grammar_text() -> str:
    return resources.files(GRAMMAR_PACKAGE).joinpath(GRAMMAR_FILE).read_text(encoding="utf-8")

@ComponentBase.register_type(ToolBase, "ASN1EncodeTool")
class ASN1EncodeTool(ToolBase):
    def __init__(self, asn1_files: list[str]):
        super().__init__()
        grammar = _load_grammar_text()
        self._lark = Lark(
            grammar,
            parser="earley",
            lexer="dynamic",
            ambiguity="resolve",
            maybe_placeholders=True,
            cache=True
        )
        self._schema: Schema = self._compile_modules(asn1_files)

    def _compile_modules(self, files) -> Schema:
        text = "\n".join(Path(p).read_text(encoding="utf-8") for p in files)
        tree = self._lark.parse(text)
        return Asn1ToIR().transform(tree)

    def __call__(self, *, type_name: str, data: dict, out: str | None = None) -> bytes:
        raise NotImplementedError("Encoder stub: implement encode_value analogously to decode_value")