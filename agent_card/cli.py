"""Command line: `agent-card validate FILE` and `agent-card init`. Standard library only."""
import argparse
import json
import os
import sys
from importlib import resources

from agent_card import __version__, validator


def _template() -> str:
    return resources.files("agent_card").joinpath("data/agent-card.template.json").read_text(encoding="utf-8")


def build_card(name: str, description: str, website: str, endpoint: str) -> dict:
    """Fill the template. Values go through json so quotes in names cannot break the file."""
    card = json.loads(_template())

    def fill(x):
        if isinstance(x, str):
            return x.replace("{name}", name).replace("{description}", description).replace("{website}", website).replace("{endpoint}", endpoint)
        if isinstance(x, list):
            return [fill(i) for i in x]
        if isinstance(x, dict):
            return {k: fill(v) for k, v in x.items()}
        return x
    return fill(card)


def cmd_init(a) -> int:
    website = a.website.rstrip("/")
    endpoint = a.endpoint or website + "/mcp"
    card = build_card(a.name, a.description, website, endpoint)
    errors, warnings = validator.validate(card, "agent-card")
    if errors:
        for m in errors:
            print("ERROR  " + m)
        return 1
    target = os.path.join(a.out, ".well-known", "agent-card.json")
    if os.path.exists(target) and not a.force:
        print("ERROR  %s exists already (use --force to overwrite)" % target)
        return 1
    os.makedirs(os.path.dirname(target), exist_ok=True)
    with open(target, "w", encoding="utf-8") as f:
        json.dump(card, f, ensure_ascii=False, indent=2)
        f.write("\n")
    for m in warnings:
        print("WARN   " + m)
    print("Wrote %s" % target)
    print("Next: add one skill per service you really offer, keep prices and phone numbers out,")
    print("point supportedInterfaces at an endpoint you really operate, run `agent-card validate %s`," % target)
    print("then publish the file at %s/.well-known/agent-card.json" % website)
    return 0


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(prog="agent-card", description="Make a small business readable for AI assistants.")
    ap.add_argument("--version", action="version", version="agent-card-starter " + __version__)
    sub = ap.add_subparsers(dest="cmd", required=True)
    v = sub.add_parser("validate", help="check an agent card, server card or catalog (offline)")
    v.add_argument("file")
    v.add_argument("--type", choices=["auto", "agent-card", "server-card", "catalog"], default="auto")
    v.add_argument("--strict", action="store_true", help="treat warnings as errors")
    i = sub.add_parser("init", help="write a first agent card to <out>/.well-known/agent-card.json")
    i.add_argument("--name", required=True, help="business name")
    i.add_argument("--description", required=True, help="one or two sentences: what you do and where")
    i.add_argument("--website", required=True, help="https URL of your website")
    i.add_argument("--endpoint", default="", help="https URL of an endpoint you really operate (default: <website>/mcp)")
    i.add_argument("--out", default=".", help="folder to write into (default: current folder)")
    i.add_argument("--force", action="store_true", help="overwrite an existing card")
    a = ap.parse_args(argv)
    if a.cmd == "validate":
        extra = [a.file, "--type", a.type] + (["--strict"] if a.strict else [])
        return validator.main(extra)
    return cmd_init(a)


if __name__ == "__main__":
    sys.exit(main())
