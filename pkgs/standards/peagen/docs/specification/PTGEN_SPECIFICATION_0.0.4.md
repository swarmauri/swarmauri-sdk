# PTGEN_SPECIFICATION 0.0.4

---

## Introduction

The **PTGEN_SPECIFICATION 0.0.4** defines a structured approach for generating project files and source code from a declarative YAML specification. This system is aimed at tool authors, DevOps engineers, and developers seeking to automate project scaffolding while maintaining consistency. The specification leverages YAML for configuration and Jinja templates for file rendering. In this revision, we streamline the required keys and move all additional metadata into an “EXTRAS” container at the project, package, module, and file levels, and all schema keys are now uppercase.

Key updates in this version include:

- **Project Level:**  
  - Renamed `PROJECT_NAME` and `PROJECT_ROOT` to `NAME` and `ROOT` respectively.  
  - Moved project description into project EXTRAS.

- **Package Level:**  
  - Only the package’s `NAME` and its collection of modules remain as required keys.  
  - All additional data—such as AUTHORS, PURPOSE, DESCRIPTION, REQUIREMENTS, and PACKAGE_REQUIRES—are now housed under PKG EXTRAS.

- **Module Level:**  
  - Only the module’s `NAME` is required.  
  - All other details (PURPOSE, DESCRIPTION, REQUIREMENTS, DEPENDENCIES, EXAMPLES, etc.) reside in MOD EXTRAS.

- **File Schema (ptree.yaml.j2):**  
  - Renamed `FILE_NAME` and `RENDERED_FILE_NAME` to `NAME` and `RENDERED_NAME`.  
  - The required keys (PROCESS_TYPE, AGENT_PROMPT_TEMPLATE, PROJECT_NAME, PACKAGE_NAME, MODULE_NAME) remain at the top level.  
  - All other attributes—including those originally defined under FILE_CTX—are now nested within an EXTRAS container.

---

## Scope

This specification addresses:

- **Schema Definitions:**  
  How the YAML configuration is structured for projects, packages, modules, and file generation. It distinguishes between required keys (necessary for the generator to run) and EXTRAS (which provide additional context for template developers).

- **Template Contexts:**  
  The hierarchy of contexts (PROJECT, PACKAGE, MODULE, FILE) and how each level’s EXTRAS enable flexibility without impacting core functionality.

- **Generation Mechanics:**  
  A conceptual explanation of how the YAML input is parsed, contexts are constructed, and files are rendered or copied via Jinja templates.

**Outside the Scope:**  
- Specific implementation details (e.g., Jinja or Python versions).  
- CI/CD integration, deployment processes, or advanced runtime customizations.

---

## Definitions, Acronyms, and Abbreviations

- **PTGEN:** **Project Template Generation** – The system automating project scaffolding using YAML and Jinja.  
- **PTREE:** **Project Tree** – Both the structured file index produced by PTGEN and the `ptree.yaml.j2` template that orchestrates file creation.  
- **YAML:** A human-friendly data serialization format (YAML Ain’t Markup Language).  
- **JINJA:** The templating engine that renders templates (e.g., `agent_default.j2`) using context data.  
- **EXTRAS:** A container for non-critical metadata (descriptions, authors, requirements, dependencies, examples, etc.) that are not required for the engine’s core operation but useful for template customization.

- **Context Levels:**  
  - **PROJECT (PROJ) CONTEXT:** Overall project metadata from `projects_payload.yaml`.  
  - **PACKAGE (PKG) CONTEXT:** Package-specific data.  
  - **MODULE (MOD) CONTEXT:** Module-specific information.  
  - **FILE CONTEXT (FILE):** Transient context produced during file record generation; all non-required attributes are nested under an EXTRAS key.

---

## Table of Contents

