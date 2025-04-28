
# MEP-0022: F-String Interpolation
**Author:** Jacob Stewart
**Status:** Draft  
**Created:** April 04, 2025  
**Target Language:** TBD


## Abstract
This proposal introduces f-string interpolation with embedded conditional logic using `{}` brackets as a mechanism for dynamic string generation within the markup language. F-strings provide a readable way to embed expressions and variables, while conditional logic within `{}` allows for inline decision-making, producing string values or null. This enhances the language’s templating capabilities without requiring external processing.

## Motivation
Static markup languages often lack flexible string templating. F-string interpolation with embedded conditional logic enables:
- Dynamic string construction with variables and expressions.
- Inline conditional logic for concise, context-aware strings.
- Seamless integration with key-value assignments and prior MEPs (e.g., MEP-0021).

Use cases include configuration templating, conditional labels, and runtime string customization.

## Specification

### General Syntax
F-strings are prefixed with `f` and use `{}` to embed expressions or variables. Conditional logic is embedded within `{}` using an `if-else` structure, producing a string or null.
- **Assignment:** `key = f"template {expression}"`
- **Embedded Conditional:** `{value if condition else alternative}`
- **Output:** A single string with resolved expressions.

### F-String Interpolation
Variables or expressions within `{}` are evaluated and inserted into the string.
- **Syntax:**
  ```plaintext
  key = f"prefix {var} suffix"
  ```
  - `var`: A variable or expression (e.g., `{a}`, `{b[0]}`, `{x + 1}`).

- **Example:**
  ```plaintext
  a = "world"
  greeting = f"Hello, {a}!"
  ```
  - **Result:** `greeting = "Hello, world!"`

### Embedded Conditional Logic
Conditions within `{}` use a ternary-like syntax to choose between two values.
- **Syntax:**
  ```plaintext
  key = f"prefix {value if condition else alternative} suffix"
  ```
  - `value`: String or expression if the condition is true.
  - `condition`: Logical expression (e.g., `{a} == "banace"`).
  - `alternative`: String or null if the condition is false.

- **Example:**
  ```plaintext
  b = ["banace", "other"]
  a = {b[0]}
  test = f"Result: {'dfdf' if {a} == 'banace' else 'nope'}"
  ```
  - **Result:** `test = "Result: dfdf"`

### With Multiple Conditions:
  ```plaintext
  a = "banace"
  test = f"Status: {'match' if {a} == 'banace' and {a} != '' else 'no_match'}"
  ```
  - **Result:** `test = "Status: match"`

### With Null:
  ```plaintext
  b = ["xyz", "other"]
  a = {b[0]}
  test = f"Result: {'dfdf' if {a} == 'banace' else null}"
  ```
  - **Result:** `test = "Result: null"`

## Supported Features
- **Expressions:** Arithmetic (e.g., `{x + 1}`), comparisons (e.g., `{a} == 'banace'`), or concatenation (e.g., `'pre' + {a}`).
- **Variables:** Resolved from a scope (e.g., `{a}`, `{b[0]}`), to be defined in a future MEP.
- **Null:** Indicates no value, consistent with MEP-0021.

## Rationale
- **Readability:** F-strings with `{}` are intuitive and widely recognized (e.g., from Python).
- **Power:** Embedded `if-else` logic reduces verbosity compared to external conditionals.
- **Consistency:** Aligns with MEP-0021’s f-string and null usage.

## Backwards Compatibility
As a new feature, f-strings and embedded conditionals do not affect existing syntax. Parsers without support can treat them as plain strings, though they won’t evaluate correctly.

## Implementation Notes
- **Parsing:** Requires recognizing `f` prefix and evaluating `{}` contents, including conditional logic.
- **Evaluation:** Variables must be resolved from a scope (future MEP).
- **Errors:** Undefined variables or invalid conditions raise parse-time errors.

## Examples

### Basic Interpolation
```plaintext
name = "alice"
message = f"User: {name}"
```
- **Result:** `message = "User: alice"`

### Conditional Logic
```plaintext
b = ["banace", "other"]
a = {b[0]}
test = f"Outcome: {'success' if {a} == 'banace' else 'failure'}"
```
- **Result:** `test = "Outcome: success"`

### Complex Condition
```plaintext
value = "banace"
check = f"{'Valid' if {value} == 'banace' and {value} != '' else 'Invalid'} input"
```
- **Result:** `check = "Valid input"`

## Open Issues
- Should alternatives to null (e.g., nil, empty string) be allowed?
- Are nested conditionals (e.g., `{x if c1 else y if c2 else z}`) needed?
- Should string literals inside `{}` require quotes (e.g., `'dfdf'` vs. `dfdf`)?

## Future Work
- Define variable scoping (MEP-XXXX).
- Extend with filters or functions (e.g., `{a.upper()}`).
```
