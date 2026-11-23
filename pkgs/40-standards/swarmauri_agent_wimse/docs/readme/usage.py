from http.server import ThreadingHTTPServer
from swarmauri_agent_wimse import (
    FileToolEndpoint,
    TransactionPolicy,
    http_handler,
)


def file_server(files, workload_trust, transaction_keys):
    endpoint = FileToolEndpoint(
        tool=dict(files).__getitem__,
        audience="http://rich.ietf127.example:5063",
        trust=workload_trust,
        transaction=TransactionPolicy(
            issuer="http://rich.ietf127.example:5061",
            audience="rich.ietf127.example",
            keys=tuple(transaction_keys),
        ),
        research_subject="wimse://rich.ietf127.example/agent/research",
    )
    return ThreadingHTTPServer(("127.0.0.1", 5063), http_handler(endpoint))
