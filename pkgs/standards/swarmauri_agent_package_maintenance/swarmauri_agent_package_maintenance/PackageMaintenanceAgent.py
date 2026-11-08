from collections.abc import Callable
from typing import Literal

from pydantic import Field, PrivateAttr
from swarmauri_agent_runner import AgentRunner
from swarmauri_agent_runner.ApprovalDecision import ApprovalDecision
from swarmauri_agent_runner.RunStore import RunStore
from swarmauri_base.ComponentBase import ComponentBase
from swarmauri_base.agents.AgentBase import AgentBase
from swarmauri_base.skills.SkillCatalog import SkillCatalog
from swarmauri_standard.messages.AnswerMessage import AnswerMessage
from swarmauri_tool_runpackagechecks import RunPackageChecks
from swarmauri_core.toolkits.IToolkit import IToolkit
from swarmauri_toolkit_runtime import RuntimeToolkit
from swarmauri_toolkit_skillset import SkillsetToolkit

from .PackageMaintenancePolicy import package_maintenance_policy


@ComponentBase.register_type(AgentBase, "PackageMaintenanceAgent")
class PackageMaintenanceAgent(AgentBase):
    """Run an SDK maintenance workflow in a configured container workspace."""

    type: Literal["PackageMaintenanceAgent"] = "PackageMaintenanceAgent"
    store: RunStore = Field(exclude=True)
    skills: SkillCatalog = Field(exclude=True)
    container: IToolkit = Field(exclude=True)
    on_output: Callable | None = Field(default=None, exclude=True)
    repository_scope: str = Field(min_length=1)
    workspace_cwd: str = "/workspace"
    members: dict[str, str]
    _runner: AgentRunner = PrivateAttr()
    _runtime: RuntimeToolkit = PrivateAttr()

    def model_post_init(self, context):
        skillset = SkillsetToolkit(catalog=self.skills)
        self._runtime = RuntimeToolkit()
        command = self.container.get_tool_by_name("RunCommandTool")
        checks = RunPackageChecks(
            backend=command.backend,
            workspace=command.workspace,
            cwd=self.workspace_cwd,
            members=self.members,
            on_output=self.on_output,
        )
        tools = {
            name: tool
            for name, tool in self.container.tools.items()
            if name
            not in {"ContainerNewSessionTool", "ContainerFeedCharsTool"}
        }
        tools.update(skillset.tools)
        tools[checks.name] = checks
        self._runner = AgentRunner(
            self.llm.propose_tool_step,
            self.store,
            tools=tools,
            dynamic_tools=lambda: {
                **skillset.available_tools(),
                **self._runtime.tools,
            },
            approval_policy=package_maintenance_policy,
            approval_scope=self.repository_scope,
        )
        self._runtime.bind_recipe_dispatch(self._runner.dispatch_recipe_step)

    def exec(self, input_str="", llm_kwargs=None):
        prompt = input_str if isinstance(input_str, str) else input_str.content
        return self._runner.start(prompt)

    async def aexec(self, input_str="", llm_kwargs=None):
        import asyncio

        return await asyncio.to_thread(self.exec, input_str, llm_kwargs)

    def resume(self, run_id: str, answer: AnswerMessage):
        return self._runner.resume(run_id, answer)

    def decide(self, run_id: str, decision: ApprovalDecision):
        return self._runner.decide(run_id, decision)
