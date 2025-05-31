from __future__ import annotations

import os
import uuid
from pathlib import Path

import typer

from peagen.cli_common import global_cli_options
from peagen.llm.ensemble import LLMEnsemble
from peagen.prompt_sampler import PromptSampler
from peagen.mutators.mutate_patch import apply_patch
from peagen.queue import make_queue
from peagen.queue.model import Task, TaskKind

mutate_app = typer.Typer(help="Mutate source with LLM")


def run_mutate(
    target_file: str,
    entry_fn: str,
    output: str,
    backend: str | None,
    queue: bool,
) -> None:
    """Generate a mutated variant of ``target_file`` using an LLM."""

    parent_src = Path(target_file).read_text()

    if queue:
        queue_url = os.environ.get("QUEUE_URL", "stub://")
        provider = "redis" if queue_url.startswith("redis") else "stub"
        q = make_queue(provider, url=queue_url)
        tid = f"mut-{uuid.uuid4().hex[:8]}"
        payload = {
            "parent_src": parent_src,
            "entry_sig": entry_fn,
            "child_path": str(Path(output).resolve()),
        }
        task = Task(TaskKind.MUTATE, tid, payload, requires={"llm", "cpu"})
        q.enqueue(task)
        typer.echo(f"enqueued {task.id} -> {output}")
        return

    prompt = PromptSampler.build_mutate_prompt(parent_src, [], entry_fn)
    diff = LLMEnsemble.generate(prompt, backend or "auto")
    child_src = apply_patch(parent_src, diff)
    Path(output).write_text(child_src)
    typer.echo(f"wrote mutated file to {output}")


@mutate_app.command("mutate")
@global_cli_options
def mutate_cmd(
    ctx: typer.Context,
    target_file: str = typer.Option(..., "--target-file", help="Source file"),
    entry_fn: str = typer.Option(..., "--entry-fn", help="Entry function"),
    output: str = typer.Option("target_mutated.py", "--output", help="Output file"),
    backend: str | None = typer.Option(None, "--backend", help="LLM backend"),
    queue: bool = typer.Option(True, "--queue/--sync", help="Queue tasks"),
) -> None:
    run_mutate(target_file, entry_fn, output, backend, queue)
