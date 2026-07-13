# Swarmauri Package Index

Generated from `package-index.toml`. Do not move package directories as part of
index maintenance; this index records current paths and keeps distribution names
and import roots stable.

Index values are displayed as `layer.order`, where `layer` captures package
citizenship/dependency band and `order` captures composition depth. A
same-layer package that composes another package is indexed at a higher
order than the package it composes.

Order is `explicit` when `package-index.toml` carries an intentional
override. Otherwise it is inferred from the package layer, family, metadata
signals, and internal runtime dependencies. Same-layer dependency cycles
fail validation because they make composition order ambiguous.

## Layer Summary

| Layer | Packages | Workspace packages | Purpose |
|---|---:|---:|---|
| `00-typing` | 1 | 1 | typing helpers and generic type composition primitives |
| `10-interfaces` | 1 | 1 | interface and protocol contracts |
| `20-bases` | 1 | 1 | reusable base classes, mixins, and component models |
| `30-standard-kernel` | 1 | 1 | bundled first-party standard component kernel |
| `40-standards` | 181 | 181 | first-party split standard packages |
| `50-community` | 109 | 109 | community and provider-specific packages |
| `60-plugins` | 5 | 5 | plugin packages and plugin examples |
| `70-experimental` | 36 | 12 | incubating and planning-stage packages |
| `80-facades` | 1 | 1 | aggregate user-facing facade packages |
| `90-deprecated` | 4 | 1 | deprecated compatibility packages |

## By Layer

### `00-typing`

| Index | Package | Path | Family | Role | Maturity | Workspace |
|---|---|---|---|---|---|---|
| `00.0` | [swarmauri_typing](typing/) | `typing` | `typing` | `atomic-foundation` | `foundation` | yes |

### `10-interfaces`

| Index | Package | Path | Family | Role | Maturity | Workspace |
|---|---|---|---|---|---|---|
| `10.0` | [swarmauri_core](core/) | `core` | `interfaces` | `interface-contract` | `foundation` | yes |

### `20-bases`

| Index | Package | Path | Family | Role | Maturity | Workspace |
|---|---|---|---|---|---|---|
| `20.0` | [swarmauri_base](base/) | `base` | `bases` | `base-implementation` | `foundation` | yes |

### `30-standard-kernel`

| Index | Package | Path | Family | Role | Maturity | Workspace |
|---|---|---|---|---|---|---|
| `30.0` | [swarmauri_standard](swarmauri_standard/) | `swarmauri_standard` | `standard-kernel` | `standard-kernel` | `standard-kernel` | yes |

### `40-standards`

