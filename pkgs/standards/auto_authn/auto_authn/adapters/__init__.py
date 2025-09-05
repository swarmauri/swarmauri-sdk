# auto_authn/v2/adapters/__init__.py
def __getattr__(name):
    if name == "RemoteAuthNAdapter":
        from .remote_adapter import RemoteAuthNAdapter

        return RemoteAuthNAdapter
    if name == "LocalAuthNAdapter":
        from .local_adapter import LocalAuthNAdapter

        return LocalAuthNAdapter
    raise AttributeError(name)


__all__ = ["LocalAuthNAdapter", "RemoteAuthNAdapter"]
