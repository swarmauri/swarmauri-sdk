# PTGEN_SPECIFICATION 0.0.3

---

## Introduction
The **PTGEN_SPECIFICATION 0.0.3** describes a structured approach for generating project files and source code from a declarative YAML specification. It is intended for tool authors, DevOps engineers, and developers looking to automate repetitive project scaffolding tasks. By defining a standardized schema and templating model, the PTGEN system allows teams to streamline boilerplate creation, maintain uniform project structures, and reduce development overhead.

PTGEN centers around four main artifacts:

1. `projects_payload.yaml` – The core configuration that describes a project’s overarching metadata, requirements, packages, and modules.  
2. `ptree.yaml.j2` – A Jinja-based template that iterates over the payload to produce a structured set of file definitions. These definitions determine how, where, and in what form each file in the project is generated or copied.  
3. `agent_default.j2` – The default file template, consuming the final file-level context to output code and documentation aligned with the specified project requirements and style guidelines.  
4. `*.*.j2` files – *(Placeholder for additional, specialized templates.)*

By combining these four components, PTGEN enables the automated generation of consistent, well-structured codebases that adhere to user-defined requirements and best practices.

---

## Scope
This specification focuses on the following key elements:

- **Schema Definitions**: Lays out the required and optional fields within each of the three core PTGEN artifacts. It also provides guidelines for how individual fields should be interpreted or transformed.  
- **Template Contexts**: Explains the hierarchical context model—project, package, module, and file-level data—and how those contexts are passed among various templates.  
- **Generation Mechanics**: Describes how PTGEN processes the YAML payload and Jinja templates to produce or modify files.

**Outside of scope** are the following areas:

- **Implementation Details** of the template engine runtime, such as the specific version of Jinja or Python.  
- **Deployment** or integration processes for PTGEN in CI/CD environments.  
- **Extended Customization** of advanced logic like post-processing scripts, plugin-based transformations, or dynamic user input that might occur after file generation.

---

## Definitions, Acronyms, and Abbreviations

- **PTGEN**: An acronym for **Project Template Generation**, referring to the overall mechanism or system that automates project scaffolding based on YAML specifications and Jinja templates.  
- **PTREE**: Shorthand for **Project Tree**, used to describe a structured index of files and folders in a generated project. It also refers to the `ptree.yaml.j2` template that orchestrates file generation.  
- **YAML**: Stands for **YAML Ain’t Markup Language**, a human-friendly data serialization format used for the `projects_payload.yaml` configuration file.  
- **Jinja**: A Python-based templating engine that processes template files (e.g., `agent_default.j2`) using context from YAML inputs to render final artifacts.  
- **Project Context**: The highest-level context in PTGEN, derived from the top-level information in `projects_payload.yaml` (e.g., `project_name`, `project_root`, etc.).  
- **Package Context**: A context object generated for each package within the project, containing package-specific metadata (name, authors, purpose, etc.).  
- **Module Context**: A context object generated for each module in a package, capturing module-specific metadata (name, description, dependencies, etc.).  
- **File Context**: Context data that describes an individual file to be generated, including file-specific purpose, requirements, and dependencies. Produced by combining the higher-level contexts in the `ptree.yaml.j2` template.  
- **PEP 8**: The **Python Enhancement Proposal** that defines style conventions for Python code, including formatting, naming standards, and whitespace usage.  
- **PEP 420**: The **Python Enhancement Proposal** introducing implicit namespace packages. This allows a single import namespace to be split across multiple directories without requiring an `__init__.py`.  
- **PEP 484**: The **Python Enhancement Proposal** introducing optional type hints and annotations to improve code clarity and tooling support.  
- **CI/CD**: **Continuous Integration/Continuous Deployment**, a software development practice that automates building, testing, and deploying code.  
- **Spec (or Specification)**: This PTGEN document, outlining structure, formatting, and behavioral rules for the PTGEN ecosystem.

---

## Table of Contents

