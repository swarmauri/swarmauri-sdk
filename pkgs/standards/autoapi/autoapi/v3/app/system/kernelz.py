from __future__ import annotations

from autoapi.v3.runtime.kernel import _default_kernel as K


def build_kernelz_endpoint(app):
    # Autoprime under the hood; downstream users never see Kernel.
    K.ensure_primed(app)

    async def _kernelz():
        return K.kernelz_payload(app)  # cached, endpoint-ready

    return _kernelz
