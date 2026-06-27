# Swarmauri SDK Product Portfolio Website Brief

Audience: copywriting, technical writing, developer relations, product marketing, and website implementation teams.

Source basis: local `swarmauri-sdk` repository audit on June 19, 2026. Primary repo sources inspected include the root `README.md`, `pkgs/README.md`, `pkgs/pyproject.toml`, foundational package metadata and READMEs, `pkgs/swarmauri/docs/callflow.md`, `pkgs/swarmauri/docs/citizenship.md`, and active package manifests under `pkgs/`.

## Executive Summary

Swarmauri SDK is best presented as a composable Python infrastructure SDK for typed AI, agent, security, runtime, and integration components. It is not just an agent framework and not just a provider wrapper collection. The repository is structured as a large `uv` workspace with independently installable packages, a stable public namespace package, interface contracts, reusable Pydantic-backed base classes, first-party standard components, and many focused standards/community/provider packages.

The strongest website framing is:

> Swarmauri is composable intelligence infrastructure for Python teams building typed, pluggable systems across agents, models, tools, retrieval, security, transports, middleware, storage, billing, and provider integrations.

The portfolio site should make the architecture legible in three layers:

1. Foundation: `swarmauri`, `swarmauri_core`, `swarmauri_base`, `swarmauri_standard`, and `swarmauri_typing`.
2. Component families: agents, LLMs, tools, parsers, vector stores, security, runtime, middleware, storage, billing, XMP, transports, and identity/provider integrations.
3. Package channels: first-party standard packages, standards-oriented packages, community packages, plugin packages, experimental packages, and deprecated compatibility packages.

## Verified Repository Facts

- The active workspace manifest lists 305 active workspace members.
- Active package areas include 173 `standards` packages, 108 `community` packages, 13 `experimental` packages, 5 `plugins` packages, 5 foundational entries, and 1 deprecated package.
- Foundational packages are `swarmauri`, `swarmauri_core`, `swarmauri_base`, `swarmauri_standard`, and `swarmauri_typing`.
- The public namespace package is `swarmauri` at version `0.9.1.dev5`.
- The core/base/standard packages are at version `0.10.1.dev5`.
- The monorepo workspace package is `swarmauri_monorepo` at version `0.6.2.dev3`.
- Package metadata targets Python `>=3.10,<3.15`, with classifiers and badges for Python 3.10, 3.11, 3.12, 3.13, and 3.14 in the foundational packages.
- The license is Apache-2.0.
- Author metadata lists Jacob Stewart `<jacob@swarmauri.com>`.
- The root README describes Swarmauri as a composable intelligence infrastructure SDK for typed, pluggable Python systems.
- The preferred workflow for plugins and examples is direct instantiation, not routing through `PluginManager`, unless a package explicitly requires it.

## Product Positioning

### Primary Positioning

Swarmauri should be positioned as infrastructure for composable intelligence systems. The phrase "composable intelligence infrastructure" is already used in package descriptions and should become the headline architecture term across the website.

Recommended homepage/product-portfolio statement:

> Swarmauri SDK gives Python teams a typed component system for building AI and infrastructure workflows from interchangeable agents, model adapters, tools, parsers, vector stores, signing components, key providers, transports, middleware, storage adapters, billing providers, and provider integrations.

### What Swarmauri Is

- A Python SDK for composable intelligence infrastructure.
- A namespace and package ecosystem with independently installable components.
- A contract-first component model built around `swarmauri_core` interfaces.
- A Pydantic-backed component implementation layer through `swarmauri_base`.
- A first-party standard component bundle through `swarmauri_standard`.
- A plugin and entry-point discovery system for first-class, second-class, and third-class component packages.
- A large package portfolio spanning AI workflow, retrieval, security, runtime, middleware, transport, storage, billing, and provider integration surfaces.

### What Swarmauri Is Not

Avoid narrowing Swarmauri to any of these:

- Not only an agent framework.
- Not only an LLM provider wrapper.
- Not only a vector-store abstraction.
- Not only a plugin registry.
- Not only a security or signing library.

