# Swarmauri Package Index

Generated from [`index.toml`](../index.toml). Package paths follow
`pkgs/<layer>/` and preserve distribution names and import roots.

Index values are displayed as `layer.order`, where `layer` captures package
citizenship/dependency band and `order` captures composition depth. A
same-layer package that composes another package is indexed at a higher
order than the package it composes.

Order is `explicit` when `index.toml` carries an intentional
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
| `40-standards` | 238 | 238 | first-party split standard packages |
| `50-community` | 130 | 130 | community and provider-specific packages |
| `60-plugins` | 5 | 5 | plugin packages and plugin examples |
| `70-experimental` | 45 | 13 | incubating and planning-stage packages |
| `80-facades` | 1 | 1 | aggregate user-facing facade packages |
| `90-deprecated` | 6 | 3 | deprecated compatibility packages |

## By Layer

### `00-typing`

| Index | Package | Path | Family | Role | Maturity | Workspace |
|---|---|---|---|---|---|---|
| `00.0` | [swarmauri_typing](00-typing/swarmauri_typing/) | `00-typing/swarmauri_typing` | `typing` | `atomic-foundation` | `foundation` | yes |

### `10-interfaces`

| Index | Package | Path | Family | Role | Maturity | Workspace |
|---|---|---|---|---|---|---|
| `10.0` | [swarmauri_core](10-interfaces/swarmauri_core/) | `10-interfaces/swarmauri_core` | `interfaces` | `interface-contract` | `foundation` | yes |

### `20-bases`

| Index | Package | Path | Family | Role | Maturity | Workspace |
|---|---|---|---|---|---|---|
| `20.0` | [swarmauri_base](20-bases/swarmauri_base/) | `20-bases/swarmauri_base` | `bases` | `base-implementation` | `foundation` | yes |

### `30-standard-kernel`

| Index | Package | Path | Family | Role | Maturity | Workspace |
|---|---|---|---|---|---|---|
| `30.0` | [swarmauri_standard](30-standard-kernel/swarmauri_standard/) | `30-standard-kernel/swarmauri_standard` | `standard-kernel` | `standard-kernel` | `standard-kernel` | yes |

### `40-standards`

| Index | Package | Path | Family | Role | Maturity | Workspace |
|---|---|---|---|---|---|---|
| `40.0` | [swarmauri_agent_compacting](40-standards/swarmauri_agent_compacting/) | `40-standards/swarmauri_agent_compacting` | `agent` | `atomic-concrete` | `standard` | yes |
| `40.0` | [swarmauri_agent_package_maintenance](40-standards/swarmauri_agent_package_maintenance/) | `40-standards/swarmauri_agent_package_maintenance` | `agent` | `atomic-concrete` | `standard` | yes |
| `40.0` | [swarmauri_agent_realtime](40-standards/swarmauri_agent_realtime/) | `40-standards/swarmauri_agent_realtime` | `agent` | `atomic-concrete` | `standard` | yes |
| `40.0` | [swarmauri_agent_runner](40-standards/swarmauri_agent_runner/) | `40-standards/swarmauri_agent_runner` | `agent` | `atomic-concrete` | `standard` | yes |
| `40.0` | [swarmauri_agent_skill](40-standards/swarmauri_agent_skill/) | `40-standards/swarmauri_agent_skill` | `agent` | `atomic-concrete` | `standard` | yes |
| `40.0` | [swarmauri_agent_texttospeech](40-standards/swarmauri_agent_texttospeech/) | `40-standards/swarmauri_agent_texttospeech` | `agent` | `atomic-concrete` | `standard` | yes |
| `40.0` | [swarmauri_agent_wimse](40-standards/swarmauri_agent_wimse/) | `40-standards/swarmauri_agent_wimse` | `agent` | `atomic-concrete` | `standard` | yes |
| `40.0` | [swarmauri_auth_idp_apple](40-standards/swarmauri_auth_idp_apple/) | `40-standards/swarmauri_auth_idp_apple` | `auth_idp` | `atomic-concrete` | `standard` | yes |
| `40.0` | [swarmauri_auth_idp_aws](40-standards/swarmauri_auth_idp_aws/) | `40-standards/swarmauri_auth_idp_aws` | `auth_idp` | `atomic-concrete` | `standard` | yes |
| `40.0` | [swarmauri_auth_idp_azure](40-standards/swarmauri_auth_idp_azure/) | `40-standards/swarmauri_auth_idp_azure` | `auth_idp` | `atomic-concrete` | `standard` | yes |
| `40.0` | [swarmauri_auth_idp_cognito](40-standards/swarmauri_auth_idp_cognito/) | `40-standards/swarmauri_auth_idp_cognito` | `auth_idp` | `atomic-concrete` | `standard` | yes |
| `40.0` | [swarmauri_auth_idp_facebook](40-standards/swarmauri_auth_idp_facebook/) | `40-standards/swarmauri_auth_idp_facebook` | `auth_idp` | `atomic-concrete` | `standard` | yes |
| `40.0` | [swarmauri_auth_idp_gitea](40-standards/swarmauri_auth_idp_gitea/) | `40-standards/swarmauri_auth_idp_gitea` | `auth_idp` | `atomic-concrete` | `standard` | yes |
| `40.0` | [swarmauri_auth_idp_github](40-standards/swarmauri_auth_idp_github/) | `40-standards/swarmauri_auth_idp_github` | `auth_idp` | `atomic-concrete` | `standard` | yes |
| `40.0` | [swarmauri_auth_idp_gitlab](40-standards/swarmauri_auth_idp_gitlab/) | `40-standards/swarmauri_auth_idp_gitlab` | `auth_idp` | `atomic-concrete` | `standard` | yes |
| `40.0` | [swarmauri_auth_idp_google](40-standards/swarmauri_auth_idp_google/) | `40-standards/swarmauri_auth_idp_google` | `auth_idp` | `atomic-concrete` | `standard` | yes |
| `40.0` | [swarmauri_auth_idp_keycloak](40-standards/swarmauri_auth_idp_keycloak/) | `40-standards/swarmauri_auth_idp_keycloak` | `auth_idp` | `atomic-concrete` | `standard` | yes |
| `40.0` | [swarmauri_auth_idp_okta](40-standards/swarmauri_auth_idp_okta/) | `40-standards/swarmauri_auth_idp_okta` | `auth_idp` | `atomic-concrete` | `standard` | yes |
| `40.0` | [swarmauri_auth_idp_salesforce](40-standards/swarmauri_auth_idp_salesforce/) | `40-standards/swarmauri_auth_idp_salesforce` | `auth_idp` | `atomic-concrete` | `standard` | yes |
| `40.0` | [swarmauri_billing_mock](40-standards/swarmauri_billing_mock/) | `40-standards/swarmauri_billing_mock` | `billing` | `atomic-concrete` | `standard` | yes |
| `40.0` | [swarmauri_billing_stripe](40-standards/swarmauri_billing_stripe/) | `40-standards/swarmauri_billing_stripe` | `billing` | `atomic-concrete` | `standard` | yes |
| `40.0` | [swarmauri_certs_local_ca](40-standards/swarmauri_certs_local_ca/) | `40-standards/swarmauri_certs_local_ca` | `certs` | `atomic-concrete` | `standard` | yes |
| `40.0` | [swarmauri_certs_remote_ca](40-standards/swarmauri_certs_remote_ca/) | `40-standards/swarmauri_certs_remote_ca` | `certs` | `atomic-concrete` | `standard` | yes |
| `40.0` | [swarmauri_certs_self_signed](40-standards/swarmauri_certs_self_signed/) | `40-standards/swarmauri_certs_self_signed` | `certs` | `atomic-concrete` | `standard` | yes |
| `40.0` | [swarmauri_certs_x509verify](40-standards/swarmauri_certs_x509verify/) | `40-standards/swarmauri_certs_x509verify` | `certs` | `atomic-concrete` | `standard` | yes |
| `40.0` | [swarmauri_cipher_suite_cades](40-standards/swarmauri_cipher_suite_cades/) | `40-standards/swarmauri_cipher_suite_cades` | `cipher_suite` | `atomic-concrete` | `standard` | yes |
| `40.0` | [swarmauri_cipher_suite_cnsa20](40-standards/swarmauri_cipher_suite_cnsa20/) | `40-standards/swarmauri_cipher_suite_cnsa20` | `cipher_suite` | `atomic-concrete` | `standard` | yes |
| `40.0` | [swarmauri_cipher_suite_cose](40-standards/swarmauri_cipher_suite_cose/) | `40-standards/swarmauri_cipher_suite_cose` | `cipher_suite` | `atomic-concrete` | `standard` | yes |
| `40.0` | [swarmauri_cipher_suite_fips1403](40-standards/swarmauri_cipher_suite_fips1403/) | `40-standards/swarmauri_cipher_suite_fips1403` | `cipher_suite` | `atomic-concrete` | `standard` | yes |
| `40.0` | [swarmauri_cipher_suite_fips203](40-standards/swarmauri_cipher_suite_fips203/) | `40-standards/swarmauri_cipher_suite_fips203` | `cipher_suite` | `atomic-concrete` | `standard` | yes |
| `40.0` | [swarmauri_cipher_suite_fips204](40-standards/swarmauri_cipher_suite_fips204/) | `40-standards/swarmauri_cipher_suite_fips204` | `cipher_suite` | `atomic-concrete` | `standard` | yes |
| `40.0` | [swarmauri_cipher_suite_fips205](40-standards/swarmauri_cipher_suite_fips205/) | `40-standards/swarmauri_cipher_suite_fips205` | `cipher_suite` | `atomic-concrete` | `standard` | yes |
| `40.0` | [swarmauri_cipher_suite_ipsec](40-standards/swarmauri_cipher_suite_ipsec/) | `40-standards/swarmauri_cipher_suite_ipsec` | `cipher_suite` | `atomic-concrete` | `standard` | yes |
| `40.0` | [swarmauri_cipher_suite_jwa](40-standards/swarmauri_cipher_suite_jwa/) | `40-standards/swarmauri_cipher_suite_jwa` | `cipher_suite` | `atomic-concrete` | `standard` | yes |
| `40.0` | [swarmauri_cipher_suite_pades](40-standards/swarmauri_cipher_suite_pades/) | `40-standards/swarmauri_cipher_suite_pades` | `cipher_suite` | `atomic-concrete` | `standard` | yes |
| `40.0` | [swarmauri_cipher_suite_pep458](40-standards/swarmauri_cipher_suite_pep458/) | `40-standards/swarmauri_cipher_suite_pep458` | `cipher_suite` | `atomic-concrete` | `standard` | yes |
| `40.0` | [swarmauri_cipher_suite_sigstore](40-standards/swarmauri_cipher_suite_sigstore/) | `40-standards/swarmauri_cipher_suite_sigstore` | `cipher_suite` | `atomic-concrete` | `standard` | yes |
| `40.0` | [swarmauri_cipher_suite_ssh](40-standards/swarmauri_cipher_suite_ssh/) | `40-standards/swarmauri_cipher_suite_ssh` | `cipher_suite` | `atomic-concrete` | `standard` | yes |
| `40.0` | [swarmauri_cipher_suite_tls13](40-standards/swarmauri_cipher_suite_tls13/) | `40-standards/swarmauri_cipher_suite_tls13` | `cipher_suite` | `atomic-concrete` | `standard` | yes |
| `40.0` | [swarmauri_cipher_suite_webauthn](40-standards/swarmauri_cipher_suite_webauthn/) | `40-standards/swarmauri_cipher_suite_webauthn` | `cipher_suite` | `atomic-concrete` | `standard` | yes |
| `40.0` | [swarmauri_cipher_suite_xades](40-standards/swarmauri_cipher_suite_xades/) | `40-standards/swarmauri_cipher_suite_xades` | `cipher_suite` | `atomic-concrete` | `standard` | yes |
| `40.0` | [swarmauri_cipher_suite_yubikey](40-standards/swarmauri_cipher_suite_yubikey/) | `40-standards/swarmauri_cipher_suite_yubikey` | `cipher_suite` | `atomic-concrete` | `standard` | yes |
| `40.0` | [swarmauri_cipher_suite_yubikey_fips](40-standards/swarmauri_cipher_suite_yubikey_fips/) | `40-standards/swarmauri_cipher_suite_yubikey_fips` | `cipher_suite` | `atomic-concrete` | `standard` | yes |
| `40.0` | [swarmauri_conversation_compacting](40-standards/swarmauri_conversation_compacting/) | `40-standards/swarmauri_conversation_compacting` | `conversation` | `atomic-concrete` | `standard` | yes |
| `40.0` | [swarmauri_crypto_ecdh_es_a128kw](40-standards/swarmauri_crypto_ecdh_es_a128kw/) | `40-standards/swarmauri_crypto_ecdh_es_a128kw` | `crypto` | `atomic-concrete` | `standard` | yes |
| `40.0` | [swarmauri_crypto_jwe](40-standards/swarmauri_crypto_jwe/) | `40-standards/swarmauri_crypto_jwe` | `crypto` | `atomic-concrete` | `standard` | yes |
| `40.0` | [swarmauri_crypto_nacl_pkcs11](40-standards/swarmauri_crypto_nacl_pkcs11/) | `40-standards/swarmauri_crypto_nacl_pkcs11` | `crypto` | `atomic-concrete` | `standard` | yes |
| `40.0` | [swarmauri_crypto_paramiko](40-standards/swarmauri_crypto_paramiko/) | `40-standards/swarmauri_crypto_paramiko` | `crypto` | `atomic-concrete` | `standard` | yes |
| `40.0` | [swarmauri_crypto_pgp](40-standards/swarmauri_crypto_pgp/) | `40-standards/swarmauri_crypto_pgp` | `crypto` | `atomic-concrete` | `standard` | yes |
| `40.0` | [swarmauri_crypto_rust](40-standards/swarmauri_crypto_rust/) | `40-standards/swarmauri_crypto_rust` | `crypto` | `atomic-concrete` | `standard` | yes |
| `40.0` | [swarmauri_delegation_attenuating](40-standards/swarmauri_delegation_attenuating/) | `40-standards/swarmauri_delegation_attenuating` | `delegation` | `atomic-concrete` | `standard` | yes |
| `40.0` | [swarmauri_distance_canberra](40-standards/swarmauri_distance_canberra/) | `40-standards/swarmauri_distance_canberra` | `distance` | `atomic-concrete` | `standard` | yes |
| `40.0` | [swarmauri_distance_chebyshev](40-standards/swarmauri_distance_chebyshev/) | `40-standards/swarmauri_distance_chebyshev` | `distance` | `atomic-concrete` | `standard` | yes |
| `40.0` | [swarmauri_distance_chi_squared](40-standards/swarmauri_distance_chi_squared/) | `40-standards/swarmauri_distance_chi_squared` | `distance` | `atomic-concrete` | `standard` | yes |
| `40.0` | [swarmauri_distance_cosine](40-standards/swarmauri_distance_cosine/) | `40-standards/swarmauri_distance_cosine` | `distance` | `atomic-concrete` | `standard` | yes |
| `40.0` | [swarmauri_distance_euclidean](40-standards/swarmauri_distance_euclidean/) | `40-standards/swarmauri_distance_euclidean` | `distance` | `atomic-concrete` | `standard` | yes |
| `40.0` | [swarmauri_distance_haversine](40-standards/swarmauri_distance_haversine/) | `40-standards/swarmauri_distance_haversine` | `distance` | `atomic-concrete` | `standard` | yes |
| `40.0` | [swarmauri_distance_jaccard_index](40-standards/swarmauri_distance_jaccard_index/) | `40-standards/swarmauri_distance_jaccard_index` | `distance` | `atomic-concrete` | `standard` | yes |
| `40.0` | [swarmauri_distance_levenshtein](40-standards/swarmauri_distance_levenshtein/) | `40-standards/swarmauri_distance_levenshtein` | `distance` | `atomic-concrete` | `standard` | yes |
| `40.0` | [swarmauri_distance_manhattan](40-standards/swarmauri_distance_manhattan/) | `40-standards/swarmauri_distance_manhattan` | `distance` | `atomic-concrete` | `standard` | yes |
| `40.0` | [swarmauri_distance_minkowski](40-standards/swarmauri_distance_minkowski/) | `40-standards/swarmauri_distance_minkowski` | `distance` | `atomic-concrete` | `standard` | yes |
| `40.0` | [swarmauri_distance_sorensen_dice](40-standards/swarmauri_distance_sorensen_dice/) | `40-standards/swarmauri_distance_sorensen_dice` | `distance` | `atomic-concrete` | `standard` | yes |
| `40.0` | [swarmauri_distance_squared_euclidean](40-standards/swarmauri_distance_squared_euclidean/) | `40-standards/swarmauri_distance_squared_euclidean` | `distance` | `atomic-concrete` | `standard` | yes |
| `40.0` | [swarmauri_embedding_doc2vec](40-standards/swarmauri_embedding_doc2vec/) | `40-standards/swarmauri_embedding_doc2vec` | `embedding` | `atomic-concrete` | `standard` | yes |
| `40.0` | [swarmauri_embedding_nmf](40-standards/swarmauri_embedding_nmf/) | `40-standards/swarmauri_embedding_nmf` | `embedding` | `atomic-concrete` | `standard` | yes |
| `40.0` | [swarmauri_evaluator_abstractmethods](40-standards/swarmauri_evaluator_abstractmethods/) | `40-standards/swarmauri_evaluator_abstractmethods` | `evaluator` | `atomic-concrete` | `standard` | yes |
| `40.0` | [swarmauri_evaluator_anyusage](40-standards/swarmauri_evaluator_anyusage/) | `40-standards/swarmauri_evaluator_anyusage` | `evaluator` | `atomic-concrete` | `standard` | yes |
| `40.0` | [swarmauri_evaluator_constanttime](40-standards/swarmauri_evaluator_constanttime/) | `40-standards/swarmauri_evaluator_constanttime` | `evaluator` | `atomic-concrete` | `standard` | yes |
| `40.0` | [swarmauri_evaluator_externalimports](40-standards/swarmauri_evaluator_externalimports/) | `40-standards/swarmauri_evaluator_externalimports` | `evaluator` | `atomic-concrete` | `standard` | yes |
| `40.0` | [swarmauri_evaluator_subprocess](40-standards/swarmauri_evaluator_subprocess/) | `40-standards/swarmauri_evaluator_subprocess` | `evaluator` | `atomic-concrete` | `standard` | yes |
| `40.0` | [swarmauri_evaluatorpool_accessibility](40-standards/swarmauri_evaluatorpool_accessibility/) | `40-standards/swarmauri_evaluatorpool_accessibility` | `evaluatorpool` | `atomic-concrete` | `standard` | yes |
| `40.0` | [swm_example_package](40-standards/swm_example_package/) | `40-standards/swm_example_package` | `example` | `atomic-concrete` | `standard` | yes |
| `40.0` | [swarmauri_execution_default](40-standards/swarmauri_execution_default/) | `40-standards/swarmauri_execution_default` | `execution` | `atomic-concrete` | `standard` | yes |
| `40.0` | [swarmauri_gitfilter_gh_release](40-standards/swarmauri_gitfilter_gh_release/) | `40-standards/swarmauri_gitfilter_gh_release` | `gitfilter` | `atomic-concrete` | `standard` | yes |
| `40.0` | [swarmauri_gitfilter_minio](40-standards/swarmauri_gitfilter_minio/) | `40-standards/swarmauri_gitfilter_minio` | `gitfilter` | `atomic-concrete` | `standard` | yes |
| `40.0` | [swarmauri_gitfilter_s3fs](40-standards/swarmauri_gitfilter_s3fs/) | `40-standards/swarmauri_gitfilter_s3fs` | `gitfilter` | `atomic-concrete` | `standard` | yes |
| `40.0` | [swarmauri_grantstore_sqlite](40-standards/swarmauri_grantstore_sqlite/) | `40-standards/swarmauri_grantstore_sqlite` | `grantstore` | `atomic-concrete` | `standard` | yes |
| `40.0` | [swarmauri_invoker_default](40-standards/swarmauri_invoker_default/) | `40-standards/swarmauri_invoker_default` | `invoker` | `atomic-concrete` | `standard` | yes |
| `40.0` | [swarmauri_keyprovider_file](40-standards/swarmauri_keyprovider_file/) | `40-standards/swarmauri_keyprovider_file` | `keyprovider` | `atomic-concrete` | `standard` | yes |
| `40.0` | [swarmauri_keyprovider_inmemory](40-standards/swarmauri_keyprovider_inmemory/) | `40-standards/swarmauri_keyprovider_inmemory` | `keyprovider` | `atomic-concrete` | `standard` | yes |
| `40.0` | [swarmauri_keyprovider_local](40-standards/swarmauri_keyprovider_local/) | `40-standards/swarmauri_keyprovider_local` | `keyprovider` | `atomic-concrete` | `standard` | yes |
| `40.0` | [swarmauri_keyprovider_ssh](40-standards/swarmauri_keyprovider_ssh/) | `40-standards/swarmauri_keyprovider_ssh` | `keyprovider` | `atomic-concrete` | `standard` | yes |
| `40.0` | [swamauri_metric_wasserstein](40-standards/swamauri_metric_wasserstein/) | `40-standards/swamauri_metric_wasserstein` | `metric` | `atomic-concrete` | `standard` | yes |
| `40.0` | [swarmauri_middleware_bulkhead](40-standards/swarmauri_middleware_bulkhead/) | `40-standards/swarmauri_middleware_bulkhead` | `middleware` | `atomic-concrete` | `standard` | yes |
| `40.0` | [swarmauri_middleware_cachecontrol](40-standards/swarmauri_middleware_cachecontrol/) | `40-standards/swarmauri_middleware_cachecontrol` | `middleware` | `atomic-concrete` | `standard` | yes |
| `40.0` | [swarmauri_middleware_cors](40-standards/swarmauri_middleware_cors/) | `40-standards/swarmauri_middleware_cors` | `middleware` | `atomic-concrete` | `standard` | yes |
| `40.0` | [swarmauri_middleware_exceptionhandling](40-standards/swarmauri_middleware_exceptionhandling/) | `40-standards/swarmauri_middleware_exceptionhandling` | `middleware` | `atomic-concrete` | `standard` | yes |
| `40.0` | [swarmauri_middleware_gzipcompression](40-standards/swarmauri_middleware_gzipcompression/) | `40-standards/swarmauri_middleware_gzipcompression` | `middleware` | `atomic-concrete` | `standard` | yes |
| `40.0` | [swarmauri_middleware_httpsig](40-standards/swarmauri_middleware_httpsig/) | `40-standards/swarmauri_middleware_httpsig` | `middleware` | `atomic-concrete` | `standard` | yes |
| `40.0` | [swarmauri_middleware_jsonrpc](40-standards/swarmauri_middleware_jsonrpc/) | `40-standards/swarmauri_middleware_jsonrpc` | `middleware` | `atomic-concrete` | `standard` | yes |
| `40.0` | [swarmauri_middleware_jwksverifier](40-standards/swarmauri_middleware_jwksverifier/) | `40-standards/swarmauri_middleware_jwksverifier` | `middleware` | `atomic-concrete` | `standard` | yes |
| `40.0` | [swarmauri_middleware_llamaguard](40-standards/swarmauri_middleware_llamaguard/) | `40-standards/swarmauri_middleware_llamaguard` | `middleware` | `atomic-concrete` | `standard` | yes |
| `40.0` | [swarmauri_middleware_logging](40-standards/swarmauri_middleware_logging/) | `40-standards/swarmauri_middleware_logging` | `middleware` | `atomic-concrete` | `standard` | yes |
| `40.0` | [swarmauri_middleware_ratelimit](40-standards/swarmauri_middleware_ratelimit/) | `40-standards/swarmauri_middleware_ratelimit` | `middleware` | `atomic-concrete` | `standard` | yes |
| `40.0` | [swarmauri_middleware_securityheaders](40-standards/swarmauri_middleware_securityheaders/) | `40-standards/swarmauri_middleware_securityheaders` | `middleware` | `atomic-concrete` | `standard` | yes |
| `40.0` | [swarmauri_middleware_session](40-standards/swarmauri_middleware_session/) | `40-standards/swarmauri_middleware_session` | `middleware` | `atomic-concrete` | `standard` | yes |
| `40.0` | [swarmauri_middleware_stdio](40-standards/swarmauri_middleware_stdio/) | `40-standards/swarmauri_middleware_stdio` | `middleware` | `atomic-concrete` | `standard` | yes |
| `40.0` | [swarmauri_middleware_time](40-standards/swarmauri_middleware_time/) | `40-standards/swarmauri_middleware_time` | `middleware` | `atomic-concrete` | `standard` | yes |
| `40.0` | [swarmauri_mre_crypto_age](40-standards/swarmauri_mre_crypto_age/) | `40-standards/swarmauri_mre_crypto_age` | `mre_crypto` | `atomic-concrete` | `standard` | yes |
| `40.0` | [swarmauri_mre_crypto_ecdh_es_kw](40-standards/swarmauri_mre_crypto_ecdh_es_kw/) | `40-standards/swarmauri_mre_crypto_ecdh_es_kw` | `mre_crypto` | `atomic-concrete` | `standard` | yes |
| `40.0` | [swarmauri_mre_crypto_keyring](40-standards/swarmauri_mre_crypto_keyring/) | `40-standards/swarmauri_mre_crypto_keyring` | `mre_crypto` | `atomic-concrete` | `standard` | yes |
| `40.0` | [swarmauri_mre_crypto_pgp](40-standards/swarmauri_mre_crypto_pgp/) | `40-standards/swarmauri_mre_crypto_pgp` | `mre_crypto` | `atomic-concrete` | `standard` | yes |
| `40.0` | [swarmauri_mre_crypto_shamir](40-standards/swarmauri_mre_crypto_shamir/) | `40-standards/swarmauri_mre_crypto_shamir` | `mre_crypto` | `atomic-concrete` | `standard` | yes |
| `40.0` | [swarmauri_parser_beautifulsoupelement](40-standards/swarmauri_parser_beautifulsoupelement/) | `40-standards/swarmauri_parser_beautifulsoupelement` | `parser` | `atomic-concrete` | `standard` | yes |
| `40.0` | [swarmauri_parser_keywordextractor](40-standards/swarmauri_parser_keywordextractor/) | `40-standards/swarmauri_parser_keywordextractor` | `parser` | `atomic-concrete` | `standard` | yes |
| `40.0` | [swarmauri_permission_explicit](40-standards/swarmauri_permission_explicit/) | `40-standards/swarmauri_permission_explicit` | `permission` | `atomic-concrete` | `standard` | yes |
| `40.0` | [swarmauri_pop_cwt](40-standards/swarmauri_pop_cwt/) | `40-standards/swarmauri_pop_cwt` | `pop` | `atomic-concrete` | `standard` | yes |
| `40.0` | [swarmauri_pop_dpop](40-standards/swarmauri_pop_dpop/) | `40-standards/swarmauri_pop_dpop` | `pop` | `atomic-concrete` | `standard` | yes |
| `40.0` | [swarmauri_pop_x509](40-standards/swarmauri_pop_x509/) | `40-standards/swarmauri_pop_x509` | `pop` | `atomic-concrete` | `standard` | yes |
| `40.0` | [swarmauri_process_docker](40-standards/swarmauri_process_docker/) | `40-standards/swarmauri_process_docker` | `process` | `atomic-concrete` | `standard` | yes |
| `40.0` | [swarmauri_process_kubernetes](40-standards/swarmauri_process_kubernetes/) | `40-standards/swarmauri_process_kubernetes` | `process` | `atomic-concrete` | `standard` | yes |
| `40.0` | [swarmauri_process_subprocess](40-standards/swarmauri_process_subprocess/) | `40-standards/swarmauri_process_subprocess` | `process` | `atomic-concrete` | `standard` | yes |
| `40.0` | [swarmauri_prompt_j2prompttemplate](40-standards/swarmauri_prompt_j2prompttemplate/) | `40-standards/swarmauri_prompt_j2prompttemplate` | `prompt` | `atomic-concrete` | `standard` | yes |
| `40.0` | [swarmauri_publisher_rabbitmq](40-standards/swarmauri_publisher_rabbitmq/) | `40-standards/swarmauri_publisher_rabbitmq` | `publisher` | `atomic-concrete` | `standard` | yes |
| `40.0` | [swarmauri_publisher_redis](40-standards/swarmauri_publisher_redis/) | `40-standards/swarmauri_publisher_redis` | `publisher` | `atomic-concrete` | `standard` | yes |
| `40.0` | [swarmauri_publisher_webhook](40-standards/swarmauri_publisher_webhook/) | `40-standards/swarmauri_publisher_webhook` | `publisher` | `atomic-concrete` | `standard` | yes |
| `40.0` | [swarmauri_runstore_sqlite](40-standards/swarmauri_runstore_sqlite/) | `40-standards/swarmauri_runstore_sqlite` | `runstore` | `atomic-concrete` | `standard` | yes |
| `40.0` | [swarmauri_signing_ca](40-standards/swarmauri_signing_ca/) | `40-standards/swarmauri_signing_ca` | `signing` | `atomic-concrete` | `standard` | yes |
| `40.0` | [swarmauri_signing_cms](40-standards/swarmauri_signing_cms/) | `40-standards/swarmauri_signing_cms` | `signing` | `atomic-concrete` | `standard` | yes |
| `40.0` | [swarmauri_signing_ecdsa](40-standards/swarmauri_signing_ecdsa/) | `40-standards/swarmauri_signing_ecdsa` | `signing` | `atomic-concrete` | `standard` | yes |
| `40.0` | [swarmauri_signing_ed25519](40-standards/swarmauri_signing_ed25519/) | `40-standards/swarmauri_signing_ed25519` | `signing` | `atomic-concrete` | `standard` | yes |
| `40.0` | [swarmauri_signing_hmac](40-standards/swarmauri_signing_hmac/) | `40-standards/swarmauri_signing_hmac` | `signing` | `atomic-concrete` | `standard` | yes |
| `40.0` | [swarmauri_signing_openpgp](40-standards/swarmauri_signing_openpgp/) | `40-standards/swarmauri_signing_openpgp` | `signing` | `atomic-concrete` | `standard` | yes |
| `40.0` | [swarmauri_signing_pep458](40-standards/swarmauri_signing_pep458/) | `40-standards/swarmauri_signing_pep458` | `signing` | `atomic-concrete` | `standard` | yes |
| `40.0` | [swarmauri_signing_pgp](40-standards/swarmauri_signing_pgp/) | `40-standards/swarmauri_signing_pgp` | `signing` | `atomic-concrete` | `standard` | yes |
| `40.0` | [swarmauri_signing_rsa](40-standards/swarmauri_signing_rsa/) | `40-standards/swarmauri_signing_rsa` | `signing` | `atomic-concrete` | `standard` | yes |
| `40.0` | [swarmauri_signing_secp256k1](40-standards/swarmauri_signing_secp256k1/) | `40-standards/swarmauri_signing_secp256k1` | `signing` | `atomic-concrete` | `standard` | yes |
| `40.0` | [swarmauri_signing_sigv4](40-standards/swarmauri_signing_sigv4/) | `40-standards/swarmauri_signing_sigv4` | `signing` | `atomic-concrete` | `standard` | yes |
| `40.0` | [swarmauri_signing_ssh](40-standards/swarmauri_signing_ssh/) | `40-standards/swarmauri_signing_ssh` | `signing` | `atomic-concrete` | `standard` | yes |
| `40.0` | [swarmauri_signing_xmld](40-standards/swarmauri_signing_xmld/) | `40-standards/swarmauri_signing_xmld` | `signing` | `atomic-concrete` | `standard` | yes |
| `40.0` | [swarmauri_similarity_gzip](40-standards/swarmauri_similarity_gzip/) | `40-standards/swarmauri_similarity_gzip` | `similarity` | `atomic-concrete` | `standard` | yes |
| `40.0` | [swarmauri_skill_dummy_filesystem](40-standards/swarmauri_skill_dummy_filesystem/) | `40-standards/swarmauri_skill_dummy_filesystem` | `skill` | `atomic-concrete` | `standard` | yes |
| `40.0` | [swarmauri_skill_dummy_local](40-standards/swarmauri_skill_dummy_local/) | `40-standards/swarmauri_skill_dummy_local` | `skill` | `atomic-concrete` | `standard` | yes |
| `40.0` | [swarmauri_skill_filesystem](40-standards/swarmauri_skill_filesystem/) | `40-standards/swarmauri_skill_filesystem` | `skill` | `atomic-concrete` | `standard` | yes |
| `40.0` | [swarmauri_skill_local](40-standards/swarmauri_skill_local/) | `40-standards/swarmauri_skill_local` | `skill` | `atomic-concrete` | `standard` | yes |
| `40.0` | [swarmauri_storage_file](40-standards/swarmauri_storage_file/) | `40-standards/swarmauri_storage_file` | `storage` | `atomic-concrete` | `standard` | yes |
| `40.0` | [swarmauri_storage_github](40-standards/swarmauri_storage_github/) | `40-standards/swarmauri_storage_github` | `storage` | `atomic-concrete` | `standard` | yes |
| `40.0` | [swarmauri_storage_github_release](40-standards/swarmauri_storage_github_release/) | `40-standards/swarmauri_storage_github_release` | `storage` | `atomic-concrete` | `standard` | yes |
| `40.0` | [swarmauri_storage_memory](40-standards/swarmauri_storage_memory/) | `40-standards/swarmauri_storage_memory` | `storage` | `atomic-concrete` | `standard` | yes |
| `40.0` | [swarmauri_storage_minio](40-standards/swarmauri_storage_minio/) | `40-standards/swarmauri_storage_minio` | `storage` | `atomic-concrete` | `standard` | yes |
| `40.0` | [swarmauri_storage_s3](40-standards/swarmauri_storage_s3/) | `40-standards/swarmauri_storage_s3` | `storage` | `atomic-concrete` | `standard` | yes |
| `40.0` | [swarmauri_storage_s3_over_sftp](40-standards/swarmauri_storage_s3_over_sftp/) | `40-standards/swarmauri_storage_s3_over_sftp` | `storage` | `atomic-concrete` | `standard` | yes |
| `40.0` | [swarmauri_storage_s3fs](40-standards/swarmauri_storage_s3fs/) | `40-standards/swarmauri_storage_s3fs` | `storage` | `atomic-concrete` | `standard` | yes |
| `40.0` | [swarmauri_storage_webdav](40-standards/swarmauri_storage_webdav/) | `40-standards/swarmauri_storage_webdav` | `storage` | `atomic-concrete` | `standard` | yes |
| `40.0` | [swarmauri_taskmanager_default](40-standards/swarmauri_taskmanager_default/) | `40-standards/swarmauri_taskmanager_default` | `taskmanager` | `atomic-concrete` | `standard` | yes |
| `40.0` | [swarmauri_taskstore_sqlite](40-standards/swarmauri_taskstore_sqlite/) | `40-standards/swarmauri_taskstore_sqlite` | `taskstore` | `atomic-concrete` | `standard` | yes |
| `40.0` | [swarmauri_tokens_dpopboundjwt](40-standards/swarmauri_tokens_dpopboundjwt/) | `40-standards/swarmauri_tokens_dpopboundjwt` | `tokens` | `atomic-concrete` | `standard` | yes |
| `40.0` | [swarmauri_tokens_introspection](40-standards/swarmauri_tokens_introspection/) | `40-standards/swarmauri_tokens_introspection` | `tokens` | `atomic-concrete` | `standard` | yes |
| `40.0` | [swarmauri_tokens_jwt](40-standards/swarmauri_tokens_jwt/) | `40-standards/swarmauri_tokens_jwt` | `tokens` | `atomic-concrete` | `standard` | yes |
| `40.0` | [swarmauri_tokens_paseto_v4](40-standards/swarmauri_tokens_paseto_v4/) | `40-standards/swarmauri_tokens_paseto_v4` | `tokens` | `atomic-concrete` | `standard` | yes |
| `40.0` | [swarmauri_tokens_remoteoidc](40-standards/swarmauri_tokens_remoteoidc/) | `40-standards/swarmauri_tokens_remoteoidc` | `tokens` | `atomic-concrete` | `standard` | yes |
| `40.0` | [swarmauri_tokens_rotatingjwt](40-standards/swarmauri_tokens_rotatingjwt/) | `40-standards/swarmauri_tokens_rotatingjwt` | `tokens` | `atomic-concrete` | `standard` | yes |
| `40.0` | [swarmauri_tokens_sshcert](40-standards/swarmauri_tokens_sshcert/) | `40-standards/swarmauri_tokens_sshcert` | `tokens` | `atomic-concrete` | `standard` | yes |
| `40.0` | [swarmauri_tokens_sshsig](40-standards/swarmauri_tokens_sshsig/) | `40-standards/swarmauri_tokens_sshsig` | `tokens` | `atomic-concrete` | `standard` | yes |
| `40.0` | [swarmauri_tokens_tlsboundjwt](40-standards/swarmauri_tokens_tlsboundjwt/) | `40-standards/swarmauri_tokens_tlsboundjwt` | `tokens` | `atomic-concrete` | `standard` | yes |
| `40.0` | [swarmauri_tool_activateskill](40-standards/swarmauri_tool_activateskill/) | `40-standards/swarmauri_tool_activateskill` | `tool` | `atomic-concrete` | `standard` | yes |
| `40.0` | [swarmauri_tool_askuser](40-standards/swarmauri_tool_askuser/) | `40-standards/swarmauri_tool_askuser` | `tool` | `atomic-concrete` | `standard` | yes |
| `40.0` | [swarmauri_tool_cancelprocess](40-standards/swarmauri_tool_cancelprocess/) | `40-standards/swarmauri_tool_cancelprocess` | `tool` | `atomic-concrete` | `standard` | yes |
| `40.0` | [swarmauri_tool_containerfeedchars](40-standards/swarmauri_tool_containerfeedchars/) | `40-standards/swarmauri_tool_containerfeedchars` | `tool` | `atomic-concrete` | `standard` | yes |
| `40.0` | [swarmauri_tool_containermakepr](40-standards/swarmauri_tool_containermakepr/) | `40-standards/swarmauri_tool_containermakepr` | `tool` | `atomic-concrete` | `standard` | yes |
| `40.0` | [swarmauri_tool_containernewsession](40-standards/swarmauri_tool_containernewsession/) | `40-standards/swarmauri_tool_containernewsession` | `tool` | `atomic-concrete` | `standard` | yes |
| `40.0` | [swarmauri_tool_githubloader](40-standards/swarmauri_tool_githubloader/) | `40-standards/swarmauri_tool_githubloader` | `tool` | `atomic-concrete` | `standard` | yes |
| `40.0` | [swarmauri_tool_httploaded](40-standards/swarmauri_tool_httploaded/) | `40-standards/swarmauri_tool_httploaded` | `tool` | `atomic-concrete` | `standard` | yes |
| `40.0` | [swarmauri_tool_inspectruntimetool](40-standards/swarmauri_tool_inspectruntimetool/) | `40-standards/swarmauri_tool_inspectruntimetool` | `tool` | `atomic-concrete` | `standard` | yes |
| `40.0` | [swarmauri_tool_inspectskill](40-standards/swarmauri_tool_inspectskill/) | `40-standards/swarmauri_tool_inspectskill` | `tool` | `atomic-concrete` | `standard` | yes |
| `40.0` | [swarmauri_tool_listruntimetools](40-standards/swarmauri_tool_listruntimetools/) | `40-standards/swarmauri_tool_listruntimetools` | `tool` | `atomic-concrete` | `standard` | yes |
| `40.0` | [swarmauri_tool_listskills](40-standards/swarmauri_tool_listskills/) | `40-standards/swarmauri_tool_listskills` | `tool` | `atomic-concrete` | `standard` | yes |
| `40.0` | [swarmauri_tool_matplotlib](40-standards/swarmauri_tool_matplotlib/) | `40-standards/swarmauri_tool_matplotlib` | `tool` | `atomic-concrete` | `standard` | yes |
| `40.0` | [swarmauri_tool_readprocessoutput](40-standards/swarmauri_tool_readprocessoutput/) | `40-standards/swarmauri_tool_readprocessoutput` | `tool` | `atomic-concrete` | `standard` | yes |
| `40.0` | [swarmauri_tool_readskillresource](40-standards/swarmauri_tool_readskillresource/) | `40-standards/swarmauri_tool_readskillresource` | `tool` | `atomic-concrete` | `standard` | yes |
| `40.0` | [swarmauri_tool_registerruntimetool](40-standards/swarmauri_tool_registerruntimetool/) | `40-standards/swarmauri_tool_registerruntimetool` | `tool` | `atomic-concrete` | `standard` | yes |
| `40.0` | [swarmauri_tool_replaceruntimetool](40-standards/swarmauri_tool_replaceruntimetool/) | `40-standards/swarmauri_tool_replaceruntimetool` | `tool` | `atomic-concrete` | `standard` | yes |
| `40.0` | [swarmauri_tool_runbashscript](40-standards/swarmauri_tool_runbashscript/) | `40-standards/swarmauri_tool_runbashscript` | `tool` | `atomic-concrete` | `standard` | yes |
| `40.0` | [swarmauri_tool_runcommand](40-standards/swarmauri_tool_runcommand/) | `40-standards/swarmauri_tool_runcommand` | `tool` | `atomic-concrete` | `standard` | yes |
| `40.0` | [swarmauri_tool_runpackagechecks](40-standards/swarmauri_tool_runpackagechecks/) | `40-standards/swarmauri_tool_runpackagechecks` | `tool` | `atomic-concrete` | `standard` | yes |
| `40.0` | [swarmauri_tool_skill_execution](40-standards/swarmauri_tool_skill_execution/) | `40-standards/swarmauri_tool_skill_execution` | `tool` | `atomic-concrete` | `standard` | yes |
| `40.0` | [swarmauri_tool_subprocess](40-standards/swarmauri_tool_subprocess/) | `40-standards/swarmauri_tool_subprocess` | `tool` | `atomic-concrete` | `standard` | yes |
| `40.0` | [swarmauri_tool_unregisterruntimetool](40-standards/swarmauri_tool_unregisterruntimetool/) | `40-standards/swarmauri_tool_unregisterruntimetool` | `tool` | `atomic-concrete` | `standard` | yes |
| `40.0` | [swarmauri_tool_writestdin](40-standards/swarmauri_tool_writestdin/) | `40-standards/swarmauri_tool_writestdin` | `tool` | `atomic-concrete` | `standard` | yes |
| `40.0` | [swarmauri_transport_asgi](40-standards/swarmauri_transport_asgi/) | `40-standards/swarmauri_transport_asgi` | `transport` | `atomic-concrete` | `standard` | yes |
| `40.0` | [swarmauri_transport_aws_eventstream](40-standards/swarmauri_transport_aws_eventstream/) | `40-standards/swarmauri_transport_aws_eventstream` | `transport` | `atomic-concrete` | `standard` | yes |
| `40.0` | [swarmauri_transport_h2mux](40-standards/swarmauri_transport_h2mux/) | `40-standards/swarmauri_transport_h2mux` | `transport` | `atomic-concrete` | `standard` | yes |
| `40.0` | [swarmauri_transport_httpx](40-standards/swarmauri_transport_httpx/) | `40-standards/swarmauri_transport_httpx` | `transport` | `atomic-concrete` | `standard` | yes |
| `40.0` | [swarmauri_transport_meshsidecarhttp2](40-standards/swarmauri_transport_meshsidecarhttp2/) | `40-standards/swarmauri_transport_meshsidecarhttp2` | `transport` | `atomic-concrete` | `standard` | yes |
| `40.0` | [swarmauri_transport_mtlsunicast](40-standards/swarmauri_transport_mtlsunicast/) | `40-standards/swarmauri_transport_mtlsunicast` | `transport` | `atomic-concrete` | `standard` | yes |
| `40.0` | [swarmauri_transport_quic](40-standards/swarmauri_transport_quic/) | `40-standards/swarmauri_transport_quic` | `transport` | `atomic-concrete` | `standard` | yes |
| `40.0` | [swarmauri_transport_retry](40-standards/swarmauri_transport_retry/) | `40-standards/swarmauri_transport_retry` | `transport` | `atomic-concrete` | `standard` | yes |
| `40.0` | [swarmauri_transport_sseoutbound](40-standards/swarmauri_transport_sseoutbound/) | `40-standards/swarmauri_transport_sseoutbound` | `transport` | `atomic-concrete` | `standard` | yes |
| `40.0` | [swarmauri_transport_sshtunnel](40-standards/swarmauri_transport_sshtunnel/) | `40-standards/swarmauri_transport_sshtunnel` | `transport` | `atomic-concrete` | `standard` | yes |
| `40.0` | [swarmauri_transport_stdio](40-standards/swarmauri_transport_stdio/) | `40-standards/swarmauri_transport_stdio` | `transport` | `atomic-concrete` | `standard` | yes |
| `40.0` | [swarmauri_transport_tcpunicast](40-standards/swarmauri_transport_tcpunicast/) | `40-standards/swarmauri_transport_tcpunicast` | `transport` | `atomic-concrete` | `standard` | yes |
| `40.0` | [swarmauri_transport_tls_unicast](40-standards/swarmauri_transport_tls_unicast/) | `40-standards/swarmauri_transport_tls_unicast` | `transport` | `atomic-concrete` | `standard` | yes |
| `40.0` | [swarmauri_transport_udp](40-standards/swarmauri_transport_udp/) | `40-standards/swarmauri_transport_udp` | `transport` | `atomic-concrete` | `standard` | yes |
| `40.0` | [swarmauri_transport_uds_unicast](40-standards/swarmauri_transport_uds_unicast/) | `40-standards/swarmauri_transport_uds_unicast` | `transport` | `atomic-concrete` | `standard` | yes |
| `40.0` | [swarmauri_transport_websocket](40-standards/swarmauri_transport_websocket/) | `40-standards/swarmauri_transport_websocket` | `transport` | `atomic-concrete` | `standard` | yes |
| `40.0` | [swarmauri_transport_wsjsonrpcmux](40-standards/swarmauri_transport_wsjsonrpcmux/) | `40-standards/swarmauri_transport_wsjsonrpcmux` | `transport` | `atomic-concrete` | `standard` | yes |
| `40.0` | [swarmauri_tts_azure](40-standards/swarmauri_tts_azure/) | `40-standards/swarmauri_tts_azure` | `tts` | `atomic-concrete` | `standard` | yes |
| `40.0` | [swarmauri_tts_cartesia](40-standards/swarmauri_tts_cartesia/) | `40-standards/swarmauri_tts_cartesia` | `tts` | `atomic-concrete` | `standard` | yes |
| `40.0` | [swarmauri_tts_deepgram](40-standards/swarmauri_tts_deepgram/) | `40-standards/swarmauri_tts_deepgram` | `tts` | `atomic-concrete` | `standard` | yes |
| `40.0` | [swarmauri_tts_deepinfra](40-standards/swarmauri_tts_deepinfra/) | `40-standards/swarmauri_tts_deepinfra` | `tts` | `atomic-concrete` | `standard` | yes |
| `40.0` | [swarmauri_tts_deepinfra_kokoro](40-standards/swarmauri_tts_deepinfra_kokoro/) | `40-standards/swarmauri_tts_deepinfra_kokoro` | `tts` | `atomic-concrete` | `standard` | yes |
| `40.0` | [swarmauri_tts_deepinfra_qwen3](40-standards/swarmauri_tts_deepinfra_qwen3/) | `40-standards/swarmauri_tts_deepinfra_qwen3` | `tts` | `atomic-concrete` | `standard` | yes |
| `40.0` | [swarmauri_tts_deepinfra_qwen3_voicedesign](40-standards/swarmauri_tts_deepinfra_qwen3_voicedesign/) | `40-standards/swarmauri_tts_deepinfra_qwen3_voicedesign` | `tts` | `atomic-concrete` | `standard` | yes |
| `40.0` | [swarmauri_tts_elevenlabs](40-standards/swarmauri_tts_elevenlabs/) | `40-standards/swarmauri_tts_elevenlabs` | `tts` | `atomic-concrete` | `standard` | yes |
| `40.0` | [swarmauri_tts_elevenlabs_dialogue](40-standards/swarmauri_tts_elevenlabs_dialogue/) | `40-standards/swarmauri_tts_elevenlabs_dialogue` | `tts` | `atomic-concrete` | `standard` | yes |
| `40.0` | [swarmauri_tts_gemini](40-standards/swarmauri_tts_gemini/) | `40-standards/swarmauri_tts_gemini` | `tts` | `atomic-concrete` | `standard` | yes |
| `40.0` | [swarmauri_tts_gemini_dialogue](40-standards/swarmauri_tts_gemini_dialogue/) | `40-standards/swarmauri_tts_gemini_dialogue` | `tts` | `atomic-concrete` | `standard` | yes |
| `40.0` | [swarmauri_tts_openai](40-standards/swarmauri_tts_openai/) | `40-standards/swarmauri_tts_openai` | `tts` | `atomic-concrete` | `standard` | yes |
| `40.0` | [swarmauri_tts_polly](40-standards/swarmauri_tts_polly/) | `40-standards/swarmauri_tts_polly` | `tts` | `atomic-concrete` | `standard` | yes |
| `40.0` | [swarmauri_tts_together](40-standards/swarmauri_tts_together/) | `40-standards/swarmauri_tts_together` | `tts` | `atomic-concrete` | `standard` | yes |
| `40.0` | [swarmauri_xmp_gif](40-standards/swarmauri_xmp_gif/) | `40-standards/swarmauri_xmp_gif` | `xmp` | `atomic-concrete` | `standard` | yes |
| `40.0` | [swarmauri_xmp_jpeg](40-standards/swarmauri_xmp_jpeg/) | `40-standards/swarmauri_xmp_jpeg` | `xmp` | `atomic-concrete` | `standard` | yes |
| `40.0` | [swarmauri_xmp_mp4](40-standards/swarmauri_xmp_mp4/) | `40-standards/swarmauri_xmp_mp4` | `xmp` | `atomic-concrete` | `standard` | yes |
| `40.0` | [swarmauri_xmp_pdf](40-standards/swarmauri_xmp_pdf/) | `40-standards/swarmauri_xmp_pdf` | `xmp` | `atomic-concrete` | `standard` | yes |
| `40.0` | [swarmauri_xmp_png](40-standards/swarmauri_xmp_png/) | `40-standards/swarmauri_xmp_png` | `xmp` | `atomic-concrete` | `standard` | yes |
| `40.0` | [swarmauri_xmp_svg](40-standards/swarmauri_xmp_svg/) | `40-standards/swarmauri_xmp_svg` | `xmp` | `atomic-concrete` | `standard` | yes |
| `40.0` | [swarmauri_xmp_tiff](40-standards/swarmauri_xmp_tiff/) | `40-standards/swarmauri_xmp_tiff` | `xmp` | `atomic-concrete` | `standard` | yes |
| `40.0` | [swarmauri_xmp_webp](40-standards/swarmauri_xmp_webp/) | `40-standards/swarmauri_xmp_webp` | `xmp` | `atomic-concrete` | `standard` | yes |
| `40.1` | [swarmauri_certs_composite](40-standards/swarmauri_certs_composite/) | `40-standards/swarmauri_certs_composite` | `certs` | `composite-concrete` | `standard` | yes |
| `40.1` | [swarmauri_certs_x509](40-standards/swarmauri_certs_x509/) | `40-standards/swarmauri_certs_x509` | `certs` | `composite-concrete` | `standard` | yes |
| `40.1` | [swarmauri_crypto_composite](40-standards/swarmauri_crypto_composite/) | `40-standards/swarmauri_crypto_composite` | `crypto` | `composite-concrete` | `standard` | yes |
| `40.1` | [swarmauri_gitfilter_file](40-standards/swarmauri_gitfilter_file/) | `40-standards/swarmauri_gitfilter_file` | `gitfilter` | `composite-concrete` | `standard` | yes |
| `40.1` | [swarmauri_keyprovider_hierarchical](40-standards/swarmauri_keyprovider_hierarchical/) | `40-standards/swarmauri_keyprovider_hierarchical` | `keyprovider` | `composite-concrete` | `standard` | yes |
| `40.1` | [swarmauri_keyprovider_remote_jwks](40-standards/swarmauri_keyprovider_remote_jwks/) | `40-standards/swarmauri_keyprovider_remote_jwks` | `keyprovider` | `composite-concrete` | `standard` | yes |
| `40.1` | [swarmauri_keyproviders_mirrored](40-standards/swarmauri_keyproviders_mirrored/) | `40-standards/swarmauri_keyproviders_mirrored` | `keyproviders` | `composite-concrete` | `standard` | yes |
| `40.1` | [swarmauri_signing_jws](40-standards/swarmauri_signing_jws/) | `40-standards/swarmauri_signing_jws` | `signing` | `composite-concrete` | `standard` | yes |
| `40.1` | [swarmauri_signing_pdf](40-standards/swarmauri_signing_pdf/) | `40-standards/swarmauri_signing_pdf` | `signing` | `composite-concrete` | `standard` | yes |
| `40.1` | [swarmauri_tokens_composite](40-standards/swarmauri_tokens_composite/) | `40-standards/swarmauri_tokens_composite` | `tokens` | `composite-concrete` | `standard` | yes |
| `40.1` | [swarmauri_transport_h2](40-standards/swarmauri_transport_h2/) | `40-standards/swarmauri_transport_h2` | `transport` | `composite-concrete` | `standard` | yes |
| `40.1` | [swarmauri_vectorstore_doc2vec](40-standards/swarmauri_vectorstore_doc2vec/) | `40-standards/swarmauri_vectorstore_doc2vec` | `vectorstore` | `composite-concrete` | `standard` | yes |
| `40.2` | [swarmauri_middleware_jwt](40-standards/swarmauri_middleware_jwt/) | `40-standards/swarmauri_middleware_jwt` | `middleware` | `orchestrator` | `standard` | yes |
| `40.2` | [swarmauri_signing_dpop](40-standards/swarmauri_signing_dpop/) | `40-standards/swarmauri_signing_dpop` | `signing` | `orchestrator` | `standard` | yes |
| `40.2` | [swarmauri_toolkit_containertoolkit](40-standards/swarmauri_toolkit_containertoolkit/) | `40-standards/swarmauri_toolkit_containertoolkit` | `toolkit` | `orchestrator` | `standard` | yes |
| `40.2` | [swarmauri_toolkit_runtime](40-standards/swarmauri_toolkit_runtime/) | `40-standards/swarmauri_toolkit_runtime` | `toolkit` | `orchestrator` | `standard` | yes |
| `40.2` | [swarmauri_toolkit_skillset](40-standards/swarmauri_toolkit_skillset/) | `40-standards/swarmauri_toolkit_skillset` | `toolkit` | `orchestrator` | `standard` | yes |
| `40.2` | [swarmauri_transport_https_unicast](40-standards/swarmauri_transport_https_unicast/) | `40-standards/swarmauri_transport_https_unicast` | `transport` | `orchestrator` | `standard` | yes |
| `40.2` | [swarmauri_workflow_delegatedresearch](40-standards/swarmauri_workflow_delegatedresearch/) | `40-standards/swarmauri_workflow_delegatedresearch` | `workflow` | `orchestrator` | `standard` | yes |
| `40.2` | [swarmauri_workflow_documentassistant](40-standards/swarmauri_workflow_documentassistant/) | `40-standards/swarmauri_workflow_documentassistant` | `workflow` | `orchestrator` | `standard` | yes |

