"""
Machine CLI — generates keypair, shows QR code, waits for phone to connect.

Usage: python machine.py [relay_url]
  Displays a QR code in the terminal. Scan it with the web app.
  Once paired, you have an encrypted bidirectional channel.
"""
import asyncio
import json
import os
import secrets
import sys

import qrcode
from websockets.asyncio.client import connect

from crypto_utils import (
    generate_keypair, derive_shared_secret, ratchet_chain_key,
    encrypt, decrypt, pk_to_b64, b64_to_pk,
)

RELAY_URL = os.environ.get("RELAY_URL", "ws://localhost:4900")


async def main() -> None:
    relay = sys.argv[1] if len(sys.argv) > 1 else RELAY_URL

    sk, pk = generate_keypair()
    session_id = secrets.token_hex(16)

    qr_payload = json.dumps({
        "r": relay, "s": session_id, "k": pk_to_b64(pk), "v": 1,
    }, separators=(",", ":"))

    print("\n  Scan this QR code with the web app to pair:\n")
    qr = qrcode.QRCode(box_size=1, border=1)
    qr.add_data(qr_payload)
    qr.print_ascii(invert=True)
    print(f"\n  Session: {session_id}")
    print("  Waiting for peer...\n")

    chain_key: bytes | None = None

    async with connect(f"{relay}/{session_id}") as ws:

        async def recv_loop() -> None:
            nonlocal chain_key
            async for raw in ws:
                msg = json.loads(raw)

                if msg["type"] == "handshake" and chain_key is None:
                    phone_pk = b64_to_pk(msg["publicKey"])
                    chain_key = derive_shared_secret(sk, phone_pk)
                    await ws.send(json.dumps({"type": "handshake-ack"}))
                    print("  Paired! Encrypted channel established.")
                    print("  Type a message and press Enter to send.\n")

                elif msg["type"] == "encrypted" and chain_key is not None:
                    mk, chain_key = ratchet_chain_key(chain_key)
                    text = decrypt(msg["payload"], mk)
                    if text:
                        print(f"\r  phone> {text}")
                        print("  you> ", end="", flush=True)
                    else:
                        print("  [decryption failed]")

        async def send_loop() -> None:
            nonlocal chain_key
            loop = asyncio.get_event_loop()
            while True:
                line = await loop.run_in_executor(None, sys.stdin.readline)
                if not line:
                    break
                line = line.strip()
                if not line or chain_key is None:
                    continue
                mk, chain_key = ratchet_chain_key(chain_key)
                payload = encrypt(line, mk)
                await ws.send(json.dumps({"type": "encrypted", "payload": payload}))
                print("  you> ", end="", flush=True)

        await asyncio.gather(recv_loop(), send_loop())


if __name__ == "__main__":
    asyncio.run(main())
