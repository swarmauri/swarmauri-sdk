import json
from typing import List, Dict, Literal, Optional
from openai import OpenAI  # DeepInfra's client library
from swarmauri.core.typing import SubclassUnion

from swarmauri.standard.messages.base.MessageBase import MessageBase
from swarmauri.standard.messages.concrete.AgentMessage import AgentMessage
from swarmauri.standard.llms.base.LLMBase import LLMBase


class DeepInfraModel(LLMBase):
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
        "meta-llama/Llama-2-13b-chat-hf",
        "meta-llama/Llama-2-70b-chat-hf",
        "meta-llama/Llama-2-7b-chat-hf",
        "microsoft/Phi-3-medium-4k-instruct",
        "mistralai/Mistral-7B-Instruct-v0.1",
        "mistralai/Mistral-7B-Instruct-v0.2",
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
        """
        Format the messages into the format expected by the DeepInfra API.
        """
        message_properties = ["content", "role", "name"]
        formatted_messages = [
            message.model_dump(include=message_properties, exclude_none=True)
            for message in messages
        ]
        return formatted_messages

    def predict(
        self,
        conversation,
        temperature: float = 0.7,
        max_tokens: int = 256,
        enable_json: bool = False,
        stop: Optional[List[str]] = None,
        stream: bool = False,
    ):
        """
        Generate predictions using the DeepInfra model.

        Parameters:
        - conversation: Conversation object containing message history.
        - temperature (float): Sampling temperature.
        - max_tokens (int): Maximum number of tokens to generate.
        - enable_json (bool): Format response as JSON.
        - stop (Optional[List[str]]): List of stop sequences.
        - stream (bool): Whether to stream the response.

        Returns:
        - The updated conversation with the model's response.
        """
        formatted_messages = self._format_messages(conversation.history)
        client = OpenAI(
            api_key=self.api_key, base_url="https://api.deepinfra.com/v1/openai"
        )

        if stream:
            response = client.chat.completions.create(
                model=self.name,
                messages=formatted_messages,
                temperature=temperature,
                max_tokens=max_tokens,
                stop=stop,
                stream=True,
            )

            for event in response:
                if event.choices[0].finish_reason:
                    print(
                        "Completion finished. Reason:",
                        event.choices[0].finish_reason,
                    )
                else:
                    # Get the streamed content
                    message_content = event.choices[0].delta.get("content", "")
                    if message_content:
                        conversation.add_message(AgentMessage(content=message_content))
        else:
            response = client.chat.completions.create(
                model=self.name,
                messages=formatted_messages,
                temperature=temperature,
                max_tokens=max_tokens,
                stop=stop,
            )

            if enable_json:
                # Return the raw JSON response
                result = json.loads(response)
            else:
                result = response

            # Add the model's response to the conversation
            message_content = result["choices"][0]["message"]["content"]
            conversation.add_message(AgentMessage(content=message_content))

        return conversation
