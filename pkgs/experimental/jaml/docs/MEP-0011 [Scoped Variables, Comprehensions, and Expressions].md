# MEP-0011: Scoped Variables, Comprehensions, and Expressions
**Author:** Jacob Stewart
**Status:** Draft  
**Created:** April 04, 2025  
**Target Language:** TBD



---

## 1. Abstract

This proposal defines a unified system for handling variable scoping, dynamic string interpolation, list and dict comprehensions, and expressions in our markup language. It introduces three distinct variable scopes, two forms of string interpolation (f-string and concatenation), and  expression syntaxes. Expressions are evaluated during resolve time, with one important exception: any sub-expression that references a context variable (using the `${...}` syntax) is deferred and evaluated only during render time.

---

## 2. Motivation

- **Clear Scoping:**  
  Three separate scopes ensure that configuration authors know precisely where each value originates. Global (`@{...}`) and table-local (`%{...}`) variables are available at load time, while context (`${...}`) variables are provided at render time.

- **Dynamic vs. Static Evaluation:**  
  By performing most evaluations at load time, configurations become predictable and efficient. At the same time, deferred evaluation for context variables ensures that dynamic data can be injected at render time without reprocessing static components.

- **Expressiveness and Flexibility:**  
  F-string interpolation with inline conditionals and comprehensions (for both lists and dictionaries) enables concise and powerful configuration expressions. This flexibility allows arithmetic, string concatenation, logical operations, and ternary-like conditional expressions.

- **Performance Optimization:**  
  Precomputing static parts during load time reduces runtime overhead. Only dynamic context references are evaluated later, ensuring optimal performance during configuration rendering.

---

## 3. Specification

### 3.1. Variable Scoping

The language supports three variable scopes, each using a distinct syntax:

- **Global Scope (`@{...}`):**  
  Defined globally (e.g., in a `[globals]` section) and used as defaults.
  
  ```toml
  [globals]
  base = "/home/user"
  ```

- **Self/Local Scope (`%{...}`):**  
  Defined within the current table; these override global definitions.
  
  ```toml
  [user]
  name = "Alice"
  greeting = f"Hello, %{name}!"  # Uses the table-local 'name'
  ```

- **Context Scope (`${...}`):**  
  Provided externally at render time and not defined within the configuration file.
  
  ```toml
  [logic]
  summary = f"User: ${user.name}, Age: ${user.age}"
  ```

### 3.2. F-String Interpolation

F-strings are prefixed with `f` and allow embedding variables and expressions within `{}`:

- **Basic Usage:**

  ```toml
  [user]
  name = "John"

  [section]
  greeting = f"Hello, @{user.name}!"
  ```

- **Conditional Logic and Ternary-like Syntax:**  
  Supports inline conditions:
  
  ```toml
  [user]
  active = "Active"
  
  [section]
  status = f"{'Active' if @{user.active} else 'Inactive'}"
  ```

- **Operations Supported:**  
  Arithmetic (e.g., `{x + 1}`), string concatenation, logical operators (`and`, `or`), and combined conditions.

### 3.3. List and Dict Comprehensions

Inline comprehensions facilitate dynamic generation of lists and dictionaries:

- **List Comprehension:**

  ```toml
  numbers = [1, 2, 3, 4]
  evens = [f"Even: {n}" for n in numbers if n % 2 == 0 else null]
  ```

- **Dict Comprehension:**

  ```toml
  names = ["alice", "bob"]
  ids = {f"user_{n}": f"ID-{i}" for i, n in enumerate(names)}
  ```

- **Conditional Inclusion:**  
  The optional `if ... else null` clause allows elements to be conditionally included or mapped to `null`.

### 3.4. Expressions

Expressions allow for immediate, load-time computation of configuration values.

- **Deferred Expressions (`<{ ... }>`):**  
  Evaluations are deferred entirely during load time. They may include arithmetic, string concatenation, and logical operations.  
  **Note:** Any reference to a scoped variable (`@{...}`, `%{...}`, `${...}`) within an deferred expression is deferred and will be evaluated only during render time.

  **Example:**
  
  ```toml
  [paths]
  base = "/usr/local"
  config = <{ @{base} + '/config.toml' }>
  ```

### 3.5. Folded Expressions

Folded expressions provide a more readable alternative when constructing complex expressions. They use the `<( ... )>` syntax.

- **Folded Expression Syntax:**

  ```toml
  [server]
  address = <( @{host} + ":" + @{port} )>
  ```

- **Evaluation:**  
  All sub-expressions referencing only global (`@{...}`) and self (`%{...}`) variables are computed at load time. Any portion that references a context variable (`${...}`) is not resolved until render time.
  
- **Example with Mixed Static and Dynamic Data:**

  ```toml
  [api]
  # 'host' and 'port' are loaded immediately while 'auth_token' is deferred.
  endpoint = <( "http://" + @{server.host} + ":" + @{server.port} + "/api?token=" + ${auth_token} )>
  ```

  At load time, the static parts (using `@{...}`) are resolved. At render time, when the context supplies `auth_token`, the full expression is finalized.

