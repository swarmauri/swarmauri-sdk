from __future__ import annotations

import os
import uvicorn


def main() -> None:
    """Run the peagen worker using uvicorn."""
    host = os.getenv("HOST", "0.0.0.0")
    port = int(os.getenv("PORT", "8000"))
    log_level = os.getenv("PEAGEN_LOG_LEVEL", "info").lower()
    uvicorn.run(
        "peagen.worker:app",
        host=host,
        port=port,
        log_level=log_level,
    )


if __name__ == "__main__":
    main()
