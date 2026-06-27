"""Internal YAML parser support for Cayaml."""


def split_inline_comment(text: str) -> tuple[str, str | None]:
    """Split a YAML value from its inline comment while respecting quotes."""
    in_quote = False
    quote_char = ""
    escape = False

    for index, char in enumerate(text):
        if escape:
            escape = False
            continue
        if char == "\\" and in_quote:
            escape = True
            continue
        if in_quote:
            if char == quote_char:
                in_quote = False
            continue
        if char in ("'", '"'):
            in_quote = True
            quote_char = char
            continue
        if char == "#" and (index == 0 or text[index - 1].isspace()):
            return text[:index].rstrip(), text[index:].strip()

    if in_quote:
        return text.lstrip(), None
    return text.strip(), None


def indentation_width(line: str) -> int:
    """Return indentation width, rejecting tabs used as indentation."""
    width = 0
    for char in line:
        if char == " ":
            width += 1
            continue
        if char == "\t":
            if width:
                break
            break
        break
    return width


def is_document_marker(line: str, marker: str) -> bool:
    """Return True for a standalone document marker with optional comment."""
    stripped = line.strip()
    if stripped == marker:
        return True
    return (
        len(stripped) > len(marker)
        and stripped.startswith(marker)
        and stripped[len(marker)].isspace()
    )


def is_sequence_entry(line: str) -> bool:
    """Return True when a stripped line starts with a YAML sequence dash."""
    stripped = line.strip()
    return stripped == "-" or (
        len(stripped) > 1 and stripped[0] == "-" and stripped[1].isspace()
    )


def is_explicit_key_entry(line: str) -> bool:
    """Return True for YAML explicit-key markers."""
    stripped = line.strip()
    return stripped == "?" or (
        len(stripped) > 1 and stripped[0] == "?" and stripped[1].isspace()
    )


def split_top_level(text: str, delimiter: str) -> list[str]:
    """Split on a delimiter outside quotes and flow brackets."""
    parts = []
    start = 0
    depth = 0
    quote = ""
    escape = False

    for index, char in enumerate(text):
        if escape:
            escape = False
            continue
        if quote:
            if char == "\\" and quote == '"':
                escape = True
            elif char == quote:
                if (
                    quote == "'"
                    and index + 1 < len(text)
                    and text[index + 1] == "'"
                ):
                    escape = True
                    continue
                quote = ""
            continue
        if char in ("'", '"'):
            quote = char
            continue
        if char in "[{":
            depth += 1
            continue
        if char in "]}":
            if depth:
                depth -= 1
            continue
        if char == delimiter and depth == 0:
            parts.append(text[start:index].strip())
            start = index + 1

    parts.append(text[start:].strip())
    return parts


def find_top_level_colon(text: str) -> int:
    """Return the index of the first top-level mapping colon, or -1."""
    depth = 0
    quote = ""
    escape = False
    for index, char in enumerate(text):
        if escape:
            escape = False
            continue
        if quote:
            if char == "\\" and quote == '"':
                escape = True
            elif char == quote:
                if (
                    quote == "'"
                    and index + 1 < len(text)
                    and text[index + 1] == "'"
                ):
                    escape = True
                    continue
                quote = ""
            continue
        if char in ("'", '"') and (index == 0 or text[index - 1].isspace()):
            quote = char
            continue
        if char in "[{":
            depth += 1
            continue
        if char in "]}":
            if depth:
                depth -= 1
            continue
        if (
            char == ":"
            and depth == 0
            and text.startswith(("&", "*"))
            and not any(part.isspace() for part in text[:index])
        ):
            continue
        if (
            char == ":"
            and depth == 0
            and (index + 1 == len(text) or text[index + 1].isspace())
        ):
            return index
    return -1


def find_flow_mapping_colon(text: str) -> int:
    """Return a flow-map colon while preserving plain scalar colons."""
    colon = find_top_level_colon(text)
    if colon != -1:
        return colon

    depth = 0
    quote = ""
    escape = False
    for index, char in enumerate(text):
        if escape:
            escape = False
            continue
        if quote:
            if char == "\\" and quote == '"':
                escape = True
            elif char == quote:
                if (
                    quote == "'"
                    and index + 1 < len(text)
                    and text[index + 1] == "'"
                ):
                    escape = True
                    continue
                quote = ""
            continue
        if char in ("'", '"'):
            quote = char
            continue
        if char in "[{":
            depth += 1
            continue
        if char in "]}":
            depth -= 1
            continue
        if char != ":" or depth != 0:
            continue
        key_text = text[:index].strip()
        next_char = text[index + 1] if index + 1 < len(text) else ""
        if key_text.startswith(("'", '"', "[", "{")) or next_char in ",]}":
            return index
    return -1


def is_balanced_flow(text: str) -> bool:
    """Return True when flow brackets are balanced outside quotes."""
    depth = 0
    quote = ""
    escape = False
    for index, char in enumerate(text):
        if escape:
            escape = False
            continue
        if quote:
            if char == "\\" and quote == '"':
                escape = True
            elif char == quote:
                if (
                    quote == "'"
                    and index + 1 < len(text)
                    and text[index + 1] == "'"
                ):
                    escape = True
                    continue
                quote = ""
            continue
        if char in ("'", '"'):
            quote = char
            continue
        if char in "[{":
            depth += 1
        elif char in "]}":
            depth -= 1
            if depth < 0:
                return False
    return depth == 0 and not quote


def has_unclosed_quote(text: str) -> bool:
    """Return True if a scalar contains an unclosed quote."""
    quote = ""
    escape = False
    for index, char in enumerate(text):
        if escape:
            escape = False
            continue
        if quote:
            if char == "\\" and quote == '"':
                escape = True
            elif char == quote:
                if (
                    quote == "'"
                    and index + 1 < len(text)
                    and text[index + 1] == "'"
                ):
                    escape = True
                    continue
                quote = ""
            continue
        if char in ("'", '"'):
            quote = char
    return bool(quote)
