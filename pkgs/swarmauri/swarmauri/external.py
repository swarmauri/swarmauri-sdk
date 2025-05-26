# external.py
"""Utility functions for interacting with external LLMs and agents.

These helpers mirror similar functions in ``peagen`` but leverage the
Swarmauri plugin system to dynamically load components registered under
the ``swarmauri`` namespace.
"""
from __future__ import annotations

import importlib
import logging
import os
import re
from typing import Any, Dict, Optional

from colorama import init as colorama_init

from .plugin_citizenship_registry import PluginCitizenshipRegistry

colorama_init(autoreset=True)

logger = logging.getLogger(__name__)


def _load_registered_class(resource_name: str, namespace: str) -> type:
    """Resolve and import a class registered in ``PluginCitizenshipRegistry``.

    Parameters
    ----------
    resource_name:
        Either a fully qualified resource path (e.g. ``"swarmauri.llms.OpenAIModel"``)
        or just the class name within the given namespace.
    namespace:
        Namespace within ``swarmauri`` where the class is registered
        (e.g. ``"llms"`` or ``"agents"``).
    """
    if resource_name.startswith("swarmauri."):
        resource_path = resource_name
        class_name = resource_name.split(".")[-1]
    else:
        class_name = resource_name
        resource_path = f"swarmauri.{namespace}.{class_name}"

    module_path = PluginCitizenshipRegistry.get_external_module_path(resource_path)
    if not module_path:
        raise ImportError(f"No module registered for '{resource_path}'")

    module = importlib.import_module(module_path)
    try:
        return getattr(module, class_name)
    except AttributeError as exc:
        raise ImportError(
            f"Class '{class_name}' not found in module '{module_path}'"
        ) from exc


def call_external_llm(
    provider: str,
    api_key: Optional[str] = None,
    model_name: Optional[str] = None,
    timeout: float = 1200.0,
    **kwargs: Any,
):
    """Instantiate an LLM registered on the ``swarmauri`` namespace."""
    llm_cls = _load_registered_class(provider, "llms")

    init_args = {"timeout": timeout, **kwargs}
    if model_name:
        init_args["name"] = model_name
    if api_key:
        init_args["api_key"] = api_key

    return llm_cls(**init_args)


def chunk_content(full_content: str, logger: Optional[Any] = None) -> str:
    """Split content into a single code chunk if possible."""
    pattern = r"<think>[\s\S]*?</think>"
    cleaned_text = re.sub(pattern, "", full_content).strip()

    try:
        from swarmauri.chunkers.MdSnippetChunker import MdSnippetChunker

        chunker = MdSnippetChunker()
        chunks = chunker.chunk_text(cleaned_text)
        if len(chunks) > 1:
            if logger:
                logger.warning(
                    "MdSnippetChunker found more than one snippet, took the first."
                )
            return chunks[0][2]
        return chunks[0][2] if chunks else cleaned_text
    except ImportError:
        if logger:
            logger.warning(
                "MdSnippetChunker not found. Returning full content without chunking."
            )
        return cleaned_text
    except Exception as exc:  # pragma: no cover - defensive
        if logger:
            logger.error(f"[ERROR] Failed to chunk content: {exc}")
        return cleaned_text


def call_external_agent(
    prompt: str,
    agent_env: Dict[str, Any],
    logger: Optional[Any] = None,
) -> str:
    """Execute a prompt against an agent from the ``swarmauri`` namespace."""
    provider = os.getenv("PROVIDER") or agent_env.get("provider", "DeepInfraModel")
    api_key = os.getenv(f"{provider.upper()}_API_KEY") or agent_env.get("api_key")
    model_name = agent_env.get("model_name")
    max_tokens = int(agent_env.get("max_tokens", 8192))

    if logger:
        truncated_prompt = prompt[:140] + "..." if len(prompt) > 140 else prompt
        logger.info(f"Sending prompt to external llm: \n\t{truncated_prompt}\n")
        logger.debug(f"Agent env: {agent_env}")

    llm = call_external_llm(provider, api_key=api_key, model_name=model_name)

    agent_class_name = agent_env.get("agent_class", "QAAgent")
    agent_cls = _load_registered_class(agent_class_name, "agents")

    try:
        agent = agent_cls(llm=llm)
    except Exception as exc:
        raise ImportError(
            f"Failed to instantiate agent '{agent_class_name}': {exc}"
        ) from exc

    system_context = agent_env.get("system_context", "You are a software developer.")
    try:
        from swarmauri.messages.SystemMessage import SystemMessage

        agent.conversation.system_context = SystemMessage(content=system_context)
    except Exception:  # pragma: no cover - if conversation not available
        pass

    try:
        result = agent.exec(prompt, llm_kwargs={"max_tokens": max_tokens})
    except KeyboardInterrupt:
        raise KeyboardInterrupt("'Interrupted...'")

    content = chunk_content(result, logger)
    del agent
    return content
