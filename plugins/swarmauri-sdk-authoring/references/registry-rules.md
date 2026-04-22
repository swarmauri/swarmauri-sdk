# Registry Rules

Use registry changes only when the new surface must be discoverable through Swarmauri package lookup.

## Interface Registry

Edit `pkgs/swarmauri/swarmauri/interface_registry.py` when adding a new resource namespace or when changing the base interface for a namespace.

- Add a namespace key such as `swarmauri.tools`.
- Map it to the matching base class import path such as `swarmauri_base.tools.ToolBase`.
- Use `None` only for namespaces that intentionally have no validation interface.
- Add or update focused tests in `pkgs/swarmauri/tests/unit/interface_registry_unit_test.py`.

Do not update the interface registry for a core-interface-only addition unless the namespace becomes a new discoverable resource family.

## Citizenship Registry

Edit `pkgs/swarmauri/swarmauri/plugin_citizenship_registry.py` when a component must be visible through a facade resource path.

- `FIRST_CLASS_REGISTRY`: standards packages and built-in `swarmauri_standard` concretes.
- `SECOND_CLASS_REGISTRY`: community packages.
- `THIRD_CLASS_REGISTRY`: generic plugins under `swarmauri.plugins`.

Registry keys use facade resource paths:

```python
"swarmauri.tools.TextLengthTool": "swarmauri_tool_textlength.TextLengthTool"
```

Entry-point groups should match the namespace portion:

```toml
[project.entry-points."swarmauri.tools"]
TextLengthTool = "swarmauri_tool_textlength:TextLengthTool"
```

Add tests for registry rows, duplicate behavior, or entry-point discovery when registry content changes.
