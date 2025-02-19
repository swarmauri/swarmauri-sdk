"""
external.py

This module contains functions for external integrations.
It provides:

  1. call_external_agent:
     - Sends a rendered prompt to an external agent (e.g., an LLM or language model API)
       and returns the generated content.
       
  2. chunk_content:
     - Optionally splits or processes the generated content into manageable chunks
       before saving.
       
Note:
  - The implementations here are placeholders. In a real-world scenario, you would
    replace them with calls to an actual external API (e.g., OpenAI, Hugging Face, etc.).
"""

import re
import os
from typing import Dict
from dotenv import load_dotenv

load_dotenv()

def call_external_agent(prompt: str, agent_env: Dict[str, str]) -> str:
    """
    Sends the rendered prompt to an external agent (e.g., a language model) and returns the generated content.
    
    Parameters:
      prompt (str): The prompt string to send to the external agent.
      agent_env (dict): A dictionary containing configuration for the external agent (e.g., API key, model name).
    
    Returns:
      str: The content generated by the external agent.
    
    Note:
      This is a placeholder implementation. Replace this with an actual API call to your LLM provider.
    """
    print(os.getenv("PROVIDER", agent_env.get("provider", None)))
    print(agent_env)
    from .O1Model import O1Model
    from .DeepInfraModel import DeepInfraModel 
    from .LlamaCppModel import LlamaCppModel
    from swarmauri.agents.RagAgent import RagAgent
    from swarmauri.vector_stores.TfidfVectorStore import TfidfVectorStore
    # For demonstration purposes, we simply log the prompt and return a dummy response.
    truncated_prompt = prompt + "..." if len(prompt) > 100 else prompt
    print(f"[INFO] Sending prompt to external agent: \n{truncated_prompt}")
    
    
    llm = DeepInfraModel(api_key=os.getenv("DEEPINFRA_API_KEY"), name="meta-llama/Meta-Llama-3.1-405B-Instruct")
    system_context = "You are a software developer."
    agent = RagAgent(llm=llm, vector_store=TfidfVectorStore(), system_context=system_context)

    if os.getenv("PROVIDER", agent_env.get("provider", None)) == "Openai":
        llm = O1Model(api_key=os.getenv("API_KEY"), name=agent_env.get("model_name", "o3-mini"))
        agent.llm = llm
        result = agent.exec(prompt, top_k=0)
    elif os.getenv("PROVIDER", agent_env.get("provider", None)) == "LlamaCpp":
        llm = LlamaCppModel(allowed_models=['localhost'], name="localhost")
        agent.llm = llm
        result = agent.exec(prompt, top_k=0, llm_kwargs={"max_tokens": 3000}) 
    else:
        agent.llm.name == agent_env.get("model_name", "meta-llama/Meta-Llama-3.1-405B-Instruct")
        result = agent.exec(prompt, top_k=0, llm_kwargs={"max_tokens": 3000})
        

    content = chunk_content(result)
    del agent
    return content
    # return ""


def chunk_content(full_content: str) -> str:
    """
    Optionally splits the content into chunks. Returns either a single chunk
    or the full content.
    """
    try:
        # Remove any unwanted <think> blocks
        pattern = r"<think>[\s\S]*?</think>"
        cleaned_text = re.sub(pattern, "", full_content).strip()

        from swarmauri.chunkers.MdSnippetChunker import MdSnippetChunker
        chunker = MdSnippetChunker()
        chunks = chunker.chunk_text(cleaned_text)
        if len(chunks) > 1:
            return cleaned_text
        try:
            return chunks[0][2]
        except IndexError:
            return cleaned_text
    except ImportError:
        print("[WARNING] MdSnippetChunker not found. Returning full content without chunking.")
        return full_content
    except Exception as e:
        print(f"[ERROR] Failed to chunk content: {e}")
        return full_content