### `50-community`

| Index | Package | Path | Family | Role | Maturity | Workspace |
|---|---|---|---|---|---|---|
| `50.0` | [swarmauri_billing_adyen](50-community/swarmauri_billing_adyen/) | `50-community/swarmauri_billing_adyen` | `billing` | `atomic-concrete` | `community` | yes |
| `50.0` | [swarmauri_billing_authorize_net](50-community/swarmauri_billing_authorize_net/) | `50-community/swarmauri_billing_authorize_net` | `billing` | `atomic-concrete` | `community` | yes |
| `50.0` | [swarmauri_billing_braintree](50-community/swarmauri_billing_braintree/) | `50-community/swarmauri_billing_braintree` | `billing` | `atomic-concrete` | `community` | yes |
| `50.0` | [swarmauri_billing_paypal](50-community/swarmauri_billing_paypal/) | `50-community/swarmauri_billing_paypal` | `billing` | `atomic-concrete` | `community` | yes |
| `50.0` | [swarmauri_billing_paystack](50-community/swarmauri_billing_paystack/) | `50-community/swarmauri_billing_paystack` | `billing` | `atomic-concrete` | `community` | yes |
| `50.0` | [swarmauri_billing_razorpay](50-community/swarmauri_billing_razorpay/) | `50-community/swarmauri_billing_razorpay` | `billing` | `atomic-concrete` | `community` | yes |
| `50.0` | [swarmauri_billing_square](50-community/swarmauri_billing_square/) | `50-community/swarmauri_billing_square` | `billing` | `atomic-concrete` | `community` | yes |
| `50.0` | [swarmauri_certs_acme](50-community/swarmauri_certs_acme/) | `50-community/swarmauri_certs_acme` | `certs` | `atomic-concrete` | `community` | yes |
| `50.0` | [swarmauri_certs_azure](50-community/swarmauri_certs_azure/) | `50-community/swarmauri_certs_azure` | `certs` | `atomic-concrete` | `community` | yes |
| `50.0` | [swarmauri_certs_cfssl](50-community/swarmauri_certs_cfssl/) | `50-community/swarmauri_certs_cfssl` | `certs` | `atomic-concrete` | `community` | yes |
| `50.0` | [swarmauri_certs_crlverifyservice](50-community/swarmauri_certs_crlverifyservice/) | `50-community/swarmauri_certs_crlverifyservice` | `certs` | `atomic-concrete` | `community` | yes |
| `50.0` | [swarmauri_certs_csronly](50-community/swarmauri_certs_csronly/) | `50-community/swarmauri_certs_csronly` | `certs` | `atomic-concrete` | `community` | yes |
| `50.0` | [swarmauri_certs_ocspverify](50-community/swarmauri_certs_ocspverify/) | `50-community/swarmauri_certs_ocspverify` | `certs` | `atomic-concrete` | `community` | yes |
| `50.0` | [swarmauri_certservice_aws_kms](50-community/swarmauri_certservice_aws_kms/) | `50-community/swarmauri_certservice_aws_kms` | `certservice` | `atomic-concrete` | `community` | yes |
| `50.0` | [swarmauri_certservice_gcpkms](50-community/swarmauri_certservice_gcpkms/) | `50-community/swarmauri_certservice_gcpkms` | `certservice` | `atomic-concrete` | `community` | yes |
| `50.0` | [swarmauri_certservice_ms_adcs](50-community/swarmauri_certservice_ms_adcs/) | `50-community/swarmauri_certservice_ms_adcs` | `certservice` | `atomic-concrete` | `community` | yes |
| `50.0` | [swarmauri_certservice_scep](50-community/swarmauri_certservice_scep/) | `50-community/swarmauri_certservice_scep` | `certservice` | `atomic-concrete` | `community` | yes |
| `50.0` | [swarmauri_certservice_stepca](50-community/swarmauri_certservice_stepca/) | `50-community/swarmauri_certservice_stepca` | `certservice` | `atomic-concrete` | `community` | yes |
| `50.0` | [swarmauri_embedding_mlm](50-community/swarmauri_embedding_mlm/) | `50-community/swarmauri_embedding_mlm` | `embedding` | `atomic-concrete` | `community` | yes |
| `50.0` | [swm_example_community_package](50-community/swm_example_community_package/) | `50-community/swm_example_community_package` | `example` | `atomic-concrete` | `community` | yes |
| `50.0` | [swarmauri_keyprovider_aws_kms](50-community/swarmauri_keyprovider_aws_kms/) | `50-community/swarmauri_keyprovider_aws_kms` | `keyprovider` | `atomic-concrete` | `community` | yes |
| `50.0` | [swarmauri_keyprovider_gcpkms](50-community/swarmauri_keyprovider_gcpkms/) | `50-community/swarmauri_keyprovider_gcpkms` | `keyprovider` | `atomic-concrete` | `community` | yes |
| `50.0` | [swarmauri_keyprovider_vaulttransit](50-community/swarmauri_keyprovider_vaulttransit/) | `50-community/swarmauri_keyprovider_vaulttransit` | `keyprovider` | `atomic-concrete` | `community` | yes |
| `50.0` | [swarmauri_live_model_amazon_nova](50-community/swarmauri_live_model_amazon_nova/) | `50-community/swarmauri_live_model_amazon_nova` | `live` | `atomic-concrete` | `community` | yes |
| `50.0` | [swarmauri_live_model_gemini](50-community/swarmauri_live_model_gemini/) | `50-community/swarmauri_live_model_gemini` | `live` | `atomic-concrete` | `community` | yes |
| `50.0` | [swarmauri_live_model_openai](50-community/swarmauri_live_model_openai/) | `50-community/swarmauri_live_model_openai` | `live` | `atomic-concrete` | `community` | yes |
| `50.0` | [swarmauri_live_model_qwen](50-community/swarmauri_live_model_qwen/) | `50-community/swarmauri_live_model_qwen` | `live` | `atomic-concrete` | `community` | yes |
| `50.0` | [swarmauri_live_model_xai](50-community/swarmauri_live_model_xai/) | `50-community/swarmauri_live_model_xai` | `live` | `atomic-concrete` | `community` | yes |
| `50.0` | [swarmauri_llm_ai21](50-community/swarmauri_llm_ai21/) | `50-community/swarmauri_llm_ai21` | `llm` | `atomic-concrete` | `community` | yes |
| `50.0` | [swarmauri_llm_anthropic](50-community/swarmauri_llm_anthropic/) | `50-community/swarmauri_llm_anthropic` | `llm` | `atomic-concrete` | `community` | yes |
| `50.0` | [swarmauri_llm_azureopenai](50-community/swarmauri_llm_azureopenai/) | `50-community/swarmauri_llm_azureopenai` | `llm` | `atomic-concrete` | `community` | yes |
| `50.0` | [swarmauri_llm_cerebras](50-community/swarmauri_llm_cerebras/) | `50-community/swarmauri_llm_cerebras` | `llm` | `atomic-concrete` | `community` | yes |
| `50.0` | [swarmauri_llm_cloudflare](50-community/swarmauri_llm_cloudflare/) | `50-community/swarmauri_llm_cloudflare` | `llm` | `atomic-concrete` | `community` | yes |
| `50.0` | [swarmauri_llm_cohere](50-community/swarmauri_llm_cohere/) | `50-community/swarmauri_llm_cohere` | `llm` | `atomic-concrete` | `community` | yes |
| `50.0` | [swarmauri_llm_deepinfra](50-community/swarmauri_llm_deepinfra/) | `50-community/swarmauri_llm_deepinfra` | `llm` | `atomic-concrete` | `community` | yes |
| `50.0` | [swarmauri_llm_deepseek](50-community/swarmauri_llm_deepseek/) | `50-community/swarmauri_llm_deepseek` | `llm` | `atomic-concrete` | `community` | yes |
| `50.0` | [swarmauri_llm_falai](50-community/swarmauri_llm_falai/) | `50-community/swarmauri_llm_falai` | `llm` | `atomic-concrete` | `community` | yes |
| `50.0` | [swarmauri_llm_gemini](50-community/swarmauri_llm_gemini/) | `50-community/swarmauri_llm_gemini` | `llm` | `atomic-concrete` | `community` | yes |
| `50.0` | [swarmauri_llm_groq](50-community/swarmauri_llm_groq/) | `50-community/swarmauri_llm_groq` | `llm` | `atomic-concrete` | `community` | yes |
| `50.0` | [swarmauri_llm_hyperbolic](50-community/swarmauri_llm_hyperbolic/) | `50-community/swarmauri_llm_hyperbolic` | `llm` | `atomic-concrete` | `community` | yes |
| `50.0` | [swarmauri_llm_leptonai](50-community/swarmauri_llm_leptonai/) | `50-community/swarmauri_llm_leptonai` | `llm` | `atomic-concrete` | `community` | yes |
| `50.0` | [swarmauri_llm_llamacpp](50-community/swarmauri_llm_llamacpp/) | `50-community/swarmauri_llm_llamacpp` | `llm` | `atomic-concrete` | `community` | yes |
| `50.0` | [swarmauri_llm_mistral](50-community/swarmauri_llm_mistral/) | `50-community/swarmauri_llm_mistral` | `llm` | `atomic-concrete` | `community` | yes |
| `50.0` | [swarmauri_llm_nvidia_nim](50-community/swarmauri_llm_nvidia_nim/) | `50-community/swarmauri_llm_nvidia_nim` | `llm` | `atomic-concrete` | `community` | yes |
| `50.0` | [swarmauri_llm_openai](50-community/swarmauri_llm_openai/) | `50-community/swarmauri_llm_openai` | `llm` | `atomic-concrete` | `community` | yes |
| `50.0` | [swarmauri_llm_perplexity](50-community/swarmauri_llm_perplexity/) | `50-community/swarmauri_llm_perplexity` | `llm` | `atomic-concrete` | `community` | yes |
| `50.0` | [swarmauri_llm_whisper](50-community/swarmauri_llm_whisper/) | `50-community/swarmauri_llm_whisper` | `llm` | `atomic-concrete` | `community` | yes |
| `50.0` | [swarmauri_llm_xai](50-community/swarmauri_llm_xai/) | `50-community/swarmauri_llm_xai` | `llm` | `atomic-concrete` | `community` | yes |
| `50.0` | [swarmauri_measurement_mutualinformation](50-community/swarmauri_measurement_mutualinformation/) | `50-community/swarmauri_measurement_mutualinformation` | `measurement` | `atomic-concrete` | `community` | yes |
| `50.0` | [swarmauri_measurement_tokencountestimator](50-community/swarmauri_measurement_tokencountestimator/) | `50-community/swarmauri_measurement_tokencountestimator` | `measurement` | `atomic-concrete` | `community` | yes |
| `50.0` | [swarmauri_metric_hamming](50-community/swarmauri_metric_hamming/) | `50-community/swarmauri_metric_hamming` | `metric` | `atomic-concrete` | `community` | yes |
| `50.0` | [swarmauri_middleware_circuitbreaker](50-community/swarmauri_middleware_circuitbreaker/) | `50-community/swarmauri_middleware_circuitbreaker` | `middleware` | `atomic-concrete` | `community` | yes |
| `50.0` | [swarmauri_middleware_ratepolicy](50-community/swarmauri_middleware_ratepolicy/) | `50-community/swarmauri_middleware_ratepolicy` | `middleware` | `atomic-concrete` | `community` | yes |
| `50.0` | [swarmauri_ocr_pytesseract](50-community/swarmauri_ocr_pytesseract/) | `50-community/swarmauri_ocr_pytesseract` | `ocr` | `atomic-concrete` | `community` | yes |
| `50.0` | [swarmauri_parser_bertembedding](50-community/swarmauri_parser_bertembedding/) | `50-community/swarmauri_parser_bertembedding` | `parser` | `atomic-concrete` | `community` | yes |
| `50.0` | [swarmauri_parser_entityrecognition](50-community/swarmauri_parser_entityrecognition/) | `50-community/swarmauri_parser_entityrecognition` | `parser` | `atomic-concrete` | `community` | yes |
| `50.0` | [swarmauri_parser_fitzpdf](50-community/swarmauri_parser_fitzpdf/) | `50-community/swarmauri_parser_fitzpdf` | `parser` | `atomic-concrete` | `community` | yes |
| `50.0` | [swarmauri_parser_pypdf2](50-community/swarmauri_parser_pypdf2/) | `50-community/swarmauri_parser_pypdf2` | `parser` | `atomic-concrete` | `community` | yes |
| `50.0` | [swarmauri_parser_pypdftk](50-community/swarmauri_parser_pypdftk/) | `50-community/swarmauri_parser_pypdftk` | `parser` | `atomic-concrete` | `community` | yes |
| `50.0` | [swarmauri_parser_slate](50-community/swarmauri_parser_slate/) | `50-community/swarmauri_parser_slate` | `parser` | `atomic-concrete` | `community` | yes |
| `50.0` | [swarmauri_parser_textblob](50-community/swarmauri_parser_textblob/) | `50-community/swarmauri_parser_textblob` | `parser` | `atomic-concrete` | `community` | yes |
| `50.0` | [swarmauri_provider_amazon_nova](50-community/swarmauri_provider_amazon_nova/) | `50-community/swarmauri_provider_amazon_nova` | `provider` | `atomic-concrete` | `community` | yes |
| `50.0` | [swarmauri_provider_gemini](50-community/swarmauri_provider_gemini/) | `50-community/swarmauri_provider_gemini` | `provider` | `atomic-concrete` | `community` | yes |
| `50.0` | [swarmauri_provider_openai](50-community/swarmauri_provider_openai/) | `50-community/swarmauri_provider_openai` | `provider` | `atomic-concrete` | `community` | yes |
| `50.0` | [swarmauri_provider_openrouter](50-community/swarmauri_provider_openrouter/) | `50-community/swarmauri_provider_openrouter` | `provider` | `atomic-concrete` | `community` | yes |
| `50.0` | [swarmauri_provider_qwen](50-community/swarmauri_provider_qwen/) | `50-community/swarmauri_provider_qwen` | `provider` | `atomic-concrete` | `community` | yes |
| `50.0` | [swarmauri_provider_xai](50-community/swarmauri_provider_xai/) | `50-community/swarmauri_provider_xai` | `provider` | `atomic-concrete` | `community` | yes |
| `50.0` | [swarmauri_signing_dsse](50-community/swarmauri_signing_dsse/) | `50-community/swarmauri_signing_dsse` | `signing` | `atomic-concrete` | `community` | yes |
| `50.0` | [swarmauri_state_clipboard](50-community/swarmauri_state_clipboard/) | `50-community/swarmauri_state_clipboard` | `state` | `atomic-concrete` | `community` | yes |
| `50.0` | [swarmauri_tests_griffe](50-community/swarmauri_tests_griffe/) | `50-community/swarmauri_tests_griffe` | `tests` | `atomic-concrete` | `community` | yes |
| `50.0` | [swarmauri_tool_addcontenttorag](50-community/swarmauri_tool_addcontenttorag/) | `50-community/swarmauri_tool_addcontenttorag` | `tool` | `atomic-concrete` | `community` | yes |
| `50.0` | [swarmauri_tool_captchagenerator](50-community/swarmauri_tool_captchagenerator/) | `50-community/swarmauri_tool_captchagenerator` | `tool` | `atomic-concrete` | `community` | yes |
| `50.0` | [swarmauri_tool_createfile](50-community/swarmauri_tool_createfile/) | `50-community/swarmauri_tool_createfile` | `tool` | `atomic-concrete` | `community` | yes |
| `50.0` | [swarmauri_tool_dalechallreadability](50-community/swarmauri_tool_dalechallreadability/) | `50-community/swarmauri_tool_dalechallreadability` | `tool` | `atomic-concrete` | `community` | yes |
| `50.0` | [swarmauri_tool_downloadpdf](50-community/swarmauri_tool_downloadpdf/) | `50-community/swarmauri_tool_downloadpdf` | `tool` | `atomic-concrete` | `community` | yes |
| `50.0` | [swarmauri_tool_entityrecognition](50-community/swarmauri_tool_entityrecognition/) | `50-community/swarmauri_tool_entityrecognition` | `tool` | `atomic-concrete` | `community` | yes |
| `50.0` | [swarmauri_tool_findfile](50-community/swarmauri_tool_findfile/) | `50-community/swarmauri_tool_findfile` | `tool` | `atomic-concrete` | `community` | yes |
| `50.0` | [swarmauri_tool_folium](50-community/swarmauri_tool_folium/) | `50-community/swarmauri_tool_folium` | `tool` | `atomic-concrete` | `community` | yes |
| `50.0` | [swarmauri_tool_getmethodsignature](50-community/swarmauri_tool_getmethodsignature/) | `50-community/swarmauri_tool_getmethodsignature` | `tool` | `atomic-concrete` | `community` | yes |
| `50.0` | [swarmauri_tool_gmail](50-community/swarmauri_tool_gmail/) | `50-community/swarmauri_tool_gmail` | `tool` | `atomic-concrete` | `community` | yes |
| `50.0` | [swarmauri_tool_jupyterclearoutput](50-community/swarmauri_tool_jupyterclearoutput/) | `50-community/swarmauri_tool_jupyterclearoutput` | `tool` | `atomic-concrete` | `community` | yes |
| `50.0` | [swarmauri_tool_jupyterdisplay](50-community/swarmauri_tool_jupyterdisplay/) | `50-community/swarmauri_tool_jupyterdisplay` | `tool` | `atomic-concrete` | `community` | yes |
| `50.0` | [swarmauri_tool_jupyterdisplayhtml](50-community/swarmauri_tool_jupyterdisplayhtml/) | `50-community/swarmauri_tool_jupyterdisplayhtml` | `tool` | `atomic-concrete` | `community` | yes |
| `50.0` | [swarmauri_tool_jupyterexecuteandconvert](50-community/swarmauri_tool_jupyterexecuteandconvert/) | `50-community/swarmauri_tool_jupyterexecuteandconvert` | `tool` | `atomic-concrete` | `community` | yes |
| `50.0` | [swarmauri_tool_jupyterexecutecell](50-community/swarmauri_tool_jupyterexecutecell/) | `50-community/swarmauri_tool_jupyterexecutecell` | `tool` | `atomic-concrete` | `community` | yes |
| `50.0` | [swarmauri_tool_jupyterexecutenotebook](50-community/swarmauri_tool_jupyterexecutenotebook/) | `50-community/swarmauri_tool_jupyterexecutenotebook` | `tool` | `atomic-concrete` | `community` | yes |
| `50.0` | [swarmauri_tool_jupyterexecutenotebookwithparameters](50-community/swarmauri_tool_jupyterexecutenotebookwithparameters/) | `50-community/swarmauri_tool_jupyterexecutenotebookwithparameters` | `tool` | `atomic-concrete` | `community` | yes |
| `50.0` | [swarmauri_tool_jupyterexporthtml](50-community/swarmauri_tool_jupyterexporthtml/) | `50-community/swarmauri_tool_jupyterexporthtml` | `tool` | `atomic-concrete` | `community` | yes |
| `50.0` | [swarmauri_tool_jupyterexportlatex](50-community/swarmauri_tool_jupyterexportlatex/) | `50-community/swarmauri_tool_jupyterexportlatex` | `tool` | `atomic-concrete` | `community` | yes |
| `50.0` | [swarmauri_tool_jupyterexportmarkdown](50-community/swarmauri_tool_jupyterexportmarkdown/) | `50-community/swarmauri_tool_jupyterexportmarkdown` | `tool` | `atomic-concrete` | `community` | yes |
| `50.0` | [swarmauri_tool_jupyterexportpython](50-community/swarmauri_tool_jupyterexportpython/) | `50-community/swarmauri_tool_jupyterexportpython` | `tool` | `atomic-concrete` | `community` | yes |
| `50.0` | [swarmauri_tool_jupyterfromdict](50-community/swarmauri_tool_jupyterfromdict/) | `50-community/swarmauri_tool_jupyterfromdict` | `tool` | `atomic-concrete` | `community` | yes |
| `50.0` | [swarmauri_tool_jupytergetiopubmessage](50-community/swarmauri_tool_jupytergetiopubmessage/) | `50-community/swarmauri_tool_jupytergetiopubmessage` | `tool` | `atomic-concrete` | `community` | yes |
| `50.0` | [swarmauri_tool_jupytergetshellmessage](50-community/swarmauri_tool_jupytergetshellmessage/) | `50-community/swarmauri_tool_jupytergetshellmessage` | `tool` | `atomic-concrete` | `community` | yes |
| `50.0` | [swarmauri_tool_jupyterreadnotebook](50-community/swarmauri_tool_jupyterreadnotebook/) | `50-community/swarmauri_tool_jupyterreadnotebook` | `tool` | `atomic-concrete` | `community` | yes |
| `50.0` | [swarmauri_tool_jupyterruncell](50-community/swarmauri_tool_jupyterruncell/) | `50-community/swarmauri_tool_jupyterruncell` | `tool` | `atomic-concrete` | `community` | yes |
| `50.0` | [swarmauri_tool_jupytershutdownkernel](50-community/swarmauri_tool_jupytershutdownkernel/) | `50-community/swarmauri_tool_jupytershutdownkernel` | `tool` | `atomic-concrete` | `community` | yes |
| `50.0` | [swarmauri_tool_jupyterstartkernel](50-community/swarmauri_tool_jupyterstartkernel/) | `50-community/swarmauri_tool_jupyterstartkernel` | `tool` | `atomic-concrete` | `community` | yes |
| `50.0` | [swarmauri_tool_jupytervalidatenotebook](50-community/swarmauri_tool_jupytervalidatenotebook/) | `50-community/swarmauri_tool_jupytervalidatenotebook` | `tool` | `atomic-concrete` | `community` | yes |
| `50.0` | [swarmauri_tool_jupyterwritenotebook](50-community/swarmauri_tool_jupyterwritenotebook/) | `50-community/swarmauri_tool_jupyterwritenotebook` | `tool` | `atomic-concrete` | `community` | yes |
| `50.0` | [swarmauri_tool_lexicaldensity](50-community/swarmauri_tool_lexicaldensity/) | `50-community/swarmauri_tool_lexicaldensity` | `tool` | `atomic-concrete` | `community` | yes |
| `50.0` | [swarmauri_tool_listfiles](50-community/swarmauri_tool_listfiles/) | `50-community/swarmauri_tool_listfiles` | `tool` | `atomic-concrete` | `community` | yes |
| `50.0` | [swarmauri_tool_psutil](50-community/swarmauri_tool_psutil/) | `50-community/swarmauri_tool_psutil` | `tool` | `atomic-concrete` | `community` | yes |
| `50.0` | [swarmauri_tool_qrcodegenerator](50-community/swarmauri_tool_qrcodegenerator/) | `50-community/swarmauri_tool_qrcodegenerator` | `tool` | `atomic-concrete` | `community` | yes |
| `50.0` | [swarmauri_tool_queryimagevectorstore](50-community/swarmauri_tool_queryimagevectorstore/) | `50-community/swarmauri_tool_queryimagevectorstore` | `tool` | `atomic-concrete` | `community` | yes |
| `50.0` | [swarmauri_tool_queryknowledgebase](50-community/swarmauri_tool_queryknowledgebase/) | `50-community/swarmauri_tool_queryknowledgebase` | `tool` | `atomic-concrete` | `community` | yes |
| `50.0` | [swarmauri_tool_scrollfile](50-community/swarmauri_tool_scrollfile/) | `50-community/swarmauri_tool_scrollfile` | `tool` | `atomic-concrete` | `community` | yes |
| `50.0` | [swarmauri_tool_searchword](50-community/swarmauri_tool_searchword/) | `50-community/swarmauri_tool_searchword` | `tool` | `atomic-concrete` | `community` | yes |
| `50.0` | [swarmauri_tool_sentencecomplexity](50-community/swarmauri_tool_sentencecomplexity/) | `50-community/swarmauri_tool_sentencecomplexity` | `tool` | `atomic-concrete` | `community` | yes |
| `50.0` | [swarmauri_tool_sentimentanalysis](50-community/swarmauri_tool_sentimentanalysis/) | `50-community/swarmauri_tool_sentimentanalysis` | `tool` | `atomic-concrete` | `community` | yes |
| `50.0` | [swarmauri_tool_smogindex](50-community/swarmauri_tool_smogindex/) | `50-community/swarmauri_tool_smogindex` | `tool` | `atomic-concrete` | `community` | yes |
| `50.0` | [swarmauri_tool_textlength](50-community/swarmauri_tool_textlength/) | `50-community/swarmauri_tool_textlength` | `tool` | `atomic-concrete` | `community` | yes |
| `50.0` | [swarmauri_tool_webscraping](50-community/swarmauri_tool_webscraping/) | `50-community/swarmauri_tool_webscraping` | `tool` | `atomic-concrete` | `community` | yes |
| `50.0` | [swarmauri_tool_zapierhook](50-community/swarmauri_tool_zapierhook/) | `50-community/swarmauri_tool_zapierhook` | `tool` | `atomic-concrete` | `community` | yes |
| `50.0` | [swarmauri_vectorstore_annoy](50-community/swarmauri_vectorstore_annoy/) | `50-community/swarmauri_vectorstore_annoy` | `vectorstore` | `atomic-concrete` | `community` | yes |
| `50.0` | [swarmauri_vectorstore_cloudweaviate](50-community/swarmauri_vectorstore_cloudweaviate/) | `50-community/swarmauri_vectorstore_cloudweaviate` | `vectorstore` | `atomic-concrete` | `community` | yes |
| `50.0` | [swarmauri_vectorstore_duckdb](50-community/swarmauri_vectorstore_duckdb/) | `50-community/swarmauri_vectorstore_duckdb` | `vectorstore` | `atomic-concrete` | `community` | yes |
| `50.0` | [swarmauri_vectorstore_fs](50-community/swarmauri_vectorstore_fs/) | `50-community/swarmauri_vectorstore_fs` | `vectorstore` | `atomic-concrete` | `community` | yes |
| `50.0` | [swarmauri_vectorstore_git](50-community/swarmauri_vectorstore_git/) | `50-community/swarmauri_vectorstore_git` | `vectorstore` | `atomic-concrete` | `community` | yes |
| `50.0` | [swarmauri_vectorstore_neo4j](50-community/swarmauri_vectorstore_neo4j/) | `50-community/swarmauri_vectorstore_neo4j` | `vectorstore` | `atomic-concrete` | `community` | yes |
| `50.0` | [swarmauri_vectorstore_persistentchromadb](50-community/swarmauri_vectorstore_persistentchromadb/) | `50-community/swarmauri_vectorstore_persistentchromadb` | `vectorstore` | `atomic-concrete` | `community` | yes |
| `50.0` | [swarmauri_vectorstore_pinecone](50-community/swarmauri_vectorstore_pinecone/) | `50-community/swarmauri_vectorstore_pinecone` | `vectorstore` | `atomic-concrete` | `community` | yes |
| `50.0` | [swarmauri_vectorstore_qdrant](50-community/swarmauri_vectorstore_qdrant/) | `50-community/swarmauri_vectorstore_qdrant` | `vectorstore` | `atomic-concrete` | `community` | yes |
| `50.0` | [swarmauri_vectorstore_redis](50-community/swarmauri_vectorstore_redis/) | `50-community/swarmauri_vectorstore_redis` | `vectorstore` | `atomic-concrete` | `community` | yes |
| `50.0` | [swarmauri_video_lipsync_synclabs](50-community/swarmauri_video_lipsync_synclabs/) | `50-community/swarmauri_video_lipsync_synclabs` | `video` | `atomic-concrete` | `community` | yes |
| `50.1` | [swarmauri_llm_openrouter](50-community/swarmauri_llm_openrouter/) | `50-community/swarmauri_llm_openrouter` | `llm` | `composite-concrete` | `community` | yes |
| `50.1` | [swarmauri_matrix_hamming74](50-community/swarmauri_matrix_hamming74/) | `50-community/swarmauri_matrix_hamming74` | `matrix` | `composite-concrete` | `community` | yes |
| `50.1` | [swarmauri_vectorstore_mlm](50-community/swarmauri_vectorstore_mlm/) | `50-community/swarmauri_vectorstore_mlm` | `vectorstore` | `composite-concrete` | `community` | yes |
| `50.2` | [swarmauri_toolkit_github](50-community/swarmauri_toolkit_github/) | `50-community/swarmauri_toolkit_github` | `toolkit` | `orchestrator` | `community` | yes |
| `50.2` | [swarmauri_toolkit_jupytertoolkit](50-community/swarmauri_toolkit_jupytertoolkit/) | `50-community/swarmauri_toolkit_jupytertoolkit` | `toolkit` | `orchestrator` | `community` | yes |