Those are all valid surfaces, but the portfolio story is broader: Swarmauri is a typed component ecosystem for composable Python systems.

## Recommended Website Information Architecture

### Top-Level Portfolio Sections

1. Overview
2. Architecture
3. Foundational Packages
4. Component Portfolio
5. Security and Trust
6. Runtime and Integration
7. Developer Workflow
8. Package Catalog
9. Examples and Guides
10. Community and Contribution

### Homepage First View

The homepage should immediately show that Swarmauri is both an SDK and a package portfolio. Suggested first viewport:

- H1: "Swarmauri SDK"
- Subheadline: "Composable intelligence infrastructure for typed, pluggable Python systems."
- Supporting copy: "Build AI, agent, security, runtime, and integration workflows from independently installable components with stable contracts, Pydantic-backed models, namespace discovery, and provider-specific packages."
- Primary CTA: "Install Swarmauri"
- Secondary CTA: "Explore Packages"
- Technical proof strip: "305 active workspace packages", "Python 3.10-3.14", "Apache-2.0", "Core/Base/Standard architecture", "Entry-point plugin discovery"

Use the Swarmauri brand asset from `assets/swarmauri.brand.theme.svg` or the existing README image path. If the website needs a single product image, show an architectural system map rather than a generic AI illustration.

## Foundational Package Messaging

### `swarmauri`

Role: public namespace microkernel.

Current metadata description:

> Swarmauri namespace microkernel for registry-backed imports, plugin discovery, and composable intelligence infrastructure components.

Website message:

`swarmauri` is the stable public import and discovery layer. It provides namespace-backed access to installed Swarmauri components and coordinates registry-backed dynamic imports through the public `swarmauri.*` namespace.

Claims to use:

- Stable namespace imports.
- Registry-backed component discovery.
- Entry-point plugin discovery.
- Curated optional dependency groups, including an `llms` optional group.
- Depends on `swarmauri_core`, `swarmauri_base`, and `swarmauri_standard`.

Example install:

```bash
uv add swarmauri
pip install swarmauri
```

### `swarmauri_core`

Role: interface contract layer.

Website message:

`swarmauri_core` defines the stable interfaces and shared types that component authors use to build Swarmauri-compatible packages without depending on every implementation package.

Claims to use:

- Contract-first design.
- Minimal runtime dependency footprint.
- Interfaces for agents, LLMs, tools, parsers, vector stores, crypto, signing, key providers, transports, middleware, storage, billing, XMP, and more.
- Intended mainly for component authors, extension builders, and teams defining compatible implementations.

Example copy:

> Build against interfaces first. Swarmauri Core keeps component contracts independent from concrete implementations so package authors can ship focused integrations without pulling in the whole ecosystem.

### `swarmauri_base`

Role: reusable implementation base layer.

Website message:

`swarmauri_base` turns Swarmauri interfaces into reusable component foundations with Pydantic models, dynamic subtype registration, serialization, resource metadata, and base classes for each major component family.

Claims to use:

- `ComponentBase` provides Pydantic-backed components with `type`, `resource`, `name`, and `version` fields.
- `DynamicBase` and `SubclassUnion` support discriminator-based hydration of registered component subtypes.
- JSON, YAML, and TOML serialization behavior.
- Base classes and mixins for AI workflows, retrieval, runtime, security, storage, billing, XMP, transports, middleware, tools, and model providers.

Example copy:

> Swarmauri Base gives implementations a common runtime shape: typed Pydantic models, dynamic serialization, family-specific base behavior, and registry-ready component metadata.

### `swarmauri_standard`

Role: first-party ready-to-use components.

Website message:

`swarmauri_standard` provides maintained first-party components that users can install and instantiate directly. It is the practical starting point for examples, prototypes, tests, and production workflows that fit the included component behavior.

Claims to use:

- Includes standard agents, chains, documents, tools, toolkits, parsers, prompts, vectors, vector stores, metrics, similarities, schema converters, state, tracing utilities, signing helpers, key-provider components, and model surfaces.
- Demonstrates expected Swarmauri component style: typed base classes, direct imports, dynamic serialization, and namespace-ready registration.
- Direct instantiation should be shown in examples.

