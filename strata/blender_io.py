"""
Socket client for the add-on's bridge (addon/bridge_server.py, listening on
localhost:9877 by default). The ONLY file in strata/'s core (non-plugin) code
that assumes a live Blender process exists -- it still doesn't `import bpy`
itself, it's a plain TCP/JSON client, so it stays importable (and testable
with a fake server) from a machine with no Blender installed at all.
"""
from __future__ import annotations

import json
import socket
from typing import Any, Dict, Optional

DEFAULT_HOST = "localhost"
DEFAULT_PORT = 9877

_sock: Optional[socket.socket] = None
_buffer: bytes = b""


def _connect(host: str, port: int) -> bool:
    global _sock
    if _sock:
        return True
    try:
        _sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        _sock.connect((host, port))
        return True
    except OSError:
        _sock = None
        return False


def call(command: str, host: str = DEFAULT_HOST, port: int = DEFAULT_PORT, timeout: float = 120.0, **params) -> Dict[str, Any]:
    global _buffer
    if not _connect(host, port):
        raise ConnectionError(
            f"Can't reach the Strata add-on's bridge at {host}:{port}. Is Blender "
            "open with the bridge started (sidebar > Strata tab > "
            "'Start Strata Bridge')? See docs/SETUP.md."
        )
    _sock.settimeout(timeout)
    payload = json.dumps({"command": command, "params": params}) + "\n"
    _sock.sendall(payload.encode("utf-8"))

    while b"\n" not in _buffer:
        chunk = _sock.recv(65536)
        if not chunk:
            raise ConnectionError("Blender closed the bridge connection mid-response")
        _buffer += chunk
    line, _buffer = _buffer.split(b"\n", 1)
    response = json.loads(line.decode("utf-8"))
    if not response.get("ok"):
        raise RuntimeError(response.get("error", "unknown error from the Strata bridge"))
    return response.get("result")
