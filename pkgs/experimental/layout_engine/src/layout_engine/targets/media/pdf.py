from __future__ import annotations
from pathlib import Path
from typing import Mapping, Any
from ..base import IMediaTarget
from ...manifest.spec import Manifest
from .html import HtmlExporter

class PdfExporter(IMediaTarget):
    """
    CSS-aware PDF export using Playwright (headless Chromium).
    Produces an HTML sidecar with HtmlExporter, then prints to PDF.
    """
    def __init__(
        self,
        *,
        wait_until: str = "networkidle",
        print_background: bool = True,
        prefer_css_page_size: bool = True,
        timeout_ms: int = 30000,
        scale: float | None = None,                   # 0.1..2.0
        margin: Mapping[str, str] | None = None,     # {"top":"12mm", "right":"12mm", ...}
        format: str | None = None,                   # e.g., "A4", "Letter"
        width: str | None = None,                    # overrides format if provided (e.g., "1280px")
        height: str | None = None,
        html_title: str | None = None,
        css_links: list[str] | None = None,
        inline_css: str | None = None,
    ) -> None:
        self.wait_until = wait_until
        self.print_background = print_background
        self.prefer_css_page_size = prefer_css_page_size
        self.timeout_ms = timeout_ms
        self.scale = scale
        self.margin = dict(margin or {})
        self.format = format
        self.width = width
        self.height = height
        # Styling forwarded to HtmlExporter
        self.html_title = html_title
        self.css_links = list(css_links or [])
        self.inline_css = inline_css or ""

    def export(self, manifest: Manifest, *, out: str) -> str:
        out_path = Path(out)
        out_path.parent.mkdir(parents=True, exist_ok=True)

        # 1) Emit HTML next to target PDF
        html_path = out_path.with_suffix(".html")
        HtmlExporter(
            title=self.html_title or f"{manifest.kind}",
            css_links=self.css_links,
            inline_css=self.inline_css,
        ).export(manifest, out=str(html_path))

        # 2) Convert HTML → PDF with Playwright
        try:
            from playwright.sync_api import sync_playwright
        except Exception as e:
            raise RuntimeError(
                "Playwright is required for PdfExporter. Install with:
"
                "  uv add playwright
"
                "and run one-time:
"
                "  uv run playwright install chromium"
            ) from e

        with sync_playwright() as p:
            browser = p.chromium.launch()
            page = browser.new_page()
            page.goto(html_path.as_uri(), wait_until=self.wait_until, timeout=self.timeout_ms)

            pdf_kwargs: dict[str, Any] = {
                "path": str(out_path),
                "print_background": self.print_background,
                "prefer_css_page_size": self.prefer_css_page_size,
            }
            if self.scale is not None:
                pdf_kwargs["scale"] = self.scale
            if self.margin:
                pdf_kwargs["margin"] = dict(self.margin)
            if self.format:
                pdf_kwargs["format"] = self.format
            if self.width and self.height:
                pdf_kwargs["width"] = self.width
                pdf_kwargs["height"] = self.height

            page.pdf(**pdf_kwargs)
            browser.close()
        return str(out_path)
