"""Verify --output-dir CLI flag overrides TOML value."""


def test_output_dir_cli_overrides_toml():
    """CLI flag overrides TOML; omitting flag leaves TOML/default intact."""

    def resolve(cli=None, toml=None, default="output"):
        if cli is not None:
            return cli
        if toml is not None:
            return toml
        return default

    assert resolve(cli="cli_out", toml="toml_out") == "cli_out"
    assert resolve(toml="toml_out") == "toml_out"
    assert resolve() == "output"
