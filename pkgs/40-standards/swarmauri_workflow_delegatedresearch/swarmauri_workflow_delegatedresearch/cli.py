"""Run offline research with real keys, grants and agent execution."""

import argparse
import asyncio
import json
import tempfile
from dataclasses import asdict

from swarmauri_core.permissions import Permission
from swarmauri_workflow_documentassistant.demo import (
    ScriptedDocumentModel,
    demo_tokens,
)
from .DelegatedResearchWorkflow import DelegatedResearchWorkflow


async def run(directory):
    tokens, kid, issuer = await demo_tokens()
    workflow = DelegatedResearchWorkflow.create(
        directory,
        tokens=tokens,
        kid=kid,
        issuer=issuer,
        model_factory=ScriptedDocumentModel,
        authorize=lambda subject, permission: subject == "demo:alice",
        documents={"document:123": "Revenue increased by 12%."},
        permission=Permission("documents:read", "document:123", "demo"),
    )
    result = await workflow.run("demo:alice")
    return result, workflow.runtime.events


def main():
    parser = argparse.ArgumentParser(
        description="Offline fixture models with real delegation enforcement"
    )
    parser.parse_args()
    with tempfile.TemporaryDirectory() as directory:
        result, trace = asyncio.run(run(directory))
    print(json.dumps({"execution": asdict(result), "trace": trace}, indent=2))
    if result.status != "completed":
        raise SystemExit(1)


if __name__ == "__main__":
    main()
