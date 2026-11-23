# MEP-0011c: Resolution Rules

**Author:** Jacob Stewart  
**Status:** Draft  
**Created:** April 09, 2025  
**Target Language:** TBD

---

## 1. Abstract

MEP-0011c defines a comprehensive set of resolution rules for our configuration language that optimizes the Abstract Syntax Tree (AST) during the resolve phase. This phase precomputes all parts of the configuration that depend solely on static data (global and local scopes) while leaving unresolved only those parts that depend on dynamic context. In particular, if string concatenation involves context variables, the rule mandates folding the result into an f‑string to guarantee proper string interpretation at render time.

---

## 2. Motivation

### 2.1. Separation of Static and Dynamic Concerns

By applying resolution rules to reduce static expressions at resolve time, we can:
- **Optimize Performance:** Eliminate unnecessary computation during the render phase.
- **Increase Predictability:** Ensure that every expression resolvable by known variables is computed early, leaving dynamic substitutions isolated.
- **Simplify Debugging:** The AST at the end of the resolve phase clearly shows which parts are static and which parts require context.

### 2.2. Consistent Expression Handling

Having clear, systematic rules for:
- **Variable Substitution:** Ensures that global (`@{…}`) and local (`%{…}`) variables are correctly and consistently replaced.
- **Arithmetic and Boolean Simplification:** Allows mathematical and logical expressions to be computed at resolve time.
- **String Concatenation:** Enables the automatic transformation of mixed static-dynamic string expressions into f‑strings, ensuring that dynamic parts (context variables) are interpreted correctly during render time.

---

## 3. Specification of Resolution Rules

The resolution rules apply to each expression node in the AST. They are designed to operate recursively, simplifying expressions as completely as possible using only static (global and local) data. The primary components are as follows:

### 3.1. Variable Substitution
- **Static Variables:**
  - **Rule:** Replace every occurrence of a global (`@{variable}`) or local (`%{variable}`) variable with its resolved value.
  - **Example:**  
    - Given `[globals] base = "/home/user"`, replace `@{base}` with `"/home/user"`.

- **Context Variables:**
  - **Rule:** Leave `${…}` placeholders intact; they remain unresolved until render time.

### 3.2. Arithmetic Evaluation
- **Constant Folding:**
  - **Rule:** If all operands in an arithmetic expression (e.g., addition, subtraction, multiplication, division) are static values, evaluate the expression immediately.
  - **Example:**  
    - `<( 3 + 4 )>` becomes `7`.
- **Operator Precedence:**
  - **Rule:** Respect standard operator precedence (e.g., multiplication/division before addition/subtraction).
  - **Example:**  
    - `<( 2 + 3 * 4 )>` is resolved as `14` (i.e. compute `3 * 4` first).

- **Mixed Expressions:**
  - **Rule:** For arithmetic expressions that include dynamic context, evaluate the static parts and leave the unresolved elements as placeholders.

### 3.3. Boolean Logic Simplification
- **Static Boolean Evaluation:**
  - **Rule:** Evaluate Boolean expressions that contain only known static values.
  - **Example:**  
    - `<( true and false )>` resolves to `false`.
- **Conditional (Ternary) Expressions:**
  - **Rule:** For expressions like `<( 'Yes' if true else 'No' )>`, if `true` and `false` are resolved to Python booleans, compute the result accordingly.
  - **Example:**  
    - With `true` as `True`, the expression becomes `"Yes"`.

### 3.4. String Concatenation
- **Static Concatenation:**
  - **Rule:** If an expression concatenates only static strings (or already resolved values), simply join them.
  - **Example:**  
    - `<( "Hello, " + "World!" )>` resolves to `"Hello, World!"`.
- **Dynamic Concatenation Involving Context Variables:**
  - **Rule:** When concatenation involves any context variable (i.e., `${…}`), the entire expression must be folded into an f‑string.
  - **Rationale:**  
    This ensures that the dynamic portion will be evaluated as a string during render time.
  - **Example:**  
    - `<( "http://" + @{server.host} + "/api?token=" + ${auth_token} )>` should be folded into an f‑string equivalent to:  
      ```python
      f"http://{server.host}/api?token={auth_token}"
      ```
    - At resolve time, static parts (like `@{server.host}`) are replaced; the context placeholder (`${auth_token}`) is retained and resolved at render.

### 3.5. Resolution Process Flow

1. **Traverse the AST:**
   - Recursively analyze every node in the expression tree.
2. **Substitution and Evaluation:**
   - For each node, substitute global and local values.
   - Apply constant folding for arithmetic and Boolean expressions.
3. **Simplify String Operations:**
   - When encountering a string concatenation:
     - **If purely static:** Concatenate immediately.
     - **If mixed:** Fold the expression into an f‑string.
4. **Leave Dynamic Placeholders:**
   - Any part of the expression involving `${…}` that can’t be resolved with static data is left for render time.

---

## 4. Examples

### 4.1. Substitution and Arithmetic
**Input:**
```toml
[globals]
base = "/home/user"

[calc]
sum = <( 3 + 4 )>
```
**Resolution:**
- `@{base}` would be substituted if present.
- `<( 3 + 4 )>` is fully computed to `7`.

### 4.2. Boolean and Conditional Logic
**Input:**
```toml
[cond]
status = <( 'Yes' if true else 'No' )>
```
**Resolution:**
- With `true` mapped to Python’s `True`, this resolves to `"Yes"`.

### 4.3. Static String Concatenation
**Input:**
```toml
[message]
text = <( "Hello, " + "World!" )>
```
**Resolution:**
- Evaluates immediately to `"Hello, World!"`.

### 4.4. Dynamic String Concatenation (Folding into an f-string)
**Input:**
```toml
[api]
endpoint = <( "http://" + @{server.host} + "/api?token=" + ${auth_token} )>
```
**Resolution:**
- **Step 1 (Substitution):** Replace `@{server.host}` with its static value (e.g., `"prodserver"`).
- **Step 2 (Dynamic Folding):**  
  Since `${auth_token}` is a context variable, fold the concatenation into an f‑string:
  ```python
  f"http://prodserver/api?token={auth_token}"
  ```
- **Render Outcome:** With a context providing `"ABC123"` for `auth_token`, the final resolved value is:  
  `"http://prodserver/api?token=ABC123"`

---

## 5. Conclusion

**MEP-0011c: Resolution Rules** establishes a clear, systematic approach for simplifying configuration expressions during the resolve phase. By:
- **Substituting** static global and local variables,
- **Evaluating** arithmetic and Boolean expressions,
- **Concatenating** strings statically when possible,
- **Folding** into f‑strings when context variables are encountered,

we can optimize the AST so that only genuinely dynamic content remains for the render phase. This rules-based approach not only improves performance but also clarifies the separation between static and dynamic evaluation, thereby enhancing both predictability and maintainability of our configuration system.
