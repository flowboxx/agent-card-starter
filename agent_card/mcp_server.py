#!/usr/bin/env python3
"""Minimal MCP example server (stdio, JSON-RPC 2.0, Python standard library only).

Two tools:
  leistungen      list the services of the (fictional) business
  anfrage_anlegen STUB: validates input, stores nothing, returns a reference

Run:    agent-card-server   or   python3 -m agent_card.mcp_server   (stdin, one JSON per line)
Edit:   SERVICES and BUSINESS below, then replace the stub with your own intake.

A stub on purpose: a real intake needs consent text, spam protection and a human
who answers. Der Stub speichert nichts.
"""
from __future__ import annotations

import json
import sys
import uuid
from typing import Any, Dict, List, Optional

PROTOCOL_VERSION = "2025-06-18"
BUSINESS = {"name": "Beispiel Dachdecker GmbH", "url": "https://www.beispiel-dachdecker.example"}
SERVICES: List[Dict[str, str]] = [
    {"id": "dachsanierung", "name": "Dachsanierung",
     "beschreibung": "Sanierung von Steildächern, Neueindeckung, Dämmung. Raum Musterstadt."},
    {"id": "flachdach", "name": "Flachdach abdichten",
     "beschreibung": "Abdichtung und Reparatur von Flachdächern."},
]
NOTE = "Automatische Auskunft. Preise und Termine nennt ein Mensch im Betrieb."

TOOLS = [
    {
        "name": "leistungen",
        "description": "List the services of the business. Auskunft über die Leistungen des Betriebs.",
        "inputSchema": {"type": "object", "properties": {}, "additionalProperties": False},
    },
    {
        "name": "anfrage_anlegen",
        "description": "Create an inquiry (stub, nothing is stored). Anfrage anlegen (Stub, nichts wird gespeichert).",
        "inputSchema": {
            "type": "object",
            "properties": {
                "leistung": {"type": "string", "description": "id from the tool 'leistungen'"},
                "nachricht": {"type": "string", "maxLength": 1000},
                "rueckmeldung": {"type": "string", "description": "how the business may answer (e-mail or phone)"},
            },
            "required": ["leistung", "nachricht", "rueckmeldung"],
            "additionalProperties": False,
        },
    },
]


def _text(payload: Any, error: bool = False) -> Dict[str, Any]:
    return {"content": [{"type": "text", "text": json.dumps(payload, ensure_ascii=False)}], "isError": error}


def tool_leistungen(_args: Dict[str, Any]) -> Dict[str, Any]:
    return _text({"betrieb": BUSINESS["name"], "leistungen": SERVICES, "hinweis": NOTE})


def tool_anfrage_anlegen(args: Dict[str, Any]) -> Dict[str, Any]:
    ids = {s["id"] for s in SERVICES}
    problems = []
    if args.get("leistung") not in ids:
        problems.append("leistung must be one of %s" % sorted(ids))
    msg = args.get("nachricht")
    if not isinstance(msg, str) or not msg.strip() or len(msg) > 1000:
        problems.append("nachricht: 1 to 1000 characters")
    back = args.get("rueckmeldung")
    if not isinstance(back, str) or not back.strip():
        problems.append("rueckmeldung: required")
    if problems:
        return _text({"angelegt": False, "fehler": problems}, error=True)
    # STUB: replace with your own intake (store, notify a human, rate limit, consent).
    return _text({"angelegt": False, "stub": True, "referenz": "demo-" + uuid.uuid4().hex[:8],
                  "hinweis": "Stub: es wurde nichts gespeichert. " + NOTE})


HANDLERS = {"leistungen": tool_leistungen, "anfrage_anlegen": tool_anfrage_anlegen}


def _result(rid: Any, result: Any) -> Dict[str, Any]:
    return {"jsonrpc": "2.0", "id": rid, "result": result}


def _error(rid: Any, code: int, message: str) -> Dict[str, Any]:
    return {"jsonrpc": "2.0", "id": rid, "error": {"code": code, "message": message}}


def handle(msg: Any) -> Optional[Dict[str, Any]]:
    """Handle one JSON-RPC message. Returns None for notifications."""
    if not isinstance(msg, dict) or msg.get("jsonrpc") != "2.0" or "method" not in msg:
        return _error(msg.get("id") if isinstance(msg, dict) else None, -32600, "Invalid Request")
    rid, method = msg.get("id"), msg["method"]
    params = msg.get("params") or {}
    if "id" not in msg:  # notification
        return None
    if method == "initialize":
        return _result(rid, {
            "protocolVersion": PROTOCOL_VERSION,
            "capabilities": {"tools": {}},
            "serverInfo": {"name": "beispiel-dachdecker-tuer", "version": "1.0.0"},
        })
    if method == "ping":
        return _result(rid, {})
    if method == "tools/list":
        return _result(rid, {"tools": TOOLS})
    if method == "tools/call":
        name = params.get("name")
        if name not in HANDLERS:
            return _error(rid, -32602, "Unknown tool: %s" % name)
        args = params.get("arguments") or {}
        if not isinstance(args, dict):
            return _error(rid, -32602, "arguments must be an object")
        return _result(rid, HANDLERS[name](args))
    return _error(rid, -32601, "Method not found: %s" % method)


def serve(stdin=sys.stdin, stdout=sys.stdout) -> None:
    for line in stdin:
        line = line.strip()
        if not line:
            continue
        try:
            msg = json.loads(line)
        except ValueError:
            reply: Optional[Dict[str, Any]] = _error(None, -32700, "Parse error")
        else:
            reply = handle(msg)
        if reply is not None:
            stdout.write(json.dumps(reply, ensure_ascii=False) + "\n")
            stdout.flush()


def main() -> None:
    serve()


if __name__ == "__main__":
    main()
