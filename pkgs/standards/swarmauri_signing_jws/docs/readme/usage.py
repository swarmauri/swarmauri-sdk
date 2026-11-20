import asyncio
from swarmauri_signing_jws import JwsSignerVerifier


async def main() -> None:
    signer = JwsSignerVerifier()
    key = {"kind": "raw", "key": "0" * 32}

    compact = await signer.sign_compact(
        payload={"msg": "hi"},
        alg="HS256",
        key=key,
    )

    result = await signer.verify_compact(
        compact,
        hmac_keys=[key],
    )

    print(result.payload.decode("utf-8"))


if __name__ == "__main__":
    asyncio.run(main())
