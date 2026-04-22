from __future__ import annotations

from monotone_ops.evidence import ClaimEvidence, certified_claims, claim_evidence_merge

state = ClaimEvidence({"feature:ga": frozenset({"svc-a"})})
update = ClaimEvidence({"feature:ga": frozenset({"svc-b"}), "feature:beta": frozenset({"svc-c"})})
merged = claim_evidence_merge(state, update)

print(certified_claims(merged, quorum=2))