### 3.6. Supported Operations and Constructs

- **Arithmetic:**  
  Operations such as `+`, `-`, `*`, `/` (e.g., `<{ @{default} * 2 }>`).

- **String Concatenation:**  
  Performed using `+` within expressions or f-string interpolation.

- **Logical Operators:**  
  Including `and` and `or`, enabling complex conditionals.

- **Ternary-like Conditional Syntax:**  
  Supports inline conditions, for example:

  ```toml
  check = f"{'Valid' if {value} == 'expected' else 'Invalid'}"
  ```

- **Context vs. Load-Time Evaluation:**  
  Folded expressions (`<( ... )>`) are processed at load time; however, any component referencing a context variable (`${...}`) is deferred until render time.

### 3.7. Load Time vs. Render Time

- **Load Time:**  
  Folded expressions (`<( ... )>`) are evaluated during the configuration file’s load phase. All references to global (`@{...}`) and self (`%{...}`) variables are computed then.

- **Render Time:**  
  Deferred expressions (`<{ ... }>`) are evaluated during the configuration file's render phase. Additionally, any portion of an expression that references a context variable (`${...}`) is deferred until render time. During rendering, the external context is used to resolve these variables and complete the final value.

### 3.8. Error Handling

- **Undefined Variables:**  
  References to undefined global or table-local variables within folded expressions must produce clear, descriptive parse-time errors.

- **Disallowed Context Usage:**  
  Folded expressions should not improperly embed context variables. If found, only the context parts are deferred while static parts are computed; any misuse should generate an error.

- **Syntax Errors:**  
  Any syntax errors (e.g., unmatched brackets, incorrect conditional syntax) should trigger informative error messages indicating the nature and location of the error.

---

## 4. Examples

### Example 1: Basic Scoping and Interpolation

```toml
[globals]
base = "/home/user"

[user]
name = "Alice"
greeting_local = f"User config: %{base}/config.toml"
greeting_global = f"Default config: @{base}/config.toml"
```

*Expected Output:*

- `greeting_local` → `"User config: /home/user/config.toml"`
- `greeting_global` → `"Default config: /home/user/config.toml"`

### Example 2: List and Dict Comprehensions

```toml
[globals]
prefix = "item"
items = ["apple", "banana", "cherry"]

[server]
dict_config = {f"@{prefix}_{item}": {item} for item in @{items} if item != "banana" else null}
list_config = [f"@{prefix}_{item}" for item in @{items} if item != "banana" else null]
```

*Expected Result:*

- `dict_config` → `{"item_apple": "apple", "item_cherry": "cherry"}`
- `list_config` → `["item_apple", "item_cherry"]`

---


### Example 4: Folded Expressions with `<( ... )>`

```toml
[server]
host = "prodserver"
port = 8080

[api]
# 'host' and 'port' are evaluated at load time while 'auth_token' is deferred.
endpoint = <( "http://" + @{server.host} + ":" + @{server.port} + "/api?token=" + ${auth_token} )>
```

*Load-Time Evaluation:*

- `@{server.host}` resolves to `"prodserver"`.
- `@{server.port}` resolves to `8080`.

*Render-Time Evaluation:*

- When `auth_token` is provided (e.g., `"ABC123"`), the final endpoint becomes:  
  `"http://prodserver:8080/api?token=ABC123"`

---

### Example 5: Conditional Logic and Mixed Evaluation

```toml
[logic]
is_production = false

[settings]
# Using a conditional expression with mixed evaluation.
strategy = <( "ProductionStrategy" if @{logic.is_production} else ${dynamic_strategy} )>
```

*Load-Time Evaluation:*

- `@{logic.is_production}` resolves to `false`, so the conditional defers to `${dynamic_strategy}`.

*Render-Time Evaluation:*

- With `dynamic_strategy` provided (e.g., `"Development"`), the final value becomes:  
  `"Development"`

---

## 5. Implementation Considerations

- **Parsing and AST Construction:**  
  The parser must correctly identify and differentiate among the various scoped variable syntaxes (`@{}`, `%{}`, `${}`) as well as the two types of expression enclosures (`<{ ... }>` for immediate expressions and `<( ... )>` for folded expressions).

- **Evaluation Phases:**  
  A clear separation must be maintained between load-time and render-time evaluation. Load-time evaluation will compute all static components, while render-time evaluation will resolve deferred context variables.

- **Operator Precedence and Nesting:**  
  The language should define and document operator precedence rules to ensure unambiguous evaluation of arithmetic, concatenation, and logical operations. Limits on expression nesting may be considered for performance reasons.

- **Tooling and Error Reporting:**  
  Editor plugins and debugging tools need updates to support the new syntax, providing accurate highlighting and informative error messages.