Example copy:

> Start with maintained first-party components, then install focused provider packages when you need a narrower integration.

### `swarmauri_typing`

Role: dynamic typing utility support.

Website message:

`swarmauri_typing` supports dynamic typing utilities used by the base component model. It should appear in architecture diagrams and package catalog listings but does not need equal marketing prominence with Core, Base, and Standard.

## Package Portfolio Taxonomy

The website should group packages by user problem, not raw directory name alone. Directory area still matters for trust and lifecycle:

- Foundation: core contracts, base behavior, standard components, namespace, typing utilities.
- Standards: first-class packages aligned to standard interfaces or formalized component families.
- Community: provider integrations and ecosystem packages.
- Plugins: package-level extensions and generic plugin examples.
- Experimental: early-stage or research-oriented packages.
- Deprecated: compatibility surfaces retained for migration.

### Active Workspace Area Counts

| Area | Active workspace members | Website interpretation |
| --- | ---: | --- |
| `standards` | 173 | First-class standards-oriented package portfolio. |
| `community` | 108 | Provider integrations, community-maintained extensions, and specialized tools. |
| `experimental` | 13 | Early-stage, research, or incubating packages. |
| `plugins` | 5 | Plugin package examples and extension surfaces. |
| Foundation/root package entries | 5 | Public namespace, core contracts, base classes, standard bundle, typing. |
| `deprecated` | 1 | Compatibility and migration-only surfaces. |

### Largest Component Families

| Family | Count | Website framing |
| --- | ---: | --- |
| Tools | 42 | Task-specific callable utilities and workflow tools. |
| Middleware | 19 | Runtime request/response, auth, compression, policy, logging, and protocol middleware. |
| Cipher suites | 18 | Standards-aligned cryptographic suite packages. |
| LLMs | 17 | Provider-specific model integrations. |
| Signing | 17 | Signature, envelope, protocol, document, and proof signing surfaces. |
| Transports | 14 | Runtime communication adapters including stdio, TCP, UDP, TLS, QUIC, ASGI, H2, and WebSocket/JSON-RPC styles. |
| Certificates | 13 | Certificate creation, verification, CA, CSR, OCSP/CRL, KMS, and service integrations. |
| Auth IDPs | 12 | Identity provider integrations such as AWS, Azure, Cognito, GitHub, GitLab, Google, Keycloak, Okta, Salesforce, and others. |
| Distances | 12 | Legacy/deprecated distance compatibility surfaces and migration context. |
| Vector stores | 12 | Retrieval and vector database integrations. |
| Key providers | 10 | Key material, KMS, SSH, JWKS, file, local, remote, and mirrored provider abstractions. |
| Parsers | 10 | Document and text parsing utilities. |
| Tokens | 10 | JWT, rotating JWT, DPoP-bound JWT, TLS-bound JWT, PASETO, SSH certificate/signature, introspection, OIDC, and composite token packages. |
| Billing | 9 | Payment and billing provider integrations plus mock/standard package. |
| Crypto | 9 | Cryptographic provider packages and composition helpers. |
| XMP | 8 | Metadata embedding/handling for media and document formats. |
| Storage | 7 | Memory, file, S3, S3FS, MinIO, GitHub, and GitHub Release storage adapters. |

## Component Portfolio Detail

### AI and Agent Workflow

Relevant surfaces:

- Agents
- Chains
- Conversations
- Swarms
- Pipelines
- Task management strategies
- Prompts and prompt templates
- Tool LLMs
- LLMs
- VLMs
- Image generation
- OCR
- STT
- TTS

Website framing:

> Compose AI workflows from typed components: agents, chains, prompts, tools, model adapters, vector stores, and multimodal surfaces that share common contracts.

Recommended pages:

- "Agents and Workflows"
- "Model Integrations"
- "Tools and Toolkits"

Developer relations examples:

- A direct `swarmauri_standard` agent example.
- A model-provider swap example using provider-specific LLM packages.
- A tool-using workflow with direct class imports and `swarmauri_base` serialization.

