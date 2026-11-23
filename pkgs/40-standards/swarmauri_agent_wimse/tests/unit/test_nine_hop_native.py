"""Exercise all nine B_CHAIN hops over an in-process request transport."""

from base64 import b64encode, urlsafe_b64encode
from dataclasses import dataclass
from hashlib import sha256
import json
import re
from time import time
from unittest.mock import Mock
from urllib.parse import urlsplit
from uuid import uuid4

from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
import pytest
from swarmauri_standard.agents.SimpleConversationAgent import (
    SimpleConversationAgent,
)
from swarmauri_standard.conversations.Conversation import Conversation
from swarmauri_standard.llms.OpenAIModel import OpenAIModel
from swarmauri_standard.messages.AgentMessage import AgentMessage
from swarmauri_standard.tool_llms.OpenAIToolModel import OpenAIToolModel
from tba_concrete_jwt import decode_jwt_unverified
from tba_profile_workload_credential_wimse_wit import issue_wit
from tba_profile_workload_proof_wimse_http_signature.request import (
    FIELDS,
    _sign_request,
)
from tba_provider_jose_cryptography.jws import (
    JwsCryptographyProvider,
    sign_compact_jwt,
)
from tba_provider_jose_cryptography.public_jws import verify_public_jws

from swarmauri_agent_wimse import (
    FileToolEndpoint,
    ResearchAgentEndpoint,
    TransactionPolicy,
    WimseIngressEndpoint,
)
from swarmauri_agent_wimse.proof import (
    Rejected,
    ReplayCache,
    headers_dict,
    produce_wpt,
    verify_http,
    verify_wpt,
)


DOMAIN_A = "https://domain-a.example"
DOMAIN_B = "https://domain-b.example"
INGRESS_ORIGIN = "https://ingress.example"
COORDINATOR_ORIGIN = "https://coordinator.example"
RESEARCH_ORIGIN = "https://research.example"
FILE_ORIGIN = "https://files.example"

CLIENT = "wimse://domain-a.example/client"
COORDINATOR = "wimse://domain-b.example/coordinator"
RESEARCH = "wimse://domain-b.example/research"
FILE = "Q3.pdf"
DOCUMENT = "Quarterly revenue was $4.2M."
READ_SCOPE = "files:read"
RESEARCH_SCOPE = "research:summarize files:read"

TOKEN_A = DOMAIN_A + "/tts/token"
EXCHANGE_A = DOMAIN_A + "/oauth/token"
EXCHANGE_B = DOMAIN_B + "/oauth/token"
TOKEN_B = DOMAIN_B + "/tts/token"
INGRESS = INGRESS_ORIGIN + "/workflows/text-stats/executions"
COORDINATE = COORDINATOR_ORIGIN + "/coordinate"
RESEARCH_URL = RESEARCH_ORIGIN + "/research"
READ_FILE = FILE_ORIGIN + "/files/read"


class LocalRequests:
    """Dispatch serialized requests and record nested hops in arrival order."""

    def __init__(self):
        self.routes = {}
        self.trace = []

    def send(self, url, data, headers=None):
        record = [url, None]
        self.trace.append(record)
        body = json.dumps(data).encode("utf-8")
        fields = {"content-type": "application/json", **(headers or {})}
        try:
            result = self.routes[url](urlsplit(url).path, fields.items(), body)
        except Rejected as error:
            status, result = error.status, {"error": str(error)}
        else:
            status = 200
        record[1] = status
        return status, result

    def post_json(self, url, data, headers=None):
        status, result = self.send(url, data, headers)
        assert status == 200, (url, status, result)
        return result


def public_jwk(key, kid):
    return {
        "kid": kid,
        "alg": "EdDSA",
        "kty": "OKP",
        "crv": "Ed25519",
        "x": urlsafe_b64encode(key.public_key().public_bytes_raw())
        .rstrip(b"=")
        .decode("ascii"),
    }


class Issuer:
    """Issue short-lived fixture tokens using a fresh asymmetric key."""

    def __init__(self, issuer):
        self.issuer = issuer
        key = Ed25519PrivateKey.generate()
        self.jwk = public_jwk(key, issuer)
        self.signer = JwsCryptographyProvider({issuer: key})

    def issue(self, kind, audience, transaction, *, workload, scope):
        now = int(time())
        return sign_compact_jwt(
            self.signer,
            {
                **{key: transaction[key] for key in ("txn", "sub", "tctx")},
                "iss": self.issuer,
                "aud": audience,
                "iat": now,
                "exp": now + 120,
                "scope": scope,
                "req_wl": workload,
            },
            headers={"alg": "EdDSA", "kid": self.issuer, "typ": kind},
            key_reference=self.issuer,
        )

    def claims(self, token, kind, audience, *, workload, scope):
        verify_public_jws(token, self.jwk)
        decoded = decode_jwt_unverified(token)
        claims = decoded.claims
        assert decoded.jws.protected_headers["typ"] == kind
        assert claims["iss"] == self.issuer and claims["aud"] == audience
        assert claims["iat"] <= time() < claims["exp"]
        assert claims["req_wl"] == workload and claims["scope"] == scope
        return claims


