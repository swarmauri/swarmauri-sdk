# Contributing to Peagen

This guide explains how to extend Peagen and how to propose major changes via Peagen Improvement Proposals (PEA-IPs).

## Template-Sets

- Place new template files under `peagen/templates/<set_name>`.
- Expose the set with an entry point under the **`peagen.template_sets`** group in your `pyproject.toml`:
  ```toml
  [project.entry-points."peagen.template_sets"]
  my_templates = "my_package.templates"
  ```

## Storage Adapters

- Implement a class exposing `upload()` and `download()`.
- Register it via the **`peagen.storage_adapters`** entry point group.

## Publishers

- Publishers broadcast events produced by the CLI.
- Create a class with a `publish()` method and add it under the **`peagen.publishers`** group.

## Evaluation Pools

- Evaluation pools manage collections of `EvaluatorBase` instances.
- Add your pool to the **`peagen.evaluator_pools`** entry point group so `peagen eval` can discover it.

## Peagen Improvement Proposals (PEA-IPs)

For substantial changes to Peagen, submit a PEA-IP:

1. Copy [docs/pea-ips/ip-template.md](docs/pea-ips/ip-template.md) to a new file `ip-XXXX.md` in the same folder.
2. Fill out all sections, including the **Status** field at the top.
3. Open a pull request with your proposal.


