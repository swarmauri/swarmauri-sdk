# MEP-0028: Conditional Table Sections

## 1. Abstract

This proposal introduces conditional table sections in our markup language, allowing tables to be included or excluded based on evaluated expressions. Conditional table sections enhance flexibility and dynamic configuration by enabling or disabling sections based on context, environment variables, or other conditions. The conditional expression must result in a valid **table name** or **null/false**. The language supports both **ternary** and **comprehension-style** expressions for conditional table headers.

---

## 2. Motivation

- **Dynamic Configuration:**  
  Allows configurations to adapt based on environment, user input, or other conditions.

- **Reduce Redundancy:**  
  Avoids duplicating configurations by selectively enabling sections based on conditions.

- **Improved Readability:**  
  Consolidates conditional logic within table headers, keeping configurations clean and organized.

- **Context-Aware Configuration:**  
  Supports creating modular and context-sensitive configurations for different environments or situations.

---

## 3. Specification

### 3.1. Syntax

Conditional table sections are defined using the `~(...)` syntax within the table header. The expression inside `~(...)` determines whether the table is included or excluded during rendering.

**Syntax:**
```toml
[~(expression)]
key = "value"
```

#### Key Characteristics:
- The expression inside `~(...)` **must evaluate to either**:
  - A **valid table name** (string)  
  - **null** or **false** (indicating exclusion)  
- If the expression evaluates to **a string**, it becomes the **table name**.
- If the expression evaluates to **null** or **false**, the table is **excluded**.
- The expression **cannot** contain load-time evaluation; it must be purely render-time since it depends on context variables.

---

### 3.2. Supported Expression Styles

#### 3.2.1. Ternary Operations:
- Uses the syntax:  
  ```
  "name" if condition else None
  ```
- Example:
  ```toml
  [~("prod_config" if ${env} == "production" else None)]
  db_host = "prod.database.example.com"
  ```

#### 3.2.2. Comprehension-Style Expressions:
- Uses a natural, readable format:  
  ```
  "name" if condition else None
  ```
- Example:
  ```toml
  [~("debug" if ${is_debug} else None)]
  log_level = "DEBUG"
  ```

#### 3.2.3. Direct Boolean Expression:
- If the expression directly evaluates to **true**, the table name is retained. If **false**, the table is excluded.  
- Example:
  ```toml
  [~(${env} == "production")]
  db_url = "https://prod-db.example.com"
  ```

#### Key Differences:
- The ternary and comprehension-style expressions are **functionally identical** and both provide a flexible way to include or exclude tables.
- The direct boolean expression style is more concise when only true/false conditions are involved.

---

### 3.3. Naming and Context

- The **result of the conditional expression** directly determines the table name.
- No **stacking headers** are allowed, meaning that the evaluated result itself becomes the effective table name.
- Variables used inside `~(...)` must come from another table or context, using `${}` for context attributes and `@{}` for same-file attributes.

#### Example:
```toml
[settings]
env = "production"

[~("prod_config" if ${settings.env} == "production" else None)]
db_host = "prod.database.example.com"

[~("dev_config" if ${settings.env} == "development" else None)]
db_host = "localhost"
```

**Rendered Output (if env = "production"):**
```json
{
  "prod_config": {
    "db_host": "prod.database.example.com"
  }
}
```

---

### 3.4. Evaluation Rules

1. **Render-Time Only:**  
   - Conditional expressions in table headers are evaluated **at render time**. 
   - Any attempt to use load-time variables will raise an error.

2. **Valid Expressions:**  
   - Conditional expressions must result in either:
     - A **valid table name** (string)
     - **null** or **false** (for exclusion)  
   - Invalid expressions will result in a render-time error.

3. **Dynamic Table Naming:**  
   - If the expression evaluates to a **string**, it becomes the **table name**.
   - If it evaluates to **null** or **false**, the table is excluded.

4. **Multiple Conditional Tables:**  
   - If multiple conditional tables evaluate to **true** with the same name, they will be **merged**.
   - The **last declared table wins** in case of key conflicts.

---

## 4. Examples

### Example 1: Environment-Specific Configuration

```toml
[settings]
env = "production"

[~("prod_config" if ${settings.env} == "production" else None)]
db_url = "https://prod-db.example.com"

[~("dev_config" if ${settings.env} == "development" else None)]
db_url = "http://localhost:5432"
```

### Example 2: Conditional Inclusion Based on User Role

```toml
[user]
role = "admin"

[~("admin_permissions" if ${user.role} == "admin" else "user_permissions")]
permissions = ["read", "write", "delete"]
```

### Example 3: Using Comprehension-Style Expression

```toml
[flags]
is_debug = true

[~("debug" if ${flags.is_debug} else None)]
log_level = "DEBUG"
```

### Example 4: Direct Boolean Expression

```toml
[env]
is_prod = true

[~(${env.is_prod})]
log_level = "INFO"
```

---

## 5. Error Handling

- **Invalid Expression:**  
  - Any syntax error within the condition will halt the rendering process.
  - Example:  
    ```toml
    [~("config" if ${env} = "prod" else None)]  # Error: Invalid syntax (single = instead of ==)
    ```

- **Missing Context:**  
  - If a context variable referenced in the condition does not exist, the parser will raise an error.
  - Example:  
    ```toml
    [~("section" if ${missing_var} else None)]  # Error: Variable 'missing_var' not defined
    ```

- **Non-String or Non-Boolean Result:**  
  - If the conditional expression does not return a string, `null`, or `false`, an error will be raised.
  - Example:  
    ```toml
    [~(${env} + "test")]  # Error: Expression must return a valid name or null/false
    ```

---

## 6. Open Issues

- **Consistency of Syntax:**  
  - Since both ternary and comprehension-style expressions are supported, ensure clear documentation on when to use each.

- **Merge Behavior with Identical Names:**  
  - Clearly document that **last declared table wins** when multiple conditional tables result in the same name.

---

## 7. Conclusion

MEP-0028 introduces conditional table sections that dynamically include or exclude tables based on render-time expressions. The evaluated result must be a **valid table name**, `null`, or `false`. The language supports both **ternary** and **comprehension-style** expressions, providing flexibility and clarity in context-aware configurations.