### `60-plugins`

| Index | Package | Path | Family | Role | Maturity | Workspace |
|---|---|---|---|---|---|---|
| `60.0` | [EmbedXMP](60-plugins/EmbedXMP/) | `60-plugins/EmbedXMP` | `embedxmp` | `plugin` | `plugin` | yes |
| `60.0` | [swm_example_plugin](60-plugins/example_plugin/) | `60-plugins/example_plugin` | `example` | `plugin` | `plugin` | yes |
| `60.0` | [zdx](60-plugins/zdx/) | `60-plugins/zdx` | `zdx` | `plugin` | `plugin` | yes |
| `60.1` | [MediaSigner](60-plugins/media_signer/) | `60-plugins/media_signer` | `mediasigner` | `plugin-composite` | `plugin` | yes |
| `60.2` | [EmbeddedSigner](60-plugins/embedded_signer/) | `60-plugins/embedded_signer` | `embeddedsigner` | `plugin-orchestrator` | `plugin` | yes |

### `70-experimental`

| Index | Package | Path | Family | Role | Maturity | Workspace |
|---|---|---|---|---|---|---|
| `70.0` | [6w](70-experimental/6w/) | `70-experimental/6w` | `6w` | `experimental-atomic` | `experimental` | no |
| `70.0` | [6x](70-experimental/6x/) | `70-experimental/6x` | `6x` | `experimental-atomic` | `experimental` | no |
| `70.0` | [6y](70-experimental/6y/) | `70-experimental/6y` | `6y` | `experimental-atomic` | `experimental` | no |
| `70.0` | [6z](70-experimental/6z/) | `70-experimental/6z` | `6z` | `experimental-atomic` | `experimental` | no |
| `70.0` | [77](70-experimental/77/) | `70-experimental/77` | `77` | `experimental-atomic` | `experimental` | no |
| `70.0` | [9x](70-experimental/9x/) | `70-experimental/9x` | `9x` | `experimental-atomic` | `experimental` | no |
| `70.0` | [swarmauri_canon_http](70-experimental/swarmauri_canon_http/) | `70-experimental/swarmauri_canon_http` | `canon` | `experimental-atomic` | `experimental` | no |
| `70.0` | [catoml](70-experimental/catoml/) | `70-experimental/catoml` | `catoml` | `experimental-atomic` | `experimental` | no |
| `70.0` | [cayaml](70-experimental/cayaml/) | `70-experimental/cayaml` | `cayaml` | `experimental-atomic` | `experimental` | no |
| `70.0` | [swarmauri_certs_pkcs11](70-experimental/swarmauri_certs_pkcs11/) | `70-experimental/swarmauri_certs_pkcs11` | `certs` | `experimental-atomic` | `experimental` | yes |
| `70.0` | [swarmauri_crypto_sodium](70-experimental/swarmauri_crypto_sodium/) | `70-experimental/swarmauri_crypto_sodium` | `crypto` | `experimental-atomic` | `experimental` | yes |
| `70.0` | [DistanceMetrics](70-experimental/RapidSimilarity/DistanceMetrics/) | `70-experimental/RapidSimilarity/DistanceMetrics` | `distancemetrics` | `experimental-atomic` | `experimental` | no |
| `70.0` | [do](70-experimental/do/) | `70-experimental/do` | `do` | `experimental-atomic` | `experimental` | no |
| `70.0` | [FastTokenizer](70-experimental/FastTokenizer/) | `70-experimental/FastTokenizer` | `fasttokenizer` | `experimental-atomic` | `experimental` | no |
| `70.0` | [g9](70-experimental/g9/) | `70-experimental/g9` | `g9` | `experimental-atomic` | `experimental` | no |
| `70.0` | [gk](70-experimental/gk/) | `70-experimental/gk` | `gk` | `experimental-atomic` | `experimental` | no |
| `70.0` | [IndexBuilder](70-experimental/RapidSimilarity/IndexBuilder/) | `70-experimental/RapidSimilarity/IndexBuilder` | `indexbuilder` | `experimental-atomic` | `experimental` | no |
| `70.0` | [jaml](70-experimental/jaml/) | `70-experimental/jaml` | `jaml` | `experimental-atomic` | `experimental` | no |
| `70.0` | [jz](70-experimental/jz/) | `70-experimental/jz` | `jz` | `experimental-atomic` | `experimental` | no |
| `70.0` | [swarmauri_keyprovider_pkcs11](70-experimental/swarmauri_keyprovider_pkcs11/) | `70-experimental/swarmauri_keyprovider_pkcs11` | `keyprovider` | `experimental-atomic` | `experimental` | yes |
| `70.0` | [layout_engine](70-experimental/layout_engine/) | `70-experimental/layout_engine` | `layout` | `experimental-atomic` | `experimental` | no |
| `70.0` | [monotone-ops](70-experimental/monotone_ops/) | `70-experimental/monotone_ops` | `monotone` | `experimental-atomic` | `experimental` | yes |
| `70.0` | [mto](70-experimental/mto/) | `70-experimental/mto` | `mto` | `experimental-atomic` | `experimental` | yes |
| `70.0` | [swarmauri_parser_asn1](70-experimental/swarmauri_parser_asn1/) | `70-experimental/swarmauri_parser_asn1` | `parser` | `experimental-atomic` | `experimental` | yes |
| `70.0` | [pj](70-experimental/pj/) | `70-experimental/pj` | `pj` | `experimental-atomic` | `experimental` | no |
| `70.0` | [ptree_dag_extension_example](70-experimental/ptree_dag_extension_example/) | `70-experimental/ptree_dag_extension_example` | `ptree` | `experimental-atomic` | `experimental` | yes |
| `70.0` | [QueryEngine](70-experimental/RapidSimilarity/QueryEngine/) | `70-experimental/RapidSimilarity/QueryEngine` | `queryengine` | `experimental-atomic` | `experimental` | no |
| `70.0` | [s.f](70-experimental/s_f/) | `70-experimental/s_f` | `s.f` | `experimental-atomic` | `experimental` | no |
| `70.0` | [sfw](70-experimental/sfw/) | `70-experimental/sfw` | `sfw` | `experimental-atomic` | `experimental` | no |
| `70.0` | [snt](70-experimental/snt/) | `70-experimental/snt` | `snt` | `experimental-atomic` | `experimental` | no |
| `70.0` | [swarmauri_tests_component](70-experimental/swarmauri_tests_component/) | `70-experimental/swarmauri_tests_component` | `tests` | `experimental-atomic` | `experimental` | yes |
| `70.0` | [swarmauri_tests_loc_tersity](70-experimental/swarmauri_tests_loc_tersity/) | `70-experimental/swarmauri_tests_loc_tersity` | `tests` | `experimental-atomic` | `experimental` | yes |
| `70.0` | [swarmauri_tests_pylicense](70-experimental/swarmauri_tests_pylicense/) | `70-experimental/swarmauri_tests_pylicense` | `tests` | `experimental-atomic` | `experimental` | yes |
| `70.0` | [swarmauri_tests_readme_examples](70-experimental/swarmauri_tests_readme_examples/) | `70-experimental/swarmauri_tests_readme_examples` | `tests` | `experimental-atomic` | `experimental` | yes |
| `70.0` | [tigr](70-experimental/tigr/) | `70-experimental/tigr` | `tigr` | `experimental-atomic` | `experimental` | yes |
| `70.0` | [uu](70-experimental/uu/) | `70-experimental/uu` | `uu` | `experimental-atomic` | `experimental` | no |
| `70.0` | [vb](70-experimental/vb/) | `70-experimental/vb` | `vb` | `experimental-atomic` | `experimental` | no |
| `70.0` | [xj](70-experimental/xj/) | `70-experimental/xj` | `xj` | `experimental-atomic` | `experimental` | no |
| `70.0` | [xk](70-experimental/xk/) | `70-experimental/xk` | `xk` | `experimental-atomic` | `experimental` | no |
| `70.0` | [xz](70-experimental/xz/) | `70-experimental/xz` | `xz` | `experimental-atomic` | `experimental` | no |
| `70.0` | [ye](70-experimental/ye/) | `70-experimental/ye` | `ye` | `experimental-atomic` | `experimental` | no |
| `70.0` | [ymls](70-experimental/ymls/) | `70-experimental/ymls` | `ymls` | `experimental-atomic` | `experimental` | no |
| `70.0` | [zr0](70-experimental/zr0/) | `70-experimental/zr0` | `zr0` | `experimental-atomic` | `experimental` | no |
| `70.1` | [layout_engine_atoms](70-experimental/layout_engine_atoms/) | `70-experimental/layout_engine_atoms` | `layout` | `experimental-composite` | `experimental` | no |
| `70.2` | [swarmauri_workflow_statedriven](70-experimental/swarmauri_workflow_statedriven/) | `70-experimental/swarmauri_workflow_statedriven` | `workflow` | `experimental-orchestrator` | `experimental` | yes |

### `80-facades`

| Index | Package | Path | Family | Role | Maturity | Workspace |
|---|---|---|---|---|---|---|
| `80.3` | [swarmauri](80-facades/swarmauri/) | `80-facades/swarmauri` | `facade` | `facade` | `facade` | yes |

### `90-deprecated`

| Index | Package | Path | Family | Role | Maturity | Workspace |
|---|---|---|---|---|---|---|
| `90.0` | [swarmauri_documentstore_redis](90-deprecated/swarmauri_documentstore_redis/) | `90-deprecated/swarmauri_documentstore_redis` | `documentstore` | `compat` | `deprecated` | no |
| `90.0` | [swarmauri_embedding_tfidf](90-deprecated/swarmauri_embedding_tfidf/) | `90-deprecated/swarmauri_embedding_tfidf` | `embedding` | `compat` | `deprecated` | no |
| `90.0` | [swarmauri_experimental](90-deprecated/swarmauri_experimental/) | `90-deprecated/swarmauri_experimental` | `experimental` | `compat` | `deprecated` | yes |
| `90.0` | [swarmauri_llm_playht](90-deprecated/swarmauri_llm_playht/) | `90-deprecated/swarmauri_llm_playht` | `llm` | `compat` | `deprecated` | yes |
| `90.0` | [swarmauri_tts_playht](90-deprecated/swarmauri_tts_playht/) | `90-deprecated/swarmauri_tts_playht` | `tts` | `compat` | `deprecated` | yes |
| `90.1` | [swarmauri_vectorstore_tfidf](90-deprecated/swarmauri_vectorstore_tfidf/) | `90-deprecated/swarmauri_vectorstore_tfidf` | `vectorstore` | `compat-composite` | `deprecated` | no |

## By Layer And Order

### `00.0`

| Package | Family | Role | Source | Composes | Order reason |
|---|---|---|---|---:|---|
| [swarmauri_typing](00-typing/swarmauri_typing/) | `typing` | `atomic-foundation` | `inferred` | 0 | foundation layers are atomic by policy |

### `10.0`

| Package | Family | Role | Source | Composes | Order reason |
|---|---|---|---|---:|---|
| [swarmauri_core](10-interfaces/swarmauri_core/) | `interfaces` | `interface-contract` | `inferred` | 0 | foundation layers are atomic by policy |

### `20.0`

| Package | Family | Role | Source | Composes | Order reason |
|---|---|---|---|---:|---|
| [swarmauri_base](20-bases/swarmauri_base/) | `bases` | `base-implementation` | `inferred` | 0 | foundation layers are atomic by policy |

### `30.0`

| Package | Family | Role | Source | Composes | Order reason |
|---|---|---|---|---:|---|
| [swarmauri_standard](30-standard-kernel/swarmauri_standard/) | `standard-kernel` | `standard-kernel` | `inferred` | 0 | foundation layers are atomic by policy |

### `40.0`

