# MEP-001: Keywords, Operators, and Patterns
**Author:** Jacob Stewart
**Status:** Draft  
**Created:** April 04, 2025  
**Target Language:** TBD

## 1. Abstract

This proposal specifies the reserved keywords, operators, punctuation, and common expression patterns for our markup language. It establishes clear rules for keyword usage, operator precedence, and syntax validation. Key updates include support for pipeline operations, enhanced string literal handling (with various quoting forms), conditional (ternary) expressions, membership and merge operators, and reserved functions like `File()` and `Git()`.

---

## 2. Motivation

- **Consistency and Clarity:**  
  Defining keywords, operators, and punctuation prevents naming conflicts and ambiguous syntax, ensuring consistent parsing and predictable expression evaluation.

- **Avoiding Conflicts:**  
  Reserving critical language constructs (keywords, functions, and punctuation) stops users from unintentionally overwriting core elements, which could lead to errors.

- **Enhanced Error Handling:**  
  A well-defined syntax with reserved elements enables robust parsing and clear error messages, aiding debugging and future tooling integrations.

---

## 3. Specification

### 3.1. Reserved Keywords

The following identifiers are reserved and **cannot** be used as names for keys, tables, variables, or user-defined types:

- **Logical and Boolean Keywords:**  
  - `true`, `false`, `null`, `is`, `not`, `and`, `or`
- **Control Flow Keywords:**  
  - `if`, **`elif`**, `else`, `for`, `in`, `enumerate`
- **Directive Keywords:**  
  - `include`
- **Reserved Functions:** 
  - `File()`, `Git()`

#### Keyword Usage
- Keywords must appear in the appropriate context (for example, `if` and `elif` in conditional expressions).
- Using any of these reserved words as identifiers will result in a syntax error.

---

### 3.2. Reserved Punctuations and Brackets

#### 3.2.1. Reserved Punctuation Marks

The following punctuation marks are reserved and **must not** be used as part of key names, variable names, or unquoted strings:

