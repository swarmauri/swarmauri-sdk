# Column Specs

Tigrbl columns are declared with helper functions like `acol` and `vcol`.
Each column is driven by three smaller specs that describe how the value is
stored, validated, and exposed. These specs keep column behaviour
consistent across the ORM, schema generation, and the runtime API.

## StorageSpec (`S`)
Describes the database shape and storage behaviour.

- `type_` – SQLAlchemy column type.
- `nullable`, `unique`, `index`, `primary_key`, `autoincrement`.
- Defaults and generation: `default`, `onupdate`, `server_default`,
  `refresh_on_return`.
- Optional helpers: `transform`, `fk`, `check`, `comment`.

## FieldSpec (`F`)
Captures Pydantic metadata and request policy.

- `py_type` – Python type, inferred when omitted.
- `constraints` – passed to `pydantic.Field` for validation.
- `required_in` / `allow_null_in` – control required and nullable verbs.

## IOSpec (`IO`)
Controls API exposure and advanced value handling.

- `in_verbs` / `out_verbs` – verbs that accept or emit the value.
- `mutable_verbs` – verbs allowed to change the value.
- `alias_in` / `alias_out` – alternative field names.
- `sensitive`, `redact_last` – masking and redaction options.
- `filter_ops`, `sortable` – enable filtering and sorting.
- Helpers: `assemble`, `paired`, `alias_readtime` for computed aliases.

## ColumnSpec
`ColumnSpec` ties the three specs together and adds runtime helpers such as
`default_factory` and `read_producer`.

```python
from tigrbl.column import acol, vcol, F, IO, S

class Widget(Base):
    __tablename__ = "widgets"

    id: Mapped[int] = acol(storage=S(primary_key=True))
    name: Mapped[str] = acol(
        field=F(constraints={"max_length": 50}),
        storage=S(nullable=False, index=True),
        io=IO(
            in_verbs=("create", "update"),
            out_verbs=("read", "list"),
            sortable=True,
        ),
    )
    checksum: Mapped[str] = vcol(
        field=F(),
        io=IO(out_verbs=("read",)),
        read_producer=lambda obj, ctx: f"{obj.name}:{obj.id}",
    )
```

For additional background see the "Column-Level Configuration" section in the
parent [README](../README.md).
