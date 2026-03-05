from __future__ import annotations

import json as json_module
from dataclasses import dataclass
from http.cookies import SimpleCookie
from typing import Any, Mapping

from tigrbl_core._spec.response_spec import ResponseSpec, TemplateSpec

from ._headers_base import HeaderCookiesBase, HeadersBase


class ResponseBase(ResponseSpec):
    """Abstract-leaning response base with transport-friendly defaults."""

    def __init__(
        self,
        *,
        status_code: int = 200,
        headers: Mapping[str, str] | list[tuple[str, str]] | None = None,
        body: bytes | None = None,
        content: bytes | None = None,
        media_type: str | None = None,
        kind: str = "auto",
        envelope: bool | None = None,
        template: TemplateSpec | None = None,
        filename: str | None = None,
        download: bool | None = None,
        etag: str | None = None,
        cache_control: str | None = None,
        redirect_to: str | None = None,
    ) -> None:
        if body is not None and content is not None:
            raise TypeError(
                "ResponseBase: provide either 'body' or 'content', not both"
            )

        payload = (
            body if body is not None else (content if content is not None else b"")
        )
        normalized_headers = {
            str(key).lower(): str(value)
            for key, value in (
                headers.items() if hasattr(headers, "items") else (headers or [])
            )
        }

        super().__init__(
            kind=kind,
            media_type=media_type,
            status_code=status_code,
            headers=dict(normalized_headers),
            envelope=envelope,
            template=template,
            filename=filename,
            download=download,
            etag=etag,
            cache_control=cache_control,
            redirect_to=redirect_to,
        )
        self.status_code = status_code
        self.headers: HeadersBase = HeadersBase(normalized_headers)
        self.body = payload
        self.media_type = media_type

    @property
    def raw_headers(self) -> list[tuple[bytes, bytes]]:
        return [
            (k.encode("latin-1"), v.encode("latin-1")) for k, v in self.headers.items()
        ]

    @property
    def headers_map(self) -> HeadersBase:
        return self.headers

    @property
    def body_text(self) -> str:
        return self.body.decode("utf-8")

    def json_body(self) -> Any:
        if not self.body:
            return None
        return json_module.loads(self.body.decode("utf-8"))

    @property
    def cookies(self) -> HeaderCookiesBase:
        cookie = SimpleCookie()
        set_cookie = self.headers.get("set-cookie")
        if set_cookie:
            cookie.load(set_cookie)
        return HeaderCookiesBase(
            {name: morsel.value for name, morsel in cookie.items()}
        )


@dataclass
class TemplateBase(TemplateSpec):
    """Template configuration base for response rendering."""


__all__ = ["HeaderCookiesBase", "HeadersBase", "ResponseBase", "TemplateBase"]