### Retrieval, Documents, and Data

Relevant surfaces:

- Documents
- Document stores
- Parsers
- Chunkers
- Embeddings
- Vector stores
- Vectors
- Schema converters
- Data connectors
- Measurements and token counting

Website framing:

> Swarmauri separates retrieval contracts from storage and provider implementations, letting teams combine parsers, embeddings, vector stores, and document models without coupling workflows to one database or model provider.

Packages to showcase:

- `swarmauri_vectorstore_pinecone`
- `swarmauri_vectorstore_qdrant`
- `swarmauri_vectorstore_redis`
- `swarmauri_vectorstore_duckdb`
- `swarmauri_vectorstore_neo4j`
- `swarmauri_vectorstore_cloudweaviate`
- `swarmauri_vectorstore_annoy`
- `swarmauri_vectorstore_fs`
- `swarmauri_vectorstore_git`
- `swarmauri_vectorstore_persistentchromadb`
- `swarmauri_embedding_doc2vec`
- `swarmauri_embedding_nmf`
- `swarmauri_embedding_mlm`

Developer relations examples:

- Parse a document, chunk it, embed it, store vectors, and retrieve context.
- Show narrow install commands for one vector store rather than `full` install.
- Explain when to use `swarmauri_standard` versus focused provider packages.

### Security, Trust, and Cryptographic Infrastructure

Relevant surfaces:

- Signing
- Crypto
- MRE crypto
- Cipher suites
- Key providers
- Certificates
- Certificate services
- Proof of possession
- Tokens
- Auth IDPs
- XMP metadata
- Git filters

Website framing:

> Swarmauri includes a broad security-oriented component portfolio for signing, tokens, proof-of-possession, certificate workflows, key providers, cipher suites, identity-provider integrations, and metadata workflows.

Do not overclaim compliance or certification. The repo contains packages named around FIPS, CNSA, WebAuthn, TLS 1.3, COSE, JWA, XAdES, PAdES, CAdES, Sigstore, PEP 458, YubiKey, and related surfaces, but website copy should describe these as packages/surfaces unless each compliance claim is separately verified.

Good claim:

> Standards-oriented packages cover modern signing, token, certificate, proof-of-possession, key-provider, and cipher-suite workflows.

Avoid without external validation:

> Fully certified FIPS-compliant cryptography.

Packages to showcase:

- `swarmauri_signing_ed25519`
- `swarmauri_signing_jws`
- `swarmauri_signing_dpop`
- `swarmauri_signing_pdf`
- `swarmauri_signing_openpgp`
- `swarmauri_crypto_composite`
- `swarmauri_crypto_jwe`
- `swarmauri_keyprovider_inmemory`
- `swarmauri_keyprovider_file`
- `swarmauri_keyprovider_remote_jwks`
- `swarmauri_tokens_jwt`
- `swarmauri_tokens_rotatingjwt`
- `swarmauri_tokens_dpopboundjwt`
- `swarmauri_tokens_tlsboundjwt`
- `swarmauri_pop_dpop`
- `swarmauri_pop_x509`
- `swarmauri_certs_x509`
- `swarmauri_certs_x509verify`

Developer relations examples:

- Sign and verify a payload with Ed25519.
- Issue or validate a token using a token package.
- Show key-provider interchangeability.
- Demonstrate XMP metadata handling for PDF, PNG, SVG, JPEG, MP4, TIFF, WebP, and GIF packages only after verifying package-level usage examples.

### Runtime, Middleware, and Transport

Relevant surfaces:

- Middleware
- Transports
- Publishers
- Rate limits
- Logging
- Service registries
- State
- Storage
- Git filters

Website framing:

> Swarmauri is not limited to AI composition; it also includes runtime infrastructure components for moving, securing, storing, publishing, and observing data across Python workflows.

Packages to showcase:

