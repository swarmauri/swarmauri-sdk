import argparse
import json
import logging
from typing import Iterable, Optional

from rich.console import Console
from rich.logging import RichHandler
from rich.table import Table

from .FsVectorStore import FsVectorStore


LOGGER = logging.getLogger("swarmauri.fs_vectorstore")
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
        description="BM25F retrieval over filesystem files and chunks."
    )
    parser.add_argument("--root", default=".", help="Root directory to index")
    parser.add_argument(
        "--mode",
        choices=["chunk", "file", "chunk_file"],
        default="chunk",
        help="Indexing mode",
    )
    parser.add_argument("--chunk-size", type=int, default=1200, help="Chunk size in characters")
    parser.add_argument("--chunk-overlap", type=int, default=120, help="Chunk overlap in characters")
    parser.add_argument("--include", action="append", dest="include", help="Glob to include")
    parser.add_argument("--exclude", action="append", dest="exclude", help="Glob to exclude")
    parser.add_argument(
        "--max-file-size",
        type=int,
        default=1_000_000,
        help="Maximum file size in bytes to index",
    )
    parser.add_argument("--verbose", action="store_true", help="Enable debug logging")

    subparsers = parser.add_subparsers(dest="command", required=True)

    query_parser = subparsers.add_parser("query", help="Query indexed filesystem documents")
    query_parser.add_argument("--query", required=True, help="Query text")
    query_parser.add_argument("--top-k", type=int, default=5, help="Number of hits to return")
    query_parser.add_argument("--json", action="store_true", help="Emit JSON output")

    show_parser = subparsers.add_parser("show", help="Print a document by id")
    show_parser.add_argument("--document-id", required=True, help="Document id to display")

    return parser


def build_store(args: argparse.Namespace) -> FsVectorStore:
    store = FsVectorStore(
        root_path=args.root,
        mode=args.mode,
        chunk_size=args.chunk_size,
        chunk_overlap=args.chunk_overlap,
        include=tuple(args.include or ()),
        exclude=tuple(args.exclude or ()),
        max_file_size=args.max_file_size,
    )
    LOGGER.info(
        "Building filesystem BM25F index [bold cyan](root=%s, mode=%s)[/bold cyan]",
        args.root,
        args.mode,
    )
    store.build_index()
    LOGGER.info("Indexed [bold green]%s[/bold green] documents", len(store.documents))
    return store


def render_query_results(store: FsVectorStore, query: str, top_k: int, as_json: bool) -> int:
    LOGGER.info("Running BM25F retrieval for query [bold yellow]%s[/bold yellow]", query)
    results = store.search(query, top_k=top_k)
    if not results:
        LOGGER.warning("No lexical matches found for query [bold yellow]%s[/bold yellow]", query)

    if as_json:
        payload = [
            {
                "id": document.id,
                "score": score,
                "metadata": document.metadata,
                "content": document.content,
            }
            for document, score in results
        ]
        CONSOLE.print_json(json.dumps(payload))
        return 0

    table = Table(title=f"Fs Vector Store Results ({len(results)} hits)")
    table.add_column("Document ID", style="cyan", overflow="fold")
    table.add_column("Score", style="green")
    table.add_column("Kind", style="magenta")
    table.add_column("Path", style="white", overflow="fold")
    table.add_column("Lines", style="blue")

    for document, score in results:
        table.add_row(
            document.id,
            f"{score:.4f}",
            str(document.metadata.get("document_kind", "")),
            str(document.metadata.get("relative_path", "")),
            f"{document.metadata.get('start_line')}:{document.metadata.get('end_line')}",
        )
    CONSOLE.print(table)
    return 0


def render_document(store: FsVectorStore, document_id: str) -> int:
    document = store.get_document(document_id)
    if not document:
        LOGGER.error("Document [bold red]%s[/bold red] was not found", document_id)
        return 1

    LOGGER.info("Printing document [bold cyan]%s[/bold cyan]", document_id)
    CONSOLE.rule(f"[bold blue]{document_id}")
    CONSOLE.print_json(json.dumps(document.metadata))
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
