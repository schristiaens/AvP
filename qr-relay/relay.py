"""
Untrusted relay server.
Routes opaque encrypted blobs between peers sharing a session ID.
Never sees plaintext — just WebSocket rooms.
"""
import asyncio
import sys
from collections import defaultdict
from websockets.asyncio.server import serve, ServerConnection

rooms: dict[str, set[ServerConnection]] = defaultdict(set)


async def handler(ws: ServerConnection) -> None:
    # Session ID from URL path: ws://relay:4900/<session_id>
    session_id = ws.request.path.strip("/")  # type: ignore[union-attr]
    if not session_id:
        await ws.close(4000, "Missing session ID in URL path")
        return

    room = rooms[session_id]
    room.add(ws)
    print(f"[+] {session_id} ({len(room)} peers)")

    try:
        async for message in ws:
            # Broadcast to all OTHER peers in the same session
            for peer in room:
                if peer is not ws:
                    await peer.send(message)
    finally:
        room.discard(ws)
        if not room:
            del rooms[session_id]
        print(f"[-] {session_id} ({len(rooms.get(session_id, set()))} peers)")


async def run(port: int = 4900) -> None:
    async with serve(handler, "0.0.0.0", port):
        print(f"Relay listening on ws://localhost:{port}")
        await asyncio.Future()  # run forever


def main() -> None:
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 4900
    asyncio.run(run(port))


if __name__ == "__main__":
    main()
