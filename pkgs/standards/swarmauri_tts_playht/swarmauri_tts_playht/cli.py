"""Generate speech from a user prompt with PlayHT."""

from __future__ import annotations

import argparse
import os
import sys
from collections.abc import Callable, Iterable
from pathlib import Path
from typing import Any, TextIO


DEFAULT_MODEL = "Play3.0-mini"
DEFAULT_OUTPUT = "output.mp3"
DEFAULT_VOICE = "Adolfo"
PLAYHT_MODELS = (
    "Play3.0-mini",
    "PlayHT2.0-turbo",
    "PlayHT1.0",
    "PlayHT2.0",
)


def build_parser() -> argparse.ArgumentParser:
    """Build the PlayHT command-line parser."""
    parser = argparse.ArgumentParser(
        prog="swarmauri-playht",
        description="Generate an audio file from text with PlayHT.",
    )
    parser.add_argument(
        "prompt",
        nargs="?",
        help="Text to speak; omit to read piped input or prompt interactively",
    )
    parser.add_argument(
        "-f",
        "--prompt-file",
        type=Path,
        help="Read the text to speak from a UTF-8 file",
    )
    parser.add_argument(
        "-o",
        "--output",
        type=Path,
        default=Path(DEFAULT_OUTPUT),
        help=f"Audio output path (default: {DEFAULT_OUTPUT})",
    )
    parser.add_argument(
        "--voice",
        default=DEFAULT_VOICE,
        help=f"PlayHT voice name (default: {DEFAULT_VOICE})",
    )
    parser.add_argument(
        "--voice-model",
        "--model",
        dest="voice_model",
        choices=PLAYHT_MODELS,
        default=DEFAULT_MODEL,
        help=f"PlayHT voice engine (default: {DEFAULT_MODEL})",
    )
    parser.add_argument(
        "--api-key",
        help="PlayHT API key (prefer the PLAYHT_API_KEY environment variable)",
    )
    parser.add_argument(
        "--user-id",
        help="PlayHT user ID (prefer the PLAYHT_USER_ID environment variable)",
    )
    parser.add_argument(
        "--timeout",
        type=float,
        default=600.0,
        help="Provider request timeout in seconds (default: 600)",
    )
    return parser


def read_prompt(
    args: argparse.Namespace,
    input_stream: TextIO,
    input_func: Callable[[str], str],
) -> str:
    """Read and validate prompt text from the selected input source."""
    if args.prompt is not None and args.prompt_file is not None:
        raise ValueError("Use either PROMPT or --prompt-file, not both.")

    if args.prompt_file is not None:
        try:
            prompt = args.prompt_file.read_text(encoding="utf-8")
        except OSError as exc:
            raise ValueError(
                f"Could not read prompt file '{args.prompt_file}': {exc}"
            ) from exc
    elif args.prompt is not None:
        prompt = args.prompt
    elif not input_stream.isatty():
        prompt = input_stream.read()
    else:
        prompt = input_func("Text to synthesize: ")

    prompt = prompt.strip()
    if not prompt:
        raise ValueError("The prompt cannot be empty.")
    return prompt


def resolve_credentials(args: argparse.Namespace) -> tuple[str, str]:
    """Resolve PlayHT credentials from flags or environment variables."""
    api_key = args.api_key or os.getenv("PLAYHT_API_KEY")
    user_id = args.user_id or os.getenv("PLAYHT_USER_ID")

    missing = []
    if not api_key:
        missing.append("PLAYHT_API_KEY")
    if not user_id:
        missing.append("PLAYHT_USER_ID")
    if missing:
        names = " and ".join(missing)
        raise ValueError(f"Missing PlayHT credentials: set {names}.")

    return api_key, user_id


def generate_audio(
    args: argparse.Namespace,
    prompt: str,
    tts_factory: Callable[..., Any] | None = None,
    agent_factory: Callable[..., Any] | None = None,
) -> Path:
    """Generate an audio file and return its absolute path."""
    if args.timeout <= 0:
        raise ValueError("--timeout must be greater than zero.")

    api_key, user_id = resolve_credentials(args)
    if tts_factory is None:
        from .PlayHTModel import PlayHTModel

        tts_factory = PlayHTModel

    output = args.output.expanduser().resolve()
    output.parent.mkdir(parents=True, exist_ok=True)
    tts = tts_factory(
        api_key=api_key,
        user_id=user_id,
        name=args.voice_model,
        voice=args.voice,
        timeout=args.timeout,
    )
    if agent_factory is None:
        from swarmauri_agent_texttospeech import TextToSpeechAgent

        agent_factory = TextToSpeechAgent
    agent = agent_factory(tts=tts, output_path=str(output))
    return Path(agent.exec(prompt))


def main(
    argv: Iterable[str] | None = None,
    *,
    input_stream: TextIO | None = None,
    output_stream: TextIO | None = None,
    error_stream: TextIO | None = None,
    input_func: Callable[[str], str] = input,
    tts_factory: Callable[..., Any] | None = None,
    agent_factory: Callable[..., Any] | None = None,
) -> int:
    """Run the PlayHT audio-generation command."""
    parser = build_parser()
    args = parser.parse_args(list(argv) if argv is not None else None)
    input_stream = input_stream or sys.stdin
    output_stream = output_stream or sys.stdout
    error_stream = error_stream or sys.stderr

    try:
        prompt = read_prompt(args, input_stream, input_func)
        audio_path = generate_audio(
            args,
            prompt,
            tts_factory=tts_factory,
            agent_factory=agent_factory,
        )
    except KeyboardInterrupt:
        print("Audio generation cancelled.", file=error_stream)
        return 130
    except ValueError as exc:
        print(f"Error: {exc}", file=error_stream)
        return 2
    except Exception as exc:
        print(f"PlayHT audio generation failed: {exc}", file=error_stream)
        return 1

    print(f"Audio saved to {audio_path}", file=output_stream)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
