## PTGEN_SPECIFICATION 0.0.2

---

### 1. **projects_payload.yaml**

**Purpose:**  
Defines the primary metadata for a project’s structure, including the project name, description, requirements, packages, and modules. It serves as the core data source that other templates and processes consume.

**Schema Overview:**

1. **Project-Level Keys**  
   - **project_name** *(string, required)*  
     Name of the project.
   - **project_root** *(string, required)*  
     Designated root folder for project output.
   - **project_purpose** *(string, optional)*  
     Brief statement describing the project’s objective.
   - **project_description** *(string, optional)*  
     More detailed description of the project’s functionality or goals.
   - **project_requirements** *(list of strings, optional)*  
     Global requirements that apply to the entire project.
   - **template_set** *(string, required)*  
     Defines which template set or theme is used to generate the project’s artifacts.
   - **packages** *(list, required)*  
     An array of package entries, each describing an individual package.

2. **Package-Level Schema** *(each entry in `packages`)*  
   - **name** *(string, required)*  
     Package name (often used as the folder and distribution name).
   - **authors** *(list of strings, required)*  
     Maintainers or authors of this package.
   - **purpose** *(string, required)*  
     High-level goal or objective of the package.
   - **description** *(string, required)*  
     A brief summary of what the package does.
   - **requirements** *(list of strings, required)*  
     Package-level requirements and constraints.
   - **package_requires** *(list, optional)*  
     A list specifying external library dependencies for this package, often with versions.
   - **modules** *(list, optional)*  
     A collection of module definitions belonging to this package.
   - **template_set_override** *(string, optional)*  
     Overrides the package’s default template set, if needed.

3. **Module-Level Schema** *(each entry in `modules`)*  
   - **name** *(string, required)*  
     Name of the module (usually the Python file name).
   - **authors** *(list of strings, optional)*  
     List of authors for the module (may default to the package authors if omitted).
   - **purpose** *(string, required)*  
     High-level purpose of the module.
   - **description** *(string, required)*  
     Brief description of the module’s functionality.
   - **requirements** *(list of strings, required)*  
     Functional or design requirements for this module.
   - **dependencies** *(list of strings, optional)*  
     References to other modules, packages, or files this module depends on.  
     - **Colon Notation** *(e.g., `package_name:ModuleName.extension`)* is supported to link modules across packages.  
     - **Direct Paths** *(e.g., `base/filename.py`)* can also be used.
   - **examples** *(list of strings, optional)*  
     References to example files or modules that demonstrate usage.
   - **template_set_override** *(string, optional)*  
     Overrides the default or package-level template set for specific module use cases.
   - **extras** *(object, optional)*  
     - **resource_kind** *(string)*  
       A label indicating the resource category (e.g., “tools”, “toolkits”, etc.).
     - **base_name** *(string)*  
       The Python base class name to inherit from.
     - **base_file** *(string)*  
       The file path where the base class is located.

**Contexts Produced:**  
- **Project Context (PROJECT_CTX)**: Contains the overarching project details—name, root, requirements, etc.  
- **Package Context (PKG_CTX)**: Produced for each package in `packages`; includes package-specific metadata.  
- **Module Context (MOD_CTX)**: Produced for each module within each package; includes module-specific metadata.

---

### 2. **ptree.yaml.j2**

**Purpose:**  
A Jinja-based template that iterates through the **projects_payload.yaml** data to generate a “project file tree” specification. This file tree tells the generator what files to create, copy, or render, and with which templates or transformations.

**Schema Overview (File Record Schema):**  
Each file record in the `ptree.yaml.j2` output specifies:

- **FILE_NAME** *(string, required)*  
  Jinja expression for the source template file path (e.g., `{{ PROJECT_ROOT }}/{{ PKG.NAME }}/...`).
- **RENDERED_FILE_NAME** *(string, required)*  
  The destination path for the rendered file (e.g., `{{ PROJECT_ROOT }}/{{ PKG.NAME }}/LICENSE`).
- **PROCESS_TYPE** *(enum, required)*  
  - `COPY`: Copy the file directly, no additional rendering.  
  - `GENERATE`: Render the file as a Jinja template.  
  - `SCRIPT`: A special process type for scripts or custom logic.
- **AGENT_PROMPT_TEMPLATE** *(string, optional)*  
  Points to the Jinja template (e.g., `agent_default.j2`) used to process this file.  
- **PROJECT_NAME** *(string)*  
  Project name context for the file.
- **PACKAGE_NAME** *(string, optional)*  
  Package name context for the file.
- **MODULE_NAME** *(string, optional)*  
  Module name context for the file.
- **FILE_CTX** *(object, required)* 
  Contains the file-specific context:
  - **purpose** *(string)*  
    What this file is meant to accomplish.
  - **description** *(string)*  
    Additional details about what the file will hold or do.
  - **requirements** *(list of strings)*  
    Functional or structural requirements for the file.
  - **DEPENDENCIES** *(list of strings, optional)*  
    Additional files or modules needed to render or validate this file.
  - **EXAMPLES** *(list of strings, optional)*  
    References to example files or code snippets to incorporate.
  - **extras.base_class** *(string, optional)*  
    The base class to inherit from if generating Python classes.
  - **extras.mixins** *(list, optional)*  
    Extra classes or mixins to incorporate in the Python class.
  - **extras.resource_kind** *(string, optional)*  
    An additional label or tag for specialized resource handling.

**Contexts Used and Produced:**  
- **Project, Package, and Module Contexts** from **projects_payload.yaml** are each read in sequence.  
- For each context, the template generates file records describing how to construct or render each file.  
- **File Context (FIL_CTX)**: A refined context for each generated file, including the file’s purpose, description, dependencies, etc.

---

### 3. **agent_default.j2**

**Purpose:**  
Acts as the default code generation or content generation template for individual files. It uses the context passed in from **ptree.yaml.j2** (including project, package, module, and file context) to produce a final rendered output.

**Structure & Fields:**
- **command** *(string)*  
  A potential command or label for the generation step (sometimes unused).
- **purpose** *(string)*  
  Purpose pulled from the `FILE_CTX` or module context.
- **description** *(string)*  
  Detailed explanation pulled from the `FILE_CTX` or module context.
- **requirements** *(list of strings)*  
  Requirements from the `FILE_CTX`.
- **style guide** *(list of rules)*  
  Often appended to enforce PEP 8, docstring style, or other formatting rules.
- **dependencies** *(list of strings)*  
  List of any files or modules that should be included or referenced.
- **file and code preferences** *(list of constraints)*  
  This typically ensures that the generated code or file content meets user-defined constraints (e.g., “must use logging”, “must fully implement all methods”).
- **desired output** *(instructions)*  
  Tells the agent or generator how to finalize the file, often referencing example code or usage scenarios.
- **example output** *(illustration)*  
  Shows a sample of how the final file might look (for demonstration in comments or included references).

**Contexts Consumed:**  
- **Project Context, Package Context, Module Context, File Context** generated within **ptree.yaml.j2**.  
- Merges these contexts into one final Jinja environment to produce the ultimate content for each file.

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

**End of PTGEN_SPECIFICATION 0.0.2**