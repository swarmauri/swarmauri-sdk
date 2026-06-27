"""Internal YAML parser support for Cayaml."""

from .errors import YamlParseError

FLOW_INDICATORS = set("[]{},")
TAG_FORBIDDEN_CHARS = set("{}[],")


def validate_anchor_name(name: str, kind: str = "anchor") -> str:
    """Validate a YAML anchor or alias name."""
    if not name or any(
        char.isspace() or char in FLOW_INDICATORS for char in name
    ):
        raise YamlParseError(f"invalid {kind} name: {name!r}")
    return name


def split_tag_anchor_prefix(text: str) -> tuple[str | None, str | None, str]:
    """Return tag, anchor, and remaining scalar text from a YAML value."""
    tag = None
    anchor = None
    remaining = text.lstrip()
    if remaining.startswith(("[", "{", '"', "'")):
        return tag, anchor, remaining
    remaining = remaining.strip()

    while remaining.startswith(("!", "&")):
        token, _, tail = remaining.partition(" ")
        part = token.strip()
        if part.startswith("&"):
            anchor = validate_anchor_name(part[1:], "anchor")
        else:
            if not part.startswith("!<") and any(
                char in TAG_FORBIDDEN_CHARS for char in part
            ):
                raise YamlParseError(f"invalid tag: {part}")
            tag = part
        remaining = tail.lstrip()

    return tag, anchor, remaining
