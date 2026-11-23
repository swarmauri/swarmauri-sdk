"""Demonstration helpers for CMS and S/MIME workflows."""

from .cms_and_smime_examples import (
    build_ephemeral_identity,
    cms_detached_signature,
    describe_certificate_chain,
    smime_attached_message,
)

__all__ = [
    "build_ephemeral_identity",
    "cms_detached_signature",
    "describe_certificate_chain",
    "smime_attached_message",
]
