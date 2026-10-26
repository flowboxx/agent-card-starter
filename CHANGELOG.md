# Changelog

All notable changes are listed here. Format: [Keep a Changelog](https://keepachangelog.com), versions follow [SemVer](https://semver.org).
Alle wichtigen Änderungen stehen hier. Format wie Keep a Changelog, Versionen nach SemVer.

## [0.2.1] - 2026-10-26

### Added
- Command `agent-card-server`: the example MCP server (stdio) now ships inside the package, so `uvx agent-card-starter` style launchers and the official MCP Registry can start it. `server/mcp_server.py` stays as a thin wrapper.
- `server.json` and the `mcp-name` marker for the official MCP Registry. Package on PyPI: `pip install agent-card-starter`.

## [0.2.0] - 2026-10-26

### Added
- Installable package `agent-card-starter` with the command `agent-card`: `init` writes a first agent card, `validate` checks cards (same checks as before).
- Discussions form "Show and tell" and a "Built with this? Tell us" section in the README.

### Changed
- The validator now lives in `agent_card/validator.py`. `tools/validate_agent_card.py` stays as a thin wrapper, the old command keeps working.

### Fixed
- The hygiene test no longer fails on `glama.json` (it must name the maintainer account). The CI run after the Glama commit was red because of that.

## [0.1.1] - 2026-10-17

### Added
- Dockerfile for the example MCP server (python:3.12-slim, stdio, non-root) and a CI job that builds it and checks `initialize` and `tools/list`.

## [0.1.0] - 2026-10-17

First public release / Erste öffentliche Fassung.

### Added
- A2A agent card example (v1.0 field names) for a fictional business, plus a byte-identical `agent.json` copy and a commented variant.
- MCP server card example and blank templates for server card and AI catalog.
- Minimal MCP example server over stdio (standard library only) with the tools `leistungen` and `anfrage_anlegen` (stub, stores nothing).
- Offline validator for agent card, server card and catalog, with `--strict`.
- pytest suite and a GitHub Actions workflow (Python 3.9 to 3.13, no external services).
- English and German README.
