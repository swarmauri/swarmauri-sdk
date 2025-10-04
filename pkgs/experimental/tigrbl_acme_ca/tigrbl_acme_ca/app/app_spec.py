from __future__ import annotations

class AcmeCaAppSpec:
    name = "tigrbl_acme_ca"
    version = "0.1.0"

    def load_tables(self):
        from tigrbl_acme_ca.app.table_spec import TABLES
        _ = [t for t in TABLES]
        return TABLES

    def load_api(self):
        from tigrbl_acme_ca.app.api_spec import API_ROUTES
        return API_ROUTES
