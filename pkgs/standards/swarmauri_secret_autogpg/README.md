<!-- Dark OS/GitHub theme → show LIGHT PNG; Light → show DARK PNG -->
<picture>
  <source media="(prefers-color-scheme: dark)"  srcset="../../../assets/swarmauri_brand_frag_light.png">
  <source media="(prefers-color-scheme: light)" srcset="../../../assets/swarmauri_brand_frag_dark.png">
  <!-- Fallback below (see #2) -->
  <img alt="Project logo" src="../../../assets/swarmauri_brand_frag_dark.png" width="640">
</picture>


<p align="center">
    <a href="https://pypi.org/project/swarmauri_secret_autogpg/">
        <img src="https://img.shields.io/pypi/dm/swarmauri_secret_autogpg" alt="PyPI - Downloads"/></a>
    <a href="https://hits.sh/github.com/swarmauri/swarmauri-sdk/tree/master/pkgs/standards/swarmauri_secret_autogpg/">
        <img alt="Hits" src="https://hits.sh/github.com/swarmauri/swarmauri-sdk/tree/master/pkgs/standards/swarmauri_secret_autogpg.svg"/></a>
    <a href="https://pypi.org/project/swarmauri_secret_autogpg/">
        <img src="https://img.shields.io/pypi/pyversions/swarmauri_secret_autogpg" alt="PyPI - Python Version"/></a>
    <a href="https://pypi.org/project/swarmauri_secret_autogpg/">
        <img src="https://img.shields.io/pypi/l/swarmauri_secret_autogpg" alt="PyPI - License"/></a>
    <a href="https://pypi.org/project/swarmauri_secret_autogpg/">
        <img src="https://img.shields.io/pypi/v/swarmauri_secret_autogpg?label=swarmauri_secret_autogpg&color=green" alt="PyPI - swarmauri_secret_autogpg"/></a>
 </p>

---

## Swarmauri Secret AutoGPG

Pure-Python PGP-based secret drive using `pgpy`, implementing the `ISecretDrive` contract via `SecretDriveBase`.

- Manages an RSA keypair on first use (stored under a local key directory)
- Encrypts for recipients and decrypts locally (no system `gpg` binary required)
- Intended for developer-friendly secret key management in Swarmauri

## Installation

```bash
pip install swarmauri_secret_autogpg
```

## Usage

```python
from swarmauri_secret_autogpg import AutoGpgSecretDrive

# Initialize with an isolated key directory (created on first use)
drv = AutoGpgSecretDrive(key_dir="/tmp/sa-keys")

# Encrypt for one or more recipients (paths or ASCII-armored public keys)
plaintext = b"super-secret"
ciphertext = drv.encrypt(plaintext, recipients=[str(drv.pub_path)])

# Decrypt using the driver's private key
roundtrip = drv.decrypt(ciphertext)
assert roundtrip == plaintext
```

## Notes

- Keys are stored as ASCII-armored `private.asc` and `public.asc`
- RSA-2048 with SHA-256 and AES-256 (via `pgpy`)
- For integration with Swarmauri, the driver implements `ISecretDrive` via `SecretDriveBase`
