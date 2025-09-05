# MEP-0022: Expressions
**Author:** Jacob Stewart
**Status:** Draft  
**Created:** April 04, 2025  
**Target Language:** TBD


## 1. Abstract

This proposal defines the syntax and semantics for expressions in our new markup language, introducing a unified system for immediate (load-time) evaluation. In MEP-0022, expressions are enclosed in `<{}>` and `<()>` for different types of evaluations. The evaluated result is inserted into the final configuration without extra quotation marks, and its type is either explicitly declared or inferred by the parser.

---

## 2. Motivation

- **Immediate Computation:**  
  Evaluating expressions at load time ensures that computed values are fixed and available immediately, reducing runtime overhead.

- **Predictable and Type-Safe Configuration:**  
  By performing load-time evaluation and type inference, users can design configurations that are both predictable and type-correct. The evaluated result is inserted into the configuration as a plain value (without extra quotes) according to its inferred or declared type.

- **Separation of Concerns:**  
  Load-time expressions are restricted to variables defined within the file (global and table-local scopes). This clear separation prevents accidental reliance on external (render-time) context variables in this phase.

- **Simplified Syntax:**  
  Using two distinct enclosures—`<{}>` and `<()>`—simplifies the expression system. These two formats allow for different uses of expressions, with `<{}>` used for typical expressions and `<()>` used for folded expressions, making it easier to read and write.

---

## 3. Specification

### 3.1. Syntax: `<{}>` (Expression)

- **Expression Enclosure:**  
  Expressions that require immediate evaluation are wrapped in `<{}>`. These expressions will be computed at load-time when the configuration file is loaded.
  ```toml
  key = <{ expression }>
  ```

  **Example:**
  ```toml
  config = <{ @{base} + '/config.toml' }>
  ```

### 3.2. Syntax: `<()>` (Folded Expression)

- **Folded Expression Enclosure:**  
  This syntax is used for expressions that are easier to type and read, simplifying complex expressions without sacrificing readability. Folded expressions are still evaluated immediately at load-time like regular expressions, but they are more readable and user-friendly.
  ```toml
  key = <( expression )>
  ```

  **Example:**
  ```toml
  config = <( @{base} + '/config.toml' )>
  ```

  The `<( ... )>` syntax is functionally equivalent to `<{}>` but is easier to type and more readable in the case of complex or long expressions.

### 3.3. Type Inference and Operations

- **Type Inference:**  
  The type of an expression’s result is either declared on the key or inferred by the parser.  
  - When a string is expected, the result is inserted as a plain string (without extra quotes).
  - When a numeric or boolean type is expected, the expression result is converted accordingly.

- **Allowed Operations:**  
  Expressions support:
  - **Arithmetic:** `+`, `-`, `*`, `/`, etc.
  - **String Concatenation:** For example, `<{ @{base} + '/config.toml' }>` results in string concatenation.
  - **Conditional Expressions:** Ternary-like syntax (e.g., `<{ "DEBUG" if false else "INFO" }>`).
  - **List Comprehensions:** For creating lists from static arrays.
  - **Logical Operators:** Such as `and`, `or`, etc.

### 3.4. Scope Restrictions

- **Allowed Scopes:**  
  - **Global Scope (`@{...}`):**  
    Variables defined in a global section or as defaults.
  - **Self (Table-Local) Scope (`%{...}`):**  
    Variables defined within the same table.
  
- **Disallowed Scopes:**  
  - **Context Scope (`${...}`):**  
    External context variables are not allowed in `<{}>` or `<()>` expressions. Any attempt to use a context variable in this phase must trigger a validation error.

### 3.5. Evaluation Semantics

- **Immediate Resolution:**  
  Expressions enclosed in `<{}>` or `<()>` are evaluated immediately when the configuration file is loaded. The resulting value replaces the original expression.

- **Insertion of Results:**  
  Regardless of whether the result is a string, number, boolean, or list, it is inserted directly into the configuration without additional quotation marks.

- **Static Behavior:**  
  All computations in `<{}>` and `<()>` are static and are not re-evaluated at runtime.

### 3.6. Error Handling

- If an expression refers to an undefined variable or includes a disallowed context variable (`${...}`), the parser must raise a descriptive error.
- Syntax errors within the expression should produce clear error messages, indicating the error’s location and nature.

---

## 4. Examples

### Example 1: Simple String Concatenation

```toml
[paths]
base = "/usr/local"
config = <{ @{base} + '/config.toml' }>
```

*Explanation:*  
The global variable `@{base}` is concatenated with the literal `'/config.toml'` to yield the string `/usr/local/config.toml`.

### Example 2: Arithmetic Computation

```toml
[settings]
default_retries = 3
max_retries = <{ @{default_retries} * 2 }>
```

*Explanation:*  
Multiplies `3` by `2` to yield the integer `6`.

### Example 3: Conditional Expression

```toml
[system]
debug_mode = false
log_level: str = <{ "DEBUG" if false else "INFO" }>
```

*Explanation:*  
Since the condition is false, the expression evaluates to `"INFO"` and inserts it as a plain string.

### Example 4: List Comprehension

```toml
[data]
values = <{ [x * 2 for x in [1, 2, 3]] }>
```

*Explanation:*  
The expression produces the list `[2, 4, 6]`.

### Example 5: Folded Expression for Readability

```toml
[server]
address = <( @{host} + ":" + @{port} )>
```

*Explanation:*  
The folded expression `<( @{host} + ":" + @{port} )>` is easier to read and type compared to `<{ @{host} + ":" + @{port} }>`. It resolves to the combined value of `@{host}` and `@{port}`, yielding a string like `"localhost:8080"`.

---

## 5. Open Issues

- **Complexity Limits:**  
  Define acceptable complexity for load-time expressions, especially regarding nesting and operator precedence.
  
- **Operator Precedence:**  
  Establish precise rules to avoid ambiguity in expressions involving multiple operators.
  
- **Tooling and Debugging:**  
  Ensure that editor plugins and error messages correctly reflect the semantics of `<{}>` and `<()>` expressions.

---

## 6. Conclusion

MEP-0022 introduces a unified expression system for our markup language using the `<{}>` syntax for immediate evaluation. This approach enables immediate computation of arithmetic, string, and logical expressions while ensuring type correctness and predictability. The new folded expression syntax `<()>` provides an easier-to-read and more user-friendly alternative for complex expressions. This proposal lays the foundation for efficient and flexible configuration management in our markup language.
