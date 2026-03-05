from __future__ import annotations

from http.cookies import SimpleCookie
from typing import Any, Mapping

from tigrbl_base._base._response_base import ResponseBase, TemplateBase

from ._headers import HeaderCookies, Headers


class _JSONDualMethod:
    def __get__(self, obj: "Response" | None, owner: type["Response"]):
        if obj is None:

            def _factory(
                data: Any,
                status_code: int = 200,
                headers: Mapping[str, str] | None = None,
            ) -> "Response":
                return owner.from_json(data, status_code=status_code, headers=headers)

            return _factory

        return obj.json_body


class Template(TemplateBase):
    """Concrete template configuration used at runtime."""


class Response(ResponseBase):
    """Concrete response configuration used at runtime."""

    json = _JSONDualMethod()

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
        template: TemplateBase | None = None,
        filename: str | None = None,
        download: bool | None = None,
        etag: str | None = None,
        cache_control: str | None = None,
        redirect_to: str | None = None,
    ) -> None:
        super().__init__(
            status_code=status_code,
            headers=headers,
            body=body,
            content=content,
            media_type=media_type,
            kind=kind,
            envelope=envelope,
            template=template,
            filename=filename,
            download=download,
            etag=etag,
            cache_control=cache_control,
            redirect_to=redirect_to,
        )
        self.headers = Headers(headers or {})

    @property
    def headers_map(self) -> Headers:
        return self.headers

    @property
    def cookies(self) -> HeaderCookies:
        parsed = SimpleCookie()
        for name, value in self.headers.items():
            if name == "set-cookie":
                parsed.load(value)
        return HeaderCookies({name: morsel.value for name, morsel in parsed.items()})

    @staticmethod
    def _status_text(code: int) -> str:
        return {
            200: "OK",
            201: "Created",
            205: "Reset Content",
            204: "No Content",
            301: "Moved Permanently",
            302: "Found",
            307: "Temporary Redirect",
            308: "Permanent Redirect",
            400: "Bad Request",
            401: "Unauthorized",
            403: "Forbidden",
            404: "Not Found",
            405: "Method Not Allowed",
            422: "Unprocessable Entity",
            500: "Internal Server Error",
        }.get(code, "OK")

    def status_line(self) -> str:
        return f"{self.status_code} {self._status_text(self.status_code)}"

    def set_cookie(
        self,
        key: str,
        value: str,
        *,
        path: str = "/",
        domain: str | None = None,
        secure: bool = False,
        httponly: bool = False,
        samesite: str | None = None,
        max_age: int | None = None,
        expires: str | None = None,
    ) -> None:
        cookie = SimpleCookie()
        cookie[key] = value
        morsel = cookie[key]
        morsel["path"] = path
        if domain is not None:
            morsel["domain"] = domain
        if secure:
            morsel["secure"] = True
        if httponly:
            morsel["httponly"] = True
        if samesite is not None:
            morsel["samesite"] = samesite
        if max_age is not None:
            morsel["max-age"] = str(max_age)
        if expires is not None:
            morsel["expires"] = expires
        self.headers["set-cookie"] = cookie.output(header="").strip()

    @classmethod
    def html(
        cls,
        html: str,
        status_code: int = 200,
        headers: Mapping[str, str] | None = None,
    ) -> "Response":
        payload = html.encode("utf-8")
        hdrs = [("content-type", "text/html; charset=utf-8")]
        for key, value in (headers or {}).items():
            hdrs.append((key.lower(), value))
        return cls(
            status_code=status_code, headers=hdrs, body=payload, media_type="text/html"
        )

    @classmethod
    def text(
        cls,
        text: str,
        status_code: int = 200,
        headers: Mapping[str, str] | None = None,
    ) -> "Response":
        payload = text.encode("utf-8")
        hdrs = [("content-type", "text/plain; charset=utf-8")]
        for key, value in (headers or {}).items():
            hdrs.append((key.lower(), value))
        return cls(
            status_code=status_code, headers=hdrs, body=payload, media_type="text/plain"
        )

    @classmethod
    def from_json(
        cls,
        data: Any,
        status_code: int = 200,
        headers: Mapping[str, str] | None = None,
    ) -> "Response":
        import json as json_module

        payload = json_module.dumps(
            data, ensure_ascii=False, separators=(",", ":"), default=str
        ).encode("utf-8")
        hdrs = [("content-type", "application/json; charset=utf-8")]
        for key, value in (headers or {}).items():
            hdrs.append((key.lower(), value))
        return cls(
            status_code=status_code,
            headers=hdrs,
            body=payload,
            media_type="application/json",
        )


__all__ = ["Template", "Response"]
