# Python compatibility checks

Run isolated package checks from the repository root:

```powershell
uv run scripts/run_all_tests.py --python 3.10 3.11 3.12 3.13 3.14 --jobs 4
```

The runner builds the selected package and its local dependency closure, installs
them in a separate environment for each interpreter, and runs unit tests from
`pkgs/`. Integration, performance, and documentation-example markers are excluded.
Native extensions require their compiler toolchains. Some tests require OpenSSL;
use `--tool-path "C:\Program Files\Git\usr\bin"` on Windows when appropriate.

`--packages NAME ...` selects packages. `--resume --retry-failed` reuses results
whose source signatures still match. `--cases-from results.json` selects explicit
package/version pairs for a focused rerun. Use different output directories for
concurrent runs. Each directory contains stage logs, JUnit XML, individual result
JSON, and an aggregate `results.json`; `context.json` records platform information,
arguments, and hashes of explicitly supplied dependency wheels.

## Interpreting results

`passed` requires successful functional tests. `no_tests`, `no_tests_collected`,
`license_only`, and `tests_skipped` describe coverage gaps; they are neither
functional passes nor failures. Packages without tests are still built and
installed. Build, install, collection, assertion, timeout, and runner errors remain
failures. JUnit counts distinguish license checks from functional tests and retain
skip reasons. A successful unit check does not certify external services, optional
extras, other operating systems, or skipped features.

## Dependency limitations

The November 2026 Windows validation uses an explicit local Gensim 4.4.0 rebuild
for Python 3.14. Reproduce it with:

```powershell
uv run scripts/build_gensim_compat.py --python 3.14
uv run scripts/run_all_tests.py --find-links .tmp/compatibility-dependency-wheels
```

The recipe verifies pinned upstream source hashes and regenerates extension code
with Cython. It writes wheel hashes and build provenance beside the artifacts.
This is a local dependency workaround, not evidence that a normal PyPI-only
installation works on those interpreters.

The deprecated experimental umbrella keeps TensorFlow/DeepFace and PaCMAP in
optional `vision` and `manifold` extras. Its default unit checks do not validate
those backends. Unix process limits and Unix-domain socket cases are explicitly
skipped on unsupported Windows platforms. The libsodium Windows bundle is tested;
its Unix source-build branch requires separate platform validation.
