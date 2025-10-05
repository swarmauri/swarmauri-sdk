import base64
import importlib
import json
import sys
import types
from pathlib import Path

import pytest


@pytest.fixture(scope="module")
def cwt_module():
    """Load the CWT module with lightweight stubs for external deps."""

    root = Path(__file__).resolve()
    standards_dir = root.parents[2]
    pkgs_dir = root.parents[3]

    added_paths = []
    core_path = pkgs_dir / "core"
    if str(core_path) not in sys.path:
        sys.path.insert(0, str(core_path))
        added_paths.append(str(core_path))
    if str(standards_dir) not in sys.path:
        sys.path.insert(0, str(standards_dir))
        added_paths.append(str(standards_dir))

    stubs: dict[str, types.ModuleType] = {}

    # Minimal CBOR helpers implemented with JSON for determinism.
    cbor2_mod = types.ModuleType("cbor2")

    def dumps(obj, canonical=False):
        return json.dumps(obj, sort_keys=canonical).encode()

    def loads(data):
        return json.loads(data.decode())

    cbor2_mod.dumps = dumps
    cbor2_mod.loads = loads
    stubs["cbor2"] = cbor2_mod

    # COSE algorithm and message primitives.
    cose_pkg = types.ModuleType("cose")
    cose_pkg.__path__ = []  # type: ignore[attr-defined]
    stubs["cose"] = cose_pkg

    algorithms_mod = types.ModuleType("cose.algorithms")

    class SignatureAlg:
        def __init__(self, name):
            self.name = name

    algorithms_mod.SignatureAlg = SignatureAlg
    stubs["cose.algorithms"] = algorithms_mod

    exceptions_mod = types.ModuleType("cose.exceptions")

    class CoseException(Exception):
        """Stub for COSE exception hierarchy."""

    exceptions_mod.CoseException = CoseException
    stubs["cose.exceptions"] = exceptions_mod

    headers_mod = types.ModuleType("cose.headers")
    headers_mod.Algorithm = "alg"
    headers_mod.KID = "kid"
    stubs["cose.headers"] = headers_mod

    keys_mod = types.ModuleType("cose.keys")

    class CoseKey(dict):
        @classmethod
        def from_dict(cls, data):
            inst = cls()
            inst.update(data)
            return inst

    keys_mod.CoseKey = CoseKey
    stubs["cose.keys"] = keys_mod

    keyparam_mod = types.ModuleType("cose.keys.keyparam")
    keyparam_mod.EC2KpCurve = "ec2_curve"
    keyparam_mod.EC2KpX = "ec2_x"
    keyparam_mod.EC2KpY = "ec2_y"
    keyparam_mod.KpKty = "kty"
    keyparam_mod.OKPKpCurve = "okp_curve"
    keyparam_mod.OKPKpX = "okp_x"
    keyparam_mod.RSAKpE = "rsa_e"
    keyparam_mod.RSAKpN = "rsa_n"
    stubs["cose.keys.keyparam"] = keyparam_mod

    keytype_mod = types.ModuleType("cose.keys.keytype")

    class _BaseKty:
        def __init__(self, identifier):
            self.identifier = identifier

    keytype_mod.KtyEC2 = _BaseKty("EC2")
    keytype_mod.KtyOKP = _BaseKty("OKP")
    keytype_mod.KtyRSA = _BaseKty("RSA")
    stubs["cose.keys.keytype"] = keytype_mod

    messages_mod = types.ModuleType("cose.messages")

    class Sign1Message:
        def __init__(self, phdr, uhdr, payload):
            self.phdr = phdr
            self.uhdr = uhdr
            self.payload = payload
            self.key = None
            self._verify_result = True

        def encode(self):
            return json.dumps({"phdr": self.phdr, "payload": self.payload}).encode()

        def verify_signature(self):
            if isinstance(self._verify_result, Exception):
                raise self._verify_result
            return self._verify_result

        @classmethod
        def decode(cls, _data):
            raise NotImplementedError("tests patch Sign1Message.decode")

    messages_mod.Sign1Message = Sign1Message
    stubs["cose.messages"] = messages_mod

    # Minimal component base used for registration decorators.
    base_component_mod = types.ModuleType("swarmauri_base.ComponentBase")

    class ComponentBase:
        registry: dict[str, type] = {}

        @classmethod
        def register_type(cls, _base, _name):
            def decorator(target):
                return target

            return decorator

    def register_model():
        def decorator(target):
            return target

        return decorator

    base_component_mod.ComponentBase = ComponentBase
    base_component_mod.register_model = register_model
    stubs["swarmauri_base.ComponentBase"] = base_component_mod

    pop_base_mod = types.ModuleType("swarmauri_base.pop")

    class RequestContext:
        def __init__(self, method, htu, policy):
            self.method = method
            self.htu = htu
            self.policy = policy

    class PopVerifierBase:
        def __init__(self, *, kind, header_name, features, algorithms):
            self.kind = kind
            self.header_name = header_name
            self.features = features
            self.algorithms = algorithms

        def _enforce_bind_type(self, *args, **kwargs):  # noqa: D401
            pass

        def _enforce_alg_policy(self, *args, **kwargs):
            pass

        def _validate_iat(self, *args, **kwargs):
            pass

        def _require_ath(self, *args, **kwargs):
            pass

        def _compute_ath(self, _access_token):
            return "computed-ath"

        def _check_replay(self, *args, **kwargs):
            pass

    class PopSigningBase(base_component_mod.ComponentBase):
        def __init__(self, *, kind, header_name, include_query=False):
            self.kind = kind
            self.header_name = header_name
            self.include_query = include_query

        def _base_claims(self, method, url, *, jti=None, ath_b64u=None):
            claims = {"htm": method, "htu": url, "iat": 0}
            if jti is not None:
                claims["jti"] = jti
            if ath_b64u is not None:
                claims["ath"] = ath_b64u
            return claims

        def _merge_claims(self, base, extra):
            merged = dict(base)
            if extra:
                merged.update(extra)
            return merged

    def sha256_b64u(data: bytes) -> str:
        return base64.urlsafe_b64encode(data).rstrip(b"=").decode()

    pop_base_mod.PopSigningBase = PopSigningBase
    pop_base_mod.PopVerifierBase = PopVerifierBase
    pop_base_mod.RequestContext = RequestContext
    pop_base_mod.sha256_b64u = sha256_b64u
    stubs["swarmauri_base.pop"] = pop_base_mod

    previous = {}
    for name, module in stubs.items():
        previous[name] = sys.modules.get(name)
        sys.modules[name] = module

    module = importlib.import_module("swarmauri_pop_cwt.cwt")

    yield module

    for name, module in stubs.items():
        if previous[name] is None:
            sys.modules.pop(name, None)
        else:
            sys.modules[name] = previous[name]

    for path in added_paths:
        if path in sys.path:
            sys.path.remove(path)


