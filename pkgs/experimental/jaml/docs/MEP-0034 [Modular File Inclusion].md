# MEP-016: Modular File Inclusion
**Author:** Jacob Stewart
**Status:** Draft  
**Created:** April 04, 2025  
**Target Language:** TBD


## 1. Abstract

This proposal introduces modular file inclusion into our new markup language. Modular file inclusion allows users to break large configurations into smaller, manageable files and then include them into a main configuration document. This feature enables reusability of common configurations, better organization, and enhanced maintainability. External files can be merged into the current configuration seamlessly, with clearly defined rules for path resolution, merging, and error handling.

---

## 2. Motivation

- **Modularity and Maintainability:**  
  Large configuration files can become difficult to manage. By allowing modular file inclusion, users can split configuration data into logically organized, smaller files.

- **Reusability:**  
  Common configuration elements (e.g., defaults, shared settings) can be defined in a single file and reused across multiple environments or projects.

- **Clarity:**  
  Modular configurations promote clarity by separating concerns—such as base configuration versus environment-specific overrides—into distinct files.

- **Interoperability:**  
  The ability to include external files enables integration with version-controlled configuration repositories, ensuring consistency across deployments.

---

## 3. Specification

### 3.1. Syntax

- **Include Directive:**  
  A new directive, `include`, will be used to incorporate external files. The syntax is as follows:
  ```toml
  include "relative/or/absolute/path/to/file.jml"
  ```
  This directive can appear at the top level or within a section to merge the included file’s contents at that point.

### 3.2. Semantics

- **File Merging:**  
  When a file is included using the `include` directive, the content of that file is merged into the current configuration at the location of the directive.
  - If the included file defines sections or keys that do not exist in the including file, they are added.
  - If there are key conflicts, the content in the including file overrides the included content.

- **Path Resolution:**  
  - Relative paths are resolved relative to the location of the including file.
  - Absolute paths are supported as well.
  
- **Recursive Inclusion:**  
  - Included files may themselves include other files.
  - Circular inclusion must be detected and raise an error to prevent infinite loops.

### 3.3. Merging Behavior

- **Merge Strategy:**  
  The merge operation works at both the table and key level:
  - **Tables:**  
    Entire sections from the included file are merged into the current configuration.
  - **Keys:**  
    Keys in the including file override keys in the included file if there is a conflict.
  - **Preservation of Formatting and Comments:**  
    For round-trip parsers, the original `include` directive should be preserved in the AST, ensuring that comments and formatting are not lost.

### 3.4. Error Handling

- **Missing File:**  
  If the specified file cannot be found or read, the parser should raise a clear error.
  
- **Circular Inclusion:**  
  If circular references are detected (i.e., a file includes another file that eventually includes the first file), the parser must raise an error to prevent infinite recursion.

- **Invalid Format:**  
  If an included file does not conform to the markup language’s syntax, an error should be raised with details indicating the nature of the syntax violation.

---

## 4. Examples

### Example 1: Basic Inclusion

```toml
# Main configuration file: main.jml
include "common.jml"

[database]
host = "localhost"
```

*Explanation:*  
The file `common.jml` is included at the top level and its contents become part of the main configuration.

---

### Example 2: Section-Specific Inclusion

```toml
[build-system]
include "build_defaults.jml"
build-backend = "poetry.core.masonry.api"
```

*Explanation:*  
The content of `build_defaults.jml` is merged into the `build-system` section. If `build_defaults.jml` defines keys that conflict with those specified after the `include` directive, the local values take precedence.

---

### Example 3: Recursive Inclusion with Merge

```toml
# File: base_config.jml
[settings]
timeout = 30
retries = 3

# File: prod_config.jml
include "base_config.jml"

[settings]
timeout = 60
```

*Explanation:*  
The `prod_config.jml` file includes `base_config.jml` so that the `settings` table starts with `timeout = 30` and `retries = 3` from the base. The local override in `prod_config.jml` then sets `timeout = 60`, leaving `retries = 3` unchanged.

---

## 5. Open Issues

- **Comment Preservation:**  
  How should comments in included files be preserved during round-trip operations? We must ensure that the `include` directive and its associated comments remain intact in the AST.
  
- **Granular Merge Control:**  
  Consider adding options to control merge behavior (e.g., merge vs. replace) for specific keys or sections.
  
- **Remote File Inclusion:**  
  Future work may include support for remote file inclusion (via HTTP/HTTPS), including caching and security considerations.
  
- **Conditional Inclusion:**  
  An extension might allow conditional file inclusion based on context or environment variables, though this is beyond the current scope.

---

## 6. Conclusion

MEP-016 introduces modular file inclusion as a core feature of our new markup language. By supporting the `include` directive, users can split configurations into modular files, promoting reusability and maintainability. The specification defines clear semantics for merging included content, handling path resolution, and ensuring error handling for missing or circular inclusions. This proposal lays the groundwork for flexible, modular configurations and will be further refined as we integrate additional features and edge-case handling.