- `swarmauri_transport_stdio`
- `swarmauri_transport_tcpunicast`
- `swarmauri_transport_udp`
- `swarmauri_transport_tls_unicast`
- `swarmauri_transport_mtlsunicast`
- `swarmauri_transport_quic`
- `swarmauri_transport_asgi`
- `swarmauri_transport_h2`
- `swarmauri_transport_wsjsonrpcmux`
- `swarmauri_middleware_auth`
- `swarmauri_middleware_jwt`
- `swarmauri_middleware_jsonrpc`
- `swarmauri_middleware_cors`
- `swarmauri_middleware_ratelimit`
- `swarmauri_middleware_securityheaders`
- `swarmauri_storage_memory`
- `swarmauri_storage_file`
- `swarmauri_storage_s3`
- `swarmauri_storage_minio`
- `swarmauri_storage_github`

Developer relations examples:

- Build a JSON-RPC-style tool surface over a transport.
- Add middleware to a request/response flow.
- Store artifacts through memory/file/S3-compatible storage.

### Business and Provider Integrations

Relevant surfaces:

- Billing provider packages.
- Auth IDP packages.
- LLM provider packages.
- Cloud/key/certificate service packages.
- Jupyter tooling packages.
- GitHub toolkit and loader packages.

Website framing:

> Swarmauri packages provider-specific integrations behind stable component contracts, so applications can adopt focused dependencies without losing a common programming model.

Billing packages to mention:

- `swarmauri_billing_adyen`
- `swarmauri_billing_authorize_net`
- `swarmauri_billing_braintree`
- `swarmauri_billing_paypal`
- `swarmauri_billing_paystack`
- `swarmauri_billing_razorpay`
- `swarmauri_billing_square`
- `swarmauri_billing_stripe`
- `swarmauri_billing_mock`

LLM provider packages to mention:

- `swarmauri_llm_ai21`
- `swarmauri_llm_anthropic`
- `swarmauri_llm_cerebras`
- `swarmauri_llm_cohere`
- `swarmauri_llm_deepinfra`
- `swarmauri_llm_deepseek`
- `swarmauri_llm_falai`
- `swarmauri_llm_gemini`
- `swarmauri_llm_groq`
- `swarmauri_llm_hyperbolic`
- `swarmauri_llm_leptonai`
- `swarmauri_llm_llamacpp`
- `swarmauri_llm_mistral`
- `swarmauri_llm_openai`
- `swarmauri_llm_perplexity`
- `swarmauri_llm_playht`
- `swarmauri_llm_whisper`

Identity provider packages to mention:

- `swarmauri_auth_idp_aws`
- `swarmauri_auth_idp_apple`
- `swarmauri_auth_idp_azure`
- `swarmauri_auth_idp_cognito`
- `swarmauri_auth_idp_facebook`
- `swarmauri_auth_idp_gitea`
- `swarmauri_auth_idp_github`
- `swarmauri_auth_idp_gitlab`
- `swarmauri_auth_idp_google`
- `swarmauri_auth_idp_keycloak`
- `swarmauri_auth_idp_okta`
- `swarmauri_auth_idp_salesforce`

## Plugin and Discovery Story

The website should explain plugin discovery in plain language:

> Swarmauri packages can expose components through entry points and namespace mappings. The `swarmauri` namespace importer checks registry mappings, discovers installed entry points, validates first-class and second-class plugins against expected interfaces, and makes components available through stable public import paths.

Plugin classes from `pkgs/swarmauri/docs/citizenship.md`:

- First-class plugins: pre-registered, priority mapped under specific namespaces such as `swarmauri.agents`, and expected to implement required interfaces.
- Second-class plugins: community-contributed, not pre-registered, share the same namespace as first-class components, and expected to implement required interfaces.
- Third-class plugins: generic plugins mapped under `swarmauri.plugins`, not tied to a specific resource kind, and not subject to the same interface validation.

Developer relations should avoid `PluginManager` examples unless explicitly requested by a package. The repo contribution guide states that plugins should be instantiated directly.

## Website Copy Blocks

### Short Product Description

Swarmauri SDK is composable intelligence infrastructure for Python. It gives developers typed interfaces, reusable Pydantic-backed base classes, first-party components, provider integrations, and namespace-backed discovery for building AI, agent, security, runtime, and integration workflows.

