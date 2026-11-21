# Composable authenticated agent execution

This implementation adds seven reusable packages and two scenario compositions.
It reuses the SDK's service registry, task assignment, agent runner, guarded
workflow, checkpoint store, token services and transport contracts. It does not
add an authenticator or transport family. Nothing is deprecated or published
by this change.

## Package inventory

| Kind | Package | Responsibility |
| --- | --- | --- |
| Factor | swarmauri_permission_explicit | Exact action/resource/tenant checks |
| Factor | swarmauri_taskstore_sqlite | Durable task intent and revisions |
| Factor | swarmauri_grantstore_sqlite | Durable grant ancestry and revocation |
| Infrastructure composition | swarmauri_execution_default | Cooperative driver control and checkpoints |
| Infrastructure composition | swarmauri_taskmanager_default | Admitted tasks, placement and lifecycle coordination |
| Infrastructure composition | swarmauri_delegation_attenuating | Policy, live grants and credential issuance |
| Infrastructure composition | swarmauri_invoker_default | Receiving admission and local/HTTP invocation |
| Scenario composition | swarmauri_workflow_documentassistant | One agent reads an authorized document |
| Scenario composition | swarmauri_workflow_delegatedresearch | Coordinator invokes research and retrieval agents |

New interfaces and immutable records live in core's executions, tasks,
workflows, permissions, delegation and invocations namespaces. Matching ABC
component bases live in base. Every concrete component is discoverable through
entry points and facade registration. Constructors accept interfaces; direct
instantiation remains the recommended composition style.

The existing IServiceRegistry resolves service bindings. Workflow definitions
own their nodes and edges. Plugin registries discover Python components.
These are three distinct lookup responsibilities; there is no graph registry
package or new node/edge catalog.

The existing ITaskMgmtStrategy and RoundRobinStrategy remain placement
strategies. Their signatures now agree while preserving legacy two-argument
assignment. They do not become lifecycle controllers. Pipeline and Swarm
retain their existing interfaces. DAG execution is deferred; neither scenario
requires a DAG implementation.

## Definitions

A task is admitted business intent. An execution is one tracked computation.
A node references a service; an edge expresses graph connectivity. A
state-driven Transition adds a Condition to an edge. EdgeAuthorizationBinding
links an edge to configured callers, operations and permission ceilings.
An invocation is an actual call; delegation is authority granted for further
work. A grant can authorize several calls. Credentials represent grants but
live task/grant records remain the authority source.

The default invoker requires a validated service binding, configured edge,
matching operation, and exact resource argument. It obtains a credential
through an IAuthorityStrategy. HTTP uses existing IHttpClient/HttpxClient;
local delivery uses the same request codec and receiving application.
InvocationEndpoint implements the existing HttpApp and exposes an explicit
ASGI adapter. It never assumes HttpApp's four arguments are an ASGI signature.

## Run the offline showcases

Install the matching workspace packages together. The new APIs are unreleased;
an older published core/base is not compatible. A focused validation environment
can be prepared with the steps in scripts/verify_composable_execution.py's
module documentation. The repository's normal uv workspace environment also
works when its full dependency set is available.

From an environment containing the workspace packages:

```sh
python -m swarmauri_workflow_documentassistant.cli
python -m swarmauri_workflow_delegatedresearch.cli
python scripts/verify_composable_execution.py
```

Both commands explicitly run offline fixtures: ScriptedDocumentModel and a
host-admitted demo:alice subject. They do not fake an IdP exchange. The
LocalKeyProvider, JWTTokenService/JWS verification, SQLite records, agent tool
execution, graph conditions and delegation checks are real. Keys are generated
ephemerally and the CLI deletes its temporary database directory on exit.
The model fixture returns tool results; it is not a claim of LLM summarization.

The document sequence is:

```text
host-authenticated Alice
  -> resource admission -> task -> root grant for assistant
  -> AgentRunnerExecutionDriver -> ReadDocument tool
  -> invoker delegates to document service
  -> receiving JWT/grant/resource checks -> document read
  -> tool result -> model result
```

The research sequence is:

```text
host-authenticated Alice -> admitted task -> coordinator grant (depth 3)
  -> state-driven coordinator/research transition
  -> research endpoint (depth 2)
       -> checkpointed research AgentRunner
       -> retrieval endpoint (depth 1)
            -> checkpointed retrieval AgentRunner
            -> documents endpoint (depth 0)
```

The top-level graph schedules coordinator/research stages. Research and
retrieval are real child agent executions and are linked by invocation context
to their parent executions. Task records contain all execution IDs for group
control. Results join as data; authority is never unioned by merging results.
No token or grant identity is a model-visible tool parameter.

## Supply a real model and IdP

Both compositions expose create(..., model_factory=..., authorize=...).
model_factory(resource) returns an existing IToolStepModel or legacy runner
model-step callable. For example, an existing OpenAIToolModel's
propose_tool_step callback can be injected. The host supplies provider
credentials outside the model transcript.

For a real provider, inject an existing OIDC login adapter:

