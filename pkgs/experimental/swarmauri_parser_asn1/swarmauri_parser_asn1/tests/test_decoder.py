from pathlib import Path
from lark import Lark
from swarmauri_asn1.transformer import Asn1ToIR
from swarmauri_asn1.der_codec import decode_value

def test_decode_question():
    root = Path(__file__).resolve().parents[1]
    grammar = (root / "swarmauri_asn1" / "grammar" / "asn1.lark").read_text(encoding="utf-8")
    parser = Lark(grammar, parser="earley", lexer="dynamic", ambiguity="resolve", maybe_placeholders=True, cache=True)

    spec = (root / "specs" / "Example.asn").read_text(encoding="utf-8")
    schema = Asn1ToIR().transform(parser.parse(spec))

    buf = bytes.fromhex("300A02012A160548656C6C6F")
    value, _ = decode_value(schema, schema.resolve("Question"), buf, 0)
    assert value == {"id": 42, "question": "Hello"}