@dataclass
class Workload:
    subject: str
    key: Ed25519PrivateKey
    wit: str

    @classmethod
    def create(cls, subject, issuer):
        key = Ed25519PrivateKey.generate()
        now = int(time())
        wit = issue_wit(
            issuer.signer,
            subject=subject,
            confirmation_jwk=public_jwk(key, subject),
            issuer_key_reference=issuer.issuer,
            issuer_key_id=issuer.issuer,
            issuer_algorithm="EdDSA",
            issued_at=now,
            expires_at=now + 120,
        )
        return cls(subject, key, wit)

    @property
    def signer(self):
        return JwsCryptographyProvider({self.subject: self.key})

    def http_headers(self, url, data, **headers):
        target = urlsplit(url)
        body = json.dumps(data).encode("utf-8")
        digest = b64encode(sha256(body).digest()).decode("ascii")
        # The public TbA profile signs bodyless requests. Match the SDK's
        # JSON profile extension by covering Content-Digest and Content-Type.
        return _sign_request(
            self.key,
            self.wit,
            "POST",
            target.path,
            int(time()),
            extra_headers={
                "content-type": "application/json",
                "content-digest": f"sha-256=:{digest}:",
                **headers,
            },
            authority=None,
            derived=FIELDS,
            binding="wimse-aud",
            value=f"{target.scheme}://{target.netloc}",
        )

    def file_headers(self, token, audience=FILE_ORIGIN):
        return produce_wpt(
            self.wit,
            token,
            audience=audience,
            signer=self.signer,
            key_reference=self.subject,
        )


@pytest.fixture
def local_chain():
    requests = LocalRequests()
    a, b = Issuer(DOMAIN_A), Issuer(DOMAIN_B)
    client = Workload.create(CLIENT, a)
    coordinator = Workload.create(COORDINATOR, b)
    research = Workload.create(RESEARCH, b)
    trust = {"domain-a.example": (a.jwk,), "domain-b.example": (b.jwk,)}
    policy = TransactionPolicy(DOMAIN_B, FILE_ORIGIN, (b.jwk,))
    return requests, a, b, client, coordinator, research, trust, policy


def summarize(content):
    return re.search(r"\$[0-9.]+M", content).group(0)


def workflow_ingress(issuer, trust, text_stats):
    return WimseIngressEndpoint(
        audience=INGRESS_ORIGIN,
        trust=trust,
        transaction=TransactionPolicy(DOMAIN_A, DOMAIN_A, (issuer.jwk,)),
        workflows={"text-stats": text_stats},
        grants=frozenset({(CLIENT, "text-stats")}),
    )