| Package | Family | Role | Source | Composes | Order reason |
|---|---|---|---|---:|---|
| [swarmauri_agent_compacting](40-standards/swarmauri_agent_compacting/) | `agent` | `atomic-concrete` | `inferred` | 0 | single-capability package by default |
| [swarmauri_agent_package_maintenance](40-standards/swarmauri_agent_package_maintenance/) | `agent` | `atomic-concrete` | `inferred` | 0 | single-capability package by default |
| [swarmauri_agent_realtime](40-standards/swarmauri_agent_realtime/) | `agent` | `atomic-concrete` | `inferred` | 0 | single-capability package by default |
| [swarmauri_agent_runner](40-standards/swarmauri_agent_runner/) | `agent` | `atomic-concrete` | `inferred` | 0 | single-capability package by default |
| [swarmauri_agent_skill](40-standards/swarmauri_agent_skill/) | `agent` | `atomic-concrete` | `inferred` | 0 | single-capability package by default |
| [swarmauri_agent_texttospeech](40-standards/swarmauri_agent_texttospeech/) | `agent` | `atomic-concrete` | `inferred` | 0 | single-capability package by default |
| [swarmauri_agent_wimse](40-standards/swarmauri_agent_wimse/) | `agent` | `atomic-concrete` | `inferred` | 0 | single-capability package by default |
| [swarmauri_auth_idp_apple](40-standards/swarmauri_auth_idp_apple/) | `auth_idp` | `atomic-concrete` | `inferred` | 0 | single-capability package by default |
| [swarmauri_auth_idp_aws](40-standards/swarmauri_auth_idp_aws/) | `auth_idp` | `atomic-concrete` | `inferred` | 0 | single-capability package by default |
| [swarmauri_auth_idp_azure](40-standards/swarmauri_auth_idp_azure/) | `auth_idp` | `atomic-concrete` | `inferred` | 0 | single-capability package by default |
| [swarmauri_auth_idp_cognito](40-standards/swarmauri_auth_idp_cognito/) | `auth_idp` | `atomic-concrete` | `inferred` | 0 | single-capability package by default |
| [swarmauri_auth_idp_facebook](40-standards/swarmauri_auth_idp_facebook/) | `auth_idp` | `atomic-concrete` | `inferred` | 0 | single-capability package by default |
| [swarmauri_auth_idp_gitea](40-standards/swarmauri_auth_idp_gitea/) | `auth_idp` | `atomic-concrete` | `inferred` | 0 | single-capability package by default |
| [swarmauri_auth_idp_github](40-standards/swarmauri_auth_idp_github/) | `auth_idp` | `atomic-concrete` | `inferred` | 0 | single-capability package by default |
| [swarmauri_auth_idp_gitlab](40-standards/swarmauri_auth_idp_gitlab/) | `auth_idp` | `atomic-concrete` | `inferred` | 0 | single-capability package by default |
| [swarmauri_auth_idp_google](40-standards/swarmauri_auth_idp_google/) | `auth_idp` | `atomic-concrete` | `inferred` | 0 | single-capability package by default |
| [swarmauri_auth_idp_keycloak](40-standards/swarmauri_auth_idp_keycloak/) | `auth_idp` | `atomic-concrete` | `inferred` | 0 | single-capability package by default |
| [swarmauri_auth_idp_okta](40-standards/swarmauri_auth_idp_okta/) | `auth_idp` | `atomic-concrete` | `inferred` | 0 | single-capability package by default |
| [swarmauri_auth_idp_salesforce](40-standards/swarmauri_auth_idp_salesforce/) | `auth_idp` | `atomic-concrete` | `inferred` | 0 | single-capability package by default |
| [swarmauri_billing_mock](40-standards/swarmauri_billing_mock/) | `billing` | `atomic-concrete` | `inferred` | 0 | single-capability package by default |
| [swarmauri_billing_stripe](40-standards/swarmauri_billing_stripe/) | `billing` | `atomic-concrete` | `inferred` | 0 | single-capability package by default |
| [swarmauri_certs_local_ca](40-standards/swarmauri_certs_local_ca/) | `certs` | `atomic-concrete` | `inferred` | 0 | single-capability package by default |
| [swarmauri_certs_remote_ca](40-standards/swarmauri_certs_remote_ca/) | `certs` | `atomic-concrete` | `inferred` | 0 | single-capability package by default |
| [swarmauri_certs_self_signed](40-standards/swarmauri_certs_self_signed/) | `certs` | `atomic-concrete` | `inferred` | 0 | single-capability package by default |
| [swarmauri_certs_x509verify](40-standards/swarmauri_certs_x509verify/) | `certs` | `atomic-concrete` | `inferred` | 0 | single-capability package by default |
| [swarmauri_cipher_suite_cades](40-standards/swarmauri_cipher_suite_cades/) | `cipher_suite` | `atomic-concrete` | `inferred` | 0 | single-capability package by default |
| [swarmauri_cipher_suite_cnsa20](40-standards/swarmauri_cipher_suite_cnsa20/) | `cipher_suite` | `atomic-concrete` | `inferred` | 0 | single-capability package by default |
| [swarmauri_cipher_suite_cose](40-standards/swarmauri_cipher_suite_cose/) | `cipher_suite` | `atomic-concrete` | `inferred` | 0 | single-capability package by default |
| [swarmauri_cipher_suite_fips1403](40-standards/swarmauri_cipher_suite_fips1403/) | `cipher_suite` | `atomic-concrete` | `inferred` | 0 | single-capability package by default |
| [swarmauri_cipher_suite_fips203](40-standards/swarmauri_cipher_suite_fips203/) | `cipher_suite` | `atomic-concrete` | `inferred` | 0 | single-capability package by default |
| [swarmauri_cipher_suite_fips204](40-standards/swarmauri_cipher_suite_fips204/) | `cipher_suite` | `atomic-concrete` | `inferred` | 0 | single-capability package by default |
| [swarmauri_cipher_suite_fips205](40-standards/swarmauri_cipher_suite_fips205/) | `cipher_suite` | `atomic-concrete` | `inferred` | 0 | single-capability package by default |
| [swarmauri_cipher_suite_ipsec](40-standards/swarmauri_cipher_suite_ipsec/) | `cipher_suite` | `atomic-concrete` | `inferred` | 0 | single-capability package by default |
| [swarmauri_cipher_suite_jwa](40-standards/swarmauri_cipher_suite_jwa/) | `cipher_suite` | `atomic-concrete` | `inferred` | 0 | single-capability package by default |
| [swarmauri_cipher_suite_pades](40-standards/swarmauri_cipher_suite_pades/) | `cipher_suite` | `atomic-concrete` | `inferred` | 0 | single-capability package by default |
| [swarmauri_cipher_suite_pep458](40-standards/swarmauri_cipher_suite_pep458/) | `cipher_suite` | `atomic-concrete` | `inferred` | 0 | single-capability package by default |
| [swarmauri_cipher_suite_sigstore](40-standards/swarmauri_cipher_suite_sigstore/) | `cipher_suite` | `atomic-concrete` | `inferred` | 0 | single-capability package by default |
| [swarmauri_cipher_suite_ssh](40-standards/swarmauri_cipher_suite_ssh/) | `cipher_suite` | `atomic-concrete` | `inferred` | 0 | single-capability package by default |
| [swarmauri_cipher_suite_tls13](40-standards/swarmauri_cipher_suite_tls13/) | `cipher_suite` | `atomic-concrete` | `inferred` | 0 | single-capability package by default |
| [swarmauri_cipher_suite_webauthn](40-standards/swarmauri_cipher_suite_webauthn/) | `cipher_suite` | `atomic-concrete` | `inferred` | 0 | single-capability package by default |
| [swarmauri_cipher_suite_xades](40-standards/swarmauri_cipher_suite_xades/) | `cipher_suite` | `atomic-concrete` | `inferred` | 0 | single-capability package by default |
| [swarmauri_cipher_suite_yubikey](40-standards/swarmauri_cipher_suite_yubikey/) | `cipher_suite` | `atomic-concrete` | `inferred` | 0 | single-capability package by default |
| [swarmauri_cipher_suite_yubikey_fips](40-standards/swarmauri_cipher_suite_yubikey_fips/) | `cipher_suite` | `atomic-concrete` | `inferred` | 0 | single-capability package by default |
| [swarmauri_conversation_compacting](40-standards/swarmauri_conversation_compacting/) | `conversation` | `atomic-concrete` | `inferred` | 0 | single-capability package by default |
| [swarmauri_crypto_ecdh_es_a128kw](40-standards/swarmauri_crypto_ecdh_es_a128kw/) | `crypto` | `atomic-concrete` | `inferred` | 0 | single-capability package by default |
| [swarmauri_crypto_jwe](40-standards/swarmauri_crypto_jwe/) | `crypto` | `atomic-concrete` | `inferred` | 0 | single-capability package by default |
| [swarmauri_crypto_nacl_pkcs11](40-standards/swarmauri_crypto_nacl_pkcs11/) | `crypto` | `atomic-concrete` | `inferred` | 0 | single-capability package by default |
| [swarmauri_crypto_paramiko](40-standards/swarmauri_crypto_paramiko/) | `crypto` | `atomic-concrete` | `inferred` | 0 | single-capability package by default |
| [swarmauri_crypto_pgp](40-standards/swarmauri_crypto_pgp/) | `crypto` | `atomic-concrete` | `inferred` | 0 | single-capability package by default |
| [swarmauri_crypto_rust](40-standards/swarmauri_crypto_rust/) | `crypto` | `atomic-concrete` | `inferred` | 0 | single-capability package by default |
| [swarmauri_delegation_attenuating](40-standards/swarmauri_delegation_attenuating/) | `delegation` | `atomic-concrete` | `inferred` | 0 | single-capability package by default |
| [swarmauri_distance_canberra](40-standards/swarmauri_distance_canberra/) | `distance` | `atomic-concrete` | `inferred` | 0 | single-capability package by default |
| [swarmauri_distance_chebyshev](40-standards/swarmauri_distance_chebyshev/) | `distance` | `atomic-concrete` | `inferred` | 0 | single-capability package by default |
| [swarmauri_distance_chi_squared](40-standards/swarmauri_distance_chi_squared/) | `distance` | `atomic-concrete` | `inferred` | 0 | single-capability package by default |
| [swarmauri_distance_cosine](40-standards/swarmauri_distance_cosine/) | `distance` | `atomic-concrete` | `inferred` | 0 | single-capability package by default |
| [swarmauri_distance_euclidean](40-standards/swarmauri_distance_euclidean/) | `distance` | `atomic-concrete` | `inferred` | 0 | single-capability package by default |
| [swarmauri_distance_haversine](40-standards/swarmauri_distance_haversine/) | `distance` | `atomic-concrete` | `inferred` | 0 | single-capability package by default |
| [swarmauri_distance_jaccard_index](40-standards/swarmauri_distance_jaccard_index/) | `distance` | `atomic-concrete` | `inferred` | 0 | single-capability package by default |
| [swarmauri_distance_levenshtein](40-standards/swarmauri_distance_levenshtein/) | `distance` | `atomic-concrete` | `inferred` | 0 | single-capability package by default |
| [swarmauri_distance_manhattan](40-standards/swarmauri_distance_manhattan/) | `distance` | `atomic-concrete` | `inferred` | 0 | single-capability package by default |
| [swarmauri_distance_minkowski](40-standards/swarmauri_distance_minkowski/) | `distance` | `atomic-concrete` | `inferred` | 0 | single-capability package by default |
| [swarmauri_distance_sorensen_dice](40-standards/swarmauri_distance_sorensen_dice/) | `distance` | `atomic-concrete` | `inferred` | 0 | single-capability package by default |
| [swarmauri_distance_squared_euclidean](40-standards/swarmauri_distance_squared_euclidean/) | `distance` | `atomic-concrete` | `inferred` | 0 | single-capability package by default |
| [swarmauri_embedding_doc2vec](40-standards/swarmauri_embedding_doc2vec/) | `embedding` | `atomic-concrete` | `inferred` | 0 | single-capability package by default |
| [swarmauri_embedding_nmf](40-standards/swarmauri_embedding_nmf/) | `embedding` | `atomic-concrete` | `inferred` | 0 | single-capability package by default |
| [swarmauri_evaluator_abstractmethods](40-standards/swarmauri_evaluator_abstractmethods/) | `evaluator` | `atomic-concrete` | `inferred` | 0 | single-capability package by default |
| [swarmauri_evaluator_anyusage](40-standards/swarmauri_evaluator_anyusage/) | `evaluator` | `atomic-concrete` | `inferred` | 0 | single-capability package by default |
| [swarmauri_evaluator_constanttime](40-standards/swarmauri_evaluator_constanttime/) | `evaluator` | `atomic-concrete` | `inferred` | 0 | single-capability package by default |
| [swarmauri_evaluator_externalimports](40-standards/swarmauri_evaluator_externalimports/) | `evaluator` | `atomic-concrete` | `inferred` | 0 | single-capability package by default |
| [swarmauri_evaluator_subprocess](40-standards/swarmauri_evaluator_subprocess/) | `evaluator` | `atomic-concrete` | `inferred` | 0 | single-capability package by default |
| [swarmauri_evaluatorpool_accessibility](40-standards/swarmauri_evaluatorpool_accessibility/) | `evaluatorpool` | `atomic-concrete` | `inferred` | 0 | single-capability package by default |
| [swm_example_package](40-standards/swm_example_package/) | `example` | `atomic-concrete` | `inferred` | 0 | single-capability package by default |
| [swarmauri_execution_default](40-standards/swarmauri_execution_default/) | `execution` | `atomic-concrete` | `inferred` | 0 | single-capability package by default |
| [swarmauri_gitfilter_gh_release](40-standards/swarmauri_gitfilter_gh_release/) | `gitfilter` | `atomic-concrete` | `inferred` | 0 | single-capability package by default |
| [swarmauri_gitfilter_minio](40-standards/swarmauri_gitfilter_minio/) | `gitfilter` | `atomic-concrete` | `inferred` | 0 | single-capability package by default |
| [swarmauri_gitfilter_s3fs](40-standards/swarmauri_gitfilter_s3fs/) | `gitfilter` | `atomic-concrete` | `inferred` | 0 | single-capability package by default |
| [swarmauri_grantstore_sqlite](40-standards/swarmauri_grantstore_sqlite/) | `grantstore` | `atomic-concrete` | `inferred` | 0 | single-capability package by default |
| [swarmauri_invoker_default](40-standards/swarmauri_invoker_default/) | `invoker` | `atomic-concrete` | `inferred` | 0 | single-capability package by default |
| [swarmauri_keyprovider_file](40-standards/swarmauri_keyprovider_file/) | `keyprovider` | `atomic-concrete` | `inferred` | 0 | single-capability package by default |
| [swarmauri_keyprovider_inmemory](40-standards/swarmauri_keyprovider_inmemory/) | `keyprovider` | `atomic-concrete` | `inferred` | 0 | single-capability package by default |
| [swarmauri_keyprovider_local](40-standards/swarmauri_keyprovider_local/) | `keyprovider` | `atomic-concrete` | `inferred` | 0 | single-capability package by default |
| [swarmauri_keyprovider_ssh](40-standards/swarmauri_keyprovider_ssh/) | `keyprovider` | `atomic-concrete` | `inferred` | 0 | single-capability package by default |
| [swamauri_metric_wasserstein](40-standards/swamauri_metric_wasserstein/) | `metric` | `atomic-concrete` | `inferred` | 0 | single-capability package by default |
| [swarmauri_middleware_bulkhead](40-standards/swarmauri_middleware_bulkhead/) | `middleware` | `atomic-concrete` | `inferred` | 0 | single-capability package by default |
| [swarmauri_middleware_cachecontrol](40-standards/swarmauri_middleware_cachecontrol/) | `middleware` | `atomic-concrete` | `inferred` | 0 | single-capability package by default |
| [swarmauri_middleware_cors](40-standards/swarmauri_middleware_cors/) | `middleware` | `atomic-concrete` | `inferred` | 0 | single-capability package by default |
| [swarmauri_middleware_exceptionhandling](40-standards/swarmauri_middleware_exceptionhandling/) | `middleware` | `atomic-concrete` | `inferred` | 0 | single-capability package by default |
| [swarmauri_middleware_gzipcompression](40-standards/swarmauri_middleware_gzipcompression/) | `middleware` | `atomic-concrete` | `inferred` | 0 | single-capability package by default |
| [swarmauri_middleware_httpsig](40-standards/swarmauri_middleware_httpsig/) | `middleware` | `atomic-concrete` | `inferred` | 0 | single-capability package by default |
| [swarmauri_middleware_jsonrpc](40-standards/swarmauri_middleware_jsonrpc/) | `middleware` | `atomic-concrete` | `inferred` | 0 | single-capability package by default |
| [swarmauri_middleware_jwksverifier](40-standards/swarmauri_middleware_jwksverifier/) | `middleware` | `atomic-concrete` | `inferred` | 0 | single-capability package by default |
| [swarmauri_middleware_llamaguard](40-standards/swarmauri_middleware_llamaguard/) | `middleware` | `atomic-concrete` | `inferred` | 0 | single-capability package by default |
| [swarmauri_middleware_logging](40-standards/swarmauri_middleware_logging/) | `middleware` | `atomic-concrete` | `inferred` | 0 | single-capability package by default |
| [swarmauri_middleware_ratelimit](40-standards/swarmauri_middleware_ratelimit/) | `middleware` | `atomic-concrete` | `inferred` | 0 | single-capability package by default |
| [swarmauri_middleware_securityheaders](40-standards/swarmauri_middleware_securityheaders/) | `middleware` | `atomic-concrete` | `inferred` | 0 | single-capability package by default |
| [swarmauri_middleware_session](40-standards/swarmauri_middleware_session/) | `middleware` | `atomic-concrete` | `inferred` | 0 | single-capability package by default |
| [swarmauri_middleware_stdio](40-standards/swarmauri_middleware_stdio/) | `middleware` | `atomic-concrete` | `inferred` | 0 | single-capability package by default |
| [swarmauri_middleware_time](40-standards/swarmauri_middleware_time/) | `middleware` | `atomic-concrete` | `inferred` | 0 | single-capability package by default |
| [swarmauri_mre_crypto_age](40-standards/swarmauri_mre_crypto_age/) | `mre_crypto` | `atomic-concrete` | `inferred` | 0 | single-capability package by default |
| [swarmauri_mre_crypto_ecdh_es_kw](40-standards/swarmauri_mre_crypto_ecdh_es_kw/) | `mre_crypto` | `atomic-concrete` | `inferred` | 0 | single-capability package by default |
| [swarmauri_mre_crypto_keyring](40-standards/swarmauri_mre_crypto_keyring/) | `mre_crypto` | `atomic-concrete` | `inferred` | 0 | single-capability package by default |
| [swarmauri_mre_crypto_pgp](40-standards/swarmauri_mre_crypto_pgp/) | `mre_crypto` | `atomic-concrete` | `inferred` | 0 | single-capability package by default |
| [swarmauri_mre_crypto_shamir](40-standards/swarmauri_mre_crypto_shamir/) | `mre_crypto` | `atomic-concrete` | `inferred` | 0 | single-capability package by default |
| [swarmauri_parser_beautifulsoupelement](40-standards/swarmauri_parser_beautifulsoupelement/) | `parser` | `atomic-concrete` | `inferred` | 0 | single-capability package by default |
| [swarmauri_parser_keywordextractor](40-standards/swarmauri_parser_keywordextractor/) | `parser` | `atomic-concrete` | `inferred` | 0 | single-capability package by default |
| [swarmauri_permission_explicit](40-standards/swarmauri_permission_explicit/) | `permission` | `atomic-concrete` | `inferred` | 0 | single-capability package by default |
| [swarmauri_pop_cwt](40-standards/swarmauri_pop_cwt/) | `pop` | `atomic-concrete` | `inferred` | 0 | single-capability package by default |
| [swarmauri_pop_dpop](40-standards/swarmauri_pop_dpop/) | `pop` | `atomic-concrete` | `inferred` | 0 | single-capability package by default |
| [swarmauri_pop_x509](40-standards/swarmauri_pop_x509/) | `pop` | `atomic-concrete` | `inferred` | 0 | single-capability package by default |
| [swarmauri_process_docker](40-standards/swarmauri_process_docker/) | `process` | `atomic-concrete` | `inferred` | 0 | single-capability package by default |
| [swarmauri_process_kubernetes](40-standards/swarmauri_process_kubernetes/) | `process` | `atomic-concrete` | `inferred` | 0 | single-capability package by default |
| [swarmauri_process_subprocess](40-standards/swarmauri_process_subprocess/) | `process` | `atomic-concrete` | `inferred` | 0 | single-capability package by default |
| [swarmauri_prompt_j2prompttemplate](40-standards/swarmauri_prompt_j2prompttemplate/) | `prompt` | `atomic-concrete` | `inferred` | 0 | single-capability package by default |
| [swarmauri_publisher_rabbitmq](40-standards/swarmauri_publisher_rabbitmq/) | `publisher` | `atomic-concrete` | `inferred` | 0 | single-capability package by default |
| [swarmauri_publisher_redis](40-standards/swarmauri_publisher_redis/) | `publisher` | `atomic-concrete` | `inferred` | 0 | single-capability package by default |
| [swarmauri_publisher_webhook](40-standards/swarmauri_publisher_webhook/) | `publisher` | `atomic-concrete` | `inferred` | 0 | single-capability package by default |
| [swarmauri_runstore_sqlite](40-standards/swarmauri_runstore_sqlite/) | `runstore` | `atomic-concrete` | `inferred` | 0 | single-capability package by default |
| [swarmauri_signing_ca](40-standards/swarmauri_signing_ca/) | `signing` | `atomic-concrete` | `inferred` | 0 | single-capability package by default |
| [swarmauri_signing_cms](40-standards/swarmauri_signing_cms/) | `signing` | `atomic-concrete` | `inferred` | 0 | single-capability package by default |
| [swarmauri_signing_ecdsa](40-standards/swarmauri_signing_ecdsa/) | `signing` | `atomic-concrete` | `inferred` | 0 | single-capability package by default |
| [swarmauri_signing_ed25519](40-standards/swarmauri_signing_ed25519/) | `signing` | `atomic-concrete` | `inferred` | 0 | single-capability package by default |
| [swarmauri_signing_hmac](40-standards/swarmauri_signing_hmac/) | `signing` | `atomic-concrete` | `inferred` | 0 | single-capability package by default |
| [swarmauri_signing_openpgp](40-standards/swarmauri_signing_openpgp/) | `signing` | `atomic-concrete` | `inferred` | 0 | single-capability package by default |
| [swarmauri_signing_pep458](40-standards/swarmauri_signing_pep458/) | `signing` | `atomic-concrete` | `inferred` | 0 | single-capability package by default |
| [swarmauri_signing_pgp](40-standards/swarmauri_signing_pgp/) | `signing` | `atomic-concrete` | `inferred` | 0 | single-capability package by default |
| [swarmauri_signing_rsa](40-standards/swarmauri_signing_rsa/) | `signing` | `atomic-concrete` | `inferred` | 0 | single-capability package by default |
| [swarmauri_signing_secp256k1](40-standards/swarmauri_signing_secp256k1/) | `signing` | `atomic-concrete` | `inferred` | 0 | single-capability package by default |
| [swarmauri_signing_sigv4](40-standards/swarmauri_signing_sigv4/) | `signing` | `atomic-concrete` | `inferred` | 0 | single-capability package by default |
| [swarmauri_signing_ssh](40-standards/swarmauri_signing_ssh/) | `signing` | `atomic-concrete` | `inferred` | 0 | single-capability package by default |
| [swarmauri_signing_xmld](40-standards/swarmauri_signing_xmld/) | `signing` | `atomic-concrete` | `inferred` | 0 | single-capability package by default |
| [swarmauri_similarity_gzip](40-standards/swarmauri_similarity_gzip/) | `similarity` | `atomic-concrete` | `inferred` | 0 | single-capability package by default |
| [swarmauri_skill_dummy_filesystem](40-standards/swarmauri_skill_dummy_filesystem/) | `skill` | `atomic-concrete` | `inferred` | 0 | single-capability package by default |
| [swarmauri_skill_dummy_local](40-standards/swarmauri_skill_dummy_local/) | `skill` | `atomic-concrete` | `inferred` | 0 | single-capability package by default |
| [swarmauri_skill_filesystem](40-standards/swarmauri_skill_filesystem/) | `skill` | `atomic-concrete` | `inferred` | 0 | single-capability package by default |
| [swarmauri_skill_local](40-standards/swarmauri_skill_local/) | `skill` | `atomic-concrete` | `inferred` | 0 | single-capability package by default |
| [swarmauri_storage_file](40-standards/swarmauri_storage_file/) | `storage` | `atomic-concrete` | `inferred` | 0 | single-capability package by default |
| [swarmauri_storage_github](40-standards/swarmauri_storage_github/) | `storage` | `atomic-concrete` | `inferred` | 0 | single-capability package by default |
| [swarmauri_storage_github_release](40-standards/swarmauri_storage_github_release/) | `storage` | `atomic-concrete` | `inferred` | 0 | single-capability package by default |
| [swarmauri_storage_memory](40-standards/swarmauri_storage_memory/) | `storage` | `atomic-concrete` | `inferred` | 0 | single-capability package by default |
| [swarmauri_storage_minio](40-standards/swarmauri_storage_minio/) | `storage` | `atomic-concrete` | `inferred` | 0 | single-capability package by default |
| [swarmauri_storage_s3](40-standards/swarmauri_storage_s3/) | `storage` | `atomic-concrete` | `inferred` | 0 | single-capability package by default |
| [swarmauri_storage_s3_over_sftp](40-standards/swarmauri_storage_s3_over_sftp/) | `storage` | `atomic-concrete` | `inferred` | 0 | single-capability package by default |
| [swarmauri_storage_s3fs](40-standards/swarmauri_storage_s3fs/) | `storage` | `atomic-concrete` | `inferred` | 0 | single-capability package by default |
| [swarmauri_storage_webdav](40-standards/swarmauri_storage_webdav/) | `storage` | `atomic-concrete` | `inferred` | 0 | single-capability package by default |
| [swarmauri_taskmanager_default](40-standards/swarmauri_taskmanager_default/) | `taskmanager` | `atomic-concrete` | `inferred` | 0 | single-capability package by default |
| [swarmauri_taskstore_sqlite](40-standards/swarmauri_taskstore_sqlite/) | `taskstore` | `atomic-concrete` | `inferred` | 0 | single-capability package by default |
| [swarmauri_tokens_dpopboundjwt](40-standards/swarmauri_tokens_dpopboundjwt/) | `tokens` | `atomic-concrete` | `inferred` | 0 | single-capability package by default |
| [swarmauri_tokens_introspection](40-standards/swarmauri_tokens_introspection/) | `tokens` | `atomic-concrete` | `inferred` | 0 | single-capability package by default |
| [swarmauri_tokens_jwt](40-standards/swarmauri_tokens_jwt/) | `tokens` | `atomic-concrete` | `inferred` | 0 | single-capability package by default |
| [swarmauri_tokens_paseto_v4](40-standards/swarmauri_tokens_paseto_v4/) | `tokens` | `atomic-concrete` | `inferred` | 0 | single-capability package by default |
| [swarmauri_tokens_remoteoidc](40-standards/swarmauri_tokens_remoteoidc/) | `tokens` | `atomic-concrete` | `inferred` | 0 | single-capability package by default |
| [swarmauri_tokens_rotatingjwt](40-standards/swarmauri_tokens_rotatingjwt/) | `tokens` | `atomic-concrete` | `inferred` | 0 | single-capability package by default |
| [swarmauri_tokens_sshcert](40-standards/swarmauri_tokens_sshcert/) | `tokens` | `atomic-concrete` | `inferred` | 0 | single-capability package by default |
| [swarmauri_tokens_sshsig](40-standards/swarmauri_tokens_sshsig/) | `tokens` | `atomic-concrete` | `inferred` | 0 | single-capability package by default |
| [swarmauri_tokens_tlsboundjwt](40-standards/swarmauri_tokens_tlsboundjwt/) | `tokens` | `atomic-concrete` | `inferred` | 0 | single-capability package by default |
| [swarmauri_tool_activateskill](40-standards/swarmauri_tool_activateskill/) | `tool` | `atomic-concrete` | `inferred` | 0 | single-capability package by default |
| [swarmauri_tool_askuser](40-standards/swarmauri_tool_askuser/) | `tool` | `atomic-concrete` | `inferred` | 0 | single-capability package by default |
| [swarmauri_tool_cancelprocess](40-standards/swarmauri_tool_cancelprocess/) | `tool` | `atomic-concrete` | `inferred` | 0 | single-capability package by default |
| [swarmauri_tool_containerfeedchars](40-standards/swarmauri_tool_containerfeedchars/) | `tool` | `atomic-concrete` | `inferred` | 0 | single-capability package by default |
| [swarmauri_tool_containermakepr](40-standards/swarmauri_tool_containermakepr/) | `tool` | `atomic-concrete` | `inferred` | 0 | single-capability package by default |
| [swarmauri_tool_containernewsession](40-standards/swarmauri_tool_containernewsession/) | `tool` | `atomic-concrete` | `inferred` | 0 | single-capability package by default |
| [swarmauri_tool_githubloader](40-standards/swarmauri_tool_githubloader/) | `tool` | `atomic-concrete` | `inferred` | 0 | single-capability package by default |
| [swarmauri_tool_httploaded](40-standards/swarmauri_tool_httploaded/) | `tool` | `atomic-concrete` | `inferred` | 0 | single-capability package by default |
| [swarmauri_tool_inspectruntimetool](40-standards/swarmauri_tool_inspectruntimetool/) | `tool` | `atomic-concrete` | `inferred` | 0 | single-capability package by default |
| [swarmauri_tool_inspectskill](40-standards/swarmauri_tool_inspectskill/) | `tool` | `atomic-concrete` | `inferred` | 0 | single-capability package by default |
| [swarmauri_tool_listruntimetools](40-standards/swarmauri_tool_listruntimetools/) | `tool` | `atomic-concrete` | `inferred` | 0 | single-capability package by default |
| [swarmauri_tool_listskills](40-standards/swarmauri_tool_listskills/) | `tool` | `atomic-concrete` | `inferred` | 0 | single-capability package by default |
| [swarmauri_tool_matplotlib](40-standards/swarmauri_tool_matplotlib/) | `tool` | `atomic-concrete` | `inferred` | 0 | single-capability package by default |
| [swarmauri_tool_readprocessoutput](40-standards/swarmauri_tool_readprocessoutput/) | `tool` | `atomic-concrete` | `inferred` | 0 | single-capability package by default |
| [swarmauri_tool_readskillresource](40-standards/swarmauri_tool_readskillresource/) | `tool` | `atomic-concrete` | `inferred` | 0 | single-capability package by default |
| [swarmauri_tool_registerruntimetool](40-standards/swarmauri_tool_registerruntimetool/) | `tool` | `atomic-concrete` | `inferred` | 0 | single-capability package by default |
| [swarmauri_tool_replaceruntimetool](40-standards/swarmauri_tool_replaceruntimetool/) | `tool` | `atomic-concrete` | `inferred` | 0 | single-capability package by default |
| [swarmauri_tool_runbashscript](40-standards/swarmauri_tool_runbashscript/) | `tool` | `atomic-concrete` | `inferred` | 0 | single-capability package by default |
| [swarmauri_tool_runcommand](40-standards/swarmauri_tool_runcommand/) | `tool` | `atomic-concrete` | `inferred` | 0 | single-capability package by default |
| [swarmauri_tool_runpackagechecks](40-standards/swarmauri_tool_runpackagechecks/) | `tool` | `atomic-concrete` | `inferred` | 0 | single-capability package by default |
| [swarmauri_tool_skill_execution](40-standards/swarmauri_tool_skill_execution/) | `tool` | `atomic-concrete` | `inferred` | 0 | single-capability package by default |
| [swarmauri_tool_subprocess](40-standards/swarmauri_tool_subprocess/) | `tool` | `atomic-concrete` | `inferred` | 0 | single-capability package by default |
| [swarmauri_tool_unregisterruntimetool](40-standards/swarmauri_tool_unregisterruntimetool/) | `tool` | `atomic-concrete` | `inferred` | 0 | single-capability package by default |
| [swarmauri_tool_writestdin](40-standards/swarmauri_tool_writestdin/) | `tool` | `atomic-concrete` | `inferred` | 0 | single-capability package by default |
| [swarmauri_transport_asgi](40-standards/swarmauri_transport_asgi/) | `transport` | `atomic-concrete` | `inferred` | 0 | single-capability package by default |
| [swarmauri_transport_aws_eventstream](40-standards/swarmauri_transport_aws_eventstream/) | `transport` | `atomic-concrete` | `inferred` | 0 | single-capability package by default |
| [swarmauri_transport_h2mux](40-standards/swarmauri_transport_h2mux/) | `transport` | `atomic-concrete` | `inferred` | 0 | single-capability package by default |
| [swarmauri_transport_httpx](40-standards/swarmauri_transport_httpx/) | `transport` | `atomic-concrete` | `inferred` | 0 | single-capability package by default |
| [swarmauri_transport_meshsidecarhttp2](40-standards/swarmauri_transport_meshsidecarhttp2/) | `transport` | `atomic-concrete` | `inferred` | 0 | single-capability package by default |
| [swarmauri_transport_mtlsunicast](40-standards/swarmauri_transport_mtlsunicast/) | `transport` | `atomic-concrete` | `inferred` | 0 | single-capability package by default |
| [swarmauri_transport_quic](40-standards/swarmauri_transport_quic/) | `transport` | `atomic-concrete` | `inferred` | 0 | single-capability package by default |
| [swarmauri_transport_retry](40-standards/swarmauri_transport_retry/) | `transport` | `atomic-concrete` | `explicit` | 0 | concrete retry policy and execution for HTTP client contracts |
| [swarmauri_transport_sseoutbound](40-standards/swarmauri_transport_sseoutbound/) | `transport` | `atomic-concrete` | `inferred` | 0 | single-capability package by default |
| [swarmauri_transport_sshtunnel](40-standards/swarmauri_transport_sshtunnel/) | `transport` | `atomic-concrete` | `inferred` | 0 | single-capability package by default |
| [swarmauri_transport_stdio](40-standards/swarmauri_transport_stdio/) | `transport` | `atomic-concrete` | `inferred` | 0 | single-capability package by default |
| [swarmauri_transport_tcpunicast](40-standards/swarmauri_transport_tcpunicast/) | `transport` | `atomic-concrete` | `inferred` | 0 | single-capability package by default |
| [swarmauri_transport_tls_unicast](40-standards/swarmauri_transport_tls_unicast/) | `transport` | `atomic-concrete` | `inferred` | 0 | single-capability package by default |
| [swarmauri_transport_udp](40-standards/swarmauri_transport_udp/) | `transport` | `atomic-concrete` | `inferred` | 0 | single-capability package by default |
| [swarmauri_transport_uds_unicast](40-standards/swarmauri_transport_uds_unicast/) | `transport` | `atomic-concrete` | `inferred` | 0 | single-capability package by default |
| [swarmauri_transport_websocket](40-standards/swarmauri_transport_websocket/) | `transport` | `atomic-concrete` | `inferred` | 0 | single-capability package by default |
| [swarmauri_transport_wsjsonrpcmux](40-standards/swarmauri_transport_wsjsonrpcmux/) | `transport` | `atomic-concrete` | `inferred` | 0 | single-capability package by default |
| [swarmauri_tts_azure](40-standards/swarmauri_tts_azure/) | `tts` | `atomic-concrete` | `inferred` | 0 | single-capability package by default |
| [swarmauri_tts_cartesia](40-standards/swarmauri_tts_cartesia/) | `tts` | `atomic-concrete` | `inferred` | 0 | single-capability package by default |
| [swarmauri_tts_deepgram](40-standards/swarmauri_tts_deepgram/) | `tts` | `atomic-concrete` | `inferred` | 0 | single-capability package by default |
| [swarmauri_tts_deepinfra](40-standards/swarmauri_tts_deepinfra/) | `tts` | `atomic-concrete` | `inferred` | 0 | single-capability package by default |
| [swarmauri_tts_deepinfra_kokoro](40-standards/swarmauri_tts_deepinfra_kokoro/) | `tts` | `atomic-concrete` | `inferred` | 0 | single-capability package by default |
| [swarmauri_tts_deepinfra_qwen3](40-standards/swarmauri_tts_deepinfra_qwen3/) | `tts` | `atomic-concrete` | `inferred` | 0 | single-capability package by default |
| [swarmauri_tts_deepinfra_qwen3_voicedesign](40-standards/swarmauri_tts_deepinfra_qwen3_voicedesign/) | `tts` | `atomic-concrete` | `inferred` | 0 | single-capability package by default |
| [swarmauri_tts_elevenlabs](40-standards/swarmauri_tts_elevenlabs/) | `tts` | `atomic-concrete` | `inferred` | 0 | single-capability package by default |
| [swarmauri_tts_elevenlabs_dialogue](40-standards/swarmauri_tts_elevenlabs_dialogue/) | `tts` | `atomic-concrete` | `inferred` | 0 | single-capability package by default |
| [swarmauri_tts_gemini](40-standards/swarmauri_tts_gemini/) | `tts` | `atomic-concrete` | `inferred` | 0 | single-capability package by default |
| [swarmauri_tts_gemini_dialogue](40-standards/swarmauri_tts_gemini_dialogue/) | `tts` | `atomic-concrete` | `inferred` | 0 | single-capability package by default |
| [swarmauri_tts_openai](40-standards/swarmauri_tts_openai/) | `tts` | `atomic-concrete` | `inferred` | 0 | single-capability package by default |
| [swarmauri_tts_polly](40-standards/swarmauri_tts_polly/) | `tts` | `atomic-concrete` | `inferred` | 0 | single-capability package by default |
| [swarmauri_tts_together](40-standards/swarmauri_tts_together/) | `tts` | `atomic-concrete` | `inferred` | 0 | single-capability package by default |
| [swarmauri_xmp_gif](40-standards/swarmauri_xmp_gif/) | `xmp` | `atomic-concrete` | `inferred` | 0 | single-capability package by default |
| [swarmauri_xmp_jpeg](40-standards/swarmauri_xmp_jpeg/) | `xmp` | `atomic-concrete` | `inferred` | 0 | single-capability package by default |
| [swarmauri_xmp_mp4](40-standards/swarmauri_xmp_mp4/) | `xmp` | `atomic-concrete` | `inferred` | 0 | single-capability package by default |
| [swarmauri_xmp_pdf](40-standards/swarmauri_xmp_pdf/) | `xmp` | `atomic-concrete` | `inferred` | 0 | single-capability package by default |
| [swarmauri_xmp_png](40-standards/swarmauri_xmp_png/) | `xmp` | `atomic-concrete` | `inferred` | 0 | single-capability package by default |
| [swarmauri_xmp_svg](40-standards/swarmauri_xmp_svg/) | `xmp` | `atomic-concrete` | `inferred` | 0 | single-capability package by default |
| [swarmauri_xmp_tiff](40-standards/swarmauri_xmp_tiff/) | `xmp` | `atomic-concrete` | `inferred` | 0 | single-capability package by default |
| [swarmauri_xmp_webp](40-standards/swarmauri_xmp_webp/) | `xmp` | `atomic-concrete` | `inferred` | 0 | single-capability package by default |

### `40.1`

| Package | Family | Role | Source | Composes | Order reason |
|---|---|---|---|---:|---|
| [swarmauri_certs_composite](40-standards/swarmauri_certs_composite/) | `certs` | `composite-concrete` | `inferred` | 0 | composite signal from metadata for swarmauri_certs_composite |
| [swarmauri_certs_x509](40-standards/swarmauri_certs_x509/) | `certs` | `composite-concrete` | `inferred` | 2 | depends on 2 internal concrete packages |
| [swarmauri_crypto_composite](40-standards/swarmauri_crypto_composite/) | `crypto` | `composite-concrete` | `inferred` | 0 | composite signal from metadata for swarmauri_crypto_composite |
| [swarmauri_gitfilter_file](40-standards/swarmauri_gitfilter_file/) | `gitfilter` | `composite-concrete` | `inferred` | 1 | raised to order 1 because it depends on same-layer package swarmauri_storage_file at 40.0 |
| [swarmauri_keyprovider_hierarchical](40-standards/swarmauri_keyprovider_hierarchical/) | `keyprovider` | `composite-concrete` | `inferred` | 1 | raised to order 1 because it depends on same-layer package swarmauri_keyprovider_local at 40.0 |
| [swarmauri_keyprovider_remote_jwks](40-standards/swarmauri_keyprovider_remote_jwks/) | `keyprovider` | `composite-concrete` | `inferred` | 1 | raised to order 1 because it depends on same-layer package swarmauri_keyprovider_local at 40.0 |
| [swarmauri_keyproviders_mirrored](40-standards/swarmauri_keyproviders_mirrored/) | `keyproviders` | `composite-concrete` | `inferred` | 1 | raised to order 1 because it depends on same-layer package swarmauri_keyprovider_local at 40.0 |
| [swarmauri_signing_jws](40-standards/swarmauri_signing_jws/) | `signing` | `composite-concrete` | `inferred` | 4 | composite signal from metadata for swarmauri_signing_jws |
| [swarmauri_signing_pdf](40-standards/swarmauri_signing_pdf/) | `signing` | `composite-concrete` | `inferred` | 1 | raised to order 1 because it depends on same-layer package swarmauri_signing_cms at 40.0 |
| [swarmauri_tokens_composite](40-standards/swarmauri_tokens_composite/) | `tokens` | `composite-concrete` | `inferred` | 0 | composite signal from metadata for swarmauri_tokens_composite |
| [swarmauri_transport_h2](40-standards/swarmauri_transport_h2/) | `transport` | `composite-concrete` | `inferred` | 1 | raised to order 1 because it depends on same-layer package swarmauri_transport_h2mux at 40.0 |
| [swarmauri_vectorstore_doc2vec](40-standards/swarmauri_vectorstore_doc2vec/) | `vectorstore` | `composite-concrete` | `inferred` | 1 | raised to order 1 because it depends on same-layer package swarmauri_embedding_doc2vec at 40.0 |

### `40.2`

| Package | Family | Role | Source | Composes | Order reason |
|---|---|---|---|---:|---|
| [swarmauri_middleware_jwt](40-standards/swarmauri_middleware_jwt/) | `middleware` | `orchestrator` | `inferred` | 2 | raised to order 2 because it depends on same-layer package swarmauri_signing_jws at 40.1 |
| [swarmauri_signing_dpop](40-standards/swarmauri_signing_dpop/) | `signing` | `orchestrator` | `inferred` | 1 | raised to order 2 because it depends on same-layer package swarmauri_signing_jws at 40.1 |
| [swarmauri_toolkit_containertoolkit](40-standards/swarmauri_toolkit_containertoolkit/) | `toolkit` | `orchestrator` | `inferred` | 0 | orchestrator signal from metadata for swarmauri_toolkit_containertoolkit |
| [swarmauri_toolkit_runtime](40-standards/swarmauri_toolkit_runtime/) | `toolkit` | `orchestrator` | `inferred` | 0 | orchestrator signal from metadata for swarmauri_toolkit_runtime |
| [swarmauri_toolkit_skillset](40-standards/swarmauri_toolkit_skillset/) | `toolkit` | `orchestrator` | `inferred` | 0 | orchestrator signal from metadata for swarmauri_toolkit_skillset |
| [swarmauri_transport_https_unicast](40-standards/swarmauri_transport_https_unicast/) | `transport` | `orchestrator` | `inferred` | 4 | raised to order 2 because it depends on same-layer package swarmauri_signing_jws at 40.1 |
| [swarmauri_workflow_delegatedresearch](40-standards/swarmauri_workflow_delegatedresearch/) | `workflow` | `orchestrator` | `inferred` | 0 | orchestrator signal from metadata for swarmauri_workflow_delegatedresearch |
| [swarmauri_workflow_documentassistant](40-standards/swarmauri_workflow_documentassistant/) | `workflow` | `orchestrator` | `inferred` | 0 | orchestrator signal from metadata for swarmauri_workflow_documentassistant |

