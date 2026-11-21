import asyncio

from swarmauri_mre_crypto_shamir import ShamirMreCrypto


async def main() -> None:
    provider = ShamirMreCrypto()

    recipients = [
        {"kid": "alice"},
        {"kid": "bob"},
        {"kid": "carol"},
    ]

    plaintext = b"Secret launch codes"

    envelope = await provider.encrypt_for_many(
        recipients,
        plaintext,
        opts={"threshold_k": 2},
    )

    print("Mode:", envelope["mode"])
    print("Recipients:", [entry["id"] for entry in envelope["recipients"]])
    print(
        "Threshold:",
        int.from_bytes(envelope["shared"]["threshold_k"], "big"),
    )

    recovered = await provider.open_for_many(
        [{"kid": "alice"}, {"kid": "carol"}],
        envelope,
    )

    assert recovered == plaintext
    print("Recovered plaintext:", recovered.decode("utf-8"))


if __name__ == "__main__":
    asyncio.run(main())
