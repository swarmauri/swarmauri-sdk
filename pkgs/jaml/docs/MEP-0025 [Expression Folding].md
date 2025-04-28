# MEP-0025: Expression Folding
**Author:** Jacob Stewart
**Status:** Draft  
**Created:** April 04, 2025  
**Target Language:** TBD


## 1. Abstract

This proposal introduces **expression folding** to our markup language by enabling expressions to be partially evaluated at load time and then finalized at render time. Expression folding is encapsulated within the `{^ ... ^}` enclosure. During the load phase, any sub-expressions referencing only global (`@{...}`) or self (table-local, `%{...}`) variables are resolved immediately, while sub-expressions referencing context variables (`${...}`) remain deferred. Furthermore, additional simplification rules are applied; for instance, if a folded expression reduces to a form like `true and ${flag}`, the redundant `true and` is dropped, reducing the expression to a simpler form (e.g. `{^ %{flag} ^}`).

---

## 2. Motivation

- **Unified Expression Writing:**  
  Many configuration values depend on both fixed (static) data and dynamic, context-supplied parameters. Expression folding allows authors to write a single, cohesive expression that seamlessly combines these two aspects.

- **Performance Benefits:**  
  By precomputing all static portions at load time, the system minimizes repeated computations during render time. This enhances performance when configurations are rendered repeatedly with varying contexts.

- **Clear Separation of Evaluation Phases:**  
  The `{^ ... ^}` enclosure signals that an expression will be split into a static (load-time) phase and a dynamic (render-time) phase, reducing errors from inadvertently mixing context variables into static computations.

- **Reduction of Redundancy:**  
  Additional simplification rules—such as reducing `true and ${flag}` to simply the context variable—streamline expressions and yield more concise, readable configurations.

---

## 3. Specification

### 3.1. Syntax: `{^ ... ^}`

- **Folding Enclosure:**  
  Expression folding is indicated by wrapping an expression in `{^ ... ^}`.
  ```toml
  key = {^ expression ^}
  ```
- **Sub-Expressions:**  
  Within the `{^ ... ^}` enclosure, the expression may contain:
  - **Load-Time References:** Global (`@{...}`) and self (table-local, `%{...}`) variables.
  - **Context References:** External variables (`${...}`) that are provided at render time.
  - **Standard Operations:** Arithmetic, logical operations, string concatenation, conditionals, and list comprehensions.

### 3.2. Two-Phase Evaluation

#### 3.2.1. Load-Time Pass

- **Static Resolution:**  
  During configuration load, every sub-expression that references only load-time variables is immediately evaluated. For example:
  ```toml
  {^ "http://" + @{server.host} + ":" + @{server.port} + "/api?token=" + ${auth_token} ^}
  ```
  In this phase:
  - `@{server.host}` and `@{server.port}` are resolved.
  - Static string literals and operations are computed.
  - The dynamic portion `${auth_token}` remains deferred.
  
- **Partial Result Example:**  
  After load time, the above expression might reduce to:
  ```toml
  {^ "http://prodserver:8080/api?token=" + ${auth_token} ^}
  ```

#### 3.2.2. Render-Time Pass

- **Dynamic Resolution:**  
  At render time, deferred context references (such as `${auth_token}`) are substituted using the provided runtime context.
- **Final Evaluation:**  
  The fully substituted expression is then computed to yield the final value.

#### 3.2.3. Additional Simplification Rule

- **Simplifying Redundant Boolean Logic:**  
  If, after load-time evaluation, a folded expression reduces to a logical conjunction where the left-hand side is the literal `true`, the `true and` portion is dropped.  
  For example, an expression like:
  ```toml
  {^ true and ${flag} ^}
  ```
  simplifies to:
  ```toml
  {^ %{flag} ^}
  ```
  This rule eliminates redundant boolean logic and yields a more concise expression.

### 3.3. Error Handling

- **Undefined or Invalid References:**  
  If a load-time sub-expression references an undefined global or table-local variable, the parser must raise a descriptive error during the load phase.
- **Context Variable Errors:**  
  At render time, if a context variable referenced in a folded expression is missing, the system should produce a clear error message indicating which variable is absent.