class DummyPolicy:
    def __init__(self, *, require_ath=False, max_skew_s=60):
        self.require_ath = require_ath
        self.max_skew_s = max_skew_s


def make_context(cwt, *, require_ath=False):
    return cwt.RequestContext(
        "GET", "https://example.test/resource", DummyPolicy(require_ath=require_ath)
    )


class DummySign1:
    def __init__(self, phdr, payload, verify=True):
        self.phdr = phdr
        self.payload = payload
        self.key = None
        self._verify = verify

    def verify_signature(self):
        if isinstance(self._verify, Exception):
            raise self._verify
        return self._verify


def set_decode(monkeypatch, cwt, message):
    def decode(cls, _data):
        return message

    monkeypatch.setattr(cwt.Sign1Message, "decode", classmethod(decode))


def make_okp_key(cwt):
    curve = types.SimpleNamespace(identifier="Ed25519")
    key = cwt.CoseKey(
        {
            cwt.KpKty: cwt.KtyOKP,
            cwt.OKPKpCurve: curve,
            cwt.OKPKpX: "abc",
        }
    )
    return key


def make_ec2_key(cwt):
    curve = types.SimpleNamespace(identifier="P-256")
    key = cwt.CoseKey(
        {
            cwt.KpKty: cwt.KtyEC2,
            cwt.EC2KpCurve: curve,
            cwt.EC2KpX: "x",
            cwt.EC2KpY: "y",
        }
    )
    return key


