# Package maintenance with Docker and restartable approval

Run real Ruff and pytest checks in Docker with
[`PackageMaintenanceAgent`](https://pypi.org/project/swarmauri-agent-package-maintenance/0.1.0/).
Its [`AgentRunner`](https://pypi.org/project/swarmauri-agent-runner/0.1.0/)
stores the pending approval in SQLite, so you can review it after the Python
process exits and apply your decision from a fresh process.

This example is maintained with the Swarmauri SDK examples. To share it,
copy this directory or link to it at a specific SDK commit. The host uses the
published versions declared in `pyproject.toml`. The Docker image contains a small
fixture package with an intentional formatting issue. A scripted model
selects the tool calls from the transcript, so the demo needs no LLM account
or API key.

## Install and start

Use Python 3.12, `uv`, and a running Docker engine in Linux container mode.
From the repository root, run:

```sh
cd docs/examples/package-maintenance
uv sync
uv run python -m swarmauri_package_maintenance_demo start
```

The Python demo builds the image from its packaged Dockerfile and fixture,
starts a disposable container, and runs the checks through the SDK's Docker
backend. The build downloads its dependencies. The running container uses
its installed tools offline and has no host mounts.

The agent calls `RunPackageChecks` with `fix=false`. Ruff streams a
`Would reformat` message and exits with code 1. The agent proposes the same
tool with `fix=true`. The SDK policy asks for approval, and the runner saves
the invocation and its approval ID in `.state/runs.sqlite3`.
The terminal shows the run ID, approval ID, tool arguments, and Docker scope.
Enter `a` to approve or `d` to deny. The demo submits your answer and the
approval ID to the runner. Enter `e` or press Enter to exit and decide later.
Closing input or pressing Ctrl+C at the prompt also leaves the request
pending. Save the run ID. The demo keeps the container running while it waits
for your decision.

## Resume in a new process

Use the run ID to reopen the same approval prompt:

```sh
run_id='paste-run-id'
uv run python -m swarmauri_package_maintenance_demo resume "$run_id"
```

If you restart your terminal, return to the same working directory. If you
set `--db` before the `start` subcommand, pass the same path before `resume`.

The new agent constructs a fresh runner, recovers the Docker container ID
from SQLite, and verifies the approval against that container and the saved
tool arguments. It streams Ruff formatting, lint, and pytest output to the
terminal. Pytest prints `Checking fixture addition...` and then
`Fixture addition passed.` before the final `completed: Package checks passed.`
The read-only check from the first command has already finished and is not
replayed.

The demo stops and removes the container after approval or denial completes.
Each `start` creates a fresh workspace. Restart recovery applies at the saved
approval checkpoint.

When standard input is redirected, `start` and `resume` print the pending
request and exit. For a decision without a prompt, use the exact approval ID
shown in the request and choose `approve` or `deny`:

```sh
approval_id='paste-approval-id'
uv run python -m swarmauri_package_maintenance_demo decide "$run_id" "$approval_id" approve
```

## Build the Python distributable

```sh
uv build
```

The wheel and source distribution include the Dockerfile and fixture.
The installed module uses those files when it builds the workspace, so the
wheel can run independently of the SDK checkout.
