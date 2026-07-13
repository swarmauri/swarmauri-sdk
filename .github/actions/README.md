# Shared Composite Actions

Org-level composite GitHub Actions used across Swarmauri repositories.

## Purpose

Centralize reusable CI/CD steps so every repo can adopt the same workflows without copy-paste. Actions live here; consumers pin a ref and call them.

## Usage

From any repo in the org:

```yaml
- uses: swarmauri/swarmauri-sdk/.github/actions/<name>@<ref>
  with:
    # action inputs
```

Replace `<name>` with the action directory name and `<ref>` with a tag, branch, or commit SHA.

Example:

```yaml
- uses: swarmauri/swarmauri-sdk/.github/actions/setup-python@v1
```

## Versioning

- Prefer immutable tags (`v1`, `v1.2.0`) or commit SHAs in production workflows.
- Branches (`main`) are for development only; they move and can break consumers.
- Breaking changes get a new major tag. Non-breaking fixes stay on the current major.

## Develop-then-adopt

Flow (see issue #1254):

1. **Develop** the action in this repo under `.github/actions/<name>/`.
2. **Validate** with workflows in this repo that exercise the action.
3. **Tag** a release when stable.
4. **Adopt** in other repos by pointing `uses:` at the tagged ref.
5. **Iterate** here first; consumers bump their pin when ready.

Do not copy action source into consumer repos. Pin and update the ref instead.