def make_rsa_key(cwt):
    key = cwt.CoseKey(
        {
            cwt.KpKty: cwt.KtyRSA,
            cwt.RSAKpN: "n",
            cwt.RSAKpE: "e",
        }
    )
    return key


def build_claims(**overrides):
    claims = {
        "htm": "GET",
        "htu": "https://example.test/resource",
        "iat": 123,
        "jti": "jti-123",
    }
    claims.update(overrides)
    return claims


def make_payload(cwt, claims):
    return cwt.cbor2.dumps(claims, canonical=True)


def build_message(cwt, *, algorithm="ES256", claims=None, verify=True, kid=None):
    phdr = {cwt.Algorithm: cwt.SignatureAlg(algorithm)}
    if kid is not None:
        phdr[cwt.KID] = kid
    payload = make_payload(cwt, claims or build_claims())
    return DummySign1(phdr, payload, verify=verify)


def make_cnf(cwt, value="thumb"):
    return cwt.CnfBinding(cwt.BindType.COSE_THUMB, value)


def make_public_key(cwt):
    return make_ec2_key(cwt)


def setup_thumbprint(monkeypatch, cwt, value="thumb"):
    monkeypatch.setattr(cwt, "_compute_cose_thumbprint", lambda _key: value)


def run_verify(verifier, proof, context, cnf, *, replay=None, keys=None, extras=None):
    if replay is None:
        replay = object()
    if extras is None:
        extras = {}
    return verifier._verify_core(
        proof, context, cnf, replay=replay, keys=keys, extras=extras
    )


def test_b64u_decode_handles_missing_padding(cwt_module):
    assert cwt_module._b64u_decode("YQ") == b"a"


def test_ensure_cose_key_returns_existing_instance(cwt_module):
    key = cwt_module.CoseKey()
    assert cwt_module._ensure_cose_key(key) is key


def test_ensure_cose_key_accepts_mapping(monkeypatch, cwt_module):
    seen = {}

    def fake_from_dict(cls, data):
        seen["data"] = data
        inst = cls()
        inst.update(data)
        return inst

    monkeypatch.setattr(cwt_module.CoseKey, "from_dict", classmethod(fake_from_dict))

    mapping = {"a": "b"}
    result = cwt_module._ensure_cose_key(mapping)
    assert dict(result) == mapping
    assert seen["data"] == mapping


def test_ensure_cose_key_rejects_invalid_input(cwt_module):
    with pytest.raises(TypeError):
        cwt_module._ensure_cose_key(123)


def test_compute_thumbprint_okp(monkeypatch, cwt_module):
    captured = {}

    def fake_sha(data):
        captured["data"] = data
        return "thumb"

    monkeypatch.setattr(cwt_module, "sha256_b64u", fake_sha)
    key = make_okp_key(cwt_module)
    result = cwt_module._compute_cose_thumbprint(key)
    assert result == "thumb"
    assert json.loads(captured["data"].decode()) == {
        "-2": "abc",
        "-1": "Ed25519",
        "1": "OKP",
    }


def test_compute_thumbprint_ec2(monkeypatch, cwt_module):
    captured = {}
    monkeypatch.setattr(
        cwt_module,
        "sha256_b64u",
        lambda data: captured.setdefault("data", data) or "thumb",
    )
    key = make_ec2_key(cwt_module)
    cwt_module._compute_cose_thumbprint(key)
    assert json.loads(captured["data"].decode()) == {
        "-3": "y",
        "-2": "x",
        "-1": "P-256",
        "1": "EC2",
    }


