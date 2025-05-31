# `peagen plugin`

Manage Peagen plugin distributions.

## list

```console
peagen plugin list [-v]
```

Lists discovered plugins grouped by entry-point type. Use `-v` to also show the owning distribution.

## install

```console
peagen plugin install PKG|WHEEL|DIR [OPTIONS]
```

Install a plugin package from PyPI, a wheel/sdist file or a local directory. When installing from a directory you can use `--editable` to install in editable mode.

### Options

* `-e`, `--editable` – Install a local directory in editable mode.
* `--force` – Re-install even if the package is already installed.
* `-v`, `--verbose` – Show pip/uv output.

## remove

```console
peagen plugin remove PACKAGE [OPTIONS]
```

Uninstall a plugin distribution by its package name.

### Options

* `-y`, `--yes` – Skip confirmation prompt.
* `-v`, `--verbose` – Show pip/uv output.