### Longer Product Description

Swarmauri SDK helps Python teams build pluggable systems from stable component contracts. Start with `swarmauri_core` interfaces, implement reusable components with `swarmauri_base`, use maintained first-party components from `swarmauri_standard`, and install focused provider packages for LLMs, vector stores, signing, key providers, transports, middleware, storage, billing, certificates, tokens, identity providers, and more. The public `swarmauri` namespace keeps imports stable while each package keeps dependencies focused.

### Hero Bullets

- Typed contracts for agents, models, tools, retrieval, runtime, storage, security, and provider integrations.
- Pydantic-backed component models with dynamic serialization and subtype hydration.
- Independently installable packages for focused dependency footprints.
- Namespace and entry-point discovery for registry-backed component imports.
- First-party standard components plus standards, community, plugin, and experimental package channels.

### Technical Proof Points

- 305 active workspace members in the local `pkgs/` manifest.
- 173 active standards packages and 108 active community packages.
- Python 3.10 through 3.14 metadata support in foundational packages.
- Apache-2.0 license.
- 223 Python files in `swarmauri_core`, 203 in `swarmauri_base`, and 315 in `swarmauri_standard` at audit time.
- Entry-point groups include Swarmauri auth IDPs, tools, LLMs, middlewares, cipher suites, vector stores, distances, signings, key providers, parsers, cert services, evaluators, tokens, billing providers, XMP handlers, crypto, MRE crypto, storage adapters, toolkits, publishers, agents, and more.

## Technical Writer Guidance

### Documentation Pages to Create or Refresh

1. "What is Swarmauri?"
2. "Architecture: Core, Base, Standard, Namespace"
3. "Installing Swarmauri"
4. "Choosing a Package"
5. "Building a Component"
6. "Direct Instantiation Patterns"
7. "Dynamic Serialization and `SubclassUnion`"
8. "Plugin Discovery and Citizenship"
9. "Package Catalog"
10. "Migration Notes: Distance Compatibility"

### Docs Should Emphasize

- Direct class imports and direct instantiation.
- Core interfaces before base classes.
- Base classes before standard implementations.
- Narrow package installs for production dependency control.
- `swarmauri[full]` only when a broad local bundle is appropriate.
- `swarmauri_standard` as maintained first-party implementation surface.
- Community packages as focused integrations.
- Experimental packages as not yet the main product promise.

### Docs Should Avoid

- Treating package names as proof of certified compliance.
- Presenting experimental packages as stable production recommendations.
- Using `PluginManager` as the default pattern.
- Suggesting users must install the whole monorepo for ordinary usage.
- Flattening first-party, standards, community, plugin, and experimental package lifecycles into one bucket.

## Copywriter Guidance

### Voice

Use precise infrastructure language. Swarmauri should sound like a serious developer platform, not a novelty agent demo.

Preferred words:

- composable
- typed
- pluggable
- contracts
- interfaces
- components
- namespace
- provider integrations
- independently installable
- dependency-focused
- registry-backed
- Pydantic-backed

Use carefully:

- AI agents
- orchestration
- enterprise
- secure
- compliance
- certified

Avoid:

- magical
- autonomous everything
- no-code
- universal replacement
- guaranteed compliance
- fully certified cryptography unless separately verified

### Messaging Pillars

1. Contract-first: Build against stable interfaces.
2. Composition-first: Assemble workflows from typed components.
3. Package-first: Install only the providers and surfaces you need.
4. Discovery-ready: Use namespace and entry-point discovery when components should be public and discoverable.
5. Infrastructure breadth: AI workflows plus runtime, security, storage, middleware, billing, and transport components.

## Developer Relations Guidance

### Example Strategy

Developer relations should produce examples in this order:

1. Direct install and import.
2. Direct instantiation of `swarmauri_standard` components.
3. A focused provider package install and use.
4. A custom component built from `swarmauri_core` and `swarmauri_base`.
5. Serialization and hydration with `ComponentBase`, `DynamicBase`, and `SubclassUnion`.
6. Entry-point or namespace discovery for a discoverable package.

