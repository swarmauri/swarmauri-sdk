from __future__ import annotations

import os
import uvicorn


def main() -> None:
    """Run the peagen gateway using uvicorn."""
    host = os.getenv("HOST", "0.0.0.0")
    port = int(os.getenv("PORT", "8000"))
    log_level = os.getenv("PEAGEN_LOG_LEVEL", "info").lower()
    uvicorn.run(
        "peagen.gateway:app",
        host=host,
        port=port,
        log_level=log_level,
        proxy_headers=True,
        forwarded_allow_ips="*",
    )


if __name__ == "__main__":
    main()
