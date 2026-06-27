"""Internal YAML parser support for Cayaml."""

from .errors import YamlParseError


def _more_indented_content(line: str) -> bool:
    """Return True when folded scalar content starts with whitespace."""
    return bool(line) and line[0].isspace()


def block_scalar_value(
    style: str, lines: list[str], chomping: str | None = None
) -> str:
    """Convert captured block scalar lines to their plain scalar value."""
    if not lines:
        return ""
    if all(line == "" for line in lines):
        if chomping == "+":
            return "\n" * len(lines)
        return ""

    if style == "|":
        value = "\n".join(lines) + "\n"
    else:
        value = None
        previous = ""
        blank_count = 0
        for line in lines:
            if line == "":
                blank_count += 1
                continue
            if value is None:
                value = "\n" * blank_count + line
            elif blank_count:
                breaks = blank_count
                if _more_indented_content(line) or _more_indented_content(
                    previous
                ):
                    breaks += 1
                value += "\n" * breaks + line
            elif _more_indented_content(line) or _more_indented_content(
                previous
            ):
                value += "\n" + line
            else:
                value += " " + line
            previous = line
            blank_count = 0
        if value is None:
            value = "\n" * blank_count
        elif blank_count:
            value += "\n" * blank_count
        value += "\n"

    if chomping == "-":
        return value.rstrip("\n")
    if chomping == "+":
        return value
    return value.rstrip("\n") + "\n"


def _blank_block_line(
    line: str, line_indent: int, block_indent: int | None
) -> str:
    """Return preserved content for an all-space block scalar line."""
    if block_indent is not None and line_indent >= block_indent:
        return line[block_indent:]
    return ""


def parse_block_scalar_header(
    raw_value: str,
) -> tuple[str, str | None, int | None] | None:
    """Parse block scalar style/chomping indicators from |, >, |-, >+, etc."""
    if not raw_value or raw_value[0] not in ("|", ">"):
        return None
    style = raw_value[0]
    chomping = None
    indent_indicator = None
    for char in raw_value[1:]:
        if char in ("+", "-"):
            if chomping is not None:
                raise YamlParseError(
                    f"invalid block scalar indicators: {raw_value}"
                )
            chomping = char
        elif char.isdigit():
            if char == "0" or indent_indicator is not None:
                raise YamlParseError(
                    f"invalid block scalar indicators: {raw_value}"
                )
            indent_indicator = int(char)
            continue
        else:
            raise YamlParseError(
                f"invalid block scalar indicators: {raw_value}"
            )
    return style, chomping, indent_indicator


def parse_block_scalar_lines(
    lines: list[str],
    start: int,
    current_indent: int,
    indent_indicator: int | None = None,
    allow_same_indent: bool = False,
):
    """Capture block scalar lines and return (lines, next_index)."""
    block_lines = []
    block_indent = (
        current_indent + indent_indicator
        if indent_indicator is not None
        else None
    )
    i = start
    pending_blank_indents = []
    while i < len(lines):
        next_line = lines[i]
        next_line_indent = len(next_line) - len(next_line.lstrip(" "))
        content = next_line[next_line_indent:]
        if (
            content.startswith("\t")
            and block_indent is None
            and next_line_indent <= current_indent
        ):
            raise YamlParseError("tab indentation is not allowed")
        if content == "" or content.strip(" ") == "":
            if block_indent is None and next_line_indent > current_indent:
                pending_blank_indents.append(next_line_indent)
            block_lines.append(
                _blank_block_line(next_line, next_line_indent, block_indent)
            )
            i += 1
            continue
        if allow_same_indent:
            if next_line_indent < current_indent:
                break
        elif next_line_indent <= current_indent:
            break
        if block_indent is None:
            block_indent = next_line_indent
            if any(
                blank_indent > block_indent
                for blank_indent in pending_blank_indents
            ):
                raise YamlParseError("invalid block scalar indentation")
        if next_line_indent < block_indent:
            break
        block_lines.append(next_line[block_indent:])
        i += 1
    return block_lines, i
