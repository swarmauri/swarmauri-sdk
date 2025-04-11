# MEP-005: Namespaces
**Author:** Jacob Stewart
**Status:** Draft  
**Created:** April 04, 2025  
**Target Language:** TBD


## 1. Abstract

This proposal defines namespaces within our markup language as a mechanism for logically organizing and merging keys from multiple table sections under a common namespace. Namespaces allow keys from different tables to be grouped together, providing modularity, clarity, and preventing naming conflicts across configurations. In cases where keys conflict within the same namespace, the **last key wins**.

---

## 2. Motivation

- **Logical Organization:**  
  Group related keys from separate sections into a single coherent namespace, clarifying their intended use.

- **Key Merging:**  
  Allow keys from multiple tables to be merged into a common namespace, reducing redundancy and enhancing modularity.

- **Avoiding Naming Conflicts:**  
  Ensure that overlapping keys within the same namespace are resolved predictably, with the last key definition taking precedence.

- **Simplicity and Flexibility:**  
  Use implicit namespace merging through dotted table names without requiring explicit namespace declarations.

---

## 3. Specification

### 3.1. Namespace Definition

Namespaces are formed implicitly by using dotted table names. Multiple tables sharing a common prefix are automatically merged into a single namespace.

#### Syntax:

```toml
[namespace.subnamespace]
key1 = "value1"

[namespace.another_subnamespace]
key2 = "value2"
```

In the above example:
- `namespace` is the primary namespace.
- `subnamespace` and `another_subnamespace` are nested within the primary namespace.

### 3.2. Key Merging Rules

- Keys from different tables under the **same namespace** are merged.
- **If keys conflict within the same namespace, the last key definition wins.**
- There is no explicit declaration or merging syntax; namespaces are inferred solely from dotted table names.

#### Example:

```toml
[database.credentials]
user = "admin"

[database.connection]
host = "localhost"
port = 5432

[database.credentials]
user = "root"  # Overwrites the previous "user" key
```

**Merged Namespace:**

```json
{
  "database": {
    "credentials": {
      "user": "root"
    },
    "connection": {
      "host": "localhost",
      "port": 5432
    }
  }
}
```

### 3.3. Accessing Namespaced Keys

Keys within a namespace can be accessed using dot notation. This applies both when defining variables and when referencing them within expressions:

```toml
[api.config]
url = "http://example.com"

[api.credentials]
token = "abc123"

[service]
endpoint = "@{api.config.url}/endpoint"
```

### 3.4. Conflict Resolution: Last Key Wins

- When two tables under the same namespace define the **same key**, the **last key definition wins**.
- This ensures predictable behavior when merging configurations from multiple sources.

#### Example:

```toml
[logging]
level = "info"

[logging]
level = "debug"  # Last definition wins
```

**Final Merged Table:**

```json
{
  "logging": {
    "level": "debug"
  }
}
```

---

## 4. Examples

### Example 1: Simple Namespace Merging

```toml
[app.settings]
debug = true

[app.paths]
log = "/var/log/app.log"
```

**Merged Namespace:**

```json
{
  "app": {
    "settings": {
      "debug": true
    },
    "paths": {
      "log": "/var/log/app.log"
    }
  }
}
```

### Example 2: Conflicting Keys - Last Key Wins

```toml
[server]
host = "127.0.0.1"

[server]
host = "localhost"  # Last definition wins
port = 8080
```

**Final Merged Table:**

```json
{
  "server": {
    "host": "localhost",
    "port": 8080
  }
}
```

### Example 3: Nested Namespace

```toml
[project.metadata]
name = "MyApp"
version = "1.0.0"

[project.author]
name = "John Doe"
email = "john@example.com"
```

**Merged Namespace:**

```json
{
  "project": {
    "metadata": {
      "name": "MyApp",
      "version": "1.0.0"
    },
    "author": {
      "name": "John Doe",
      "email": "john@example.com"
    }
  }
}
```

---

## 5. Open Issues

- **Automatic Conflict Detection:**  
  While the **last key wins** rule ensures predictability, it might be helpful to warn users when a key is overwritten to avoid accidental data loss.

- **Deep Merging of Nested Namespaces:**  
  Clarify how deeply nested namespaces behave when keys overlap across different depth levels.

---

## 6. Conclusion

MEP-005 establishes simple namespace merging within our markup language. By implicitly forming namespaces through dotted table names and adopting a **last key wins** rule for conflicts, the language remains modular, readable, and predictable. This approach avoids the complexity of explicit namespace declarations while providing the flexibility needed for complex configurations.
