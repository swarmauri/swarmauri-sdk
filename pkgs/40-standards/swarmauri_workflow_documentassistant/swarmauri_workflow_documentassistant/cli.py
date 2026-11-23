"""Run the explicitly offline reference composition."""

import argparse
import asyncio
import tempfile
from dataclasses import asdict
import json

from swarmauri_core.permissions import Permission
from .DocumentAssistantWorkflow import DocumentAssistantWorkflow
from .demo import ScriptedDocumentModel, demo_tokens


async def run(directory):
    tokens, kid, issuer = await demo_tokens()
    workflow = DocumentAssistantWorkflow.create(
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
        description="Offline fixture model with real JWT/grant verification"
    )
    parser.parse_args()
    with tempfile.TemporaryDirectory() as directory:
        result, trace = asyncio.run(run(directory))
    print(json.dumps({"execution": asdict(result), "trace": trace}, indent=2))
    if result.status != "completed":
        raise SystemExit(1)


if __name__ == "__main__":
    main()
