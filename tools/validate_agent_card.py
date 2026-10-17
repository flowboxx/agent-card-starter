#!/usr/bin/env python3
"""Validate an A2A Agent Card, an MCP Server Card or an AI catalog (offline, stdlib only).

Usage:
    python3 tools/validate_agent_card.py path/to/agent-card.json
    python3 tools/validate_agent_card.py card.json --type server-card --strict

Exit code 0 = valid (warnings allowed), 1 = errors found (or warnings with --strict).

This is a pragmatic subset check of the required fields, not a full JSON Schema
validation. Standards move: check the official specs before you rely on it.
Nützlich zum schnellen Prüfen der Pflichtfelder, ersetzt keine Volltest-Validierung.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from typing import Any, List, Tuple

KNOWN_BINDINGS = {"JSONRPC", "GRPC", "HTTP+JSON", "MCP"}
SEMVER = re.compile(r"^\d+\.\d+\.\d+([-+][0-9A-Za-z.-]+)?$")
MEDIA_TYPE = re.compile(r"^[A-Za-z0-9.+-]+/[A-Za-z0-9.+-]+$")
EURO = re.compile(r"(€|\bEUR\b|\bEuro\b)", re.IGNORECASE)
PHONE = re.compile(r"(\+\d{2}[\d\s/()-]{6,}|\b0\d{2,5}[\s/-]?\d{4,})")
EMAIL = re.compile(r"[\w.+-]+@[\w-]+\.[\w.-]+")
CATALOG_TYPES = {"application/a2a-agent-card+json", "application/mcp-server-card+json"}


def strip_comments(text: str) -> str:
    """Remove // line comments and /* block */ comments outside of strings (JSONC)."""
    out: List[str] = []
    i, n = 0, len(text)
    in_str = False
    while i < n:
        c = text[i]
        if in_str:
            out.append(c)
            if c == "\\" and i + 1 < n:
                out.append(text[i + 1])
                i += 1
            elif c == '"':
                in_str = False
        elif c == '"':
            in_str = True
            out.append(c)
        elif text.startswith("//", i):
            while i < n and text[i] != "\n":
                i += 1
            continue
        elif text.startswith("/*", i):
            end = text.find("*/", i + 2)
            i = n if end == -1 else end + 2
            continue
        else:
            out.append(c)
        i += 1
    return "".join(out)


def load(path: str) -> Any:
    with open(path, encoding="utf-8") as fh:
        return json.loads(strip_comments(fh.read()))


def _is_str(v: Any) -> bool:
    return isinstance(v, str) and v.strip() != ""


def _https(v: Any) -> bool:
    return _is_str(v) and v.startswith("https://") and " " not in v


def detect_type(doc: Any) -> str:
    if isinstance(doc, dict):
        if "entries" in doc:
            return "catalog"
        if "remotes" in doc or "$schema" in doc:
            return "server-card"
    return "agent-card"


def _texts(doc: Any):
    if isinstance(doc, dict):
        for k, v in doc.items():
            if k in ("url", "$schema", "websiteUrl", "documentationUrl", "identifier"):
                continue
            yield from _texts(v)
    elif isinstance(doc, list):
        for v in doc:
            yield from _texts(v)
    elif isinstance(doc, str):
        yield doc


def content_warnings(doc: Any) -> List[str]:
    w: List[str] = []
    for t in _texts(doc):
        if EURO.search(t):
            w.append("price/currency in card text (%r): prices belong to a human offer" % t[:40])
        if PHONE.search(t):
            w.append("phone number in card text (%r)" % t[:40])
        if EMAIL.search(t):
            w.append("e-mail address in card text (%r)" % t[:40])
    return w


