import asyncio
from datetime import datetime, timedelta, timezone
from pathlib import Path

from swarmauri_certservice_aws_kms import AwsKmsCertService
from swarmauri_core.crypto.types import KeyRef


async def main() -> None:
    service = AwsKmsCertService(region_name="us-east-1")
    kms_key = KeyRef(
        kid="arn:aws:kms:us-east-1:123456789012:key/abcd-1234",
    )

    certificate = await service.sign_cert(
        csr=Path("tenant.csr").read_bytes(),
        ca_key=kms_key,
        issuer={"CN": "Example KMS Issuing CA", "O": "Example Corp"},
        not_after=int(
            (datetime.now(timezone.utc) + timedelta(days=365)).timestamp()
        ),
    )
    Path("tenant.pem").write_bytes(certificate)


asyncio.run(main())