def test_compute_thumbprint_rsa(monkeypatch, cwt_module):
    captured = {}
    monkeypatch.setattr(
        cwt_module,
        "sha256_b64u",
        lambda data: captured.setdefault("data", data) or "thumb",
    )
    key = make_rsa_key(cwt_module)
    cwt_module._compute_cose_thumbprint(key)
    assert json.loads(captured["data"].decode()) == {"-2": "e", "-1": "n", "1": "RSA"}


def test_compute_thumbprint_rejects_unknown_type(cwt_module):
    class Unknown:
        identifier = "mystery"

    key = cwt_module.CoseKey({cwt_module.KpKty: Unknown()})
    with pytest.raises(cwt_module.PoPParseError):
        cwt_module._compute_cose_thumbprint(key)


def test_alg_name_prefers_attribute(cwt_module):
    alg = cwt_module.SignatureAlg("ES256")
    assert cwt_module._alg_name(alg) == "ES256"


def test_alg_name_falls_back_to_string(cwt_module):
    class NoName:
        def __str__(self):
            return "alg"

    assert cwt_module._alg_name(NoName()) == "alg"


@pytest.mark.asyncio
async def test_verify_rejects_invalid_cwt_payload(monkeypatch, cwt_module):
    verifier = cwt_module.CwtPoPVerifier()
    context = make_context(cwt_module)
    cnf = make_cnf(cwt_module)

    def bad_decode(cls, _data):
        raise ValueError("boom")

    monkeypatch.setattr(cwt_module.Sign1Message, "decode", classmethod(bad_decode))

    with pytest.raises(cwt_module.PoPParseError):
        await run_verify(verifier, "cHJvb2Y", context, cnf)


@pytest.mark.asyncio
async def test_verify_requires_algorithm_header(monkeypatch, cwt_module):
    verifier = cwt_module.CwtPoPVerifier()
    context = make_context(cwt_module)
    cnf = make_cnf(cwt_module)
    message = DummySign1({}, make_payload(cwt_module, build_claims()))
    set_decode(monkeypatch, cwt_module, message)

    with pytest.raises(cwt_module.PoPParseError):
        await run_verify(verifier, "cHJvb2Y", context, cnf)


@pytest.mark.asyncio
async def test_verify_enforces_algorithm_policy(monkeypatch, cwt_module):
    verifier = cwt_module.CwtPoPVerifier()
    context = make_context(cwt_module)
    cnf = make_cnf(cwt_module, value="good-thumb")
    setup_thumbprint(monkeypatch, cwt_module, "good-thumb")
    message = build_message(cwt_module)
    set_decode(monkeypatch, cwt_module, message)

    called = {}

    def enforce(self, alg, policy):
        called["alg"] = alg
        called["policy"] = policy

    monkeypatch.setattr(verifier, "_enforce_alg_policy", enforce.__get__(verifier))

    extras = {"public_cose_key": make_public_key(cwt_module)}
    await run_verify(verifier, "cHJvb2Y", context, cnf, extras=extras)
    assert called["alg"] == "ES256"
    assert called["policy"] is context.policy


@pytest.mark.asyncio
async def test_verify_requires_key(monkeypatch, cwt_module):
    verifier = cwt_module.CwtPoPVerifier()
    context = make_context(cwt_module)
    cnf = make_cnf(cwt_module)
    setup_thumbprint(monkeypatch, cwt_module, cnf.value_b64u)
    message = build_message(cwt_module)
    set_decode(monkeypatch, cwt_module, message)

    class Resolver:
        def by_kid(self, _kid):
            return None

        def by_thumb(self, _cnf):
            return None

    with pytest.raises(cwt_module.PoPVerificationError):
        await run_verify(verifier, "cHJvb2Y", context, cnf, keys=Resolver(), extras={})


@pytest.mark.asyncio
async def test_verify_detects_thumb_mismatch(monkeypatch, cwt_module):
    verifier = cwt_module.CwtPoPVerifier()
    context = make_context(cwt_module)
    cnf = make_cnf(cwt_module, value="expected")
    setup_thumbprint(monkeypatch, cwt_module, "other")
    message = build_message(cwt_module)
    set_decode(monkeypatch, cwt_module, message)
    extras = {"public_cose_key": make_public_key(cwt_module)}

    with pytest.raises(cwt_module.PoPBindingError):
        await run_verify(verifier, "cHJvb2Y", context, cnf, extras=extras)


