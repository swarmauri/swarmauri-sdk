# Inheritance And Entry Points

Follow local inheritance before inventing a new structure.

## Interfaces

- Core interfaces live in `swarmauri_core`.
- Use `ABC` and `abstractmethod`.
- Keep interface methods typed and behavior-free.

## Base Classes

- Base classes live in `swarmauri_base`.
- Inherit the matching core interface and `ComponentBase`.
- Decorate base models with `@ComponentBase.register_model()`.
- Set `resource` from `ResourceTypes`.
- Set `type: Literal["<BaseName>"] = "<BaseName>"`.

## Mixins

- Prefer the sibling mixin pattern in the same family.
- Mixins commonly inherit a narrow core interface plus `BaseModel`, or another local mixin.
- Avoid `ComponentBase.register_model()` for mixins unless adjacent code already uses it.

## Concretes

- Concretes inherit the matching base class.
- Decorate with `@ComponentBase.register_type(<BaseClass>, "<ConcreteName>")`.
- Set `type: Literal["<ConcreteName>"] = "<ConcreteName>"`.
- Add exports in `__init__.py` when the package exposes sibling concretes.

## Entry Points

Use entry points for install-time discovery:

```toml
[project.entry-points."swarmauri.tools"]
ToolName = "package_name:ToolName"
```

Use `swarmauri.plugins` for generic plugin packages:

```toml
[project.entry-points."swarmauri.plugins"]
plugin_name = "package_name.module:PluginClass"
```

Entry-point group, citizenship registry key, and interface registry namespace must agree when the resource is facade-visible.
