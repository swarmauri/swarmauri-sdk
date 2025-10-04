from __future__ import annotations

from tigrbl_acme_ca.tables.accounts import Account
from tigrbl_acme_ca.tables.orders import Order
from tigrbl_acme_ca.tables.authorizations import Authorization
from tigrbl_acme_ca.tables.challenges import Challenge
from tigrbl_acme_ca.tables.certificates import Certificate
from tigrbl_acme_ca.tables.revocations import Revocation
from tigrbl_acme_ca.tables.nonces import Nonce
from tigrbl_acme_ca.tables.audit_events import AuditEvent
from tigrbl_acme_ca.tables.external_account_bindings import ExternalAccountBinding
from tigrbl_acme_ca.tables.tos_agreements import TosAgreement

TABLES = [
    Account,
    Order,
    Authorization,
    Challenge,
    Certificate,
    Revocation,
    Nonce,
    AuditEvent,
    ExternalAccountBinding,
    TosAgreement,
]
