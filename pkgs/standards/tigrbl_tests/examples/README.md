# Tigrbl Examples Curriculum

The `examples/` directory is a downstream-facing learning workspace for
implementers of Tigrbl. Each lesson is a pytest module that demonstrates
intended usage patterns from model definition to fully running APIs. The
curriculum is structured to ramp from beginner fundamentals through advanced
patterns, with a placeholder for future expert modules.

> ✅ These lessons use pytest only (no monkeypatch or mock).
> ✅ Usage lessons deploy a real uvicorn server to validate end-to-end behavior.

## How to run the lessons

From `/workspace/swarmauri-sdk/pkgs`:

```bash
uv run --package tigrbl-tests --directory standards/tigrbl_tests pytest examples
```

## Curriculum overview

### Beginner modules (01–05)
1. **01 - Foundations**
   - 01: Class creation basics
   - 02: Instantiation and attribute access
   - 03: Column registration fundamentals
   - 04: Mapped vs. virtual (non-mapped) columns
2. **02 - Column Specs**
   - 01: Storage specs (`S`)
   - 02: Field specs (`F`)
   - 03: IO specs (`IO`)
   - 04: Column spec composition
3. **03 - Mixins + Table Args**
   - 01: GUID primary keys
   - 02: Timestamped mixins
   - 03: Table args (constraints + indexes)
   - 04: Engine binding via table config
4. **04 - App + API Basics**
   - 01: Defining app specs
   - 02: Deriving app classes
   - 03: Table specs and MRO merge
   - 04: Including models in APIs
5. **05 - Usage Essentials**
   - 01: REST create + read
   - 02: OpenAPI path discovery
   - 03: Health and kernel diagnostics
   - 04: RPC create via `tigrbl_client`

### Intermediate modules (06–10)
6. **06 - Bindings**
   - 01: Binding opspecs
   - 02: Binding columns
   - 03: Including multiple models
   - 04: REST router attachment
7. **07 - Decorators**
   - 01: `@schema_ctx`
   - 02: `@op_ctx`
   - 03: `@hook_ctx`
   - 04: `@response_ctx`
8. **08 - Configuration + MRO**
   - 01: Table engine precedence
   - 02: Table sequence merge
   - 03: App spec precedence
   - 04: Table config inheritance
9. **09 - Ops + IO**
   - 01: IO aliasing
   - 02: IO filters
   - 03: Column IO usage
   - 04: Default opspecs
10. **10 - System Diagnostics**
    - 01: `/healthz`
    - 02: `/hookz` + `/methodz`
    - 03: `/systemz` prefix routes
    - 04: OpenAPI system paths

### Advanced modules (11–15)
11. **11 - Uvicorn E2E**
    - 01: REST update flows
    - 02: REST list + delete
    - 03: `/kernelz` visibility
    - 04: `/healthz` validation
12. **12 - REST/RPC Parity**
    - 01: httpx vs `tigrbl_client` REST
    - 02: JSON-RPC parity
    - 03: REST + RPC ID alignment
    - 04: Async `tigrbl_client`
13. **13 - Hooks**
    - 01: POST_RESPONSE hook mutation
    - 02: `/hookz` endpoint
    - 03: `/kernelz` endpoint
    - 04: Custom op + hook chain
14. **14 - Column Types**
    - 01: Scalar types
    - 02: Text + JSON types
    - 03: Binary + array types
    - 04: Postgres-specific types
15. **15 - Advanced Table Design**
    - 01: Table args (constraints)
    - 02: Default factories
    - 03: Virtual read producers
    - 04: Mixins + custom columns

### Expert modules (placeholder)
16. **16 - Expert: Multi-tenant orchestration** *(placeholder)*
17. **17 - Expert: Policy-driven hooks** *(placeholder)*
18. **18 - Expert: Advanced op pipelines** *(placeholder)*
19. **19 - Expert: Custom engine providers** *(placeholder)*
20. **20 - Expert: Observability + tracing** *(placeholder)*
