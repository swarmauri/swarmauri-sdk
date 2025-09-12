![Swamauri Logo](https://res.cloudinary.com/dbjmpekvl/image/upload/v1730099724/Swarmauri-logo-lockup-2048x757_hww01w.png)

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

1. Place your documentation sources in a dedicated directory (e.g., `docs/swarmauri-sdk`).
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
