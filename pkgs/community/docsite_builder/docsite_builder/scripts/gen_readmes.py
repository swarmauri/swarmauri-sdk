from __future__ import annotations

from pathlib import Path

import mkdocs_gen_files
from mkdocs_gen_files import Nav

# Roots to scan; adapt to your repo
ROOTS = ("pkgs", "packages", "apps", "libs", "services")

# Static assets we'll copy alongside README content (allowlist)
STATIC_EXTS = {
    ".png",
    ".jpg",
    ".jpeg",
    ".gif",
    ".svg",
    ".webp",
    ".ico",
    ".bmp",
    ".css",
    ".js",
    ".json",
    ".txt",
    ".pdf",
    ".toml",
    ".yaml",
    ".yml",
}


def main() -> None:
    root = Path.cwd()
    nav = Nav()

    def write_binary(src: Path, dest: Path) -> None:
        with mkdocs_gen_files.open(dest.as_posix(), "wb") as out:
            out.write(src.read_bytes())

    def write_text(src: Path, dest: Path) -> None:
        with mkdocs_gen_files.open(dest.as_posix(), "w", encoding="utf-8") as out:
            out.write(src.read_text(encoding="utf-8"))

    for base in ROOTS:
        base_path = root / base
        if not base_path.exists():
            continue

        for readme in base_path.rglob("README.md"):
            rel_from_repo = readme.relative_to(root)
            doc_dir_parts = rel_from_repo.parts[:-1]
            out_md = Path(*doc_dir_parts) / "index.md"

            write_text(readme, out_md)
            mkdocs_gen_files.set_edit_path(out_md.as_posix(), readme.as_posix())

            nav[doc_dir_parts] = out_md.as_posix()

            for p in readme.parent.rglob("*"):
                if (
                    p.is_file()
                    and p.suffix.lower() in STATIC_EXTS
                    and p.name != "index.md"
                ):
                    out_asset = Path(*p.relative_to(root).parts)
                    write_binary(p, out_asset)

    with mkdocs_gen_files.open("SUMMARY.md", "w") as f:
        f.writelines(nav.build_literate_nav())


if __name__ == "__main__":
    main()
