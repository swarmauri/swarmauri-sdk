<picture>
  <source media="(prefers-color-scheme: dark)"  srcset="https://res.cloudinary.com/dryedzrlo/image/upload/v1757724629/swarmauri_brand_frag_light_mg8cmd.png">
  <source media="(prefers-color-scheme: light)" srcset="https://res.cloudinary.com/dryedzrlo/image/upload/v1757724629/swarmauri_brand_frag_dark_tzjuja.png">
  <!-- Fallback below (see #2) -->
  <img alt="Swarmauri Logo" src="https://res.cloudinary.com/dryedzrlo/image/upload/v1757724629/swarmauri_brand_frag_dark_tzjuja.png">
</picture>

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