@pytest.mark.asyncio
async def test_verify_detects_signature_failure(monkeypatch, cwt_module):
    verifier = cwt_module.CwtPoPVerifier()
    context = make_context(cwt_module)
    cnf = make_cnf(cwt_module, value="expected")
    setup_thumbprint(monkeypatch, cwt_module, "expected")
    message = build_message(cwt_module, verify=False)
    set_decode(monkeypatch, cwt_module, message)
    extras = {"public_cose_key": make_public_key(cwt_module)}

    with pytest.raises(cwt_module.PoPVerificationError):
        await run_verify(verifier, "cHJvb2Y", context, cnf, extras=extras)


@pytest.mark.asyncio
async def test_verify_wraps_signature_exception(monkeypatch, cwt_module):
    verifier = cwt_module.CwtPoPVerifier()
    context = make_context(cwt_module)
    cnf = make_cnf(cwt_module, value="expected")
    setup_thumbprint(monkeypatch, cwt_module, "expected")
    message = build_message(cwt_module, verify=cwt_module.CoseException("bad"))
    set_decode(monkeypatch, cwt_module, message)
    extras = {"public_cose_key": make_public_key(cwt_module)}

    with pytest.raises(cwt_module.PoPVerificationError):
        await run_verify(verifier, "cHJvb2Y", context, cnf, extras=extras)


@pytest.mark.asyncio
async def test_verify_rejects_invalid_cbor(monkeypatch, cwt_module):
    verifier = cwt_module.CwtPoPVerifier()
    context = make_context(cwt_module)
    cnf = make_cnf(cwt_module)
    setup_thumbprint(monkeypatch, cwt_module, cnf.value_b64u)
    message = build_message(cwt_module)
    set_decode(monkeypatch, cwt_module, message)
    monkeypatch.setattr(
        cwt_module.cbor2,
        "loads",
        lambda _data: (_ for _ in ()).throw(ValueError("bad")),
    )
    extras = {"public_cose_key": make_public_key(cwt_module)}

    with pytest.raises(cwt_module.PoPParseError):
        await run_verify(verifier, "cHJvb2Y", context, cnf, extras=extras)


@pytest.mark.asyncio
async def test_verify_rejects_htm_mismatch(monkeypatch, cwt_module):
    verifier = cwt_module.CwtPoPVerifier()
    context = make_context(cwt_module)
    cnf = make_cnf(cwt_module)
    setup_thumbprint(monkeypatch, cwt_module, cnf.value_b64u)
    claims = build_claims(htm="POST")
    message = build_message(cwt_module, claims=claims)
    set_decode(monkeypatch, cwt_module, message)
    extras = {"public_cose_key": make_public_key(cwt_module)}

    with pytest.raises(cwt_module.PoPVerificationError):
        await run_verify(verifier, "cHJvb2Y", context, cnf, extras=extras)


@pytest.mark.asyncio
async def test_verify_rejects_htu_mismatch(monkeypatch, cwt_module):
    verifier = cwt_module.CwtPoPVerifier()
    context = make_context(cwt_module)
    cnf = make_cnf(cwt_module)
    setup_thumbprint(monkeypatch, cwt_module, cnf.value_b64u)
    claims = build_claims(htu="https://example.test/other")
    message = build_message(cwt_module, claims=claims)
    set_decode(monkeypatch, cwt_module, message)
    extras = {"public_cose_key": make_public_key(cwt_module)}

    with pytest.raises(cwt_module.PoPVerificationError):
        await run_verify(verifier, "cHJvb2Y", context, cnf, extras=extras)


