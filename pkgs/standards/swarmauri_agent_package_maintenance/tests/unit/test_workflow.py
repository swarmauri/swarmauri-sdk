import json

import pytest
from swarmauri_agent_package_maintenance import PackageMaintenanceAgent
from swarmauri_agent_runner import SqliteRunStore
from swarmauri_base.skills.SkillBase import SkillBase
from swarmauri_base.skills.SkillCatalog import SkillCatalog
from swarmauri_core.processes import (
    IProcessBackend,
    ProcessEvent,
    ProcessHandle,
    ProcessOutput,
)
from swarmauri_standard.messages.AnswerMessage import AnswerMessage
from swarmauri_standard.tool_llms.OpenAIToolModel import OpenAIToolModel
from swarmauri_toolkit_containertoolkit import ContainerToolkit


class FixtureBackend(IProcessBackend):
    def __init__(self):
        self.requests = []

    def start(self, request):
        self.requests.append(request)
        return ProcessHandle(str(len(self.requests)))

    def read(self, handle, *, after=0, wait=0):
        return ProcessOutput(
            (ProcessEvent(1, "exit", exit_code=0, outcome="exited"),), 1
        )

    def write_stdin(self, handle, data, *, close=False):
        pass

    def cancel(self, handle):
        return False

    def release(self, handle):
        pass


@pytest.mark.unit
def test_ask_activate_and_create_a_recipe(tmp_path, monkeypatch):
    calls = [
        (
            "AskUserTool",
            {"prompt": "Which member?", "choices": ["swarmauri_core"]},
        ),
        ("ActivateSkill", {"name": "sdk-authoring"}),
        (
            "RegisterRuntimeTool",
            {
                "tool_spec": {
                    "type": "RecipeTool",
                    "name": "CheckCore",
                    "description": "Check a selected package",
                    "parameters": [
                        {
                            "name": "member",
                            "description": "Package name",
                            "input_type": "string",
                            "required": True,
                        }
                    ],
                    "steps": [
                        {
                            "tool": "RunPackageChecks",
                            "arguments": {
                                "package": {"input": "member"},
                            },
                        }
                    ],
                }
            },
        ),
        ("CheckCore", {"member": "swarmauri_core"}),
    ]

    def propose(self, messages, tools):
        if not calls:
            result = json.loads(messages[-1]["content"])
            assert result["steps"][0]["value"]["status"] == "passed"
            return {"role": "assistant", "content": "Checks passed"}
        name, args = calls.pop(0)
        assert name in tools
        return {
            "role": "assistant",
            "tool_calls": [
                {
                    "id": name,
                    "function": {
                        "name": name,
                        "arguments": json.dumps(args),
                    },
                }
            ],
        }

    monkeypatch.setattr(OpenAIToolModel, "propose_tool_step", propose)
    backend = FixtureBackend()
    agent = PackageMaintenanceAgent(
        llm=OpenAIToolModel(api_key="test"),
        store=SqliteRunStore(tmp_path / "run.db"),
        skills=SkillCatalog(
            [
                SkillBase(
                    name="sdk-authoring",
                    description="Maintain packages",
                    instructions="Check the member before editing.",
                )
            ]
        ),
        container=ContainerToolkit(container_name="sdk", backend=backend),
        repository_scope="test",
        members={"swarmauri_core": "pkgs/core"},
    )
    waiting = agent.exec("Check one member")
    assert waiting.status == "input_required"
    answer = AnswerMessage(
        question_id=waiting.questions[-1].question_id,
        answer="swarmauri_core",
    )
    assert agent.resume(waiting.run_id, answer).result == "Checks passed"
    assert len(backend.requests) == 3
    assert all(request.workspace == "sdk" for request in backend.requests)
    assert backend.requests[-1].argv[-1] == "pytest"