1. [Introduction](#introduction)  
2. [Scope](#scope)  
3. [Definitions, Acronyms, and Abbreviations](#definitions-acronyms-and-abbreviations)  
4. [PTGEN Specification Overview](#ptgen-specification-overview)  
   4.1 [projects_payload.yaml](#1-projects_payloadyaml)  
   4.2 [ptree.yaml.j2](#2-ptreeyamlj2)  
   4.3 [agent_default.j2](#3-agent_defaultj2)  
   4.4 [Context Production and Consumption Summary](#4-context-production-and-consumption-summary)  
5. [Revision History](#revision-history)  
6. [References](#references)  
7. [Roles and Responsibilities](#roles-and-responsibilities)  
   7.1 [Specification Owner](#specification-owner)  
   7.2 [Maintainers](#maintainers)  
   7.3 [Contributors](#contributors)  
   7.4 [Implementers](#implementers)  
   7.5 [Reviewers](#reviewers)  
8. [Compliance and Conformance](#compliance-and-conformance)

---

## PTGEN Specification Overview

### 1. **projects_payload.yaml**

**Purpose:**  
Defines the primary metadata for a project’s structure, including the project name, description, requirements, packages, and modules. It serves as the core data source that other templates and processes consume.

#### **Project-Level Keys**

| Key                   | Type              | Required? | Description                                                                |
|-----------------------|-------------------|----------|----------------------------------------------------------------------------|
| `project_name`        | string           | Required | Name of the project.                                                       |
| `project_root`        | string           | Required | Designated root folder for project output.                                 |
| `project_purpose`     | string           | Optional | Brief statement describing the project’s objective.                        |
| `project_description` | string           | Optional | More detailed description of the project’s functionality or goals.         |
| `project_requirements`| list of strings  | Optional | Global requirements that apply to the entire project.                      |
| `template_set`        | string           | Required | Defines which template set or theme is used to generate the project’s artifacts. |
| `packages`            | list             | Required | An array of package entries, each describing an individual package.        |

#### **Package-Level Schema** *(each entry in `packages`)*

| Key                     | Type              | Required? | Description                                                                                                              |
|-------------------------|-------------------|----------|--------------------------------------------------------------------------------------------------------------------------|
| `name`                  | string           | Required | Package name (often used as the folder and distribution name).                                                          |
| `authors`               | list of strings  | Required | Maintainers or authors of this package.                                                                                 |
| `purpose`               | string           | Required | High-level goal or objective of the package.                                                                            |
| `description`           | string           | Required | A brief summary of what the package does.                                                                               |
| `requirements`          | list of strings  | Required | Package-level requirements and constraints.                                                                             |
| `modules`               | list             | Required | A collection of module definitions belonging to this package.                                                           |
| `template_set_override` | string           | Optional | Overrides the package’s default template set, if needed.                                                                |
| `package_requires`      | list             | Optional | A list specifying external library dependencies for this package, often with versions.                                  |

#### **Module-Level Schema** *(each entry in `modules`)*

| Key                      | Type              | Required? | Description                                                                                                                                         |
|--------------------------|-------------------|----------|-----------------------------------------------------------------------------------------------------------------------------------------------------|
| `name`                   | string           | Required | Name of the module (usually the Python file name).                                                                                                  |
| `purpose`                | string           | Required | High-level purpose of the module.                                                                                                                   |
| `description`            | string           | Required | Brief description of the module’s functionality.                                                                                                    |
| `requirements`           | list of strings  | Required | Functional or design requirements for this module.                                                                                                 |
| `dependencies`           | list of strings  | Optional | References to other modules, packages, or files this module depends on.<br> - **Colon Notation** (e.g., `package_name:ModuleName.extension`) links modules across packages.<br> - **Direct Paths** (e.g., `base/filename.py`) can also be used. |
| `examples`               | list of strings  | Optional | References to example files or modules that demonstrate usage.                                                                                      |
| `template_set_override`  | string           | Optional | Overrides the default or package-level template set for specific module use cases.                                                                  |
| `extras`                 | object           | Optional | Additional metadata. For example:<br> - `resource_kind` (string): A label indicating the resource category (e.g., tools, toolkits, etc.)<br> - `base_name` (string): Python base class name to inherit from<br> - `base_file` (string): The file path where the base class is located. |

**Contexts Produced:**  
- **Project Context (PROJECT_CTX)**: Contains the overarching project details—name, root, requirements, etc.  
- **Package Context (PKG_CTX)**: Produced for each package in `packages`; includes package-specific metadata.  
- **Module Context (MOD_CTX)**: Produced for each module within each package; includes module-specific metadata.

---

### 2. **ptree.yaml.j2**

**Purpose:**  
A Jinja-based template that iterates through the **projects_payload.yaml** data to generate a “project file tree” specification. This file tree tells the generator what files to create, copy, or render, and with which templates or transformations.

#### **File Record Schema** 

| Key                   | Type             | Required? | Description                                                                                                                                             |
|-----------------------|------------------|----------|---------------------------------------------------------------------------------------------------------------------------------------------------------|
| `FILE_NAME`           | string          | Required | Jinja expression for the source template file path (e.g., `{{ PROJECT_ROOT }}/{{ PKG.NAME }}/...`).                                                    |
| `RENDERED_FILE_NAME`  | string          | Required | The destination path for the rendered file (e.g., `{{ PROJECT_ROOT }}/{{ PKG.NAME }}/LICENSE`).                                                        |
| `PROCESS_TYPE`        | enum            | Required | Determines how the file is handled:<br> - `COPY`: Copy the file directly, no additional rendering.<br> - `GENERATE`: Render the file as a Jinja template.<br> - `SCRIPT`: A special process type for scripts or custom logic. |
| `AGENT_PROMPT_TEMPLATE` | string        | Required | Points to the Jinja template (e.g., `agent_default.j2`) used to process this file.                                                                      |
| `PROJECT_NAME`        | string          | Required | Project name context for the file.                                                                                                                      |
| `PACKAGE_NAME`        | string          | Required | Package name context for the file.                                                                                                                      |
| `MODULE_NAME`         | string          | Required | Module name context for the file.                                                                                                                       |
| `FILE_CTX`            | object          | Required | Contains the file-specific context: <br> - `purpose` (string): What this file is meant to accomplish.<br> - `description` (string): Details about the file’s purpose.<br> - `requirements` (list of strings): Requirements for this file.<br> - `DEPENDENCIES` (list of strings, optional): Additional files or modules needed.<br> - `EXAMPLES` (list of strings, optional): References to example files or code snippets.<br> - `extras.base_class` (string, optional): Base class for Python classes.<br> - `extras.mixins` (list, optional): Extra classes or mixins.<br> - `extras.resource_kind` (string, optional): Label or tag for specialized resource handling. |

**Contexts Used and Produced:**  
- **Project, Package, and Module Contexts** from **projects_payload.yaml** are each read in sequence.  
- For each context, the template generates file records describing how to construct or render each file.  
- **File Context (FIL_CTX)**: A refined context for each generated file, including the file’s purpose, description, dependencies, etc.

---

### 3. **agent_default.j2**

**Purpose:**  
Acts as the default code generation or content generation template for individual files. It uses the context passed in from **ptree.yaml.j2** (including project, package, module, and file context) to produce a final rendered output.

| Field                      | Type               | Description                                                                                                                                                                                                     |
|---------------------------|--------------------|-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| `command`                 | string             | A potential command or label for the generation step (sometimes unused).                                                                                                                                        |
| `purpose`                 | string             | Purpose pulled from the `FILE_CTX` or module context.                                                                                                                                                           |
| `description`             | string             | Detailed explanation pulled from the `FILE_CTX` or module context.                                                                                                                                              |
| `requirements`            | list of strings    | Requirements from the `FILE_CTX`.                                                                                                                                                                               |
| `style guide`             | list of rules      | Often appended to enforce PEP 8, docstring style, or other formatting rules.                                                                                                                                    |
| `dependencies`            | list of strings    | List of any files or modules that should be included or referenced.                                                                                                                                             |
| `file and code preferences` | list of constraints | Ensures that the generated code or file content meets user-defined constraints (e.g., “must use logging”, “must fully implement all methods”).                                                                  |
| `desired output`          | instructions       | Tells the generator how to finalize the file, often referencing example code or usage scenarios.                                                                                                                |
| `example output`          | illustration       | Shows a sample of how the final file might look (for demonstration in comments or included references).                                                                                                         |

**Contexts Consumed:**  
- **Package Context, Module Context, and File Context** generated within **ptree.yaml.j2**. These contexts are merged into one final Jinja environment to produce the ultimate content for each file.

---

### 4. **Context Production and Consumption Summary**

- **projects_payload.yaml**  
  Produces **Project Context**, **Package Context**, and **Module Context** used by subsequent templates.

- **ptree.yaml.j2**  
  Consumes the above contexts and produces a list of **File Context** records (one for each file).

- **agent_default.j2**  
  Consumes the final **File Context** and any higher-level context to render or generate the final file output.

Each step in the pipeline expands or refines context data, which drives the final rendered files.

---

## Revision History

No notes to add.

---

## References

- **PEP 8 – Style Guide for Python Code**  
  <https://peps.python.org/pep-0008/>  

- **PEP 420 – Implicit Namespace Packages**  
  <https://peps.python.org/pep-0420/>  

- **PEP 484 – Type Hints**  
  <https://peps.python.org/pep-0484/>  

- **YAML Specification**  
  <https://yaml.org/spec/>  

- **Jinja Documentation**  
  <https://jinja.palletsprojects.com/>  

- **Python Packaging User Guide** (for `pyproject.toml` and related packaging details)  
  <https://packaging.python.org/>

---

## Roles and Responsibilities

In order to maintain a clear process for updating and using the **PTGEN_SPECIFICATION 0.0.3**, the following roles and their associated responsibilities are defined:

### Specification Owner

- Oversees the overall direction, completeness, and accuracy of the PTGEN specification.  
- Approves major changes and version increments.  
- Ensures alignment of updates with overarching organizational or community goals.

### Maintainers

- Manage the day-to-day upkeep of the specification, including minor fixes, clarifications, and editorial improvements.  
- Incorporate feedback from contributors and end users.  
- Handle version control, merge requests, and documentation of revisions (e.g., updating the Revision History).

### Contributors

- Propose changes, improvements, or clarifications to the specification.  
- Provide feedback on new features, schema revisions, or clarifications.  
- Adhere to established guidelines for submitting pull requests, issues, or discussion threads.

### Implementers

- Use the PTGEN specification to create or generate projects, packages, and modules.  
- Report issues or ambiguities in the specification.  
- Offer suggestions to improve usability, clarity, or compliance with actual project needs.

### Reviewers

- Provide quality checks on proposed changes.  
- Ensure that new or modified elements remain consistent with the established scope and style of the specification.  
- Verify that all updates adhere to the relevant standards (PEP 8, PEP 420, PEP 484, etc.).

---

## Compliance and Conformance

To ensure consistent project generation and alignment with the **PTGEN_SPECIFICATION 0.0.3**, any implementation of PTGEN should meet the following conformance criteria:

1. **Schema Adherence**  
   - **Required Fields**: All required fields in the `projects_payload.yaml` (e.g., `project_name`, `packages[].name`, `modules[].name`) must be present and correctly typed.  
   - **Optional Fields**: Optional fields, if used, must follow the specified format. For instance, `packages[].package_requires` must be a list of dependency objects with valid `NAME` and `VERSION` properties.

2. **Template Integrity**  
   - **ptree.yaml.j2 Generation**: The file definitions produced by iterating over the `projects_payload.yaml` must correctly reflect the input data. Missing or superfluous file definitions indicate non-compliance.  
   - **agent_default.j2 Output**: Generated files should adhere to the style guidelines (PEP 8, PEP 420, PEP 484) and incorporate the specified docstrings, logging, and function signatures.

3. **Context Handling**  
   - **Project, Package, Module, and File Context**: Implementations must correctly assemble and pass contexts through the generation pipeline. Each context should correctly represent its related entity (e.g., package context for each package, module context for each module, etc.).

4. **Error Handling**  
   - **Validation**: Implementations must gracefully handle invalid or incomplete `projects_payload.yaml` inputs by reporting errors or warnings.  
   - **Fallback Mechanisms**: Where partial data is present, the generator should either provide defaults (if documented) or halt and notify the user with a clear message.

5. **Continuous Verification**  
   - **Automated Testing**: Projects generated using this specification should, where possible, include or pass unit tests confirming that the structure matches PTGEN norms (e.g., presence of a `tests` folder, adherence to naming conventions, etc.).

Implementations satisfying these criteria can claim **conformance** with PTGEN_SPECIFICATION 0.0.3. Third-party verifications or self-audits may reference the criteria above to ensure consistent and reliable usage of the specification.

---

*End of PTGEN_SPECIFICATION 0.0.3*
