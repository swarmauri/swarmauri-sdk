# Composable execution release

This release distributes the interfaces, implementations and two compositions
merged in PR #6321. Exact package versions and workspace members are recorded
in [release-packages.json](release-packages.json).

The core, base, standard and agent runner versions are bumped because the
previously published versions do not contain the new APIs. Runtime dependency
minimums require the releases containing those APIs. Existing SDK packages
remain on the 0.11 development release line; the nine new packages begin at
0.1.0 and retain their Planning classifiers.

## Publication sequence

Publish one package at a time. Before each publication, configure or verify its
GitHub trusted publisher on PyPI with these exact values:

- Owner: `swarmauri`
- Repository: `swarmauri-sdk`
- Workflow: `v0.10.0_mono_prepare_validate_publish_batch.yaml`
- Environment: `pypi-trusted-publishing`

Use a pending trusted publisher for a project that does not yet exist. Dispatch
the existing workflow with a singleton `members_json`, `bump_type=preserve`,
`publish_mode=trusted`, and the prepared release ref. Retain the protected
`pypi-new-package-approval` environment gate. Verify the wheel and source
distribution on PyPI and the GitHub release before proceeding to the next
package. A failed publication stops the sequence; inspect registry state
before retrying to avoid duplicate or inconsistent releases.

Order: core, base, standard, agent runner, state-driven workflow, JWT tokens;
then execution controller, task manager, task store, permission policy,
delegation service, grant store, invoker; then document assistant, delegated
research, and finally the Swarmauri facade.

## Candidate validation

- All 16 wheel and source distribution builds succeeded with Poetry Core.
- `uv lock --directory pkgs` resolved the full workspace (848 packages).
- A new Python 3.12 environment installed the release wheels plus published
  PyPI dependencies, with no editable installs or workspace sources.
- `uv pip check` confirmed all 71 installed packages are compatible.
- Both installed composition commands completed. The delegated research
  command exercised grants with remaining depths 2, 1 and 0.
- The nine component/composition package suites passed (29 tests).

These are candidate checks, not evidence of publication. Hosted release gates
and registry-only installation verification must also succeed. Examples use
the documented scripted model and local identities; this release does not
claim live OAuth-provider or LLM interoperability.

## Recovery and adoption

PyPI artifacts are immutable. If a published release is defective, stop the
sequence and prepare a corrected version; do not replace its files. Consumers
can retain their previously pinned versions. If a release must be yanked,
assess dependent packages and coordinate their constraints first.

After all uploads, install the two compositions and facade in a fresh
environment using only PyPI, run `uv pip check`, and repeat both commands.
The [composition guide](README.md) is the developer handoff for configuration,
custom implementations and the limits of the demo providers.
