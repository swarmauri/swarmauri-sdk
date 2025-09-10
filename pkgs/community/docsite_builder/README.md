![Swamauri Logo](https://res.cloudinary.com/dbjmpekvl/image/upload/v1730099724/Swarmauri-logo-lockup-2048x757_hww01w.png)

# Docsite Builder

Reusable tooling to build and serve MkDocs-based documentation sites for Swarmauri projects.

## Features

- Material for MkDocs configuration
- mkdocstrings support for API reference generation
- Dockerfile for containerized deployments

## Getting Started

1. Place your documentation sources in a dedicated directory (e.g., `docs/swarmauri-sdk`).
2. Customize `mkdocs.yml` and `api_manifest.yaml` for your project.
3. Install `docsite_builder` and use the `docsite-builder` CLI to build and preview the site.


## CLI Usage

### Generate from a manifest
```bash
docsite-builder generate --docs-dir /path/to/docs --manifest api_manifest.yaml
```

### Serve the site
```bash
docsite-builder serve --docs-dir /path/to/docs
```

### Generate and serve together
```bash
docsite-builder serve --generate --docs-dir /path/to/docs --manifest api_manifest.yaml
```
