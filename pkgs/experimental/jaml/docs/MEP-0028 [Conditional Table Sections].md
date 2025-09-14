# MEP-0028: Conditional Table Sections  
**Author:** Jacob Stewart  
**Status:** Draft  
**Created:** April 04, 2025  
**Target Language:** TBD  

## 1. Abstract  
This proposal introduces dynamic table definitions in our markup language using expression-based headers. Table headers evaluate at render time to determine inclusion, naming, and batch generation. A header expression must return a string (the table name) or null/false (omit the table). When combined with generator clauses, multiple tables can be created via comprehensions.  

## 2. Motivation  
- **Dynamic Inclusion/Exclusion:**  
  Enable or disable entire tables based on render-time conditions.  

- **Batch Generation:**  
  Generate multiple tables in one concise block by iterating over collections.  

- **Reduced Redundancy:**  
  Avoid repetitive boilerplate by parameterizing similar table definitions.  

- **Context-Aware Configuration:**  
  Centralize conditional logic in headers, keeping bodies clean.  

## 3. Specification  

### 3.1. Header Syntax  
Table headers support an expression followed by zero or more generator clauses:  
```toml
[<header_expr>
  for <item> as %{alias} in @{collection} [if <cond>]
  [...]
]
```  
- `<header_expr>`: any expression that evaluates to a string, null, or false.  
- Each `for` clause binds one element of a collection as an iteration variable (`%{alias}`).  
- Optional `if` filters determine which iterations produce tables.  

### 3.2. Header Expressions  
Expressions may reference:  
- **Context variables:** `${var}`  
- **File attributes:** `@{attr}`  
- **Iteration variables:** `%{alias}`  

Supported expression forms include:  
- **String Literal:**  
  ```toml
  ["name"]
  ```  
- **F‑String:**  
  ```toml
  [f"prefix.{%{alias}}.suffix"]
  ```  
- **Ternary Expression:**  
  ```toml
  ["prod" if ${env} == "production" else null]
  ```  

A header whose expression yields a string produces a table with that name; if it yields `null` or `false`, the table is omitted.  

### 3.3. Generator Clauses (Comprehensions)  
When one or more `for … in @{…}` clauses follow the header expression, the header is evaluated once per combination of bound variables that satisfy all `if` filters. Each successful iteration produces a separate table.  

### 3.4. Render‑Time Semantics  
1. **Evaluate Headers:** All header expressions and generator clauses execute in file order.  
2. **Omit Null Tables:** Any header evaluation yielding null/false is skipped.  
3. **Produce Tables:** For comprehensions, one table per passing iteration.  
4. **Merge Duplicates:** Tables sharing a name are merged; later keys override earlier ones.  
5. **Error Conditions:** Syntax errors, undefined variables, or invalid header results (non-string, non-null, non-false) abort rendering with an error.  

## 4. Examples  

### 4.1. Conditional Inclusion  
```toml
["prod_config" if ${settings.env} == "production" else null]
db_url = "https://prod.example.com"
```
Only rendered when `settings.env` equals `production`.  

### 4.2. Batch Generation Over Packages and Modules  
```toml
rootDir  = "src"
packages = @{packages}

[ f"file.{pkg.name}.{mod.name}.source"
  for pkg as %{pkg} in @{packages} if pkg.active
  for mod as %{mod} in @{pkg.modules} if mod.enabled
]
name      = %{mod.name} + ".py"
path      = @{rootDir} + "/" + %{pkg.name} + "/" + %{name}
type      = "python"
test_conf = { testFramework = "pytest", tests = %{mod.tests} }
```
Generates one table per active module under each active package.  

## 5. Error Handling  
- **Syntax Errors:** Halt rendering at parse time.  
- **Undefined Variables:** Render‑time exception if any `${…}` or `@{…}` reference is missing.  
- **Invalid Header Results:** Errors if a header expression yields any type other than string, null, or false.  

## 6. Open Issues  
- Nested comprehension depth and readability.  
- Editor and tooling support for mixed expression/comprehension syntax.  
- Performance considerations for large collections.  

## 7. Conclusion  
This MEP standardizes expression-based table headers for dynamic inclusion, omission, and batch generation without legacy syntax, enabling concise, context-aware configurations at render time.