### `50.0`

| Package | Family | Role | Source | Composes | Order reason |
|---|---|---|---|---:|---|
| [swarmauri_billing_adyen](50-community/swarmauri_billing_adyen/) | `billing` | `atomic-concrete` | `inferred` | 0 | single-capability package by default |
| [swarmauri_billing_authorize_net](50-community/swarmauri_billing_authorize_net/) | `billing` | `atomic-concrete` | `inferred` | 0 | single-capability package by default |
| [swarmauri_billing_braintree](50-community/swarmauri_billing_braintree/) | `billing` | `atomic-concrete` | `inferred` | 0 | single-capability package by default |
| [swarmauri_billing_paypal](50-community/swarmauri_billing_paypal/) | `billing` | `atomic-concrete` | `inferred` | 0 | single-capability package by default |
| [swarmauri_billing_paystack](50-community/swarmauri_billing_paystack/) | `billing` | `atomic-concrete` | `inferred` | 0 | single-capability package by default |
| [swarmauri_billing_razorpay](50-community/swarmauri_billing_razorpay/) | `billing` | `atomic-concrete` | `inferred` | 0 | single-capability package by default |
| [swarmauri_billing_square](50-community/swarmauri_billing_square/) | `billing` | `atomic-concrete` | `inferred` | 0 | single-capability package by default |
| [swarmauri_certs_acme](50-community/swarmauri_certs_acme/) | `certs` | `atomic-concrete` | `inferred` | 0 | single-capability package by default |
| [swarmauri_certs_azure](50-community/swarmauri_certs_azure/) | `certs` | `atomic-concrete` | `inferred` | 0 | single-capability package by default |
| [swarmauri_certs_cfssl](50-community/swarmauri_certs_cfssl/) | `certs` | `atomic-concrete` | `inferred` | 0 | single-capability package by default |
| [swarmauri_certs_crlverifyservice](50-community/swarmauri_certs_crlverifyservice/) | `certs` | `atomic-concrete` | `inferred` | 0 | single-capability package by default |
| [swarmauri_certs_csronly](50-community/swarmauri_certs_csronly/) | `certs` | `atomic-concrete` | `inferred` | 0 | single-capability package by default |
| [swarmauri_certs_ocspverify](50-community/swarmauri_certs_ocspverify/) | `certs` | `atomic-concrete` | `inferred` | 0 | single-capability package by default |
| [swarmauri_certservice_aws_kms](50-community/swarmauri_certservice_aws_kms/) | `certservice` | `atomic-concrete` | `inferred` | 0 | single-capability package by default |
| [swarmauri_certservice_gcpkms](50-community/swarmauri_certservice_gcpkms/) | `certservice` | `atomic-concrete` | `inferred` | 0 | single-capability package by default |
| [swarmauri_certservice_ms_adcs](50-community/swarmauri_certservice_ms_adcs/) | `certservice` | `atomic-concrete` | `inferred` | 0 | single-capability package by default |
| [swarmauri_certservice_scep](50-community/swarmauri_certservice_scep/) | `certservice` | `atomic-concrete` | `inferred` | 0 | single-capability package by default |
| [swarmauri_certservice_stepca](50-community/swarmauri_certservice_stepca/) | `certservice` | `atomic-concrete` | `inferred` | 0 | single-capability package by default |
| [swarmauri_embedding_mlm](50-community/swarmauri_embedding_mlm/) | `embedding` | `atomic-concrete` | `inferred` | 0 | single-capability package by default |
| [swm_example_community_package](50-community/swm_example_community_package/) | `example` | `atomic-concrete` | `inferred` | 0 | single-capability package by default |
| [swarmauri_keyprovider_aws_kms](50-community/swarmauri_keyprovider_aws_kms/) | `keyprovider` | `atomic-concrete` | `inferred` | 0 | single-capability package by default |
| [swarmauri_keyprovider_gcpkms](50-community/swarmauri_keyprovider_gcpkms/) | `keyprovider` | `atomic-concrete` | `inferred` | 0 | single-capability package by default |
| [swarmauri_keyprovider_vaulttransit](50-community/swarmauri_keyprovider_vaulttransit/) | `keyprovider` | `atomic-concrete` | `inferred` | 0 | single-capability package by default |
| [swarmauri_live_model_amazon_nova](50-community/swarmauri_live_model_amazon_nova/) | `live` | `atomic-concrete` | `inferred` | 0 | single-capability package by default |
| [swarmauri_live_model_gemini](50-community/swarmauri_live_model_gemini/) | `live` | `atomic-concrete` | `inferred` | 0 | single-capability package by default |
| [swarmauri_live_model_openai](50-community/swarmauri_live_model_openai/) | `live` | `atomic-concrete` | `inferred` | 0 | single-capability package by default |
| [swarmauri_live_model_qwen](50-community/swarmauri_live_model_qwen/) | `live` | `atomic-concrete` | `inferred` | 0 | single-capability package by default |
| [swarmauri_live_model_xai](50-community/swarmauri_live_model_xai/) | `live` | `atomic-concrete` | `inferred` | 0 | single-capability package by default |
| [swarmauri_llm_ai21](50-community/swarmauri_llm_ai21/) | `llm` | `atomic-concrete` | `inferred` | 0 | single-capability package by default |
| [swarmauri_llm_anthropic](50-community/swarmauri_llm_anthropic/) | `llm` | `atomic-concrete` | `inferred` | 0 | single-capability package by default |
| [swarmauri_llm_azureopenai](50-community/swarmauri_llm_azureopenai/) | `llm` | `atomic-concrete` | `inferred` | 0 | single-capability package by default |
| [swarmauri_llm_cerebras](50-community/swarmauri_llm_cerebras/) | `llm` | `atomic-concrete` | `inferred` | 0 | single-capability package by default |
| [swarmauri_llm_cloudflare](50-community/swarmauri_llm_cloudflare/) | `llm` | `atomic-concrete` | `inferred` | 0 | single-capability package by default |
| [swarmauri_llm_cohere](50-community/swarmauri_llm_cohere/) | `llm` | `atomic-concrete` | `inferred` | 0 | single-capability package by default |
| [swarmauri_llm_deepinfra](50-community/swarmauri_llm_deepinfra/) | `llm` | `atomic-concrete` | `inferred` | 0 | single-capability package by default |
| [swarmauri_llm_deepseek](50-community/swarmauri_llm_deepseek/) | `llm` | `atomic-concrete` | `inferred` | 0 | single-capability package by default |
| [swarmauri_llm_falai](50-community/swarmauri_llm_falai/) | `llm` | `atomic-concrete` | `inferred` | 0 | single-capability package by default |
| [swarmauri_llm_gemini](50-community/swarmauri_llm_gemini/) | `llm` | `atomic-concrete` | `inferred` | 0 | single-capability package by default |
| [swarmauri_llm_groq](50-community/swarmauri_llm_groq/) | `llm` | `atomic-concrete` | `inferred` | 0 | single-capability package by default |
| [swarmauri_llm_hyperbolic](50-community/swarmauri_llm_hyperbolic/) | `llm` | `atomic-concrete` | `inferred` | 0 | single-capability package by default |
| [swarmauri_llm_leptonai](50-community/swarmauri_llm_leptonai/) | `llm` | `atomic-concrete` | `inferred` | 0 | single-capability package by default |
| [swarmauri_llm_llamacpp](50-community/swarmauri_llm_llamacpp/) | `llm` | `atomic-concrete` | `inferred` | 0 | single-capability package by default |
| [swarmauri_llm_mistral](50-community/swarmauri_llm_mistral/) | `llm` | `atomic-concrete` | `inferred` | 0 | single-capability package by default |
| [swarmauri_llm_nvidia_nim](50-community/swarmauri_llm_nvidia_nim/) | `llm` | `atomic-concrete` | `inferred` | 0 | single-capability package by default |
| [swarmauri_llm_openai](50-community/swarmauri_llm_openai/) | `llm` | `atomic-concrete` | `inferred` | 0 | single-capability package by default |
| [swarmauri_llm_perplexity](50-community/swarmauri_llm_perplexity/) | `llm` | `atomic-concrete` | `inferred` | 0 | single-capability package by default |
| [swarmauri_llm_whisper](50-community/swarmauri_llm_whisper/) | `llm` | `atomic-concrete` | `inferred` | 0 | single-capability package by default |
| [swarmauri_llm_xai](50-community/swarmauri_llm_xai/) | `llm` | `atomic-concrete` | `inferred` | 0 | single-capability package by default |
| [swarmauri_measurement_mutualinformation](50-community/swarmauri_measurement_mutualinformation/) | `measurement` | `atomic-concrete` | `inferred` | 0 | single-capability package by default |
| [swarmauri_measurement_tokencountestimator](50-community/swarmauri_measurement_tokencountestimator/) | `measurement` | `atomic-concrete` | `inferred` | 0 | single-capability package by default |
| [swarmauri_metric_hamming](50-community/swarmauri_metric_hamming/) | `metric` | `atomic-concrete` | `inferred` | 0 | single-capability package by default |
| [swarmauri_middleware_circuitbreaker](50-community/swarmauri_middleware_circuitbreaker/) | `middleware` | `atomic-concrete` | `inferred` | 0 | single-capability package by default |
| [swarmauri_middleware_ratepolicy](50-community/swarmauri_middleware_ratepolicy/) | `middleware` | `atomic-concrete` | `inferred` | 0 | single-capability package by default |
| [swarmauri_ocr_pytesseract](50-community/swarmauri_ocr_pytesseract/) | `ocr` | `atomic-concrete` | `inferred` | 0 | single-capability package by default |
| [swarmauri_parser_bertembedding](50-community/swarmauri_parser_bertembedding/) | `parser` | `atomic-concrete` | `inferred` | 0 | single-capability package by default |
| [swarmauri_parser_entityrecognition](50-community/swarmauri_parser_entityrecognition/) | `parser` | `atomic-concrete` | `inferred` | 0 | single-capability package by default |
| [swarmauri_parser_fitzpdf](50-community/swarmauri_parser_fitzpdf/) | `parser` | `atomic-concrete` | `inferred` | 0 | single-capability package by default |
| [swarmauri_parser_pypdf2](50-community/swarmauri_parser_pypdf2/) | `parser` | `atomic-concrete` | `inferred` | 0 | single-capability package by default |
| [swarmauri_parser_pypdftk](50-community/swarmauri_parser_pypdftk/) | `parser` | `atomic-concrete` | `inferred` | 0 | single-capability package by default |
| [swarmauri_parser_slate](50-community/swarmauri_parser_slate/) | `parser` | `atomic-concrete` | `inferred` | 0 | single-capability package by default |
| [swarmauri_parser_textblob](50-community/swarmauri_parser_textblob/) | `parser` | `atomic-concrete` | `inferred` | 0 | single-capability package by default |
| [swarmauri_provider_amazon_nova](50-community/swarmauri_provider_amazon_nova/) | `provider` | `atomic-concrete` | `inferred` | 0 | single-capability package by default |
| [swarmauri_provider_gemini](50-community/swarmauri_provider_gemini/) | `provider` | `atomic-concrete` | `inferred` | 0 | single-capability package by default |
| [swarmauri_provider_openai](50-community/swarmauri_provider_openai/) | `provider` | `atomic-concrete` | `inferred` | 0 | single-capability package by default |
| [swarmauri_provider_openrouter](50-community/swarmauri_provider_openrouter/) | `provider` | `atomic-concrete` | `explicit` | 0 | provider configuration without transport execution |
| [swarmauri_provider_qwen](50-community/swarmauri_provider_qwen/) | `provider` | `atomic-concrete` | `inferred` | 0 | single-capability package by default |
| [swarmauri_provider_xai](50-community/swarmauri_provider_xai/) | `provider` | `atomic-concrete` | `inferred` | 0 | single-capability package by default |
| [swarmauri_signing_dsse](50-community/swarmauri_signing_dsse/) | `signing` | `atomic-concrete` | `inferred` | 0 | single-capability package by default |
| [swarmauri_state_clipboard](50-community/swarmauri_state_clipboard/) | `state` | `atomic-concrete` | `inferred` | 0 | single-capability package by default |
| [swarmauri_tests_griffe](50-community/swarmauri_tests_griffe/) | `tests` | `atomic-concrete` | `inferred` | 0 | single-capability package by default |
| [swarmauri_tool_addcontenttorag](50-community/swarmauri_tool_addcontenttorag/) | `tool` | `atomic-concrete` | `inferred` | 0 | single-capability package by default |
| [swarmauri_tool_captchagenerator](50-community/swarmauri_tool_captchagenerator/) | `tool` | `atomic-concrete` | `inferred` | 0 | single-capability package by default |
| [swarmauri_tool_createfile](50-community/swarmauri_tool_createfile/) | `tool` | `atomic-concrete` | `inferred` | 0 | single-capability package by default |
| [swarmauri_tool_dalechallreadability](50-community/swarmauri_tool_dalechallreadability/) | `tool` | `atomic-concrete` | `inferred` | 0 | single-capability package by default |
| [swarmauri_tool_downloadpdf](50-community/swarmauri_tool_downloadpdf/) | `tool` | `atomic-concrete` | `inferred` | 0 | single-capability package by default |
| [swarmauri_tool_entityrecognition](50-community/swarmauri_tool_entityrecognition/) | `tool` | `atomic-concrete` | `inferred` | 0 | single-capability package by default |
| [swarmauri_tool_findfile](50-community/swarmauri_tool_findfile/) | `tool` | `atomic-concrete` | `inferred` | 0 | single-capability package by default |
| [swarmauri_tool_folium](50-community/swarmauri_tool_folium/) | `tool` | `atomic-concrete` | `inferred` | 0 | single-capability package by default |
| [swarmauri_tool_getmethodsignature](50-community/swarmauri_tool_getmethodsignature/) | `tool` | `atomic-concrete` | `inferred` | 0 | single-capability package by default |
| [swarmauri_tool_gmail](50-community/swarmauri_tool_gmail/) | `tool` | `atomic-concrete` | `inferred` | 0 | single-capability package by default |
| [swarmauri_tool_jupyterclearoutput](50-community/swarmauri_tool_jupyterclearoutput/) | `tool` | `atomic-concrete` | `inferred` | 0 | single-capability package by default |
| [swarmauri_tool_jupyterdisplay](50-community/swarmauri_tool_jupyterdisplay/) | `tool` | `atomic-concrete` | `inferred` | 0 | single-capability package by default |
| [swarmauri_tool_jupyterdisplayhtml](50-community/swarmauri_tool_jupyterdisplayhtml/) | `tool` | `atomic-concrete` | `inferred` | 0 | single-capability package by default |
| [swarmauri_tool_jupyterexecuteandconvert](50-community/swarmauri_tool_jupyterexecuteandconvert/) | `tool` | `atomic-concrete` | `inferred` | 0 | single-capability package by default |
| [swarmauri_tool_jupyterexecutecell](50-community/swarmauri_tool_jupyterexecutecell/) | `tool` | `atomic-concrete` | `inferred` | 0 | single-capability package by default |
| [swarmauri_tool_jupyterexecutenotebook](50-community/swarmauri_tool_jupyterexecutenotebook/) | `tool` | `atomic-concrete` | `inferred` | 0 | single-capability package by default |
| [swarmauri_tool_jupyterexecutenotebookwithparameters](50-community/swarmauri_tool_jupyterexecutenotebookwithparameters/) | `tool` | `atomic-concrete` | `inferred` | 0 | single-capability package by default |
| [swarmauri_tool_jupyterexporthtml](50-community/swarmauri_tool_jupyterexporthtml/) | `tool` | `atomic-concrete` | `inferred` | 0 | single-capability package by default |
| [swarmauri_tool_jupyterexportlatex](50-community/swarmauri_tool_jupyterexportlatex/) | `tool` | `atomic-concrete` | `inferred` | 0 | single-capability package by default |
| [swarmauri_tool_jupyterexportmarkdown](50-community/swarmauri_tool_jupyterexportmarkdown/) | `tool` | `atomic-concrete` | `inferred` | 0 | single-capability package by default |
| [swarmauri_tool_jupyterexportpython](50-community/swarmauri_tool_jupyterexportpython/) | `tool` | `atomic-concrete` | `inferred` | 0 | single-capability package by default |
| [swarmauri_tool_jupyterfromdict](50-community/swarmauri_tool_jupyterfromdict/) | `tool` | `atomic-concrete` | `inferred` | 0 | single-capability package by default |
| [swarmauri_tool_jupytergetiopubmessage](50-community/swarmauri_tool_jupytergetiopubmessage/) | `tool` | `atomic-concrete` | `inferred` | 0 | single-capability package by default |
| [swarmauri_tool_jupytergetshellmessage](50-community/swarmauri_tool_jupytergetshellmessage/) | `tool` | `atomic-concrete` | `inferred` | 0 | single-capability package by default |
| [swarmauri_tool_jupyterreadnotebook](50-community/swarmauri_tool_jupyterreadnotebook/) | `tool` | `atomic-concrete` | `inferred` | 0 | single-capability package by default |
| [swarmauri_tool_jupyterruncell](50-community/swarmauri_tool_jupyterruncell/) | `tool` | `atomic-concrete` | `inferred` | 0 | single-capability package by default |
| [swarmauri_tool_jupytershutdownkernel](50-community/swarmauri_tool_jupytershutdownkernel/) | `tool` | `atomic-concrete` | `inferred` | 0 | single-capability package by default |
| [swarmauri_tool_jupyterstartkernel](50-community/swarmauri_tool_jupyterstartkernel/) | `tool` | `atomic-concrete` | `inferred` | 0 | single-capability package by default |
| [swarmauri_tool_jupytervalidatenotebook](50-community/swarmauri_tool_jupytervalidatenotebook/) | `tool` | `atomic-concrete` | `inferred` | 0 | single-capability package by default |
| [swarmauri_tool_jupyterwritenotebook](50-community/swarmauri_tool_jupyterwritenotebook/) | `tool` | `atomic-concrete` | `inferred` | 0 | single-capability package by default |
| [swarmauri_tool_lexicaldensity](50-community/swarmauri_tool_lexicaldensity/) | `tool` | `atomic-concrete` | `inferred` | 0 | single-capability package by default |
| [swarmauri_tool_listfiles](50-community/swarmauri_tool_listfiles/) | `tool` | `atomic-concrete` | `inferred` | 0 | single-capability package by default |
| [swarmauri_tool_psutil](50-community/swarmauri_tool_psutil/) | `tool` | `atomic-concrete` | `inferred` | 0 | single-capability package by default |
| [swarmauri_tool_qrcodegenerator](50-community/swarmauri_tool_qrcodegenerator/) | `tool` | `atomic-concrete` | `inferred` | 0 | single-capability package by default |
| [swarmauri_tool_queryimagevectorstore](50-community/swarmauri_tool_queryimagevectorstore/) | `tool` | `atomic-concrete` | `inferred` | 0 | single-capability package by default |
| [swarmauri_tool_queryknowledgebase](50-community/swarmauri_tool_queryknowledgebase/) | `tool` | `atomic-concrete` | `inferred` | 0 | single-capability package by default |
| [swarmauri_tool_scrollfile](50-community/swarmauri_tool_scrollfile/) | `tool` | `atomic-concrete` | `inferred` | 0 | single-capability package by default |
| [swarmauri_tool_searchword](50-community/swarmauri_tool_searchword/) | `tool` | `atomic-concrete` | `inferred` | 0 | single-capability package by default |
| [swarmauri_tool_sentencecomplexity](50-community/swarmauri_tool_sentencecomplexity/) | `tool` | `atomic-concrete` | `inferred` | 0 | single-capability package by default |
| [swarmauri_tool_sentimentanalysis](50-community/swarmauri_tool_sentimentanalysis/) | `tool` | `atomic-concrete` | `inferred` | 0 | single-capability package by default |
| [swarmauri_tool_smogindex](50-community/swarmauri_tool_smogindex/) | `tool` | `atomic-concrete` | `inferred` | 0 | single-capability package by default |
| [swarmauri_tool_textlength](50-community/swarmauri_tool_textlength/) | `tool` | `atomic-concrete` | `inferred` | 0 | single-capability package by default |
| [swarmauri_tool_webscraping](50-community/swarmauri_tool_webscraping/) | `tool` | `atomic-concrete` | `inferred` | 0 | single-capability package by default |
| [swarmauri_tool_zapierhook](50-community/swarmauri_tool_zapierhook/) | `tool` | `atomic-concrete` | `inferred` | 0 | single-capability package by default |
| [swarmauri_vectorstore_annoy](50-community/swarmauri_vectorstore_annoy/) | `vectorstore` | `atomic-concrete` | `inferred` | 1 | single-capability package by default |
| [swarmauri_vectorstore_cloudweaviate](50-community/swarmauri_vectorstore_cloudweaviate/) | `vectorstore` | `atomic-concrete` | `inferred` | 1 | single-capability package by default |
| [swarmauri_vectorstore_duckdb](50-community/swarmauri_vectorstore_duckdb/) | `vectorstore` | `atomic-concrete` | `inferred` | 1 | single-capability package by default |
| [swarmauri_vectorstore_fs](50-community/swarmauri_vectorstore_fs/) | `vectorstore` | `atomic-concrete` | `inferred` | 0 | single-capability package by default |
| [swarmauri_vectorstore_git](50-community/swarmauri_vectorstore_git/) | `vectorstore` | `atomic-concrete` | `inferred` | 0 | single-capability package by default |
| [swarmauri_vectorstore_neo4j](50-community/swarmauri_vectorstore_neo4j/) | `vectorstore` | `atomic-concrete` | `inferred` | 0 | single-capability package by default |
| [swarmauri_vectorstore_persistentchromadb](50-community/swarmauri_vectorstore_persistentchromadb/) | `vectorstore` | `atomic-concrete` | `inferred` | 1 | single-capability package by default |
| [swarmauri_vectorstore_pinecone](50-community/swarmauri_vectorstore_pinecone/) | `vectorstore` | `atomic-concrete` | `inferred` | 1 | single-capability package by default |
| [swarmauri_vectorstore_qdrant](50-community/swarmauri_vectorstore_qdrant/) | `vectorstore` | `atomic-concrete` | `inferred` | 1 | single-capability package by default |
| [swarmauri_vectorstore_redis](50-community/swarmauri_vectorstore_redis/) | `vectorstore` | `atomic-concrete` | `inferred` | 1 | single-capability package by default |
| [swarmauri_video_lipsync_synclabs](50-community/swarmauri_video_lipsync_synclabs/) | `video` | `atomic-concrete` | `inferred` | 0 | single-capability package by default |

### `50.1`

| Package | Family | Role | Source | Composes | Order reason |
|---|---|---|---|---:|---|
| [swarmauri_llm_openrouter](50-community/swarmauri_llm_openrouter/) | `llm` | `composite-concrete` | `explicit` | 3 | OpenRouter models compose provider configuration with shared HTTP and retry transports |
| [swarmauri_matrix_hamming74](50-community/swarmauri_matrix_hamming74/) | `matrix` | `composite-concrete` | `inferred` | 1 | raised to order 1 because it depends on same-layer package swarmauri_metric_hamming at 50.0 |
| [swarmauri_vectorstore_mlm](50-community/swarmauri_vectorstore_mlm/) | `vectorstore` | `composite-concrete` | `inferred` | 1 | raised to order 1 because it depends on same-layer package swarmauri_embedding_mlm at 50.0 |

### `50.2`

| Package | Family | Role | Source | Composes | Order reason |
|---|---|---|---|---:|---|
| [swarmauri_toolkit_github](50-community/swarmauri_toolkit_github/) | `toolkit` | `orchestrator` | `inferred` | 0 | orchestrator signal from metadata for swarmauri_toolkit_github |
| [swarmauri_toolkit_jupytertoolkit](50-community/swarmauri_toolkit_jupytertoolkit/) | `toolkit` | `orchestrator` | `inferred` | 20 | orchestrator signal from metadata for swarmauri_toolkit_jupytertoolkit |

### `60.0`

| Package | Family | Role | Source | Composes | Order reason |
|---|---|---|---|---:|---|
| [EmbedXMP](60-plugins/EmbedXMP/) | `embedxmp` | `plugin` | `inferred` | 1 | single-capability package by default |
| [swm_example_plugin](60-plugins/example_plugin/) | `example` | `plugin` | `inferred` | 0 | single-capability package by default |
| [zdx](60-plugins/zdx/) | `zdx` | `plugin` | `inferred` | 0 | single-capability package by default |

### `60.1`

| Package | Family | Role | Source | Composes | Order reason |
|---|---|---|---|---:|---|
| [MediaSigner](60-plugins/media_signer/) | `mediasigner` | `plugin-composite` | `inferred` | 6 | depends on 6 internal concrete packages |

### `60.2`

| Package | Family | Role | Source | Composes | Order reason |
|---|---|---|---|---:|---|
| [EmbeddedSigner](60-plugins/embedded_signer/) | `embeddedsigner` | `plugin-orchestrator` | `inferred` | 2 | raised to order 2 because it depends on same-layer package MediaSigner at 60.1 |

### `70.0`

| Package | Family | Role | Source | Composes | Order reason |
|---|---|---|---|---:|---|
| [6w](70-experimental/6w/) | `6w` | `experimental-atomic` | `inferred` | 0 | single-capability package by default |
| [6x](70-experimental/6x/) | `6x` | `experimental-atomic` | `inferred` | 0 | single-capability package by default |
| [6y](70-experimental/6y/) | `6y` | `experimental-atomic` | `inferred` | 0 | single-capability package by default |
| [6z](70-experimental/6z/) | `6z` | `experimental-atomic` | `inferred` | 0 | single-capability package by default |
| [77](70-experimental/77/) | `77` | `experimental-atomic` | `inferred` | 0 | single-capability package by default |
| [9x](70-experimental/9x/) | `9x` | `experimental-atomic` | `inferred` | 0 | single-capability package by default |
| [swarmauri_canon_http](70-experimental/swarmauri_canon_http/) | `canon` | `experimental-atomic` | `inferred` | 0 | single-capability package by default |
| [catoml](70-experimental/catoml/) | `catoml` | `experimental-atomic` | `inferred` | 0 | single-capability package by default |
| [cayaml](70-experimental/cayaml/) | `cayaml` | `experimental-atomic` | `inferred` | 0 | single-capability package by default |
| [swarmauri_certs_pkcs11](70-experimental/swarmauri_certs_pkcs11/) | `certs` | `experimental-atomic` | `inferred` | 0 | single-capability package by default |
| [swarmauri_crypto_sodium](70-experimental/swarmauri_crypto_sodium/) | `crypto` | `experimental-atomic` | `inferred` | 0 | single-capability package by default |
| [DistanceMetrics](70-experimental/RapidSimilarity/DistanceMetrics/) | `distancemetrics` | `experimental-atomic` | `inferred` | 0 | single-capability package by default |
| [do](70-experimental/do/) | `do` | `experimental-atomic` | `inferred` | 0 | single-capability package by default |
| [FastTokenizer](70-experimental/FastTokenizer/) | `fasttokenizer` | `experimental-atomic` | `inferred` | 0 | single-capability package by default |
| [g9](70-experimental/g9/) | `g9` | `experimental-atomic` | `inferred` | 0 | single-capability package by default |
| [gk](70-experimental/gk/) | `gk` | `experimental-atomic` | `inferred` | 0 | single-capability package by default |
| [IndexBuilder](70-experimental/RapidSimilarity/IndexBuilder/) | `indexbuilder` | `experimental-atomic` | `inferred` | 0 | single-capability package by default |
| [jaml](70-experimental/jaml/) | `jaml` | `experimental-atomic` | `inferred` | 0 | single-capability package by default |
| [jz](70-experimental/jz/) | `jz` | `experimental-atomic` | `inferred` | 0 | single-capability package by default |
| [swarmauri_keyprovider_pkcs11](70-experimental/swarmauri_keyprovider_pkcs11/) | `keyprovider` | `experimental-atomic` | `inferred` | 0 | single-capability package by default |
| [layout_engine](70-experimental/layout_engine/) | `layout` | `experimental-atomic` | `inferred` | 0 | single-capability package by default |
| [monotone-ops](70-experimental/monotone_ops/) | `monotone` | `experimental-atomic` | `inferred` | 0 | single-capability package by default |
| [mto](70-experimental/mto/) | `mto` | `experimental-atomic` | `inferred` | 0 | single-capability package by default |
| [swarmauri_parser_asn1](70-experimental/swarmauri_parser_asn1/) | `parser` | `experimental-atomic` | `inferred` | 0 | single-capability package by default |
| [pj](70-experimental/pj/) | `pj` | `experimental-atomic` | `inferred` | 0 | single-capability package by default |
| [ptree_dag_extension_example](70-experimental/ptree_dag_extension_example/) | `ptree` | `experimental-atomic` | `inferred` | 0 | single-capability package by default |
| [QueryEngine](70-experimental/RapidSimilarity/QueryEngine/) | `queryengine` | `experimental-atomic` | `inferred` | 0 | single-capability package by default |
| [s.f](70-experimental/s_f/) | `s.f` | `experimental-atomic` | `inferred` | 0 | single-capability package by default |
| [sfw](70-experimental/sfw/) | `sfw` | `experimental-atomic` | `inferred` | 0 | single-capability package by default |
| [snt](70-experimental/snt/) | `snt` | `experimental-atomic` | `inferred` | 0 | single-capability package by default |
| [swarmauri_tests_component](70-experimental/swarmauri_tests_component/) | `tests` | `experimental-atomic` | `inferred` | 0 | single-capability package by default |
| [swarmauri_tests_loc_tersity](70-experimental/swarmauri_tests_loc_tersity/) | `tests` | `experimental-atomic` | `inferred` | 0 | single-capability package by default |
| [swarmauri_tests_pylicense](70-experimental/swarmauri_tests_pylicense/) | `tests` | `experimental-atomic` | `inferred` | 0 | single-capability package by default |
| [swarmauri_tests_readme_examples](70-experimental/swarmauri_tests_readme_examples/) | `tests` | `experimental-atomic` | `inferred` | 0 | single-capability package by default |
| [tigr](70-experimental/tigr/) | `tigr` | `experimental-atomic` | `inferred` | 0 | single-capability package by default |
| [uu](70-experimental/uu/) | `uu` | `experimental-atomic` | `inferred` | 0 | single-capability package by default |
| [vb](70-experimental/vb/) | `vb` | `experimental-atomic` | `inferred` | 0 | single-capability package by default |
| [xj](70-experimental/xj/) | `xj` | `experimental-atomic` | `inferred` | 0 | single-capability package by default |
| [xk](70-experimental/xk/) | `xk` | `experimental-atomic` | `inferred` | 0 | single-capability package by default |
| [xz](70-experimental/xz/) | `xz` | `experimental-atomic` | `inferred` | 0 | single-capability package by default |
| [ye](70-experimental/ye/) | `ye` | `experimental-atomic` | `inferred` | 0 | single-capability package by default |
| [ymls](70-experimental/ymls/) | `ymls` | `experimental-atomic` | `inferred` | 0 | single-capability package by default |
| [zr0](70-experimental/zr0/) | `zr0` | `experimental-atomic` | `inferred` | 0 | single-capability package by default |

### `70.1`

| Package | Family | Role | Source | Composes | Order reason |
|---|---|---|---|---:|---|
| [layout_engine_atoms](70-experimental/layout_engine_atoms/) | `layout` | `experimental-composite` | `inferred` | 1 | raised to order 1 because it depends on same-layer package layout_engine at 70.0 |

### `70.2`

| Package | Family | Role | Source | Composes | Order reason |
|---|---|---|---|---:|---|
| [swarmauri_workflow_statedriven](70-experimental/swarmauri_workflow_statedriven/) | `workflow` | `experimental-orchestrator` | `inferred` | 0 | orchestrator signal from metadata for swarmauri_workflow_statedriven |

### `80.3`

| Package | Family | Role | Source | Composes | Order reason |
|---|---|---|---|---:|---|
| [swarmauri](80-facades/swarmauri/) | `facade` | `facade` | `inferred` | 0 | facade layer packages are aggregate surfaces |

### `90.0`

| Package | Family | Role | Source | Composes | Order reason |
|---|---|---|---|---:|---|
| [swarmauri_documentstore_redis](90-deprecated/swarmauri_documentstore_redis/) | `documentstore` | `compat` | `inferred` | 0 | single-capability package by default |
| [swarmauri_embedding_tfidf](90-deprecated/swarmauri_embedding_tfidf/) | `embedding` | `compat` | `inferred` | 0 | single-capability package by default |
| [swarmauri_experimental](90-deprecated/swarmauri_experimental/) | `experimental` | `compat` | `inferred` | 0 | single-capability package by default |
| [swarmauri_llm_playht](90-deprecated/swarmauri_llm_playht/) | `llm` | `compat` | `inferred` | 0 | single-capability package by default |
| [swarmauri_tts_playht](90-deprecated/swarmauri_tts_playht/) | `tts` | `compat` | `inferred` | 0 | single-capability package by default |

### `90.1`

| Package | Family | Role | Source | Composes | Order reason |
|---|---|---|---|---:|---|
| [swarmauri_vectorstore_tfidf](90-deprecated/swarmauri_vectorstore_tfidf/) | `vectorstore` | `compat-composite` | `inferred` | 1 | raised to order 1 because it depends on same-layer package swarmauri_embedding_tfidf at 90.0 |

## By Domain Family

### `6w`

| Index | Package | Layer | Path | Role | Maturity | Workspace |
|---|---|---|---|---|---|---|
| `70.0` | [6w](70-experimental/6w/) | `70-experimental` | `70-experimental/6w` | `experimental-atomic` | `experimental` | no |

### `6x`

| Index | Package | Layer | Path | Role | Maturity | Workspace |
|---|---|---|---|---|---|---|
| `70.0` | [6x](70-experimental/6x/) | `70-experimental` | `70-experimental/6x` | `experimental-atomic` | `experimental` | no |

### `6y`

| Index | Package | Layer | Path | Role | Maturity | Workspace |
|---|---|---|---|---|---|---|
| `70.0` | [6y](70-experimental/6y/) | `70-experimental` | `70-experimental/6y` | `experimental-atomic` | `experimental` | no |

### `6z`

| Index | Package | Layer | Path | Role | Maturity | Workspace |
|---|---|---|---|---|---|---|
| `70.0` | [6z](70-experimental/6z/) | `70-experimental` | `70-experimental/6z` | `experimental-atomic` | `experimental` | no |

### `77`

