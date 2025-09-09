import logging

# tigrbl/v3/bindings/columns.py
from sqlalchemy import Column
from ..specs import ColumnSpec, is_virtual

logger = logging.getLogger("uvicorn")
logger.debug("Loaded module v3/bindings/columns")


def build_and_attach(model: type, specs=None, only_keys=None):
    cols = {}
    for name, attr in list(model.__dict__.items()):
        if not isinstance(attr, ColumnSpec):
            continue
        if is_virtual(attr):
            cols[name] = attr
            continue

        st = attr.storage
        # Ensure type instantiation
        col_type = st.type_
        if isinstance(col_type, type):
            # Special case UUID/Enum
            if col_type.__name__ == "UUID":
                col_type = col_type(as_uuid=True)
            elif col_type.__name__ == "Enum":
                raise RuntimeError("Use SAEnum(enum_cls) not bare Enum class")
            else:
                col_type = col_type()

        col = Column(
            col_type,
            primary_key=st.primary_key,
            nullable=st.nullable,
            unique=st.unique,
            index=st.index,
            autoincrement=st.autoincrement,
            default=st.default,
            onupdate=st.onupdate,
            server_default=st.server_default,
            comment=st.comment,
        )
        setattr(model, name, col)
        cols[name] = attr

    # register map for later (your Key already has one, but ensure default)
    if not hasattr(model, "__tigrbl_cols__"):
        model.__tigrbl_cols__ = cols