@pytest.mark.asyncio
async def test_verify_requires_integer_iat(monkeypatch, cwt_module):
    verifier = cwt_module.CwtPoPVerifier()
    context = make_context(cwt_module)
    cnf = make_cnf(cwt_module)
    setup_thumbprint(monkeypatch, cwt_module, cnf.value_b64u)
    claims = build_claims(iat="not-int")
    message = build_message(cwt_module, claims=claims)
    set_decode(monkeypatch, cwt_module, message)
    extras = {"public_cose_key": make_public_key(cwt_module)}

    with pytest.raises(cwt_module.PoPParseError):
        await run_verify(verifier, "cHJvb2Y", context, cnf, extras=extras)


@pytest.mark.asyncio
async def test_verify_requires_string_jti(monkeypatch, cwt_module):
    verifier = cwt_module.CwtPoPVerifier()
    context = make_context(cwt_module)
    cnf = make_cnf(cwt_module)
    setup_thumbprint(monkeypatch, cwt_module, cnf.value_b64u)
    claims = build_claims(jti="")
    message = build_message(cwt_module, claims=claims)
    set_decode(monkeypatch, cwt_module, message)
    extras = {"public_cose_key": make_public_key(cwt_module)}

    with pytest.raises(cwt_module.PoPParseError):
        await run_verify(verifier, "cHJvb2Y", context, cnf, extras=extras)


@pytest.mark.asyncio
async def test_verify_detects_nonce_mismatch(monkeypatch, cwt_module):
    verifier = cwt_module.CwtPoPVerifier()
    context = make_context(cwt_module)
    cnf = make_cnf(cwt_module)
    setup_thumbprint(monkeypatch, cwt_module, cnf.value_b64u)
    claims = build_claims(nonce="different")
    message = build_message(cwt_module, claims=claims)
    set_decode(monkeypatch, cwt_module, message)
    extras = {"public_cose_key": make_public_key(cwt_module), "nonce": "expected"}

    with pytest.raises(cwt_module.PoPVerificationError):
        await run_verify(verifier, "cHJvb2Y", context, cnf, extras=extras)


@pytest.mark.asyncio
async def test_verify_checks_ath_when_optional(monkeypatch, cwt_module):
    verifier = cwt_module.CwtPoPVerifier()
    context = make_context(cwt_module)
    cnf = make_cnf(cwt_module)
    setup_thumbprint(monkeypatch, cwt_module, cnf.value_b64u)
    claims = build_claims(ath="mismatch")
    message = build_message(cwt_module, claims=claims)
    set_decode(monkeypatch, cwt_module, message)

    def compute_ath(_self, token):
        return "expected"

    monkeypatch.setattr(verifier, "_compute_ath", compute_ath.__get__(verifier))
    extras = {"public_cose_key": make_public_key(cwt_module), "access_token": "token"}

    with pytest.raises(cwt_module.PoPVerificationError):
        await run_verify(verifier, "cHJvb2Y", context, cnf, extras=extras)


@pytest.mark.asyncio
async def test_verify_requires_ath_when_policy_demands(monkeypatch, cwt_module):
    verifier = cwt_module.CwtPoPVerifier()
    context = make_context(cwt_module, require_ath=True)
    cnf = make_cnf(cwt_module)
    setup_thumbprint(monkeypatch, cwt_module, cnf.value_b64u)
    claims = build_claims(ath="value")
    message = build_message(cwt_module, claims=claims)
    set_decode(monkeypatch, cwt_module, message)

    called = {}

    def require(self, *, ath_claim, policy, extras):
        called["ath_claim"] = ath_claim
        called["policy"] = policy
        called["extras"] = extras

    monkeypatch.setattr(verifier, "_require_ath", require.__get__(verifier))
    extras = {"public_cose_key": make_public_key(cwt_module)}

    await run_verify(verifier, "cHJvb2Y", context, cnf, extras=extras)
    assert called["ath_claim"] == "value"
    assert called["policy"] is context.policy
    assert called["extras"] is extras