| Index | Package | Layer | Path | Role | Maturity | Workspace |
|---|---|---|---|---|---|---|
| `70.0` | [77](70-experimental/77/) | `70-experimental` | `70-experimental/77` | `experimental-atomic` | `experimental` | no |

### `9x`

| Index | Package | Layer | Path | Role | Maturity | Workspace |
|---|---|---|---|---|---|---|
| `70.0` | [9x](70-experimental/9x/) | `70-experimental` | `70-experimental/9x` | `experimental-atomic` | `experimental` | no |

### `agent`

| Index | Package | Layer | Path | Role | Maturity | Workspace |
|---|---|---|---|---|---|---|
| `40.0` | [swarmauri_agent_compacting](40-standards/swarmauri_agent_compacting/) | `40-standards` | `40-standards/swarmauri_agent_compacting` | `atomic-concrete` | `standard` | yes |
| `40.0` | [swarmauri_agent_package_maintenance](40-standards/swarmauri_agent_package_maintenance/) | `40-standards` | `40-standards/swarmauri_agent_package_maintenance` | `atomic-concrete` | `standard` | yes |
| `40.0` | [swarmauri_agent_realtime](40-standards/swarmauri_agent_realtime/) | `40-standards` | `40-standards/swarmauri_agent_realtime` | `atomic-concrete` | `standard` | yes |
| `40.0` | [swarmauri_agent_runner](40-standards/swarmauri_agent_runner/) | `40-standards` | `40-standards/swarmauri_agent_runner` | `atomic-concrete` | `standard` | yes |
| `40.0` | [swarmauri_agent_skill](40-standards/swarmauri_agent_skill/) | `40-standards` | `40-standards/swarmauri_agent_skill` | `atomic-concrete` | `standard` | yes |
| `40.0` | [swarmauri_agent_texttospeech](40-standards/swarmauri_agent_texttospeech/) | `40-standards` | `40-standards/swarmauri_agent_texttospeech` | `atomic-concrete` | `standard` | yes |
| `40.0` | [swarmauri_agent_wimse](40-standards/swarmauri_agent_wimse/) | `40-standards` | `40-standards/swarmauri_agent_wimse` | `atomic-concrete` | `standard` | yes |

### `auth_idp`

| Index | Package | Layer | Path | Role | Maturity | Workspace |
|---|---|---|---|---|---|---|
| `40.0` | [swarmauri_auth_idp_apple](40-standards/swarmauri_auth_idp_apple/) | `40-standards` | `40-standards/swarmauri_auth_idp_apple` | `atomic-concrete` | `standard` | yes |
| `40.0` | [swarmauri_auth_idp_aws](40-standards/swarmauri_auth_idp_aws/) | `40-standards` | `40-standards/swarmauri_auth_idp_aws` | `atomic-concrete` | `standard` | yes |
| `40.0` | [swarmauri_auth_idp_azure](40-standards/swarmauri_auth_idp_azure/) | `40-standards` | `40-standards/swarmauri_auth_idp_azure` | `atomic-concrete` | `standard` | yes |
| `40.0` | [swarmauri_auth_idp_cognito](40-standards/swarmauri_auth_idp_cognito/) | `40-standards` | `40-standards/swarmauri_auth_idp_cognito` | `atomic-concrete` | `standard` | yes |
| `40.0` | [swarmauri_auth_idp_facebook](40-standards/swarmauri_auth_idp_facebook/) | `40-standards` | `40-standards/swarmauri_auth_idp_facebook` | `atomic-concrete` | `standard` | yes |
| `40.0` | [swarmauri_auth_idp_gitea](40-standards/swarmauri_auth_idp_gitea/) | `40-standards` | `40-standards/swarmauri_auth_idp_gitea` | `atomic-concrete` | `standard` | yes |
| `40.0` | [swarmauri_auth_idp_github](40-standards/swarmauri_auth_idp_github/) | `40-standards` | `40-standards/swarmauri_auth_idp_github` | `atomic-concrete` | `standard` | yes |
| `40.0` | [swarmauri_auth_idp_gitlab](40-standards/swarmauri_auth_idp_gitlab/) | `40-standards` | `40-standards/swarmauri_auth_idp_gitlab` | `atomic-concrete` | `standard` | yes |
| `40.0` | [swarmauri_auth_idp_google](40-standards/swarmauri_auth_idp_google/) | `40-standards` | `40-standards/swarmauri_auth_idp_google` | `atomic-concrete` | `standard` | yes |
| `40.0` | [swarmauri_auth_idp_keycloak](40-standards/swarmauri_auth_idp_keycloak/) | `40-standards` | `40-standards/swarmauri_auth_idp_keycloak` | `atomic-concrete` | `standard` | yes |
| `40.0` | [swarmauri_auth_idp_okta](40-standards/swarmauri_auth_idp_okta/) | `40-standards` | `40-standards/swarmauri_auth_idp_okta` | `atomic-concrete` | `standard` | yes |
| `40.0` | [swarmauri_auth_idp_salesforce](40-standards/swarmauri_auth_idp_salesforce/) | `40-standards` | `40-standards/swarmauri_auth_idp_salesforce` | `atomic-concrete` | `standard` | yes |

### `bases`

| Index | Package | Layer | Path | Role | Maturity | Workspace |
|---|---|---|---|---|---|---|
| `20.0` | [swarmauri_base](20-bases/swarmauri_base/) | `20-bases` | `20-bases/swarmauri_base` | `base-implementation` | `foundation` | yes |

### `billing`

| Index | Package | Layer | Path | Role | Maturity | Workspace |
|---|---|---|---|---|---|---|
| `40.0` | [swarmauri_billing_mock](40-standards/swarmauri_billing_mock/) | `40-standards` | `40-standards/swarmauri_billing_mock` | `atomic-concrete` | `standard` | yes |
| `40.0` | [swarmauri_billing_stripe](40-standards/swarmauri_billing_stripe/) | `40-standards` | `40-standards/swarmauri_billing_stripe` | `atomic-concrete` | `standard` | yes |
| `50.0` | [swarmauri_billing_adyen](50-community/swarmauri_billing_adyen/) | `50-community` | `50-community/swarmauri_billing_adyen` | `atomic-concrete` | `community` | yes |
| `50.0` | [swarmauri_billing_authorize_net](50-community/swarmauri_billing_authorize_net/) | `50-community` | `50-community/swarmauri_billing_authorize_net` | `atomic-concrete` | `community` | yes |
| `50.0` | [swarmauri_billing_braintree](50-community/swarmauri_billing_braintree/) | `50-community` | `50-community/swarmauri_billing_braintree` | `atomic-concrete` | `community` | yes |
| `50.0` | [swarmauri_billing_paypal](50-community/swarmauri_billing_paypal/) | `50-community` | `50-community/swarmauri_billing_paypal` | `atomic-concrete` | `community` | yes |
| `50.0` | [swarmauri_billing_paystack](50-community/swarmauri_billing_paystack/) | `50-community` | `50-community/swarmauri_billing_paystack` | `atomic-concrete` | `community` | yes |
| `50.0` | [swarmauri_billing_razorpay](50-community/swarmauri_billing_razorpay/) | `50-community` | `50-community/swarmauri_billing_razorpay` | `atomic-concrete` | `community` | yes |
| `50.0` | [swarmauri_billing_square](50-community/swarmauri_billing_square/) | `50-community` | `50-community/swarmauri_billing_square` | `atomic-concrete` | `community` | yes |

### `canon`

| Index | Package | Layer | Path | Role | Maturity | Workspace |
|---|---|---|---|---|---|---|
| `70.0` | [swarmauri_canon_http](70-experimental/swarmauri_canon_http/) | `70-experimental` | `70-experimental/swarmauri_canon_http` | `experimental-atomic` | `experimental` | no |

### `catoml`

| Index | Package | Layer | Path | Role | Maturity | Workspace |
|---|---|---|---|---|---|---|
| `70.0` | [catoml](70-experimental/catoml/) | `70-experimental` | `70-experimental/catoml` | `experimental-atomic` | `experimental` | no |

### `cayaml`

| Index | Package | Layer | Path | Role | Maturity | Workspace |
|---|---|---|---|---|---|---|
| `70.0` | [cayaml](70-experimental/cayaml/) | `70-experimental` | `70-experimental/cayaml` | `experimental-atomic` | `experimental` | no |

### `certs`

| Index | Package | Layer | Path | Role | Maturity | Workspace |
|---|---|---|---|---|---|---|
| `40.0` | [swarmauri_certs_local_ca](40-standards/swarmauri_certs_local_ca/) | `40-standards` | `40-standards/swarmauri_certs_local_ca` | `atomic-concrete` | `standard` | yes |
| `40.0` | [swarmauri_certs_remote_ca](40-standards/swarmauri_certs_remote_ca/) | `40-standards` | `40-standards/swarmauri_certs_remote_ca` | `atomic-concrete` | `standard` | yes |
| `40.0` | [swarmauri_certs_self_signed](40-standards/swarmauri_certs_self_signed/) | `40-standards` | `40-standards/swarmauri_certs_self_signed` | `atomic-concrete` | `standard` | yes |
| `40.0` | [swarmauri_certs_x509verify](40-standards/swarmauri_certs_x509verify/) | `40-standards` | `40-standards/swarmauri_certs_x509verify` | `atomic-concrete` | `standard` | yes |
| `40.1` | [swarmauri_certs_composite](40-standards/swarmauri_certs_composite/) | `40-standards` | `40-standards/swarmauri_certs_composite` | `composite-concrete` | `standard` | yes |
| `40.1` | [swarmauri_certs_x509](40-standards/swarmauri_certs_x509/) | `40-standards` | `40-standards/swarmauri_certs_x509` | `composite-concrete` | `standard` | yes |
| `50.0` | [swarmauri_certs_acme](50-community/swarmauri_certs_acme/) | `50-community` | `50-community/swarmauri_certs_acme` | `atomic-concrete` | `community` | yes |
| `50.0` | [swarmauri_certs_azure](50-community/swarmauri_certs_azure/) | `50-community` | `50-community/swarmauri_certs_azure` | `atomic-concrete` | `community` | yes |
| `50.0` | [swarmauri_certs_cfssl](50-community/swarmauri_certs_cfssl/) | `50-community` | `50-community/swarmauri_certs_cfssl` | `atomic-concrete` | `community` | yes |
| `50.0` | [swarmauri_certs_crlverifyservice](50-community/swarmauri_certs_crlverifyservice/) | `50-community` | `50-community/swarmauri_certs_crlverifyservice` | `atomic-concrete` | `community` | yes |
| `50.0` | [swarmauri_certs_csronly](50-community/swarmauri_certs_csronly/) | `50-community` | `50-community/swarmauri_certs_csronly` | `atomic-concrete` | `community` | yes |
| `50.0` | [swarmauri_certs_ocspverify](50-community/swarmauri_certs_ocspverify/) | `50-community` | `50-community/swarmauri_certs_ocspverify` | `atomic-concrete` | `community` | yes |
| `70.0` | [swarmauri_certs_pkcs11](70-experimental/swarmauri_certs_pkcs11/) | `70-experimental` | `70-experimental/swarmauri_certs_pkcs11` | `experimental-atomic` | `experimental` | yes |

### `certservice`

| Index | Package | Layer | Path | Role | Maturity | Workspace |
|---|---|---|---|---|---|---|
| `50.0` | [swarmauri_certservice_aws_kms](50-community/swarmauri_certservice_aws_kms/) | `50-community` | `50-community/swarmauri_certservice_aws_kms` | `atomic-concrete` | `community` | yes |
| `50.0` | [swarmauri_certservice_gcpkms](50-community/swarmauri_certservice_gcpkms/) | `50-community` | `50-community/swarmauri_certservice_gcpkms` | `atomic-concrete` | `community` | yes |
| `50.0` | [swarmauri_certservice_ms_adcs](50-community/swarmauri_certservice_ms_adcs/) | `50-community` | `50-community/swarmauri_certservice_ms_adcs` | `atomic-concrete` | `community` | yes |
| `50.0` | [swarmauri_certservice_scep](50-community/swarmauri_certservice_scep/) | `50-community` | `50-community/swarmauri_certservice_scep` | `atomic-concrete` | `community` | yes |
| `50.0` | [swarmauri_certservice_stepca](50-community/swarmauri_certservice_stepca/) | `50-community` | `50-community/swarmauri_certservice_stepca` | `atomic-concrete` | `community` | yes |

### `cipher_suite`

| Index | Package | Layer | Path | Role | Maturity | Workspace |
|---|---|---|---|---|---|---|
| `40.0` | [swarmauri_cipher_suite_cades](40-standards/swarmauri_cipher_suite_cades/) | `40-standards` | `40-standards/swarmauri_cipher_suite_cades` | `atomic-concrete` | `standard` | yes |
| `40.0` | [swarmauri_cipher_suite_cnsa20](40-standards/swarmauri_cipher_suite_cnsa20/) | `40-standards` | `40-standards/swarmauri_cipher_suite_cnsa20` | `atomic-concrete` | `standard` | yes |
| `40.0` | [swarmauri_cipher_suite_cose](40-standards/swarmauri_cipher_suite_cose/) | `40-standards` | `40-standards/swarmauri_cipher_suite_cose` | `atomic-concrete` | `standard` | yes |
| `40.0` | [swarmauri_cipher_suite_fips1403](40-standards/swarmauri_cipher_suite_fips1403/) | `40-standards` | `40-standards/swarmauri_cipher_suite_fips1403` | `atomic-concrete` | `standard` | yes |
| `40.0` | [swarmauri_cipher_suite_fips203](40-standards/swarmauri_cipher_suite_fips203/) | `40-standards` | `40-standards/swarmauri_cipher_suite_fips203` | `atomic-concrete` | `standard` | yes |
| `40.0` | [swarmauri_cipher_suite_fips204](40-standards/swarmauri_cipher_suite_fips204/) | `40-standards` | `40-standards/swarmauri_cipher_suite_fips204` | `atomic-concrete` | `standard` | yes |
| `40.0` | [swarmauri_cipher_suite_fips205](40-standards/swarmauri_cipher_suite_fips205/) | `40-standards` | `40-standards/swarmauri_cipher_suite_fips205` | `atomic-concrete` | `standard` | yes |
| `40.0` | [swarmauri_cipher_suite_ipsec](40-standards/swarmauri_cipher_suite_ipsec/) | `40-standards` | `40-standards/swarmauri_cipher_suite_ipsec` | `atomic-concrete` | `standard` | yes |
| `40.0` | [swarmauri_cipher_suite_jwa](40-standards/swarmauri_cipher_suite_jwa/) | `40-standards` | `40-standards/swarmauri_cipher_suite_jwa` | `atomic-concrete` | `standard` | yes |
| `40.0` | [swarmauri_cipher_suite_pades](40-standards/swarmauri_cipher_suite_pades/) | `40-standards` | `40-standards/swarmauri_cipher_suite_pades` | `atomic-concrete` | `standard` | yes |
| `40.0` | [swarmauri_cipher_suite_pep458](40-standards/swarmauri_cipher_suite_pep458/) | `40-standards` | `40-standards/swarmauri_cipher_suite_pep458` | `atomic-concrete` | `standard` | yes |
| `40.0` | [swarmauri_cipher_suite_sigstore](40-standards/swarmauri_cipher_suite_sigstore/) | `40-standards` | `40-standards/swarmauri_cipher_suite_sigstore` | `atomic-concrete` | `standard` | yes |
| `40.0` | [swarmauri_cipher_suite_ssh](40-standards/swarmauri_cipher_suite_ssh/) | `40-standards` | `40-standards/swarmauri_cipher_suite_ssh` | `atomic-concrete` | `standard` | yes |
| `40.0` | [swarmauri_cipher_suite_tls13](40-standards/swarmauri_cipher_suite_tls13/) | `40-standards` | `40-standards/swarmauri_cipher_suite_tls13` | `atomic-concrete` | `standard` | yes |
| `40.0` | [swarmauri_cipher_suite_webauthn](40-standards/swarmauri_cipher_suite_webauthn/) | `40-standards` | `40-standards/swarmauri_cipher_suite_webauthn` | `atomic-concrete` | `standard` | yes |
| `40.0` | [swarmauri_cipher_suite_xades](40-standards/swarmauri_cipher_suite_xades/) | `40-standards` | `40-standards/swarmauri_cipher_suite_xades` | `atomic-concrete` | `standard` | yes |
| `40.0` | [swarmauri_cipher_suite_yubikey](40-standards/swarmauri_cipher_suite_yubikey/) | `40-standards` | `40-standards/swarmauri_cipher_suite_yubikey` | `atomic-concrete` | `standard` | yes |
| `40.0` | [swarmauri_cipher_suite_yubikey_fips](40-standards/swarmauri_cipher_suite_yubikey_fips/) | `40-standards` | `40-standards/swarmauri_cipher_suite_yubikey_fips` | `atomic-concrete` | `standard` | yes |

### `conversation`

| Index | Package | Layer | Path | Role | Maturity | Workspace |
|---|---|---|---|---|---|---|
| `40.0` | [swarmauri_conversation_compacting](40-standards/swarmauri_conversation_compacting/) | `40-standards` | `40-standards/swarmauri_conversation_compacting` | `atomic-concrete` | `standard` | yes |

### `crypto`

| Index | Package | Layer | Path | Role | Maturity | Workspace |
|---|---|---|---|---|---|---|
| `40.0` | [swarmauri_crypto_ecdh_es_a128kw](40-standards/swarmauri_crypto_ecdh_es_a128kw/) | `40-standards` | `40-standards/swarmauri_crypto_ecdh_es_a128kw` | `atomic-concrete` | `standard` | yes |
| `40.0` | [swarmauri_crypto_jwe](40-standards/swarmauri_crypto_jwe/) | `40-standards` | `40-standards/swarmauri_crypto_jwe` | `atomic-concrete` | `standard` | yes |
| `40.0` | [swarmauri_crypto_nacl_pkcs11](40-standards/swarmauri_crypto_nacl_pkcs11/) | `40-standards` | `40-standards/swarmauri_crypto_nacl_pkcs11` | `atomic-concrete` | `standard` | yes |
| `40.0` | [swarmauri_crypto_paramiko](40-standards/swarmauri_crypto_paramiko/) | `40-standards` | `40-standards/swarmauri_crypto_paramiko` | `atomic-concrete` | `standard` | yes |
| `40.0` | [swarmauri_crypto_pgp](40-standards/swarmauri_crypto_pgp/) | `40-standards` | `40-standards/swarmauri_crypto_pgp` | `atomic-concrete` | `standard` | yes |
| `40.0` | [swarmauri_crypto_rust](40-standards/swarmauri_crypto_rust/) | `40-standards` | `40-standards/swarmauri_crypto_rust` | `atomic-concrete` | `standard` | yes |
| `40.1` | [swarmauri_crypto_composite](40-standards/swarmauri_crypto_composite/) | `40-standards` | `40-standards/swarmauri_crypto_composite` | `composite-concrete` | `standard` | yes |
| `70.0` | [swarmauri_crypto_sodium](70-experimental/swarmauri_crypto_sodium/) | `70-experimental` | `70-experimental/swarmauri_crypto_sodium` | `experimental-atomic` | `experimental` | yes |

### `delegation`

| Index | Package | Layer | Path | Role | Maturity | Workspace |
|---|---|---|---|---|---|---|
| `40.0` | [swarmauri_delegation_attenuating](40-standards/swarmauri_delegation_attenuating/) | `40-standards` | `40-standards/swarmauri_delegation_attenuating` | `atomic-concrete` | `standard` | yes |

### `distance`

| Index | Package | Layer | Path | Role | Maturity | Workspace |
|---|---|---|---|---|---|---|
| `40.0` | [swarmauri_distance_canberra](40-standards/swarmauri_distance_canberra/) | `40-standards` | `40-standards/swarmauri_distance_canberra` | `atomic-concrete` | `standard` | yes |
| `40.0` | [swarmauri_distance_chebyshev](40-standards/swarmauri_distance_chebyshev/) | `40-standards` | `40-standards/swarmauri_distance_chebyshev` | `atomic-concrete` | `standard` | yes |
| `40.0` | [swarmauri_distance_chi_squared](40-standards/swarmauri_distance_chi_squared/) | `40-standards` | `40-standards/swarmauri_distance_chi_squared` | `atomic-concrete` | `standard` | yes |
| `40.0` | [swarmauri_distance_cosine](40-standards/swarmauri_distance_cosine/) | `40-standards` | `40-standards/swarmauri_distance_cosine` | `atomic-concrete` | `standard` | yes |
| `40.0` | [swarmauri_distance_euclidean](40-standards/swarmauri_distance_euclidean/) | `40-standards` | `40-standards/swarmauri_distance_euclidean` | `atomic-concrete` | `standard` | yes |
| `40.0` | [swarmauri_distance_haversine](40-standards/swarmauri_distance_haversine/) | `40-standards` | `40-standards/swarmauri_distance_haversine` | `atomic-concrete` | `standard` | yes |
| `40.0` | [swarmauri_distance_jaccard_index](40-standards/swarmauri_distance_jaccard_index/) | `40-standards` | `40-standards/swarmauri_distance_jaccard_index` | `atomic-concrete` | `standard` | yes |
| `40.0` | [swarmauri_distance_levenshtein](40-standards/swarmauri_distance_levenshtein/) | `40-standards` | `40-standards/swarmauri_distance_levenshtein` | `atomic-concrete` | `standard` | yes |
| `40.0` | [swarmauri_distance_manhattan](40-standards/swarmauri_distance_manhattan/) | `40-standards` | `40-standards/swarmauri_distance_manhattan` | `atomic-concrete` | `standard` | yes |
| `40.0` | [swarmauri_distance_minkowski](40-standards/swarmauri_distance_minkowski/) | `40-standards` | `40-standards/swarmauri_distance_minkowski` | `atomic-concrete` | `standard` | yes |
| `40.0` | [swarmauri_distance_sorensen_dice](40-standards/swarmauri_distance_sorensen_dice/) | `40-standards` | `40-standards/swarmauri_distance_sorensen_dice` | `atomic-concrete` | `standard` | yes |
| `40.0` | [swarmauri_distance_squared_euclidean](40-standards/swarmauri_distance_squared_euclidean/) | `40-standards` | `40-standards/swarmauri_distance_squared_euclidean` | `atomic-concrete` | `standard` | yes |

### `distancemetrics`

| Index | Package | Layer | Path | Role | Maturity | Workspace |
|---|---|---|---|---|---|---|
| `70.0` | [DistanceMetrics](70-experimental/RapidSimilarity/DistanceMetrics/) | `70-experimental` | `70-experimental/RapidSimilarity/DistanceMetrics` | `experimental-atomic` | `experimental` | no |

### `do`

| Index | Package | Layer | Path | Role | Maturity | Workspace |
|---|---|---|---|---|---|---|
| `70.0` | [do](70-experimental/do/) | `70-experimental` | `70-experimental/do` | `experimental-atomic` | `experimental` | no |

### `documentstore`

| Index | Package | Layer | Path | Role | Maturity | Workspace |
|---|---|---|---|---|---|---|
| `90.0` | [swarmauri_documentstore_redis](90-deprecated/swarmauri_documentstore_redis/) | `90-deprecated` | `90-deprecated/swarmauri_documentstore_redis` | `compat` | `deprecated` | no |

### `embeddedsigner`

| Index | Package | Layer | Path | Role | Maturity | Workspace |
|---|---|---|---|---|---|---|
| `60.2` | [EmbeddedSigner](60-plugins/embedded_signer/) | `60-plugins` | `60-plugins/embedded_signer` | `plugin-orchestrator` | `plugin` | yes |

### `embedding`

| Index | Package | Layer | Path | Role | Maturity | Workspace |
|---|---|---|---|---|---|---|
| `40.0` | [swarmauri_embedding_doc2vec](40-standards/swarmauri_embedding_doc2vec/) | `40-standards` | `40-standards/swarmauri_embedding_doc2vec` | `atomic-concrete` | `standard` | yes |
| `40.0` | [swarmauri_embedding_nmf](40-standards/swarmauri_embedding_nmf/) | `40-standards` | `40-standards/swarmauri_embedding_nmf` | `atomic-concrete` | `standard` | yes |
| `50.0` | [swarmauri_embedding_mlm](50-community/swarmauri_embedding_mlm/) | `50-community` | `50-community/swarmauri_embedding_mlm` | `atomic-concrete` | `community` | yes |
| `90.0` | [swarmauri_embedding_tfidf](90-deprecated/swarmauri_embedding_tfidf/) | `90-deprecated` | `90-deprecated/swarmauri_embedding_tfidf` | `compat` | `deprecated` | no |

### `embedxmp`

| Index | Package | Layer | Path | Role | Maturity | Workspace |
|---|---|---|---|---|---|---|
| `60.0` | [EmbedXMP](60-plugins/EmbedXMP/) | `60-plugins` | `60-plugins/EmbedXMP` | `plugin` | `plugin` | yes |

### `evaluator`

| Index | Package | Layer | Path | Role | Maturity | Workspace |
|---|---|---|---|---|---|---|
| `40.0` | [swarmauri_evaluator_abstractmethods](40-standards/swarmauri_evaluator_abstractmethods/) | `40-standards` | `40-standards/swarmauri_evaluator_abstractmethods` | `atomic-concrete` | `standard` | yes |
| `40.0` | [swarmauri_evaluator_anyusage](40-standards/swarmauri_evaluator_anyusage/) | `40-standards` | `40-standards/swarmauri_evaluator_anyusage` | `atomic-concrete` | `standard` | yes |
| `40.0` | [swarmauri_evaluator_constanttime](40-standards/swarmauri_evaluator_constanttime/) | `40-standards` | `40-standards/swarmauri_evaluator_constanttime` | `atomic-concrete` | `standard` | yes |
| `40.0` | [swarmauri_evaluator_externalimports](40-standards/swarmauri_evaluator_externalimports/) | `40-standards` | `40-standards/swarmauri_evaluator_externalimports` | `atomic-concrete` | `standard` | yes |
| `40.0` | [swarmauri_evaluator_subprocess](40-standards/swarmauri_evaluator_subprocess/) | `40-standards` | `40-standards/swarmauri_evaluator_subprocess` | `atomic-concrete` | `standard` | yes |

### `evaluatorpool`

| Index | Package | Layer | Path | Role | Maturity | Workspace |
|---|---|---|---|---|---|---|
| `40.0` | [swarmauri_evaluatorpool_accessibility](40-standards/swarmauri_evaluatorpool_accessibility/) | `40-standards` | `40-standards/swarmauri_evaluatorpool_accessibility` | `atomic-concrete` | `standard` | yes |

### `example`

| Index | Package | Layer | Path | Role | Maturity | Workspace |
|---|---|---|---|---|---|---|
| `40.0` | [swm_example_package](40-standards/swm_example_package/) | `40-standards` | `40-standards/swm_example_package` | `atomic-concrete` | `standard` | yes |
| `50.0` | [swm_example_community_package](50-community/swm_example_community_package/) | `50-community` | `50-community/swm_example_community_package` | `atomic-concrete` | `community` | yes |
| `60.0` | [swm_example_plugin](60-plugins/example_plugin/) | `60-plugins` | `60-plugins/example_plugin` | `plugin` | `plugin` | yes |

### `execution`

| Index | Package | Layer | Path | Role | Maturity | Workspace |
|---|---|---|---|---|---|---|
| `40.0` | [swarmauri_execution_default](40-standards/swarmauri_execution_default/) | `40-standards` | `40-standards/swarmauri_execution_default` | `atomic-concrete` | `standard` | yes |

### `experimental`

| Index | Package | Layer | Path | Role | Maturity | Workspace |
|---|---|---|---|---|---|---|
| `90.0` | [swarmauri_experimental](90-deprecated/swarmauri_experimental/) | `90-deprecated` | `90-deprecated/swarmauri_experimental` | `compat` | `deprecated` | yes |

### `facade`

| Index | Package | Layer | Path | Role | Maturity | Workspace |
|---|---|---|---|---|---|---|
| `80.3` | [swarmauri](80-facades/swarmauri/) | `80-facades` | `80-facades/swarmauri` | `facade` | `facade` | yes |

### `fasttokenizer`

| Index | Package | Layer | Path | Role | Maturity | Workspace |
|---|---|---|---|---|---|---|
| `70.0` | [FastTokenizer](70-experimental/FastTokenizer/) | `70-experimental` | `70-experimental/FastTokenizer` | `experimental-atomic` | `experimental` | no |

### `g9`

| Index | Package | Layer | Path | Role | Maturity | Workspace |
|---|---|---|---|---|---|---|
| `70.0` | [g9](70-experimental/g9/) | `70-experimental` | `70-experimental/g9` | `experimental-atomic` | `experimental` | no |

### `gitfilter`

| Index | Package | Layer | Path | Role | Maturity | Workspace |
|---|---|---|---|---|---|---|
| `40.0` | [swarmauri_gitfilter_gh_release](40-standards/swarmauri_gitfilter_gh_release/) | `40-standards` | `40-standards/swarmauri_gitfilter_gh_release` | `atomic-concrete` | `standard` | yes |
| `40.0` | [swarmauri_gitfilter_minio](40-standards/swarmauri_gitfilter_minio/) | `40-standards` | `40-standards/swarmauri_gitfilter_minio` | `atomic-concrete` | `standard` | yes |
| `40.0` | [swarmauri_gitfilter_s3fs](40-standards/swarmauri_gitfilter_s3fs/) | `40-standards` | `40-standards/swarmauri_gitfilter_s3fs` | `atomic-concrete` | `standard` | yes |
| `40.1` | [swarmauri_gitfilter_file](40-standards/swarmauri_gitfilter_file/) | `40-standards` | `40-standards/swarmauri_gitfilter_file` | `composite-concrete` | `standard` | yes |

### `gk`

| Index | Package | Layer | Path | Role | Maturity | Workspace |
|---|---|---|---|---|---|---|
| `70.0` | [gk](70-experimental/gk/) | `70-experimental` | `70-experimental/gk` | `experimental-atomic` | `experimental` | no |

### `grantstore`

| Index | Package | Layer | Path | Role | Maturity | Workspace |
|---|---|---|---|---|---|---|
| `40.0` | [swarmauri_grantstore_sqlite](40-standards/swarmauri_grantstore_sqlite/) | `40-standards` | `40-standards/swarmauri_grantstore_sqlite` | `atomic-concrete` | `standard` | yes |

### `indexbuilder`

| Index | Package | Layer | Path | Role | Maturity | Workspace |
|---|---|---|---|---|---|---|
| `70.0` | [IndexBuilder](70-experimental/RapidSimilarity/IndexBuilder/) | `70-experimental` | `70-experimental/RapidSimilarity/IndexBuilder` | `experimental-atomic` | `experimental` | no |

### `interfaces`

| Index | Package | Layer | Path | Role | Maturity | Workspace |
|---|---|---|---|---|---|---|
| `10.0` | [swarmauri_core](10-interfaces/swarmauri_core/) | `10-interfaces` | `10-interfaces/swarmauri_core` | `interface-contract` | `foundation` | yes |

### `invoker`

| Index | Package | Layer | Path | Role | Maturity | Workspace |
|---|---|---|---|---|---|---|
| `40.0` | [swarmauri_invoker_default](40-standards/swarmauri_invoker_default/) | `40-standards` | `40-standards/swarmauri_invoker_default` | `atomic-concrete` | `standard` | yes |

### `jaml`

| Index | Package | Layer | Path | Role | Maturity | Workspace |
|---|---|---|---|---|---|---|
| `70.0` | [jaml](70-experimental/jaml/) | `70-experimental` | `70-experimental/jaml` | `experimental-atomic` | `experimental` | no |

### `jz`

| Index | Package | Layer | Path | Role | Maturity | Workspace |
|---|---|---|---|---|---|---|
| `70.0` | [jz](70-experimental/jz/) | `70-experimental` | `70-experimental/jz` | `experimental-atomic` | `experimental` | no |

### `keyprovider`

| Index | Package | Layer | Path | Role | Maturity | Workspace |
|---|---|---|---|---|---|---|
| `40.0` | [swarmauri_keyprovider_file](40-standards/swarmauri_keyprovider_file/) | `40-standards` | `40-standards/swarmauri_keyprovider_file` | `atomic-concrete` | `standard` | yes |
| `40.0` | [swarmauri_keyprovider_inmemory](40-standards/swarmauri_keyprovider_inmemory/) | `40-standards` | `40-standards/swarmauri_keyprovider_inmemory` | `atomic-concrete` | `standard` | yes |
| `40.0` | [swarmauri_keyprovider_local](40-standards/swarmauri_keyprovider_local/) | `40-standards` | `40-standards/swarmauri_keyprovider_local` | `atomic-concrete` | `standard` | yes |
| `40.0` | [swarmauri_keyprovider_ssh](40-standards/swarmauri_keyprovider_ssh/) | `40-standards` | `40-standards/swarmauri_keyprovider_ssh` | `atomic-concrete` | `standard` | yes |
| `40.1` | [swarmauri_keyprovider_hierarchical](40-standards/swarmauri_keyprovider_hierarchical/) | `40-standards` | `40-standards/swarmauri_keyprovider_hierarchical` | `composite-concrete` | `standard` | yes |
| `40.1` | [swarmauri_keyprovider_remote_jwks](40-standards/swarmauri_keyprovider_remote_jwks/) | `40-standards` | `40-standards/swarmauri_keyprovider_remote_jwks` | `composite-concrete` | `standard` | yes |
| `50.0` | [swarmauri_keyprovider_aws_kms](50-community/swarmauri_keyprovider_aws_kms/) | `50-community` | `50-community/swarmauri_keyprovider_aws_kms` | `atomic-concrete` | `community` | yes |
| `50.0` | [swarmauri_keyprovider_gcpkms](50-community/swarmauri_keyprovider_gcpkms/) | `50-community` | `50-community/swarmauri_keyprovider_gcpkms` | `atomic-concrete` | `community` | yes |
| `50.0` | [swarmauri_keyprovider_vaulttransit](50-community/swarmauri_keyprovider_vaulttransit/) | `50-community` | `50-community/swarmauri_keyprovider_vaulttransit` | `atomic-concrete` | `community` | yes |
| `70.0` | [swarmauri_keyprovider_pkcs11](70-experimental/swarmauri_keyprovider_pkcs11/) | `70-experimental` | `70-experimental/swarmauri_keyprovider_pkcs11` | `experimental-atomic` | `experimental` | yes |

### `keyproviders`

| Index | Package | Layer | Path | Role | Maturity | Workspace |
|---|---|---|---|---|---|---|
| `40.1` | [swarmauri_keyproviders_mirrored](40-standards/swarmauri_keyproviders_mirrored/) | `40-standards` | `40-standards/swarmauri_keyproviders_mirrored` | `composite-concrete` | `standard` | yes |

### `layout`

