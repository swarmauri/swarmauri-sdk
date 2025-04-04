# MEP-0022: Expressions

## 1. Abstract

This proposal defines the syntax and semantics for expressions in our new markup language using a unified system that supports immediate (load-time) evaluation. In MEP-0022, expressions are enclosed in `{~ ... ~}` and allow for computations—including arithmetic, logical operations, string concatenation, conditional expressions, and list comprehensions—to be evaluated as soon as the configuration file is loaded. The evaluated result is inserted into the final configuration without extra quotation marks, and its type is either explicitly declared or inferred by the parser.

> **Note:** MEP-0022 covers the load-time expression mechanism using `{~ ... ~}`. Dynamic evaluation and partial deferral of expressions will be handled later in MEP-0025 with the introduction of the `{^ ... ^}` notation.

---

## 2. Motivation

- **Immediate Computation:**  
  Evaluating expressions at load time ensures that computed values are fixed and available immediately, reducing runtime overhead.

- **Predictable and Type-Safe Configuration:**  
  By performing load-time evaluation and type inference, users can design configurations that are both predictable and type-correct. The evaluated result is inserted into the configuration as a plain value (without extra quotes) according to its inferred or declared type.

- **Separation of Concerns:**  
  Load-time expressions are restricted to variables defined within the file (global and table-local scopes). This clear separation prevents accidental reliance on external (render-time) context variables in this phase.

- **Unified Expression System:**  
  Using a single enclosure—`{~ ... ~}`—for immediate evaluation simplifies the language’s syntax. Authors write expressions in one familiar format, while support for dynamic deferral and expression folding (via `{^ ... ^}`) is deferred to a later proposal (MEP-0025).

---

## 3. Specification

### 3.1. Syntax: `{~ ... ~}`

- **Expression Enclosure:**  
  Load-time expressions are wrapped in `{~ ... ~}`.
  ```toml
  key = {~ expression ~}
  ```
  For example:
  ```toml
  config = {~ @{base} + '/config.toml' ~}
  ```

### 3.2. Type Inference and Operations

- **Type Inference:**  
  The type of an expression’s result is either declared on the key or inferred by the parser.  
  - When a string is expected, the result is inserted as a plain string (without extra quotes).
  - When a numeric or boolean type is expected, the expression result is converted accordingly.

- **Allowed Operations:**  
  Expressions support:
  - **Arithmetic:** `+`, `-`, `*`, `/`, etc.
  - **String Concatenation:** For example, `{~ @{base} + '/config.toml' ~}`.
  - **Conditional Expressions:** Ternary-like syntax (e.g., `{~ "DEBUG" if false else "INFO" ~}`).
  - **List Comprehensions:** For creating lists from static arrays.
  - **Logical Operators:** Such as `and`, `or`, etc.

### 3.3. Scope Restrictions

- **Allowed Scopes:**  
  - **Global Scope (`@{...}`):**  
    Variables defined in a global section or as defaults.
  - **Self (Table-Local) Scope (`%{...}`):**  
    Variables defined within the same table.
  
- **Disallowed Scopes:**  
  - **Context Scope (`${...}`):**  
    External context variables are not allowed in `{~ ... ~}` expressions. Any attempt to use a context variable in this phase must trigger a validation error.

### 3.4. Evaluation Semantics

- **Immediate Resolution:**  
  Expressions enclosed in `{~ ... ~}` are evaluated immediately when the configuration file is loaded. The resulting value replaces the original expression.

- **Insertion of Results:**  
  Regardless of whether the result is a string, number, boolean, or list, it is inserted directly into the configuration without additional quotation marks.

- **Static Behavior:**  
  All computations in `{~ ... ~}` are static and are not re-evaluated at runtime.

### 3.5. Error Handling

- If an expression refers to an undefined variable or includes a disallowed context variable (`${...}`), the parser must raise a descriptive error.
- Syntax errors within the expression should produce clear error messages, indicating the error’s location and nature.

---

## 4. Examples

### Example 1: Simple String Concatenation

```toml
[paths]
base = "/usr/local"
config = {~ @{base} + '/config.toml' ~}
```

*Explanation:*  
The global variable `@{base}` is concatenated with the literal `'/config.toml'` to yield the string `/usr/local/config.toml`.

### Example 2: Arithmetic Computation

```toml
[settings]
default_retries = 3
max_retries = {~ @{default_retries} * 2 ~}
```

*Explanation:*  
Multiplies `3` by `2` to yield the integer `6`.

### Example 3: Conditional Expression

```toml
[system]
debug_mode = false
log_level: str = {~ "DEBUG" if false else "INFO" ~}
```

*Explanation:*  
Since the condition is false, the expression evaluates to `"INFO"` and inserts it as a plain string.

### Example 4: List Comprehension

```toml
[data]
values = {~ [x * 2 for x in [1, 2, 3]] ~}
```

*Explanation:*  
The expression produces the list `[2, 4, 6]`.

---

## 5. Open Issues

- **Complexity Limits:**  
  Define acceptable complexity for load-time expressions, especially regarding nesting and operator precedence.
  
- **Operator Precedence:**  
  Establish precise rules to avoid ambiguity in expressions involving multiple operators.
  
- **Tooling and Debugging:**  
  Ensure that editor plugins and error messages correctly reflect the semantics of `{~ ... ~}` expressions.

---

## 6. Conclusion

MEP-0022 introduces a unified expression system for our markup language using the `{~ ... ~}` syntax for load-time evaluation. This approach enables immediate computation of arithmetic, string, and logical expressions while ensuring type correctness and predictability.

