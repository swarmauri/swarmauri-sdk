from __future__ import annotations

import asyncio
import warnings
from collections.abc import Mapping
from typing import Any, Literal
from urllib.parse import unquote, urlsplit

from pydantic import Field
from swarmauri_base.ComponentBase import ComponentBase, ResourceTypes
from swarmauri_base.transports.bidirectional.BidirectionalStreamClientBase import (  # noqa: E501
    BidirectionalStreamClientBase,
)

from .AwsEventStreamConnection import AwsEventStreamConnection


@ComponentBase.register_type(
    BidirectionalStreamClientBase, "AwsEventStreamClient"
)
class AwsEventStreamClient(BidirectionalStreamClientBase):
    """Open Bedrock bidirectional streams through AWS's Smithy SDK."""

    region: str = "us-east-1"
    sdk_client_factory: Any = Field(default=None, exclude=True)
    type: Literal["AwsEventStreamClient"] = "AwsEventStreamClient"
    resource: str = Field(default=ResourceTypes.TRANSPORT.value, frozen=True)

    @staticmethod
    def _run_sync(awaitable: Any) -> Any:
        try:
            asyncio.get_running_loop()
        except RuntimeError:
            return asyncio.run(awaitable)
        close = getattr(awaitable, "close", None)
        if close is not None:
            close()
        raise RuntimeError("Use aconnect() inside an event loop")

    @staticmethod
    def _model_from_endpoint(endpoint: str) -> str | None:
        path = urlsplit(endpoint).path
        prefix = "/model/"
        suffix = "/invoke-with-bidirectional-stream"
        if path.startswith(prefix) and path.endswith(suffix):
            return unquote(path[len(prefix) : -len(suffix)])
        return None

    @staticmethod
    def _profile_credentials(profile: str) -> dict[str, str]:
        from botocore.session import Session

        credentials = Session(profile=profile).get_credentials()
        if credentials is None:
            raise ValueError(f"AWS profile {profile!r} has no credentials")
        frozen = credentials.get_frozen_credentials()
        result = {
            "aws_access_key_id": frozen.access_key,
            "aws_secret_access_key": frozen.secret_key,
        }
        if frozen.token:
            result["aws_session_token"] = frozen.token
        return result

    @staticmethod
    def _default_sdk():
        try:
            from aws_sdk_bedrock_runtime.config import Config
            from aws_sdk_bedrock_runtime.models import (
                InvokeModelWithBidirectionalStreamOperationInput,
            )
        except ImportError as exc:  # pragma: no cover - Python < 3.12
            raise RuntimeError(
                "AWS Bedrock bidirectional transport requires Python 3.12 "
                "and aws-sdk-bedrock-runtime"
            ) from exc
        try:
            from aws_sdk_bedrock_runtime.client import (
                AsyncBedrockRuntimeClient,
            )

            client_type = AsyncBedrockRuntimeClient
        except ImportError:
            with warnings.catch_warnings():
                warnings.simplefilter("ignore", DeprecationWarning)
                from aws_sdk_bedrock_runtime.client import (
                    BedrockRuntimeClient,
                )

            client_type = BedrockRuntimeClient
        return (
            client_type,
            Config,
            (InvokeModelWithBidirectionalStreamOperationInput),
        )

    def connect(
        self,
        endpoint: str,
        *,
        headers: Mapping[str, str] | None = None,
        **kwargs: Any,
    ) -> AwsEventStreamConnection:
        return self._run_sync(
            self.aconnect(endpoint, headers=headers, **kwargs)
        )

    async def aconnect(
        self,
        endpoint: str,
        *,
        headers: Mapping[str, str] | None = None,
        **kwargs: Any,
    ) -> AwsEventStreamConnection:
        if headers:
            raise ValueError(
                "Custom headers are unsupported; the AWS SDK owns "
                "SigV4 headers"
            )

        model_id = kwargs.pop("model_id", None) or self._model_from_endpoint(
            endpoint
        )
        if not model_id:
            raise ValueError("model_id is required for a Bedrock event stream")

        region = str(kwargs.pop("region", None) or self.region)
        profile = kwargs.pop("profile", None)
        credential_options = {
            key: kwargs.pop(key)
            for key in (
                "aws_access_key_id",
                "aws_secret_access_key",
                "aws_session_token",
            )
            if kwargs.get(key) is not None
        }
        if ("aws_access_key_id" in credential_options) != (
            "aws_secret_access_key" in credential_options
        ):
            raise ValueError(
                "aws_access_key_id and aws_secret_access_key must be "
                "provided together"
            )
        if profile and not credential_options:
            credential_options = await asyncio.to_thread(
                self._profile_credentials, str(profile)
            )
        if kwargs:
            names = ", ".join(sorted(kwargs))
            raise TypeError(f"Unsupported AWS event stream options: {names}")

        client_type, config_type, input_type = self._default_sdk()
        split = urlsplit(endpoint)
        if split.scheme not in {"http", "https"} or not split.netloc:
            raise ValueError("endpoint must be an absolute HTTP or HTTPS URL")
        endpoint_uri = f"{split.scheme}://{split.netloc}"
        config = config_type(
            region=region,
            endpoint_uri=endpoint_uri,
            **credential_options,
        )
        factory = self.sdk_client_factory or client_type
        client = factory(config)
        stream = client.invoke_model_with_bidirectional_stream(
            input_type(model_id=str(model_id))
        )
        return AwsEventStreamConnection.from_stream(stream)
