# MEP-009: Type Annotations
**Author:** Jacob Stewart
**Status:** Draft  
**Created:** April 04, 2025  
**Target Language:** TBD


## 1. Abstract

This proposal defines the syntax and semantics for type annotations within our markup language. Type annotations allow users to explicitly declare the expected data type of a key's value, enhancing both readability and validation. Supported annotations include primitive types such as `str`, `int`, `float`, `bool`, and `null`, as well as collection types like `list` and composite types such as `table` for inline tables. This mechanism provides a clear, human-readable way to communicate the intended type and enables potential future static type checking or runtime validations.

---

## 2. Motivation

- **Improved Documentation:**  
  By explicitly annotating types (e.g., `greeting: str`), the configuration becomes self-documenting. This makes it easier for both users and tools to understand the intended use of each field.

- **Enhanced Validation:**  
  Type annotations provide a basis for verifying that values conform to expected types. This helps catch configuration errors early, reducing runtime errors.

- **Consistency and Clarity:**  
  A clear, consistent type annotation syntax aligns with modern programming practices and improves maintainability for complex configurations.

- **Extensibility:**  
  Future enhancements may leverage these annotations for advanced features such as schema validation, auto-completion in editors, and improved interoperability with other data formats.

---

## 3. Specification

### 3.1. Supported Type Annotations

The following type annotations are supported:

- **Primitive Types:**
  - **`str`**: Denotes string values enclosed in double quotes.
  - **`int`**: Denotes integer values, supporting decimal, octal (`0o` prefix), hexadecimal (`0x` prefix), and binary (`0b` prefix) formats.
  - **`float`**: Denotes floating-point numbers, including standard floats as well as special values like `inf` and `nan`.
  - **`bool`**: Denotes Boolean values (`true` and `false`).
  - **`null`**: Denotes a null value.

- **Collection Types:**
  - **`list`**: Denotes an array. Both inline arrays (using square brackets) and multiline arrays are supported.
  - **`table`**: Denotes an inline table, which is represented as a dictionary-like structure enclosed in curly braces.

### 3.2. Annotation Syntax

Type annotations are written immediately after a key using a colon, followed by the type name. The general format is:

```toml
key: type = value
```

For example:
- **String Annotation:**  
  ```toml
  greeting: str = "Hello, World!"
  ```
- **Integer Annotation:**  
  ```toml
  answer: int = 42
  ```
- **Float Annotation:**  
  ```toml
  pi: float = 3.14
  ```
- **Boolean Annotation:**  
  ```toml
  is_active: bool = true
  ```
- **List Annotation:**  
  ```toml
  colors: list = ["red", "green", "blue"]
  ```
- **Inline Table Annotation:**  
  ```toml
  point: table = { x = 10, y = 20 }
  ```
- **Null Annotation:**  
  ```toml
  missing: null = null
  ```

### 3.3. Semantics

- **Declaration:**  
  The type annotation acts as a declaration, informing both the parser and the user of the intended type for the key’s value.
- **Validation:**  
  At load time, the system may optionally validate that the provided value conforms to the declared type.  
- **Documentation:**  
  Type annotations improve the readability of configuration files and serve as documentation for developers.

---

## 4. Examples

### 4.1. Basic Scalars

```toml
[section]
greeting: str = "Hello, World!"
answer: int = 42
pi: float = 3.14
infinity: float = inf
not_a_number: float = nan
is_active: bool = true
is_valid: bool = false
missing: null = null
```

### 4.2. Lists

```toml
[section]
numbers: list = [1, 2, 3, 4]
colors: list = ["red", "green", "blue"]
```

### 4.3. Tables

```toml
[section]
point: table = { x = 10, y = 20 }
```

### 4.4. Nested Inline Tables

```toml
[section]
user: table = { name = "Azzy", details = { age = 9, role = "admin" } }
```

### 4.5. Table Arrays and Lists of Inline Tables

```toml
[project]
name: str = "jaml"
version: str = "0.1.0.dev8"
description: str = "Swarmauri's Canon Jaml Handler"
authors: list = [{ name: str = "Jacob Stewart", email: str = "jacob@swarmauri.com" }]
```

---

## 5. Open Issues

- **Validation Mechanisms:**  
  How strict should type validation be? Should the system enforce types at load time, or simply serve as documentation?
  
- **Complex Types:**  
  How to handle nested or composite types beyond the basic ones. Future proposals may extend support to union types or custom schemas.

- **Interoperability:**  
  Mapping our type annotations to other configuration formats (e.g., JSON Schema) remains an open area for future work.

---

## 6. Conclusion

MEP-009 establishes a clear, concise method for adding type annotations to our new markup language. By following a syntax similar to `key: type = value`, we provide both human-readable documentation and a potential mechanism for validation. This proposal builds on the simplicity and readability of TOML while introducing modern, explicit type declarations. It lays the groundwork for advanced type checking and further enhancements in future MEPs.