```python
from swarmauri_workflow_documentassistant.login import OIDCAdmission

admission = OIDCAdmission(
    login=configured_oidc_adapter,
    resolve_identity=map_provider_identity_to_local_subject,
)
payload, browser_binding = await admission.begin()
# Redirect the browser to payload["url"]. Store browser_binding in the host's
# Secure, HttpOnly, SameSite session cookie; do not put it in the redirect URL.
subject = await admission.complete(code, state, browser_binding)
execution = workflow.start(subject)
```

The host authenticates lifecycle commands too; start/pause/resume/stop and broker
root/delegate/credential methods are trusted host operations, not unauthenticated
HTTP APIs. authorize(subject, permission) checks the actual user's resource
access. Login establishes identity, not document permission.

OIDCAdmission's pending-login store is bounded and process-local. Multiworker
hosts must provide sticky login handling or a shared session admission adapter.
Offline tests exercise browser binding and one-use state with a clearly named
provider test double. No live IdP interoperability was exercised.

Production hosts inject durable key providers and trusted verifier
configuration instead of demo_tokens(). Agents must not receive broker signing
capability as a tool. The default bearer profile relies on authenticated
credential issuance and HTTPS. It does not prove possession of a workload key;
existing DPoP/mTLS/WIMSE integrations require their own configured profiles.
External Google APIs still require Google-issued credentials.

## Replace factors and delivery

create_runtime accepts interchangeable task/grant/checkpoint stores, permission
policy, service registry, delegation service and existing HTTP client.
Composition create() also accepts runtime_factory and runtime_options.
Use these to replace the default wiring, not subclass scenario business logic.

To exercise real HTTP client semantics against the receiving app in process:

```python
import httpx
from swarmauri_transport_httpx import HttpxClient

endpoint = workflow.runtime.endpoints["documents"]
async with httpx.AsyncClient(
    transport=httpx.ASGITransport(app=endpoint.asgi)
) as client:
    workflow.runtime.invoker.http_client = HttpxClient(async_client=client)
    workflow.runtime.services.update_service("documents", {
        "protocol": "http",
        "endpoint": "http://localhost/invocations",
    })
    # Subsequent agent calls use HTTP encoding, headers and receiving admission.
    result = await workflow.run(authenticated_subject)
```

For actual network delivery, host endpoint.asgi with a compatible existing ASGI
server and configure an HTTPS endpoint. The invoker refuses non-loopback plain
HTTP. Deployment owns trusted stores, keys, service bindings and caller
authentication. The reference factory places broker and stores in one trust
domain; it is not a distributed OAuth token-exchange server. A remote broker
implementation can satisfy IDelegationService without changing agent code.

WorkloadAuthorityStrategy instead uses explicitly configured standing service
permissions. Configure the receiving edge with delegated=False for that profile.
It deliberately does not claim to carry the initiating user's permissions.

## Lifecycle and recovery

ExecutionController.start creates a ready checkpoint. advance performs one
driver step. Pause/stop during an in-flight step become pausing/stopping and
acknowledge at the next boundary. They do not interrupt a synchronous model/tool
already running in a worker thread and cannot undo external effects. Stop takes
precedence over pause. Resuming waits for quiescence and rechecks task validity.

TaskManager persists task intent before coordinating executions. Live receiving
admission and grant issuance reject paused/stopped/expired tasks. Repeat control
commands to reconcile a partially interrupted coordination. Parent execution
stop propagates to registered descendants.

AgentRunner.initialize and advance(max_steps=1) are additive APIs; existing
start/resume behavior remains. Human answers/approvals still go through the
existing runner's resume/decide APIs before controller resumption.

StateDrivenExecutionDriver persists its queue, results, buffers and strategy
state after each node. It reuses existing conditions, inputs, joins and merges.
Definitions have a host-supplied version which must remain stable on restore.
Default strategy state must be JSON serializable. Custom strategies can
override dump_strategy/restore_strategy; checkpointing does not serialize
Python callables or live agent instances.

Built-in strategy callables remain configuration in the versioned graph
definition and are rebound when the driver is reconstructed. Mutable JSON
strategy state is checkpointed separately. SplitInputMode expansions enter
the persisted ready queue, including when an authorized dispatcher is used;
the dispatcher is not called for the expansion-only step.

Compositions expose restore(execution_id) to rebind drivers on the current
event loop using the same durable stores, model configuration and token keys.
Do not call start() to resume an existing task.

An execution left running by process failure is not replayed automatically.
Reconcile uncertain effects before starting a replacement attempt. Invocation
IDs persist a digest and result using IRunStore. Completed duplicates return the
saved result after fresh authorization; conflicting IDs and uncertain/failed
attempts do not re-execute side effects. This is not an exactly-once guarantee.
Revocation is checked on admission, not retroactively during an admitted effect.

## Verification and release boundary

Tests cover real JWT verification, audience/resource/tenant rejection,
attenuation/depth, ancestry revocation, task state, revision conflicts, durable
duplicates, local/HTTP parity, cooperative pause/stop, restart, join buffers,
actual agent tool calls and facade/entry-point wiring. Existing runner and
state-driven unit suites are retained.

No new distribution has been published. Before publication, bump and constrain
compatible core/base/runner releases, regenerate the release lock, build every
wheel, and run the normal full release gates. This implementation's focused
environment avoids resolving unrelated workspace providers.
