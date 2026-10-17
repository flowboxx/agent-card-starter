import io
import json
import os
import subprocess
import sys

import mcp_server as s

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def call(method, params=None, rid=1):
    return s.handle({"jsonrpc": "2.0", "id": rid, "method": method, "params": params or {}})


def payload(res):
    return json.loads(res["result"]["content"][0]["text"])


def test_initialize():
    r = call("initialize")
    assert r["result"]["protocolVersion"] == s.PROTOCOL_VERSION
    assert "tools" in r["result"]["capabilities"]


def test_notification_has_no_reply():
    assert s.handle({"jsonrpc": "2.0", "method": "notifications/initialized"}) is None


def test_tools_list_names():
    names = [t["name"] for t in call("tools/list")["result"]["tools"]]
    assert names == ["leistungen", "anfrage_anlegen"]


def test_leistungen():
    p = payload(call("tools/call", {"name": "leistungen", "arguments": {}}))
    assert p["leistungen"] and "Mensch" in p["hinweis"]


def test_anfrage_is_stub_and_validates():
    ok = payload(call("tools/call", {"name": "anfrage_anlegen", "arguments": {
        "leistung": "flachdach", "nachricht": "Dach undicht", "rueckmeldung": "a@b.example"}}))
    assert ok["stub"] is True and ok["angelegt"] is False and ok["referenz"].startswith("demo-")
    bad = call("tools/call", {"name": "anfrage_anlegen", "arguments": {"leistung": "nix", "nachricht": ""}})
    assert bad["result"]["isError"] is True
    assert len(payload(bad)["fehler"]) == 3


def test_unknown_tool_and_method_and_invalid_request():
    assert call("tools/call", {"name": "nope"})["error"]["code"] == -32602
    assert call("nope")["error"]["code"] == -32601
    assert s.handle({"hello": 1})["error"]["code"] == -32600


def test_serve_handles_garbage_lines():
    out = io.StringIO()
    inp = io.StringIO('not json\n\n{"jsonrpc":"2.0","id":7,"method":"ping"}\n')
    s.serve(inp, out)
    lines = [json.loads(x) for x in out.getvalue().splitlines()]
    assert lines[0]["error"]["code"] == -32700 and lines[1]["id"] == 7


def test_stdio_roundtrip():
    req = '{"jsonrpc":"2.0","id":1,"method":"tools/list"}\n'
    r = subprocess.run([sys.executable, os.path.join(ROOT, "server", "mcp_server.py")],
                       input=req, capture_output=True, text=True, timeout=20)
    assert json.loads(r.stdout)["result"]["tools"]


def test_card_matches_server_tools_story():
    # the example card promises an 'anfrage' skill, the server offers the tool
    card = json.load(open(os.path.join(ROOT, "examples", "well-known", "agent-card.json"), encoding="utf-8"))
    assert "anfrage" in [x["id"] for x in card["skills"]]