### High-Value Example Ideas

- Build and serialize a typed tool component.
- Swap an LLM provider package while preserving the contract shape.
- Parse, embed, store, and retrieve documents.
- Sign and verify a message with a focused signing package.
- Route data through storage adapters.
- Add runtime middleware to a transport-oriented flow.
- Use a billing provider behind a common billing interface.
- Publish a custom package with a `swarmauri.<kind>` entry point.

### Example Rules

- Prefer direct imports from implementation packages.
- Keep dependency surfaces narrow.
- Include both `uv add` and `pip install` commands.
- Mention Python 3.10-3.14 support.
- Use concrete package names rather than abstract category language alone.
- Where package support is uncertain, show a verified local package example rather than extrapolating.

## Suggested Website Components

### Architecture Diagram

Use a layered diagram:

```text
Application Workflows
        |
swarmauri namespace imports and discovery
        |
First-party standard components + focused provider packages
        |
swarmauri_base component model and serialization
        |
swarmauri_core interface contracts
```

Add side rails for package channels:

- Standards
- Community
- Plugins
- Experimental
- Deprecated compatibility

### Package Catalog Filters

Recommended filters:

- Package channel: foundation, standards, community, plugin, experimental, deprecated.
- Component family: agents, LLMs, tools, parsers, vector stores, signing, crypto, key providers, certs, tokens, middleware, transports, storage, billing, XMP, auth IDP, publisher, evaluator.
- Python support.
- Installation command.
- Lifecycle status.
- Direct import example available.
- Entry-point group.

### Portfolio Cards

Each card should include:

- Package name.
- One-line purpose.
- Channel.
- Component family.
- Install command.
- Direct import snippet.
- Related core interface or base class.
- Stability/lifecycle note.

## Claims Matrix

| Claim | Use on website? | Evidence from repo | Caveat |
| --- | --- | --- | --- |
| Swarmauri is composable intelligence infrastructure | Yes | Root README and package metadata use this framing. | Keep phrasing technical, not hype-driven. |
| Swarmauri supports Python 3.10-3.14 | Yes | Foundational package classifiers and requires-python `>=3.10,<3.15`. | Individual packages should still be checked before package-specific claims. |
| Swarmauri has 305 active workspace members | Yes | `pkgs/pyproject.toml` active workspace member count. | Count excludes commented-out workspace entries. |
| Swarmauri has first-party standard components | Yes | `swarmauri_standard` README and metadata. | Do not imply every component family has mature production coverage. |
| Swarmauri supports plugin discovery | Yes | `swarmauri` README, docs callflow, entry points across packages. | Explain direct instantiation as preferred user workflow. |
| Swarmauri includes security and trust packages | Yes | Signing, crypto, keyprovider, token, cert, cipher, pop packages. | Avoid certification/compliance claims unless separately verified. |
| Swarmauri includes billing integrations | Yes | Billing packages across standards and community. | Provider feature completeness must be verified package by package. |
| Swarmauri includes LLM integrations | Yes | 17 LLM family packages plus optional `llms` group. | Model/provider availability may drift externally. |
| Swarmauri includes vector-store integrations | Yes | 12 vectorstore family packages. | Backend versions and service features may drift externally. |
| Swarmauri is an enterprise-ready compliance platform | Not as written | Repo has standards-oriented packages but not a website-verified compliance claim. | Rephrase as "standards-oriented security and runtime component packages." |

## Recommended Homepage Copy Draft

### Hero

Swarmauri SDK

Composable intelligence infrastructure for typed, pluggable Python systems.

Build AI, agent, security, runtime, and integration workflows from stable contracts, Pydantic-backed components, first-party standard implementations, and focused provider packages.

Primary CTA: Install Swarmauri

Secondary CTA: Explore the Package Portfolio

### Section: Build From Contracts

Swarmauri separates component contracts from implementations. `swarmauri_core` defines the interfaces, `swarmauri_base` adds reusable component behavior and serialization, and `swarmauri_standard` provides maintained first-party implementations. Provider packages can stay focused while applications keep a common programming model.

