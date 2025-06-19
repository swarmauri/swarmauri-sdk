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
exported for common prefixes such as :data:`RUN_REF` and
:data:`PROMOTED_REF`.

When fetching a workspace, a ``workspace_uri`` beginning with
``git+`` will be cloned to the destination directory. Both branches and
SHA identifiers are supported via ``git+<url>@<ref>``.

Git filters store artifacts outside the repository. Run ``peagen init filter``
to set up ``clean`` and ``smudge`` scripts and record the filter URI in
``.peagen.toml``. Built‑in filters include ``file://`` and ``s3://`` via
``S3FSFilter``.

Additional helpers let tasks create branches (``fan_out``), move refs
(``promote``), apply tags, or reset a working tree with ``clean_reset``.

Example::

    peagen init filter s3://mybucket

You can also run ``peagen dx filter`` as a quick shortcut::

    peagen dx filter s3://mybucket

To enable the filter manually in an existing repository use the
following snippet::

    with r.config_writer() as cw:
        s = 'filter "minio-oid"'
        cw.set_value(s, "clean", clean_cmd)
        cw.set_value(s, "smudge", smudge_cmd)
        cw.set_value(s, "required", "true")
    (REPO_DIR / ".gitattributes").write_text(
        "workspace/** filter=minio-oid diff=minio-oid\n"
        "workspace/artifacts/** -filter -diff\n"
    )

The ``init project`` command accepts ``--git-remote`` to set an origin
URL during repository creation and ``--filter-uri`` to configure the
default filter in the generated ``.peagen.toml``.

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
