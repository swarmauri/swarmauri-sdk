from __future__ import annotations
from typing import Any, List
from lark import Transformer, Token, Tree
from .ir import *

def _tok_to_int(t: Any) -> int:
    if isinstance(t, Token):
        return int(t.value)
    return int(str(t))

class Asn1ToIR(Transformer):
    # start: module+
    def start(self, items):
        s = Schema()
        for m in items:
            s.modules[m.name] = m
        return s

    # module: UIDENT "DEFINITIONS" "::=" "BEGIN" module_body "END"
    def module(self, items):
        name_tok, body = items[0], items[1]
        return Module(str(name_tok), **body)

    # module_body: (assignment | ";")*
    def module_body(self, items):
        types = {}
        values = {}
        for it in items:
            if isinstance(it, TypeAssignment):
                types[it.name] = it
            elif isinstance(it, ValueAssignment):
                values[it.name] = it
        return {"types": types, "values": values}

    # type_assignment: UIDENT "::=" type
    def type_assignment(self, items):
        name, t = items
        return TypeAssignment(str(name), t)

    # value_assignment -> value_assign
    def value_assign(self, items):
        name, t, v = items
        return ValueAssignment(str(name), t, v)

    # Types
    def type_ref(self, items):
        (name,) = items
        return TypeRef(str(name))

    def t_boolean(self, _=None): return Builtin("BOOLEAN")
    def t_integer(self, items=None):
        enum = items[0] if items else None
        return Builtin("INTEGER", enum=enum)
    def t_enumerated(self, items):
        enum = items[0] if items else {}
        return Builtin("ENUMERATED", enum=enum)
    def t_bitstring(self, _=None): return Builtin("BIT STRING")
    def t_octetstring(self, _=None): return Builtin("OCTET STRING")
    def t_null(self, _=None): return Builtin("NULL")
    def t_oid(self, _=None): return Builtin("OBJECT IDENTIFIER")
    def t_ia5(self, _=None): return Builtin("IA5String")
    def t_utf8(self, _=None): return Builtin("UTF8String")
    def t_printable(self, _=None): return Builtin("PrintableString")
    def t_utctime(self, _=None): return Builtin("UTCTime")
    def t_gentime(self, _=None): return Builtin("GeneralizedTime")

    def seq_type(self, items): 
        fields = items[0] if items else []
        return Sequence(fields)
    def set_type(self, items): 
        fields = items[0] if items else []
        return SetType(fields)
    def seqof_type(self, items): return SeqOf(items[0])
    def setof_type(self, items): return SetOf(items[0])
    def choice_type(self, items): return Choice(items[0])

    def field_list(self, items): return items
    def field(self, items):
        name = str(items[0]); t = items[1]
        f = Field(name=name, type=t)
        if len(items) > 2:
            opts = items[2]
            if isinstance(opts, tuple) and opts and opts[0] == "DEFAULT":
                f.default = opts[1]
            elif opts == "OPTIONAL":
                f.optional = True
        return f

    def field_opts(self, items):
        if not items: 
            return None
        head = items[0]
        if isinstance(head, Token) and head.value == "OPTIONAL":
            return "OPTIONAL"
        if isinstance(head, Token) and head.value == "DEFAULT":
            return ("DEFAULT", items[1])
        if isinstance(head, str) and head == "OPTIONAL":
            return "OPTIONAL"
        if isinstance(head, str) and head == "DEFAULT":
            return ("DEFAULT", items[1])
        return None

    def alt_list(self, items): return items
    def alt(self, items): 
        name, t = items
        return (str(name), t)

    def enum_list(self, items):
        enum = {}
        next_val = 0
        for it in items:
            if isinstance(it, tuple):
                k, v = it; enum[k] = v; next_val = v + 1
            else:
                enum[it] = next_val; next_val += 1
        return enum

    def enum_item(self, items):
        if len(items) == 2:
            return (str(items[0]), _tok_to_int(items[1]))
        return str(items[0])

    # Tagging
    def tagclass(self, items):
        return str(items[0])

    def tagged_type(self, items):
        # items: [tagclass? , INT, mode?, type]
        idx = 0
        tagcls = "CONTEXT"
        if items and isinstance(items[0], str):
            tagcls = items[0]; idx += 1
        tagnum = _tok_to_int(items[idx]); idx += 1
        mode = "implicit"
        if idx < len(items) - 1:
            m = items[idx]
            if isinstance(m, Token) and m.value in ("IMPLICIT", "EXPLICIT"):
                mode = m.value.lower(); idx += 1
            elif isinstance(m, str) and m in ("IMPLICIT", "EXPLICIT"):
                mode = m.lower(); idx += 1
        t = items[idx]
        return (t, Tag("CONTEXT" if tagcls == "CONTEXT-SPECIFIC" else tagcls, tagnum, mode))

    # Constraints
    def constrained_type(self, items):
        t, c = items
        return (t, c)

    def constraint(self, items):
        # items: [list of constraint_term]
        c = Constraint()
        for term in items[0]:
            if isinstance(term, tuple) and term[0] == "size":
                c.size = term[1]
            elif isinstance(term, tuple) and term[0] == "range":
                c.value_range = term[1]
        return c

    def constraint_body(self, items):
        return items

    def size_constraint(self, items):
        rng = items[1]
        if isinstance(rng, tuple):
            return ("size", (rng[0], rng[1]))
        v = rng
        return ("size", (v, v))

    def size_range(self, items):
        a, b = items
        return (_tok_to_int(a), _tok_to_int(b))

    def value_range(self, items):
        a, b = items
        return ("range", (_tok_to_int(a), _tok_to_int(b)))

    # Values
    def NUMBER(self, t): return int(t.value)
    def INT(self, t): return int(t.value)
    def STRING(self, s):
        ss = s.value
        if ss.startswith("'") and ss.endswith("'"): 
            return ss[1:-1]
        if ss.startswith('"') and ss.endswith('"'):
            return ss[1:-1]
        return ss

    def oid_value(self, items):
        # Keep textual OID as string; codec will parse arcs
        # Rebuild from components if needed
        parts = []
        for it in items[0]:
            if isinstance(it, tuple):
                parts.append(f"{it[0]}({it[1]})")
            else:
                parts.append(str(it))
        return "{" + " ".join(parts) + "}"