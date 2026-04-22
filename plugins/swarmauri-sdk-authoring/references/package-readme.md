# Package README Rules

Every new Swarmauri or Tigrbl package README must be publishable, not a stub.

## Branding

- Use Swarmauri branding by default.
- Use Tigrbl branding for Tigrbl packages.
- Do not embed local image paths.

Swarmauri SVG:

```markdown
![Swarmauri Logo](https://github.com/swarmauri/swarmauri-sdk/blob/3d4d1cfa949399d7019ae9d8f296afba773dfb7f/assets/swarmauri.brand.theme.svg)
```

Tigrbl SVG:

```markdown
![Tigrbl Logo](https://github.com/swarmauri/swarmauri-sdk/blob/a170683ecda8ca1c4f912c966d4499649ffb8224/assets/tigrbl.brand.theme.svg)
```

## Required Sections

- Title and one short purpose paragraph.
- Badge set: downloads, hits, supported Python versions, license, and release version.
- `## Features` with concrete package capabilities.
- `## Installation` with both `uv` and `pip` commands.
- `## Usage` showing expected workflows with importable code.
- Project links or contribution guidance consistent with nearby packages.

## Badge Targets

Use the package distribution name in PyPI badge URLs. Use the package repo path in the hits badge URL. Prefer the repository default branch `master` unless the package family already uses another branch in nearby files.
