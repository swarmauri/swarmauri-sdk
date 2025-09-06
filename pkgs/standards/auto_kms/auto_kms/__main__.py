from __future__ import annotations

import os
import uvicorn


def main() -> None:
    """Run the auto_kms server using uvicorn."""
    host = os.getenv("HOST", "0.0.0.0")
    port = int(os.getenv("PORT", "8000"))
    log_level = os.getenv("AUTO_KMS_LOG_LEVEL", "debug").lower()
    uvicorn.run(
        "auto_kms.app:app",
        host=host,
        port=port,
        log_level=log_level,
        proxy_headers=True,
        forwarded_allow_ips="*",
    )


if __name__ == "__main__":
    main()
