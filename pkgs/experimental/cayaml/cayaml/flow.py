"""Internal YAML parser support for Cayaml."""

from .ast_nodes import MappingNode, SequenceNode, ScalarNode
from .errors import YamlParseError
from .mapping_keys import add_mapping_pair
from .scanner import (
    find_flow_mapping_colon,
    has_unclosed_quote,
    is_balanced_flow,
    is_explicit_key_entry,
    split_inline_comment,
    split_top_level,
)


def parse_flow_node(text: str, anchors: dict[str, object]):
    """Parse a flow-style sequence or mapping into AST nodes."""
    text = text.strip()
    if (text.startswith("[") and not text.endswith("]")) or (
        text.startswith("{") and not text.endswith("}")
    ):
        raise YamlParseError(f"malformed flow collection: {text}")
    if text.startswith(("[", "{")) and text.endswith(("]", "}")):
        if not is_balanced_flow(text):
            if has_unclosed_quote(text):
                raise YamlParseError(
                    f"unterminated quoted scalar in flow collection: {text}"
                )
            raise YamlParseError(f"malformed flow collection: {text}")
    if text.startswith("[") and text.endswith("]"):
        sequence = SequenceNode()
        sequence.flow_style = True
        inner = text[1:-1].strip()
        if inner:
            parts = split_top_level(inner, ",")
            for index, item in enumerate(parts):
                if not item:
                    if index == len(parts) - 1 and len(parts) > 1:
                        continue
                    raise YamlParseError("empty flow sequence entry")
                if item in ("-", "?", ":") or item.startswith("#"):
                    raise YamlParseError(
                        f"invalid flow sequence entry: {item}"
                    )
                sequence.add_item(parse_flow_sequence_entry(item, anchors))
        return sequence

    if text.startswith("{") and text.endswith("}"):
        mapping = MappingNode()
        mapping.flow_style = True
        inner = text[1:-1].strip()
        if inner:
            for item in split_top_level(inner, ","):
                if not item:
                    continue
                if item.startswith("#"):
                    raise YamlParseError(f"invalid flow mapping entry: {item}")
                key_node, value_node = parse_flow_pair(
                    item, anchors, allow_omitted_value=True
                )
                add_mapping_pair(mapping, key_node, value_node)
        return mapping

    return None


def parse_flow_sequence_entry(text: str, anchors: dict[str, object]):
    """Parse one flow sequence entry, including YAML pair entries."""
    from .construction import make_scalar_node

    try:
        key_node, value_node = parse_flow_pair(text, anchors)
    except YamlParseError:
        return make_scalar_node(text, anchors)

    mapping = MappingNode()
    mapping.flow_style = True
    mapping.add_pair(key_node, value_node)
    return mapping


def parse_flow_pair(
    text: str,
    anchors: dict[str, object],
    allow_omitted_value: bool = False,
):
    """Parse a flow mapping pair entry."""
    from .construction import make_scalar_node

    item = text.strip()
    explicit_key = False
    if is_explicit_key_entry(item):
        explicit_key = True
        item = item[1:].strip()
    colon = find_flow_mapping_colon(item)
    if colon == -1:
        if explicit_key or allow_omitted_value:
            return make_scalar_node(item, anchors), ScalarNode(None)
        raise YamlParseError(f"malformed flow mapping entry: {text}")
    key_text = item[:colon].strip()
    value_text = item[colon + 1 :].strip()
    return make_scalar_node(key_text, anchors), make_scalar_node(
        value_text, anchors
    )


def fold_plain_continuation(base: str, continuation_lines: list[str]) -> str:
    """Fold plain or quoted scalar continuation lines."""
    if not continuation_lines:
        return base
    if base.startswith(("'", '"')) and (
        len(base) == 1 or not base.endswith(base[0])
    ):

        def trim_non_content(text: str) -> str:
            text = text.replace("\\\t", "\0T").replace("\\ ", "\0S")
            text = text.rstrip(" \t")
            return text.replace("\0T", "\\t").replace("\0S", "\\ ")

        quote = base[0]
        value = trim_non_content(base[1:])
        blank_count = 0
        for line in continuation_lines:
            stripped = line.strip()
            if not stripped:
                blank_count += 1
                continue
            has_end_quote = stripped.endswith(quote)
            if has_end_quote:
                content = stripped[:-1]
            else:
                content = trim_non_content(stripped)
            if blank_count:
                value += "\n" * blank_count + content
            elif value.endswith("\\"):
                value = value[:-1] + content
            else:
                value += " " + content
            blank_count = 0
            if has_end_quote:
                return quote + value + quote
        if blank_count:
            value += "\n" * blank_count
        return quote + value
    value = base
    pending_break = False
    for line in continuation_lines:
        stripped = line.strip()
        if not stripped:
            pending_break = True
            continue
        if pending_break:
            value += "\n" + stripped
        else:
            value += " " + stripped
        pending_break = False
    return value


def collect_flow_text(lines: list[str]) -> tuple[str, int] | None:
    """Collect a multi-line flow collection and consumed line count."""
    if not lines:
        return None
    first = lines[0].strip()
    if not first.startswith(("[", "{")):
        return None
    parts = []
    flow_kind = first[0]
    for index, line in enumerate(lines):
        stripped_line = line.strip()
        if line.lstrip(" ").startswith("\t") and stripped_line not in (
            "",
            "[",
            "]",
            "{",
            "}",
            "[]",
            "{}",
        ):
            raise YamlParseError("tab indentation is not allowed in flow")
        stripped, _ = split_inline_comment(line.strip())
        if not stripped:
            continue
        if parts and invalid_flow_line_join(flow_kind, parts[-1], stripped):
            raise YamlParseError("missing flow entry separator")
        parts.append(stripped)
        joined = " ".join(parts)
        if is_balanced_flow(joined):
            return joined, index + 1
    raise YamlParseError(f"malformed flow collection: {' '.join(parts)}")


def invalid_flow_line_join(
    flow_kind: str, previous: str, current: str
) -> bool:
    """Return True when adjacent flow lines need an entry separator."""
    previous = previous.rstrip()
    current = current.lstrip()
    if current.startswith(("]", "}")):
        return False
    if previous.endswith((",", "[", "{", "?", ":")):
        return False
    if current.startswith(":"):
        return flow_kind == "["
    if flow_kind == "{" and ":" in previous and ":" in current:
        return True
    return False
