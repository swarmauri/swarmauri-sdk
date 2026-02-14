from __future__ import annotations
from importlib import resources
from pathlib import Path
import json
from lark import Lark
from .transformer import Asn1ToIR
from .der_codec import decode_value
from .ir import Schema

# If swarmauri SDK is present, these imports work; otherwise they are only needed when used via SDK.
try:
    from swarmauri_core.parsers import ParserBase
    from swarmauri.documents import Document
    from swarmauri_base import ComponentBase
except Exception:
    # Minimal fallbacks for standalone demo
    class ParserBase: ...
    class Document:
        def __init__(self, content: str, metadata: dict | None = None):
            self.content = content; self.metadata = metadata or {}
    class ComponentBase:
        @staticmethod
        def register_type(base, name): 
            def deco(cls): return cls
            return deco

GRAMMAR_PACKAGE = "swarmauri_asn1.grammar"
GRAMMAR_FILE = "asn1.lark"

def _load_grammar_text() -> str:
    return resources.files(GRAMMAR_PACKAGE).joinpath(GRAMMAR_FILE).read_text(encoding="utf-8")

@ComponentBase.register_type(ParserBase, "ASN1Parser")
class ASN1Parser(ParserBase):
    """
    Grammar-driven ASN.1 parser using Lark Earley (MIT-only path).
    - Parses .asn modules into an IR
    - Decodes DER bytes into a JSON content Document
    """
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
        self._schema = self._compile_modules(asn1_files)

    def _compile_modules(self, files) -> Schema:
        text = "\n".join(Path(p).read_text(encoding="utf-8") for p in files)
        tree = self._lark.parse(text)
        return Asn1ToIR().transform(tree)

    def parse(self, data: bytes | str | Path, type_name: str, **_):
        if isinstance(data, (str, Path)) and Path(data).exists():
            raw = Path(data).read_bytes()
        elif isinstance(data, str):
            s = data.strip().replace(" ", "")
            try:
                raw = bytes.fromhex(s)
            except Exception:
                import base64
                raw = base64.b64decode(data)
        elif isinstance(data, (bytes, bytearray)):
            raw = bytes(data)
        else:
            raise ValueError("Unsupported input type for `data`.")

        value, _end = decode_value(self._schema, self._schema.resolve(type_name), raw, 0)
        doc = Document(
            content=json.dumps(value, ensure_ascii=False, separators=(",", ":")),
            metadata={"format":"asn.1", "codec":"der", "root_type": type_name}
        )
        return [doc]