1. [Introduction](#introduction)  
2. [Scope](#scope)  
3. [Definitions, Acronyms, and Abbreviations](#definitions-acronyms-and-abbreviations)  
4. [PTGEN Specification Overview](#ptgen-specification-overview)  
   4.1 [PROJECTS_PAYLOAD.YAML](#41-projects_payloadyaml)  
   4.2 [PTREE.YAML.J2](#42-ptreeyamlj2)  
   4.3 [AGENT_DEFAULT.J2](#43-agent_defaultj2)  
   4.4 [FILE TEMPLATES](#44-file-templates)
   4.5 [Template Set Extras Reference](#45-template-set-extras-reference)
   4.6 [Context Production and Consumption Summary](#46-context-production-and-consumption-summary)
5. [Conceptual Generation Mechanics](#5-conceptual-generation-mechanics)  
   5.1 [Process Flow](#51-process-flow)  
   5.2 [Rationale for a Conceptual Approach](#52-rationale-for-a-conceptual-approach)  
6. [Revision History](#revision-history)  
7. [References](#references)  
8. [Roles and Responsibilities](#roles-and-responsibilities)  
9. [Compliance and Conformance](#compliance-and-conformance)

---

## 4. PTGEN Specification Overview

### 4.1. PROJECTS_PAYLOAD.YAML

**Purpose:**  
Defines the core metadata for a project’s structure. It is the primary source of information for the generator.

#### **PROJECT-LEVEL KEYS**

| KEY            | TYPE   | REQUIRED? | DESCRIPTION                                                      |
|----------------|--------|-----------|------------------------------------------------------------------|
| NAME           | string | Required  | The name of the project (formerly PROJECT_NAME).                 |
| ROOT           | string | Required  | The root folder for project output (formerly PROJECT_ROOT).        |
| TEMPLATE_SET   | string | Required  | The template set or theme used for generating artifacts.         |
| PACKAGES       | list   | Required  | An array of package entries that comprise the project.           |

#### **PROJECT EXTRAS**

All non-critical project metadata is housed under an EXTRAS container. For example:
- **DESCRIPTION:** A detailed description of the project (formerly PROJECT_DESCRIPTION).  
- Additional fields such as PURPOSE or GLOBAL REQUIREMENTS may be added here.

---

#### **PACKAGE-LEVEL SCHEMA** *(each entry in PACKAGES)*

| KEY                     | TYPE   | REQUIRED? | DESCRIPTION                                           |
|-------------------------|--------|-----------|-------------------------------------------------------|
| NAME                    | string | Required  | The package name.                                     |
| MODULES                 | list   | Required  | A collection of module definitions for the package. |
| TEMPLATE_SET_OVERRIDE   | string | Optional  | Optional override for the package’s template set.     |

#### **PACKAGE EXTRAS**

All other package-specific metadata is moved under EXTRAS:
- **AUTHORS:** List of maintainers or authors.
- **PURPOSE:** The high-level goal of the package.
- **DESCRIPTION:** A summary of the package’s functionality.
- **REQUIREMENTS:** Package-level requirements and constraints.
- **PACKAGE_REQUIRES:** External library dependencies (with version details).

---

#### **MODULE-LEVEL SCHEMA** *(each entry in a package’s MODULES)*

| KEY   | TYPE   | REQUIRED? | DESCRIPTION                         |
|-------|--------|-----------|-------------------------------------|
| NAME  | string | Required  | The module name (typically a filename). |

#### **MODULE EXTRAS**

For each module, all additional metadata is moved under EXTRAS:
- **PURPOSE:** The module’s high-level purpose.
- **DESCRIPTION:** A brief description of what the module does.
- **REQUIREMENTS:** Functional or design requirements.
- **DEPENDENCIES:** References to other modules, packages, or files.
- **EXAMPLES:** Example files or usage references.
- **TEMPLATE_SET_OVERRIDE:** Optional override for the module’s template set.

---

### 4.2. PTREE.YAML.J2

**Purpose:**  
A Jinja template that iterates over the `PROJECTS_PAYLOAD.YAML` data to produce a “project file tree” specification. This file tree directs how the generator should create, copy, or render files.

#### **FILE RECORD SCHEMA**

| KEY                     | TYPE   | REQUIRED? | DESCRIPTION                                                                                           |
|-------------------------|--------|-----------|-------------------------------------------------------------------------------------------------------|
| NAME                    | string | Required  | Jinja expression for the source template file path (formerly FILE_NAME).                              |
| RENDERED_NAME           | string | Required  | The destination path for the rendered file (formerly RENDERED_FILE_NAME).                             |
| PROCESS_TYPE            | enum   | Required  | Indicates how the file is processed: COPY, GENERATE, or SCRIPT.                                       |
| AGENT_PROMPT_TEMPLATE   | string | Required  | The Jinja template (e.g., AGENT_DEFAULT.J2) used for rendering the file.                              |
| PROJECT_NAME            | string | Required  | The project name context (should match the project’s NAME).                                           |
| PACKAGE_NAME            | string | Required  | The package name context (should match the package’s NAME).                                           |
| MODULE_NAME             | string | Required  | The module name context (should match the module’s NAME).                                             |

#### **FILE EXTRAS**

All other file-specific attributes are consolidated under an EXTRAS container. This includes any metadata previously defined in FILE_CTX such as:
- **PURPOSE**
- **DESCRIPTION**
- **REQUIREMENTS**
- **DEPENDENCIES**
- **EXAMPLES**  
…and any additional information the template might need.

---

### 4.3. AGENT_DEFAULT.J2

**Purpose:**  
This template serves as the default for generating file content. It merges the required file context (as defined in PTREE.YAML.J2) with the EXTRAS from the project, package, and module levels to produce the final rendered file.

| FIELD                         | TYPE         | REQUIRED? | DESCRIPTION                                                                                           |
|-------------------------------|--------------|-----------|-------------------------------------------------------------------------------------------------------|
| COMMAND                       | string       | Required  | A label or command for the generation step (may sometimes be unused).                               |
| PURPOSE                       | string       | Optional  | (From EXTRAS) Explains the file’s objective.                                                        |
| DESCRIPTION                   | string       | Optional  | (From EXTRAS) Provides detailed information about the file’s functionality.                         |
| REQUIREMENTS                  | list         | Optional  | (From EXTRAS) Lists the requirements for the file.                                                  |
| STYLE GUIDE                   | list         | Optional  | (From EXTRAS) Coding style guidelines (e.g., PEP 8) to follow.                                       |
| DEPENDENCIES                  | list         | Optional  | (From EXTRAS) Other files or modules that should be referenced or included.                         |
| FILE AND CODE PREFERENCES     | list         | Optional  | (From EXTRAS) Constraints to ensure the generated code adheres to specific standards.               |
| DESIRED OUTPUT                | instructions | Optional  | (From EXTRAS) Instructions on the final appearance or usage of the file.                            |
| EXAMPLE OUTPUT                | illustration | Optional  | (From EXTRAS) A sample or demonstration of what the final file might look like.                     |

**Contexts Consumed:**  
- Combines required keys from PTREE.YAML.J2 (PROJECT_NAME, PACKAGE_NAME, MODULE_NAME, etc.) with all additional metadata found in the EXTRAS containers from the project, package, module, and file levels.

---

### 4.4. FILE TEMPLATES

*Additional specialized templates (e.g., `*.J2` files) may be defined to handle custom file types or processing logic. These templates follow the same context conventions, where only minimal keys remain at the top level and all extra metadata is contained in an EXTRAS object.*

---

### 4.5. Template Set Extras Reference

Each template set can interpret custom keys within the `EXTRAS` container. A small
`EXTRAS.md` file resides in every template set directory under
`peagen/templates/<TEMPLATE_SET>/`. These documents list the extra keys that are
understood by that template set.

---

### 4.6. Context Production and Consumption Summary

- **PROJECTS_PAYLOAD.YAML**  
  – Produces the PROJECT, PKG, and MOD contexts. Only the minimal keys (NAME, ROOT, TEMPLATE_SET for projects; NAME and MODULES for packages; NAME for modules) are defined at the top level. All additional metadata is nested under EXTRAS.

- **PTREE.YAML.J2**  
  – Consumes the above contexts and produces a list of file records. In these records, only the required keys (NAME, RENDERED_NAME, PROCESS_TYPE, AGENT_PROMPT_TEMPLATE, PROJECT_NAME, PACKAGE_NAME, MODULE_NAME) remain at the top level. All other file-specific metadata is stored under the EXTRAS container.

- **AGENT_DEFAULT.J2**  
  – Merges the required file context with all EXTRAS from higher levels to render the final file output.

---

## 5. Conceptual Generation Mechanics

### 5.1 Process Flow

1. **Initial Input Parsing:**  
   - The generator loads and validates the YAML configuration (PROJECTS_PAYLOAD.YAML).  
   - Only the minimal keys (e.g., NAME, ROOT, PACKAGE NAME, MODULE NAME) are required; any additional metadata is optional and stored in EXTRAS.

2. **Context Construction:**  
   - The processor builds hierarchical contexts:  
     - **PROJECT CONTEXT:** Contains NAME, ROOT, TEMPLATE_SET plus any EXTRAS (e.g., DESCRIPTION).  
     - **PKG CONTEXT:** Contains NAME and MODULES with EXTRAS (e.g., AUTHORS, PURPOSE, DESCRIPTION, REQUIREMENTS, PACKAGE_REQUIRES).  
     - **MOD CONTEXT:** Contains NAME with EXTRAS (e.g., PURPOSE, DESCRIPTION, REQUIREMENTS, DEPENDENCIES, EXAMPLES).

3. **File Record Generation:**  
   - The PTREE.YAML.J2 template iterates over these contexts to produce file records.  
   - Each record holds the required keys (e.g., NAME, RENDERED_NAME) at the top level, with all additional file attributes nested under an EXTRAS container.

4. **Rendering or Copying Files:**  
   - Based on PROCESS_TYPE, the generator renders the file using the appropriate Jinja template (such as AGENT_DEFAULT.J2) or copies it directly.  
   - The final file output is placed at the location specified by RENDERED_NAME.

### 5.2 Rationale for a Conceptual Approach

- **Implementation Agnosticism:**  
  The abstract separation between required keys and EXTRAS allows any templating engine or language to implement the generator without enforcing unnecessary constraints.

- **Clear Data Flow:**  
  The hierarchical contexts (PROJECT, PKG, MOD, and FILE) ensure that data flows logically from high-level project configuration to individual file attributes, with EXTRAS providing additional details for customization.

- **Extensibility and Flexibility:**  
  Required keys ensure core functionality, while the EXTRAS containers allow template developers to include as much detail as necessary without cluttering the minimal required schema.

---

## Revision History

- **0.0.3:**  
  Initial specification outlining schema for PROJECTS_PAYLOAD.YAML, PTREE.YAML.J2, and AGENT_DEFAULT.J2.

- **0.0.4:**  
  - Renamed key names and restructured context schemas:
    - The project’s PROJECT_NAME and PROJECT_ROOT are now NAME and ROOT.
    - Project DESCRIPTION is moved to project EXTRAS.
    - For packages: Only NAME and MODULES are required; AUTHORS, PURPOSE, DESCRIPTION, REQUIREMENTS, and PACKAGE_REQUIRES are now under PKG EXTRAS.
    - For modules: Only NAME is required; all additional attributes (PURPOSE, DESCRIPTION, REQUIREMENTS, DEPENDENCIES, EXAMPLES) are under MOD EXTRAS.
    - For files in PTREE.YAML.J2: FILE_NAME and RENDERED_FILE_NAME become NAME and RENDERED_NAME; all other properties (including FILE_CTX) are consolidated under an EXTRAS container.
  - All keys in schema tables have been converted to uppercase.
  - Minor editorial updates for clarity and consistency.

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

- **Python Packaging User Guide**  
  <https://packaging.python.org/>

---

## Roles and Responsibilities

### SPECIFICATION OWNER

- Oversees the overall direction and integrity of the PTGEN specification.
- Approves major changes and version increments.
- Ensures that updates align with organizational or community goals.

### MAINTAINERS

- Manage day-to-day updates, fixes, and clarifications.
- Incorporate feedback from contributors and end users.
- Handle version control, merge requests, and documentation of revisions.

### CONTRIBUTORS

- Propose improvements or clarifications to the specification.
- Provide feedback on schema revisions or new features.
- Follow established guidelines for submitting changes.

### IMPLEMENTERS

- Use the PTGEN specification to generate projects, packages, and modules.
- Report ambiguities or issues with the specification.
- Offer suggestions to improve clarity or functionality.

### REVIEWERS

- Conduct quality checks on proposed changes.
- Verify that modifications remain consistent with the established scope and style.
- Ensure updates adhere to coding and design standards.

---

## Compliance and Conformance

To claim conformance with **PTGEN_SPECIFICATION 0.0.4**, implementations must:

1. **SCHEMA ADHERENCE:**  
   - Ensure that all required keys in PROJECTS_PAYLOAD.YAML (e.g., NAME, ROOT, PACKAGE NAME, MODULE NAME) are present and correctly typed.  
   - Any additional metadata is housed under the appropriate EXTRAS container.

2. **TEMPLATE INTEGRITY:**  
   - File records produced by PTREE.YAML.J2 must correctly reflect the input data with required keys at the top level and EXTRAS containing all additional information.  
   - Files generated using AGENT_DEFAULT.J2 must meet style and documentation guidelines, incorporating EXTRAS as needed.

3. **CONTEXT HANDLING:**  
   - Properly assemble and pass contexts (PROJECT, PKG, MOD, FILE) through the generation pipeline, ensuring that only the minimal keys are required at the top level and all supplemental data is available in EXTRAS.

4. **ERROR HANDLING:**  
   - Validate YAML inputs and provide clear error messages for missing required fields.  
   - Use default values or fallbacks only for documented cases.

5. **CONTINUOUS VERIFICATION:**  
   - Generated projects should pass verification tests (e.g., proper folder structure, naming conventions) confirming adherence to PTGEN norms.

---

*End of PTGEN_SPECIFICATION 0.0.4*

---

This updated specification now presents all schema keys in uppercase, ensuring consistency across the project, package, module, and file definitions while maintaining a clear separation between minimal required keys and additional metadata provided in EXTRAS.PTGEN_SPECIFICATION_0.0.3.md