| Index | Package | Layer | Path | Role | Maturity | Workspace |
|---|---|---|---|---|---|---|
| `70.0` | [layout_engine](70-experimental/layout_engine/) | `70-experimental` | `70-experimental/layout_engine` | `experimental-atomic` | `experimental` | no |
| `70.1` | [layout_engine_atoms](70-experimental/layout_engine_atoms/) | `70-experimental` | `70-experimental/layout_engine_atoms` | `experimental-composite` | `experimental` | no |

### `live`

| Index | Package | Layer | Path | Role | Maturity | Workspace |
|---|---|---|---|---|---|---|
| `50.0` | [swarmauri_live_model_amazon_nova](50-community/swarmauri_live_model_amazon_nova/) | `50-community` | `50-community/swarmauri_live_model_amazon_nova` | `atomic-concrete` | `community` | yes |
| `50.0` | [swarmauri_live_model_gemini](50-community/swarmauri_live_model_gemini/) | `50-community` | `50-community/swarmauri_live_model_gemini` | `atomic-concrete` | `community` | yes |
| `50.0` | [swarmauri_live_model_openai](50-community/swarmauri_live_model_openai/) | `50-community` | `50-community/swarmauri_live_model_openai` | `atomic-concrete` | `community` | yes |
| `50.0` | [swarmauri_live_model_qwen](50-community/swarmauri_live_model_qwen/) | `50-community` | `50-community/swarmauri_live_model_qwen` | `atomic-concrete` | `community` | yes |
| `50.0` | [swarmauri_live_model_xai](50-community/swarmauri_live_model_xai/) | `50-community` | `50-community/swarmauri_live_model_xai` | `atomic-concrete` | `community` | yes |

### `llm`

| Index | Package | Layer | Path | Role | Maturity | Workspace |
|---|---|---|---|---|---|---|
| `50.0` | [swarmauri_llm_ai21](50-community/swarmauri_llm_ai21/) | `50-community` | `50-community/swarmauri_llm_ai21` | `atomic-concrete` | `community` | yes |
| `50.0` | [swarmauri_llm_anthropic](50-community/swarmauri_llm_anthropic/) | `50-community` | `50-community/swarmauri_llm_anthropic` | `atomic-concrete` | `community` | yes |
| `50.0` | [swarmauri_llm_azureopenai](50-community/swarmauri_llm_azureopenai/) | `50-community` | `50-community/swarmauri_llm_azureopenai` | `atomic-concrete` | `community` | yes |
| `50.0` | [swarmauri_llm_cerebras](50-community/swarmauri_llm_cerebras/) | `50-community` | `50-community/swarmauri_llm_cerebras` | `atomic-concrete` | `community` | yes |
| `50.0` | [swarmauri_llm_cloudflare](50-community/swarmauri_llm_cloudflare/) | `50-community` | `50-community/swarmauri_llm_cloudflare` | `atomic-concrete` | `community` | yes |
| `50.0` | [swarmauri_llm_cohere](50-community/swarmauri_llm_cohere/) | `50-community` | `50-community/swarmauri_llm_cohere` | `atomic-concrete` | `community` | yes |
| `50.0` | [swarmauri_llm_deepinfra](50-community/swarmauri_llm_deepinfra/) | `50-community` | `50-community/swarmauri_llm_deepinfra` | `atomic-concrete` | `community` | yes |
| `50.0` | [swarmauri_llm_deepseek](50-community/swarmauri_llm_deepseek/) | `50-community` | `50-community/swarmauri_llm_deepseek` | `atomic-concrete` | `community` | yes |
| `50.0` | [swarmauri_llm_falai](50-community/swarmauri_llm_falai/) | `50-community` | `50-community/swarmauri_llm_falai` | `atomic-concrete` | `community` | yes |
| `50.0` | [swarmauri_llm_gemini](50-community/swarmauri_llm_gemini/) | `50-community` | `50-community/swarmauri_llm_gemini` | `atomic-concrete` | `community` | yes |
| `50.0` | [swarmauri_llm_groq](50-community/swarmauri_llm_groq/) | `50-community` | `50-community/swarmauri_llm_groq` | `atomic-concrete` | `community` | yes |
| `50.0` | [swarmauri_llm_hyperbolic](50-community/swarmauri_llm_hyperbolic/) | `50-community` | `50-community/swarmauri_llm_hyperbolic` | `atomic-concrete` | `community` | yes |
| `50.0` | [swarmauri_llm_leptonai](50-community/swarmauri_llm_leptonai/) | `50-community` | `50-community/swarmauri_llm_leptonai` | `atomic-concrete` | `community` | yes |
| `50.0` | [swarmauri_llm_llamacpp](50-community/swarmauri_llm_llamacpp/) | `50-community` | `50-community/swarmauri_llm_llamacpp` | `atomic-concrete` | `community` | yes |
| `50.0` | [swarmauri_llm_mistral](50-community/swarmauri_llm_mistral/) | `50-community` | `50-community/swarmauri_llm_mistral` | `atomic-concrete` | `community` | yes |
| `50.0` | [swarmauri_llm_nvidia_nim](50-community/swarmauri_llm_nvidia_nim/) | `50-community` | `50-community/swarmauri_llm_nvidia_nim` | `atomic-concrete` | `community` | yes |
| `50.0` | [swarmauri_llm_openai](50-community/swarmauri_llm_openai/) | `50-community` | `50-community/swarmauri_llm_openai` | `atomic-concrete` | `community` | yes |
| `50.0` | [swarmauri_llm_perplexity](50-community/swarmauri_llm_perplexity/) | `50-community` | `50-community/swarmauri_llm_perplexity` | `atomic-concrete` | `community` | yes |
| `50.0` | [swarmauri_llm_whisper](50-community/swarmauri_llm_whisper/) | `50-community` | `50-community/swarmauri_llm_whisper` | `atomic-concrete` | `community` | yes |
| `50.0` | [swarmauri_llm_xai](50-community/swarmauri_llm_xai/) | `50-community` | `50-community/swarmauri_llm_xai` | `atomic-concrete` | `community` | yes |
| `50.1` | [swarmauri_llm_openrouter](50-community/swarmauri_llm_openrouter/) | `50-community` | `50-community/swarmauri_llm_openrouter` | `composite-concrete` | `community` | yes |
| `90.0` | [swarmauri_llm_playht](90-deprecated/swarmauri_llm_playht/) | `90-deprecated` | `90-deprecated/swarmauri_llm_playht` | `compat` | `deprecated` | yes |

### `matrix`

| Index | Package | Layer | Path | Role | Maturity | Workspace |
|---|---|---|---|---|---|---|
| `50.1` | [swarmauri_matrix_hamming74](50-community/swarmauri_matrix_hamming74/) | `50-community` | `50-community/swarmauri_matrix_hamming74` | `composite-concrete` | `community` | yes |

### `measurement`

| Index | Package | Layer | Path | Role | Maturity | Workspace |
|---|---|---|---|---|---|---|
| `50.0` | [swarmauri_measurement_mutualinformation](50-community/swarmauri_measurement_mutualinformation/) | `50-community` | `50-community/swarmauri_measurement_mutualinformation` | `atomic-concrete` | `community` | yes |
| `50.0` | [swarmauri_measurement_tokencountestimator](50-community/swarmauri_measurement_tokencountestimator/) | `50-community` | `50-community/swarmauri_measurement_tokencountestimator` | `atomic-concrete` | `community` | yes |

### `mediasigner`

| Index | Package | Layer | Path | Role | Maturity | Workspace |
|---|---|---|---|---|---|---|
| `60.1` | [MediaSigner](60-plugins/media_signer/) | `60-plugins` | `60-plugins/media_signer` | `plugin-composite` | `plugin` | yes |

### `metric`

| Index | Package | Layer | Path | Role | Maturity | Workspace |
|---|---|---|---|---|---|---|
| `40.0` | [swamauri_metric_wasserstein](40-standards/swamauri_metric_wasserstein/) | `40-standards` | `40-standards/swamauri_metric_wasserstein` | `atomic-concrete` | `standard` | yes |
| `50.0` | [swarmauri_metric_hamming](50-community/swarmauri_metric_hamming/) | `50-community` | `50-community/swarmauri_metric_hamming` | `atomic-concrete` | `community` | yes |

### `middleware`

| Index | Package | Layer | Path | Role | Maturity | Workspace |
|---|---|---|---|---|---|---|
| `40.0` | [swarmauri_middleware_bulkhead](40-standards/swarmauri_middleware_bulkhead/) | `40-standards` | `40-standards/swarmauri_middleware_bulkhead` | `atomic-concrete` | `standard` | yes |
| `40.0` | [swarmauri_middleware_cachecontrol](40-standards/swarmauri_middleware_cachecontrol/) | `40-standards` | `40-standards/swarmauri_middleware_cachecontrol` | `atomic-concrete` | `standard` | yes |
| `40.0` | [swarmauri_middleware_cors](40-standards/swarmauri_middleware_cors/) | `40-standards` | `40-standards/swarmauri_middleware_cors` | `atomic-concrete` | `standard` | yes |
| `40.0` | [swarmauri_middleware_exceptionhandling](40-standards/swarmauri_middleware_exceptionhandling/) | `40-standards` | `40-standards/swarmauri_middleware_exceptionhandling` | `atomic-concrete` | `standard` | yes |
| `40.0` | [swarmauri_middleware_gzipcompression](40-standards/swarmauri_middleware_gzipcompression/) | `40-standards` | `40-standards/swarmauri_middleware_gzipcompression` | `atomic-concrete` | `standard` | yes |
| `40.0` | [swarmauri_middleware_httpsig](40-standards/swarmauri_middleware_httpsig/) | `40-standards` | `40-standards/swarmauri_middleware_httpsig` | `atomic-concrete` | `standard` | yes |
| `40.0` | [swarmauri_middleware_jsonrpc](40-standards/swarmauri_middleware_jsonrpc/) | `40-standards` | `40-standards/swarmauri_middleware_jsonrpc` | `atomic-concrete` | `standard` | yes |
| `40.0` | [swarmauri_middleware_jwksverifier](40-standards/swarmauri_middleware_jwksverifier/) | `40-standards` | `40-standards/swarmauri_middleware_jwksverifier` | `atomic-concrete` | `standard` | yes |
| `40.0` | [swarmauri_middleware_llamaguard](40-standards/swarmauri_middleware_llamaguard/) | `40-standards` | `40-standards/swarmauri_middleware_llamaguard` | `atomic-concrete` | `standard` | yes |
| `40.0` | [swarmauri_middleware_logging](40-standards/swarmauri_middleware_logging/) | `40-standards` | `40-standards/swarmauri_middleware_logging` | `atomic-concrete` | `standard` | yes |
| `40.0` | [swarmauri_middleware_ratelimit](40-standards/swarmauri_middleware_ratelimit/) | `40-standards` | `40-standards/swarmauri_middleware_ratelimit` | `atomic-concrete` | `standard` | yes |
| `40.0` | [swarmauri_middleware_securityheaders](40-standards/swarmauri_middleware_securityheaders/) | `40-standards` | `40-standards/swarmauri_middleware_securityheaders` | `atomic-concrete` | `standard` | yes |
| `40.0` | [swarmauri_middleware_session](40-standards/swarmauri_middleware_session/) | `40-standards` | `40-standards/swarmauri_middleware_session` | `atomic-concrete` | `standard` | yes |
| `40.0` | [swarmauri_middleware_stdio](40-standards/swarmauri_middleware_stdio/) | `40-standards` | `40-standards/swarmauri_middleware_stdio` | `atomic-concrete` | `standard` | yes |
| `40.0` | [swarmauri_middleware_time](40-standards/swarmauri_middleware_time/) | `40-standards` | `40-standards/swarmauri_middleware_time` | `atomic-concrete` | `standard` | yes |
| `40.2` | [swarmauri_middleware_jwt](40-standards/swarmauri_middleware_jwt/) | `40-standards` | `40-standards/swarmauri_middleware_jwt` | `orchestrator` | `standard` | yes |
| `50.0` | [swarmauri_middleware_circuitbreaker](50-community/swarmauri_middleware_circuitbreaker/) | `50-community` | `50-community/swarmauri_middleware_circuitbreaker` | `atomic-concrete` | `community` | yes |
| `50.0` | [swarmauri_middleware_ratepolicy](50-community/swarmauri_middleware_ratepolicy/) | `50-community` | `50-community/swarmauri_middleware_ratepolicy` | `atomic-concrete` | `community` | yes |

### `monotone`

| Index | Package | Layer | Path | Role | Maturity | Workspace |
|---|---|---|---|---|---|---|
| `70.0` | [monotone-ops](70-experimental/monotone_ops/) | `70-experimental` | `70-experimental/monotone_ops` | `experimental-atomic` | `experimental` | yes |

### `mre_crypto`

| Index | Package | Layer | Path | Role | Maturity | Workspace |
|---|---|---|---|---|---|---|
| `40.0` | [swarmauri_mre_crypto_age](40-standards/swarmauri_mre_crypto_age/) | `40-standards` | `40-standards/swarmauri_mre_crypto_age` | `atomic-concrete` | `standard` | yes |
| `40.0` | [swarmauri_mre_crypto_ecdh_es_kw](40-standards/swarmauri_mre_crypto_ecdh_es_kw/) | `40-standards` | `40-standards/swarmauri_mre_crypto_ecdh_es_kw` | `atomic-concrete` | `standard` | yes |
| `40.0` | [swarmauri_mre_crypto_keyring](40-standards/swarmauri_mre_crypto_keyring/) | `40-standards` | `40-standards/swarmauri_mre_crypto_keyring` | `atomic-concrete` | `standard` | yes |
| `40.0` | [swarmauri_mre_crypto_pgp](40-standards/swarmauri_mre_crypto_pgp/) | `40-standards` | `40-standards/swarmauri_mre_crypto_pgp` | `atomic-concrete` | `standard` | yes |
| `40.0` | [swarmauri_mre_crypto_shamir](40-standards/swarmauri_mre_crypto_shamir/) | `40-standards` | `40-standards/swarmauri_mre_crypto_shamir` | `atomic-concrete` | `standard` | yes |

### `mto`

| Index | Package | Layer | Path | Role | Maturity | Workspace |
|---|---|---|---|---|---|---|
| `70.0` | [mto](70-experimental/mto/) | `70-experimental` | `70-experimental/mto` | `experimental-atomic` | `experimental` | yes |

### `ocr`

| Index | Package | Layer | Path | Role | Maturity | Workspace |
|---|---|---|---|---|---|---|
| `50.0` | [swarmauri_ocr_pytesseract](50-community/swarmauri_ocr_pytesseract/) | `50-community` | `50-community/swarmauri_ocr_pytesseract` | `atomic-concrete` | `community` | yes |

### `parser`

| Index | Package | Layer | Path | Role | Maturity | Workspace |
|---|---|---|---|---|---|---|
| `40.0` | [swarmauri_parser_beautifulsoupelement](40-standards/swarmauri_parser_beautifulsoupelement/) | `40-standards` | `40-standards/swarmauri_parser_beautifulsoupelement` | `atomic-concrete` | `standard` | yes |
| `40.0` | [swarmauri_parser_keywordextractor](40-standards/swarmauri_parser_keywordextractor/) | `40-standards` | `40-standards/swarmauri_parser_keywordextractor` | `atomic-concrete` | `standard` | yes |
| `50.0` | [swarmauri_parser_bertembedding](50-community/swarmauri_parser_bertembedding/) | `50-community` | `50-community/swarmauri_parser_bertembedding` | `atomic-concrete` | `community` | yes |
| `50.0` | [swarmauri_parser_entityrecognition](50-community/swarmauri_parser_entityrecognition/) | `50-community` | `50-community/swarmauri_parser_entityrecognition` | `atomic-concrete` | `community` | yes |
| `50.0` | [swarmauri_parser_fitzpdf](50-community/swarmauri_parser_fitzpdf/) | `50-community` | `50-community/swarmauri_parser_fitzpdf` | `atomic-concrete` | `community` | yes |
| `50.0` | [swarmauri_parser_pypdf2](50-community/swarmauri_parser_pypdf2/) | `50-community` | `50-community/swarmauri_parser_pypdf2` | `atomic-concrete` | `community` | yes |
| `50.0` | [swarmauri_parser_pypdftk](50-community/swarmauri_parser_pypdftk/) | `50-community` | `50-community/swarmauri_parser_pypdftk` | `atomic-concrete` | `community` | yes |
| `50.0` | [swarmauri_parser_slate](50-community/swarmauri_parser_slate/) | `50-community` | `50-community/swarmauri_parser_slate` | `atomic-concrete` | `community` | yes |
| `50.0` | [swarmauri_parser_textblob](50-community/swarmauri_parser_textblob/) | `50-community` | `50-community/swarmauri_parser_textblob` | `atomic-concrete` | `community` | yes |
| `70.0` | [swarmauri_parser_asn1](70-experimental/swarmauri_parser_asn1/) | `70-experimental` | `70-experimental/swarmauri_parser_asn1` | `experimental-atomic` | `experimental` | yes |

### `permission`

| Index | Package | Layer | Path | Role | Maturity | Workspace |
|---|---|---|---|---|---|---|
| `40.0` | [swarmauri_permission_explicit](40-standards/swarmauri_permission_explicit/) | `40-standards` | `40-standards/swarmauri_permission_explicit` | `atomic-concrete` | `standard` | yes |

### `pj`

| Index | Package | Layer | Path | Role | Maturity | Workspace |
|---|---|---|---|---|---|---|
| `70.0` | [pj](70-experimental/pj/) | `70-experimental` | `70-experimental/pj` | `experimental-atomic` | `experimental` | no |

### `pop`

| Index | Package | Layer | Path | Role | Maturity | Workspace |
|---|---|---|---|---|---|---|
| `40.0` | [swarmauri_pop_cwt](40-standards/swarmauri_pop_cwt/) | `40-standards` | `40-standards/swarmauri_pop_cwt` | `atomic-concrete` | `standard` | yes |
| `40.0` | [swarmauri_pop_dpop](40-standards/swarmauri_pop_dpop/) | `40-standards` | `40-standards/swarmauri_pop_dpop` | `atomic-concrete` | `standard` | yes |
| `40.0` | [swarmauri_pop_x509](40-standards/swarmauri_pop_x509/) | `40-standards` | `40-standards/swarmauri_pop_x509` | `atomic-concrete` | `standard` | yes |

### `process`

| Index | Package | Layer | Path | Role | Maturity | Workspace |
|---|---|---|---|---|---|---|
| `40.0` | [swarmauri_process_docker](40-standards/swarmauri_process_docker/) | `40-standards` | `40-standards/swarmauri_process_docker` | `atomic-concrete` | `standard` | yes |
| `40.0` | [swarmauri_process_kubernetes](40-standards/swarmauri_process_kubernetes/) | `40-standards` | `40-standards/swarmauri_process_kubernetes` | `atomic-concrete` | `standard` | yes |
| `40.0` | [swarmauri_process_subprocess](40-standards/swarmauri_process_subprocess/) | `40-standards` | `40-standards/swarmauri_process_subprocess` | `atomic-concrete` | `standard` | yes |

### `prompt`

| Index | Package | Layer | Path | Role | Maturity | Workspace |
|---|---|---|---|---|---|---|
| `40.0` | [swarmauri_prompt_j2prompttemplate](40-standards/swarmauri_prompt_j2prompttemplate/) | `40-standards` | `40-standards/swarmauri_prompt_j2prompttemplate` | `atomic-concrete` | `standard` | yes |

### `provider`

| Index | Package | Layer | Path | Role | Maturity | Workspace |
|---|---|---|---|---|---|---|
| `50.0` | [swarmauri_provider_amazon_nova](50-community/swarmauri_provider_amazon_nova/) | `50-community` | `50-community/swarmauri_provider_amazon_nova` | `atomic-concrete` | `community` | yes |
| `50.0` | [swarmauri_provider_gemini](50-community/swarmauri_provider_gemini/) | `50-community` | `50-community/swarmauri_provider_gemini` | `atomic-concrete` | `community` | yes |
| `50.0` | [swarmauri_provider_openai](50-community/swarmauri_provider_openai/) | `50-community` | `50-community/swarmauri_provider_openai` | `atomic-concrete` | `community` | yes |
| `50.0` | [swarmauri_provider_openrouter](50-community/swarmauri_provider_openrouter/) | `50-community` | `50-community/swarmauri_provider_openrouter` | `atomic-concrete` | `community` | yes |
| `50.0` | [swarmauri_provider_qwen](50-community/swarmauri_provider_qwen/) | `50-community` | `50-community/swarmauri_provider_qwen` | `atomic-concrete` | `community` | yes |
| `50.0` | [swarmauri_provider_xai](50-community/swarmauri_provider_xai/) | `50-community` | `50-community/swarmauri_provider_xai` | `atomic-concrete` | `community` | yes |

### `ptree`

| Index | Package | Layer | Path | Role | Maturity | Workspace |
|---|---|---|---|---|---|---|
| `70.0` | [ptree_dag_extension_example](70-experimental/ptree_dag_extension_example/) | `70-experimental` | `70-experimental/ptree_dag_extension_example` | `experimental-atomic` | `experimental` | yes |

### `publisher`

| Index | Package | Layer | Path | Role | Maturity | Workspace |
|---|---|---|---|---|---|---|
| `40.0` | [swarmauri_publisher_rabbitmq](40-standards/swarmauri_publisher_rabbitmq/) | `40-standards` | `40-standards/swarmauri_publisher_rabbitmq` | `atomic-concrete` | `standard` | yes |
| `40.0` | [swarmauri_publisher_redis](40-standards/swarmauri_publisher_redis/) | `40-standards` | `40-standards/swarmauri_publisher_redis` | `atomic-concrete` | `standard` | yes |
| `40.0` | [swarmauri_publisher_webhook](40-standards/swarmauri_publisher_webhook/) | `40-standards` | `40-standards/swarmauri_publisher_webhook` | `atomic-concrete` | `standard` | yes |

### `queryengine`

| Index | Package | Layer | Path | Role | Maturity | Workspace |
|---|---|---|---|---|---|---|
| `70.0` | [QueryEngine](70-experimental/RapidSimilarity/QueryEngine/) | `70-experimental` | `70-experimental/RapidSimilarity/QueryEngine` | `experimental-atomic` | `experimental` | no |

### `runstore`

| Index | Package | Layer | Path | Role | Maturity | Workspace |
|---|---|---|---|---|---|---|
| `40.0` | [swarmauri_runstore_sqlite](40-standards/swarmauri_runstore_sqlite/) | `40-standards` | `40-standards/swarmauri_runstore_sqlite` | `atomic-concrete` | `standard` | yes |

### `s.f`

| Index | Package | Layer | Path | Role | Maturity | Workspace |
|---|---|---|---|---|---|---|
| `70.0` | [s.f](70-experimental/s_f/) | `70-experimental` | `70-experimental/s_f` | `experimental-atomic` | `experimental` | no |

### `sfw`

| Index | Package | Layer | Path | Role | Maturity | Workspace |
|---|---|---|---|---|---|---|
| `70.0` | [sfw](70-experimental/sfw/) | `70-experimental` | `70-experimental/sfw` | `experimental-atomic` | `experimental` | no |

### `signing`

| Index | Package | Layer | Path | Role | Maturity | Workspace |
|---|---|---|---|---|---|---|
| `40.0` | [swarmauri_signing_ca](40-standards/swarmauri_signing_ca/) | `40-standards` | `40-standards/swarmauri_signing_ca` | `atomic-concrete` | `standard` | yes |
| `40.0` | [swarmauri_signing_cms](40-standards/swarmauri_signing_cms/) | `40-standards` | `40-standards/swarmauri_signing_cms` | `atomic-concrete` | `standard` | yes |
| `40.0` | [swarmauri_signing_ecdsa](40-standards/swarmauri_signing_ecdsa/) | `40-standards` | `40-standards/swarmauri_signing_ecdsa` | `atomic-concrete` | `standard` | yes |
| `40.0` | [swarmauri_signing_ed25519](40-standards/swarmauri_signing_ed25519/) | `40-standards` | `40-standards/swarmauri_signing_ed25519` | `atomic-concrete` | `standard` | yes |
| `40.0` | [swarmauri_signing_hmac](40-standards/swarmauri_signing_hmac/) | `40-standards` | `40-standards/swarmauri_signing_hmac` | `atomic-concrete` | `standard` | yes |
| `40.0` | [swarmauri_signing_openpgp](40-standards/swarmauri_signing_openpgp/) | `40-standards` | `40-standards/swarmauri_signing_openpgp` | `atomic-concrete` | `standard` | yes |
| `40.0` | [swarmauri_signing_pep458](40-standards/swarmauri_signing_pep458/) | `40-standards` | `40-standards/swarmauri_signing_pep458` | `atomic-concrete` | `standard` | yes |
| `40.0` | [swarmauri_signing_pgp](40-standards/swarmauri_signing_pgp/) | `40-standards` | `40-standards/swarmauri_signing_pgp` | `atomic-concrete` | `standard` | yes |
| `40.0` | [swarmauri_signing_rsa](40-standards/swarmauri_signing_rsa/) | `40-standards` | `40-standards/swarmauri_signing_rsa` | `atomic-concrete` | `standard` | yes |
| `40.0` | [swarmauri_signing_secp256k1](40-standards/swarmauri_signing_secp256k1/) | `40-standards` | `40-standards/swarmauri_signing_secp256k1` | `atomic-concrete` | `standard` | yes |
| `40.0` | [swarmauri_signing_sigv4](40-standards/swarmauri_signing_sigv4/) | `40-standards` | `40-standards/swarmauri_signing_sigv4` | `atomic-concrete` | `standard` | yes |
| `40.0` | [swarmauri_signing_ssh](40-standards/swarmauri_signing_ssh/) | `40-standards` | `40-standards/swarmauri_signing_ssh` | `atomic-concrete` | `standard` | yes |
| `40.0` | [swarmauri_signing_xmld](40-standards/swarmauri_signing_xmld/) | `40-standards` | `40-standards/swarmauri_signing_xmld` | `atomic-concrete` | `standard` | yes |
| `40.1` | [swarmauri_signing_jws](40-standards/swarmauri_signing_jws/) | `40-standards` | `40-standards/swarmauri_signing_jws` | `composite-concrete` | `standard` | yes |
| `40.1` | [swarmauri_signing_pdf](40-standards/swarmauri_signing_pdf/) | `40-standards` | `40-standards/swarmauri_signing_pdf` | `composite-concrete` | `standard` | yes |
| `40.2` | [swarmauri_signing_dpop](40-standards/swarmauri_signing_dpop/) | `40-standards` | `40-standards/swarmauri_signing_dpop` | `orchestrator` | `standard` | yes |
| `50.0` | [swarmauri_signing_dsse](50-community/swarmauri_signing_dsse/) | `50-community` | `50-community/swarmauri_signing_dsse` | `atomic-concrete` | `community` | yes |

### `similarity`

| Index | Package | Layer | Path | Role | Maturity | Workspace |
|---|---|---|---|---|---|---|
| `40.0` | [swarmauri_similarity_gzip](40-standards/swarmauri_similarity_gzip/) | `40-standards` | `40-standards/swarmauri_similarity_gzip` | `atomic-concrete` | `standard` | yes |

### `skill`

| Index | Package | Layer | Path | Role | Maturity | Workspace |
|---|---|---|---|---|---|---|
| `40.0` | [swarmauri_skill_dummy_filesystem](40-standards/swarmauri_skill_dummy_filesystem/) | `40-standards` | `40-standards/swarmauri_skill_dummy_filesystem` | `atomic-concrete` | `standard` | yes |
| `40.0` | [swarmauri_skill_dummy_local](40-standards/swarmauri_skill_dummy_local/) | `40-standards` | `40-standards/swarmauri_skill_dummy_local` | `atomic-concrete` | `standard` | yes |
| `40.0` | [swarmauri_skill_filesystem](40-standards/swarmauri_skill_filesystem/) | `40-standards` | `40-standards/swarmauri_skill_filesystem` | `atomic-concrete` | `standard` | yes |
| `40.0` | [swarmauri_skill_local](40-standards/swarmauri_skill_local/) | `40-standards` | `40-standards/swarmauri_skill_local` | `atomic-concrete` | `standard` | yes |

### `snt`

| Index | Package | Layer | Path | Role | Maturity | Workspace |
|---|---|---|---|---|---|---|
| `70.0` | [snt](70-experimental/snt/) | `70-experimental` | `70-experimental/snt` | `experimental-atomic` | `experimental` | no |

### `standard-kernel`

| Index | Package | Layer | Path | Role | Maturity | Workspace |
|---|---|---|---|---|---|---|
| `30.0` | [swarmauri_standard](30-standard-kernel/swarmauri_standard/) | `30-standard-kernel` | `30-standard-kernel/swarmauri_standard` | `standard-kernel` | `standard-kernel` | yes |

### `state`

| Index | Package | Layer | Path | Role | Maturity | Workspace |
|---|---|---|---|---|---|---|
| `50.0` | [swarmauri_state_clipboard](50-community/swarmauri_state_clipboard/) | `50-community` | `50-community/swarmauri_state_clipboard` | `atomic-concrete` | `community` | yes |

### `storage`

| Index | Package | Layer | Path | Role | Maturity | Workspace |
|---|---|---|---|---|---|---|
| `40.0` | [swarmauri_storage_file](40-standards/swarmauri_storage_file/) | `40-standards` | `40-standards/swarmauri_storage_file` | `atomic-concrete` | `standard` | yes |
| `40.0` | [swarmauri_storage_github](40-standards/swarmauri_storage_github/) | `40-standards` | `40-standards/swarmauri_storage_github` | `atomic-concrete` | `standard` | yes |
| `40.0` | [swarmauri_storage_github_release](40-standards/swarmauri_storage_github_release/) | `40-standards` | `40-standards/swarmauri_storage_github_release` | `atomic-concrete` | `standard` | yes |
| `40.0` | [swarmauri_storage_memory](40-standards/swarmauri_storage_memory/) | `40-standards` | `40-standards/swarmauri_storage_memory` | `atomic-concrete` | `standard` | yes |
| `40.0` | [swarmauri_storage_minio](40-standards/swarmauri_storage_minio/) | `40-standards` | `40-standards/swarmauri_storage_minio` | `atomic-concrete` | `standard` | yes |
| `40.0` | [swarmauri_storage_s3](40-standards/swarmauri_storage_s3/) | `40-standards` | `40-standards/swarmauri_storage_s3` | `atomic-concrete` | `standard` | yes |
| `40.0` | [swarmauri_storage_s3_over_sftp](40-standards/swarmauri_storage_s3_over_sftp/) | `40-standards` | `40-standards/swarmauri_storage_s3_over_sftp` | `atomic-concrete` | `standard` | yes |
| `40.0` | [swarmauri_storage_s3fs](40-standards/swarmauri_storage_s3fs/) | `40-standards` | `40-standards/swarmauri_storage_s3fs` | `atomic-concrete` | `standard` | yes |
| `40.0` | [swarmauri_storage_webdav](40-standards/swarmauri_storage_webdav/) | `40-standards` | `40-standards/swarmauri_storage_webdav` | `atomic-concrete` | `standard` | yes |

### `taskmanager`

| Index | Package | Layer | Path | Role | Maturity | Workspace |
|---|---|---|---|---|---|---|
| `40.0` | [swarmauri_taskmanager_default](40-standards/swarmauri_taskmanager_default/) | `40-standards` | `40-standards/swarmauri_taskmanager_default` | `atomic-concrete` | `standard` | yes |

### `taskstore`

| Index | Package | Layer | Path | Role | Maturity | Workspace |
|---|---|---|---|---|---|---|
| `40.0` | [swarmauri_taskstore_sqlite](40-standards/swarmauri_taskstore_sqlite/) | `40-standards` | `40-standards/swarmauri_taskstore_sqlite` | `atomic-concrete` | `standard` | yes |

### `tests`

| Index | Package | Layer | Path | Role | Maturity | Workspace |
|---|---|---|---|---|---|---|
| `50.0` | [swarmauri_tests_griffe](50-community/swarmauri_tests_griffe/) | `50-community` | `50-community/swarmauri_tests_griffe` | `atomic-concrete` | `community` | yes |
| `70.0` | [swarmauri_tests_component](70-experimental/swarmauri_tests_component/) | `70-experimental` | `70-experimental/swarmauri_tests_component` | `experimental-atomic` | `experimental` | yes |
| `70.0` | [swarmauri_tests_loc_tersity](70-experimental/swarmauri_tests_loc_tersity/) | `70-experimental` | `70-experimental/swarmauri_tests_loc_tersity` | `experimental-atomic` | `experimental` | yes |
| `70.0` | [swarmauri_tests_pylicense](70-experimental/swarmauri_tests_pylicense/) | `70-experimental` | `70-experimental/swarmauri_tests_pylicense` | `experimental-atomic` | `experimental` | yes |
| `70.0` | [swarmauri_tests_readme_examples](70-experimental/swarmauri_tests_readme_examples/) | `70-experimental` | `70-experimental/swarmauri_tests_readme_examples` | `experimental-atomic` | `experimental` | yes |

### `tigr`

| Index | Package | Layer | Path | Role | Maturity | Workspace |
|---|---|---|---|---|---|---|
| `70.0` | [tigr](70-experimental/tigr/) | `70-experimental` | `70-experimental/tigr` | `experimental-atomic` | `experimental` | yes |

### `tokens`

| Index | Package | Layer | Path | Role | Maturity | Workspace |
|---|---|---|---|---|---|---|
| `40.0` | [swarmauri_tokens_dpopboundjwt](40-standards/swarmauri_tokens_dpopboundjwt/) | `40-standards` | `40-standards/swarmauri_tokens_dpopboundjwt` | `atomic-concrete` | `standard` | yes |
| `40.0` | [swarmauri_tokens_introspection](40-standards/swarmauri_tokens_introspection/) | `40-standards` | `40-standards/swarmauri_tokens_introspection` | `atomic-concrete` | `standard` | yes |
| `40.0` | [swarmauri_tokens_jwt](40-standards/swarmauri_tokens_jwt/) | `40-standards` | `40-standards/swarmauri_tokens_jwt` | `atomic-concrete` | `standard` | yes |
| `40.0` | [swarmauri_tokens_paseto_v4](40-standards/swarmauri_tokens_paseto_v4/) | `40-standards` | `40-standards/swarmauri_tokens_paseto_v4` | `atomic-concrete` | `standard` | yes |
| `40.0` | [swarmauri_tokens_remoteoidc](40-standards/swarmauri_tokens_remoteoidc/) | `40-standards` | `40-standards/swarmauri_tokens_remoteoidc` | `atomic-concrete` | `standard` | yes |
| `40.0` | [swarmauri_tokens_rotatingjwt](40-standards/swarmauri_tokens_rotatingjwt/) | `40-standards` | `40-standards/swarmauri_tokens_rotatingjwt` | `atomic-concrete` | `standard` | yes |
| `40.0` | [swarmauri_tokens_sshcert](40-standards/swarmauri_tokens_sshcert/) | `40-standards` | `40-standards/swarmauri_tokens_sshcert` | `atomic-concrete` | `standard` | yes |
| `40.0` | [swarmauri_tokens_sshsig](40-standards/swarmauri_tokens_sshsig/) | `40-standards` | `40-standards/swarmauri_tokens_sshsig` | `atomic-concrete` | `standard` | yes |
| `40.0` | [swarmauri_tokens_tlsboundjwt](40-standards/swarmauri_tokens_tlsboundjwt/) | `40-standards` | `40-standards/swarmauri_tokens_tlsboundjwt` | `atomic-concrete` | `standard` | yes |
| `40.1` | [swarmauri_tokens_composite](40-standards/swarmauri_tokens_composite/) | `40-standards` | `40-standards/swarmauri_tokens_composite` | `composite-concrete` | `standard` | yes |