@pytest.mark.asyncio
async def test_verify_success_checks_replay(monkeypatch, cwt_module):
    verifier = cwt_module.CwtPoPVerifier()
    context = make_context(cwt_module)
    cnf = make_cnf(cwt_module, value="thumb")
    setup_thumbprint(monkeypatch, cwt_module, "thumb")
    claims = build_claims(nonce="nonce", ath="token-ath")
    message = build_message(cwt_module, claims=claims)
    set_decode(monkeypatch, cwt_module, message)

    replay_calls = {}

    def check(self, *, replay, scope, key, ttl_s):
        replay_calls["scope"] = scope
        replay_calls["key"] = key
        replay_calls["ttl_s"] = ttl_s
        replay_calls["replay"] = replay

    monkeypatch.setattr(verifier, "_check_replay", check.__get__(verifier))

    def compute_ath(self, token):
        return "token-ath"

    monkeypatch.setattr(verifier, "_compute_ath", compute_ath.__get__(verifier))
    extras = {
        "public_cose_key": make_public_key(cwt_module),
        "nonce": "nonce",
        "access_token": "token",
    }
    replay = object()

    await run_verify(verifier, "cHJvb2Y", context, cnf, extras=extras, replay=replay)
    assert replay_calls == {
        "scope": f"cwt:{context.htu}",
        "key": "jti-123",
        "ttl_s": context.policy.max_skew_s,
        "replay": replay,
    }


def test_signer_cnf_binding_uses_thumbprint(monkeypatch, cwt_module):
    private = make_okp_key(cwt_module)
    public = make_okp_key(cwt_module)
    monkeypatch.setattr(cwt_module, "_compute_cose_thumbprint", lambda key: "thumb")
    signer = cwt_module.CwtPoPSigner(
        private_key=private,
        public_key=public,
        algorithm=cwt_module.SignatureAlg("EdDSA"),
    )
    binding = signer.cnf_binding()
    assert binding.bind_type == cwt_module.BindType.COSE_THUMB
    assert binding.value_b64u == "thumb"


def test_sign_request_builds_message(monkeypatch, cwt_module):
    private = make_okp_key(cwt_module)
    public = make_okp_key(cwt_module)
    thumbprints = {"value": "thumb"}

    def compute_thumb(key):
        thumbprints["key"] = key
        return thumbprints["value"]

    monkeypatch.setattr(cwt_module, "_compute_cose_thumbprint", compute_thumb)
    signer = cwt_module.CwtPoPSigner(
        private_key=private,
        public_key=public,
        algorithm=cwt_module.SignatureAlg("ES256"),
    )

    created = {}

    class RecordingMessage:
        instances = []

        def __init__(self, phdr, uhdr, payload):
            created["phdr"] = phdr
            created["uhdr"] = uhdr
            created["payload"] = payload
            self.key = None

        def encode(self):
            return b"encoded"

    monkeypatch.setattr(cwt_module, "Sign1Message", RecordingMessage)
    token = signer.sign_request(
        "GET",
        "https://example.test/resource",
        kid=b"kid",
        jti="jti",
        ath_b64u="ath",
        extra_claims={"nonce": "abc"},
    )
    assert token == base64.urlsafe_b64encode(b"encoded").rstrip(b"=").decode()
    assert created["phdr"] == {
        cwt_module.Algorithm: signer._algorithm,
        cwt_module.KID: b"kid",
    }
    payload = cwt_module.cbor2.loads(created["payload"])
    assert payload["htm"] == "GET"
    assert payload["htu"] == "https://example.test/resource"
    assert payload["jti"] == "jti"
    assert payload["ath"] == "ath"
    assert payload["nonce"] == "abc"
    assert created["uhdr"] == {}


def test_sign_request_uses_thumbprint_binding(monkeypatch, cwt_module):
    private = make_okp_key(cwt_module)
    public = make_okp_key(cwt_module)
    monkeypatch.setattr(cwt_module, "_compute_cose_thumbprint", lambda key: "thumb")
    signer = cwt_module.CwtPoPSigner(
        private_key=private,
        public_key=public,
        algorithm=cwt_module.SignatureAlg("ES256"),
    )
    assert signer._thumbprint == "thumb"
    assert isinstance(signer._private_key, cwt_module.CoseKey)
    assert isinstance(signer._public_key, cwt_module.CoseKey)
