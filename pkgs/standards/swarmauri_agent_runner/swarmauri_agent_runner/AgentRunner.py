import hashlib
import json
from collections.abc import Callable, Mapping
from dataclasses import asdict
from typing import Any
from uuid import uuid4

from swarmauri_base.tools.ToolBase import ToolBase
from swarmauri_core.run_stores import IRunStore
from swarmauri_core.tool_llms import (
    IToolStepModel,
    ProposedToolCall,
    ToolStepResult,
)
from swarmauri_core.tools.IToolExecutor import IToolExecutor
from swarmauri_standard.messages.AnswerMessage import AnswerMessage
from swarmauri_standard.messages.QuestionMessage import QuestionMessage
from swarmauri_standard.tools.ToolExecutor import ToolExecutor
from swarmauri_tool_askuser import AskUserTool, validate_answer

from ._checkpoint_codec import encode_checkpoint
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
        model: ModelStep | IToolStepModel,
        store: IRunStore | RunStore,
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
        self.step_model = model if isinstance(model, IToolStepModel) else None
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
            messages=(
                self.step_model.initial_tool_history(prompt)
                if self.step_model is not None
                else [{"role": "user", "content": prompt}]
            ),
            tool_step_protocol=(
                self.step_model.tool_step_protocol
                if self.step_model is not None
                else None
            ),
        )
        checkpoint = (
            encode_checkpoint(state)
            if isinstance(self.store, IRunStore)
            else state
        )
        self.store.create(checkpoint)
        return self.advance(state.run_id)

    def load(self, run_id: str) -> RunState:
        """Read the typed state of a saved run."""
        saved = self.store.load(run_id)
        state = (
            RunState.from_checkpoint(saved)
            if isinstance(self.store, IRunStore)
            else saved
        )
        if self.step_model is None:
            if state.tool_step_protocol is not None:
                raise ValueError(
                    "This run requires its original tool-step adapter"
                )
        elif state.tool_step_protocol != self.step_model.tool_step_protocol:
            if (
                state.tool_step_protocol is not None
                or self.step_model.tool_step_protocol
                != "openai-chat-completions"
            ):
                raise ValueError(
                    "This run requires its original tool-step adapter"
                )
            state.tool_step_protocol = self.step_model.tool_step_protocol
        return state

    def _save(self, state: RunState) -> RunState:
        if isinstance(self.store, IRunStore):
            return RunState.from_checkpoint(
                self.store.save(encode_checkpoint(state, advance=True))
            )
        return self.store.save(state)

    def resume(self, run_id: str, answer: AnswerMessage) -> RunState:
        state = self.load(run_id)
        if state.status != "input_required" or state.pending_call is None:
            raise ValueError("The run has no pending question")
        validate_answer(state.questions[-1], answer)
        state.answers.append(answer)
        self._record_result(state, answer.answer)
        self._save(state)
        return self.advance(run_id)

    def advance(self, run_id: str) -> RunState:
        state = self.load(run_id)
        for _ in range(self.max_steps):
            if state.status != "ready":
                return state
            if not state.pending_calls:
                content = self._propose(state)
                if not state.pending_calls:
                    state.status = "completed"
                    state.result = content
                    return self._save(state)
            call = state.pending_calls.pop(0)
            state.pending_call = call
            state.status = "dispatching"
            state = self._save(state)
            state = self._dispatch(state, call)
        return state

    def _propose(self, state: RunState) -> str | None:
        tools = self._available_tools()
        if self.step_model is None:
            message = self.model(list(state.messages), tools)
            calls = message.get("tool_calls") or []
            if len(calls) > 1:
                raise ValueError(
                    "Legacy model callables support one tool call per step"
                )
            state.messages.append(message)
            state.pending_calls = calls
            return message.get("content")

        step = self.step_model.propose_step(list(state.messages), tools)
        call_ids = [call.call_id for call in step.calls]
        if len(call_ids) != len(set(call_ids)):
            raise ValueError("The tool step contains duplicate call IDs")
        state.messages.extend(step.items)
        state.pending_calls = [
            {
                "id": call.call_id,
                "provider_call_id": call.provider_call_id,
                "function": {
                    "name": call.name,
                    "arguments": call.arguments
                    if isinstance(call.arguments, str)
                    else json.dumps(call.arguments),
                },
            }
            for call in step.calls
        ]
        return step.content

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
        state = self.load(run_id)
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
        state.approval_requests[request.approval_id] = request
        state.approval_decisions[request.approval_id] = decision
        state.approval = None
        if decision.approved:
            state.status = "dispatching"
            state = self._save(state)
            self._dispatch(state, call, approved_tool=tool)
        else:
            self._record_result(state, {"status": "denied"})
            self._save(state)
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
        self,
        state: RunState,
        call: dict[str, Any],
        *,
        approved_tool: ToolBase | None = None,
    ) -> RunState:
        function = call["function"]
        name = function["name"]
        try:
            arguments = json.loads(function["arguments"])
            if not isinstance(arguments, dict):
                raise ValueError("Tool arguments must be an object")
            tool = (
                approved_tool
                if approved_tool is not None
                else self._available_tools()[name]
            )
        except (KeyError, TypeError, ValueError) as exc:
            self._record_result(state, {"error": str(exc)})
            return self._save(state)
        policy = (
            self.approval_policy(tool, arguments)
            if self.approval_policy
            else "allow"
        )
        if policy == "ask" and approved_tool is None:
            state.approval = self._approval(state, tool, arguments)
            state.approval_requests[state.approval.approval_id] = (
                state.approval
            )
            state.status = "approval_required"
            return self._save(state)
        if policy not in ("allow", "ask"):
            self._record_result(state, {"status": "denied"})
            return self._save(state)
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
        return self._save(state)

    def _record_result(self, state: RunState, value: Any) -> None:
        assert state.pending_call is not None
        call = state.pending_call
        if self.step_model is None:
            state.messages.append(
                {
                    "role": "tool",
                    "tool_call_id": call["id"],
                    "content": json.dumps(value, default=str),
                }
            )
        else:
            result_call = ProposedToolCall(
                call_id=call["id"],
                name=call["function"]["name"],
                arguments=call["function"]["arguments"],
                provider_call_id=call.get("provider_call_id"),
            )
            state.pending_results.append(
                {
                    "call": asdict(result_call),
                    "value": json.loads(json.dumps(value, default=str)),
                }
            )
            if not state.pending_calls:
                results = [
                    ToolStepResult(
                        ProposedToolCall(**item["call"]), item["value"]
                    )
                    for item in state.pending_results
                ]
                state.messages.extend(
                    self.step_model.format_tool_results(results)
                )
                state.pending_results.clear()
        state.pending_call = None
        state.status = "ready"
