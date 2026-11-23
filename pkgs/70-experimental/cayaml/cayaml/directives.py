"""Internal YAML parser support for Cayaml."""

import re

from .errors import YamlParseError
from .scanner import split_inline_comment


def parse_directive(
    line: str,
    tag_handles: dict[str, str],
    seen_yaml: set[str] | None = None,
    seen_tag_handles: set[str] | None = None,
):
    """Parse a YAML directive and update tag handle state."""
    semantic_line, _ = split_inline_comment(line.strip())
    parts = semantic_line.split()
    if not parts:
        return None
    if parts[0] == "%YAML":
        if len(parts) != 2 or not re.fullmatch(r"\d+\.\d+", parts[1]):
            raise YamlParseError(f"invalid YAML directive: {line.strip()}")
        if seen_yaml is not None and "%YAML" in seen_yaml:
            raise YamlParseError("duplicate directive: %YAML")
        if seen_yaml is not None:
            seen_yaml.add("%YAML")
        return ("YAML", parts[1])
    if parts[0] == "%TAG":
        if len(parts) != 3:
            raise YamlParseError(f"invalid TAG directive: {line.strip()}")
        handle, prefix = parts[1], parts[2]
        if not handle.startswith("!") or not handle.endswith("!"):
            raise YamlParseError(f"invalid TAG directive: {line.strip()}")
        if seen_tag_handles is not None and handle in seen_tag_handles:
            raise YamlParseError(f"duplicate directive tag handle: {handle}")
        if seen_tag_handles is not None:
            seen_tag_handles.add(handle)
        tag_handles[handle] = prefix
        return ("TAG", handle, prefix)
    return ("RESERVED", parts[0], parts[1:])