- **Colon (`:`)** – For type annotations and key-value separation.
- **Dot (`.`)** – For namespace access.
- **Comma (`,`)** – As a separator in lists and inline tables.
- **Equals Sign (`=`)** – For assignment in key-value pairs.
- **Arrow (`->`)** – Reserved for potential functional expressions.
- **Semicolon (`;`)** – Reserved for future extensions.
- **Tilde (`~`)** – Used for load-time expressions.
- **At Symbol (`@`)** – Reserved for future use.
- **Dollar Sign (`$`)** – Reserved for future use.
- **Percent Sign (`%`)** – Reserved for future use.
- **Less Than (`<`)** and **Greater Than (`>`)** – Used in comparisons.
- **Exclamation Mark (`!`)** – For negation.
- **Asterisk (`*`)** – For multiplication and comprehensions.
- **Caret (`^`)** – Reserved for future use.
- **Ampersand (`&`)** – Reserved for future use.
- **Pipe (`|`)** – Reserved for future use.
- **Forward Slash (`/`)** – In path strings and division.
- **Backslash (`\`)** – As an escape character in strings.

#### 3.2.2. Reserved Bracket Combinations

All bracket types are reserved to ensure unambiguous syntax:

- **Round Brackets (`()`)** – For grouping expressions and function calls.
- **Square Brackets (`[]`)** – For defining lists and accessing array elements.
- **Curly Braces (`{}`)** – For inline tables and dictionary-like structures.
- **Angle Brackets (`<>`)** – Reserved for future use.
- **Nested Bracket Combinations:**  
  - Examples: `[{}]`, `{{}}`, `<(>)`, `([)])`, `<{>}`  
    These are reserved to avoid ambiguity.

#### Punctuation Usage
- Any use of reserved punctuation or bracket combinations outside their valid syntax context (or within unquoted identifiers) will raise a syntax error.

---

### 3.3. String Quotation Rules

Our markup language supports multiple string delimiters to handle both literal and interpolated content:

- **Single Quotes (`'...'`):**  
  Basic strings with no interpolation.
  ```toml
  greeting = 'Hello, World!'
  ```
- **Double Quotes (`"..."`):**  
  Strings that support interpolation.
  ```toml
  welcome = "Hello, ${user.name}!"
  ```
- **Triple Single Quotes (`'''...'''`):**  
  Multi-line literal strings.
  ```toml
  message = '''This is a
  multi-line string.'''
  ```
- **Triple Double Quotes (`"""..."""`):**  
  Multi-line strings with interpolation.
  ```toml
  announcement = """Version: ${version}
  Released Today!"""
  ```
- **Backticks (`` `...` ``):**  
  Raw strings where no escaping is performed.
  ```toml
  path = `C:\Users\Name`
  ```

#### String Quotation Guidelines
- Mixing different string delimiters in one literal is not allowed.
- Unescaped or mismatched quotes within a string will trigger a syntax error.

---

### 3.4. Supported Operators

#### 3.4.1. Arithmetic Operators
- **Addition:** `+`
- **Subtraction:** `-`
- **Multiplication:** `*`
- **Division:** `/`
- **Modulo:** `%`
- **Exponentiation:** `**`

#### 3.4.2. Comparison Operators
- **Equal to:** `==`
- **Not equal to:** `!=`
- **Greater than:** `>`
- **Less than:** `<`
- **Greater than or equal to:** `>=`
- **Less than or equal to:** `<=`
- **Identity:** `is`

#### 3.4.3. Logical Operators
- **Logical AND:** `and`
- **Logical OR:** `or`
- **Logical NOT:** `not`

#### 3.4.4. Conditional (Ternary) Operator
- Allows inline conditional expressions:
  ```toml
  status = ~( "Active" if "Active" else "Inactive" )
  ```

#### 3.4.5. Membership Operators
- **Membership:** `in`
- **Non-membership:** `not in`

---

### 3.5. Error Handling

- **Syntax Errors:**  
  - Reserved keywords or punctuation misused as identifiers will result in a syntax error.
  - Incorrect use of reserved functions (`File()`, `Git()`) or keywords (such as using `if` or `elif` as variable names) is not permitted.
- **Bracket Errors:**  
  - Unmatched, incorrectly nested, or ambiguous bracket combinations will trigger an error.
- **Invalid Punctuation:**  
  - Reserved punctuation appearing outside of its valid syntax (or within unquoted keys/identifiers) will raise a clear error.
- **String Delimiter Errors:**  
  - Mismatched or unescaped quotes in strings will cause a syntax error.

---

## 4. Examples

### Example 1: Valid Use of Reserved Keywords and Conditional Expression

```toml
[config]
is_active = true
status = ~( "Running" if "Active" else "Stopped" )
```

### Example 2: Reserved Function Usage

```toml
[dependencies]
source = File("requirements.txt")
version = Git("https://repo.git", tag="v1.0")
```

### Example 3: Membership

```toml
[settings]
allowed = ~( "admin" in ["admin"] )
```

### Example 4: Invalid Use of Reserved Punctuation

```toml
[invalid]
some:key = "value"  # Syntax error: Colon used incorrectly in key name
```

### Example 5: Invalid Use of Reserved Keyword

```toml
[config]
if = "condition"  # Syntax error: 'if' is a reserved keyword
```

---

## 5. Open Issues

- **Future Reserved Symbols:**  
  Evaluate whether symbols such as `^`, `&`, or certain bracket combinations should have dedicated functionality.
- **Keyword Expansion:**  
  Consider if additional keywords (e.g., `match`) need to be reserved as language features evolve.
- **Operator Overloading:**  
  Determine if custom operator definitions for user-defined types are desirable.
- **Pipeline Syntax Complexity:**  
  Investigate supporting more complex chaining scenarios or error reporting for pipelines.

---

## 6. Conclusion

MEP-001 clearly defines the reserved keywords, operators, punctuation, and syntax patterns for our markup language. By reserving key elements such as control flow keywords (including `elif`), special functions (`File()`, `Git()`), and specific punctuation and bracket combinations, the specification prevents naming conflicts and ambiguity. Enhanced support for pipelines, conditional expressions, membership tests, and string handling ensures that the language remains both expressive and robust. Feedback is encouraged as we continue refining these rules and explore future language enhancements.
