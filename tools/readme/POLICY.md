# Package README policy

swarmauri/swarmauri-sdk adopts package-guide-v1 from readme-standards==0.1.3. Every active Python project has the complete fixed heading tree and its own branding/counters. The H1 is the manifest package name. Authored explanations are preserved in README.md; generated regions come from manifests, the shared brand catalog, and maintained examples.

The gate checks structure, declared inputs, examples’ syntax, and referenced files. It does not confer external certification or claim that credentials, remote APIs, or every runtime workflow were exercised. Source-only harnesses use checkout instructions rather than fictitious wheel installs.

Retired packages, historical archives, and nested demonstration fixtures are explicit inventory exclusions. They are not reactivated or republished by this migration. Existing deprecation and migration instructions remain authoritative.

Run the dedicated workflow or `uv run --no-project --with readme-standards==0.1.3 pytest --readme-standards --readme-all --readme-root . -c tools/readme/pytest.ini --confcutdir tools/readme tools/readme`. Use the same environment for `readme-standards render --root PACKAGE --write`, then review the diff. A missing section or authored explanation fails; CI does not repair it.
