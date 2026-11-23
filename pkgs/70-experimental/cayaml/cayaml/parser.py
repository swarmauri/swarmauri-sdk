"""parser.py - YAML parser for Cayaml (Swarmauri's Canon YAML)."""

from .ast_nodes import (
    MappingNode,
    SequenceNode,
    ScalarNode,
    YamlStream,
    DocumentNode,
)
from .block_parser import parse_block, skip_blank_and_comment
from .construction import assign_node_metadata
from .errors import YamlParseError
from .properties import split_tag_anchor_prefix
from .scanner import (
    find_top_level_colon,
    has_unclosed_quote,
    is_document_marker,
    split_inline_comment,
)
from .tags import DEFAULT_TAG_HANDLES, TAG_HANDLES_KEY
from .directives import parse_directive


def _internal_parse_stream(yaml_str: str) -> YamlStream:
    """
    Tokenize and parse YAML into a YamlStream.
    """
    lines = yaml_str.splitlines()
    return parse_stream(lines)


def _internal_load(yaml_str: str):
    """
    Parse a YAML string and return an AST.
    If there is only one document, return that DocumentNode;
    otherwise, return a YamlStream containing multiple DocumentNodes.
    """
    lines = yaml_str.splitlines()
    stream = parse_stream(lines)
    if len(stream.documents) == 1:
        return stream.documents[0]
    return stream


def _internal_to_ast(data):
    """
    Convert plain Python data (dict, list, or scalar) into our AST.
    """

    if isinstance(data, dict):
        node = MappingNode()
        for key, value in data.items():
            key_node = ScalarNode(key)
            value_node = _internal_to_ast(value)
            node.add_pair(key_node, value_node)
        return node
    elif isinstance(data, list):
        node = SequenceNode()
        for item in data:
            node.add_item(_internal_to_ast(item))
        return node
    else:
        return ScalarNode(data)


def parse_stream(lines: list) -> YamlStream:
    """
    Parse the entire YAML stream (which may contain multiple documents).
    Returns a YamlStream object containing DocumentNode(s).
    """
    stream = YamlStream()
    i = 0
    n = len(lines)
    anchors = {}

    while i < n:
        if i == 0 and lines[i].startswith("\ufeff"):
            lines[i] = lines[i][1:]

        leading_comments = []
        # Skip any leading blank lines and collect leading comments.
        while i < n and (
            not lines[i].strip() or lines[i].lstrip().startswith("#")
        ):
            if lines[i].lstrip().startswith("#"):
                leading_comments.append(lines[i].strip())
            i += 1
        if i >= n:
            break

        doc = DocumentNode()
        doc.leading_comments.extend(leading_comments)
        tag_handles = dict(DEFAULT_TAG_HANDLES)
        directives = []
        seen_yaml_directives = set()
        seen_tag_handles = set()
        while i < n and lines[i].lstrip().startswith("%"):
            if not lines[i].startswith("%"):
                raise YamlParseError("directive must start at column zero")
            directive_line = lines[i].strip()
            parsed = parse_directive(
                directive_line,
                tag_handles,
                seen_yaml=seen_yaml_directives,
                seen_tag_handles=seen_tag_handles,
            )
            directives.append(directive_line)
            if parsed and parsed[0] == "YAML":
                doc.yaml_version = parsed[1]
            i += 1
        doc.tag_handles = {
            key: value
            for key, value in tag_handles.items()
            if key not in DEFAULT_TAG_HANDLES
            or DEFAULT_TAG_HANDLES[key] != value
        }
        doc.directives = directives
        anchors.clear()
        anchors[TAG_HANDLES_KEY] = tag_handles
        while i < n and (
            not lines[i].strip() or lines[i].lstrip().startswith("#")
        ):
            if lines[i].lstrip().startswith("#"):
                doc.leading_comments.append(lines[i].strip())
            i += 1
        if i >= n:
            if directives:
                raise YamlParseError("directive without document")
            stream.add_document(doc)
            break

        line = lines[i].strip()
        if is_document_marker(line, "..."):
            if directives:
                raise YamlParseError("directive without document")
            i += 1
            continue

        inline_root = None
        if is_document_marker(line, "---"):
            doc.has_doc_start = True
            marker_content, _ = split_inline_comment(line)
            inline_root = marker_content[3:].strip() or None
            if inline_root:
                root_tag, root_anchor, root_rest = split_tag_anchor_prefix(
                    inline_root
                )
                if (root_tag or root_anchor) and find_top_level_colon(
                    root_rest
                ) != -1:
                    raise YamlParseError(
                        "properties cannot prefix an inline mapping root"
                    )
            i += 1

        # Collect lines for *this* document until we see '...' or '---'
        doc_lines = []
        if inline_root is not None:
            doc_lines.append(inline_root)
        while i < n:
            curr = lines[i].rstrip("\n")
            curr_strip = curr.strip()
            if curr.lstrip().startswith(("%YAML", "%TAG")):
                lookahead = i + 1
                while lookahead < n and not lines[lookahead].strip():
                    lookahead += 1
                directive_before_marker = lookahead < n and is_document_marker(
                    lines[lookahead].strip(), "---"
                )
                if directive_before_marker:
                    raise YamlParseError("directive after document content")
            if is_document_marker(curr_strip, "..."):
                marker_content, _ = split_inline_comment(curr_strip)
                if marker_content.strip() != "...":
                    raise YamlParseError("invalid document end marker")
                if has_unclosed_quote("\n".join(doc_lines)):
                    raise YamlParseError("unterminated quoted scalar")
                doc.has_doc_end = True
                i += 1
                break
            if is_document_marker(curr_strip, "---"):
                if has_unclosed_quote("\n".join(doc_lines)):
                    raise YamlParseError("unterminated quoted scalar")
                # Start of next doc
                break
            doc_lines.append(curr)
            i += 1

        pending_root_tag = None
        pending_root_anchor = None
        while doc_lines:
            first_doc_line = doc_lines[0].strip()
            tag, anchor, remaining = split_tag_anchor_prefix(first_doc_line)
            if not remaining and (tag or anchor):
                pending_root_tag = tag or pending_root_tag
                pending_root_anchor = anchor or pending_root_anchor
                doc_lines.pop(0)
                continue
            break

        # If we have lines for this document, parse them as a block
        if doc_lines:
            doc.root, remaining = parse_block(
                doc_lines, indent=0, anchors=anchors
            )
            if skip_blank_and_comment(remaining):
                raise YamlParseError("extra content after document root node")
            if pending_root_tag and doc.root is not None:
                assign_node_metadata(
                    doc.root,
                    tag=pending_root_tag,
                    anchor=pending_root_anchor,
                    anchors=anchors,
                )
            elif pending_root_anchor and doc.root is not None:
                assign_node_metadata(
                    doc.root,
                    anchor=pending_root_anchor,
                    anchors=anchors,
                )
        stream.add_document(doc)

    return stream
