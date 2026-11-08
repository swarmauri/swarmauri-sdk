import hashlib
import json
from collections.abc import Callable, Mapping
from typing import Any
from uuid import uuid4

from swarmauri_base.tools.ToolBase import ToolBase
from swarmauri_core.tools.IToolExecutor import IToolExecutor
from swarmauri_standard.messages.AnswerMessage import AnswerMessage
from swarmauri_standard.messages.QuestionMessage import QuestionMessage
from swarmauri_standard.tools.ToolExecutor import ToolExecutor
from swarmauri_tool_askuser import AskUserTool, validate_answer

from .ApprovalDecision import ApprovalDecision
from .ApprovalRequest import ApprovalRequest
from .RunState import RunState
from .RunStore import RunStore

ModelStep = Callable[
    [list[dict[str, Any]], Mapping[str, ToolBase]], dict[str, Any]
]


class AgentRunner:
    """Dispatch tool calls and resume a checkpointed conversation."""

    def __init__(
        self,
        model: ModelStep,
        store: RunStore,
        *,
        tools: Mapping[str, ToolBase] | None = None,
        executor: IToolExecutor | None = None,
        approval_policy: Callable[[ToolBase, dict[str, Any]], str]
        | None = None,
        approval_scope: str = "",
        dynamic_tools: Callable[[], Mapping[str, ToolBase]] | None = None,
        max_steps: int = 32,
    ):
        self.model = model
        self.store = store
        self.executor = executor if executor is not None else ToolExecutor()
        self.tools = dict(tools or {})
        ask_user = AskUserTool(input_handler=lambda question: question)
        if ask_user.name in self.tools:
            raise ValueError("AskUserTool is managed by the runner")
        self.tools[ask_user.name] = ask_user
        self.max_steps = max_steps
        self.dynamic_tools = dynamic_tools
        if approval_policy is not None and not approval_scope:
            raise ValueError("An approval policy requires a configured scope")
        self.approval_policy = approval_policy
        self.approval_scope = approval_scope

    def start(self, prompt: str, *, run_id: str | None = None) -> RunState:
        state = RunState(
            run_id=run_id or str(uuid4()),
            messages=[{"role": "user", "content": prompt}],
        )
        self.store.create(state)
        return self.advance(state.run_id)

    def resume(self, run_id: str, answer: AnswerMessage) -> RunState:
        state = self.store.load(run_id)
        if state.status != "input_required" or state.pending_call is None:
            raise ValueError("The run has no pending question")
        validate_answer(state.questions[-1], answer)
        state.answers.append(answer)
        self._record_result(state, answer.answer)
        self.store.save(state)
        return self.advance(run_id)

    def advance(self, run_id: str) -> RunState:
        state = self.store.load(run_id)
        for _ in range(self.max_steps):
            if state.status != "ready":
                return state
            message = self.model(list(state.messages), self._available_tools())
            calls = message.get("tool_calls") or []
            if len(calls) > 1:
                raise ValueError(
                    "The runner accepts one tool call per model step"
                )
            state.messages.append(message)
            if not calls:
                state.status = "completed"
                state.result = message.get("content")
                return self.store.save(state)
            call = calls[0]
            state.pending_call = call
            state.status = "dispatching"
            state = self.store.save(state)
            state = self._dispatch(state, call)
        return state

    def _available_tools(self):
        return {
            **(self.dynamic_tools() if self.dynamic_tools else {}),
            **self.tools,
        }

    def dispatch_recipe_step(
        self, name: str, arguments: dict[str, Any]
    ) -> dict:
        """Dispatch a recipe step using the same policy as top-level calls."""
        tool = self.tools.get(name)
        if tool is None or isinstance(tool, AskUserTool):
            return {
                "status": "denied",
                "error": "Tool is unavailable in recipes",
            }
        if (
            self.approval_policy
            and self.approval_policy(tool, arguments) != "allow"
        ):
            return {
                "status": "denied",
                "error": "Invoke this tool directly for approval",
            }
        return self.executor.execute(tool, arguments).model_dump()

    def decide(self, run_id: str, decision: ApprovalDecision) -> RunState:
        """Apply a decision to the original invocation."""
        state = self.store.load(run_id)
        call = state.pending_call
        if state.status != "approval_required" or call is None:
            raise ValueError("The run has no pending approval")
        tool = self._available_tools()[call["function"]["name"]]
        arguments = json.loads(call["function"]["arguments"])
        request = self._approval(state, tool, arguments)
        if (
            state.approval != request
            or decision.approval_id != request.approval_id
        ):
            raise ValueError("Approval does not match the current invocation")
        state.approval = None
        if decision.approved:
            state.status = "dispatching"
            state = self.store.save(state)
            self._dispatch(state, call, approved=True)
        else:
            self._record_result(state, {"status": "denied"})
            self.store.save(state)
        return self.advance(run_id)

    def _approval(self, state, tool, arguments):
        call_id = state.pending_call["id"]
        payload = json.dumps(
            [
                state.run_id,
                call_id,
                self.approval_scope,
                tool.model_dump(
                    mode="json",
                    exclude={"id": True, "parameters": {"__all__": {"id"}}},
                ),
                arguments,
            ],
            sort_keys=True,
        ).encode()
        return ApprovalRequest(
            approval_id=hashlib.sha256(payload).hexdigest(),
            call_id=call_id,
            tool_name=tool.name,
            arguments=arguments,
            scope=self.approval_scope,
        )

    def _dispatch(
        self, state: RunState, call: dict[str, Any], *, approved: bool = False
    ) -> RunState:
        function = call["function"]
        name = function["name"]
        try:
            arguments = json.loads(function["arguments"])
            if not isinstance(arguments, dict):
                raise ValueError("Tool arguments must be an object")
            tool = self._available_tools()[name]
        except (KeyError, TypeError, ValueError) as exc:
            self._record_result(state, {"error": str(exc)})
            return self.store.save(state)
        policy = (
            self.approval_policy(tool, arguments)
            if self.approval_policy
            else "allow"
        )
        if policy == "ask" and not approved:
            state.approval = self._approval(state, tool, arguments)
            state.status = "approval_required"
            return self.store.save(state)
        if policy not in ("allow", "ask"):
            self._record_result(state, {"status": "denied"})
            return self.store.save(state)
        result = self.executor.execute(
            tool,
            arguments,
            call_id=call["id"],
            context={"session_id": state.run_id},
        )
        if result.status == "completed" and isinstance(
            result.value, QuestionMessage
        ):
            state.questions.append(result.value)
            state.status = "input_required"
        else:
            value = (
                result.value
                if result.status == "completed"
                else {
                    "status": result.status,
                    "error": result.error,
                }
            )
            self._record_result(state, value)
        return self.store.save(state)

    @staticmethod
    def _record_result(state: RunState, value: Any) -> None:
        assert state.pending_call is not None
        state.messages.append(
            {
                "role": "tool",
                "tool_call_id": state.pending_call["id"],
                "content": json.dumps(value, default=str),
            }
        )
        state.pending_call = None
        state.status = "ready"
