# MEP-007: Multilines
**Author:** Jacob Stewart
**Status:** Draft  
**Created:** April 04, 2025  
**Target Language:** TBD


## 1. Abstract

This proposal defines the support for multiline constructs in our markup language. In addition to standard scalar types and collections, the language will support multiline strings, multiline arrays, multiline inline tables, and lists of inline tables. A key goal is to ensure that the original formatting—including newlines, indentation, and spacing—is preserved during parsing and round-trip operations.

---

## 2. Motivation

- **Readability:**  
  Multiline constructs allow configuration files to remain human‐readable, especially when embedding lengthy texts, code snippets, or documentation.
  
- **Fidelity:**  
  Preserving the exact formatting (newlines, indentation) is essential for maintaining clarity and ensuring that documentation or code embedded in the configuration is not lost or altered during round-trip processing.
  
- **Compatibility:**  
  Users are familiar with multiline constructs in similar formats (e.g., TOML, YAML). Supporting these features reduces the learning curve and promotes adoption.

---

## 3. Specification

### 3.1. Multiline Strings

- **Syntax:**  
  Multiline strings are enclosed in triple double quotes (`"""`), similar to TOML and Python.
  ```toml
  description = """
  This is a multiline
  string that preserves
  all newlines and indentation.
  """
  ```
- **Preservation:**  
  - All newline characters and leading/trailing whitespace on each line are preserved.
  - The parser must maintain the original formatting during both load and dump operations.

### 3.2. Multiline Arrays

- **Syntax:**  
  Arrays can be defined over multiple lines, with elements separated by commas.
  ```toml
  colors = [
    "red",
    "green",
    "blue"
  ]
  ```
- **Preservation:**  
  - The order of elements and any intentional line breaks for clarity are maintained.
  - Whitespace for readability is ignored in terms of value but preserved in the output formatting.

### 3.3. Multiline Inline Tables

- **Syntax:**  
  Inline tables are written using curly braces. When a table becomes complex, it can be split over multiple lines.
  ```toml
  user = { 
    name = "Alice", 
    email = "alice@example.com",
    bio = """
    Alice is a software engineer
    with 10 years of experience.
    Passionate about open source.
    """
  }
  ```
- **Preservation:**  
  - The inline table structure remains compact and parseable, even when spread across multiple lines.
  - Multiline string values within inline tables must preserve their formatting.

### 3.4. Lists of Inline Tables

- **Syntax:**  
  Lists of inline tables are defined by placing inline tables (using curly braces) inside an array.
  ```toml
  [project]
  name = "jaml"
  version = "0.1.0.dev8"
  description = "Swarmauri's Canon Jaml Handler"
  authors = [
    { name = "Jacob Stewart", email = "jacob@swarmauri.com" },
    { name = "Jacob Stewart", email = "jacob@swarmauri.com" },
    { name = "Jacob Stewart", email = "jacob@swarmauri.com" },
  ]
  ```
- **Preservation:**  
  - The structure of the inline tables is maintained as part of the array.
  - Newlines and indentation within each inline table (if formatted over multiple lines) are preserved.

### 3.5. General Multiline Preservation

- **Consistency:**  
  - All multiline constructs, whether strings, arrays, or inline tables, will preserve their original formatting during round-trip operations.
  - The output from the language’s parser (or dump function) should exactly match the original formatting, aside from normalization of insignificant whitespace.

---

## 4. Examples

### Example 1: Multiline String

```toml
[metadata]
description = """
This project is designed to:
- Provide excellent performance.
- Support multiple languages.
- Ensure data integrity.
"""
```

### Example 2: Multiline Array

```toml
[settings]
colors = [
  "red",
  "green",
  "blue"
]
```

### Example 3: Multiline Inline Table

```toml
[user]
profile = {
  name = "Alice",
  bio = """
Alice is a dedicated developer.
She specializes in backend systems.
"""
}
```

### Example 4: Table with a List of Inline Tables

```toml
[project]
name = "jaml"
version = "0.1.0.dev8"
description = "Swarmauri's Canon Jaml Handler"
authors = [
  { name = "Jacob Stewart", email = "jacob@swarmauri.com" },
  { name = "Jacob Stewart", email = "jacob@swarmauri.com" },
  { name = "Jacob Stewart", email = "jacob@swarmauri.com" },
]
```

---

## 5. Open Issues

- **Whitespace Handling:**  
  Should leading and trailing whitespace in each line be preserved exactly, or is some normalization allowed?
  
- **Indentation Rules:**  
  How should indentation within multiline strings and inline tables be treated, especially when round-tripping?
  
- **Integration with Dynamic Evaluation:**  
  Future enhancements may interact with multiline constructs. For now, this proposal focuses solely on preserving literal formatting.

---

## 6. Conclusion

MEP-007 defines the support for multiline constructs in our new markup language. By enabling multiline strings, arrays, inline tables, and lists of inline tables—and ensuring that all formatting is preserved—we provide users with a configuration format that is both expressive and true to its original layout. This proposal lays the groundwork for enhanced readability, maintainability, and future dynamic features.

