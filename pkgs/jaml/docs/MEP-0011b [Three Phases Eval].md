# MEP-0011b: Three-Phase Evaluation with Only Folded Expressions

**Author:** Jacob Stewart  
**Status:** Draft  
**Created:** April 09, 2025  
**Target Language:** TBD

---

## 1. Abstract

This proposal redefines the processing pipeline for our configuration language by introducing a three-phase model:
 
- **Load Time:** Parse the raw configuration file into an exact Abstract Syntax Tree (AST) without any evaluation or transformation.
- **Resolve Time:** Walk the AST and “resolve” as much as possible using only the available static information (global and local scopes). This phase performs constant folding, arithmetic simplification, and substitution of any expressions that do not require dynamic input.
- **Render Time:** Finally, replace any remaining placeholders that rely on dynamic, context-specific values and fully evaluate any expressions that still contain unresolved references.

---

## 2. Motivation

### 2.1. Unified Expression Syntax

- **Simplification:**  
  By using only one set of delimiters—`<( … )>`.

- **Consistency:**  
  A single expression syntax makes it easier for configuration authors to understand how and when expressions are evaluated.

### 2.2. Separation of Evaluation Phases

- **Load Time:**  
  Capturing the user’s input exactly as written ensures round-trip fidelity and aids in debugging.
  
- **Resolve Time:**  
  Much like applying resolution rules in propositional theorem proving, the resolve phase optimizes the AST by precomputing any part of the expressions that can be determined using global (`@{…}`) and local (`%{…}`) scopes. The result is a lean AST with static values already computed and placeholders only for context-dependent data.

- **Render Time:**  
  At runtime, the environment supplying dynamic values (via `${…}` placeholders) is injected, and any remaining unresolved expressions are finalized. This design minimizes the workload during render by deferring only what is necessary.

### 2.3. Improved Performance and Predictability

- **Efficiency:**  
  Pre-resolving static parts of the configuration at resolve time minimizes the work required when rendering the final configuration.

- **Predictability:**  
  With a clear separation of static versus dynamic evaluation, the final configuration output becomes more predictable—authors know exactly which parts will be computed ahead of time and which will be substituted at render time.

---

## 3. Specification

### 3.1. Load Time

- **Objective:**  
  Read the raw configuration file and construct an AST that preserves every literal detail, including all expression markers and variable placeholders.

- **Key Points:**
  - All expression delimiters (`<( … )>`) appear exactly as written.

- **Outcome:**  
  An AST that is a faithful, unevaluated representation of the input configuration.

### 3.2. Resolve Time

- **Objective:**  
  Process the loaded AST to resolve and simplify all expressions that depend solely on static data (global and local scopes).

- **Key Points:**
  - **Static Resolution:**  
    Evaluate folded expressions `<( … )>` that involve only global (`@{…}`) and local (`%{…}`) substitutions.
  
  - **Optimization:**  
    Apply constant folding, arithmetic simplification, and Boolean reduction. For example, an expression such as  
    ```toml
    endpoint = <( "http://" + @{host} + ":" + @{port} )>
    ```  
    should be resolved to `"http://prodserver:8080"` (assuming those values are known) at resolve time.

  - **Partial Resolution:**  
    For expressions that mix static values with dynamic context references (using `${…}`), perform as much evaluation as possible so that only the context placeholders remain unresolved.

- **Outcome:**  
  A “resolved” AST where all resolvable expressions are precomputed. Only components requiring runtime context remain as placeholders.

### 3.3. Render Time

- **Objective:**  
  Finalize the configuration by substituting dynamic context values and performing any remaining evaluations.

- **Key Points:**
  - **Dynamic Substitution:**  
    Replace `${…}` placeholders in the resolved AST using values provided by the runtime context.
    
  - **Final Evaluation:**  
    Evaluate any folded expressions that could not be fully resolved in the previous phase because of remaining dynamic content.
    
  - **Output Integrity:**  
    The output is a fully evaluated configuration where every expression has been replaced with its final value.

- **Outcome:**  
  A complete configuration object that merges precomputed static data with dynamic context information.

---

## 4. Implementation Considerations

### 4.1. AST Data Structures

- Use the same AST nodes for all expressions but adjust the internal logic so that during the resolve phase, the node’s internal representation (perhaps stored in a `FoldedExpression` object) is updated if it depends solely on static data.
- Preserve the original literal for round-trip fidelity and debugging.

### 4.2. Environment Handling

- **Static Environment:**  
  Build a global/local environment during the resolve phase by merging assignments from the AST.
  
- **Dynamic Environment:**  
  At render time, augment the static environment with the dynamic context (e.g., `{"auth_token": "ABC123"}`) ensuring that keys like `true` and `false` map to Python booleans.

### 4.3. Evaluation Function

- In the resolution (or “compile”) phase, your evaluation function should call something similar to:
  ```python
  eval(expression, {"__builtins__": {}}, static_env)
  ```
  where `expression` is the folded expression content.
- For expressions that still contain `${…}`, you must leave these parts unresolved until the render phase.

### 4.4. Error Handling and Debugging

- Unresolved variables during the resolve phase should trigger explicit, helpful error messages.
- Any discrepancies between the expected and final output (e.g., due to missing context keys) must be clearly logged at render time.

---

## 5. Examples

### 5.1. Static Resolution Example

**Input Configuration:**

```toml
[globals]
base = "/home/user"

[user]
name = "Alice"
greeting = f"Hello, %{name}! Your config is at @{base}/config.toml"
```

- **Load:**  
  The AST preserves the full literal expressions.
- **Resolve:**  
  Global and local references are replaced so that `greeting` resolves to:  
  `"Hello, Alice! Your config is at /home/user/config.toml"`
- **Render:**  
  Since no dynamic placeholders exist, the resolved value is final.

### 5.2. Dynamic Substitution Example

**Input Configuration:**

```toml
[server]
host = "prodserver"
port = 8080

[api]
endpoint = <( "http://" + @{server.host} + ":" + @{server.port} + "/api?token=" + ${auth_token} )>
```

- **Load:**  
  The AST preserves the full `<( … )>` expression.
- **Resolve:**  
  Static parts are computed:  
  `"http://prodserver:8080/api?token=" + ${auth_token}`
- **Render:**  
  With context (e.g., `{"auth_token": "ABC123"}`), the dynamic placeholder is replaced, yielding:  
  `"http://prodserver:8080/api?token=ABC123"`

### 5.3. Conditional Expression Example

**Input Configuration:**

```toml
[cond]
status = <( 'Yes' if true else 'No' )>
```

- **Load:**  
  The AST preserves the full literal expression.
- **Resolve:**  
  With static booleans provided (`true` → `True`, `false` → `False`), this expression can be fully evaluated, resulting in `"Yes"`.
- **Render:**  
  Since all static resolution was possible, the final value is already `"Yes"`.

---

## 6. Conclusion

**MEP-0011b** redefines our configuration evaluation process into three clear phases: **Load**, **Resolve**, and **Render**—with the key simplification that only one expression syntax (`<( ... )>`) is used. During **Resolve Time**, the AST is optimized by applying resolution rules (akin to propositional theorem proving) so that all static expressions are precomputed. The **Render Time** phase then simply substitutes dynamic context values and finalizes any partially resolved expressions.
