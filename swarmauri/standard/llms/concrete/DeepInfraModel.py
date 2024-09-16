import json
from typing import List, Dict, Literal
from openai import OpenAI
from swarmauri.core.typing import SubclassUnion

from swarmauri.standard.messages.base.MessageBase import MessageBase
from swarmauri.standard.messages.concrete.AgentMessage import AgentMessage
from swarmauri.standard.llms.base.LLMBase import LLMBase


class DeepInfraModel(LLMBase):
    """
    Provider resources: https://deepinfra.com/models/text-generation

    """

    api_key: str
    allowed_models: List[str] = [
        "meta-llama/Meta-Llama-3.1-405B-Instruct",
        "meta-llama/Meta-Llama-3.1-70B-Instruct",
        "meta-llama/Meta-Llama-3.1-8B-Instruct",
        "mattshumer/Reflection-Llama-3.1-70B",
        "mistralai/Mistral-Nemo-Instruct-2407",
        "openbmb/MiniCPM-Llama3-V-2_5",
        "google/gemma-2-27b-it",
        "google/gemma-2-9b-it",
        "Sao10K/L3-70B-Euryale-v2.1",
        "meta-llama/Meta-Llama-3-70B-Instruct",
        "Qwen/Qwen2-72B-Instruct",
        "mistralai/Mistral-7B-Instruct-v0.3",
        "meta-llama/Meta-Llama-3-8B-Instruct",
        "mistralai/Mixtral-8x22B-Instruct-v0.1",
        "microsoft/WizardLM-2-8x22B",
        "microsoft/WizardLM-2-7B",
        "mistralai/Mixtral-8x7B-Instruct-v0.1",
        "lizpreciatior/lzlv_70b_fp16_hf",
        "01-ai/Yi-34B-Chat",
        "Austism/chronos-hermes-13b-v2",
        "Gryphe/MythoMax-L2-13b",
        "Gryphe/MythoMax-L2-13b-turbo",
        "HuggingFaceH4/zephyr-orpo-141b-A35b-v0.1",
        "Phind/Phind-CodeLlama-34B-v2",
        "Qwen/Qwen2-7B-Instruct",
        "Sao10K/L3.1-70B-Euryale-v2.2",
        "bigcode/starcoder2-15b",
        "bigcode/starcoder2-15b-instruct-v0.1",
        "codellama/CodeLlama-34b-Instruct-hf",
        "codellama/CodeLlama-70b-Instruct-hf",
        "cognitivecomputations/dolphin-2.6-mixtral-8x7b",
        "cognitivecomputations/dolphin-2.9.1-llama-3-70b",
        "databricks/dbrx-instruct",
        "deepinfra/airoboros-70b",
        "google/codegemma-7b-it",
        "google/gemma-1.1-7b-it",
        "mattshumer/Reflection-Llama-3.1-70B",
        "meta-llama/Llama-2-13b-chat-hf",
        "meta-llama/Llama-2-70b-chat-hf",
        "meta-llama/Llama-2-7b-chat-hf",
        "microsoft/Phi-3-medium-4k-instruct",
        "mistralai/Mistral-7B-Instruct-v0.1",
        "mistralai/Mistral-7B-Instruct-v0.2",
        "mistralai/Mixtral-8x22B-v0.1",
        "mistralai/Mixtral-8x22B-v0.1",
        "nvidia/Nemotron-4-340B-Instruct",
        "openchat/openchat-3.6-8b",
        "openchat/openchat_3.5",
    ]
    name: str = "Qwen/Qwen2-72B-Instruct"
    type: Literal["DeepInfraModel"] = "DeepInfraModel"

    def _format_messages(
        self, messages: List[SubclassUnion[MessageBase]]
    ) -> List[Dict[str, str]]:
        message_properties = ["content", "role", "name"]
        formatted_messages = [
            message.model_dump(include=message_properties, exclude_none=True)
            for message in messages
        ]
        return formatted_messages

    def predict(
        self,
        conversation,
        temperature=0.7,
        max_tokens=256,
        enable_json=False,
        stop: List[str] = None,
    ):
        """
        Generate predictions using the DeepInfra model.

        Parameters:
        - conversation: Conversation object containing message history.
        - temperature (float): Sampling temperature.
        - max_tokens (int): Maximum number of tokens to generate.
        - enable_json (bool): Format response as JSON.
        - stop (List[str]): List of stop sequences.

        Returns:
        - The updated conversation with the model's response.
        """
        formatted_messages = self._format_messages(conversation.history)
        client = OpenAI(
            api_key=self.api_key, base_url="https://api.deepinfra.com/v1/openai"
        )

        if enable_json:
            response = client.chat.completions.create(
                model=self.name,
                messages=formatted_messages,
                temperature=temperature,
                response_format={"type": "json_object"},
                max_tokens=max_tokens,
                top_p=1,
                frequency_penalty=0,
                presence_penalty=0,
                stop=stop,
            )
        else:
            response = client.chat.completions.create(
                model=self.name,
                messages=formatted_messages,
                temperature=temperature,
                max_tokens=max_tokens,
                top_p=1,
                frequency_penalty=0,
                presence_penalty=0,
                stop=stop,
            )

        result = json.loads(response.model_dump_json())
        message_content = result["choices"][0]["message"]["content"]
        conversation.add_message(AgentMessage(content=message_content))

        return conversation
