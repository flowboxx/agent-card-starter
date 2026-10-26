# agent-card-starter

[![tests](../../actions/workflows/ci.yml/badge.svg)](../../actions/workflows/ci.yml)
![license MIT](https://img.shields.io/badge/license-MIT-blue)
![python 3.9+](https://img.shields.io/badge/python-3.9%2B-blue)

**In 60 seconds:** AI assistants read a small JSON file to learn what your business does. This tool writes that file for you and checks it. Offline, no account, no dependencies.

```bash
pip install git+https://github.com/flowboxx/agent-card-starter
agent-card init --name "Muster Roofing Ltd" --description "Roofer in Musterstadt, repairs and new roofs." --website https://www.example.com
agent-card validate .well-known/agent-card.json --strict
```

Upload the file to `https://<your-domain>/.well-known/agent-card.json` and you are readable. Nothing here guarantees that an assistant will mention you.

**In 60 Sekunden:** KI-Assistenten lesen eine kleine Datei, um zu erfahren, was Ihr Betrieb macht. Dieses Werkzeug schreibt die Datei und prüft sie. Ohne Netz, ohne Konto, ohne Fremdpakete. Befehle siehe oben, die Datei kommt nach `https://<Ihre-Domain>/.well-known/agent-card.json`.

<!-- Picture idea: a 20 second terminal recording (init, then validate with OK) of the three commands above. Fictional business only. -->

Starter kit to make a small business readable and reachable for AI assistants:
an A2A agent card, an MCP server card, a minimal MCP example server and a validator.
Standard library only, Python 3.9+, MIT licensed.

Starter-Set, damit ein kleiner Betrieb für KI-Assistenten lesbar und erreichbar wird:
Agentenkarte (A2A), Server-Karte (MCP), ein minimaler MCP-Beispielserver und ein Prüfskript.
Nur Python-Standardbibliothek, ab Python 3.9, MIT-Lizenz.

Maintained by [flowboxx](https://flowboxx.de/?ref=github), an agency that builds AI doors for businesses.
Gepflegt von [flowboxx](https://flowboxx.de/?ref=github), einer Agentur, die KI-Türen für Betriebe baut.

---

## English

### What is in here

| Path | What it is |
| --- | --- |
| `examples/well-known/agent-card.json` | A2A agent card for a fictional "Beispiel Dachdecker GmbH" |
| `examples/well-known/agent.json` | Byte-identical copy for older readers |
| `examples/agent-card.annotated.jsonc` | Same card with comments (documentation only) |
| `examples/mcp-server-card.json` | MCP server card for the same business |
| `templates/` | Blank-ish templates: server card and AI catalog |
| `server/mcp_server.py` | MCP example server over stdio: tools `leistungen` and `anfrage_anlegen` (stub) |
| `agent_card/` | The `agent-card` command: `init` writes a first card, `validate` checks card, server card and catalog (offline) |
| `tools/validate_agent_card.py` | Same validator as a plain script |
| `tests/` | pytest suite |

### Quick start

```bash
agent-card init --name "Your Business" --description "What you do and where." --website https://www.example.com
agent-card validate .well-known/agent-card.json --strict
# from a clone, without installing:
python3 tools/validate_agent_card.py examples/well-known/agent-card.json
python3 tools/validate_agent_card.py examples/mcp-server-card.json --strict
printf '{"jsonrpc":"2.0","id":1,"method":"tools/list"}\n' | python3 server/mcp_server.py
python3 -m pip install pytest && python3 -m pytest -q
docker build -t agent-card-starter . && docker run -i --rm agent-card-starter   # MCP over stdio
```

### Use it for your business

1. Copy `examples/well-known/agent-card.json`, replace name, description, provider, skills.
2. List only services you really offer. One skill per service, stable ids.
3. Keep prices, phone numbers and promises out of the card. A human answers those.
4. Run the validator, publish the file at `https://<your-domain>/.well-known/agent-card.json`.
5. Point `supportedInterfaces` at an endpoint you really operate. The example server
   speaks MCP over stdio for learning. A public endpoint needs HTTP transport,
   rate limiting, spam protection and a privacy notice. `anfrage_anlegen` is a stub on purpose.

### Notes on the standards

- The agent card follows the A2A v1.0 field names (`supportedInterfaces`, `skills`, `provider`).
- The server card follows the MCP Server Card proposal (SEP-2127). It is an extension and
  the schema may still change. Check the current schema before you publish.
- The validator checks required fields and a few sanity rules. It is not a full JSON Schema validation.
- Nothing here guarantees that an assistant will mention or recommend you.

---

## Deutsch

### Was drin ist

| Pfad | Inhalt |
| --- | --- |
| `examples/well-known/agent-card.json` | A2A-Agentenkarte für die fiktive "Beispiel Dachdecker GmbH" |
| `examples/well-known/agent.json` | Byte-gleiche Kopie für ältere Leser |
| `examples/agent-card.annotated.jsonc` | Dieselbe Karte mit Kommentaren (nur zur Erklärung) |
| `examples/mcp-server-card.json` | MCP-Server-Karte für denselben Betrieb |
| `templates/` | Vorlagen: Server-Karte und KI-Katalog |
| `server/mcp_server.py` | MCP-Beispielserver über stdio: Werkzeuge `leistungen` und `anfrage_anlegen` (Stub) |
| `agent_card/` | Der Befehl `agent-card`: `init` schreibt eine erste Karte, `validate` prüft Karte, Server-Karte und Katalog (ohne Netz) |
| `tools/validate_agent_card.py` | Dasselbe Prüfskript als einfache Datei |
| `tests/` | pytest-Tests |

### Schnellstart

```bash
agent-card init --name "Ihr Betrieb" --description "Was Sie tun und wo." --website https://www.example.com
agent-card validate .well-known/agent-card.json --strict
# aus einem Klon, ohne Installation:
python3 tools/validate_agent_card.py examples/well-known/agent-card.json
python3 tools/validate_agent_card.py examples/mcp-server-card.json --strict
printf '{"jsonrpc":"2.0","id":1,"method":"tools/list"}\n' | python3 server/mcp_server.py
python3 -m pip install pytest && python3 -m pytest -q
docker build -t agent-card-starter . && docker run -i --rm agent-card-starter   # MCP over stdio
```

### Für den eigenen Betrieb nutzen

1. `examples/well-known/agent-card.json` kopieren, Name, Beschreibung, Anbieter und Fähigkeiten ersetzen.
2. Nur Leistungen eintragen, die Sie wirklich anbieten. Eine Fähigkeit je Leistung, stabile Ids.
3. Keine Preise, Telefonnummern oder Zusagen in die Karte. Das beantwortet ein Mensch.
4. Prüfskript laufen lassen, Datei unter `https://<Ihre-Domain>/.well-known/agent-card.json` ablegen.
5. `supportedInterfaces` auf einen Endpunkt zeigen lassen, den Sie wirklich betreiben. Der Beispielserver
   spricht MCP über stdio zum Lernen. Ein öffentlicher Endpunkt braucht HTTP, Mengenbegrenzung,
   Spam-Schutz und einen Datenschutzhinweis. `anfrage_anlegen` ist absichtlich ein Stub und speichert nichts.

### Hinweise zu den Standards

- Die Agentenkarte folgt den Feldnamen von A2A v1.0 (`supportedInterfaces`, `skills`, `provider`).
- Die Server-Karte folgt dem MCP-Vorschlag Server Card (SEP-2127). Das ist eine Erweiterung,
  das Schema kann sich noch ändern. Vor dem Veröffentlichen das aktuelle Schema prüfen.
- Das Prüfskript prüft Pflichtfelder und einige Plausibilitäten, keine vollständige JSON-Schema-Validierung.
- Nichts hier garantiert, dass ein Assistent Sie nennt oder empfiehlt.

---

## Built with this? Tell us / Damit gebaut? Erzählen Sie es uns

If you published a card with this kit, show it in [Discussions, Show and tell](../../discussions/categories/show-and-tell). We read every one. If you like, add the badge to your README:

Wenn Sie mit diesem Kit eine Karte veröffentlicht haben, zeigen Sie sie unter [Discussions, Show and tell](../../discussions/categories/show-and-tell). Das Abzeichen für Ihre README:

```markdown
[![built with agent-card-starter](https://img.shields.io/badge/built%20with-agent--card--starter-2b6cb0)](https://github.com/flowboxx/agent-card-starter)
```

---

## As is / Ohne Gewähr

This is a starting point, provided "as is" under the MIT license, without warranty of any kind. Standards around agent cards and server cards are young and change. Check the current specifications before you publish. Nothing here is legal advice, and nothing guarantees that an assistant will mention or recommend your business. Changes are listed in [CHANGELOG.md](CHANGELOG.md), how to help is in [CONTRIBUTING.md](CONTRIBUTING.md).

Dies ist ein Ausgangspunkt, bereitgestellt "wie besehen" unter der MIT-Lizenz, ohne Gewähr. Die Standards rund um Agentenkarten und Server-Karten sind jung und ändern sich. Prüfen Sie vor dem Veröffentlichen die aktuellen Spezifikationen. Nichts hier ist Rechtsberatung, und nichts garantiert, dass ein Assistent Ihren Betrieb nennt oder empfiehlt. Änderungen stehen in [CHANGELOG.md](CHANGELOG.md), Mitmachen steht in [CONTRIBUTING.md](CONTRIBUTING.md).

MIT License, see `LICENSE`. Questions and contributions welcome via issues. Fragen und Beiträge gern als Issue.

Built and maintained by [flowboxx](https://flowboxx.de/?ref=github), Germany.
