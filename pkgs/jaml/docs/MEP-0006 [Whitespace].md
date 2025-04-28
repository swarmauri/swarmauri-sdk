# MEP-006: Whitespace
**Author:** Jacob Stewart
**Status:** Draft  
**Created:** April 04, 2025  
**Target Language:** TBD


## 1. Abstract

This proposal defines how whitespace is handled in our markup language. Whitespace is essential for readability and formatting but should not interfere with data representation or introduce ambiguities. This specification outlines how whitespace is treated in various contexts, including key-value pairs, inline tables, arrays, and multiline constructs.

---

## 2. Motivation

- **Readability:**  
  Proper use of whitespace enhances the clarity and organization of configuration files.

- **Predictability:**  
  Ensuring consistent whitespace handling prevents unexpected behavior and parsing errors.

- **Format Preservation:**  
  Some constructs, especially multiline strings and arrays, require precise whitespace preservation for accurate representation.

---

## 3. Specification

### 3.1. General Whitespace Rules

- Whitespace includes spaces, tabs, and newlines.
- Whitespace is generally **ignored** when it appears between tokens, unless specified otherwise.
- Whitespace **should not** affect the semantic meaning of the configuration.

#### Allowed Whitespace:
- Between keys and assignment operators (`key = value`)
- Around punctuation (commas in arrays, colons in type annotations)
- Inside inline tables, lists, and multiline arrays
- Before and after operators in expressions
- Between table headers and their body

#### Disallowed Whitespace:
- Inside unquoted keys (e.g., `my key` is invalid)
- Inside unquoted strings (e.g., `name = my value` without quotes)

---

### 3.2. Leading and Trailing Whitespace

- Leading and trailing whitespace in **string values** is **preserved**.
- Leading and trailing whitespace in **unquoted keys** is **trimmed** during parsing.
- Trailing whitespace after values on the same line is **ignored**.

**Example:**
```toml
[settings]
name = "  Azzy  "   # Preserves leading and trailing spaces in the value
title =  "Dev"      # Trailing space after "Dev" is ignored
```

**Parsed:**
```json
{
  "settings": {
    "name": "  Azzy  ",
    "title": "Dev"
  }
}
```

---

### 3.3. Whitespace in Key-Value Pairs

- Whitespace around the assignment operator (`=`) is allowed but not required.
- Excessive whitespace is normalized to a single space when dumped back into the file.

**Example:**
```toml
[config]
key =    "value"
```

**Parsed:**
```json
{
  "config": {
    "key": "value"
  }
}
```

---

### 3.4. Whitespace in Inline Tables and Arrays

- Whitespace inside inline tables and arrays is ignored during parsing but preserved when round-tripping the file.
- Inline tables and arrays may include newlines to enhance readability.

**Example:**
```toml
[user]
profile = { name = "Alice", age = 30 }

[colors]
list = [
  "red", 
  "green", 
  "blue"
]
```

**Parsed:**
```json
{
  "user": {
    "profile": {
      "name": "Alice",
      "age": 30
    }
  },
  "colors": {
    "list": ["red", "green", "blue"]
  }
}
```

---

### 3.5. Whitespace in Multiline Strings and Arrays

- Whitespace within multiline strings is **preserved**, including newlines and indentation.
- Whitespace in multiline arrays is ignored during parsing but maintained when round-tripping.

**Example:**
```toml
[documentation]
description = """
  This is a multiline
  description with
  leading whitespace.
  """
```

**Parsed:**
```json
{
  "documentation": {
    "description": "  This is a multiline\n  description with\n  leading whitespace.\n  "
  }
}
```

---

### 3.6. Whitespace in Expressions

- Whitespace within expressions enclosed in `~(...)` is ignored when evaluating the expression.
- Whitespace between operators and operands is optional but recommended for readability.

**Example:**
```toml
[calculation]
result = ~( 1 + 2 * 3 )
```

**Parsed:**
```json
{
  "calculation": {
    "result": 7
  }
}
```

---

## 4. Error Handling

- **Invalid Key Whitespace:**  
  Keys containing unquoted whitespace will raise a syntax error:
  ```toml
  [invalid]
  my key = "value"  # Syntax Error: Unquoted whitespace in key
  ```
- **Trailing Whitespace in Keys:**  
  Trailing whitespace after key names will be **trimmed** and **ignored**.
- **Unexpected Newlines:**  
  Newlines within key-value pairs (without line continuation) will raise a syntax error.

---

## 5. Examples

### Example 1: Valid Whitespace Usage

```toml
[config]
path = "/usr/local"   # Space before and after '='
timeout =  30         # Space after '='
```

### Example 2: Inline Table with Whitespace

```toml
[user]
profile = { name = "John",  age = 25 }
```

### Example 3: Multiline Array with Whitespace

```toml
[fruits]
list = [
    "apple",
    "banana",
    "cherry"
]
```

### Example 4: Multiline String with Leading Whitespace

```toml
[description]
text = """
    This is a detailed
    description with
    preserved indentation.
    """
```

---

## 6. Open Issues

- **Line Continuation:**  
  Should we support line continuation for long key-value pairs using backslashes?

- **Whitespace Normalization:**  
  Evaluate whether excessive whitespace within expressions should be normalized.

- **Preservation vs. Ignoring:**  
  Clarify edge cases where whitespace preservation might conflict with expected formatting.

---

## 7. Conclusion

MEP-006 specifies the handling of whitespace in our markup language. By establishing clear rules for whitespace in keys, values, inline tables, arrays, and multiline strings, we ensure that configurations remain both human-readable and unambiguous. Proper handling of whitespace during parsing and round-trip operations preserves formatting without introducing inconsistencies.
