This example demonstrates a minimal setup for running the Peagen gateway and worker in a local development environment.

Files in this directory:

* `doe_spec.yaml` - Design-of-experiments specification used to generate project payloads.
* `template_project.yaml` - Base project template consumed by the DOE process.
* `.peagen.toml` - Minimal configuration that uses in-memory queues and the local filesystem for results and artifacts.

Use these files when starting the gateway and worker or when submitting a DOE processing task via `peagen remote`.