def validate_agent_card(d: Any) -> Tuple[List[str], List[str]]:
    e: List[str] = []
    w: List[str] = []
    if not isinstance(d, dict):
        return ["top level must be a JSON object"], w
    for k in ("name", "description", "version"):
        if not _is_str(d.get(k)):
            e.append("%s: required, non-empty string" % k)
    if _is_str(d.get("version")) and not SEMVER.match(d["version"]):
        w.append("version %r is not semver (x.y.z)" % d["version"])
    ifaces = d.get("supportedInterfaces")
    if not isinstance(ifaces, list) or not ifaces:
        e.append("supportedInterfaces: required, at least one entry")
    else:
        for i, it in enumerate(ifaces):
            p = "supportedInterfaces[%d]" % i
            if not isinstance(it, dict):
                e.append(p + ": must be an object")
                continue
            if not _https(it.get("url")):
                e.append(p + ".url: required, https URL")
            if not _is_str(it.get("protocolBinding")):
                e.append(p + ".protocolBinding: required")
            elif it["protocolBinding"] not in KNOWN_BINDINGS:
                w.append("%s.protocolBinding %r not in %s" % (p, it["protocolBinding"], sorted(KNOWN_BINDINGS)))
            if not _is_str(it.get("protocolVersion")):
                e.append(p + ".protocolVersion: required")
    prov = d.get("provider")
    if not isinstance(prov, dict):
        w.append("provider: recommended (organization, url)")
    else:
        if not _is_str(prov.get("organization")):
            e.append("provider.organization: required when provider is given")
        if not _https(prov.get("url")):
            e.append("provider.url: required when provider is given, https URL")
    if "documentationUrl" in d and not _https(d["documentationUrl"]):
        e.append("documentationUrl: must be an https URL")
    if not isinstance(d.get("capabilities"), dict):
        e.append("capabilities: required object (may be empty)")
    for k in ("defaultInputModes", "defaultOutputModes"):
        v = d.get(k)
        if not isinstance(v, list) or not v:
            e.append("%s: required, non-empty list of media types" % k)
        else:
            for m in v:
                if not (isinstance(m, str) and MEDIA_TYPE.match(m)):
                    e.append("%s: %r is not a media type" % (k, m))
    skills = d.get("skills")
    if not isinstance(skills, list) or not skills:
        e.append("skills: required, at least one skill")
    else:
        seen = set()
        for i, s in enumerate(skills):
            p = "skills[%d]" % i
            if not isinstance(s, dict):
                e.append(p + ": must be an object")
                continue
            for k in ("id", "name", "description"):
                if not _is_str(s.get(k)):
                    e.append("%s.%s: required, non-empty string" % (p, k))
            tags = s.get("tags")
            if not isinstance(tags, list) or not tags or not all(_is_str(t) for t in tags):
                e.append(p + ".tags: required, non-empty list of strings")
            if _is_str(s.get("id")):
                if s["id"] in seen:
                    e.append("%s.id %r is duplicated" % (p, s["id"]))
                seen.add(s["id"])
    w.extend(content_warnings(d))
    return e, w


def validate_server_card(d: Any) -> Tuple[List[str], List[str]]:
    e: List[str] = []
    w: List[str] = []
    if not isinstance(d, dict):
        return ["top level must be a JSON object"], w
    for k in ("$schema", "name", "version", "description"):
        if not _is_str(d.get(k)):
            e.append("%s: required, non-empty string" % k)
    if _is_str(d.get("version")) and not SEMVER.match(d["version"]):
        w.append("version %r is not semver (x.y.z)" % d["version"])
    if "websiteUrl" in d and not _https(d["websiteUrl"]):
        e.append("websiteUrl: must be an https URL")
    remotes = d.get("remotes")
    if remotes is None:
        w.append("remotes: none given, assistants cannot connect")
    elif not isinstance(remotes, list) or not remotes:
        e.append("remotes: must be a non-empty list")
    else:
        for i, r in enumerate(remotes):
            p = "remotes[%d]" % i
            if not isinstance(r, dict):
                e.append(p + ": must be an object")
                continue
            if r.get("type") not in ("streamable-http", "sse"):
                e.append(p + ".type: must be 'streamable-http' or 'sse'")
            if not _https(r.get("url")):
                e.append(p + ".url: required, https URL")
    w.extend(content_warnings(d))
    return e, w


def validate_catalog(d: Any) -> Tuple[List[str], List[str]]:
    e: List[str] = []
    w: List[str] = []
    if not isinstance(d, dict):
        return ["top level must be a JSON object"], w
    if not _is_str(d.get("specVersion")):
        e.append("specVersion: required")
    entries = d.get("entries")
    if not isinstance(entries, list) or not entries:
        e.append("entries: required, at least one entry")
        return e, w
    ids = set()
    for i, it in enumerate(entries):
        p = "entries[%d]" % i
        if not isinstance(it, dict):
            e.append(p + ": must be an object")
            continue
        if not _is_str(it.get("identifier")):
            e.append(p + ".identifier: required")
        elif it["identifier"] in ids:
            e.append("%s.identifier %r is duplicated" % (p, it["identifier"]))
        else:
            ids.add(it["identifier"])
        if it.get("type") not in CATALOG_TYPES:
            w.append("%s.type %r is not one of %s" % (p, it.get("type"), sorted(CATALOG_TYPES)))
        if not _https(it.get("url")):
            e.append(p + ".url: required, https URL")
    return e, w


def validate(doc: Any, kind: str = "auto") -> Tuple[List[str], List[str]]:
    if kind == "auto":
        kind = detect_type(doc)
    return {"agent-card": validate_agent_card, "server-card": validate_server_card,
            "catalog": validate_catalog}[kind](doc)


def main(argv: List[str] = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("file")
    ap.add_argument("--type", choices=["auto", "agent-card", "server-card", "catalog"], default="auto")
    ap.add_argument("--strict", action="store_true", help="treat warnings as errors")
    a = ap.parse_args(argv)
    try:
        doc = load(a.file)
    except (OSError, ValueError) as ex:
        print("ERROR cannot read %s: %s" % (a.file, ex))
        return 1
    errors, warnings = validate(doc, a.type)
    for m in errors:
        print("ERROR  " + m)
    for m in warnings:
        print("WARN   " + m)
    if errors or (a.strict and warnings):
        print("INVALID: %d error(s), %d warning(s)" % (len(errors), len(warnings)))
        return 1
    print("OK: %s (%d warning(s))" % (a.file, len(warnings)))
    return 0


if __name__ == "__main__":
    sys.exit(main())
