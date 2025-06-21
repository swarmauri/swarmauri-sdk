# BYOK and Private Repository Impact

Peagen's fitness evaluators only read code from the workspace, so the BYOK
(Bring Your Own Key) model does not require additional credentials for Ruff or
Pytest checks. Performance benchmarks may need API tokens if they interact with
external services. Use the same secret resolution flow described in
`secret_refs.md` by supplying a `secretRef` for the required key.

Large Ruff and Pytest logs should be stored as Git artifacts. When a log file is
under 1&nbsp;MB it can be committed directly. Bigger logs are uploaded through the
configured git filter and the resulting object ID is appended to the task
metadata so the gateway can retrieve it later.
