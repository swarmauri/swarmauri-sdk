"""WIMSE workflow, research, and file endpoints."""

from collections.abc import Callable, Mapping, Set
from dataclasses import dataclass, field
from http.server import BaseHTTPRequestHandler
import json
from urllib.error import HTTPError, URLError
from urllib.request import (
    HTTPRedirectHandler,
    ProxyHandler,
    Request,
    build_opener,
)

from swarmauri_base.tool_llms.ToolLLMBase import ToolLLMBase
from swarmauri_standard.toolkits.Toolkit import Toolkit
from tba_concrete_jwt import decode_jwt_unverified

from .WimseFileTool import WimseFileTool
from .WimseResearchAgent import WimseResearchAgent
from .proof import (
    Rejected,
    ReplayCache,
    headers_dict,
    verify_http,
    verify_transaction,
    verify_workload_transaction,
    verify_wpt,
)


MAX_BODY = 1024 * 1024


class NoRedirect(HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        return None


def post_json(url, data, headers):
    request = Request(
        url,
        data=json.dumps(data).encode("utf-8"),
        headers={"Content-Type": "application/json", **headers},
        method="POST",
    )
    try:
        with build_opener(ProxyHandler({}), NoRedirect()).open(
            request, timeout=10
        ) as response:
            body = response.read(MAX_BODY + 1)
            if len(body) > MAX_BODY:
                raise ValueError("oversized upstream response")
            result = json.loads(body)
            if not isinstance(result, dict):
                raise ValueError("invalid upstream response")
            return result
    except (HTTPError, URLError, OSError, ValueError) as exc:
        raise Rejected(502, "upstream-request-failed") from exc


@dataclass(frozen=True)
class TransactionPolicy:
    issuer: str
    audience: str
    keys: tuple

    def verify_workload(self, token: str, *, workload: str) -> Mapping:
        """Validate a signed transaction for the authenticated workload."""
        return verify_workload_transaction(
            token,
            keys=self.keys,
            issuer=self.issuer,
            audience=self.audience,
            workload=workload,
        )

    def verify(self, token, *, workload, file):
        return verify_transaction(
            token,
            keys=self.keys,
            issuer=self.issuer,
            audience=self.audience,
            workload=workload,
            file=file,
        )


@dataclass
class WimseIngressEndpoint:
    """Dispatch signed workflow requests from explicitly granted workloads."""

    audience: str
    trust: Mapping
    transaction: TransactionPolicy
    workflows: Mapping[str, Callable[[dict[str, object]], object]]
    grants: Set[tuple[str, str]]
    replay: ReplayCache = field(default_factory=ReplayCache)

    def post(self, target, headers, body):
        """Verify a request and run the granted workflow."""
        match target.split("/"):
            case ["", "workflows", workflow, "executions"] if (
                workflow and workflow in self.workflows
            ):
                run = self.workflows[workflow]
            case _:
                raise Rejected(404, "unknown-workflow")

        fields = headers_dict(headers)
        caller = verify_http(
            "POST",
            target,
            fields,
            body,
            audience=self.audience,
            trust=self.trust,
            replay=self.replay,
        )
        self.transaction.verify_workload(
            fields.get("txn-token", ""), workload=caller
        )
        if (caller, workflow) not in self.grants:
            raise Rejected(403, "workflow-grant-required")

        try:
            inputs = json.loads(body)["inputs"]
            if not isinstance(inputs, dict):
                raise ValueError("workflow inputs must be an object")
        except (KeyError, TypeError, ValueError) as exc:
            raise Rejected(400, "invalid-workflow-inputs") from exc
        return {"state": "completed", "data": run(inputs)}


def requested_file(body):
    try:
        data = json.loads(body)
        file = data["file"]
        if not isinstance(file, str) or not file:
            raise ValueError("missing file")
        return file
    except (KeyError, TypeError, ValueError) as exc:
        raise Rejected(400, "invalid-file-request") from exc


@dataclass
class FileToolEndpoint:
    tool: Callable[[str], str]
    audience: str
    trust: Mapping
    transaction: TransactionPolicy
    research_subject: str
    replay: ReplayCache = field(default_factory=ReplayCache)
    route = "/files/read"

    def post(self, target, headers, body):
        # Exact path and configured audience are server-side inputs.
        if target != self.route:
            raise Rejected(404, "unknown-endpoint")
        headers = headers_dict(headers)
        file = requested_file(body)
        caller = verify_wpt(
            headers,
            audience=self.audience,
            trust=self.trust,
            replay=self.replay,
        )
        if caller != self.research_subject:
            raise Rejected(403, "caller-not-authorized")
        claims = self.transaction.verify(
            headers["txn-token"], workload=caller, file=file
        )
        if claims["scope"].split() != ["files:read"]:
            raise Rejected(403, "transaction-scope-not-narrowed")
        try:
            content = self.tool(file)
        except KeyError as exc:
            raise Rejected(404, "file-not-found") from exc
        return {"file": file, "content": content, "txn": claims["txn"]}


@dataclass
class ResearchAgentEndpoint:
    audience: str
    trust: Mapping
    transaction: TransactionPolicy
    coordinator_subject: str
    research_subject: str
    wit: str
    signer: object
    key_reference: str
    issuer_url: str
    file_url: str
    file_audience: str
    llm: ToolLLMBase
    post_json: Callable = post_json
    replay: ReplayCache = field(default_factory=ReplayCache)
    route = "/research"

    def post(self, target, headers, body):
        if target != self.route:
            raise Rejected(404, "unknown-endpoint")
        headers = headers_dict(headers)
        caller = verify_http(
            "POST",
            target,
            headers,
            body,
            audience=self.audience,
            trust=self.trust,
            replay=self.replay,
        )
        if caller != self.coordinator_subject:
            raise Rejected(403, "caller-not-authorized")
        file = requested_file(body)
        prior = headers.get("txn-token", "")
        parent = self.transaction.verify(prior, workload=caller, file=file)
        if (
            decode_jwt_unverified(self.wit).claims.get("sub")
            != self.research_subject
        ):
            raise Rejected(502, "research-credential-mismatch")
        response = self.post_json(
            self.issuer_url,
            {
                "txn_token": prior,
                "scope": "files:read",
                "req_wl": self.research_subject,
            },
            {},
        )
        try:
            token = response["txn_token"]
            narrowed = self.transaction.verify(
                token, workload=self.research_subject, file=file
            )
            if (
                narrowed["txn"] != parent["txn"]
                or narrowed["sub"] != parent["sub"]
                or narrowed["scope"].split() != ["files:read"]
                or narrowed["tctx"] != parent["tctx"]
            ):
                raise ValueError("inconsistent narrowed transaction")
        except (KeyError, TypeError, ValueError) as exc:
            raise Rejected(502, "issuer-replacement-invalid") from exc
        file_tool = WimseFileTool.for_transaction(
            file=file,
            transaction_id=parent["txn"],
            wit=self.wit,
            token=token,
            audience=self.file_audience,
            signer=self.signer,
            key_reference=self.key_reference,
            url=self.file_url,
            post_json=self.post_json,
        )
        agent = WimseResearchAgent(
            llm=self.llm,
            toolkit=Toolkit(tools={file_tool.name: file_tool}),
        )
        summary = agent.research(file)
        if not file_tool.has_read or not isinstance(summary, str):
            raise Rejected(502, "research-result-invalid")
        return {
            "summary": summary,
            "txn": parent["txn"],
            "file_status": 200,
        }


def http_handler(endpoint):
    """Build a standard HTTP server handler for a configured endpoint."""

    class Handler(BaseHTTPRequestHandler):
        def do_POST(self):
            try:
                lengths = self.headers.get_all("Content-Length", [])
                if (
                    len(lengths) != 1
                    or not lengths[0].isascii()
                    or not lengths[0].isdecimal()
                    or len(lengths[0]) > 7
                    or self.headers.get("Transfer-Encoding") is not None
                ):
                    raise Rejected(400, "invalid-request-length")
                size = int(lengths[0])
                if size > MAX_BODY:
                    raise Rejected(413, "request-too-large")
                result = endpoint.post(
                    self.path, self.headers.raw_items(), self.rfile.read(size)
                )
                status = 200
            except Rejected as exc:
                status, result = exc.status, {"error": str(exc)}
            body = json.dumps(result).encode("utf-8")
            self.send_response(status)
            self.send_header("Content-Type", "application/json")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)

    return Handler
