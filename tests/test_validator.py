import copy
import json
import os
import subprocess
import sys

import pytest

import validate_agent_card as v

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CARD = os.path.join(ROOT, "examples", "well-known", "agent-card.json")


def card():
    return v.load(CARD)


def test_example_card_is_valid_without_warnings():
    e, w = v.validate(card())
    assert e == [] and w == []


def test_agent_json_copy_is_identical():
    a = open(CARD, "rb").read()
    b = open(os.path.join(ROOT, "examples", "well-known", "agent.json"), "rb").read()
    assert a == b


def test_annotated_file_equals_plain_json():
    annotated = v.load(os.path.join(ROOT, "examples", "agent-card.annotated.jsonc"))
    assert annotated == card()


def test_server_card_and_catalog_templates_are_valid():
    for f in ("templates/mcp-server-card.template.json", "examples/mcp-server-card.json",
              "templates/ai-catalog.template.json"):
        e, w = v.validate(v.load(os.path.join(ROOT, f)))
        assert e == [] and w == [], f


@pytest.mark.parametrize("field", ["name", "description", "version", "supportedInterfaces",
                                   "capabilities", "defaultInputModes", "defaultOutputModes", "skills"])
def test_missing_required_field_is_error(field):
    c = card()
    del c[field]
    e, _ = v.validate(c)
    assert any(x.startswith(field) for x in e)


def test_http_url_rejected():
    c = card()
    c["supportedInterfaces"][0]["url"] = "http://tuer.example/mcp"
    e, _ = v.validate(c)
    assert any("https" in x for x in e)


def test_skill_without_tags_and_duplicate_id():
    c = card()
    c["skills"][0].pop("tags")
    c["skills"][1]["id"] = c["skills"][2]["id"]
    e, _ = v.validate(c)
    assert any("tags" in x for x in e) and any("duplicated" in x for x in e)


def test_unknown_binding_and_bad_version_are_warnings_only():
    c = card()
    c["supportedInterfaces"][0]["protocolBinding"] = "CARRIERPIGEON"
    c["version"] = "one"
    e, w = v.validate(c)
    assert e == [] and len(w) == 2


@pytest.mark.parametrize("text", ["ab 99 Euro pro Stunde", "Preis 50 €", "Tel +49 2361 123456", "info@firma.example"])
def test_price_phone_mail_in_text_warn(text):
    c = copy.deepcopy(card())
    c["skills"][0]["description"] = text
    e, w = v.validate(c)
    assert e == [] and w


def test_non_object_is_error():
    e, _ = v.validate([], "agent-card")
    assert e


def test_comment_stripper_keeps_urls_in_strings():
    txt = '{"u": "https://x.example/a//b", /* c */ "k": 1} // end'
    assert json.loads(v.strip_comments(txt)) == {"u": "https://x.example/a//b", "k": 1}


def test_server_card_needs_schema_and_remote_type():
    d = v.load(os.path.join(ROOT, "examples", "mcp-server-card.json"))
    d.pop("$schema")
    d["remotes"][0]["type"] = "carrier"
    e, _ = v.validate(d)
    assert any("$schema" in x for x in e) and any("type" in x for x in e)


def test_catalog_duplicate_identifier():
    d = v.load(os.path.join(ROOT, "templates", "ai-catalog.template.json"))
    d["entries"][1]["identifier"] = d["entries"][0]["identifier"]
    e, _ = v.validate(d)
    assert any("duplicated" in x for x in e)


def test_cli_exit_codes(tmp_path):
    script = os.path.join(ROOT, "tools", "validate_agent_card.py")
    ok = subprocess.run([sys.executable, script, CARD], capture_output=True, text=True)
    assert ok.returncode == 0 and "OK" in ok.stdout
    bad = tmp_path / "bad.json"
    bad.write_text('{"name": "x"}')
    r = subprocess.run([sys.executable, script, str(bad)], capture_output=True, text=True)
    assert r.returncode == 1 and "INVALID" in r.stdout
    r = subprocess.run([sys.executable, script, str(tmp_path / "missing.json")], capture_output=True, text=True)
    assert r.returncode == 1