### `tool`

| Index | Package | Layer | Path | Role | Maturity | Workspace |
|---|---|---|---|---|---|---|
| `40.0` | [swarmauri_tool_activateskill](40-standards/swarmauri_tool_activateskill/) | `40-standards` | `40-standards/swarmauri_tool_activateskill` | `atomic-concrete` | `standard` | yes |
| `40.0` | [swarmauri_tool_askuser](40-standards/swarmauri_tool_askuser/) | `40-standards` | `40-standards/swarmauri_tool_askuser` | `atomic-concrete` | `standard` | yes |
| `40.0` | [swarmauri_tool_cancelprocess](40-standards/swarmauri_tool_cancelprocess/) | `40-standards` | `40-standards/swarmauri_tool_cancelprocess` | `atomic-concrete` | `standard` | yes |
| `40.0` | [swarmauri_tool_containerfeedchars](40-standards/swarmauri_tool_containerfeedchars/) | `40-standards` | `40-standards/swarmauri_tool_containerfeedchars` | `atomic-concrete` | `standard` | yes |
| `40.0` | [swarmauri_tool_containermakepr](40-standards/swarmauri_tool_containermakepr/) | `40-standards` | `40-standards/swarmauri_tool_containermakepr` | `atomic-concrete` | `standard` | yes |
| `40.0` | [swarmauri_tool_containernewsession](40-standards/swarmauri_tool_containernewsession/) | `40-standards` | `40-standards/swarmauri_tool_containernewsession` | `atomic-concrete` | `standard` | yes |
| `40.0` | [swarmauri_tool_githubloader](40-standards/swarmauri_tool_githubloader/) | `40-standards` | `40-standards/swarmauri_tool_githubloader` | `atomic-concrete` | `standard` | yes |
| `40.0` | [swarmauri_tool_httploaded](40-standards/swarmauri_tool_httploaded/) | `40-standards` | `40-standards/swarmauri_tool_httploaded` | `atomic-concrete` | `standard` | yes |
| `40.0` | [swarmauri_tool_inspectruntimetool](40-standards/swarmauri_tool_inspectruntimetool/) | `40-standards` | `40-standards/swarmauri_tool_inspectruntimetool` | `atomic-concrete` | `standard` | yes |
| `40.0` | [swarmauri_tool_inspectskill](40-standards/swarmauri_tool_inspectskill/) | `40-standards` | `40-standards/swarmauri_tool_inspectskill` | `atomic-concrete` | `standard` | yes |
| `40.0` | [swarmauri_tool_listruntimetools](40-standards/swarmauri_tool_listruntimetools/) | `40-standards` | `40-standards/swarmauri_tool_listruntimetools` | `atomic-concrete` | `standard` | yes |
| `40.0` | [swarmauri_tool_listskills](40-standards/swarmauri_tool_listskills/) | `40-standards` | `40-standards/swarmauri_tool_listskills` | `atomic-concrete` | `standard` | yes |
| `40.0` | [swarmauri_tool_matplotlib](40-standards/swarmauri_tool_matplotlib/) | `40-standards` | `40-standards/swarmauri_tool_matplotlib` | `atomic-concrete` | `standard` | yes |
| `40.0` | [swarmauri_tool_readprocessoutput](40-standards/swarmauri_tool_readprocessoutput/) | `40-standards` | `40-standards/swarmauri_tool_readprocessoutput` | `atomic-concrete` | `standard` | yes |
| `40.0` | [swarmauri_tool_readskillresource](40-standards/swarmauri_tool_readskillresource/) | `40-standards` | `40-standards/swarmauri_tool_readskillresource` | `atomic-concrete` | `standard` | yes |
| `40.0` | [swarmauri_tool_registerruntimetool](40-standards/swarmauri_tool_registerruntimetool/) | `40-standards` | `40-standards/swarmauri_tool_registerruntimetool` | `atomic-concrete` | `standard` | yes |
| `40.0` | [swarmauri_tool_replaceruntimetool](40-standards/swarmauri_tool_replaceruntimetool/) | `40-standards` | `40-standards/swarmauri_tool_replaceruntimetool` | `atomic-concrete` | `standard` | yes |
| `40.0` | [swarmauri_tool_runbashscript](40-standards/swarmauri_tool_runbashscript/) | `40-standards` | `40-standards/swarmauri_tool_runbashscript` | `atomic-concrete` | `standard` | yes |
| `40.0` | [swarmauri_tool_runcommand](40-standards/swarmauri_tool_runcommand/) | `40-standards` | `40-standards/swarmauri_tool_runcommand` | `atomic-concrete` | `standard` | yes |
| `40.0` | [swarmauri_tool_runpackagechecks](40-standards/swarmauri_tool_runpackagechecks/) | `40-standards` | `40-standards/swarmauri_tool_runpackagechecks` | `atomic-concrete` | `standard` | yes |
| `40.0` | [swarmauri_tool_skill_execution](40-standards/swarmauri_tool_skill_execution/) | `40-standards` | `40-standards/swarmauri_tool_skill_execution` | `atomic-concrete` | `standard` | yes |
| `40.0` | [swarmauri_tool_subprocess](40-standards/swarmauri_tool_subprocess/) | `40-standards` | `40-standards/swarmauri_tool_subprocess` | `atomic-concrete` | `standard` | yes |
| `40.0` | [swarmauri_tool_unregisterruntimetool](40-standards/swarmauri_tool_unregisterruntimetool/) | `40-standards` | `40-standards/swarmauri_tool_unregisterruntimetool` | `atomic-concrete` | `standard` | yes |
| `40.0` | [swarmauri_tool_writestdin](40-standards/swarmauri_tool_writestdin/) | `40-standards` | `40-standards/swarmauri_tool_writestdin` | `atomic-concrete` | `standard` | yes |
| `50.0` | [swarmauri_tool_addcontenttorag](50-community/swarmauri_tool_addcontenttorag/) | `50-community` | `50-community/swarmauri_tool_addcontenttorag` | `atomic-concrete` | `community` | yes |
| `50.0` | [swarmauri_tool_captchagenerator](50-community/swarmauri_tool_captchagenerator/) | `50-community` | `50-community/swarmauri_tool_captchagenerator` | `atomic-concrete` | `community` | yes |
| `50.0` | [swarmauri_tool_createfile](50-community/swarmauri_tool_createfile/) | `50-community` | `50-community/swarmauri_tool_createfile` | `atomic-concrete` | `community` | yes |
| `50.0` | [swarmauri_tool_dalechallreadability](50-community/swarmauri_tool_dalechallreadability/) | `50-community` | `50-community/swarmauri_tool_dalechallreadability` | `atomic-concrete` | `community` | yes |
| `50.0` | [swarmauri_tool_downloadpdf](50-community/swarmauri_tool_downloadpdf/) | `50-community` | `50-community/swarmauri_tool_downloadpdf` | `atomic-concrete` | `community` | yes |
| `50.0` | [swarmauri_tool_entityrecognition](50-community/swarmauri_tool_entityrecognition/) | `50-community` | `50-community/swarmauri_tool_entityrecognition` | `atomic-concrete` | `community` | yes |
| `50.0` | [swarmauri_tool_findfile](50-community/swarmauri_tool_findfile/) | `50-community` | `50-community/swarmauri_tool_findfile` | `atomic-concrete` | `community` | yes |
| `50.0` | [swarmauri_tool_folium](50-community/swarmauri_tool_folium/) | `50-community` | `50-community/swarmauri_tool_folium` | `atomic-concrete` | `community` | yes |
| `50.0` | [swarmauri_tool_getmethodsignature](50-community/swarmauri_tool_getmethodsignature/) | `50-community` | `50-community/swarmauri_tool_getmethodsignature` | `atomic-concrete` | `community` | yes |
| `50.0` | [swarmauri_tool_gmail](50-community/swarmauri_tool_gmail/) | `50-community` | `50-community/swarmauri_tool_gmail` | `atomic-concrete` | `community` | yes |
| `50.0` | [swarmauri_tool_jupyterclearoutput](50-community/swarmauri_tool_jupyterclearoutput/) | `50-community` | `50-community/swarmauri_tool_jupyterclearoutput` | `atomic-concrete` | `community` | yes |
| `50.0` | [swarmauri_tool_jupyterdisplay](50-community/swarmauri_tool_jupyterdisplay/) | `50-community` | `50-community/swarmauri_tool_jupyterdisplay` | `atomic-concrete` | `community` | yes |
| `50.0` | [swarmauri_tool_jupyterdisplayhtml](50-community/swarmauri_tool_jupyterdisplayhtml/) | `50-community` | `50-community/swarmauri_tool_jupyterdisplayhtml` | `atomic-concrete` | `community` | yes |
| `50.0` | [swarmauri_tool_jupyterexecuteandconvert](50-community/swarmauri_tool_jupyterexecuteandconvert/) | `50-community` | `50-community/swarmauri_tool_jupyterexecuteandconvert` | `atomic-concrete` | `community` | yes |
| `50.0` | [swarmauri_tool_jupyterexecutecell](50-community/swarmauri_tool_jupyterexecutecell/) | `50-community` | `50-community/swarmauri_tool_jupyterexecutecell` | `atomic-concrete` | `community` | yes |
| `50.0` | [swarmauri_tool_jupyterexecutenotebook](50-community/swarmauri_tool_jupyterexecutenotebook/) | `50-community` | `50-community/swarmauri_tool_jupyterexecutenotebook` | `atomic-concrete` | `community` | yes |
| `50.0` | [swarmauri_tool_jupyterexecutenotebookwithparameters](50-community/swarmauri_tool_jupyterexecutenotebookwithparameters/) | `50-community` | `50-community/swarmauri_tool_jupyterexecutenotebookwithparameters` | `atomic-concrete` | `community` | yes |
| `50.0` | [swarmauri_tool_jupyterexporthtml](50-community/swarmauri_tool_jupyterexporthtml/) | `50-community` | `50-community/swarmauri_tool_jupyterexporthtml` | `atomic-concrete` | `community` | yes |
| `50.0` | [swarmauri_tool_jupyterexportlatex](50-community/swarmauri_tool_jupyterexportlatex/) | `50-community` | `50-community/swarmauri_tool_jupyterexportlatex` | `atomic-concrete` | `community` | yes |
| `50.0` | [swarmauri_tool_jupyterexportmarkdown](50-community/swarmauri_tool_jupyterexportmarkdown/) | `50-community` | `50-community/swarmauri_tool_jupyterexportmarkdown` | `atomic-concrete` | `community` | yes |
| `50.0` | [swarmauri_tool_jupyterexportpython](50-community/swarmauri_tool_jupyterexportpython/) | `50-community` | `50-community/swarmauri_tool_jupyterexportpython` | `atomic-concrete` | `community` | yes |
| `50.0` | [swarmauri_tool_jupyterfromdict](50-community/swarmauri_tool_jupyterfromdict/) | `50-community` | `50-community/swarmauri_tool_jupyterfromdict` | `atomic-concrete` | `community` | yes |
| `50.0` | [swarmauri_tool_jupytergetiopubmessage](50-community/swarmauri_tool_jupytergetiopubmessage/) | `50-community` | `50-community/swarmauri_tool_jupytergetiopubmessage` | `atomic-concrete` | `community` | yes |
| `50.0` | [swarmauri_tool_jupytergetshellmessage](50-community/swarmauri_tool_jupytergetshellmessage/) | `50-community` | `50-community/swarmauri_tool_jupytergetshellmessage` | `atomic-concrete` | `community` | yes |
| `50.0` | [swarmauri_tool_jupyterreadnotebook](50-community/swarmauri_tool_jupyterreadnotebook/) | `50-community` | `50-community/swarmauri_tool_jupyterreadnotebook` | `atomic-concrete` | `community` | yes |
| `50.0` | [swarmauri_tool_jupyterruncell](50-community/swarmauri_tool_jupyterruncell/) | `50-community` | `50-community/swarmauri_tool_jupyterruncell` | `atomic-concrete` | `community` | yes |
| `50.0` | [swarmauri_tool_jupytershutdownkernel](50-community/swarmauri_tool_jupytershutdownkernel/) | `50-community` | `50-community/swarmauri_tool_jupytershutdownkernel` | `atomic-concrete` | `community` | yes |
| `50.0` | [swarmauri_tool_jupyterstartkernel](50-community/swarmauri_tool_jupyterstartkernel/) | `50-community` | `50-community/swarmauri_tool_jupyterstartkernel` | `atomic-concrete` | `community` | yes |
| `50.0` | [swarmauri_tool_jupytervalidatenotebook](50-community/swarmauri_tool_jupytervalidatenotebook/) | `50-community` | `50-community/swarmauri_tool_jupytervalidatenotebook` | `atomic-concrete` | `community` | yes |
| `50.0` | [swarmauri_tool_jupyterwritenotebook](50-community/swarmauri_tool_jupyterwritenotebook/) | `50-community` | `50-community/swarmauri_tool_jupyterwritenotebook` | `atomic-concrete` | `community` | yes |
| `50.0` | [swarmauri_tool_lexicaldensity](50-community/swarmauri_tool_lexicaldensity/) | `50-community` | `50-community/swarmauri_tool_lexicaldensity` | `atomic-concrete` | `community` | yes |
| `50.0` | [swarmauri_tool_listfiles](50-community/swarmauri_tool_listfiles/) | `50-community` | `50-community/swarmauri_tool_listfiles` | `atomic-concrete` | `community` | yes |
| `50.0` | [swarmauri_tool_psutil](50-community/swarmauri_tool_psutil/) | `50-community` | `50-community/swarmauri_tool_psutil` | `atomic-concrete` | `community` | yes |
| `50.0` | [swarmauri_tool_qrcodegenerator](50-community/swarmauri_tool_qrcodegenerator/) | `50-community` | `50-community/swarmauri_tool_qrcodegenerator` | `atomic-concrete` | `community` | yes |
| `50.0` | [swarmauri_tool_queryimagevectorstore](50-community/swarmauri_tool_queryimagevectorstore/) | `50-community` | `50-community/swarmauri_tool_queryimagevectorstore` | `atomic-concrete` | `community` | yes |
| `50.0` | [swarmauri_tool_queryknowledgebase](50-community/swarmauri_tool_queryknowledgebase/) | `50-community` | `50-community/swarmauri_tool_queryknowledgebase` | `atomic-concrete` | `community` | yes |
| `50.0` | [swarmauri_tool_scrollfile](50-community/swarmauri_tool_scrollfile/) | `50-community` | `50-community/swarmauri_tool_scrollfile` | `atomic-concrete` | `community` | yes |
| `50.0` | [swarmauri_tool_searchword](50-community/swarmauri_tool_searchword/) | `50-community` | `50-community/swarmauri_tool_searchword` | `atomic-concrete` | `community` | yes |
| `50.0` | [swarmauri_tool_sentencecomplexity](50-community/swarmauri_tool_sentencecomplexity/) | `50-community` | `50-community/swarmauri_tool_sentencecomplexity` | `atomic-concrete` | `community` | yes |
| `50.0` | [swarmauri_tool_sentimentanalysis](50-community/swarmauri_tool_sentimentanalysis/) | `50-community` | `50-community/swarmauri_tool_sentimentanalysis` | `atomic-concrete` | `community` | yes |
| `50.0` | [swarmauri_tool_smogindex](50-community/swarmauri_tool_smogindex/) | `50-community` | `50-community/swarmauri_tool_smogindex` | `atomic-concrete` | `community` | yes |
| `50.0` | [swarmauri_tool_textlength](50-community/swarmauri_tool_textlength/) | `50-community` | `50-community/swarmauri_tool_textlength` | `atomic-concrete` | `community` | yes |
| `50.0` | [swarmauri_tool_webscraping](50-community/swarmauri_tool_webscraping/) | `50-community` | `50-community/swarmauri_tool_webscraping` | `atomic-concrete` | `community` | yes |
| `50.0` | [swarmauri_tool_zapierhook](50-community/swarmauri_tool_zapierhook/) | `50-community` | `50-community/swarmauri_tool_zapierhook` | `atomic-concrete` | `community` | yes |

### `toolkit`

| Index | Package | Layer | Path | Role | Maturity | Workspace |
|---|---|---|---|---|---|---|
| `40.2` | [swarmauri_toolkit_containertoolkit](40-standards/swarmauri_toolkit_containertoolkit/) | `40-standards` | `40-standards/swarmauri_toolkit_containertoolkit` | `orchestrator` | `standard` | yes |
| `40.2` | [swarmauri_toolkit_runtime](40-standards/swarmauri_toolkit_runtime/) | `40-standards` | `40-standards/swarmauri_toolkit_runtime` | `orchestrator` | `standard` | yes |
| `40.2` | [swarmauri_toolkit_skillset](40-standards/swarmauri_toolkit_skillset/) | `40-standards` | `40-standards/swarmauri_toolkit_skillset` | `orchestrator` | `standard` | yes |
| `50.2` | [swarmauri_toolkit_github](50-community/swarmauri_toolkit_github/) | `50-community` | `50-community/swarmauri_toolkit_github` | `orchestrator` | `community` | yes |
| `50.2` | [swarmauri_toolkit_jupytertoolkit](50-community/swarmauri_toolkit_jupytertoolkit/) | `50-community` | `50-community/swarmauri_toolkit_jupytertoolkit` | `orchestrator` | `community` | yes |

### `transport`

| Index | Package | Layer | Path | Role | Maturity | Workspace |
|---|---|---|---|---|---|---|
| `40.0` | [swarmauri_transport_asgi](40-standards/swarmauri_transport_asgi/) | `40-standards` | `40-standards/swarmauri_transport_asgi` | `atomic-concrete` | `standard` | yes |
| `40.0` | [swarmauri_transport_aws_eventstream](40-standards/swarmauri_transport_aws_eventstream/) | `40-standards` | `40-standards/swarmauri_transport_aws_eventstream` | `atomic-concrete` | `standard` | yes |
| `40.0` | [swarmauri_transport_h2mux](40-standards/swarmauri_transport_h2mux/) | `40-standards` | `40-standards/swarmauri_transport_h2mux` | `atomic-concrete` | `standard` | yes |
| `40.0` | [swarmauri_transport_httpx](40-standards/swarmauri_transport_httpx/) | `40-standards` | `40-standards/swarmauri_transport_httpx` | `atomic-concrete` | `standard` | yes |
| `40.0` | [swarmauri_transport_meshsidecarhttp2](40-standards/swarmauri_transport_meshsidecarhttp2/) | `40-standards` | `40-standards/swarmauri_transport_meshsidecarhttp2` | `atomic-concrete` | `standard` | yes |
| `40.0` | [swarmauri_transport_mtlsunicast](40-standards/swarmauri_transport_mtlsunicast/) | `40-standards` | `40-standards/swarmauri_transport_mtlsunicast` | `atomic-concrete` | `standard` | yes |
| `40.0` | [swarmauri_transport_quic](40-standards/swarmauri_transport_quic/) | `40-standards` | `40-standards/swarmauri_transport_quic` | `atomic-concrete` | `standard` | yes |
| `40.0` | [swarmauri_transport_retry](40-standards/swarmauri_transport_retry/) | `40-standards` | `40-standards/swarmauri_transport_retry` | `atomic-concrete` | `standard` | yes |
| `40.0` | [swarmauri_transport_sseoutbound](40-standards/swarmauri_transport_sseoutbound/) | `40-standards` | `40-standards/swarmauri_transport_sseoutbound` | `atomic-concrete` | `standard` | yes |
| `40.0` | [swarmauri_transport_sshtunnel](40-standards/swarmauri_transport_sshtunnel/) | `40-standards` | `40-standards/swarmauri_transport_sshtunnel` | `atomic-concrete` | `standard` | yes |
| `40.0` | [swarmauri_transport_stdio](40-standards/swarmauri_transport_stdio/) | `40-standards` | `40-standards/swarmauri_transport_stdio` | `atomic-concrete` | `standard` | yes |
| `40.0` | [swarmauri_transport_tcpunicast](40-standards/swarmauri_transport_tcpunicast/) | `40-standards` | `40-standards/swarmauri_transport_tcpunicast` | `atomic-concrete` | `standard` | yes |
| `40.0` | [swarmauri_transport_tls_unicast](40-standards/swarmauri_transport_tls_unicast/) | `40-standards` | `40-standards/swarmauri_transport_tls_unicast` | `atomic-concrete` | `standard` | yes |
| `40.0` | [swarmauri_transport_udp](40-standards/swarmauri_transport_udp/) | `40-standards` | `40-standards/swarmauri_transport_udp` | `atomic-concrete` | `standard` | yes |
| `40.0` | [swarmauri_transport_uds_unicast](40-standards/swarmauri_transport_uds_unicast/) | `40-standards` | `40-standards/swarmauri_transport_uds_unicast` | `atomic-concrete` | `standard` | yes |
| `40.0` | [swarmauri_transport_websocket](40-standards/swarmauri_transport_websocket/) | `40-standards` | `40-standards/swarmauri_transport_websocket` | `atomic-concrete` | `standard` | yes |
| `40.0` | [swarmauri_transport_wsjsonrpcmux](40-standards/swarmauri_transport_wsjsonrpcmux/) | `40-standards` | `40-standards/swarmauri_transport_wsjsonrpcmux` | `atomic-concrete` | `standard` | yes |
| `40.1` | [swarmauri_transport_h2](40-standards/swarmauri_transport_h2/) | `40-standards` | `40-standards/swarmauri_transport_h2` | `composite-concrete` | `standard` | yes |
| `40.2` | [swarmauri_transport_https_unicast](40-standards/swarmauri_transport_https_unicast/) | `40-standards` | `40-standards/swarmauri_transport_https_unicast` | `orchestrator` | `standard` | yes |

### `tts`

| Index | Package | Layer | Path | Role | Maturity | Workspace |
|---|---|---|---|---|---|---|
| `40.0` | [swarmauri_tts_azure](40-standards/swarmauri_tts_azure/) | `40-standards` | `40-standards/swarmauri_tts_azure` | `atomic-concrete` | `standard` | yes |
| `40.0` | [swarmauri_tts_cartesia](40-standards/swarmauri_tts_cartesia/) | `40-standards` | `40-standards/swarmauri_tts_cartesia` | `atomic-concrete` | `standard` | yes |
| `40.0` | [swarmauri_tts_deepgram](40-standards/swarmauri_tts_deepgram/) | `40-standards` | `40-standards/swarmauri_tts_deepgram` | `atomic-concrete` | `standard` | yes |
| `40.0` | [swarmauri_tts_deepinfra](40-standards/swarmauri_tts_deepinfra/) | `40-standards` | `40-standards/swarmauri_tts_deepinfra` | `atomic-concrete` | `standard` | yes |
| `40.0` | [swarmauri_tts_deepinfra_kokoro](40-standards/swarmauri_tts_deepinfra_kokoro/) | `40-standards` | `40-standards/swarmauri_tts_deepinfra_kokoro` | `atomic-concrete` | `standard` | yes |
| `40.0` | [swarmauri_tts_deepinfra_qwen3](40-standards/swarmauri_tts_deepinfra_qwen3/) | `40-standards` | `40-standards/swarmauri_tts_deepinfra_qwen3` | `atomic-concrete` | `standard` | yes |
| `40.0` | [swarmauri_tts_deepinfra_qwen3_voicedesign](40-standards/swarmauri_tts_deepinfra_qwen3_voicedesign/) | `40-standards` | `40-standards/swarmauri_tts_deepinfra_qwen3_voicedesign` | `atomic-concrete` | `standard` | yes |
| `40.0` | [swarmauri_tts_elevenlabs](40-standards/swarmauri_tts_elevenlabs/) | `40-standards` | `40-standards/swarmauri_tts_elevenlabs` | `atomic-concrete` | `standard` | yes |
| `40.0` | [swarmauri_tts_elevenlabs_dialogue](40-standards/swarmauri_tts_elevenlabs_dialogue/) | `40-standards` | `40-standards/swarmauri_tts_elevenlabs_dialogue` | `atomic-concrete` | `standard` | yes |
| `40.0` | [swarmauri_tts_gemini](40-standards/swarmauri_tts_gemini/) | `40-standards` | `40-standards/swarmauri_tts_gemini` | `atomic-concrete` | `standard` | yes |
| `40.0` | [swarmauri_tts_gemini_dialogue](40-standards/swarmauri_tts_gemini_dialogue/) | `40-standards` | `40-standards/swarmauri_tts_gemini_dialogue` | `atomic-concrete` | `standard` | yes |
| `40.0` | [swarmauri_tts_openai](40-standards/swarmauri_tts_openai/) | `40-standards` | `40-standards/swarmauri_tts_openai` | `atomic-concrete` | `standard` | yes |
| `40.0` | [swarmauri_tts_polly](40-standards/swarmauri_tts_polly/) | `40-standards` | `40-standards/swarmauri_tts_polly` | `atomic-concrete` | `standard` | yes |
| `40.0` | [swarmauri_tts_together](40-standards/swarmauri_tts_together/) | `40-standards` | `40-standards/swarmauri_tts_together` | `atomic-concrete` | `standard` | yes |
| `90.0` | [swarmauri_tts_playht](90-deprecated/swarmauri_tts_playht/) | `90-deprecated` | `90-deprecated/swarmauri_tts_playht` | `compat` | `deprecated` | yes |

### `typing`

| Index | Package | Layer | Path | Role | Maturity | Workspace |
|---|---|---|---|---|---|---|
| `00.0` | [swarmauri_typing](00-typing/swarmauri_typing/) | `00-typing` | `00-typing/swarmauri_typing` | `atomic-foundation` | `foundation` | yes |

### `uu`

| Index | Package | Layer | Path | Role | Maturity | Workspace |
|---|---|---|---|---|---|---|
| `70.0` | [uu](70-experimental/uu/) | `70-experimental` | `70-experimental/uu` | `experimental-atomic` | `experimental` | no |

### `vb`

| Index | Package | Layer | Path | Role | Maturity | Workspace |
|---|---|---|---|---|---|---|
| `70.0` | [vb](70-experimental/vb/) | `70-experimental` | `70-experimental/vb` | `experimental-atomic` | `experimental` | no |

### `vectorstore`

| Index | Package | Layer | Path | Role | Maturity | Workspace |
|---|---|---|---|---|---|---|
| `40.1` | [swarmauri_vectorstore_doc2vec](40-standards/swarmauri_vectorstore_doc2vec/) | `40-standards` | `40-standards/swarmauri_vectorstore_doc2vec` | `composite-concrete` | `standard` | yes |
| `50.0` | [swarmauri_vectorstore_annoy](50-community/swarmauri_vectorstore_annoy/) | `50-community` | `50-community/swarmauri_vectorstore_annoy` | `atomic-concrete` | `community` | yes |
| `50.0` | [swarmauri_vectorstore_cloudweaviate](50-community/swarmauri_vectorstore_cloudweaviate/) | `50-community` | `50-community/swarmauri_vectorstore_cloudweaviate` | `atomic-concrete` | `community` | yes |
| `50.0` | [swarmauri_vectorstore_duckdb](50-community/swarmauri_vectorstore_duckdb/) | `50-community` | `50-community/swarmauri_vectorstore_duckdb` | `atomic-concrete` | `community` | yes |
| `50.0` | [swarmauri_vectorstore_fs](50-community/swarmauri_vectorstore_fs/) | `50-community` | `50-community/swarmauri_vectorstore_fs` | `atomic-concrete` | `community` | yes |
| `50.0` | [swarmauri_vectorstore_git](50-community/swarmauri_vectorstore_git/) | `50-community` | `50-community/swarmauri_vectorstore_git` | `atomic-concrete` | `community` | yes |
| `50.0` | [swarmauri_vectorstore_neo4j](50-community/swarmauri_vectorstore_neo4j/) | `50-community` | `50-community/swarmauri_vectorstore_neo4j` | `atomic-concrete` | `community` | yes |
| `50.0` | [swarmauri_vectorstore_persistentchromadb](50-community/swarmauri_vectorstore_persistentchromadb/) | `50-community` | `50-community/swarmauri_vectorstore_persistentchromadb` | `atomic-concrete` | `community` | yes |
| `50.0` | [swarmauri_vectorstore_pinecone](50-community/swarmauri_vectorstore_pinecone/) | `50-community` | `50-community/swarmauri_vectorstore_pinecone` | `atomic-concrete` | `community` | yes |
| `50.0` | [swarmauri_vectorstore_qdrant](50-community/swarmauri_vectorstore_qdrant/) | `50-community` | `50-community/swarmauri_vectorstore_qdrant` | `atomic-concrete` | `community` | yes |
| `50.0` | [swarmauri_vectorstore_redis](50-community/swarmauri_vectorstore_redis/) | `50-community` | `50-community/swarmauri_vectorstore_redis` | `atomic-concrete` | `community` | yes |
| `50.1` | [swarmauri_vectorstore_mlm](50-community/swarmauri_vectorstore_mlm/) | `50-community` | `50-community/swarmauri_vectorstore_mlm` | `composite-concrete` | `community` | yes |
| `90.1` | [swarmauri_vectorstore_tfidf](90-deprecated/swarmauri_vectorstore_tfidf/) | `90-deprecated` | `90-deprecated/swarmauri_vectorstore_tfidf` | `compat-composite` | `deprecated` | no |

### `video`

| Index | Package | Layer | Path | Role | Maturity | Workspace |
|---|---|---|---|---|---|---|
| `50.0` | [swarmauri_video_lipsync_synclabs](50-community/swarmauri_video_lipsync_synclabs/) | `50-community` | `50-community/swarmauri_video_lipsync_synclabs` | `atomic-concrete` | `community` | yes |

### `workflow`

| Index | Package | Layer | Path | Role | Maturity | Workspace |
|---|---|---|---|---|---|---|
| `40.2` | [swarmauri_workflow_delegatedresearch](40-standards/swarmauri_workflow_delegatedresearch/) | `40-standards` | `40-standards/swarmauri_workflow_delegatedresearch` | `orchestrator` | `standard` | yes |
| `40.2` | [swarmauri_workflow_documentassistant](40-standards/swarmauri_workflow_documentassistant/) | `40-standards` | `40-standards/swarmauri_workflow_documentassistant` | `orchestrator` | `standard` | yes |
| `70.2` | [swarmauri_workflow_statedriven](70-experimental/swarmauri_workflow_statedriven/) | `70-experimental` | `70-experimental/swarmauri_workflow_statedriven` | `experimental-orchestrator` | `experimental` | yes |

### `xj`

| Index | Package | Layer | Path | Role | Maturity | Workspace |
|---|---|---|---|---|---|---|
| `70.0` | [xj](70-experimental/xj/) | `70-experimental` | `70-experimental/xj` | `experimental-atomic` | `experimental` | no |

### `xk`

| Index | Package | Layer | Path | Role | Maturity | Workspace |
|---|---|---|---|---|---|---|
| `70.0` | [xk](70-experimental/xk/) | `70-experimental` | `70-experimental/xk` | `experimental-atomic` | `experimental` | no |

### `xmp`

| Index | Package | Layer | Path | Role | Maturity | Workspace |
|---|---|---|---|---|---|---|
| `40.0` | [swarmauri_xmp_gif](40-standards/swarmauri_xmp_gif/) | `40-standards` | `40-standards/swarmauri_xmp_gif` | `atomic-concrete` | `standard` | yes |
| `40.0` | [swarmauri_xmp_jpeg](40-standards/swarmauri_xmp_jpeg/) | `40-standards` | `40-standards/swarmauri_xmp_jpeg` | `atomic-concrete` | `standard` | yes |
| `40.0` | [swarmauri_xmp_mp4](40-standards/swarmauri_xmp_mp4/) | `40-standards` | `40-standards/swarmauri_xmp_mp4` | `atomic-concrete` | `standard` | yes |
| `40.0` | [swarmauri_xmp_pdf](40-standards/swarmauri_xmp_pdf/) | `40-standards` | `40-standards/swarmauri_xmp_pdf` | `atomic-concrete` | `standard` | yes |
| `40.0` | [swarmauri_xmp_png](40-standards/swarmauri_xmp_png/) | `40-standards` | `40-standards/swarmauri_xmp_png` | `atomic-concrete` | `standard` | yes |
| `40.0` | [swarmauri_xmp_svg](40-standards/swarmauri_xmp_svg/) | `40-standards` | `40-standards/swarmauri_xmp_svg` | `atomic-concrete` | `standard` | yes |
| `40.0` | [swarmauri_xmp_tiff](40-standards/swarmauri_xmp_tiff/) | `40-standards` | `40-standards/swarmauri_xmp_tiff` | `atomic-concrete` | `standard` | yes |
| `40.0` | [swarmauri_xmp_webp](40-standards/swarmauri_xmp_webp/) | `40-standards` | `40-standards/swarmauri_xmp_webp` | `atomic-concrete` | `standard` | yes |

### `xz`

| Index | Package | Layer | Path | Role | Maturity | Workspace |
|---|---|---|---|---|---|---|
| `70.0` | [xz](70-experimental/xz/) | `70-experimental` | `70-experimental/xz` | `experimental-atomic` | `experimental` | no |

### `ye`

| Index | Package | Layer | Path | Role | Maturity | Workspace |
|---|---|---|---|---|---|---|
| `70.0` | [ye](70-experimental/ye/) | `70-experimental` | `70-experimental/ye` | `experimental-atomic` | `experimental` | no |

### `ymls`

| Index | Package | Layer | Path | Role | Maturity | Workspace |
|---|---|---|---|---|---|---|
| `70.0` | [ymls](70-experimental/ymls/) | `70-experimental` | `70-experimental/ymls` | `experimental-atomic` | `experimental` | no |

### `zdx`

| Index | Package | Layer | Path | Role | Maturity | Workspace |
|---|---|---|---|---|---|---|
| `60.0` | [zdx](60-plugins/zdx/) | `60-plugins` | `60-plugins/zdx` | `plugin` | `plugin` | yes |

### `zr0`

| Index | Package | Layer | Path | Role | Maturity | Workspace |
|---|---|---|---|---|---|---|
| `70.0` | [zr0](70-experimental/zr0/) | `70-experimental` | `70-experimental/zr0` | `experimental-atomic` | `experimental` | no |