### Section: Install Only What You Need

Start with `swarmauri` for namespace discovery and curated defaults, install `swarmauri_standard` for first-party components, or choose focused packages such as `swarmauri_vectorstore_pinecone`, `swarmauri_llm_openai`, `swarmauri_signing_ed25519`, or `swarmauri_storage_s3` for narrower dependency surfaces.

### Section: More Than Agents

Swarmauri includes agents and model integrations, but the portfolio also covers tools, parsers, embeddings, vector stores, signing, crypto, tokens, key providers, certificates, proof-of-possession, transports, middleware, storage, billing, XMP metadata, and identity-provider integrations.

## Recommended Install Section

```bash
uv add swarmauri
pip install swarmauri
```

For first-party standard components:

```bash
uv add swarmauri_standard
pip install swarmauri_standard
```

For component authors:

```bash
uv add swarmauri_core swarmauri_base
pip install swarmauri_core swarmauri_base
```

For focused packages:

```bash
uv add swarmauri_llm_openai
uv add swarmauri_vectorstore_pinecone
uv add swarmauri_signing_ed25519
uv add swarmauri_storage_s3
```

## Recommended Code Examples

### Direct Standard Component

```python
from swarmauri_standard.documents.Document import Document

doc = Document(content="Composable intelligence infrastructure")
payload = doc.model_dump_json()
restored = Document.model_validate_json(payload)

assert restored.type == "Document"
```

### Dynamic Component Hydration

```python
from pydantic import BaseModel

from swarmauri_base.DynamicBase import SubclassUnion
from swarmauri_base.toolkits.ToolkitBase import ToolkitBase
from swarmauri_standard.toolkits.Toolkit import Toolkit


class ToolkitEnvelope(BaseModel):
    toolkit: SubclassUnion[ToolkitBase]


payload = ToolkitEnvelope(toolkit=Toolkit()).model_dump_json()
restored = ToolkitEnvelope.model_validate_json(payload)

assert isinstance(restored.toolkit, Toolkit)
```

### Component Author Shape

```python
from typing import Literal

from swarmauri_base.ComponentBase import ComponentBase
from swarmauri_base.tools.ToolBase import ToolBase


@ComponentBase.register_type(ToolBase, "EchoTool")
class EchoTool(ToolBase):
    type: Literal["EchoTool"] = "EchoTool"
    name: str = "echo"
    description: str = "Return the input payload."

    def __call__(self, payload):
        return payload
```

## Website Update Checklist

- Add a product portfolio overview page with the Core/Base/Standard/Namespace architecture.
- Add a package catalog sourced from `pkgs/pyproject.toml` rather than manually maintained lists.
- Add package-family landing pages for AI workflow, retrieval, security/trust, runtime/infrastructure, and provider integrations.
- Add a plugin discovery explainer with first-class, second-class, and third-class plugin citizenship.
- Add direct-instantiation examples and avoid `PluginManager` as the default user story.
- Add install tabs for `uv` and `pip`.
- Add caveats for experimental/deprecated packages.
- Add a claims review pass before publishing compliance-sensitive wording.
- Add a periodic package-count refresh step so website statistics do not drift from the workspace manifest.

## Open Questions for Product and Website Owners

- Should the portfolio site include experimental packages, or should they be behind an "incubating" filter?
- Should package pages be generated from `pyproject.toml` metadata and README snippets?
- Should security-oriented packages be grouped under "Trust Infrastructure", "Security", or "Cryptographic Components"?
- Should the site expose package lifecycle status from directory placement, classifiers, or a separate metadata field?
- Should Tigrbl packages inside the workspace appear in the Swarmauri product portfolio or a separate Tigrbl portfolio section?
- Which package examples should be live-tested and promoted as canonical quickstarts?

## Publishing Caveats

The website can safely claim the package portfolio exists in the repository. It should not claim full provider feature parity, compliance certification, production readiness of every package, or current external service compatibility without package-by-package validation. Provider APIs, pricing, authentication requirements, and model availability change outside this repository.

