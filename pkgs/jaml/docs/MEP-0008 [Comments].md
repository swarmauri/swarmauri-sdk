# MEP-008: Comments
**Author:** Jacob Stewart
**Status:** Draft  
**Created:** April 04, 2025  
**Target Language:** TBD


## 1. Abstract

This proposal specifies the rules and behavior for comments in our new markup language. Comments are denoted by the `#` character and can appear as standalone lines, inline after a key-value pair, or within multiline constructs. An essential requirement is that round-trip parsers—tools that load and then dump the configuration—must preserve all comments exactly as authored, ensuring that no commentary is lost during parsing and serialization.

---

## 2. Motivation

- **Documentation and Clarity:**  
  Comments are critical for explaining configuration choices, documenting the purpose of keys, and providing guidance to users. They enhance readability and maintainability.

- **Familiarity:**  
  The `#` comment syntax is widely recognized from other configuration languages (e.g., TOML, YAML, Python), reducing the learning curve for users.

- **Round-Trip Integrity:**  
  Preserving comments through round-trip parsing ensures that valuable context and documentation are maintained even as configuration files are processed by tools.

---

## 3. Specification

### 3.1. Comment Syntax

- **Single-Line Comments:**  
  A comment begins with the `#` character and extends to the end of the line. These can appear on lines by themselves:
  ```toml
  # This is a comment
  ```
  
- **Inline Comments:**  
  Comments can appear after a key-value pair on the same line. A space should precede the `#` to differentiate the comment from the value:
  ```toml
  greeting = "Hello, World!"  # This is an inline comment
  ```
  
- **Comments in Multiline Constructs:**  
  - **Multiline Strings:**  
    Comments can appear on their own lines within a multiline string block, but if a `#` appears within the quoted text, it is treated as part of the string.
  - **Multiline Arrays/Inline Tables:**  
    Comments may be interspersed among elements or key-value pairs. In these cases, comments are allowed on lines between elements, or at the end of lines after an element, provided there is a space before the `#`.

### 3.2. Preservation of Comments

- **Round-Trip Parsing:**  
  Any parser implementing the specification must preserve comments exactly as they appear in the original document. This includes:
  - The placement and content of standalone comment lines.
  - Inline comments associated with key-value pairs.
  - Comments within multiline arrays and inline tables.
  
- **Normalization:**  
  While the parser may normalize insignificant whitespace, it must not alter or remove comments during round-trip operations.

---

## 4. Examples

### Example 1: Standalone and Inline Comments

```toml
# This is a standalone comment at the top of the file

[section]
# Comment before greeting
greeting = "Hello, World!"  # Inline comment: greeting message
```

### Example 2: Multiline Arrays with Comments

```toml
[settings]
colors = [
  "red",    # Primary color
  "green",  # Secondary color
  "blue"    # Accent color
]
```

### Example 3: Multiline Inline Tables with Comments

```toml
[user]
profile = {
  name = "Alice",         # User's name
  email = "alice@example.com",  # User's email
  bio = """
  Alice is a software engineer.
  She loves coding and open source.
  # Note: The '#' here is part of the bio text, not a comment.
  """
}
```

---

## 5. Open Issues

- **Comment Positioning in Multiline Strings:**  
  Clarify whether comments placed within the boundaries of a multiline string (outside the quotes) should be preserved as separate comment lines.
  
- **Whitespace Normalization:**  
  Determine the extent to which whitespace around comments can be normalized without altering the comment's content or intent.
  
- **Tooling Integration:**  
  Ensure that code editors and linters can correctly identify and handle comments without impacting auto-completion or formatting features.

---

## 6. Conclusion

MEP-008 defines the rules for using comments in our new markup language. By using the `#` symbol for comments, supporting standalone and inline usage, and ensuring that comments are preserved during round-trip parsing, we maintain the clarity and documentation benefits that comments provide. This proposal forms an integral part of our overall specification, helping to create a robust and user-friendly configuration language.

