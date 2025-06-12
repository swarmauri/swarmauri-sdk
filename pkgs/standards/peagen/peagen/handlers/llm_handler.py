from __future__ import annotations

from typing import Any, Dict

from peagen.core._external import _direct_call_external_agent
from peagen.models import Task


async def llm_handler(task_or_dict: Dict[str, Any] | Task) -> Dict[str, Any]:
    """Run an LLM call and return its content."""
    payload = task_or_dict.get("payload", {})
    args: Dict[str, Any] = payload.get("args", {})
    prompt: str = args.get("prompt", "")
    agent_env: Dict[str, Any] = args.get("agent_env", {})
    cfg = args.get("cfg")
    content = _direct_call_external_agent(prompt, agent_env, cfg)
    return {"content": content}
