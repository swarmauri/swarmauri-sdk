"""Optional per-model op registry compatibility shim."""


def get_registered_ops(model):
    del model
    return ()


__all__ = ["get_registered_ops"]
