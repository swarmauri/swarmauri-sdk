
![Swamauri Logo](https://res.cloudinary.com/dbjmpekvl/image/upload/v1730099724/Swarmauri-logo-lockup-2048x757_hww01w.png)

<p align="center">
    <a href="https://pypi.org/project/peagen/">
        <img src="https://img.shields.io/pypi/dm/peagen" alt="PyPI - Downloads"/></a>
    <a href="https://hits.sh/github.com/swarmauri/swarmauri-sdk/tree/master/pkgs/standards/peagen/">
        <img alt="Hits" src="https://hits.sh/github.com/swarmauri/swarmauri-sdk/tree/master/pkgs/standards/peagen.svg"/></a>
    <a href="https://pypi.org/project/peagen/">
        <img src="https://img.shields.io/pypi/pyversions/peagen" alt="PyPI - Python Version"/></a>
    <a href="https://pypi.org/project/peagen/">
        <img src="https://img.shields.io/pypi/l/peagen" alt="PyPI - License"/></a>
    <a href="https://pypi.org/project/peagen/">
        <img src="https://img.shields.io/pypi/v/peagen?label=peagen&color=green" alt="PyPI - peagen"/></a>
</p>

---

# Peagen: a Template‑Driven Workflow

## Why Use the Peagen CLI?

#### Reduced Variance in LLM‑Driven Generation  
- While LLMs inherently introduce some nondeterminism, Peagen’s structured prompts, injected examples, and dependency‑aware ordering significantly reduce output variance. You’ll still see slight variations on each run, but far less than with ad‑hoc prompt calls.

#### Consistency & Repeatability  
- By centralizing file definitions in a YAML payload plus Jinja2 `ptree.yaml.j2` templates, Peagen ensures every project run follows the same logic. Changes to templates or project YAML immediately propagate on the next `peagen` invocation.

#### No Vector Store—Pure DAG + Jinja2  
- Peagen does *not* rely on a vector store or similarity search. Instead, it constructs a directed acyclic graph (DAG) of inter‑file dependencies, then topologically sorts files to determine processing order. Dependencies and example snippets are injected directly into prompt templates via Jinja2.

#### Built‑In Dependency Management  
- The CLI’s `--transitive` flag toggles between strict and transitive dependency sorts, so you can include or exclude indirect dependencies in your generation run.

#### Seamless LLM Integration  
- In GENERATE mode, the CLI automatically fills agent‑prompt templates with context and dependency examples, calls your configured LLM (e.g. OpenAI’s GPT‑4), and writes back the generated content. All model parameters (provider, model name, temperature) flow through CLI flags and environment variables—no extra scripting needed.

---

## When to Choose CLI over the Programmatic API

### Interactive Iteration  
- Quickly regenerate after tweaking templates or YAML with a single shell command—faster than editing and running a Python script.

### CI/CD Enforcement  
- Embed `peagen sort` and `peagen process` in pipelines (GitHub Actions, Jenkins, etc.) to ensure generated artifacts stay up to date. Exit codes and verbosity flags integrate seamlessly with automation tools.

### Polyglot & Minimal Overhead  
- Teams in Java, Rust, Go, or any language can use Peagen by installing and invoking the CLI—no Python API import paths to manage.

### What Is Peagen?
#### Core Concepts
> Peagen is a template‑driven orchestration engine that transforms high‑level project definitions into concrete files - statically rendered or LLM‑generated - while respecting inter‑file dependencies.

At its heart sits the Peagen class (core.py, class Peagen), which encapsulates:

Project Loading
- Reads one or more YAML payloads describing packages, modules, and template locations, turning them into in‑memory project objects.

Template Rendering
- Uses Jinja2 to render each package's ptree.yaml.j2 into a flat list of file records, complete with metadata (path, mode, dependencies).
Dependency Graph Construction
= Builds a directed acyclic graph (DAG) of file records based on declared DEPEDNENCIES fields, ensuring correct ordering.
Topological / Transitive Sorting
- Offers both strict topological sort and a transitive variant to include indirect dependencies via the --transitive flag.
File Processing
- Iterates the sorted list of file records and either:
  - Renders static COPY templates, or
  - Fills an agent‑prompt template and invokes the LLM for GENERATE mode.

#### Resume & Revision Support
Allows resuming from any file index or template, and writing revisions back to project YAML or templates when peagen revise is used.

#### Key Public Methods
All methods below belong to core.py, class Peagen:

- `load_projects()`
Loads and validates the YAML payload(s), returning a list of project dictionaries enriched with template paths and metadata.

- `process_all_projects()`
For each loaded project, runs the full render → graph → sort → process pipeline, returning a mapping of project names to processed file records.

- `process_single_project(project: Dict, start_idx: int = 0, start_file: Optional[str] = None)`
Executes the pipeline for one project, optionally resuming at start_idx or at a specific file path, and returns the sorted records plus the final index processed.

Each of these methods is invoked by the CLI commands in cli.py (e.g. process() calls Peagen.load_projects() then Peagen.process_single_project()). By understanding these core components, you can both use the CLI effectively and extend Peagen programmatically.

---

## Prerequisites & Setup

### Installing Peagen

```bash
# From PyPI (recommended)
pip install peagen

# From source (latest development)
git clone https://github.com/swarmauri/swarmauri-sdk.git
cd pkgs/standards/peagen
pip install .

peagen --help
````

### Executing `peagen --help`

```bash
peagen --help
```

![image](https://github.com/user-attachments/assets/52ce6b30-c7cc-4f9e-b9e4-8dde8f034b9c)


### Configuring `OPENAI_API_KEY`

```bash
export OPENAI_API_KEY="sk-…"
```

### CLI Defaults via `.peagen.toml`

Create a `.peagen.toml` in your project root to store provider credentials and
command defaults. A typical configuration might look like:

```toml
# .peagen.toml
[llm]
default_provider = "openai"
default_model_name = "gpt-4"

[llm.api_keys]
openai = "sk-..."

[storage]
default_adapter = "file"

[storage.adapters.file]
output_dir = "./peagen_artifacts"
```

With these values in place you can omit `--provider`, `--model-name`, and other
flags when running the CLI.

### Project YAML Schema Overview

```yaml
# projects_payload.yaml
PROJECTS:
  - NAME: "ExampleParserProject"
    ROOT: "pkgs"
    TEMPLATE_SET: "swarmauri_base"
    PACKAGES:
      - NAME: "base/swarmauri_base"
        MODULES:
          - NAME: "ParserBase"
            EXTRAS:
              PURPOSE: "Provide a base implementation of the interface class."
              DESCRIPTION: "Base implementation of the interface class"
              REQUIREMENTS:
                - "Should inherit from the interface first and ComponentBase second."
              RESOURCE_KIND: "parsers"
              INTERFACE_NAME: "IParser"
              INTERFACE_FILE: "pkgs/core/swarmauri_core/parsers/IParser.py"
```

---

## CLI Entry Point Overview

### `peagen process`

Render and/or generate files for one or more projects.

```bash
peagen process <PROJECTS_YAML> \
  [--project-name <NAME>] \
  [--include-swarmauri | --swarmauri-dev] \
  [--transitive] \
  [--provider <PROVIDER>] \
  [--model-name <MODEL>] \
  [-v | -vv]
```
    
![image](https://github.com/user-attachments/assets/1f52f066-8caa-4070-ab63-63350f95b0ee)

### `peagen sort`

Show the planned file‑generation order without making changes.

```bash
peagen sort <PROJECTS_YAML> \
  [--project-name <NAME>] \
  [--transitive] \
  [-v | -vv]
```

![image](https://github.com/user-attachments/assets/216369fb-b9e9-4ab9-84ca-5f13f7dfbc88)

### `peagen revise`

Update project YAML or templates based on previous run metadata.

```bash
peagen revise <PROJECTS_YAML> \
  [--project-name <NAME>] \
  [-v | -vv]
```

![image](https://github.com/user-attachments/assets/61292165-fb36-4662-8836-7971b2a7e7d0)

### `peagen templates`

List available template sets and their directories:

```bash
peagen templates
```

![image](https://github.com/user-attachments/assets/d0757543-87df-45d5-8962-e7580bd3738a)


---

## Examples & Walkthroughs

### Single‑Project Processing Example

```bash
peagen process projects.yaml \
  --project-name MyProject \
  --provider openai \
  --model-name gpt-4 \
  -v
```

* Loads only `MyProject` from `projects.yaml`.
* Renders its `ptree.yaml.j2` into file records.
* Builds the dependency DAG and topologically sorts it.
* Processes each record: static or LLM‑generated.

### Batch Processing All Projects

```bash
peagen process projects.yaml \
  --provider openai \
  --model-name gpt-4 \
  -vv
```

* Iterates every project in `projects.yaml`.
* Processes them sequentially (load → render → sort → generate).
* Uses DEBUG logs to print full DAGs and rendered prompts.

### Transitive Dependency Sorting with Resumption

```bash
peagen process projects.yaml \
  --project-name AnalyticsService \
  --transitive \
  --start-file services/data_pipeline.py \
  -v
```

* Builds full DAG including indirect dependencies.
* Topologically sorts all records.
* Skips ahead to `services/data_pipeline.py` and processes from there.

---

## Advanced Tips

### Resuming at a Specific Point

* `--start-file <PATH>`: begin at a given file record.
* `--start-idx <NUM>`: jump to a zero‑based index in the sorted list.

### Custom Agent‑Prompt Templates

```bash
peagen process projects.yaml \
  --agent-prompt-template-file ./custom_prompts/my_agent.j2 \
  --provider openai \
  --model-name gpt-4
```

### Integrating into CI/CD Pipelines

```yaml
# .github/workflows/generate.yml
name: Generate Files
on:
  push:
    paths:
      - 'templates/**'
      - 'packages/**'
      - 'projects.yaml'
jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.x'
      - name: Install dependencies
        run: pip install peagen
      - name: Generate files
        env:
          OPENAI_API_KEY: ${{ secrets.OPENAI_API_KEY }}
        run: |
          peagen process projects.yaml \
            --template-base-dir ./templates \
            --provider openai \
            --model-name gpt-4 \
            --transitive \
            -v
      - name: Commit changes
        run: |
          git config user.name "github-actions[bot]"
          git config user.email "actions@github.com"
          git add .
          git diff --quiet || git commit -m "chore: update generated files"
```


## Conclusion & Next Steps

### Embedding Peagen Programmatically

```python
from peagen.core import Peagen
import os

agent_env = {
    "provider": "openai",
    "model_name": "gpt-4",
    "api_key": os.environ["OPENAI_API_KEY"],
}
pea = Peagen(
    projects_payload_path="projects.yaml",
    additional_package_dirs=[],
    agent_env=agent_env,
)

projects = pea.load_projects()
result, idx = pea.process_single_project(projects[0], start_idx=0)
```

### Contributing & Extending Templates

* **Template Conventions:** Place new Jinja2 files under your `TEMPLATE_BASE_DIR` as `*.j2`, using the same context variables (`projects`, `packages`, `modules`) that core templates rely on.
* **Adding New Commands:** Define a new subcommand in `cli.py`, wire it into the parser, instantiate `Peagen`, and call core methods.
* **Submitting Pull Requests:** Fork the repo, add/update templates under `peagen/templates/`, update docs/README, and open a PR tagging maintainers.
