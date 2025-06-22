import pytest
import toml
from itertools import product

# Replace these imports with the actual locations in your project
from peagen._utils.config_loader import resolve_cfg
import peagen.defaults as defaults


def generate_test_parameters():
    """
    Generate all combinations of:
      - mode (0 = local, 1 = remote)
      - has_host (0/1)
      - config_path (0/1)
      - ov_inline (0/1)
      - ov_file (0/1)
    And compute the expected 'source' based on precedence:
      inline > file > config_path > host > builtin
    """
    params = [
        (
            mode,
            has_host,
            config_path,
            ov_inline,
            ov_file,
            "override_inline"
            if ov_inline
            else "override_file"
            if ov_file
            else "config_path"
            if config_path
            else "host"
            if has_host
            else "builtin",
        )
        for mode, has_host, config_path, ov_inline, ov_file in product((0, 1), repeat=5)
    ]
    return params


@pytest.mark.parametrize(
    "mode, has_host, config_path, ov_inline, ov_file, expected_source",
    generate_test_parameters(),
)
def test_config_precedence(
    tmp_path,
    monkeypatch,
    mode,
    has_host,
    config_path,
    ov_inline,
    ov_file,
    expected_source,
):
    """
    Parameterized test to cover all combinations of:
      - mode: 0 (local) or 1 (remote)
      - has_host: presence of .peagen.toml in working directory (or on server for remote)
      - config_path: user-specified --config file
      - ov_inline: inline JSON override
      - ov_file: file-based JSON override

    Expected outcome (one word) is determined by:
      inline_override > override_file > config_path > host > builtin
    """

    # 1. Monkeypatch built-in defaults to include a 'source' key
    monkeypatch.setattr(defaults, "CONFIG", {"source": "builtin"})

    # 2. Create and switch into a temporary working directory
    cwd = tmp_path / "workspace"
    cwd.mkdir()
    monkeypatch.chdir(cwd)

    # 3. Optionally write a host-level .peagen.toml
    if has_host:
        (cwd / ".peagen.toml").write_text('source = "host"\n', encoding="utf-8")

    # 4. Optionally write a config_path TOML
    if config_path:
        cfg_file = cwd / "custom_config.toml"
        cfg_file.write_text('source = "config_path"\n', encoding="utf-8")

    # 5. Optionally write an override file TOML
    if ov_file:
        override_file_path = cwd / "override_file.toml"
        override_file_path.write_text('source = "override_file"\n', encoding="utf-8")

    # 6. Prepare inline override dict if requested
    inline_dict = {"source": "override_inline"} if ov_inline else None

    # 7. Monkeypatch load_peagen_toml to simulate reading either host or config_path TOML
    def fake_load_peagen_toml(path: str = ".peagen.toml"):
        if config_path:
            # If a --config path is provided, load from the custom file
            return toml.loads((cwd / "custom_config.toml").read_text(encoding="utf-8"))
        if has_host:
            # Otherwise, if host TOML is present, load it
            return toml.loads((cwd / ".peagen.toml").read_text(encoding="utf-8"))
        return {}

    monkeypatch.setattr(
        "peagen._utils.config_loader.load_peagen_toml", fake_load_peagen_toml
    )

    # 8. Build the final override dict by merging file-override then inline-override
    final_override = {}
    if ov_file:
        final_override.update(
            toml.loads((cwd / "override_file.toml").read_text(encoding="utf-8"))
        )
    if ov_inline:
        final_override.update(inline_dict)

    toml_text = final_override if final_override else None

    # 9. Call resolve_cfg() under test
    cfg = resolve_cfg(toml_text=toml_text)

    # 10. Assert that the 'source' key reflects the expected precedence
    assert cfg.get("source") == expected_source, (
        f"Failed for mode={mode}, has_host={has_host}, "
        f"config_path={config_path}, ov_inline={ov_inline}, ov_file={ov_file}. "
        f"Expected 'source' = {expected_source}, but got {cfg.get('source')}"
    )
