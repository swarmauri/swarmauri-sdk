# MEP-004: Type Inference
**Author:** Jacob Stewart
**Status:** Draft  
**Created:** April 04, 2025  
**Target Language:** TBD


## 1. Abstract

This proposal defines the type inference mechanism within our markup language. Type inference automatically determines the data type of a value or expression when no explicit type annotation is provided. By incorporating type inference, the language achieves a balance between explicitness and convenience, improving readability, usability, and reducing verbosity in configurations.

---

## 2. Motivation

- **Usability and Convenience:**  
  Automatically inferring types removes the need for explicit type declarations in simple or obvious scenarios, improving ease-of-use.

- **Readability and Maintainability:**  
  Configurations become more concise and readable, enhancing maintainability without sacrificing clarity.

- **Reducing Redundancy:**  
  Eliminates the redundancy of explicitly declaring types when the data type is inherently clear.

- **Error Prevention:**  
  Early detection and clearer error messages when inferred types conflict with expected usage.

---

## 3. Specification

### 3.1. Basic Type Inference Rules

The markup language infers the type of a value according to the following rules:

| Literal Form                             | Inferred Type             |
| ---------------------------------------- | ------------------------- |
| `"Hello, World!"`                        | `str`                     |
| `'Hello, World!'`                        | `str`                     |
| `'''Multi-line\ntext'''`                 | `str`                     |
| `123`, `0xFF`, `0b1010`, `0o52`          | `int`                     |
| `3.14`, `-0.01`, `1e-10`, `inf`, `nan`   | `float`                   |
| `true`, `false`                          | `bool`                    |
| `null`                                   | `null`                    |
| `[1, 2, 3]`, `["a", "b"]`                | `list` (homogeneous or heterogeneous)|
| `{ x = 10, y = 20 }`                     | `table`                   |

### 3.2. Expression Type Inference

When values are computed using expressions (`~(...)`), the language infers their types from the evaluated result:

- Arithmetic expressions (`~(1 + 2)`) infer numeric types (`int`, `float`).
- String concatenation (`~("Hello, " + "World!")`) infers `str`.
- Logical and conditional expressions (`~(true and false)`) infer `bool`.
- List comprehensions (`~([x * 2 for x in [1, 2]])`) infer `list`.
- Expressions involving scoped variables (`@{}`, `%{}`) infer their types based on the referenced values.

### 3.3. Type Annotation Overrides

Explicit type annotations, if provided, always override inference:

```toml
count: float = 3     # explicitly float, despite literal integer
flag: str = true     # explicitly str, despite literal boolean
```

### 3.4. Conflicts and Error Handling

If an inferred type conflicts with an explicitly annotated type, the parser will:

- Emit a clear and descriptive error message indicating the conflict.
- Suggest explicit casting or correction.

---

## 4. Examples

### Example 1: Basic Type Inference

```toml
[database]
port = 5432               # inferred as int
host = "localhost"        # inferred as str
ssl_enabled = true        # inferred as bool
```

### Example 2: Expression-Based Inference

```toml
[paths]
base = "/etc/app"
config_path = "path/to/file"
timeout = 30
```

### Example 3: List and Table Inference

```toml
[settings]
modes = ["read", "write", "execute"]  # inferred as list[str]

[coordinates]
point = { x = 10, y = 20 }            # inferred as table with int values
```

### Example 4: Explicit Type Override

```toml
[flags]
value: str = true    # stored as str ("true"), despite boolean literal
```

---

## 5. Open Issues

- **Heterogeneous Lists:**  
  Should lists containing mixed types (`["a", 1, true]`) infer as a generic `list` or raise a type warning/error?

- **Complex Expressions:**  
  Establish boundaries for inference complexity in deeply nested expressions or comprehensions.

- **Inference Across File Boundaries:**  
  Clarify how inference should behave when referencing external or included files.

---

## 6. Conclusion

MEP-004 introduces type inference to our markup language, balancing explicit typing and convenience. With clearly defined inference rules, the language becomes easier to write, read, and maintain. Explicit annotations remain available to override inferred types, offering flexibility and clarity. This proposal forms the foundation for intuitive, type-safe configurations while minimizing redundancy.
