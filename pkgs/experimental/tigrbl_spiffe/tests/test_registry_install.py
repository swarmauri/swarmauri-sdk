from contextlib import contextmanager

from tigrbl_spiffe import register
from tigrbl_spiffe import plugin as plugin_module
from tigrbl_spiffe import registry as registry_module
from tigrbl_spiffe.tables import bundle, registrar, svid, workload


class DummyApp:
    def __init__(self) -> None:
        self.middlewares = []

    def use(self, middleware):
        self.middlewares.append(middleware)


@contextmanager
def override_attr(module, name, replacement):
    original = getattr(module, name)
    setattr(module, name, replacement)
    try:
        yield
    finally:
        setattr(module, name, original)


def test_register_includes_spiffe_tables():
    captured: list[type] = []
    with override_attr(
        registry_module, "include_model", lambda model: captured.append(model)
    ):
        register(app=object())

    assert captured == [
        svid.Svid,
        registrar.Registrar,
        bundle.Bundle,
        workload.Workload,
    ]


def test_plugin_install_wires_models_and_middleware():
    from tigrbl_spiffe.adapters import Endpoint
    from tigrbl_spiffe.middleware.identity import InjectSpiffeExtras
    from tigrbl_spiffe.middleware.authn import SpiffeAuthn
    from tigrbl_spiffe.middleware.tls import AttachTlsContexts
    from tigrbl_spiffe.plugin import TigrblSpiffePlugin

    captured: list[type] = []
    with override_attr(
        plugin_module, "include_model", lambda model: captured.append(model)
    ):
        plugin = TigrblSpiffePlugin(
            workload_endpoint=Endpoint(
                scheme="uds", address="unix:///tmp/workload.sock"
            )
        )
        app = DummyApp()

        plugin.install(app)

    assert captured == [
        svid.Svid,
        registrar.Registrar,
        bundle.Bundle,
        workload.Workload,
    ]

    assert [type(mw) for mw in app.middlewares] == [
        InjectSpiffeExtras,
        SpiffeAuthn,
        AttachTlsContexts,
    ]

    extras = plugin.ctx_extras()
    assert extras["spiffe_adapter"] is not None
    assert extras["rotation_policy"] is not None
    assert extras["svid_validator"] is not None
    assert extras["tls_helper"] is not None
    cfg = extras["spiffe_config"]
    assert cfg.workload_endpoint.scheme == "uds"
    assert cfg.workload_endpoint.address == "unix:///tmp/workload.sock"
