import argparse
import json
import logging
from typing import Iterable, Optional

from rich.console import Console
from rich.logging import RichHandler
from rich.table import Table

from .GitVectorStore import GitVectorStore


LOGGER = logging.getLogger("swarmauri.git_vectorstore")
CONSOLE = Console()


def configure_logging(verbose: bool = False) -> None:
    level = logging.DEBUG if verbose else logging.INFO
    logging.basicConfig(
        level=level,
        format="%(message)s",
        datefmt="[%X]",
        handlers=[RichHandler(rich_tracebacks=True, markup=True)],
        force=True,
    )


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Semantic retrieval over git commits and git log records."
    )
    parser.add_argument(
        "--repo-path", default=".", help="Path to the git repository"
    )
    parser.add_argument(
        "--ref",
        default="all",
        help="Git ref to index. Use 'all' for all refs or 'HEAD' for the current branch.",
    )
    parser.add_argument(
        "--document-kind",
        action="append",
        choices=["commit", "log"],
        dest="document_kinds",
        help="Document kinds to index. Repeat to include both.",
    )
    parser.add_argument("--max-commits", type=int, help="Cap the number of indexed commits")
    parser.add_argument(
        "--no-diff-stats",
        action="store_true",
        help="Exclude diff stat text from commit documents",
    )
    parser.add_argument("--verbose", action="store_true", help="Enable debug logging")

    subparsers = parser.add_subparsers(dest="command", required=True)

    query_parser = subparsers.add_parser("query", help="Query the indexed git documents")
    query_parser.add_argument("--query", required=True, help="Query text")
    query_parser.add_argument("--top-k", type=int, default=5, help="Number of hits to return")
    query_parser.add_argument("--json", action="store_true", help="Emit JSON output")

    show_parser = subparsers.add_parser("show", help="Print a document by id")
    show_parser.add_argument("--document-id", required=True, help="Document id to display")

    return parser


def build_store(args: argparse.Namespace) -> GitVectorStore:
    document_kinds = tuple(args.document_kinds or ("commit", "log"))
    scope = "all_refs" if args.ref == "all" else ("head" if args.ref == "HEAD" else "ref")
    ref = None if args.ref in {"all", "HEAD"} else args.ref
    store = GitVectorStore(
        repo_path=args.repo_path,
        scope=scope,
        ref=ref,
        document_kinds=document_kinds,
        include_diff_stats=not args.no_diff_stats,
        max_commits=args.max_commits,
    )
    LOGGER.info(
        "Building git vector index [bold cyan](ref=%s, kinds=%s)[/bold cyan]",
        args.ref,
        ",".join(document_kinds),
    )
    store.build_index()
    LOGGER.info("Indexed [bold green]%s[/bold green] documents", len(store.documents))
    return store


def render_query_results(store: GitVectorStore, query: str, top_k: int, as_json: bool) -> int:
    LOGGER.info("Running retrieval for query [bold yellow]%s[/bold yellow]", query)
    results = store.retrieve(query, top_k=top_k)
    if as_json:
        payload = [
            {
                "id": document.id,
                "metadata": document.metadata,
                "content": document.content,
            }
            for document in results
        ]
        CONSOLE.print_json(json.dumps(payload))
        return 0

    table = Table(title=f"Git Vector Store Results ({len(results)} hits)")
    table.add_column("Document ID", style="cyan", overflow="fold")
    table.add_column("Kind", style="magenta")
    table.add_column("OID", style="green")
    table.add_column("Subject", style="white", overflow="fold")

    for document in results:
        table.add_row(
            document.id,
            str(document.metadata.get("kind", "")),
            str(document.metadata.get("oid", ""))[:12],
            str(document.metadata.get("subject", "")).splitlines()[0],
        )
    CONSOLE.print(table)
    return 0


def render_document(store: GitVectorStore, document_id: str) -> int:
    document = store.get_document(document_id)
    if not document:
        LOGGER.error("Document [bold red]%s[/bold red] was not found", document_id)
        return 1

    LOGGER.info("Printing document [bold cyan]%s[/bold cyan]", document_id)
    CONSOLE.rule(f"[bold blue]{document_id}")
    CONSOLE.print(document.content)
    return 0


def main(argv: Optional[Iterable[str]] = None) -> int:
    parser = build_parser()
    args = parser.parse_args(list(argv) if argv is not None else None)
    configure_logging(verbose=args.verbose)
    store = build_store(args)

    if args.command == "query":
        return render_query_results(store, args.query, args.top_k, args.json)
    if args.command == "show":
        return render_document(store, args.document_id)

    parser.error(f"Unknown command: {args.command}")
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
