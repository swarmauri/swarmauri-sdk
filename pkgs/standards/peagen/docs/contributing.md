# Contributing to Peagen

This guide explains how to extend Peagen and how to propose major changes via Peagen Improvement Proposals (PEA-IPs).

All plugin implementations must be accessed via ``PluginManager``. Do not import
modules from ``peagen.plugins`` directly in production code.

## Template-Sets

- Place new template files under `peagen/templates/<set_name>`.
- Expose the set with an entry point under the **`peagen.template_sets`** group in your `pyproject.toml`:
  ```toml
  [project.entry-points."peagen.template_sets"]
  my_templates = "my_package.templates"
  ```

## Git Filters

- Implement a class exposing `upload()` and `download()`.
  The `upload()` method must return the artifact URI so Peagen can store
  references in Git commits and task payloads.
- Register it via the **`peagen.plugins.git_filters`** entry point group.

## Publishers

- Publishers broadcast events produced by the CLI.
- Create a class with a `publish()` method and add it under the **`peagen.plugins.publishers`** group.

## Evaluation Pools

- Evaluation pools manage collections of `EvaluatorBase` instances.
- Add your pool to the **`peagen.plugins.evaluator_pools`** entry point group so `peagen eval` can discover it.

## Peagen Improvement Proposals (PEA-IPs)

For substantial changes to Peagen, submit a PEA-IP:

1. Copy [docs/pea-ips/ip-template.md](docs/pea-ips/ip-template.md) to a new file `ip-XXXX.md` in the same folder.
2. Fill out all sections, including the **Status** field at the top.
3. Open a pull request with your proposal.


