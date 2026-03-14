"""
Crypto layer using PyNaCl.

Key exchange:  X25519 (Curve25519 ECDH)
Encryption:    XSalsa20-Poly1305 (NaCl secretbox)
KDF ratchet:   SHA-512 truncated to 32 bytes
"""
import hashlib
from base64 import b64encode, b64decode

import nacl.utils
from nacl.public import PrivateKey, PublicKey, Box
from nacl.secret import SecretBox


def generate_keypair() -> tuple[PrivateKey, PublicKey]:
    sk = PrivateKey.generate()
    return sk, sk.public_key


def derive_shared_secret(our_sk: PrivateKey, their_pk: PublicKey) -> bytes:
    box = Box(our_sk, their_pk)
    return box.shared_key()


def ratchet_chain_key(chain_key: bytes) -> tuple[bytes, bytes]:
    """Advance the KDF chain. Returns (message_key, next_chain_key)."""
    message_key = hashlib.sha512(chain_key + b"\x01").digest()[:32]
    next_chain_key = hashlib.sha512(chain_key + b"\x02").digest()[:32]
    return message_key, next_chain_key


def encrypt(plaintext: str, key: bytes) -> str:
    box = SecretBox(key)
    ct = box.encrypt(plaintext.encode())  # nonce auto-prepended
    return b64encode(ct).decode()


def decrypt(packed: str, key: bytes) -> str | None:
    try:
        box = SecretBox(key)
        pt = box.decrypt(b64decode(packed))
        return pt.decode()
    except Exception:
        return None


def pk_to_b64(pk: PublicKey) -> str:
    return b64encode(bytes(pk)).decode()


def b64_to_pk(b64: str) -> PublicKey:
    return PublicKey(b64decode(b64))
