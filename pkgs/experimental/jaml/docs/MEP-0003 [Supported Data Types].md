# MEP-003: Supported Data Types
**Author:** Jacob Stewart
**Status:** Draft  
**Created:** April 04, 2025  
**Target Language:** TBD


## 1. Abstract

This proposal defines the set of data types and structural elements that our new markup language will support. The design aims to be simple and human‐readable—taking inspiration from TOML—while extending support to both static and dynamic constructs. Supported data types include strings (with newline preservation and literal strings), integers (including decimal, octal, hexadecimal, and binary), floats (including special values like infinity and NaN), booleans, null, arrays (both inline and multiline), inline tables, and standard tables. In addition, the language supports sections/tables and table arrays.

---

## 2. Motivation

- **Human-Readable Syntax:**  
  The markup language should be simple and readable. We draw inspiration from TOML, keeping the syntax close to what users expect while introducing modern features.

- **Comprehensive Type and Structure Support:**  
  Users need a broad range of data types and structures to configure applications. This includes not only basic scalar types but also collections (arrays, inline tables) and higher-level structures (sections/tables, table arrays).

- **Modular Organization:**  
  The use of sections/tables and table arrays enables users to organize their configuration data into logical blocks and lists of tables, which is crucial for large and complex configurations.

---

## 3. Specification

### 3.1. Scalar Types

- **String:**  
  - Enclosed in double quotes.  
  - Newlines within strings are preserved.  
  - Literal strings (e.g., Windows paths) support standard escape sequences.

- **Integer:**  
  - Decimal integers (e.g., `42`).
  - Octal integers using the `0o` prefix (e.g., `0o52` equals 42).
  - Hexadecimal integers using the `0x` prefix (e.g., `0x2A` equals 42).
  - Binary integers using the `0b` prefix (e.g., `0b101010` equals 42).

- **Float:**  
  - Standard floating-point numbers (e.g., `3.14`).
  - Special values: `inf` for infinity and `nan` for not-a-number.

- **Boolean:**  
  - Literal values: `true` and `false`.

- **Null:**  
  - Represented as `null`.

### 3.2. Collection Types

- **Arrays:**  
  - **Inline Arrays:** Defined with square brackets, with values separated by commas.  
    _Example:_  
    ```toml
    numbers = [1, 2, 3, 4]
    ```
  - **Multiline Arrays:** Similar to inline arrays but can span multiple lines while preserving formatting.

- **Tables and Inline Tables:**  
  - **Standard Tables (Sections):**  
    Defined using square brackets. They represent named sections of configuration data.
    _Example:_  
    ```toml
    [section]
    key = "value"
    ```
  - **Table Arrays:**  
    Defined using double square brackets (`[[...]]`), these represent arrays of tables.
    _Example:_  
    ```toml
    [[products]]
    name = "Widget"
    price = 9.99

    [[products]]
    name = "Gadget"
    price = 12.49
    ```
  - **Inline Tables:**  
    Defined using curly braces, allowing a compact, one-line dictionary-like structure.
    _Example:_  
    ```toml
    point = { x = 10, y = 20 }
    ```
    
  - **Lists of Inline Tables:**  
    Inline tables may also be used as elements in an array to represent a list of dictionaries.  
    _Example:_  
    ```toml
    [project]
    name = "jaml"
    version = "0.1.0.dev8"
    description = "Swarmauri's Canon Jaml Handler"
    authors = [{ name = "Jacob Stewart", email = "jacob@swarmauri.com" }]
    ```

  - **Nested Inline Tables:**  
    Inline tables can be nested within one another to represent hierarchical data.
    _Example:_  
    ```toml
    user = { name = "Azzy", details = { age = 9, role = "admin" } }
    ```

---

## 4. Examples

### 4.1. Scalar Examples

```toml
[section]
greeting = "Hello, World!"
multiline = "Hello, World!\nHello, World!"
```

```toml
[paths]
windows_path = "C:\\Users\\Alice\\My Docs"
```

```toml
[section]
answer = 42
pi = 3.14
infinity = inf
not_a_number = nan
is_active = true
is_valid = false
missing = null
```

```toml
[section]
octal = 0o52
hex = 0x2A
binary = 0b101010
```

### 4.2. Array and Table Examples

```toml
[section]
numbers = [1, 2, 3, 4]
colors = ["red", "green", "blue"]
```

```toml
[section]
point = { x = 10, y = 20 }
```

```toml
[section]
user = { name = "Azzy", details = { age = 9, role = "admin" } }
```

```toml
[address]
city = "New York"
zip = 10001
```

#### **Tables and Table Arrays:**

```toml
[database]
host = "localhost"
port = 5432
```

```toml
[[products]]
name = "Widget"
price = 9.99

[[products]]
name = "Gadget"
price = 12.49
```

---

## 5. Open Issues

- **Dynamic Evaluation Semantics:**  
  Dynamic expressions (those wrapped in evaluation enclosures) are currently preserved as literal strings. Future enhancements may execute these expressions.

- **Error Handling:**  
  Defining robust error messages and fallback behaviors when invalid types or structures are encountered.

- **Interoperability with Existing Formats:**  
  Ensuring that our data types and structures map neatly to constructs in TOML, JSON, and YAML.

---

## 6. Conclusion

MEP-003 outlines the supported data types and structural elements for our new markup language. Our approach is to maintain simplicity and human-readability by closely aligning with TOML's core design, while extending support to both static and dynamic constructs. This proposal establishes a solid foundation for future enhancements, including dynamic evaluation and more complex type transformations. It also explicitly defines sections/tables and table arrays, ensuring that the language can organize configuration data in a modular, intuitive manner.

