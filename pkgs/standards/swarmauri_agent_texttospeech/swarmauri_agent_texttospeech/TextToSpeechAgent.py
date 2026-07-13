"""Provide a stateless agent for text-to-speech synthesis."""

from __future__ import annotations

import asyncio
from collections.abc import Sequence
from pathlib import Path
from typing import Any, Dict, List, Literal, Optional, Union

from pydantic import ConfigDict, Field

from swarmauri_base.ComponentBase import ComponentBase, SubclassUnion
from swarmauri_base.agents.AgentBase import AgentBase
from swarmauri_base.tts.TTSBase import TTSBase
from swarmauri_core.messages.IMessage import IMessage


@ComponentBase.register_type(AgentBase, "TextToSpeechAgent")
class TextToSpeechAgent(AgentBase):
    """Synthesize each input independently without memory or system context."""

    llm: None = Field(default=None, exclude=True)
    llm_kwargs: None = Field(default=None, exclude=True)
    tts: SubclassUnion[TTSBase]
    output_path: str = "output.mp3"
    tts_kwargs: Dict[str, Any] = Field(default_factory=dict)
    model_config = ConfigDict(extra="forbid", arbitrary_types_allowed=True)
    type: Literal["TextToSpeechAgent"] = "TextToSpeechAgent"

    def model_post_init(self, __context: Any) -> None:
        """Rehydrate a serialized TTS component through its base registry."""
        if not isinstance(self.tts, dict):
            return
        type_name = self.tts.get("type")
        registry = TTSBase._registry.get("TTSBase", {})
        tts_class = registry.get("subtypes", {}).get(type_name)
        if tts_class is None and type_name == "TTSBase":
            tts_class = registry.get("model_cls", TTSBase)
        if tts_class is not None:
            self.tts = tts_class.model_validate(self.tts)

    def exec(
        self,
        input_str: Optional[Union[str, IMessage]] = "",
        llm_kwargs: Optional[Dict] = None,
        *,
        audio_path: Optional[str] = None,
        tts_kwargs: Optional[Dict[str, Any]] = None,
    ) -> str:
        """Synthesize one fresh input and return the generated audio path."""
        text = self._input_text(input_str)
        kwargs = self._merge_tts_kwargs(llm_kwargs, tts_kwargs)
        return self.tts.predict(
            text=text,
            audio_path=audio_path or self.output_path,
            **kwargs,
        )

    async def aexec(
        self,
        input_str: Optional[Union[str, IMessage]] = "",
        llm_kwargs: Optional[Dict] = None,
        *,
        audio_path: Optional[str] = None,
        tts_kwargs: Optional[Dict[str, Any]] = None,
    ) -> str:
        """Asynchronously synthesize one fresh input."""
        text = self._input_text(input_str)
        kwargs = self._merge_tts_kwargs(llm_kwargs, tts_kwargs)
        return await self.tts.apredict(
            text=text,
            audio_path=audio_path or self.output_path,
            **kwargs,
        )

    def batch(
        self,
        inputs: List[Union[str, IMessage]],
        llm_kwargs: Optional[Dict] = None,
        *,
        audio_paths: Optional[Sequence[str]] = None,
        tts_kwargs: Optional[Dict[str, Any]] = None,
    ) -> List[str]:
        """Synthesize independent inputs to distinct output paths."""
        paths = self._resolve_batch_paths(len(inputs), audio_paths)
        return [
            self.exec(
                input_data,
                llm_kwargs=llm_kwargs,
                audio_path=path,
                tts_kwargs=tts_kwargs,
            )
            for input_data, path in zip(inputs, paths)
        ]

    async def abatch(
        self,
        inputs: List[Union[str, IMessage]],
        llm_kwargs: Optional[Dict] = None,
        *,
        audio_paths: Optional[Sequence[str]] = None,
        tts_kwargs: Optional[Dict[str, Any]] = None,
    ) -> List[str]:
        """Concurrently synthesize independent inputs."""
        paths = self._resolve_batch_paths(len(inputs), audio_paths)
        return await asyncio.gather(
            *[
                self.aexec(
                    input_data,
                    llm_kwargs=llm_kwargs,
                    audio_path=path,
                    tts_kwargs=tts_kwargs,
                )
                for input_data, path in zip(inputs, paths)
            ]
        )

    @staticmethod
    def _input_text(input_data: Optional[Union[str, IMessage]]) -> str:
        if isinstance(input_data, str):
            text = input_data
        elif isinstance(input_data, IMessage):
            text = input_data.content
        else:
            raise TypeError(
                "Input must be text or an IMessage with text content."
            )

        if not isinstance(text, str):
            raise TypeError("Text-to-speech input content must be a string.")
        text = text.strip()
        if not text:
            raise ValueError("Text-to-speech input cannot be empty.")
        return text

    def _merge_tts_kwargs(
        self,
        compatibility_kwargs: Optional[Dict],
        call_kwargs: Optional[Dict[str, Any]],
    ) -> Dict[str, Any]:
        kwargs = dict(self.tts_kwargs)
        kwargs.update(compatibility_kwargs or {})
        kwargs.update(call_kwargs or {})
        reserved = {"text", "audio_path"}.intersection(kwargs)
        if reserved:
            names = ", ".join(sorted(reserved))
            raise ValueError(
                f"TTS keyword arguments cannot override: {names}."
            )
        return kwargs

    def _resolve_batch_paths(
        self,
        count: int,
        audio_paths: Optional[Sequence[str]],
    ) -> List[str]:
        if audio_paths is not None:
            paths = list(audio_paths)
            if len(paths) != count:
                raise ValueError(
                    "audio_paths must match the number of inputs."
                )
            return paths

        base = Path(self.output_path)
        suffix = base.suffix or ".mp3"
        return [
            str(base.with_name(f"{base.stem}_{index}{suffix}"))
            for index in range(count)
        ]
