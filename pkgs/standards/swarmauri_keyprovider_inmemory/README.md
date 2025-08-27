# swarmauri_keyprovider_inmemory

An in-memory key provider plugin for Swarmauri. It stores all generated or imported keys only in volatile memory, ensuring no key material is written to disk.

## Features
- Supports symmetric and asymmetric key classes
- Create, import, rotate, and destroy keys
- Random bytes generation and HKDF derivation

This provider is intended for ephemeral environments where persistence is not desired.
