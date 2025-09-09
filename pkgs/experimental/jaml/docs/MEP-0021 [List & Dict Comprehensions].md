# MEP-0021: List & Dict Comprehensions
**Author:** Jacob Stewart
**Status:** Draft  
**Created:** April 04, 2025  
**Target Language:** TBD


## Abstract
This proposal introduces list and dict comprehensions as a mechanism for dynamically generating lists and dictionaries within the markup language. Using f-string notation for templating and optional conditional logic, comprehensions produce either formatted strings or null, enhancing the language’s expressiveness while preserving readability.

## Motivation
Static markup languages like TOML and YAML lack concise ways to generate structured data programmatically. List and dict comprehensions enable:
- Inline creation of lists and dictionaries from iterable sources.
- Flexible templating with embedded expressions.
- Conditional output control without external tools.

This feature supports use cases like configuration generation, data mapping, and selective formatting.

## Specification

### General Syntax
Comprehensions are assigned to keys within brackets, using f-strings for templating. They produce lists or dictionaries with elements as strings or null.
- **Assignment:** `key = [comprehension]` (list) or `key = {comprehension}` (dict).
- **F-String Notation:** `f"..."` strings evaluate expressions in `{}`.
- **Output Types:** Strings (from f-strings) or null.

### 1. List Comprehension
Generates a list by iterating over a sequence.
- **Syntax:**
  ```plaintext
  key = [f"template {var}" for var in iterable]
  key = [f"template {var}" for var in iterable if condition else null]
  ```
  - `f"template {var}"`: String template with variables/expressions.
  - `for var in iterable`: Iterates over a sequence.
  - `if condition else null`: Optional; returns the f-string if true, null if false.

- **Example:**
  ```plaintext
  numbers = [1, 2, 3, 4]
  evens = [f"Even: {n}" for n in numbers if n % 2 == 0 else null]
  ```
  - **Result:** `evens = [null, "Even: 2", null, "Even: 4"]`

### 2. Dict Comprehension
Generates a dictionary with key-value pairs from an iteration.
- **Syntax:**
  ```plaintext
  key = {f"key_template": f"value_template" for var in iterable}
  key = {f"key_template": f"value_template" for var in iterable if condition else null}
  ```
  - `f"key_template"`: Key as an f-string.
  - `f"value_template"`: Value as an f-string.
  - `if condition else null`: Optional; includes the pair if true, maps to null if false.

- **Example:**
  ```plaintext
  names = ["alice", "bob"]
  ids = {f"user_{n}": f"ID-{idx}" for idx, n in enumerate(names)}
  ```
  - **Result:** `ids = {user_alice = "ID-0", user_bob = "ID-1"}`

- **With Condition:**
  ```plaintext
  scores = [85, 92, 78]
  grades = {f"student_{i}": f"Pass: {s}" for i, s in enumerate(scores) if s >= 80 else null}
  ```
  - **Result:** `grades = {student_0 = "Pass: 85", student_1 = "Pass: 92", student_2 = null}`

## Supported Features
- **Iterables:** Lists (e.g., [1, 2, 3]), ranges (e.g., range(5)), or pairs (e.g., `enumerate(...)`).
- **Expressions:** Arithmetic (e.g., `{n * 2}`), concatenation (e.g., `{prefix + n}`), or method calls (if supported).
- **Null:** Indicates no value, aligning with TOML/YAML conventions.

## Rationale
- **Conciseness:** Brackets and f-strings offer a compact, familiar syntax.
- **Control:** Conditional logic (`if ... else null`) enables selective output.
- **Fit:** Integrates with key-value and table-based markup structures.

## Backwards Compatibility
As a new feature, comprehensions do not affect existing syntax. Unsupported parsers can reject them as invalid arrays/dicts.

## Implementation Notes
- **Parsing:** Requires identifying comprehension syntax and evaluating expressions/conditions.
- **Evaluation:** Assumes variable resolution from a scope (to be defined separately).
- **Errors:** Undefined variables or invalid conditions should raise parse-time errors.

## Examples

### Combined Usage
```plaintext
[example]
prefix = "Item"
numbers = [1, 2, 3, 4]
labels = [f"{prefix}-{n}" for n in numbers if n > 2 else null]
pairs = {f"{prefix}{i}": f"Value-{v}" for i, v in enumerate(numbers)}
```
- **Result:**
  ```plaintext
  labels = [null, null, "Item-3", "Item-4"]
  pairs = {Item0 = "Value-1", Item1 = "Value-2", Item2 = "Value-3", Item3 = "Value-4"}
  ```

## Open Issues
- Should dict comprehensions skip false conditions instead of mapping to null?
- Is `null` the preferred no-value token, or should it be `nil/~`?
- Are nested comprehensions (e.g., `[f"{x}-{y}" for x in xs for y in ys]`) needed?

## Future Work
- Define variable scoping (MEP-XXXX).
- Add multi-condition support (e.g., `if x > 0 and y < 10`).
```
