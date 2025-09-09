# MEP-023: Load-Time Expressions
**Author:** Jacob Stewart
**Status:** Draft  
**Created:** April 04, 2025  
**Target Language:** TBD


## 1. Abstract

This proposal defines the syntax and semantics for load-time expressions in our new markup language. Load-time expressions enable computations such as arithmetic, logical operations, string concatenation, and simple list comprehensions to be evaluated as soon as the configuration file is loaded. These expressions are enclosed in a dedicated syntax (`~(...)`), and—crucially—they are inserted into the final configuration without extra quotation marks even if their result is a string. The resulting value is typed according to a provided type annotation or inferred from the expression, ensuring that the configuration remains both dynamic and type-correct at load time.

---

## 2. Motivation

- **Immediate Computation:**  
  Evaluating expressions at load time ensures that computed values are fixed and readily available, reducing runtime overhead.

- **Predictable Configuration:**  
  By resolving expressions immediately and preserving their types, users can design configurations that are both flexible and predictable.

- **Type Inference and Safety:**  
  When a load-time expression produces a string, integer, boolean, or other supported type, the system automatically converts the result to the declared or inferred type—eliminating the need for manual quoting.

- **Separation from Render-Time:**  
  Load-time expressions are strictly limited to variables defined within the file (global and table-local), ensuring that no external context (`${...}`) is required. This separation keeps static configuration evaluation isolated from dynamic, runtime-driven changes.

---

## 3. Specification

### 3.1. Syntax

- **Expression Enclosure:**  
  Load-time expressions are wrapped in `~(...)`. No surrounding quotes are added to the evaluated result.
  ```toml
  key = ~( expression )
  ```
  For example:
  ```toml
  config = ~( @{base} + '/config.toml' )
  ```

- **Type Inference and Annotations:**  
  The type of the expression’s result is determined by either an explicit type annotation on the key or inferred by the parser.  
  - If a string is expected, the evaluated result is inserted as a plain string (without extra quotes).
  - If an integer, float, or boolean is expected, the result is converted accordingly.

### 3.2. Scope Restrictions

#### 3.2.1. Allowed Scopes

- **Global Scope (`@{...}`):**  
  Variables defined in a global section of the configuration file or as defaults.  
- **Self (Table-Local) Scope:**  
  Variables defined within the same table. These are referenced either using the same `@{...}` notation or an alternative (e.g., `%{...}`) if needed, but for load-time expressions, global and self variables are allowed.

#### 3.2.2. Disallowed Scopes

- **Context Scope (`${...}`):**  
  Variables provided externally at render time are not permitted in load-time expressions. Any attempt to use context scope variables within a `~(...)` expression must result in a validation error.

### 3.3. Allowed Operations

Load-time expressions support:
- **Arithmetic operations:** `+`, `-`, `*`, `/`, etc.
- **String concatenation:** e.g., `@{base} + '/config.toml'`
- **Conditional expressions:** Using a ternary-like syntax.
- **List comprehensions:** For creating lists from static arrays.
- **Logical operators:** `and`, `or`, etc.

### 3.4. Evaluation Semantics

- **Immediate Resolution:**  
  Load-time expressions are evaluated immediately during the configuration loading phase.

- **Insertion of Results:**  
  The computed result replaces the original expression in the configuration. For example, if an expression yields a string value, it is inserted as a plain string without additional quotation marks.

- **Default Static Behavior:**  
  Values not wrapped in a `~(...)` are treated as literal and are not evaluated.

### 3.5. Error Handling

- If a load-time expression refers to an undefined variable or attempts to use a context scope variable (`${...}`), the parser should raise a descriptive error.
- Syntax errors within the expression should produce clear error messages indicating the location and nature of the error.

---

## 4. Examples

### Example 1: Simple String Concatenation

```toml
[paths]
base = "/usr/local"
config = ~( @{base} + '/config.toml' )
```

*Explanation:*  
The global variable `@{base}` is concatenated with the literal `'/config.toml'` to produce `/usr/local/config.toml`. The result is inserted as a plain string.

---

### Example 2: Arithmetic Computation

```toml
[settings]
default_retries = 3
max_retries = ~( @{default_retries} * 2 )
```

*Explanation:*  
The expression multiplies the load-time variable `@{default_retries}` by 2, producing the integer `6`. The result is inserted as an integer.

---

### Example 3: Conditional Expression

```toml
[system]
debug_mode = false
log_level: str = ~( "DEBUG" if false else "INFO" )
```

*Explanation:*  
The condition evaluates to `"INFO"`, so `log_level` is set to `INFO` as a plain string.

---

## 5. Open Issues

- **Expression Complexity Limits:**  
  Establish acceptable boundaries for the complexity of load-time expressions.
  
- **Operator Precedence:**  
  Define precise operator precedence rules to avoid ambiguity in complex expressions.
  
- **Error Reporting:**  
  Further refine error messages for missing variables, invalid operations, or misuse of context scope within load-time expressions.

---

## 6. Conclusion

MEP-023 specifies the support for load-time expressions in our new markup language using the `~(...)` enclosure. These expressions are evaluated immediately during file loading, and the resulting value is inserted into the configuration without additional quotation marks—even if the result is a string. By restricting load-time expressions to global and self (table-local) variables and disallowing context variables, this approach ensures predictable and type-correct computation of configuration values. This proposal establishes a robust foundation for static evaluation, with future enhancements planned for further operations and error handling.

