import argparse
import subprocess
import sys


def run_gen_api(
    manifest: str = "api_manifest.yaml",
    docs_dir: str = ".",
    mkdocs_yml: str = "mkdocs.yml",
    api_output_dir: str = "api",
    changed_only: bool = False,
) -> None:
    """Run the API docs generation script."""
    cmd = [
        sys.executable,
        "-m",
        "docsite_builder.scripts.gen_api",
        "--manifest",
        manifest,
        "--docs-dir",
        docs_dir,
        "--mkdocs-yml",
        mkdocs_yml,
        "--api-output-dir",
        api_output_dir,
    ]
    if changed_only:
        cmd.append("--changed-only")
    subprocess.run(cmd, check=True)


def run_mkdocs_serve(
    docs_dir: str = ".",
    mkdocs_yml: str = "mkdocs.yml",
    dev_addr: str = "0.0.0.0:8000",
) -> None:
    """Launch a MkDocs development server."""
    cmd = ["mkdocs", "serve", "-f", mkdocs_yml, "-a", dev_addr]
    subprocess.run(cmd, check=True, cwd=docs_dir)


def run_gen_readmes(docs_dir: str = ".") -> None:
    """Run the README generation script."""
    cmd = [sys.executable, "-m", "docsite_builder.scripts.gen_readmes"]
    subprocess.run(cmd, check=True, cwd=docs_dir)


def main() -> None:
    parser = argparse.ArgumentParser(prog="docsite-builder")
    sub = parser.add_subparsers(dest="command", required=True)

    gen = sub.add_parser("generate", help="Generate API docs from a manifest")
    gen.add_argument("--manifest", default="api_manifest.yaml")
    gen.add_argument("--docs-dir", default=".")
    gen.add_argument("--mkdocs-yml", default="mkdocs.yml")
    gen.add_argument("--api-output-dir", default="api")
    gen.add_argument("--changed-only", action="store_true")
    gen.set_defaults(
        func=lambda args: run_gen_api(
            manifest=args.manifest,
            docs_dir=args.docs_dir,
            mkdocs_yml=args.mkdocs_yml,
            api_output_dir=args.api_output_dir,
            changed_only=args.changed_only,
        )
    )

    readmes = sub.add_parser("readmes", help="Generate documentation from README files")
    readmes.add_argument("--docs-dir", default=".")
    readmes.set_defaults(func=lambda args: run_gen_readmes(docs_dir=args.docs_dir))

    serve = sub.add_parser("serve", help="Serve the documentation with MkDocs")
    serve.add_argument("--docs-dir", default=".")
    serve.add_argument("--mkdocs-yml", default="mkdocs.yml")
    serve.add_argument("--dev-addr", default="0.0.0.0:8000")
    serve.add_argument("--manifest", default="api_manifest.yaml")
    serve.add_argument("--api-output-dir", default="api")
    serve.add_argument("--changed-only", action="store_true")
    serve.add_argument(
        "--generate",
        action="store_true",
        help="Generate API docs before serving",
    )

    def serve_cmd(args: argparse.Namespace) -> None:
        if args.generate:
            run_gen_api(
                manifest=args.manifest,
                docs_dir=args.docs_dir,
                mkdocs_yml=args.mkdocs_yml,
                api_output_dir=args.api_output_dir,
                changed_only=args.changed_only,
            )
        run_mkdocs_serve(
            docs_dir=args.docs_dir,
            mkdocs_yml=args.mkdocs_yml,
            dev_addr=args.dev_addr,
        )

    serve.set_defaults(func=serve_cmd)

    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
