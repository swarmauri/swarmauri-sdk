from __future__ import annotations

API_ROUTES = [
    {
        "method": "GET",
        "path": "/.well-known/acme-directory",
        "handler": "schema.directory_extra:build_directory",
    },
    {"method": "HEAD", "path": "/acme/new-nonce", "handler": "tables.Nonce:new_nonce"},
    {"method": "GET", "path": "/acme/new-nonce", "handler": "tables.Nonce:new_nonce"},
    {
        "method": "POST",
        "path": "/acme/new-account",
        "handler": "tables.Account:new_account",
    },
    {"method": "POST", "path": "/acme/new-order", "handler": "tables.Order:new_order"},
]
