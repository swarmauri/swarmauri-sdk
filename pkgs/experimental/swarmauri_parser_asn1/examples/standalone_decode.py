from __future__ import annotations
from importlib import resources
from pathlib import Path
import json

from lark import Lark

from swarmauri_asn1.transformer import Asn1ToIR
from swarmauri_asn1.ir import Schema
from swarmauri_asn1.der_codec import decode_value

def load_grammar_text() -> str:
    return resources.files("swarmauri_asn1.grammar").joinpath("asn1.lark").read_text(encoding="utf-8")

def main():
    root = Path(__file__).resolve().parents[1]
    spec_path = root / "specs" / "Example.asn"
    data_path = root / "examples" / "data" / "question.der"

    grammar = load_grammar_text()
    lark_parser = Lark(grammar, parser="earley", lexer="dynamic", ambiguity="resolve", maybe_placeholders=True, cache=True)
    tree = lark_parser.parse(spec_path.read_text(encoding="utf-8"))
    schema: Schema = Asn1ToIR().transform(tree)

    buf = data_path.read_bytes()
    value, _ = decode_value(schema, schema.resolve("Question"), buf, 0)
    print(json.dumps(value, ensure_ascii=False))

if __name__ == "__main__":
    main()