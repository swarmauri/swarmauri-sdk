# MEP-015: Merge Operator
**Author:** Jacob Stewart
**Status:** Draft  
**Created:** April 04, 2025  
**Target Language:** TBD


## 1. Abstract

This proposal introduces the **Merge Operator** for our new markup language—a mechanism to combine or extend configuration objects by merging keys and values from one table (or inline table) into another. In addition to supporting straightforward table merges, this proposal extends the merge operator to work in conjunction with scoped variables, allowing the merge source to include values from global, self (table-local), or context scopes. Merge operations are applicable both at the table level and within inline tables, promoting modularity and reusability throughout the configuration.

---

## 2. Motivation

- **Modularity and Reusability:**  
  Users frequently define a base configuration that should be extended or overridden in specific contexts (e.g., environments or feature-specific configurations). The merge operator enables this pattern without duplication.
  
- **Scoped Configuration:**  
  Configurations often depend on variables defined in different scopes. Allowing merge operations to incorporate scoped variables (global, self, and context) facilitates more dynamic and maintainable configurations.
  
- **Inline and Standard Structures:**  
  By supporting merge operations in both standard tables and inline tables, our language provides flexibility in how users structure and organize their configurations.
  
- **Enhanced Readability:**  
  Merging helps to keep configuration files DRY (Don't Repeat Yourself) and easier to manage. When combined with scoped variables, it also ensures that local overrides and external context are consistently applied.

---

## 3. Specification

### 3.1. Basic Merge Operator Syntax

The merge operator is denoted by `<<` and is used to merge the contents of one table into another.

- **Table Merge:**
  ```toml
  [default]
  retries = 3
  timeout = 30

  [production]
  << = default
  timeout = 60
  ```
  In this example, the `production` table inherits all key/value pairs from the `default` table. Keys defined in `production` (such as `timeout`) override those from `default`.

- **Inline Table Merge:**
  Inline tables can also merge other inline tables. For example:
  ```toml
  settings = { theme = "dark", << = { font = "Arial", size = 12 } }
  ```
  Here, the inline table `{ font = "Arial", size = 12 }` is merged into the `settings` inline table.

### 3.2. Merge Operations with Scoped Variables

Merge operations may leverage scoped variables to determine the source table for the merge. The language supports the following scopes:

- **Global Scope (`@{...}`):**  
  Values defined in a global section.
  
- **Self (Table-Local) Scope (`%{...}`):**  
  Values defined within the current table; these take precedence over global ones.
  
- **Context Scope (`${...}`):**  
  Values provided externally at render time.

**Examples:**

- **Merge Using a Global Reference:**
  ```toml
  [globals]
  base-config = { retries = 3, timeout = 30 }

  [production]
  << = @{base-config}
  timeout = 60
  ```
  Here, `@{base-config}` from the global scope is merged into `production`.

- **Merge Within an Inline Table Using Scoped Variables:**
  ```toml
  [project]
  settings = { 
    theme = "light", 
    << = %{override} 
  }

  [project.override]
  theme = "dark"
  ```
  In this example, the inline table in `project.settings` is merged with the table from `project.override` using a self (table-local) scoped reference.

- **Conditional Merge with Context Scope:**
  (Assuming that merge sources can be dynamically chosen based on context at render time.)
  ```toml
  [config]
  << = ${env_config}
  ```
  The external context supplies the value for `${env_config}` (for example, a table corresponding to a production or development configuration), which is merged into `config`.

### 3.3. Merge Semantics

- **Key Precedence:**  
  Keys defined in the target table always override keys from the merged table.
  
- **Recursive Merge:**  
  Nested tables are merged recursively following the same precedence rules.
  
- **Multiple Merges:**  
  Multiple merge operations are applied in order; later merges override earlier ones where conflicts occur.
  
- **Type Consistency:**  
  A merge operation is only valid if the corresponding values in the source and target are compatible (e.g., both tables). Merging a table into a scalar or array is considered invalid and should produce an error.

### 3.4. Merge Operator in Different Contexts

- **Within Standard Tables:**  
  The merge operator can appear as a key-value pair inside a table:
  ```toml
  [production]
  << = default
  ```
  
- **Within Inline Tables:**  
  Inline tables support merge operations as part of their definition:
  ```toml
  settings = { color = "blue", << = { font = "Arial", size = 12 } }
  ```
  
- **Using Scoped Variables:**  
  Merge sources can be specified using scoped variables:
  ```toml
  [deployment]
  << = @{base-config}
  << = ${extra_config}
  ```
  This merges both a global variable (`@{base-config}`) and a context-supplied variable (`${extra_config}`) into the `deployment` table.

### 3.5. Preservation in Round-Trip Parsing

- **AST Preservation:**  
  When a configuration file is parsed into an abstract syntax tree (AST) and then dumped back to a file, the merge operator (`<<`) and any scoped variable references used with it must be preserved exactly as authored.
  
- **No Loss of Information:**  
  The merging instructions should remain intact, ensuring that round-trip operations do not lose the original merge syntax or its semantics.

---

## 4. Examples

### Example 1: Table Merge with Scoped Global Variable

```toml
[globals]
base-config = { retries = 3, timeout = 30 }

[production]
<< = @{base-config}
timeout = 60
```

*In this example, the `production` table merges the `base-config` from the global scope, with `timeout` overridden in `production`.*

---

### Example 2: Inline Table Merge with Self Scope

```toml
[project]
settings = { theme = "light", << = %{override} }

[project.override]
theme = "dark"
```

*Here, the inline table in `project.settings` is merged with a table from the same section, overriding the theme to "dark".*

---

### Example 3: Merge Using Context Scope

```toml
[config]
<< = ${env_config}
```

*In this example, the `config` table merges an external configuration provided via the context under the key `env_config`.*

---

## 5. Open Issues

- **Error Handling:**  
  Define precise error messages for invalid merge operations, such as type mismatches or incompatible merge sources.
  
- **Performance Considerations:**  
  In configurations with many nested merges, performance optimizations may be required.
  
- **Tooling:**  
  Update editors and linters to recognize and correctly process merge operators and scoped variable references.

---

## 6. Conclusion

MEP-015 extends the merge operator functionality in our new markup language to support merging with scoped variables, applying both to standard tables and inline tables. This feature enhances modularity and reusability by allowing base configurations to be extended or overridden dynamically. By clearly defining key precedence, recursive merging, and round-trip preservation, this proposal lays the foundation for robust, maintainable configuration files.