| Index | Package | Path | Family | Role | Maturity | Workspace |
|---|---|---|---|---|---|---|
| `40.0` | [swarmauri_auth_idp_apple](standards/swarmauri_auth_idp_apple/) | `standards/swarmauri_auth_idp_apple` | `auth_idp` | `atomic-concrete` | `standard` | yes |
| `40.0` | [swarmauri_auth_idp_aws](standards/swarmauri_auth_idp_aws/) | `standards/swarmauri_auth_idp_aws` | `auth_idp` | `atomic-concrete` | `standard` | yes |
| `40.0` | [swarmauri_auth_idp_azure](standards/swarmauri_auth_idp_azure/) | `standards/swarmauri_auth_idp_azure` | `auth_idp` | `atomic-concrete` | `standard` | yes |
| `40.0` | [swarmauri_auth_idp_cognito](standards/swarmauri_auth_idp_cognito/) | `standards/swarmauri_auth_idp_cognito` | `auth_idp` | `atomic-concrete` | `standard` | yes |
| `40.0` | [swarmauri_auth_idp_facebook](standards/swarmauri_auth_idp_facebook/) | `standards/swarmauri_auth_idp_facebook` | `auth_idp` | `atomic-concrete` | `standard` | yes |
| `40.0` | [swarmauri_auth_idp_gitea](standards/swarmauri_auth_idp_gitea/) | `standards/swarmauri_auth_idp_gitea` | `auth_idp` | `atomic-concrete` | `standard` | yes |
| `40.0` | [swarmauri_auth_idp_github](standards/swarmauri_auth_idp_github/) | `standards/swarmauri_auth_idp_github` | `auth_idp` | `atomic-concrete` | `standard` | yes |
| `40.0` | [swarmauri_auth_idp_gitlab](standards/swarmauri_auth_idp_gitlab/) | `standards/swarmauri_auth_idp_gitlab` | `auth_idp` | `atomic-concrete` | `standard` | yes |
| `40.0` | [swarmauri_auth_idp_google](standards/swarmauri_auth_idp_google/) | `standards/swarmauri_auth_idp_google` | `auth_idp` | `atomic-concrete` | `standard` | yes |
| `40.0` | [swarmauri_auth_idp_keycloak](standards/swarmauri_auth_idp_keycloak/) | `standards/swarmauri_auth_idp_keycloak` | `auth_idp` | `atomic-concrete` | `standard` | yes |
| `40.0` | [swarmauri_auth_idp_okta](standards/swarmauri_auth_idp_okta/) | `standards/swarmauri_auth_idp_okta` | `auth_idp` | `atomic-concrete` | `standard` | yes |
| `40.0` | [swarmauri_auth_idp_salesforce](standards/swarmauri_auth_idp_salesforce/) | `standards/swarmauri_auth_idp_salesforce` | `auth_idp` | `atomic-concrete` | `standard` | yes |
| `40.0` | [swarmauri_billing_mock](standards/swarmauri_billing_mock/) | `standards/swarmauri_billing_mock` | `billing` | `atomic-concrete` | `standard` | yes |
| `40.0` | [swarmauri_billing_stripe](standards/swarmauri_billing_stripe/) | `standards/swarmauri_billing_stripe` | `billing` | `atomic-concrete` | `standard` | yes |
| `40.0` | [swarmauri_certs_local_ca](standards/swarmauri_certs_local_ca/) | `standards/swarmauri_certs_local_ca` | `certs` | `atomic-concrete` | `standard` | yes |
| `40.0` | [swarmauri_certs_remote_ca](standards/swarmauri_certs_remote_ca/) | `standards/swarmauri_certs_remote_ca` | `certs` | `atomic-concrete` | `standard` | yes |
| `40.0` | [swarmauri_certs_self_signed](standards/swarmauri_certs_self_signed/) | `standards/swarmauri_certs_self_signed` | `certs` | `atomic-concrete` | `standard` | yes |
| `40.0` | [swarmauri_certs_x509verify](standards/swarmauri_certs_x509verify/) | `standards/swarmauri_certs_x509verify` | `certs` | `atomic-concrete` | `standard` | yes |
| `40.0` | [swarmauri_cipher_suite_cades](standards/swarmauri_cipher_suite_cades/) | `standards/swarmauri_cipher_suite_cades` | `cipher_suite` | `atomic-concrete` | `standard` | yes |
| `40.0` | [swarmauri_cipher_suite_cnsa20](standards/swarmauri_cipher_suite_cnsa20/) | `standards/swarmauri_cipher_suite_cnsa20` | `cipher_suite` | `atomic-concrete` | `standard` | yes |
| `40.0` | [swarmauri_cipher_suite_cose](standards/swarmauri_cipher_suite_cose/) | `standards/swarmauri_cipher_suite_cose` | `cipher_suite` | `atomic-concrete` | `standard` | yes |
| `40.0` | [swarmauri_cipher_suite_fips1403](standards/swarmauri_cipher_suite_fips1403/) | `standards/swarmauri_cipher_suite_fips1403` | `cipher_suite` | `atomic-concrete` | `standard` | yes |
| `40.0` | [swarmauri_cipher_suite_fips203](standards/swarmauri_cipher_suite_fips203/) | `standards/swarmauri_cipher_suite_fips203` | `cipher_suite` | `atomic-concrete` | `standard` | yes |
| `40.0` | [swarmauri_cipher_suite_fips204](standards/swarmauri_cipher_suite_fips204/) | `standards/swarmauri_cipher_suite_fips204` | `cipher_suite` | `atomic-concrete` | `standard` | yes |
| `40.0` | [swarmauri_cipher_suite_fips205](standards/swarmauri_cipher_suite_fips205/) | `standards/swarmauri_cipher_suite_fips205` | `cipher_suite` | `atomic-concrete` | `standard` | yes |
| `40.0` | [swarmauri_cipher_suite_ipsec](standards/swarmauri_cipher_suite_ipsec/) | `standards/swarmauri_cipher_suite_ipsec` | `cipher_suite` | `atomic-concrete` | `standard` | yes |
| `40.0` | [swarmauri_cipher_suite_jwa](standards/swarmauri_cipher_suite_jwa/) | `standards/swarmauri_cipher_suite_jwa` | `cipher_suite` | `atomic-concrete` | `standard` | yes |
| `40.0` | [swarmauri_cipher_suite_pades](standards/swarmauri_cipher_suite_pades/) | `standards/swarmauri_cipher_suite_pades` | `cipher_suite` | `atomic-concrete` | `standard` | yes |
| `40.0` | [swarmauri_cipher_suite_pep458](standards/swarmauri_cipher_suite_pep458/) | `standards/swarmauri_cipher_suite_pep458` | `cipher_suite` | `atomic-concrete` | `standard` | yes |
| `40.0` | [swarmauri_cipher_suite_sigstore](standards/swarmauri_cipher_suite_sigstore/) | `standards/swarmauri_cipher_suite_sigstore` | `cipher_suite` | `atomic-concrete` | `standard` | yes |
| `40.0` | [swarmauri_cipher_suite_ssh](standards/swarmauri_cipher_suite_ssh/) | `standards/swarmauri_cipher_suite_ssh` | `cipher_suite` | `atomic-concrete` | `standard` | yes |
| `40.0` | [swarmauri_cipher_suite_tls13](standards/swarmauri_cipher_suite_tls13/) | `standards/swarmauri_cipher_suite_tls13` | `cipher_suite` | `atomic-concrete` | `standard` | yes |
| `40.0` | [swarmauri_cipher_suite_webauthn](standards/swarmauri_cipher_suite_webauthn/) | `standards/swarmauri_cipher_suite_webauthn` | `cipher_suite` | `atomic-concrete` | `standard` | yes |
| `40.0` | [swarmauri_cipher_suite_xades](standards/swarmauri_cipher_suite_xades/) | `standards/swarmauri_cipher_suite_xades` | `cipher_suite` | `atomic-concrete` | `standard` | yes |
| `40.0` | [swarmauri_cipher_suite_yubikey](standards/swarmauri_cipher_suite_yubikey/) | `standards/swarmauri_cipher_suite_yubikey` | `cipher_suite` | `atomic-concrete` | `standard` | yes |
| `40.0` | [swarmauri_cipher_suite_yubikey_fips](standards/swarmauri_cipher_suite_yubikey_fips/) | `standards/swarmauri_cipher_suite_yubikey_fips` | `cipher_suite` | `atomic-concrete` | `standard` | yes |
| `40.0` | [swarmauri_crypto_ecdh_es_a128kw](standards/swarmauri_crypto_ecdh_es_a128kw/) | `standards/swarmauri_crypto_ecdh_es_a128kw` | `crypto` | `atomic-concrete` | `standard` | yes |
| `40.0` | [swarmauri_crypto_jwe](standards/swarmauri_crypto_jwe/) | `standards/swarmauri_crypto_jwe` | `crypto` | `atomic-concrete` | `standard` | yes |
| `40.0` | [swarmauri_crypto_nacl_pkcs11](standards/swarmauri_crypto_nacl_pkcs11/) | `standards/swarmauri_crypto_nacl_pkcs11` | `crypto` | `atomic-concrete` | `standard` | yes |
| `40.0` | [swarmauri_crypto_paramiko](standards/swarmauri_crypto_paramiko/) | `standards/swarmauri_crypto_paramiko` | `crypto` | `atomic-concrete` | `standard` | yes |
| `40.0` | [swarmauri_crypto_pgp](standards/swarmauri_crypto_pgp/) | `standards/swarmauri_crypto_pgp` | `crypto` | `atomic-concrete` | `standard` | yes |
| `40.0` | [swarmauri_crypto_rust](standards/swarmauri_crypto_rust/) | `standards/swarmauri_crypto_rust` | `crypto` | `atomic-concrete` | `standard` | yes |
| `40.0` | [swarmauri_distance_canberra](standards/swarmauri_distance_canberra/) | `standards/swarmauri_distance_canberra` | `distance` | `atomic-concrete` | `standard` | yes |
| `40.0` | [swarmauri_distance_chebyshev](standards/swarmauri_distance_chebyshev/) | `standards/swarmauri_distance_chebyshev` | `distance` | `atomic-concrete` | `standard` | yes |
| `40.0` | [swarmauri_distance_chi_squared](standards/swarmauri_distance_chi_squared/) | `standards/swarmauri_distance_chi_squared` | `distance` | `atomic-concrete` | `standard` | yes |
| `40.0` | [swarmauri_distance_cosine](standards/swarmauri_distance_cosine/) | `standards/swarmauri_distance_cosine` | `distance` | `atomic-concrete` | `standard` | yes |
| `40.0` | [swarmauri_distance_euclidean](standards/swarmauri_distance_euclidean/) | `standards/swarmauri_distance_euclidean` | `distance` | `atomic-concrete` | `standard` | yes |
| `40.0` | [swarmauri_distance_haversine](standards/swarmauri_distance_haversine/) | `standards/swarmauri_distance_haversine` | `distance` | `atomic-concrete` | `standard` | yes |
| `40.0` | [swarmauri_distance_jaccard_index](standards/swarmauri_distance_jaccard_index/) | `standards/swarmauri_distance_jaccard_index` | `distance` | `atomic-concrete` | `standard` | yes |
| `40.0` | [swarmauri_distance_levenshtein](standards/swarmauri_distance_levenshtein/) | `standards/swarmauri_distance_levenshtein` | `distance` | `atomic-concrete` | `standard` | yes |
| `40.0` | [swarmauri_distance_manhattan](standards/swarmauri_distance_manhattan/) | `standards/swarmauri_distance_manhattan` | `distance` | `atomic-concrete` | `standard` | yes |
| `40.0` | [swarmauri_distance_minkowski](standards/swarmauri_distance_minkowski/) | `standards/swarmauri_distance_minkowski` | `distance` | `atomic-concrete` | `standard` | yes |
| `40.0` | [swarmauri_distance_sorensen_dice](standards/swarmauri_distance_sorensen_dice/) | `standards/swarmauri_distance_sorensen_dice` | `distance` | `atomic-concrete` | `standard` | yes |
| `40.0` | [swarmauri_distance_squared_euclidean](standards/swarmauri_distance_squared_euclidean/) | `standards/swarmauri_distance_squared_euclidean` | `distance` | `atomic-concrete` | `standard` | yes |
| `40.0` | [swarmauri_embedding_doc2vec](standards/swarmauri_embedding_doc2vec/) | `standards/swarmauri_embedding_doc2vec` | `embedding` | `atomic-concrete` | `standard` | yes |
| `40.0` | [swarmauri_embedding_nmf](standards/swarmauri_embedding_nmf/) | `standards/swarmauri_embedding_nmf` | `embedding` | `atomic-concrete` | `standard` | yes |
| `40.0` | [swarmauri_evaluator_abstractmethods](standards/swarmauri_evaluator_abstractmethods/) | `standards/swarmauri_evaluator_abstractmethods` | `evaluator` | `atomic-concrete` | `standard` | yes |
| `40.0` | [swarmauri_evaluator_anyusage](standards/swarmauri_evaluator_anyusage/) | `standards/swarmauri_evaluator_anyusage` | `evaluator` | `atomic-concrete` | `standard` | yes |
| `40.0` | [swarmauri_evaluator_constanttime](standards/swarmauri_evaluator_constanttime/) | `standards/swarmauri_evaluator_constanttime` | `evaluator` | `atomic-concrete` | `standard` | yes |
| `40.0` | [swarmauri_evaluator_externalimports](standards/swarmauri_evaluator_externalimports/) | `standards/swarmauri_evaluator_externalimports` | `evaluator` | `atomic-concrete` | `standard` | yes |
| `40.0` | [swarmauri_evaluator_subprocess](standards/swarmauri_evaluator_subprocess/) | `standards/swarmauri_evaluator_subprocess` | `evaluator` | `atomic-concrete` | `standard` | yes |
| `40.0` | [swarmauri_evaluatorpool_accessibility](standards/swarmauri_evaluatorpool_accessibility/) | `standards/swarmauri_evaluatorpool_accessibility` | `evaluatorpool` | `atomic-concrete` | `standard` | yes |
| `40.0` | [swm_example_package](standards/swm_example_package/) | `standards/swm_example_package` | `example` | `atomic-concrete` | `standard` | yes |
| `40.0` | [swarmauri_gitfilter_gh_release](standards/swarmauri_gitfilter_gh_release/) | `standards/swarmauri_gitfilter_gh_release` | `gitfilter` | `atomic-concrete` | `standard` | yes |
| `40.0` | [swarmauri_gitfilter_minio](standards/swarmauri_gitfilter_minio/) | `standards/swarmauri_gitfilter_minio` | `gitfilter` | `atomic-concrete` | `standard` | yes |
| `40.0` | [swarmauri_gitfilter_s3fs](standards/swarmauri_gitfilter_s3fs/) | `standards/swarmauri_gitfilter_s3fs` | `gitfilter` | `atomic-concrete` | `standard` | yes |
| `40.0` | [swarmauri_keyprovider_file](standards/swarmauri_keyprovider_file/) | `standards/swarmauri_keyprovider_file` | `keyprovider` | `atomic-concrete` | `standard` | yes |
| `40.0` | [swarmauri_keyprovider_inmemory](standards/swarmauri_keyprovider_inmemory/) | `standards/swarmauri_keyprovider_inmemory` | `keyprovider` | `atomic-concrete` | `standard` | yes |
| `40.0` | [swarmauri_keyprovider_local](standards/swarmauri_keyprovider_local/) | `standards/swarmauri_keyprovider_local` | `keyprovider` | `atomic-concrete` | `standard` | yes |
| `40.0` | [swarmauri_keyprovider_ssh](standards/swarmauri_keyprovider_ssh/) | `standards/swarmauri_keyprovider_ssh` | `keyprovider` | `atomic-concrete` | `standard` | yes |
| `40.0` | [swamauri_metric_wasserstein](standards/swamauri_metric_wasserstein/) | `standards/swamauri_metric_wasserstein` | `metric` | `atomic-concrete` | `standard` | yes |
| `40.0` | [swarmauri_middleware_bulkhead](standards/swarmauri_middleware_bulkhead/) | `standards/swarmauri_middleware_bulkhead` | `middleware` | `atomic-concrete` | `standard` | yes |
| `40.0` | [swarmauri_middleware_cachecontrol](standards/swarmauri_middleware_cachecontrol/) | `standards/swarmauri_middleware_cachecontrol` | `middleware` | `atomic-concrete` | `standard` | yes |
| `40.0` | [swarmauri_middleware_cors](standards/swarmauri_middleware_cors/) | `standards/swarmauri_middleware_cors` | `middleware` | `atomic-concrete` | `standard` | yes |
| `40.0` | [swarmauri_middleware_exceptionhandling](standards/swarmauri_middleware_exceptionhandling/) | `standards/swarmauri_middleware_exceptionhandling` | `middleware` | `atomic-concrete` | `standard` | yes |
| `40.0` | [swarmauri_middleware_gzipcompression](standards/swarmauri_middleware_gzipcompression/) | `standards/swarmauri_middleware_gzipcompression` | `middleware` | `atomic-concrete` | `standard` | yes |
| `40.0` | [swarmauri_middleware_httpsig](standards/swarmauri_middleware_httpsig/) | `standards/swarmauri_middleware_httpsig` | `middleware` | `atomic-concrete` | `standard` | yes |
| `40.0` | [swarmauri_middleware_jsonrpc](standards/swarmauri_middleware_jsonrpc/) | `standards/swarmauri_middleware_jsonrpc` | `middleware` | `atomic-concrete` | `standard` | yes |
| `40.0` | [swarmauri_middleware_jwksverifier](standards/swarmauri_middleware_jwksverifier/) | `standards/swarmauri_middleware_jwksverifier` | `middleware` | `atomic-concrete` | `standard` | yes |
| `40.0` | [swarmauri_middleware_jwt](standards/swarmauri_middleware_jwt/) | `standards/swarmauri_middleware_jwt` | `middleware` | `atomic-concrete` | `standard` | yes |
| `40.0` | [swarmauri_middleware_llamaguard](standards/swarmauri_middleware_llamaguard/) | `standards/swarmauri_middleware_llamaguard` | `middleware` | `atomic-concrete` | `standard` | yes |
| `40.0` | [swarmauri_middleware_logging](standards/swarmauri_middleware_logging/) | `standards/swarmauri_middleware_logging` | `middleware` | `atomic-concrete` | `standard` | yes |
| `40.0` | [swarmauri_middleware_ratelimit](standards/swarmauri_middleware_ratelimit/) | `standards/swarmauri_middleware_ratelimit` | `middleware` | `atomic-concrete` | `standard` | yes |
| `40.0` | [swarmauri_middleware_securityheaders](standards/swarmauri_middleware_securityheaders/) | `standards/swarmauri_middleware_securityheaders` | `middleware` | `atomic-concrete` | `standard` | yes |
| `40.0` | [swarmauri_middleware_session](standards/swarmauri_middleware_session/) | `standards/swarmauri_middleware_session` | `middleware` | `atomic-concrete` | `standard` | yes |
| `40.0` | [swarmauri_middleware_stdio](standards/swarmauri_middleware_stdio/) | `standards/swarmauri_middleware_stdio` | `middleware` | `atomic-concrete` | `standard` | yes |
| `40.0` | [swarmauri_middleware_time](standards/swarmauri_middleware_time/) | `standards/swarmauri_middleware_time` | `middleware` | `atomic-concrete` | `standard` | yes |
| `40.0` | [swarmauri_mre_crypto_age](standards/swarmauri_mre_crypto_age/) | `standards/swarmauri_mre_crypto_age` | `mre_crypto` | `atomic-concrete` | `standard` | yes |
| `40.0` | [swarmauri_mre_crypto_ecdh_es_kw](standards/swarmauri_mre_crypto_ecdh_es_kw/) | `standards/swarmauri_mre_crypto_ecdh_es_kw` | `mre_crypto` | `atomic-concrete` | `standard` | yes |
| `40.0` | [swarmauri_mre_crypto_keyring](standards/swarmauri_mre_crypto_keyring/) | `standards/swarmauri_mre_crypto_keyring` | `mre_crypto` | `atomic-concrete` | `standard` | yes |
| `40.0` | [swarmauri_mre_crypto_pgp](standards/swarmauri_mre_crypto_pgp/) | `standards/swarmauri_mre_crypto_pgp` | `mre_crypto` | `atomic-concrete` | `standard` | yes |
| `40.0` | [swarmauri_mre_crypto_shamir](standards/swarmauri_mre_crypto_shamir/) | `standards/swarmauri_mre_crypto_shamir` | `mre_crypto` | `atomic-concrete` | `standard` | yes |
| `40.0` | [swarmauri_parser_beautifulsoupelement](standards/swarmauri_parser_beautifulsoupelement/) | `standards/swarmauri_parser_beautifulsoupelement` | `parser` | `atomic-concrete` | `standard` | yes |
| `40.0` | [swarmauri_parser_keywordextractor](standards/swarmauri_parser_keywordextractor/) | `standards/swarmauri_parser_keywordextractor` | `parser` | `atomic-concrete` | `standard` | yes |
| `40.0` | [swarmauri_pop_cwt](standards/swarmauri_pop_cwt/) | `standards/swarmauri_pop_cwt` | `pop` | `atomic-concrete` | `standard` | yes |
| `40.0` | [swarmauri_pop_dpop](standards/swarmauri_pop_dpop/) | `…37048 tokens truncated…_tokens_dpopboundjwt/) | `40-standards` | `standards/swarmauri_tokens_dpopboundjwt` | `atomic-concrete` | `standard` | yes |
| `40.0` | [swarmauri_tokens_introspection](standards/swarmauri_tokens_introspection/) | `40-standards` | `standards/swarmauri_tokens_introspection` | `atomic-concrete` | `standard` | yes |
| `40.0` | [swarmauri_tokens_paseto_v4](standards/swarmauri_tokens_paseto_v4/) | `40-standards` | `standards/swarmauri_tokens_paseto_v4` | `atomic-concrete` | `standard` | yes |
| `40.0` | [swarmauri_tokens_remoteoidc](standards/swarmauri_tokens_remoteoidc/) | `40-standards` | `standards/swarmauri_tokens_remoteoidc` | `atomic-concrete` | `standard` | yes |
| `40.0` | [swarmauri_tokens_rotatingjwt](standards/swarmauri_tokens_rotatingjwt/) | `40-standards` | `standards/swarmauri_tokens_rotatingjwt` | `atomic-concrete` | `standard` | yes |
| `40.0` | [swarmauri_tokens_sshcert](standards/swarmauri_tokens_sshcert/) | `40-standards` | `standards/swarmauri_tokens_sshcert` | `atomic-concrete` | `standard` | yes |
| `40.0` | [swarmauri_tokens_sshsig](standards/swarmauri_tokens_sshsig/) | `40-standards` | `standards/swarmauri_tokens_sshsig` | `atomic-concrete` | `standard` | yes |
| `40.0` | [swarmauri_tokens_tlsboundjwt](standards/swarmauri_tokens_tlsboundjwt/) | `40-standards` | `standards/swarmauri_tokens_tlsboundjwt` | `atomic-concrete` | `standard` | yes |
| `40.1` | [swarmauri_tokens_composite](standards/swarmauri_tokens_composite/) | `40-standards` | `standards/swarmauri_tokens_composite` | `composite-concrete` | `standard` | yes |
| `40.2` | [swarmauri_tokens_jwt](standards/swarmauri_tokens_jwt/) | `40-standards` | `standards/swarmauri_tokens_jwt` | `orchestrator` | `standard` | yes |

### `tool`

| Index | Package | Layer | Path | Role | Maturity | Workspace |
|---|---|---|---|---|---|---|
| `40.0` | [swarmauri_tool_containerfeedchars](standards/swarmauri_tool_containerfeedchars/) | `40-standards` | `standards/swarmauri_tool_containerfeedchars` | `atomic-concrete` | `standard` | yes |
| `40.0` | [swarmauri_tool_containermakepr](standards/swarmauri_tool_containermakepr/) | `40-standards` | `standards/swarmauri_tool_containermakepr` | `atomic-concrete` | `standard` | yes |
| `40.0` | [swarmauri_tool_containernewsession](standards/swarmauri_tool_containernewsession/) | `40-standards` | `standards/swarmauri_tool_containernewsession` | `atomic-concrete` | `standard` | yes |
| `40.0` | [swarmauri_tool_githubloader](standards/swarmauri_tool_githubloader/) | `40-standards` | `standards/swarmauri_tool_githubloader` | `atomic-concrete` | `standard` | yes |
| `40.0` | [swarmauri_tool_httploaded](standards/swarmauri_tool_httploaded/) | `40-standards` | `standards/swarmauri_tool_httploaded` | `atomic-concrete` | `standard` | yes |
| `40.0` | [swarmauri_tool_matplotlib](standards/swarmauri_tool_matplotlib/) | `40-standards` | `standards/swarmauri_tool_matplotlib` | `atomic-concrete` | `standard` | yes |
| `40.0` | [swarmauri_tool_skill_execution](standards/swarmauri_tool_skill_execution/) | `40-standards` | `standards/swarmauri_tool_skill_execution` | `atomic-concrete` | `standard` | yes |
| `50.0` | [swarmauri_tool_captchagenerator](community/swarmauri_tool_captchagenerator/) | `50-community` | `community/swarmauri_tool_captchagenerator` | `atomic-concrete` | `community` | yes |
| `50.0` | [swarmauri_tool_dalechallreadability](community/swarmauri_tool_dalechallreadability/) | `50-community` | `community/swarmauri_tool_dalechallreadability` | `atomic-concrete` | `community` | yes |
| `50.0` | [swarmauri_tool_downloadpdf](community/swarmauri_tool_downloadpdf/) | `50-community` | `community/swarmauri_tool_downloadpdf` | `atomic-concrete` | `community` | yes |
| `50.0` | [swarmauri_tool_entityrecognition](community/swarmauri_tool_entityrecognition/) | `50-community` | `community/swarmauri_tool_entityrecognition` | `atomic-concrete` | `community` | yes |
| `50.0` | [swarmauri_tool_folium](community/swarmauri_tool_folium/) | `50-community` | `community/swarmauri_tool_folium` | `atomic-concrete` | `community` | yes |
| `50.0` | [swarmauri_tool_getmethodsignature](community/swarmauri_tool_getmethodsignature/) | `50-community` | `community/swarmauri_tool_getmethodsignature` | `atomic-concrete` | `community` | yes |
| `50.0` | [swarmauri_tool_gmail](community/swarmauri_tool_gmail/) | `50-community` | `community/swarmauri_tool_gmail` | `atomic-concrete` | `community` | yes |
| `50.0` | [swarmauri_tool_jupyterclearoutput](community/swarmauri_tool_jupyterclearoutput/) | `50-community` | `community/swarmauri_tool_jupyterclearoutput` | `atomic-concrete` | `community` | yes |
| `50.0` | [swarmauri_tool_jupyterdisplay](community/swarmauri_tool_jupyterdisplay/) | `50-community` | `community/swarmauri_tool_jupyterdisplay` | `atomic-concrete` | `community` | yes |
| `50.0` | [swarmauri_tool_jupyterdisplayhtml](community/swarmauri_tool_jupyterdisplayhtml/) | `50-community` | `community/swarmauri_tool_jupyterdisplayhtml` | `atomic-concrete` | `community` | yes |
| `50.0` | [swarmauri_tool_jupyterexecuteandconvert](community/swarmauri_tool_jupyterexecuteandconvert/) | `50-community` | `community/swarmauri_tool_jupyterexecuteandconvert` | `atomic-concrete` | `community` | yes |
| `50.0` | [swarmauri_tool_jupyterexecutecell](community/swarmauri_tool_jupyterexecutecell/) | `50-community` | `community/swarmauri_tool_jupyterexecutecell` | `atomic-concrete` | `community` | yes |
| `50.0` | [swarmauri_tool_jupyterexecutenotebook](community/swarmauri_tool_jupyterexecutenotebook/) | `50-community` | `community/swarmauri_tool_jupyterexecutenotebook` | `atomic-concrete` | `community` | yes |
| `50.0` | [swarmauri_tool_jupyterexecutenotebookwithparameters](community/swarmauri_tool_jupyterexecutenotebookwithparameters/) | `50-community` | `community/swarmauri_tool_jupyterexecutenotebookwithparameters` | `atomic-concrete` | `community` | yes |
| `50.0` | [swarmauri_tool_jupyterexporthtml](community/swarmauri_tool_jupyterexporthtml/) | `50-community` | `community/swarmauri_tool_jupyterexporthtml` | `atomic-concrete` | `community` | yes |
| `50.0` | [swarmauri_tool_jupyterexportlatex](community/swarmauri_tool_jupyterexportlatex/) | `50-community` | `community/swarmauri_tool_jupyterexportlatex` | `atomic-concrete` | `community` | yes |
| `50.0` | [swarmauri_tool_jupyterexportmarkdown](community/swarmauri_tool_jupyterexportmarkdown/) | `50-community` | `community/swarmauri_tool_jupyterexportmarkdown` | `atomic-concrete` | `community` | yes |
| `50.0` | [swarmauri_tool_jupyterexportpython](community/swarmauri_tool_jupyterexportpython/) | `50-community` | `community/swarmauri_tool_jupyterexportpython` | `atomic-concrete` | `community` | yes |
| `50.0` | [swarmauri_tool_jupyterfromdict](community/swarmauri_tool_jupyterfromdict/) | `50-community` | `community/swarmauri_tool_jupyterfromdict` | `atomic-concrete` | `community` | yes |
| `50.0` | [swarmauri_tool_jupytergetiopubmessage](community/swarmauri_tool_jupytergetiopubmessage/) | `50-community` | `community/swarmauri_tool_jupytergetiopubmessage` | `atomic-concrete` | `community` | yes |
| `50.0` | [swarmauri_tool_jupytergetshellmessage](community/swarmauri_tool_jupytergetshellmessage/) | `50-community` | `community/swarmauri_tool_jupytergetshellmessage` | `atomic-concrete` | `community` | yes |
| `50.0` | [swarmauri_tool_jupyterreadnotebook](community/swarmauri_tool_jupyterreadnotebook/) | `50-community` | `community/swarmauri_tool_jupyterreadnotebook` | `atomic-concrete` | `community` | yes |
| `50.0` | [swarmauri_tool_jupyterruncell](community/swarmauri_tool_jupyterruncell/) | `50-community` | `community/swarmauri_tool_jupyterruncell` | `atomic-concrete` | `community` | yes |
| `50.0` | [swarmauri_tool_jupytershutdownkernel](community/swarmauri_tool_jupytershutdownkernel/) | `50-community` | `community/swarmauri_tool_jupytershutdownkernel` | `atomic-concrete` | `community` | yes |
| `50.0` | [swarmauri_tool_jupyterstartkernel](community/swarmauri_tool_jupyterstartkernel/) | `50-community` | `community/swarmauri_tool_jupyterstartkernel` | `atomic-concrete` | `community` | yes |
| `50.0` | [swarmauri_tool_jupytervalidatenotebook](community/swarmauri_tool_jupytervalidatenotebook/) | `50-community` | `community/swarmauri_tool_jupytervalidatenotebook` | `atomic-concrete` | `community` | yes |
| `50.0` | [swarmauri_tool_jupyterwritenotebook](community/swarmauri_tool_jupyterwritenotebook/) | `50-community` | `community/swarmauri_tool_jupyterwritenotebook` | `atomic-concrete` | `community` | yes |
| `50.0` | [swarmauri_tool_lexicaldensity](community/swarmauri_tool_lexicaldensity/) | `50-community` | `community/swarmauri_tool_lexicaldensity` | `atomic-concrete` | `community` | yes |
| `50.0` | [swarmauri_tool_psutil](community/swarmauri_tool_psutil/) | `50-community` | `community/swarmauri_tool_psutil` | `atomic-concrete` | `community` | yes |
| `50.0` | [swarmauri_tool_qrcodegenerator](community/swarmauri_tool_qrcodegenerator/) | `50-community` | `community/swarmauri_tool_qrcodegenerator` | `atomic-concrete` | `community` | yes |
| `50.0` | [swarmauri_tool_queryimagevectorstore](community/swarmauri_tool_queryimagevectorstore/) | `50-community` | `community/swarmauri_tool_queryimagevectorstore` | `atomic-concrete` | `community` | yes |
| `50.0` | [swarmauri_tool_queryknowledgebase](community/swarmauri_tool_queryknowledgebase/) | `50-community` | `community/swarmauri_tool_queryknowledgebase` | `atomic-concrete` | `community` | yes |
| `50.0` | [swarmauri_tool_searchword](community/swarmauri_tool_searchword/) | `50-community` | `community/swarmauri_tool_searchword` | `atomic-concrete` | `community` | yes |
| `50.0` | [swarmauri_tool_sentencecomplexity](community/swarmauri_tool_sentencecomplexity/) | `50-community` | `community/swarmauri_tool_sentencecomplexity` | `atomic-concrete` | `community` | yes |
| `50.0` | [swarmauri_tool_sentimentanalysis](community/swarmauri_tool_sentimentanalysis/) | `50-community` | `community/swarmauri_tool_sentimentanalysis` | `atomic-concrete` | `community` | yes |
| `50.0` | [swarmauri_tool_smogindex](community/swarmauri_tool_smogindex/) | `50-community` | `community/swarmauri_tool_smogindex` | `atomic-concrete` | `community` | yes |
| `50.0` | [swarmauri_tool_textlength](community/swarmauri_tool_textlength/) | `50-community` | `community/swarmauri_tool_textlength` | `atomic-concrete` | `community` | yes |
| `50.0` | [swarmauri_tool_webscraping](community/swarmauri_tool_webscraping/) | `50-community` | `community/swarmauri_tool_webscraping` | `atomic-concrete` | `community` | yes |
| `50.0` | [swarmauri_tool_zapierhook](community/swarmauri_tool_zapierhook/) | `50-community` | `community/swarmauri_tool_zapierhook` | `atomic-concrete` | `community` | yes |

### `toolkit`

| Index | Package | Layer | Path | Role | Maturity | Workspace |
|---|---|---|---|---|---|---|
| `40.2` | [swarmauri_toolkit_containertoolkit](standards/swarmauri_toolkit_containertoolkit/) | `40-standards` | `standards/swarmauri_toolkit_containertoolkit` | `orchestrator` | `standard` | yes |
| `40.2` | [swarmauri_toolkit_runtime](standards/swarmauri_toolkit_runtime/) | `40-standards` | `standards/swarmauri_toolkit_runtime` | `orchestrator` | `standard` | yes |
| `50.2` | [swarmauri_toolkit_github](community/swarmauri_toolkit_github/) | `50-community` | `community/swarmauri_toolkit_github` | `orchestrator` | `community` | yes |
| `50.2` | [swarmauri_toolkit_jupytertoolkit](community/swarmauri_toolkit_jupytertoolkit/) | `50-community` | `community/swarmauri_toolkit_jupytertoolkit` | `orchestrator` | `community` | yes |

### `transport`

| Index | Package | Layer | Path | Role | Maturity | Workspace |
|---|---|---|---|---|---|---|
| `40.0` | [swarmauri_transport_asgi](standards/swarmauri_transport_asgi/) | `40-standards` | `standards/swarmauri_transport_asgi` | `atomic-concrete` | `standard` | yes |
| `40.0` | [swarmauri_transport_h2](standards/swarmauri_transport_h2/) | `40-standards` | `standards/swarmauri_transport_h2` | `atomic-concrete` | `standard` | yes |
| `40.0` | [swarmauri_transport_h2mux](standards/swarmauri_transport_h2mux/) | `40-standards` | `standards/swarmauri_transport_h2mux` | `atomic-concrete` | `standard` | yes |
| `40.0` | [swarmauri_transport_meshsidecarhttp2](standards/swarmauri_transport_meshsidecarhttp2/) | `40-standards` | `standards/swarmauri_transport_meshsidecarhttp2` | `atomic-concrete` | `standard` | yes |
| `40.0` | [swarmauri_transport_mtlsunicast](standards/swarmauri_transport_mtlsunicast/) | `40-standards` | `standards/swarmauri_transport_mtlsunicast` | `atomic-concrete` | `standard` | yes |
| `40.0` | [swarmauri_transport_quic](standards/swarmauri_transport_quic/) | `40-standards` | `standards/swarmauri_transport_quic` | `atomic-concrete` | `standard` | yes |
| `40.0` | [swarmauri_transport_sseoutbound](standards/swarmauri_transport_sseoutbound/) | `40-standards` | `standards/swarmauri_transport_sseoutbound` | `atomic-concrete` | `standard` | yes |
| `40.0` | [swarmauri_transport_sshtunnel](standards/swarmauri_transport_sshtunnel/) | `40-standards` | `standards/swarmauri_transport_sshtunnel` | `atomic-concrete` | `standard` | yes |
| `40.0` | [swarmauri_transport_stdio](standards/swarmauri_transport_stdio/) | `40-standards` | `standards/swarmauri_transport_stdio` | `atomic-concrete` | `standard` | yes |
| `40.0` | [swarmauri_transport_tcpunicast](standards/swarmauri_transport_tcpunicast/) | `40-standards` | `standards/swarmauri_transport_tcpunicast` | `atomic-concrete` | `standard` | yes |
| `40.0` | [swarmauri_transport_tls_unicast](standards/swarmauri_transport_tls_unicast/) | `40-standards` | `standards/swarmauri_transport_tls_unicast` | `atomic-concrete` | `standard` | yes |
| `40.0` | [swarmauri_transport_udp](standards/swarmauri_transport_udp/) | `40-standards` | `standards/swarmauri_transport_udp` | `atomic-concrete` | `standard` | yes |
| `40.0` | [swarmauri_transport_uds_unicast](standards/swarmauri_transport_uds_unicast/) | `40-standards` | `standards/swarmauri_transport_uds_unicast` | `atomic-concrete` | `standard` | yes |
| `40.0` | [swarmauri_transport_wsjsonrpcmux](standards/swarmauri_transport_wsjsonrpcmux/) | `40-standards` | `standards/swarmauri_transport_wsjsonrpcmux` | `atomic-concrete` | `standard` | yes |
| `40.2` | [swarmauri_transport_https_unicast](standards/swarmauri_transport_https_unicast/) | `40-standards` | `standards/swarmauri_transport_https_unicast` | `orchestrator` | `standard` | yes |

### `typing`

| Index | Package | Layer | Path | Role | Maturity | Workspace |
|---|---|---|---|---|---|---|
| `00.0` | [swarmauri_typing](typing/) | `00-typing` | `typing` | `atomic-foundation` | `foundation` | yes |

### `vectorstore`

| Index | Package | Layer | Path | Role | Maturity | Workspace |
|---|---|---|---|---|---|---|
| `40.1` | [swarmauri_vectorstore_doc2vec](standards/swarmauri_vectorstore_doc2vec/) | `40-standards` | `standards/swarmauri_vectorstore_doc2vec` | `composite-concrete` | `standard` | yes |
| `50.0` | [swarmauri_vectorstore_annoy](community/swarmauri_vectorstore_annoy/) | `50-community` | `community/swarmauri_vectorstore_annoy` | `atomic-concrete` | `community` | yes |
| `50.0` | [swarmauri_vectorstore_cloudweaviate](community/swarmauri_vectorstore_cloudweaviate/) | `50-community` | `community/swarmauri_vectorstore_cloudweaviate` | `atomic-concrete` | `community` | yes |
| `50.0` | [swarmauri_vectorstore_duckdb](community/swarmauri_vectorstore_duckdb/) | `50-community` | `community/swarmauri_vectorstore_duckdb` | `atomic-concrete` | `community` | yes |
| `50.0` | [swarmauri_vectorstore_fs](community/swarmauri_vectorstore_fs/) | `50-community` | `community/swarmauri_vectorstore_fs` | `atomic-concrete` | `community` | yes |
| `50.0` | [swarmauri_vectorstore_git](community/swarmauri_vectorstore_git/) | `50-community` | `community/swarmauri_vectorstore_git` | `atomic-concrete` | `community` | yes |
| `50.0` | [swarmauri_vectorstore_neo4j](community/swarmauri_vectorstore_neo4j/) | `50-community` | `community/swarmauri_vectorstore_neo4j` | `atomic-concrete` | `community` | yes |
| `50.0` | [swarmauri_vectorstore_persistentchromadb](community/swarmauri_vectorstore_persistentchromadb/) | `50-community` | `community/swarmauri_vectorstore_persistentchromadb` | `atomic-concrete` | `community` | yes |
| `50.0` | [swarmauri_vectorstore_pinecone](community/swarmauri_vectorstore_pinecone/) | `50-community` | `community/swarmauri_vectorstore_pinecone` | `atomic-concrete` | `community` | yes |
| `50.0` | [swarmauri_vectorstore_qdrant](community/swarmauri_vectorstore_qdrant/) | `50-community` | `community/swarmauri_vectorstore_qdrant` | `atomic-concrete` | `community` | yes |
| `50.0` | [swarmauri_vectorstore_redis](community/swarmauri_vectorstore_redis/) | `50-community` | `community/swarmauri_vectorstore_redis` | `atomic-concrete` | `community` | yes |
| `50.1` | [swarmauri_vectorstore_mlm](community/swarmauri_vectorstore_mlm/) | `50-community` | `community/swarmauri_vectorstore_mlm` | `composite-concrete` | `community` | yes |
| `90.1` | [swarmauri_vectorstore_tfidf](deprecated/swarmauri_vectorstore_tfidf/) | `90-deprecated` | `deprecated/swarmauri_vectorstore_tfidf` | `compat-composite` | `deprecated` | no |

### `workflow`

| Index | Package | Layer | Path | Role | Maturity | Workspace |
|---|---|---|---|---|---|---|
| `70.2` | [swarmauri_workflow_statedriven](experimental/swarmauri_workflow_statedriven/) | `70-experimental` | `experimental/swarmauri_workflow_statedriven` | `experimental-orchestrator` | `experimental` | yes |

### `xmp`

| Index | Package | Layer | Path | Role | Maturity | Workspace |
|---|---|---|---|---|---|---|
| `40.0` | [swarmauri_xmp_gif](standards/swarmauri_xmp_gif/) | `40-standards` | `standards/swarmauri_xmp_gif` | `atomic-concrete` | `standard` | yes |
| `40.0` | [swarmauri_xmp_jpeg](standards/swarmauri_xmp_jpeg/) | `40-standards` | `standards/swarmauri_xmp_jpeg` | `atomic-concrete` | `standard` | yes |
| `40.0` | [swarmauri_xmp_mp4](standards/swarmauri_xmp_mp4/) | `40-standards` | `standards/swarmauri_xmp_mp4` | `atomic-concrete` | `standard` | yes |
| `40.0` | [swarmauri_xmp_pdf](standards/swarmauri_xmp_pdf/) | `40-standards` | `standards/swarmauri_xmp_pdf` | `atomic-concrete` | `standard` | yes |
| `40.0` | [swarmauri_xmp_png](standards/swarmauri_xmp_png/) | `40-standards` | `standards/swarmauri_xmp_png` | `atomic-concrete` | `standard` | yes |
| `40.0` | [swarmauri_xmp_svg](standards/swarmauri_xmp_svg/) | `40-standards` | `standards/swarmauri_xmp_svg` | `atomic-concrete` | `standard` | yes |
| `40.0` | [swarmauri_xmp_tiff](standards/swarmauri_xmp_tiff/) | `40-standards` | `standards/swarmauri_xmp_tiff` | `atomic-concrete` | `standard` | yes |
| `40.0` | [swarmauri_xmp_webp](standards/swarmauri_xmp_webp/) | `40-standards` | `standards/swarmauri_xmp_webp` | `atomic-concrete` | `standard` | yes |

### `ye`

| Index | Package | Layer | Path | Role | Maturity | Workspace |
|---|---|---|---|---|---|---|
| `70.0` | [ye](experimental/ye/) | `70-experimental` | `experimental/ye` | `experimental-atomic` | `experimental` | no |

### `ymls`

| Index | Package | Layer | Path | Role | Maturity | Workspace |
|---|---|---|---|---|---|---|
| `70.0` | [ymls](experimental/ymls/) | `70-experimental` | `experimental/ymls` | `experimental-atomic` | `experimental` | no |

### `zdx`

| Index | Package | Layer | Path | Role | Maturity | Workspace |
|---|---|---|---|---|---|---|
| `60.0` | [zdx](plugins/zdx/) | `60-plugins` | `plugins/zdx` | `plugin` | `plugin` | yes |

### `zr0`

| Index | Package | Layer | Path | Role | Maturity | Workspace |
|---|---|---|---|---|---|---|
| `70.0` | [zr0](experimental/zr0/) | `70-experimental` | `experimental/zr0` | `experimental-atomic` | `experimental` | no |
