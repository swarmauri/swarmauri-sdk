# MEP-000: Introduction and Overview
**Author:** Jacob Stewart
**Status:** Draft  
**Created:** April 04, 2025  
**Target Language:** TBD

## 1. Abstract

This proposal introduces our new markup language—a configuration format designed to be simple, human‐readable, and expressive. Drawing inspiration from established formats like TOML, YAML, and JSON, our language extends their core concepts with enhanced support for dynamic evaluation, explicit type annotations, and rich structural constructs. MEP-000 outlines the overarching goals, design principles, and key features that will guide the subsequent enhancement proposals (MEPs) for this language.

---

## 2. Motivation

### 2.1. Simplicity and Readability

- **Human-Readable Syntax:**  
  Our language aims to maintain the clarity and simplicity of TOML, ensuring that configuration files remain accessible and easy to edit by humans.
  
- **Minimalistic Design:**  
  The syntax is designed to be lightweight and unambiguous, reducing the learning curve while still providing powerful capabilities.

### 2.2. Enhanced Expressiveness

- **Static and Dynamic Constructs:**  
  In addition to standard static data types, the language supports dynamic evaluation. This enables configurations to adapt based on external context (such as environment variables) or computed values.
  
- **Scoped Variables:**  
  Variables can be defined and referenced within multiple scopes—global, table-local (self), and context-specific—allowing for flexible configuration strategies.

### 2.3. Structural Flexibility

- **Hierarchical Organization:**  
  Inspired by TOML, our language supports sections (tables), table arrays, inline tables, and lists of inline tables, enabling users to organize configurations in a modular and logical manner.
  
- **Multiline Preservation:**  
  Multiline strings, arrays, and inline tables retain their formatting, ensuring that embedded documentation, code snippets, or lengthy texts remain exactly as authored.

### 2.4. Interoperability and Extensibility

- **Mapping to Existing Standards:**  
  The language is designed to map neatly to existing formats such as TOML, JSON, and YAML, facilitating integration with current tools and workflows.
  
- **Future-Proofing:**  
  The design anticipates future enhancements such as dynamic evaluation of expressions, integration with external schema definitions, and advanced type checking.

---

## 3. Key Features

### 3.1. Data Types and Structures

- **Scalar Types:**  
  Support for strings (including multiline strings), integers (decimal, octal, hexadecimal, binary), floats (with special values like `inf` and `nan`), booleans, and null.

- **Collection Types:**  
  Arrays (inline and multiline), inline tables, standard tables (sections), and table arrays, as well as lists of inline tables.

- **Type Annotations:**  
  Optional annotations provide clarity on expected data types and serve as documentation for validation and tooling.

### 3.2. Dynamic Evaluation

- **Evaluation Enclosures:**  
  The language distinguishes between static values and dynamically evaluated expressions. Dynamic constructs allow the configuration to adapt based on runtime or external context.

- **Evaluation Timing:**  
  Support for load-time, render-time, and mixed evaluation modes ensures that users can precisely control when expressions are resolved.

### 3.3. Scoped Variables

- **Global Scope:**  
  Variables defined in a global section, referenced with a designated symbol (e.g., `@{...}`), are available throughout the configuration.

- **Self (Table-Local) Scope:**  
  Variables defined within a table are resolved locally, allowing overrides of global defaults.

- **Context Scope:**  
  Variables provided externally (via context during rendering) are referenced with a specific notation (e.g., `${...}`) and enable dynamic configuration.

### 3.4. File and Git Referencing

- **File Referencing:**  
  The language can incorporate external file content through explicit syntax, enabling modular configuration management.

- **Git Referencing:**  
  Integration with Git repositories allows for version-controlled configurations and dynamic inclusion of external content.

### 3.5. Multiline and Preservation Features

- **Multiline Strings:**  
  Support for triple-quote syntax preserves newlines, indentation, and formatting exactly as written.

- **Multiline Arrays and Inline Tables:**  
  Arrays and inline tables may span multiple lines, preserving both order and readability.

- **List of Inline Tables:**  
  Inline tables can be used as elements within an array to represent lists of dictionaries, enhancing modular data representation.

---

## 4. Comparison with Existing Formats

Our markup language draws on the strengths of formats like TOML by:
- Maintaining a simple, clean syntax.
- Supporting rich data types and hierarchical structures.
- Extending these capabilities with dynamic evaluation and explicit type annotations.
- Ensuring that all multiline and complex structures retain their original formatting.

---

## 5. Proposed MEP Roadmap

To fully realize the language's capabilities, subsequent MEPs will address specific feature areas:
- **MEP-001:** Supported Data Types and Structural Elements
- **MEP-002:** Support for Scoped Variables (Global, Self, Context)
- **MEP-003:** Multiline Constructs and Preservation
- **MEP-004:** Type Annotations and Validation
- **MEP-005:** Dynamic Evaluation and Expression Handling
- **MEP-006:** File Referencing and Embedding
- **MEP-007:** Git Referencing and Integration
- *Additional MEPs will cover conditional logic, external schema integration, and more.*

---

## 6. Conclusion

MEP-000 establishes the overall vision and design goals of our new markup language. It outlines a language that is both simple and powerful—maintaining the readability of TOML while extending its functionality to support dynamic evaluation, explicit type annotations, and a rich set of structural constructs. This foundational document provides the framework upon which the subsequent MEPs will build, ensuring a coherent and extensible specification.

