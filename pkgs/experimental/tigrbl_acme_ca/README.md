# tigrbl_acme_ca

A Tigrbl-native ACME v2 Certificate Authority implementation.

## Highlights

- **Tables-first** design: all I/O derives from `tables/` column specs.
- **Canon verbs**: write flows use model-bound ops that alias to built-in Tigrbl verbs.
- **Ops/Hooks** only use the request `ctx` and SQLAlchemy session—**no kernel atoms**.
- **HSM/KMS-ready**: pluggable key providers (file, KMS, PKCS#11 stubs) and a signing engine.
- **OCSP/CRL/CT**: hooks and workers to publish CRLs, answer OCSP, and submit to CT logs.
- **Compliance**: audit/evidence hooks, redaction, and control enforcers.
- **Telemetry**: Prometheus metrics and OpenTelemetry tracing (optional).

## Layout

- `tables/` — database schema (Account, Order, Authorization, Challenge, Certificate, Revocation, Nonce, etc.).
- `app/` — AppSpec, TableSpec, ApiSpec.
- `ops/` — ACME verbs and guards.
- `services/` — RA/VA/CA/Revocation/Audit/Compliance/Integrations.
- `engines/` — signing engine and session.
- `key_mgmt/` — key provider interfaces + loader.
- `libs/` — cert issuance logic and KMS adapter.
- `workers/` — background tasks (validation, issuance, revocation).
- `telemetry/` — tracing + metrics helpers.
- `adapters/` — first-party adapters (JWS parser, HTTP negotiation).

## Dev Quickstart

1. Install dependencies (pseudo):  
   ```bash
   pip install -e .  # plus your runtime/gateway deps
   ```
2. Configure a dev CA key:  
   ```toml
   [acme.ca]
   key_source = "file"
   key_path = "ca.key.pem"
   ```
3. Wire a `signing_engine` into your gateway context:  
   ```python
   from tigrbl_acme_ca.engines.acme_signing import AcmeSigningEngine
   engine = AcmeSigningEngine.from_config(app_config)
   ctx["signing_engine"] = engine
   ```
4. Hit ACME endpoints: `/.well-known/acme-directory`, `/acme/new-nonce`, `/acme/new-account`, `/acme/new-order`.

## License

Apache License 2.0 — see `LICENSE`.
