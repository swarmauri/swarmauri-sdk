from __future__ import annotations

import hashlib
import math
import threading
import time
from dataclasses import dataclass
from typing import Any


def _as_bytes(x: bytes | str) -> bytes:
    if isinstance(x, bytes):
        return x
    if isinstance(x, str):
        return x.encode("utf-8", errors="strict")
    raise TypeError("key must be bytes or str")


def _optimal_m_bits(n: int, p: float) -> int:
    if n <= 0:
        raise ValueError("capacity must be > 0")
    if not (0.0 < p < 1.0):
        raise ValueError("fp_rate must be in (0, 1)")
    return max(8, int(math.ceil((-n * math.log(p)) / (math.log(2) ** 2))))


def _optimal_k_hashes(m_bits: int, n: int) -> int:
    k = int(round((m_bits / n) * math.log(2)))
    return max(1, k)


def _bitset_size_bytes(m_bits: int) -> int:
    return (m_bits + 7) // 8


def _set_bit(buf: bytearray, bit: int) -> None:
    idx = bit >> 3
    mask = 1 << (bit & 7)
    buf[idx] |= mask


def _get_bit(buf: bytearray, bit: int) -> bool:
    idx = bit >> 3
    mask = 1 << (bit & 7)
    return (buf[idx] & mask) != 0


def _hash64_pair(seed: bytes, key: bytes) -> tuple[int, int]:
    h = hashlib.blake2b(key, digest_size=16, key=seed).digest()
    h1 = int.from_bytes(h[0:8], "little", signed=False)
    h2 = int.from_bytes(h[8:16], "little", signed=False)
    if h2 == 0:
        h2 = 0x9E3779B97F4A7C15
    return h1, h2


@dataclass(frozen=True)
class BloomParams:
    m_bits: int
    k_hashes: int
    capacity: int
    fp_rate: float
    seed: bytes


class BloomFilter:
    def __init__(self, *, params: BloomParams) -> None:
        self._p = params
        self._buf = bytearray(_bitset_size_bytes(params.m_bits))
        self._lock = threading.RLock()
        self._adds = 0

    @classmethod
    def from_capacity(
        cls, *, capacity: int, fp_rate: float, seed: str | bytes
    ) -> "BloomFilter":
        seed_b = (
            seed if isinstance(seed, bytes) else seed.encode("utf-8", errors="strict")
        )
        m_bits = _optimal_m_bits(capacity, fp_rate)
        k_hashes = _optimal_k_hashes(m_bits, capacity)
        params = BloomParams(
            m_bits=m_bits,
            k_hashes=k_hashes,
            capacity=capacity,
            fp_rate=fp_rate,
            seed=seed_b,
        )
        return cls(params=params)

    def add(self, key: bytes | str) -> None:
        kb = _as_bytes(key)
        h1, h2 = _hash64_pair(self._p.seed, kb)
        m = self._p.m_bits
        with self._lock:
            for i in range(self._p.k_hashes):
                bit = (h1 + i * h2) % m
                _set_bit(self._buf, bit)
            self._adds += 1

    def __contains__(self, key: bytes | str) -> bool:
        return self.contains(key)

    def contains(self, key: bytes | str) -> bool:
        kb = _as_bytes(key)
        h1, h2 = _hash64_pair(self._p.seed, kb)
        m = self._p.m_bits
        with self._lock:
            for i in range(self._p.k_hashes):
                bit = (h1 + i * h2) % m
                if not _get_bit(self._buf, bit):
                    return False
            return True

    def add_if_absent(self, key: bytes | str) -> bool:
        kb = _as_bytes(key)
        h1, h2 = _hash64_pair(self._p.seed, kb)
        m = self._p.m_bits
        with self._lock:
            absent = False
            bits = []
            for i in range(self._p.k_hashes):
                bit = (h1 + i * h2) % m
                bits.append(bit)
                if not _get_bit(self._buf, bit):
                    absent = True
            for bit in bits:
                _set_bit(self._buf, bit)
            if absent:
                self._adds += 1
            return absent

    def reset(self) -> None:
        with self._lock:
            self._buf[:] = b"\x00" * len(self._buf)
            self._adds = 0

    def stats(self) -> dict[str, Any]:
        with self._lock:
            return {
                "mode": "single",
                "m_bits": self._p.m_bits,
                "k_hashes": self._p.k_hashes,
                "capacity": self._p.capacity,
                "fp_rate_target": self._p.fp_rate,
                "adds_approx": self._adds,
                "bytes": len(self._buf),
            }


class BloomRing:
    def __init__(self, *, filters: list[BloomFilter], window_seconds: float) -> None:
        if window_seconds <= 0:
            raise ValueError("window_seconds must be > 0")
        if len(filters) < 2:
            raise ValueError("BloomRing requires at least 2 windows")
        self._filters = filters
        self._window_seconds = float(window_seconds)
        self._lock = threading.RLock()
        self._epoch = time.monotonic()
        self._index = 0

    @classmethod
    def from_capacity(
        cls,
        *,
        capacity: int,
        fp_rate: float,
        seed: str | bytes,
        windows: int,
        window_seconds: float,
    ) -> "BloomRing":
        seed_s = (
            seed if isinstance(seed, str) else seed.decode("utf-8", errors="strict")
        )
        filters = [
            BloomFilter.from_capacity(
                capacity=capacity,
                fp_rate=fp_rate,
                seed=f"{seed_s}:w{i}",
            )
            for i in range(windows)
        ]
        return cls(filters=filters, window_seconds=window_seconds)

    def _rotate_if_needed(self) -> None:
        elapsed = time.monotonic() - self._epoch
        if elapsed < self._window_seconds:
            return
        steps = int(elapsed // self._window_seconds)
        if steps <= 0:
            return
        for _ in range(min(steps, len(self._filters))):
            self._index = (self._index + 1) % len(self._filters)
            self._filters[self._index].reset()
        self._epoch += steps * self._window_seconds

    def add(self, key: bytes | str) -> None:
        with self._lock:
            self._rotate_if_needed()
            self._filters[self._index].add(key)

    def __contains__(self, key: bytes | str) -> bool:
        return self.contains(key)

    def contains(self, key: bytes | str) -> bool:
        with self._lock:
            self._rotate_if_needed()
            for j in range(len(self._filters)):
                i = (self._index - j) % len(self._filters)
                if self._filters[i].contains(key):
                    return True
            return False

    def add_if_absent(self, key: bytes | str) -> bool:
        with self._lock:
            self._rotate_if_needed()
            present = any(filter_.contains(key) for filter_ in self._filters)
            self._filters[self._index].add(key)
            return not present

    def reset(self) -> None:
        with self._lock:
            for filter_ in self._filters:
                filter_.reset()
            self._epoch = time.monotonic()
            self._index = 0

    def stats(self) -> dict[str, Any]:
        with self._lock:
            self._rotate_if_needed()
            return {
                "mode": "ring",
                "windows": len(self._filters),
                "window_seconds": self._window_seconds,
                "current_index": self._index,
                "per_window": self._filters[self._index].stats(),
            }