@pytest.mark.unit
@pytest.mark.parametrize("sdk_role", ["research", "file-tool"])
def test_native_nine_hop_pairing(local_chain, monkeypatch, sdk_role):
    requests, a, b, client, coordinator, research, trust, policy = local_chain
    replay = ReplayCache()
    reads, workflows = [], []

    def authenticate(target, headers, body, audience, subject):
        caller = verify_http(
            "POST",
            target,
            headers_dict(headers),
            body,
            audience=audience,
            trust=trust,
            replay=replay,
        )
        assert caller == subject

    def stats_model(self, *, conversation, **kwargs):
        text = conversation.get_last().content
        workflows.append(text)
        conversation.add_message(
            AgentMessage(
                content=json.dumps({"count": len(text), "upper": text.upper()})
            )
        )
        return conversation

    def research_model(
        self, conversation, toolkit, tool_choice, multiturn=True
    ):
        assert tool_choice == {}
        content = toolkit.get_tool_by_name("read_file")(file=FILE)
        conversation.add_message(AgentMessage(content=summarize(content)))
        return conversation

    monkeypatch.setattr(OpenAIModel, "predict", stats_model)
    monkeypatch.setattr(OpenAIToolModel, "predict", research_model)

    def begin(target, headers, body):
        transaction = {
            "txn": uuid4().hex,
            "sub": "user@example.org",
            "tctx": {"file": json.loads(body)["file"]},
        }
        token = a.issue(
            "txntoken+jwt",
            DOMAIN_A,
            transaction,
            workload=CLIENT,
            scope=RESEARCH_SCOPE,
        )
        return {"txn_token": token, "txn": transaction["txn"]}

    def text_stats(inputs):
        agent = SimpleConversationAgent(
            llm=OpenAIModel(name="gpt-4o-mini", api_key="unused"),
            conversation=Conversation(),
        )
        return json.loads(agent.exec(inputs["text"]))

    def exchange_a(target, headers, body):
        authenticate(target, headers, body, DOMAIN_A, CLIENT)
        claims = a.claims(
            json.loads(body)["subject_token"],
            "txntoken+jwt",
            DOMAIN_A,
            workload=CLIENT,
            scope=RESEARCH_SCOPE,
        )
        grant = a.issue(
            "jwt-chg+jwt",
            DOMAIN_B,
            claims,
            workload=CLIENT,
            scope=RESEARCH_SCOPE,
        )
        return {"assertion": grant}

    def exchange_b(target, headers, body):
        claims = a.claims(
            json.loads(body)["assertion"],
            "jwt-chg+jwt",
            DOMAIN_B,
            workload=CLIENT,
            scope=RESEARCH_SCOPE,
        )
        access = b.issue(
            "at+jwt",
            COORDINATOR_ORIGIN,
            claims,
            workload=CLIENT,
            scope=RESEARCH_SCOPE,
        )
        return {"access_token": access}

    def delegate(target, headers, body):
        payload = json.loads(body)
        workload = payload["req_wl"]
        if "access_token" in payload:
            assert (
                workload == COORDINATOR and payload["scope"] == RESEARCH_SCOPE
            )
            parent = b.claims(
                payload["access_token"],
                "at+jwt",
                COORDINATOR_ORIGIN,
                workload=CLIENT,
                scope=RESEARCH_SCOPE,
            )
        else:
            assert workload == RESEARCH and payload["scope"] == READ_SCOPE
            parent = b.claims(
                payload["txn_token"],
                "txntoken+jwt",
                FILE_ORIGIN,
                workload=COORDINATOR,
                scope=RESEARCH_SCOPE,
            )
        return {
            "txn_token": b.issue(
                "txntoken+jwt",
                FILE_ORIGIN,
                parent,
                workload=workload,
                scope=payload["scope"],
            )
        }

    def coordinate(target, headers, body):
        authenticate(target, headers, body, COORDINATOR_ORIGIN, CLIENT)
        authorization = headers_dict(headers)["authorization"]
        scheme, access = authorization.split(" ", 1)
        assert scheme == "Bearer"
        claims = b.claims(
            access,
            "at+jwt",
            COORDINATOR_ORIGIN,
            workload=CLIENT,
            scope=RESEARCH_SCOPE,
        )
        data = json.loads(body)
        assert data == claims["tctx"]
        delegated = requests.post_json(
            TOKEN_B,
            {
                "access_token": access,
                "scope": RESEARCH_SCOPE,
                "req_wl": COORDINATOR,
            },
        )
        return requests.post_json(
            RESEARCH_URL,
            data,
            coordinator.http_headers(
                RESEARCH_URL, data, **{"txn-token": delegated["txn_token"]}
            ),
        )

    def fixture_research(target, headers, body):
        authenticate(target, headers, body, RESEARCH_ORIGIN, COORDINATOR)
        data = json.loads(body)
        parent = headers_dict(headers)["txn-token"]
        claims = policy.verify(parent, workload=COORDINATOR, file=data["file"])
        delegated = requests.post_json(
            TOKEN_B,
            {"txn_token": parent, "scope": READ_SCOPE, "req_wl": RESEARCH},
        )
        file = requests.post_json(
            READ_FILE, data, research.file_headers(delegated["txn_token"])
        )
        assert file["txn"] == claims["txn"] and file["file"] == data["file"]
        return {
            "summary": summarize(file["content"]),
            "txn": file["txn"],
            "file_status": 200,
        }

    def read(file):
        reads.append(file)
        return {FILE: DOCUMENT}[file]

    def fixture_file(target, headers, body):
        fields = headers_dict(headers)
        caller = verify_wpt(
            fields, audience=FILE_ORIGIN, trust=trust, replay=replay
        )
        assert caller == RESEARCH
        file = json.loads(body)["file"]
        claims = policy.verify(fields["txn-token"], workload=caller, file=file)
        assert claims["scope"] == READ_SCOPE
        return {"file": file, "content": read(file), "txn": claims["txn"]}

    sdk_research = ResearchAgentEndpoint(
        audience=RESEARCH_ORIGIN,
        trust=trust,
        transaction=policy,
        coordinator_subject=COORDINATOR,
        research_subject=RESEARCH,
        wit=research.wit,
        signer=research.signer,
        key_reference=RESEARCH,
        issuer_url=TOKEN_B,
        file_url=READ_FILE,
        file_audience=FILE_ORIGIN,
        llm=OpenAIToolModel(api_key="unused", name="gpt-4o-mini"),
        post_json=requests.post_json,
    )
    sdk_file = FileToolEndpoint(read, FILE_ORIGIN, trust, policy, RESEARCH)
    requests.routes = {
        TOKEN_A: begin,
        INGRESS: workflow_ingress(a, trust, text_stats).post,
        EXCHANGE_A: exchange_a,
        EXCHANGE_B: exchange_b,
        COORDINATE: coordinate,
        TOKEN_B: delegate,
        RESEARCH_URL: sdk_research.post
        if sdk_role == "research"
        else fixture_research,
        READ_FILE: sdk_file.post if sdk_role == "file-tool" else fixture_file,
    }

    started = requests.post_json(TOKEN_A, {"file": FILE})
    text_stats = {"inputs": {"text": "hello wimse"}}
    result = requests.post_json(
        INGRESS,
        text_stats,
        client.http_headers(
            INGRESS, text_stats, **{"txn-token": started["txn_token"]}
        ),
    )
    assert result == {
        "state": "completed",
        "data": {"count": 11, "upper": "HELLO WIMSE"},
    }
    assert workflows == ["hello wimse"]

    exchange = {"subject_token": started["txn_token"]}
    grant = requests.post_json(
        EXCHANGE_A, exchange, client.http_headers(EXCHANGE_A, exchange)
    )
    access = requests.post_json(EXCHANGE_B, grant)
    document = {"file": FILE}
    result = requests.post_json(
        COORDINATE,
        document,
        client.http_headers(
            COORDINATE,
            document,
            authorization="Bearer " + access["access_token"],
        ),
    )
    assert result == {
        "summary": "$4.2M",
        "txn": started["txn"],
        "file_status": 200,
    }
    assert requests.trace == [
        [route, 200]
        for route in (
            TOKEN_A,
            INGRESS,
            EXCHANGE_A,
            EXCHANGE_B,
            COORDINATE,
            TOKEN_B,
            RESEARCH_URL,
            TOKEN_B,
            READ_FILE,
        )
    ]
    assert reads == [FILE]


