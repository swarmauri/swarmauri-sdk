"""Explicit offline fixtures; real signing, stores and authorization."""

import json
from swarmauri_keyprovider_local import LocalKeyProvider
from swarmauri_core.key_providers.types import (
    KeySpec,
    KeyAlg,
    KeyClass,
    KeyUse,
    ExportPolicy,
)
from swarmauri_tokens_jwt import JWTTokenService


class ScriptedDocumentModel:
    """Deterministic model fixture, not an identity or token provider."""

    def __init__(self, resource):
        self.resource = resource

    def __call__(self, messages, tools):
        results = [m for m in messages if m.get("role") == "tool"]
        if results:
            return {
                "role": "assistant",
                "content": "Document result: " + results[-1]["content"],
            }
        return {
            "role": "assistant",
            "content": None,
            "tool_calls": [
                {
                    "id": "read-document",
                    "type": "function",
                    "function": {
                        "name": "ReadDocument",
                        "arguments": json.dumps({"resource": self.resource}),
                    },
                }
            ],
        }


async def demo_tokens():
    """Generate ephemeral local keys; production hosts inject durable keys."""
    keys = LocalKeyProvider()
    ref = await keys.create_key(
        KeySpec(
            klass=KeyClass.asymmetric,
            alg=KeyAlg.RSA_PSS_SHA256,
            uses=(KeyUse.SIGN, KeyUse.VERIFY),
            export_policy=ExportPolicy.SECRET_WHEN_ALLOWED,
            size_bits=2048,
        )
    )
    issuer = "https://reference.local"
    return JWTTokenService(keys, default_issuer=issuer), ref.kid, issuer
