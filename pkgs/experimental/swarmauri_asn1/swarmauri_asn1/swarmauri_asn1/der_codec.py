from __future__ import annotations
from typing import Tuple, Any, Dict, List
from .ir import *

# ---- DER low-level TLV ----
def _read_tag(buf: bytes, i: int) -> Tuple[int,bool,int,int]:
    b0 = buf[i]; i += 1
    cls = (b0 >> 6) & 0b11          # 0 U,1 A,2 C,3 P
    constructed = bool((b0 >> 5) & 0b1)
    tagnum = b0 & 0x1F
    if tagnum == 0x1F:              # high-tag-number
        tagnum = 0
        while True:
            b = buf[i]; i += 1
            tagnum = (tagnum << 7) | (b & 0x7F)
            if (b & 0x80) == 0: break
    return cls, constructed, tagnum, i

def _read_len(buf: bytes, i: int) -> Tuple[int,int]:
    b = buf[i]; i += 1
    if (b & 0x80) == 0:
        return b, i
    n = b & 0x7F
    if n == 0:
        raise ValueError("Indefinite length not allowed in DER")
    val = 0
    for _ in range(n):
        val = (val << 8) | buf[i]; i += 1
    return val, i

def _read_tlv(buf: bytes, i: int) -> Tuple[int,bool,int,bytes,int]:
    cls, cons, tag, j = _read_tag(buf, i)
    ln, k = _read_len(buf, j)
    end = k + ln
    return cls, cons, tag, buf[k:end], end

# ---- Utilities ----
_UC = {"UNIVERSAL":0,"APPLICATION":1,"CONTEXT":2,"PRIVATE":3}
_UNIVERSAL_TAGS = {
    "BOOLEAN":1, "INTEGER":2, "BIT STRING":3, "OCTET STRING":4, "NULL":5,
    "OBJECT IDENTIFIER":6, "UTF8String":12, "SEQUENCE":16, "SET":17,
    "PrintableString":19, "IA5String":22, "UTCTime":23, "GeneralizedTime":24
}

def _expect_tag(buf_tag: Tuple[int,bool,int], exp: Tag|None, builtin_kind: str|None):
    cls, cons, tag = buf_tag
    if exp:
        if _UC[exp.cls] != cls: 
            return False
        if tag != exp.num: 
            return False
        # For EXPLICIT the constructed bit is checked in the caller when unwrapping
        return True
    if builtin_kind:
        if cls != 0: return False
        if tag != _UNIVERSAL_TAGS[builtin_kind]: return False
        return True
    return True

# ---- Primitive decoders ----
def _dec_boolean(v: bytes) -> bool:
    return v != b"\x00"

def _dec_integer(v: bytes) -> int:
    if not v: return 0
    return int.from_bytes(v, "big", signed=True)

def _dec_octet_string(v: bytes) -> bytes: return v
def _dec_utf8(v: bytes) -> str: return v.decode("utf-8")
def _dec_ia5(v: bytes) -> str: return v.decode("ascii")
def _dec_printable(v: bytes) -> str: return v.decode("ascii")

