# Git VCS Integration

Peagen can store and manage artifacts inside a Git repository. The
:mod:`peagen.plugins.vcs` package exposes a small helper class
:class:`GitVCS` which wraps the `git` Python bindings. A default instance
is created via the ``vcs`` plugin group.

```python
from peagen.plugins.vcs import GitVCS, pea_ref, RUN_REF

# open or create a repository locally
vcs = GitVCS.ensure_repo("./repo")
# clone a remote repository if needed
vcs_remote = GitVCS.ensure_repo("./repo", remote_url="https://github.com/org/repo.git")
vcs.commit(["results.json"], "initial result")
run_ref = pea_ref("run", "exp-a")
vcs.tag(run_ref)
```

Git references follow the ``refs/pea/<kind>`` convention. Constants are
exported for common prefixes such as :data:`RUN_REF`, :data:`PROMOTED_REF`,
and :data:`KEY_AUDIT_REF`.

When fetching content from Git, a ``git+`` URL will be cloned to the
destination directory. Both branches and commit SHAs are supported via
``git+<url>@<ref>``.

Git filters store artifacts outside the repository. Run ``peagen init filter``
to write ``clean`` and ``smudge`` helpers. Pass ``--add-config`` to also store
the filter URI in ``.peagen.toml``. Built‑in filters include ``s3://`` via
``S3FSFilter`` and ``MinioFilter`` for MinIO endpoints.

Additional helpers let tasks create branches (``fan_out``), move refs
(``promote``), apply tags, or reset a working tree with ``clean_reset``.

Example::

    peagen init filter s3://mybucket

If no URI is provided the command defaults to ``s3://peagen`` using ``S3FSFilter``.
To enable the filter manually in an existing repository use the
following snippet::

    with r.config_writer() as cw:
        s = 'filter "minio-oid"'
        cw.set_value(s, "clean", clean_cmd)
        cw.set_value(s, "smudge", smudge_cmd)
        cw.set_value(s, "required", "true")
    (REPO_DIR / ".gitattributes").write_text(
        "peagen/** filter=minio-oid diff=minio-oid\n"
        "artifacts/** -filter -diff\n"
    )

The ``init project`` command accepts ``--git-remote`` to set an origin
URL during repository creation and ``--filter-uri`` to initialise a
filter. Use ``--add-filter-config`` to also write the URI to the
generated ``.peagen.toml``.

Existing projects can specify a remote in the configuration file:

```toml
[vcs]
provider = "git"
provider_params = { path = ".", remote_url = "git@github.com:tenant/repo.git" }
```

``peagen init repo`` can create a GitHub repository for you. Pass the
target as ``tenant/repo`` (where ``tenant`` is a user or organisation)
and supply a personal access token. The command also generates an
Ed25519 deploy key and registers it with the new repo so tasks can push
results via SSH.

Peagen tasks use the VCS when available. DOE expansions and Evolve jobs
create branches for each spawned run, allowing easy inspection of
intermediate results. The ``vcs`` plugin can also commit generated
files automatically.

When a repository is cloned via :class:`GitVCS`, the ``origin`` remote is
configured to fetch and push all ``refs/pea/*`` references automatically:

```
with r.config_writer() as cw:
    cw.set_value('remote "origin"', 'fetch', '+refs/pea/*:refs/pea/*')
    cw.set_value('remote "origin"', 'push', 'refs/pea/*:refs/pea/*')
```

## Using `peagen login` with a GitHub PAT

Follow these steps when your repository lives on GitHub and Peagen tasks should
push results back to it.

1. **Create the repository and deploy key** – use the ``init repo`` command with
   a personal access token. The token can be provided via ``--pat`` or the
   ``GITHUB_PAT`` environment variable.

   ```bash
   peagen init repo myuser/myrepo --pat $GITHUB_PAT
   ```

   This calls the GitHub API, creates an Ed25519 key pair and registers the
   public key as a deploy key so the CLI can push via SSH.

2. **Authenticate with the gateway** – upload the same public key so the gateway
   can verify your requests.

   ```bash
   peagen login --gateway-url https://gw.peagen.com
   ```

   After logging in you can run remote commands that operate on the GitHub
   repository, for example:

   ```bash
   peagen remote --gateway-url https://gw.peagen.com process projects.yaml
  ```

   The deploy key handles Git operations while the login step allows the
   gateway to store task results securely.

   !!! note
       After logging in, the CLI refuses to transmit GitHub PAT tokens to the
       gateway for any other command. Only `peagen init repo` may send a PAT so
       all subsequent operations rely exclusively on deploy keys.
