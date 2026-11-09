"""Stream Docker checks and resume an SDK maintenance run after approval."""

import argparse
import json
import re
import subprocess
import sys
from pathlib import Path

from swarmauri_agent_package_maintenance import PackageMaintenanceAgent
from swarmauri_agent_runner import SqliteRunStore
from swarmauri_agent_runner.ApprovalDecision import ApprovalDecision
from swarmauri_base.skills.SkillCatalog import SkillCatalog
from swarmauri_standard.tool_llms.OpenAIToolModel import OpenAIToolModel
from swarmauri_toolkit_containertoolkit import ContainerToolkit

PACKAGE = "maintenance-demo"
MEMBER = "pkgs/maintenance-demo"
CHECK_CALL = "check-fixture"
FIX_CALL = "fix-fixture"
DEFAULT_DB = Path(".state/runs.sqlite3")
WORKSPACE = Path(__file__).resolve().parent / "workspace"
DOCKER_SCOPE = r"docker:([0-9a-f]{64}):/workspace"


class ScriptedMaintenanceModel(OpenAIToolModel):
    """Choose the next tool from the transcript without calling a provider."""

    def propose_tool_step(self, messages, tools):
        last = messages[-1]
        if last["role"] == "user":
            return self._check_call(tools, CHECK_CALL, fix=False)

        result = json.loads(last["content"])
        status = result.get("status")
        if last["tool_call_id"] == CHECK_CALL:
            checks = result.get("checks", [])
            if (
                status == "failed"
                and len(checks) == 1
                and checks[0]["exit_code"] == 1
                and checks[0]["outcome"] == "exited"
            ):
                return self._check_call(tools, FIX_CALL, fix=True)
        if status == "passed":
            content = "Package checks passed."
        elif status == "denied":
            content = "Approval declined. The formatting step did not run."
        else:
            content = f"Package checks failed: {json.dumps(result)}"
        return {"role": "assistant", "content": content}

    @staticmethod
    def _check_call(tools, call_id, *, fix):
        name = tools["RunPackageChecks"].name
        return {
            "role": "assistant",
            "tool_calls": [
                {
                    "id": call_id,
                    "type": "function",
                    "function": {
                        "name": name,
                        "arguments": json.dumps({"package": PACKAGE, "fix": fix}),
                    },
                }
            ],
        }


def stream_output(event):
    """Flush Docker output immediately and mark the end of each command."""
    if event.kind == "exit":
        print(f"\n[docker] {event.outcome}, exit={event.exit_code}", flush=True)
    else:
        stream = sys.stderr if event.kind == "stderr" else sys.stdout
        stream.write(event.data.decode("utf-8", errors="replace"))
        stream.flush()


def make_agent(store, container_id):
    """Construct the agent, which creates its own AgentRunner."""
    return PackageMaintenanceAgent(
        llm=ScriptedMaintenanceModel(api_key="unused-local-demo"),
        store=store,
        skills=SkillCatalog([]),
        container=ContainerToolkit(container_name=container_id),
        repository_scope=f"docker:{container_id}:/workspace",
        members={PACKAGE: MEMBER},
        on_output=stream_output,
    )


def start(store):
    """Build the packaged fixture and keep its container until a decision."""
    print("Building the Docker workspace...", flush=True)
    image = subprocess.check_output(
        ["docker", "build", "--quiet", str(WORKSPACE)], text=True
    ).strip()
    container_id = subprocess.check_output(
        ["docker", "run", "--rm", "--detach", "--network", "none", image],
        text=True,
    ).strip()
    waiting = False
    try:
        state = make_agent(store, container_id).exec(
            "Check the fixture and request approval before formatting."
        )
        waiting = state.status == "approval_required"
        return state
    finally:
        if not waiting:
            stop_workspace(container_id)


def decide_run(store, run_id, approval_id, approved):
    """Recover the workspace ID from the saved approval and apply the decision."""
    pending = store.load(run_id)
    if pending.status != "approval_required" or pending.approval is None:
        raise ValueError("The run has no pending approval")
    scope = re.fullmatch(DOCKER_SCOPE, pending.approval.scope)
    if scope is None:
        raise ValueError("The pending approval has no Docker workspace")
    container_id = scope[1]
    state = make_agent(store, container_id).decide(
        run_id, ApprovalDecision(approval_id=approval_id, approved=approved)
    )
    if state.status != "approval_required":
        stop_workspace(container_id)
    return state


def stop_workspace(container_id):
    """Stop the workspace so Docker removes its disposable container."""
    subprocess.run(
        ["docker", "stop", "--time", "1", container_id],
        check=True,
        stdout=subprocess.DEVNULL,
    )


def prompt_for_approval(state):
    """Return the operator's decision, or leave the request pending."""
    print(f"Run ID: {state.run_id}")
    print(json.dumps(state.approval.model_dump(), indent=2), flush=True)
    if sys.stdin.isatty():
        while True:
            try:
                answer = input("Approve, deny, or exit for later [a/d/E]: ")
            except (EOFError, KeyboardInterrupt):
                print()
                break
            answer = answer.strip().lower()
            if answer in ("a", "approve"):
                return True
            if answer in ("d", "deny"):
                return False
            if answer in ("", "e", "exit"):
                break
            print("Enter a to approve, d to deny, or e to exit.")
    print("Approval pending. Use resume with the run ID to reopen the prompt.")
    return None


def main():
    """Start, resume, or submit a decision for a saved run."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--db", type=Path, default=DEFAULT_DB)
    actions = parser.add_subparsers(dest="action", required=True)
    actions.add_parser("start")
    resume = actions.add_parser("resume")
    resume.add_argument("run_id")
    decide = actions.add_parser("decide")
    decide.add_argument("run_id")
    decide.add_argument("approval_id")
    decide.add_argument("decision", choices=("approve", "deny"))
    args = parser.parse_args()
    args.db.parent.mkdir(parents=True, exist_ok=True)
    store = SqliteRunStore(args.db)
    try:
        if args.action == "start":
            state = start(store)
        elif args.action == "resume":
            state = store.load(args.run_id)
            if state.status != "approval_required" or state.approval is None:
                raise ValueError("The run has no pending approval")
        else:
            state = decide_run(
                store,
                args.run_id,
                args.approval_id,
                approved=args.decision == "approve",
            )
        if state.status == "approval_required":
            approved = prompt_for_approval(state)
            if approved is None:
                return 0
            state = decide_run(
                store, state.run_id, state.approval.approval_id, approved
            )
    except KeyError:
        parser.exit(
            2, "Run not found. Use the run ID and database from the start command.\n"
        )
    except ValueError as exc:
        parser.exit(2, f"{exc}\n")
    except (OSError, subprocess.CalledProcessError) as exc:
        parser.exit(1, f"Docker workspace error: {exc}\n")

    print(f"{state.status}: {state.result}")
    if state.status == "completed":
        last_result = json.loads(state.messages[-2]["content"])
        if last_result.get("status") in ("passed", "denied"):
            return 0
    return 1


if __name__ == "__main__":
    sys.exit(main())
