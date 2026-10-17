"""Public repo hygiene: no internal names, paths, servers, no hint on how we build."""
import os
import re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FORBIDDEN = [r"/Users/", r"/opt/", r"\bserverb\b", r"\bservera\b", r"\.claude", r"memory/",
             r"\bDPI\b", r"Tafelpr", r"Anthropic", r"ChatGPT", r"\bClaude\b", r"\bKimi\b",
             r"mit KI (gebaut|erstellt|geschrieben)", r"KI-generiert", r"cockpit", r"Sentinal",
             r"Frieda", r"Enrico", "—", "–"]


def files():
    for d, dirs, fs in os.walk(ROOT):
        dirs[:] = [x for x in dirs if x not in (".git", "__pycache__", ".pytest_cache")]
        for f in fs:
            if f == "test_hygiene.py" or f.endswith(".pyc"):
                continue
            yield os.path.join(d, f)


def test_no_forbidden_terms_in_any_file():
    hits = []
    for p in files():
        txt = open(p, encoding="utf-8").read()
        for pat in FORBIDDEN:
            if re.search(pat, txt):
                hits.append((os.path.relpath(p, ROOT), pat))
    assert hits == []


def test_license_is_mit():
    assert "MIT License" in open(os.path.join(ROOT, "LICENSE")).read()
