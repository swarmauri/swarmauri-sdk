![Swamauri Logo](https://github.com/swarmauri/swarmauri-sdk/blob/3d4d1cfa949399d7019ae9d8f296afba773dfb7f/assets/swarmauri.brand.theme.svg)

# ZDX

Z Doc Builder Experience by Swarmauri. Reusable tooling to build and serve MkDocs-based documentation sites for Swarmauri projects.

## Features

- Material for MkDocs configuration
- mkdocstrings support for API reference generation
- README harvesting across workspaces
- Dockerfile for containerized deployments

## Installation

```bash
pip install zdx
```

## Getting Started

1. Place your documentation sources in a dedicated directory (e.g., `docs/swarmauri-sdk`) and keep this location free of executable code.
2. Customize `mkdocs.yml` and `api_manifest.yaml` for your project.
3. Install `zdx` and use the `zdx` CLI to build and preview the site.


## CLI Usage

### Generate from a manifest
```bash
zdx generate --docs-dir /path/to/docs --manifest api_manifest.yaml
```

### Build READMEs into pages
```bash
zdx readmes --docs-dir /path/to/docs
```

### Serve the site
```bash
zdx serve --docs-dir /path/to/docs
```

### Generate and serve together
```bash
zdx serve --generate --docs-dir /path/to/docs --manifest api_manifest.yaml
```

## API Manifest

`zdx` uses a YAML manifest to decide which Python packages to document and how
those pages are organized. Each project keeps its manifest alongside the docs
sources. This repository includes manifests for:

| Path | Purpose |
| --- | --- |
| `infra/docs/swarmauri-sdk/api_manifest.yaml` | Generates API docs for the SDK packages. |
| `infra/docs/peagen/api_manifest.yaml` | Drives documentation for the `peagen` tool. |
| `infra/docs/tigrbl/api_manifest.yaml` | Builds docs for the `tigrbl` project. |
| `pkgs/community/zdx/api_manifest.yaml` | Template manifest for new sites. |

### Manifest Schema

An `api_manifest.yaml` file defines a list of **targets**. Each target produces
Markdown pages under `docs/api/<name>/` and a corresponding navigation entry in
the MkDocs configuration.

```yaml
targets:
  - name: Core
    package: swarmauri_core
    search_path: /pkgs/core
    include:
      - swarmauri_core.*
    exclude:
      - "*.tests.*"
```

Every field controls a different part of the generation process:

| Field | Description |
| --- | --- |
| `name` | Label used for the top‑level navigation item and the folder under `docs/api/`. |
| `search_path` | Directory containing the source package(s). The generator scans this path for modules. |
| `package` | Root import name when documenting a single package. Omit when using `discover`. |
| `discover` | When `true`, automatically finds all packages under `search_path` and builds docs for each. Generates separate folders and nav entries per package. |
| `include` | Glob patterns of fully qualified modules to include. Classes from matching modules get individual Markdown files. |
| `exclude` | Glob patterns of modules to skip. Use to drop tests or experimental code from the docs. |

For each module that survives the include/exclude filters, `zdx` writes a page
per public class. Pages land in
`docs/api/<name>/<module path>/<Class>.md` and a simple `index.md` is created if
one does not exist. The navigation section for the target is appended to
`mkdocs.yml`, ensuring the new pages appear in the rendered site.