- **Syntax Issues:**  
  Any syntax error within a `{^ ... ^}` expression must trigger an informative error message detailing the location and nature of the error.

---

## 4. Examples

### Example 1: Mixed Static and Dynamic URL Construction

#### Start File

```toml
[server]
host = "prodserver"
port = 8080

[api]
# Build the API URL using a mix of static and dynamic parts.
endpoint = {^ "http://" + @{server.host} + ":" + @{server.port} + "/api?token=" + ${auth_token} ^}
```

#### After Load-Time Evaluation

- The static parts are resolved:
  - `@{server.host}` → `"prodserver"`
  - `@{server.port}` → `8080`
- The expression becomes:
  ```toml
  [api]
  endpoint = {^ "http://prodserver:8080/api?token=" + ${auth_token} ^}
  ```

#### After Render-Time Evaluation

- With the render context:
  ```toml
  auth_token = "ABC123"
  ```
- The dynamic part is substituted, yielding:
  ```toml
  [api]
  endpoint = "http://prodserver:8080/api?token=ABC123"
  ```

#### JSON Output

```json
{
  "server": {
    "host": "prodserver",
    "port": 8080
  },
  "api": {
    "endpoint": "http://prodserver:8080/api?token=ABC123"
  }
}
```

---

### Example 2: Conditional Strategy Selection with Additional Simplification

#### Start File

```toml
[logic]
is_production = false

[settings]
# Use a conditional expression to select a strategy.
strategy = {^ "ProductionStrategy" if @{logic.is_production} else ${dynamic_strategy} ^}
```

#### After Load-Time Evaluation

- `@{logic.is_production}` is resolved to `false`.
- The conditional expression simplifies to:
  ```toml
  [settings]
  strategy = {^ ${dynamic_strategy} ^}
  ```

#### Additional Simplification

- Since the folded expression now consists solely of the context variable, the expression simplifies further:
  ```toml
  [settings]
  strategy = {^ %{dynamic_strategy} ^}
  ```

#### After Render-Time Evaluation

- With the render context:
  ```toml
  dynamic_strategy = "Development"
  ```
- The final evaluated configuration becomes:
  ```toml
  [settings]
  strategy = "Development"
  ```

#### JSON Output

```json
{
  "logic": {
    "is_production": false
  },
  "settings": {
    "strategy": "Development"
  }
}
```

---

### Example 3: Simplifying a Redundant Boolean Conjunction

#### Start File

```toml
[flags]
# A redundant boolean conjunction that will be simplified.
result = {^ true and ${flag} ^}
```

#### After Load-Time Evaluation

- The expression remains as:
  ```toml
  {^ true and ${flag} ^}
  ```

#### Additional Simplification

- The simplification rule removes the redundant `true and`, reducing the expression to:
  ```toml
  {^ %{flag} ^}
  ```

#### After Render-Time Evaluation

- With the render context:
  ```toml
  flag = "enabled"
  ```
- The final evaluated configuration becomes:
  ```toml
  [flags]
  result = "enabled"
  ```

#### JSON Output

```json
{
  "flags": {
    "result": "enabled"
  }
}
```

---

## 5. Open Issues

- **Complexity Limits and Nesting:**  
  What limits should be imposed on expression complexity and nesting depth within a `{^ ... ^}` enclosure?
  
- **Operator Precedence:**  
  Define precise rules to ensure that mixed static and dynamic operations are evaluated unambiguously.
  
- **Tooling Support:**  
  Update editor plugins and debugging tools to properly highlight and partially evaluate folded expressions.
  
- **Performance Considerations:**  
  Assess the impact of complex folded expressions on load-time and render-time performance, and explore potential caching strategies.

---

## 6. Conclusion

MEP-0025 introduces **expression folding** via the `{^ ... ^}` notation, enabling a single expression to be partially evaluated at load time while deferring context-dependent sub-expressions to render time. This approach combines the efficiency of precomputed static values with the flexibility of dynamic runtime data. Moreover, additional simplification rules—such as reducing `true and ${flag}` to `{^ %{flag} ^}`—further streamline the final configuration. Together, these enhancements provide a powerful, efficient, and readable method for handling complex configurations, complementing the load-time evaluation provided by MEP-0022.