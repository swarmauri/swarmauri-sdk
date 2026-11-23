"""Internal YAML parser support for Cayaml."""

from .errors import YamlParseError

TAG_HANDLES_KEY = "\0cayaml_tag_handles"
DEFAULT_TAG_HANDLES = {
    "!": "!",
    "!!": "tag:yaml.org,2002:",
}
CORE_TAGS = {
    "!!str": "tag:yaml.org,2002:str",
    "!!int": "tag:yaml.org,2002:int",
    "!!float": "tag:yaml.org,2002:float",
    "!!bool": "tag:yaml.org,2002:bool",
    "!!null": "tag:yaml.org,2002:null",
    "!!binary": "tag:yaml.org,2002:binary",
    "!!seq": "tag:yaml.org,2002:seq",
    "!!map": "tag:yaml.org,2002:map",
}


def tag_handles_from(anchors: dict[str, object] | None) -> dict[str, str]:
    """Return active tag handles from parser context."""
    if anchors is None:
        return dict(DEFAULT_TAG_HANDLES)
    return anchors.setdefault(TAG_HANDLES_KEY, dict(DEFAULT_TAG_HANDLES))


def expand_tag(
    tag: str | None, anchors: dict[str, object] | None
) -> str | None:
    """Expand YAML tag handles into canonical tag URI form."""
    if tag is None:
        return None
    if tag.startswith("!<") and tag.endswith(">"):
        return tag[2:-1]
    handles = tag_handles_from(anchors)
    if tag.startswith("!!") and handles.get("!!") != DEFAULT_TAG_HANDLES["!!"]:
        return handles["!!"] + tag[2:]
    if tag in CORE_TAGS:
        return CORE_TAGS[tag]
    if tag.startswith("!") and "!" in tag[1:]:
        handle_end = tag.find("!", 1) + 1
        handle = tag[:handle_end]
        if handle not in handles:
            raise YamlParseError(f"undefined tag handle: {handle}")
        return handles[handle] + tag[handle_end:]
    if tag.startswith("!") and handles.get("!") not in (None, "!"):
        return handles["!"] + tag[1:]
    for handle in sorted(handles, key=len, reverse=True):
        if tag.startswith(handle) and handle != "!":
            return handles[handle] + tag[len(handle) :]
    return tag


def emit_tag(
    tag: str | None, tag_handles: dict[str, str] | None = None
) -> str | None:
    """Compress a canonical tag using active handles when possible."""
    if tag is None:
        return None
    reverse_core = {value: key for key, value in CORE_TAGS.items()}
    if tag in reverse_core:
        return reverse_core[tag]
    handles = tag_handles or {}
    for handle, prefix in sorted(
        handles.items(), key=lambda item: len(item[1]), reverse=True
    ):
        if handle in ("!", "!!"):
            continue
        if tag.startswith(prefix):
            return handle + tag[len(prefix) :]
    if tag.startswith("tag:"):
        return f"!<{tag}>"
    return tag
