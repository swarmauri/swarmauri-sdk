## 🛠️ CLI Reference `auth‑authn`

> All commands follow the pattern
> `auto-authn <GROUP> <COMMAND> [OPTIONS]`
> Global flags (apply to every invocation):
> `--quiet/-q`  suppress banner │ `--log-level/-l DEBUG|INFO|…` │ `--db-url` override DB URL

| Group       | Command                                      | Purpose                                                          | Essential Flags                                                                             |
| ----------- | -------------------------------------------- | ---------------------------------------------------------------- | ------------------------------------------------------------------------------------------- |
| **tenants** | `create <slug>`                              | Initialise a tenant with fresh RSA keys                          | `--issuer URL` (issuer URL)<br>`--name TEXT`                                                |
|             | `list`                                       | Table of all tenants                                             | *(none)*                                                                                    |
|             | `rotate-keys`                                | Generate a new signing key for every tenant and prune stale keys | `--grace SECONDS` (keep old keys this long)                                                 |
|             | `deactivate <slug>` / `activate <slug>`      | Soft‑disable / re‑enable a tenant                                | *(none)*                                                                                    |
| **clients** | `register <tenant>`                          | Register a relying‑party (RP)                                    | `--client-id TEXT` (optional)<br>`--redirect-uris URI [...]` *(repeatable)*                 |
|             | `list <tenant>`                              | List RPs for tenant                                              | *(none)*                                                                                    |
|             | `rotate-secret <tenant> <client_id>`         | Replace client secret (prints plaintext once)                    | *(none)*                                                                                    |
|             | `deactivate / activate <tenant> <client_id>` | Toggle RP access                                                 | *(none)*                                                                                    |
| **users**   | `add`                                        | Create user interactively                                        | `--tenant/-t TENANT`<br>`--username/-u NAME`<br>`--email/-e ADDR`<br>`--random-password/-R` |
|             | `list`                                       | Show users                                                       | `--tenant TENANT` `--all` (include inactive)                                                |
|             | `passwd`                                     | Reset password                                                   | `--tenant` `--random-password/-R`                                                           |
|             | `deactivate / activate`                      | Soft‑disable / enable user                                       | `--tenant TENANT`                                                                           |
| **keys**    | `list <tenant>`                              | Show current tenant JWKS (public)                                | *(none)*                                                                                    |
|             | `export <tenant> --outfile jwks.json`        | Dump public JWKS to disk                                         | `--outfile PATH`                                                                            |

---

### Typical Workflows

#### 1 . On‑board a new SaaS customer

```bash
# A. create tenant + admin user
auto-authn tenants create acme --issuer https://login.acme.io --name "Acme Corp"
auto-authn users add --tenant acme --username alice --email alice@acme.com

# B. register Peagen & new_service
auto-authn clients register acme \
    --client-id peagen-acme \
    --redirect-uris https://app.peagen.io/auth/callback/acme
auto-authn clients register acme \
    --client-id newsvc-acme \
    --redirect-uris https://acme.newsvc.io/auth/callback
```

*The commands print the **client\_secret** once—store it in vault before closing the terminal.*

#### 2 . Rotate signing keys every quarter

```bash
auto-authn tenants rotate-keys --grace $((90*24*3600))   # keep old keys 90 days
```

Relying‑parties will automatically fetch the new public key from
`https://login.<tenant>/jwks.json`.

#### 3 . Emergency user lockout

```bash
auto-authn users deactivate --tenant acme bob
```

Tokens already issued to *bob* remain valid until expiry; new login attempts are rejected.

#### 4 . Client secret compromise

```bash
auto-authn clients rotate-secret acme peagen-acme > new_secret.txt
# update Peagen gateway environment with new secret, then delete temporary file
shred --remove new_secret.txt
```

---

### Command Help

Every command is self‑documenting:

```bash
auto-authn --help                 # global options + groups
auto-authn tenants --help         # group‑level help
auto-authn tenants create --help  # command‑level help & examples
```

`auto-authn` returns non‑zero exit codes on validation errors so it integrates cleanly with CI/CD scripts.