@pytest.mark.unit
def test_ingress_rejects_valid_workload_without_workflow_grant(local_chain):
    requests, issuer, _, _, _, _, trust, _ = local_chain
    workload = Workload.create("wimse://domain-a.example/ungranted", issuer)
    text_stats = Mock(return_value={"count": 11, "upper": "HELLO WIMSE"})
    requests.routes[INGRESS] = workflow_ingress(issuer, trust, text_stats).post
    transaction = issuer.issue(
        "txntoken+jwt",
        DOMAIN_A,
        {
            "txn": uuid4().hex,
            "sub": "user@example.org",
            "tctx": {"file": FILE},
        },
        workload=workload.subject,
        scope=RESEARCH_SCOPE,
    )
    data = {"inputs": {"text": "hello wimse"}}
    headers = workload.http_headers(
        INGRESS, data, **{"txn-token": transaction}
    )

    assert requests.send(INGRESS, data, headers) == (
        403,
        {"error": "workflow-grant-required"},
    )
    text_stats.assert_not_called()


@pytest.mark.unit
@pytest.mark.parametrize(
    ("control", "status"),
    [
        ("wrong-audience", 401),
        ("missing-proof", 401),
        ("different-file", 403),
        ("replayed-proof", 401),
    ],
)
def test_file_tool_rejects_before_an_extra_read(local_chain, control, status):
    requests, _, issuer, _, _, research, trust, policy = local_chain
    reads = []

    def read(file):
        reads.append(file)
        return {FILE: DOCUMENT, "other.pdf": "test-only"}[file]

    requests.routes[READ_FILE] = FileToolEndpoint(
        read,
        FILE_ORIGIN,
        trust,
        policy,
        RESEARCH,
    ).post
    token = issuer.issue(
        "txntoken+jwt",
        FILE_ORIGIN,
        {
            "txn": uuid4().hex,
            "sub": "user@example.org",
            "tctx": {"file": FILE},
        },
        workload=RESEARCH,
        scope=READ_SCOPE,
    )
    data = {"file": "other.pdf" if control == "different-file" else FILE}
    audience = (
        "https://other.example" if control == "wrong-audience" else FILE_ORIGIN
    )
    headers = research.file_headers(token, audience)
    if control == "missing-proof":
        del headers["Authorization"]
    if control == "replayed-proof":
        assert (
            requests.post_json(READ_FILE, data, headers)["content"] == DOCUMENT
        )

    expected_reads = reads.copy()
    assert expected_reads == ([FILE] if control == "replayed-proof" else [])
    assert requests.send(READ_FILE, data, headers)[0] == status
    assert reads == expected_reads
