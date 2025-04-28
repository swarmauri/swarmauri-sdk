# MEP-024: Render-Time Expressions
**Author:** Jacob Stewart
**Status:** Draft  
**Created:** April 04, 2025  
**Target Language:** TBD


## 1. Abstract

This proposal defines the syntax and semantics for render-time expressions in our new markup language. Render-time expressions are evaluated during the rendering phase, enabling dynamic computation that incorporates context-supplied variables. These expressions use the `{{...}}` enclosure and support logical operations, conditional logic, and list comprehensions that can leverage external context. They allow configurations to adapt dynamically based on runtime parameters.

---

## 2. Motivation

- **Dynamic Configuration:**   
  Render-time expressions allow the final configuration output to be tailored to the current environment or runtime context.

- **Flexibility:**  
  By supporting context variables (`${...}`) within render-time expressions, users can create adaptable, context-sensitive configurations.

- **Enhanced Developer Experience:**  
  Allowing dynamic computation through render-time expressions provides powerful mechanisms for constructing values, including conditionals, loops, and list comprehensions.

---

## 3. Specification

### 3.1. Syntax

- **Render-Time Expression Enclosure:**  
  Render-time expressions are enclosed in double curly braces `{{...}}`.
  ```toml
  greeting = "{{ 'Hello, ' + $user.name }}"
  ```
- **Allowed Variables:**  
  Render-time expressions can include context variables (`${...}`) as well as global (`@{...}`) and self (table-local, `%{...}`) variables if needed. However, context variables are expected to be provided externally at render time.

- **Logical Constructs:**  
  Basic conditional logic (e.g., ternary expressions) and list comprehensions are supported.
  ```toml
  status = "{{ 'Active' if true else 'Inactive' }}"
  values = "{{ [x * 2 for x in [1, 2, 3]] }}"
  ```

### 3.2. Evaluation Semantics

- **Deferred Evaluation:**  
  Render-time expressions are evaluated only when the final configuration is being generated. This permits the incorporation of external context variables.
  
- **Dynamic Resolution:**  
  Context variables (`${...}`) within render-time expressions are resolved using the provided runtime context.
  
- **Direct Use in Expressions:**  
  Render-time expressions do not require additional quotation unless necessary by the expression syntax. They are integrated directly into the configuration value.

---

## 4. Examples

### Example 1: Logical String Expression

```toml
[logic]
status: str = {{ "Active" if true else "Inactive" }}
```

*Explanation:*  
The render-time expression evaluates to `"Active"` because the condition is true.

### Example 2: Conditional Integer Expression

```toml
[logic]
number: int = {{ 100 if true else 0 }}
```

*Explanation:*  
The expression evaluates to `100`.

### Example 3: List Comprehension

```toml
[logic]
values: list = {{ [x * 2 for x in [1, 2, 3]] }}
```

*Explanation:*  
The expression produces the list `[2, 4, 6]`.

### Example 4: Nested Logical Expression with Context

```toml
[logic]
message: str = {{ "Hello, Admin" if $user.role == "admin" else "Hello, User" }}
```

*Explanation:*  
The external context must supply a value for `$user.role`. If the context provides `"admin"`, the message resolves to `"Hello, Admin"`.

### Example 5: Using Global Scope within Render-Time Expression

```toml
[user]
role: str = "admin"

[logic]
message: str = {{ "Hello, Admin" if @{user.role} == "admin" else "Hello, User" }}
```

*Explanation:*  
Here, the global reference `@{user.role}` retrieves the value `"admin"` from the `[user]` section, and the expression resolves accordingly.

---

## 5. Open Issues

- **Expression Complexity:**  
  Determining the acceptable complexity of render-time expressions, including nested conditions and comprehensions.
  
- **Error Handling:**  
  Defining clear error messages when context variables are missing or expressions are malformed.
  
- **Performance:**  
  Evaluating potentially complex expressions at render time may impact performance; strategies for caching or optimization may be required.

---

## 6. Conclusion

MEP-024 defines render-time expressions, enclosed in `{{...}}`, that allow dynamic evaluation of configuration values using context variables along with global and self-scope references. This mechanism enables configurations to be dynamically tailored based on runtime parameters, greatly enhancing flexibility and adaptability. It complements load-time expressions by handling values that must be computed only once the external context is available.

