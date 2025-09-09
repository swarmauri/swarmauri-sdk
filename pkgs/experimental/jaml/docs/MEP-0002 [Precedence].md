# MEP-002: Precedence
**Author:** Jacob Stewart
**Status:** Draft  
**Created:** April 04, 2025  
**Target Language:** TBD


## 1. Abstract

This proposal specifies the precedence rules used by the lexer to recognize and resolve tokens in our markup language. Tokens are matched in a descending-order precedence list, meaning higher-priority (more “tightly bound”) tokens are matched before lower-priority ones. This approach ensures that complex constructs like strings and scoped variables are correctly recognized before simpler tokens like operators or identifiers.

---

## 2. Motivation

- **Consistent Parsing:**  
  By defining a clear precedence order, the lexer can efficiently and accurately tokenize the input, avoiding ambiguous interpretations.

- **Predictability:**  
  Users can anticipate how complex expressions will be parsed, especially when strings, variable references, or reserved functions are involved.

- **Error Handling:**  
  A well-defined precedence order allows the lexer to catch syntax errors early, as mismatches can be reliably detected when no valid higher-priority token is found.

---

## 3. Specification

### 3.1. Precedence List (Descending Order)

1. **STRING**  
2. **SCOPED_VAR**  
3. **COMMENT**  
4. **FLOAT**  
5. **INTEGER**  
6. **BOOLEAN**  
7. **NULL**  
8. **RESERVED_FUNC**  
9. **KEYWORD**  
10. **TABLE_ARRAY**  
11. **TABLE_SECTION**  
12. **INLINE_TABLE**  
13. **ARRAY**  
14. **IDENTIFIER**  
15. **OPERATOR**  
16. **PUNCTUATION**  
17. **WHITESPACE**  
18. **MISMATCH**

### 3.2. Precedence Rules

The following is a descending-order precedence list that reflects how tokens are resolved by the lexer. Higher-priority tokens (more “tightly bound”) are matched before lower-priority ones:

1. **STRING**  
   - All string literal forms—including f-strings, multi-line strings, and raw strings.  
   - Strings may be enclosed in:
     - Single quotes (`'...'`)
     - Double quotes (`"..."`)
     - Triple single quotes (`'''...'''`)
     - Triple double quotes (`"""..."""`)
     - Backticks (`` `...` ``) for raw strings.  
   - f-strings may include interpolations using `${}`, `@{}`, or `%{}`.  
   - Examples:
     ```toml
     greeting = "Hello, World!"
     path = f"${base}/docs"
     raw = `C:\Path\to\File`
     ```

2. **SCOPED_VAR**  
   - Scoped variable references:
     - Global: `@{...}`
     - Self (table-local): `%{...}`
     - Context: `${...}`  
   - Example:
     ```toml
     config = ~( @{base} + '/config.toml' )
     ```

3. **COMMENT**  
   - Comments starting with `#`, extending to the end of the line.  
   - Example:
     ```toml
     # This is a comment
     ```

4. **FLOAT**  
   - Floating-point numeric literals, including those with exponents (`1.23e4`) and special values like `inf` and `nan`.
   - Example:
     ```toml
     pi = 3.14
     exponent = 1.23e4
     ```

5. **INTEGER**  
   - Integer numeric literals in decimal, binary (`0b...`), octal (`0o...`), and hexadecimal (`0x...`) formats.
   - Example:
     ```toml
     hex_number = 0x2A
     binary_number = 0b101010
     ```

6. **BOOLEAN**  
   - Boolean literals: `true`, `false`.
   - Example:
     ```toml
     is_active = true
     ```

7. **NULL**  
   - The literal `null`.
   - Example:
     ```toml
     missing = null
     ```

8. **KEYWORD**  
   - Reserved keywords:
     - Logical: `if`, `elif`, `else`, `not`, `and`, `or`, `is`
     - Control flow: `for`, `in`
     - Directives: `include`
   - Example:
     ```toml
     [settings]
     active = true if is_ready else false
     ```

9. **RESERVED_FUNC**  
   - Reserved special functions:
     - `File()`, `Git()`  
   - Example:
     ```toml
     source = File("requirements.txt")
     repo = Git("https://repo.git", tag="v1.0")
     ```

10. **TABLE_ARRAY**  
    - Headers for table arrays:
      ```toml
      [[products]]
      name = "Widget"
      ```

11. **TABLE_SECTION**  
    - Headers for standard tables:
      ```toml
      [globals]
      key = "value"
      ```

12. **INLINE_TABLE**  
    - Inline table syntax using curly braces:
      ```toml
      point = { x = 10, y = 20 }
      ```

13. **ARRAY**  
    - Lists enclosed in square brackets:
      ```toml
      colors = ["red", "green", "blue"]
      ```

14. **IDENTIFIER**  
    - General identifiers that do not match reserved words.
    - Example:
      ```toml
      name = "config"
      ```

15. **OPERATOR**  
    - Arithmetic: `+`, `-`, `*`, `/`, `%`, `**`  
    - Comparison: `==`, `!=`, `<`, `>`, `<=`, `>=`, `is`  
    - Logical: `and`, `or`, `not`  
    - Pipeline: `|`  
    - Example:
      ```toml
      result = ~( value1 + value2 | filter )
      ```

16. **PUNCTUATION**  
    - Colons, commas, semicolons, equals, etc.
    - Example:
      ```toml
      key: str = "value"
      ```

17. **WHITESPACE**  
    - Whitespace is recognized but ignored during parsing.
    - Example:
      ```toml
      key = "value"
      ```

18. **MISMATCH**  
    - Any character or sequence that does not match the above patterns results in an error.

---

## 4. Error Handling

- **Syntax Errors:**  
  - Occur when a token does not match any of the defined patterns.
  - The lexer should raise a descriptive error indicating the problematic token and its location.

- **Ambiguous Matches:**  
  - If a token could be interpreted as multiple types (e.g., string versus scoped variable), the higher-precedence type is chosen.

- **Invalid Characters:**  
  - Characters that do not belong to any valid token category should be reported immediately.

---

## 5. Examples

### Example 1: Valid Token Precedence

```toml
[config]
greeting = f"Hello, ${user.name}!"  # STRING takes precedence over SCOPED_VAR
status = ~( @{status} == "active" and true )  # SCOPED_VAR before BOOLEAN
```

### Example 2: Syntax Error

```toml
[config]
key: value  # Error: Colon used outside of a type annotation or dictionary context
```

---

## 6. Conclusion

MEP-002 specifies the precedence rules for token recognition in our markup language. By defining a clear, descending-order precedence list, we ensure consistent and predictable parsing. The lexer processes higher-precedence tokens first, which prevents ambiguity and ensures accurate syntax validation. Proper error handling is also integrated, allowing for clear identification and resolution of token mismatches.