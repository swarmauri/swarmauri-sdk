# Python support

All Swarmauri SDK PyPI packages must support Python 3.10, 3.11, 3.12, 3.13 and 3.14.
Their Requires-Python declarations and classifiers must include all five versions.
Run `python scripts/verify_python_support.py` with Python 3.11+ and packaging installed
to check declarations across the repository. The Python support workflow enforces this policy.

Metadata checks do not establish runtime compatibility. The composable execution
workflow tests the HTTPX transport and nine execution, task, permission, delegation,
invocation and workflow packages independently on all five interpreters, and runs
both document-assistant and delegated-research examples against published dependencies.
Provider integrations elsewhere in the SDK still require their own runtime tests.

## Corrective releases

The nine composable execution packages move from 0.1.0 to 0.1.1. Their HTTPX transport
dependency moves from 0.1.0.dev4 to 0.1.0.dev5. The compositions require the corrected
dependency versions so Python 3.13 and 3.14 can resolve the complete dependency chain.
Publish HTTPX first, followed by the seven factors, documentassistant, then delegatedresearch.

The audit also corrects Python constraints in 52 other packages and missing
classifiers elsewhere. These source changes take effect on PyPI when those packages
receive subsequent releases; existing PyPI artifacts and metadata are immutable.
