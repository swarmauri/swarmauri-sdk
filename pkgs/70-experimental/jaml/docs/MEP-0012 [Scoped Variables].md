
# MEP-012: Scoped Variables
**Author:** Jacob Stewart
**Status:** Draft  
**Created:** April 04, 2025  
**Target Language:** TBD


## 1. Abstract

This proposal defines the support for scoped variables in our markup language. The language will support three distinct scopes:

- **Global Scope:** Variables defined at a global level, referenced using `@{...}`.
- **Self (Table-Local) Scope:** Variables defined within the same table, referenced using `%{...}`.
- **Context Scope:** Variables provided externally at render time, referenced using `${...}`.

We further support two styles for using these scoped variables in configuration values:
- **Dynamic Style:** Using f-string–like syntax (e.g., `f"${base}/config.toml"`) where placeholders are replaced by their resolved values.
- **Concatenation Style:** Using an explicit concatenation operator (e.g., `${base} + '/config.toml'`) that produces the same resolved output.

This proposal does not cover arbitrary expression evaluation but focuses solely on the resolution of scoped variables in static (load-time) and dynamic (render-time) contexts.

---

## 2. Motivation

- **Clarity and Predictability:**  
  Providing three distinct scopes—global, self, and context—ensures that configuration authors can clearly designate where a variable’s value comes from, leading to predictable resolution.

- **Separation of Concerns:**  
  By distinguishing between static values (global and self scopes) and dynamic values (context scope), we ensure that configuration files can be both self-contained and dynamically adaptable based on external context.

- **Consistency in Styles:**  
  Supporting both f-string–like (dynamic) and concatenation (static) syntaxes allows flexibility in how values are constructed. Both styles should yield identical results, ensuring that users can choose the style that best fits their workflow without inconsistency.

---

## 3. Specification

### 3.1. Supported Scopes and Their Syntax

- **Global Scope (`@{...}`):**  
  Variables defined globally or in a designated global section. For example, if a global value is defined as:
  ```toml
  [globals]
  base = "/home/user"
  ```
  Then `@{base}` will reference `"/home/user"`.

- **Self (Table-Local) Scope (`%{...}`):**  
  Variables defined within the current table override any global definitions. For instance:
  ```toml
  [user]
  name = "LocalName"
  greeting = f"Hello, %{name}"  # Should resolve using a local definition if available
  ```
  Here, if the table contains a local `name`, it takes precedence over any global `name`.

- **Context Scope (`${...}`):**  
  Variables provided externally (via context during rendering). These are not defined within the file but injected at render time. For example:
  ```toml
  [logic]
  greeting = f"Hello, ${user.name}"
  ```
  The value of `${user.name}` will be supplied by the render context.

### 3.2. Styles for Referencing Variables

Our language will support two syntactic styles for including scoped variables in configuration values:

1. **Dynamic (F-string) Style:**  
   Variables can be embedded within a string literal prefixed with `f`. For example:
   ```toml
   [paths]
   config = f"${base}/config.toml"
   log = f"${base}/logs/app.log"
   ```
   In this style, placeholders are automatically replaced with their resolved values.

2. **Concatenation Style:**  
   Variables can be combined with string literals using a concatenation operator (e.g., `+`), for example:
   ```toml
   [paths]
   config = ${base} + '/config.toml'
   log = ${base} + '/logs/app.log'
   ```
   Both styles produce the same final result.

### 3.3. Resolution Order

- **Context Variables:**  
  Variables referenced via `${...}` are only available at render time and are resolved using the supplied context.
- **Default Behavior:**  
  If a scoped variable is used without additional dynamic logic, it is evaluated immediately (i.e., load-time) for global and self scopes. Context variables require rendering.

---

## 4. Rationale

- **Explicit Scoping:**  
  The use of distinct notations for each scope (`@{...}`, `%{...}`, `${...}`) provides clarity. Authors immediately understand whether a value is being drawn from a global default, a table-local override, or an external context.

- **Flexible Construction:**  
  By supporting both dynamic (f-string) and concatenation styles, the language accommodates various coding styles without sacrificing consistency. Both methods produce identical outcomes.

- **Separation of Static and Dynamic Data:**  
  Global and self-scoped variables are evaluated at load time by default, while context-scoped variables are deferred until render time. This separation ensures that configurations can be both robust and adaptable.

---

## 5. Examples

### Example: Global and Self Scope

```toml
[globals]
base = "/home/user"

[user]
name = "Alice"
greeting = f"Hello, %{name}!"  # Resolves to "Hello, Alice!"
```

### Example: Global vs. Context Scope

```toml
[logic]
summary = f"User: ${user.name}, Age: ${user.age}"
```
Here, `${user.name}` and `${user.age}` are provided by the render context.

### Example: Mixed Static Styles

```toml
[paths]
base = "/home/user"
config_fstring = f"${base}/config.toml"
config_concat = ${base} + '/config.toml'
```
Both `config_fstring` and `config_concat` resolve to `/home/user/config.toml`.

### Example: List and Dict Comprehensions with Scoped Variables

```toml
[globals]
prefix = "item"
items = ["apple", "banana", "cherry"]

[server]
dict_config = {f"@{prefix}_{item}":{item} for item in @{items} if item != "banana"}
list_config = [f"@{prefix}_{item}" for item in @{items} if item != "banana"]
```
In this case:
- `prefix` is from the global scope.
- `items` is a list in the global scope.
- The comprehension iterates over `items` and generates a set of formatted strings, excluding `"banana"`.

Result:
```plaintext
dict_config = {"item_apple": "apple", "item_cherry": "cherry"}
list_config = ["item_apple", "item_cherry"]
```

### Example: `%{base}` vs `@{base}` Comparison

```toml
# Global scope
[globals]
base = "/home/user"

# Self (Table-Local) scope
[user]
base = "/home/user/local"

# Using the variable in both contexts
greeting_local = f"User config directory (local): %{base}/config.toml"
greeting_global = f"User config directory (global): @{base}/config.toml"
```

### Expected Output:
- **greeting_local:** Resolves to the table-local `base` (`/home/user/local`) because `%{base}` refers to the local scope.
  - Result: `"User config directory (local): /home/user/local/config.toml"`
  
- **greeting_global:** Resolves to the global `base` (`/home/user`) because `@{base}` explicitly refers to the global scope.
  - Result: `"User config directory (global): /home/user/config.toml"`

---

## 6. Implementation Considerations

- **Parsing:**  
  The parser must resolve `%{...}` by first looking within the current table, then fallback to `@{...}` if not found.
  
- **Dynamic Resolution:**  
  `${...}` placeholders will be replaced during the rendering phase based on the provided context.
  
- **Consistency:**  
  Both dynamic styles (f-string and concatenation) should be handled identically in the AST and final output.

- **Comprehensions and Variables:**  
  List and dict comprehensions should support scoped variables seamlessly, with the same resolution rules as string interpolation, ensuring consistency in how scoped variables are used in dynamic and static contexts.

---

## 7. Conclusion

MEP-012 outlines the support for scoped variables in our markup language. By providing three distinct scopes—global (`@{...}`), self/local (`%{...}`), and context (`${...}`)—and supporting both dynamic and static reference styles (f-string and concatenation), we achieve a system that is clear, flexible, and predictable. The proposal also extends to list and dict comprehensions, integrating scoped variables seamlessly into these constructs. This proposal lays a solid foundation for managing configuration variables, ensuring that values are resolved in the intended order and context.