def _dec_oid(v: bytes) -> str:
    if not v: return ""
    first = v[0]
    arcs = [first // 40, first % 40]
    val = 0
    for b in v[1:]:
        val = (val << 7) | (b & 0x7F)
        if (b & 0x80) == 0:
            arcs.append(val); val = 0
    return ".".join(map(str, arcs))

# ---- High-level decode ----
def decode_value(schema: Schema, tnode: Any, buf: bytes, i: int = 0):
    node, tagwrap = _unwrap_tag(tnode)

    # EXPLICIT tagging: outer TLV has the tag, inner contains the actual type TLV
    if tagwrap and tagwrap.mode == "explicit":
        cls, cons, tag, inner, end = _read_tlv(buf, i)
        if not cons: 
            raise ValueError("EXPLICIT tag must be constructed")
        if not _expect_tag((cls,cons,tag), tagwrap, None):
            raise ValueError("EXPLICIT tag mismatch")
        val, _ = decode_value(schema, node, inner, 0)
        return val, end

    # For IMPLICIT or no tag, we decode according to node
    if isinstance(node, Builtin):
        cls, cons, tag, val, end = _read_tlv(buf, i)
        if not _expect_tag((cls,cons,tag), tagwrap if (tagwrap and tagwrap.mode == "implicit") else None, node.kind):
            raise ValueError(f"Tag mismatch for {node.kind}")
        kind = node.kind
        if kind == "BOOLEAN": return _dec_boolean(val), end
        if kind == "INTEGER":
            x = _dec_integer(val)
            if node.enum:
                for k,v in node.enum.items():
                    if v == x: return k, end
            return x, end
        if kind == "OCTET STRING": return _dec_octet_string(val), end
        if kind == "UTF8String": return _dec_utf8(val), end
        if kind == "IA5String": return _dec_ia5(val), end
        if kind == "PrintableString": return _dec_printable(val), end
        if kind == "NULL": return None, end
        if kind == "OBJECT IDENTIFIER": return _dec_oid(val), end
        if kind == "BIT STRING":
            # Simple bitstring as bytes (ignoring unused-bits count for brevity)
            return val, end
        raise NotImplementedError(f"Builtin not implemented: {kind}")

    if isinstance(node, TypeRef):
        return decode_value(schema, schema.resolve(node.name), buf, i)

    if isinstance(node, Sequence):
        cls, cons, tag, content, end = _read_tlv(buf, i)
        if not _expect_tag((cls,cons,tag), tagwrap if (tagwrap and tagwrap.mode == "implicit") else None, "SEQUENCE"):
            raise ValueError("Tag mismatch for SEQUENCE")
        j = 0
        res = {}
        for fld in node.fields:
            if j >= len(content):
                if fld.default is not None:
                    res[fld.name] = fld.default
                    continue
                if fld.optional:
                    continue
                # required but no more content
                res[fld.name] = None
                continue
            # try decode this field; if it fails and optional, skip without advancing
            try:
                val, j2 = decode_value(schema, fld.type, content, j)
                res[fld.name] = val
                j = j2
            except Exception:
                if fld.default is not None:
                    res[fld.name] = fld.default
                elif fld.optional:
                    # do not advance j; next fields may match this TLV
                    pass
                else:
                    # required but didn't match; leave None
                    res[fld.name] = None
        return res, end

    if isinstance(node, SetType):
        cls, cons, tag, content, end = _read_tlv(buf, i)
        if not _expect_tag((cls,cons,tag), tagwrap if (tagwrap and tagwrap.mode == "implicit") else None, "SET"):
            raise ValueError("Tag mismatch for SET")
        # order-agnostic: attempt to match each child TLV to a field
        j = 0
        res = {}
        remaining = list(node.fields)
        while j < len(content):
            c_cls, c_cons, c_tag, _, c_end = _read_tlv(content, j)
            matched_idx = None
            for idx, fld in enumerate(remaining):
                try:
                    val, _j2 = decode_value(schema, fld.type, content, j)
                    res[fld.name] = val
                    matched_idx = idx
                    break
                except Exception:
                    continue
            if matched_idx is not None:
                remaining.pop(matched_idx)
                j = c_end
            else:
                # skip unknown extension
                j = c_end
        for fld in remaining:
            if fld.default is not None:
                res[fld.name] = fld.default
            elif fld.optional:
                continue
            else:
                res[fld.name] = None
        return res, end

    if isinstance(node, SeqOf):
        cls, cons, tag, content, end = _read_tlv(buf, i)
        if not _expect_tag((cls,cons,tag), tagwrap if (tagwrap and tagwrap.mode == "implicit") else None, "SEQUENCE"):
            raise ValueError("Tag mismatch for SEQUENCE OF")
        j = 0; arr = []
        while j < len(content):
            v, j2 = decode_value(schema, node.elem, content, j)
            arr.append(v); j = j2
        return arr, end

    if isinstance(node, SetOf):
        cls, cons, tag, content, end = _read_tlv(buf, i)
        if not _expect_tag((cls,cons,tag), tagwrap if (tagwrap and tagwrap.mode == "implicit") else None, "SET"):
            raise ValueError("Tag mismatch for SET OF")
        j = 0; arr = []
        while j < len(content):
            v, j2 = decode_value(schema, node.elem, content, j)
            arr.append(v); j = j2
        return arr, end

    if isinstance(node, Choice):
        # For CHOICE, the encoded TLV is that of the selected alternative
        # Try each alternative against the same buffer
        for alt_name, alt_t in node.alts:
            try:
                v, end = decode_value(schema, alt_t, buf, i)
                return {alt_name: v}, end
            except Exception:
                continue
        raise ValueError("CHOICE: no alternative matched")

    # If node carries (type, Tag) or (type, Constraint)
    if isinstance(node, tuple):
        base = node[0]
        return decode_value(schema, base, buf, i)

    raise NotImplementedError(f"Unsupported node: {node}")

def _unwrap_tag(tnode):
    if isinstance(tnode, tuple) and len(tnode) == 2 and isinstance(tnode[1], Tag):
        return tnode[0], tnode[1]
    return tnode, None