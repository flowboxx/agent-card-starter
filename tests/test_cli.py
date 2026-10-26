import json
import os
import subprocess
import sys

from agent_card import cli, validator

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def test_init_writes_a_valid_card_without_warnings(tmp_path, capsys):
    rc = cli.main(["init", "--name", 'Muster "Dach" GmbH', "--description", "Dachdecker in Musterstadt.", "--website", "https://www.beispiel.example/", "--out", str(tmp_path)])
    assert rc == 0
    p = tmp_path / ".well-known" / "agent-card.json"
    card = json.loads(p.read_text(encoding="utf-8"))
    assert card["name"] == 'Muster "Dach" GmbH' and card["provider"]["url"] == "https://www.beispiel.example"
    assert card["supportedInterfaces"][0]["url"] == "https://www.beispiel.example/mcp"
    assert validator.validate(card, "agent-card") == ([], [])
    assert "Wrote" in capsys.readouterr().out


def test_init_refuses_to_overwrite_and_rejects_bad_url(tmp_path):
    args = ["init", "--name", "A", "--description", "B", "--website", "https://x.example", "--out", str(tmp_path)]
    assert cli.main(args) == 0
    assert cli.main(args) == 1
    assert cli.main(args + ["--force"]) == 0
    bad = ["init", "--name", "A", "--description", "B", "--website", "http://x.example", "--out", str(tmp_path / "n")]
    assert cli.main(bad) == 1 and not (tmp_path / "n").exists()


def test_validate_subcommand_and_old_script_agree():
    card = os.path.join(ROOT, "examples", "well-known", "agent-card.json")
    assert cli.main(["validate", card]) == 0
    r = subprocess.run([sys.executable, os.path.join(ROOT, "tools", "validate_agent_card.py"), card], capture_output=True, text=True)
    assert r.returncode == 0 and r.stdout.startswith("OK")
    r = subprocess.run([sys.executable, "-m", "agent_card", "validate", card, "--strict"], capture_output=True, text=True, cwd=ROOT)
    assert r.returncode == 0


def test_package_carries_its_template():
    assert "{name}" in cli._template()


def test_init_skills_become_stable_ids_and_keep_the_inquiry_skill_last(tmp_path):
    args = ["init", "--name", "A", "--description", "B", "--website", "https://x.example", "--out", str(tmp_path),
            "--skill", "Flachdach abdichten", "--skill", "Dämmung: Dach und Keller dämmen.", "--skill", "Flachdach abdichten"]
    assert cli.main(args) == 0
    card = json.loads((tmp_path / ".well-known" / "agent-card.json").read_text(encoding="utf-8"))
    ids = [s["id"] for s in card["skills"]]
    assert ids == ["flachdach-abdichten", "daemmung", "flachdach-abdichten-2", "anfrage"]
    assert card["skills"][1]["description"] == "Dach und Keller dämmen." and validator.validate(card, "agent-card") == ([], [])
