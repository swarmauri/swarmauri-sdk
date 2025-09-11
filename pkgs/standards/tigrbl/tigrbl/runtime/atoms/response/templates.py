from __future__ import annotations
from functools import lru_cache
import logging
from typing import Any, Dict, Iterable, Optional, Tuple

from ....deps.starlette import Request
from ....deps.jinja import (
    Environment,
    FileSystemLoader,
    PackageLoader,
    ChoiceLoader,
    select_autoescape,
    TemplateNotFound,
)

logger = logging.getLogger("uvicorn")
if Environment is None:  # pragma: no cover - jinja2 not installed

    async def render_template(
        *,
        name: str,
        context: Dict[str, Any],
        search_paths: Iterable[str] = (),
        package: Optional[str] = None,
        auto_reload: bool = False,
        filters: Optional[Dict[str, Any]] = None,
        globals_: Optional[Dict[str, Any]] = None,
        request: Optional[Request] = None,
    ) -> str:
        logger.debug("Rendering template %s", name)
        raise RuntimeError("jinja2 is required for template rendering")

else:

    def _mk_loader(search_paths: Iterable[str], package: Optional[str]) -> ChoiceLoader:
        loaders = []
        if search_paths:
            loaders.append(FileSystemLoader(list(search_paths)))
        if package:
            loaders.append(PackageLoader(package_name=package))
        if not loaders:
            loaders.append(FileSystemLoader(["."]))
        return ChoiceLoader(loaders)

    @lru_cache(maxsize=64)
    def _get_env(
        search_paths_key: Tuple[str, ...],
        package: Optional[str],
        auto_reload: bool,
    ) -> Environment:
        env = Environment(
            loader=_mk_loader(search_paths_key, package),
            autoescape=select_autoescape(["html", "xml"]),
            auto_reload=auto_reload,
            enable_async=True,
        )
        return env

    async def render_template(
        *,
        name: str,
        context: Dict[str, Any],
        search_paths: Iterable[str] = (),
        package: Optional[str] = None,
        auto_reload: bool = False,
        filters: Optional[Dict[str, Any]] = None,
        globals_: Optional[Dict[str, Any]] = None,
        request: Optional[Request] = None,
    ) -> str:
        logger.debug("Rendering template %s", name)
        env = _get_env(tuple(search_paths), package, auto_reload)
        if filters:
            env.filters.update(filters)
        if globals_:
            env.globals.update(globals_)
        if request is not None:
            env.globals.setdefault("url_for", request.url_for)
            env.globals.setdefault("request", request)

        try:
            tmpl = env.get_template(name)
        except TemplateNotFound as e:  # pragma: no cover - passthrough
            raise FileNotFoundError(f"Template not found: {name}") from e

        return await tmpl.render_async(**context)


__all__ = ["render_template"]
