from pathlib import Path

from swarmauri_certs_acme import AcmeCertService
from swarmauri_core.crypto.types import KeyRef

account_key = KeyRef(material=Path("account-key.pem").read_bytes())
service = AcmeCertService(
    account_key=account_key,
    contact_emails=["admin@example.com"],
)

print(service.supports()["features"])
