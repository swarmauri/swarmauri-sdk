# MEP-010: Hyphenated Identifiers
**Author:** Jacob Stewart
**Status:** Draft  
**Created:** April 04, 2025  
**Target Language:** TBD


## 1. Abstract

This proposal defines the support for hyphenated identifiers in our new markup language. In order to improve readability and align with common configuration practices (as seen in TOML), the language will allow hyphens (`-`) in both section names and key names. This includes support for hyphenated keys with and without type annotations. The goal is to ensure that hyphenated identifiers are parsed and preserved accurately during both load and round-trip operations.

---

## 2. Motivation

- **Familiarity:**  
  Many existing configuration formats, such as TOML and YAML, permit hyphenated section and key names. Supporting this convention reduces the learning curve and makes our language more approachable.

- **Readability:**  
  Hyphenated identifiers often improve clarity by clearly separating words, making configuration files easier to read and maintain.

- **Interoperability:**  
  Allowing hyphenated names ensures compatibility with external tools and systems that expect these naming conventions.

---

## 3. Specification

### 3.1. Identifier Grammar

- **Section Names:**  
  Section names are defined using square brackets. Hyphens are allowed as a part of the identifier without requiring additional quoting. For example, `[build-system]` is a valid section name.

- **Key Names:**  
  Key names may also include hyphens. The parser will treat the hyphen as a standard character. For example:
  ```toml
  build-backend = "poetry.core.masonry.api"
  ```
  is valid without special escaping.

- **Type Annotations:**  
  Type annotations may be applied to hyphenated key names in the same manner as non-hyphenated keys:
  ```toml
  build-backend: str = "poetry.core.masonry.api"
  ```

### 3.2. Preservation in the AST and Output

- All hyphenated identifiers, whether in section names or keys, must be preserved exactly as authored.
- Both the abstract syntax tree (AST) and the final plain data representation should maintain these hyphenated names without alteration.

---

## 4. Examples

### Example 1: Hyphenated Section Name

```toml
[build-system]
requires = ["poetry-core>=1.0.0"]
build-backend = "poetry.core.masonry.api"
```

*In this example, the section name `build-system` is hyphenated, and the keys within the section are correctly processed.*

---

### Example 2: Hyphenated Key Name

```toml
[project]
name = "jaml"
build-backend = "poetry.core.masonry.api"
```

*Here, the key `build-backend` includes a hyphen and is used without a type annotation.*

---

### Example 3: Hyphenated Key Name with a Type Annotation

```toml
[project]
name = "jaml"
build-backend: str = "poetry.core.masonry.api"
```

*In this example, the key `build-backend` is annotated as a string, demonstrating that type annotations work correctly with hyphenated key names.*

---

## 5. Open Issues

- **Normalization vs. Preservation:**  
  Determine whether hyphenated identifiers should be normalized (e.g., converted to lowercase) or preserved exactly as written. The current approach favors preservation for maximum fidelity.
  
- **Reserved Character Conflicts:**  
  Confirm that the hyphen does not conflict with any future reserved punctuation or syntax in the language.
  
- **Tooling Support:**  
  Ensure that IDEs, linters, and other tools can correctly handle, autocomplete, and highlight hyphenated identifiers.

---

## 6. Conclusion

MEP-010 establishes that hyphenated identifiers are fully supported in our new markup language. This includes both section names (e.g., `[build-system]`) and key names (e.g., `build-backend`), with and without type annotations. By adopting this approach, our language remains consistent with familiar configuration formats, enhances readability, and improves interoperability with external systems and tools.

