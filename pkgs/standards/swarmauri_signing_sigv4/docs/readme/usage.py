import asyncio
from swarmauri_signing_sigv4 import SigV4Signing


envelope = {
    "method": "GET",
    "uri": "/",
    "query": {"Action": ["ListUsers"], "Version": ["2010-05-08"]},
    "headers": {
        "host": "iam.amazonaws.com",
        "x-amz-date": "20150830T123600Z",
        "content-type": "application/x-www-form-urlencoded; charset=utf-8",
    },
    "payload_hash": "UNSIGNED-PAYLOAD",
    "amz_date": "20150830T123600Z",
    "scope": {"date": "20150830", "region": "us-east-1", "service": "iam"},
}

key = {
    "access_key": "AKIDEXAMPLE",
    "secret_key": "wJalrXUtnFEMI/K7MDENG+bPxRfiCYEXAMPLEKEY",
}


async def main() -> None:
    signer = SigV4Signing()
    signatures = await signer.sign_envelope(key, envelope)
    print(signatures[0]["signature"])


asyncio.run(main())
