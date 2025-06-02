import uvicorn

def main() -> None:
    """
    Development entry-point.

    Run with:
        python -m scripts.dev_server
    """
    uvicorn.run(
        "dqueue.transport.http_api:app",   # ← IMPORT STRING, not object
        host="0.0.0.0",
        port=8000,
        reload=True,
    )

if __name__ == "__main__":
    main()
