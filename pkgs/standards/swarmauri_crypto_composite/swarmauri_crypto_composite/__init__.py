from .CompositeCrypto import CompositeCrypto

__all__ = ["CompositeCrypto"]

try:  # pragma: no cover - simply version shim
    from importlib.metadata import PackageNotFoundError, version
except ImportError:  # pragma: no cover
    from importlib_metadata import PackageNotFoundError, version

try:  # pragma: no cover - environment dependent
    __version__ = version("swarmauri_crypto_composite")
except PackageNotFoundError:  # pragma: no cover - local dev fallback
    __version__ = "0.0.0"
