import io
from importlib.metadata import entry_points
from pathlib import Path

import pytest

from swarmauri_tts_playht.cli import build_parser, main


pytestmark = pytest.mark.unit


class FakePlayHTTTS:
    """Record CLI inputs without calling PlayHT."""

    init_kwargs = {}
    prediction = {}

    def __init__(self, **kwargs) -> None:
        type(self).init_kwargs = kwargs

    def predict(self, text: str, audio_path: str) -> str:
        type(self).prediction = {"text": text, "audio_path": audio_path}
        return audio_path


class FakeTextToSpeechAgent:
    init_kwargs = {}
    prompt = ""

    def __init__(self, **kwargs) -> None:
        type(self).init_kwargs = kwargs

    def exec(self, prompt: str) -> str:
        type(self).prompt = prompt
        return self.init_kwargs["tts"].predict(
            text=prompt,
            audio_path=self.init_kwargs["output_path"],
        )


def test_parser_defaults() -> None:
    args = build_parser().parse_args(["Hello"])

    assert args.prompt == "Hello"
    assert args.voice_model == "Play3.0-mini"
    assert not hasattr(args, "agent")
    assert args.voice == "Adolfo"
    assert args.output == Path("output.mp3")


def test_console_script_entry_point() -> None:
    scripts = entry_points(group="console_scripts")
    command = next(
        point for point in scripts if point.name == "swarmauri-playht"
    )

    assert command.value == "swarmauri_tts_playht.cli:main"


def test_main_generates_audio_from_positional_prompt(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    monkeypatch.setenv("PLAYHT_API_KEY", "secret")
    monkeypatch.setenv("PLAYHT_USER_ID", "user")
    output = tmp_path / "audio" / "greeting.mp3"
    stdout = io.StringIO()

    result = main(
        [
            "Hello from Swarmauri",
            "--voice-model",
            "PlayHT2.0-turbo",
            "--output",
            str(output),
        ],
        input_stream=io.StringIO(),
        output_stream=stdout,
        tts_factory=FakePlayHTTTS,
        agent_factory=FakeTextToSpeechAgent,
    )

    assert result == 0
    assert FakePlayHTTTS.init_kwargs == {
        "api_key": "secret",
        "user_id": "user",
        "name": "PlayHT2.0-turbo",
        "voice": "Adolfo",
        "timeout": 600.0,
    }
    assert FakePlayHTTTS.prediction == {
        "text": "Hello from Swarmauri",
        "audio_path": str(output.resolve()),
    }
    assert output.parent.is_dir()
    assert f"Audio saved to {output.resolve()}" in stdout.getvalue()


def test_main_reads_piped_prompt(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("PLAYHT_API_KEY", "secret")
    monkeypatch.setenv("PLAYHT_USER_ID", "user")

    result = main(
        [],
        input_stream=io.StringIO("  Piped prompt\n"),
        output_stream=io.StringIO(),
        tts_factory=FakePlayHTTTS,
        agent_factory=FakeTextToSpeechAgent,
    )

    assert result == 0
    assert FakePlayHTTTS.prediction["text"] == "Piped prompt"


def test_main_reads_prompt_file(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    monkeypatch.setenv("PLAYHT_API_KEY", "secret")
    monkeypatch.setenv("PLAYHT_USER_ID", "user")
    prompt_file = tmp_path / "prompt.txt"
    prompt_file.write_text("Prompt from a file", encoding="utf-8")

    result = main(
        ["--prompt-file", str(prompt_file)],
        input_stream=io.StringIO(),
        output_stream=io.StringIO(),
        tts_factory=FakePlayHTTTS,
        agent_factory=FakeTextToSpeechAgent,
    )

    assert result == 0
    assert FakePlayHTTTS.prediction["text"] == "Prompt from a file"


def test_main_prompts_interactively(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("PLAYHT_API_KEY", "secret")
    monkeypatch.setenv("PLAYHT_USER_ID", "user")
    terminal_input = io.StringIO()
    terminal_input.isatty = lambda: True

    result = main(
        [],
        input_stream=terminal_input,
        output_stream=io.StringIO(),
        input_func=lambda _: "Interactive prompt",
        tts_factory=FakePlayHTTTS,
        agent_factory=FakeTextToSpeechAgent,
    )

    assert result == 0
    assert FakePlayHTTTS.prediction["text"] == "Interactive prompt"


def test_model_alias_generates_through_agent(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    monkeypatch.setenv("PLAYHT_API_KEY", "secret")
    monkeypatch.setenv("PLAYHT_USER_ID", "user")
    output = tmp_path / "agent.mp3"

    result = main(
        [
            "Agent prompt",
            "--model",
            "PlayHT1.0",
            "--output",
            str(output),
        ],
        input_stream=io.StringIO(),
        output_stream=io.StringIO(),
        tts_factory=FakePlayHTTTS,
        agent_factory=FakeTextToSpeechAgent,
    )

    assert result == 0
    assert FakePlayHTTTS.init_kwargs["name"] == "PlayHT1.0"
    assert FakeTextToSpeechAgent.init_kwargs["tts"].__class__ is FakePlayHTTTS
    assert FakeTextToSpeechAgent.init_kwargs["output_path"] == str(
        output.resolve()
    )
    assert FakeTextToSpeechAgent.prompt == "Agent prompt"


def test_main_reports_missing_credentials(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.delenv("PLAYHT_API_KEY", raising=False)
    monkeypatch.delenv("PLAYHT_USER_ID", raising=False)
    stderr = io.StringIO()

    result = main(
        ["Hello"],
        input_stream=io.StringIO(),
        error_stream=stderr,
        tts_factory=FakePlayHTTTS,
        agent_factory=FakeTextToSpeechAgent,
    )

    assert result == 2
    assert "PLAYHT_API_KEY and PLAYHT_USER_ID" in stderr.getvalue()


def test_main_rejects_conflicting_prompt_sources() -> None:
    stderr = io.StringIO()

    result = main(
        ["Hello", "--prompt-file", "prompt.txt"],
        input_stream=io.StringIO(),
        error_stream=stderr,
        tts_factory=FakePlayHTTTS,
        agent_factory=FakeTextToSpeechAgent,
    )

    assert result == 2
    assert "either PROMPT or --prompt-file" in stderr.getvalue()
