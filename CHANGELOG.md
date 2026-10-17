# Changelog

All notable changes are listed here. Format: [Keep a Changelog](https://keepachangelog.com), versions follow [SemVer](https://semver.org).
Alle wichtigen Änderungen stehen hier. Format wie Keep a Changelog, Versionen nach SemVer.

## [0.1.0] - 2026-10-17

First public release / Erste öffentliche Fassung.

### Added
- A2A agent card example (v1.0 field names) for a fictional business, plus a byte-identical `agent.json` copy and a commented variant.
- MCP server card example and blank templates for server card and AI catalog.
- Minimal MCP example server over stdio (standard library only) with the tools `leistungen` and `anfrage_anlegen` (stub, stores nothing).
- Offline validator for agent card, server card and catalog, with `--strict`.
- pytest suite and a GitHub Actions workflow (Python 3.9 to 3.13, no external services).
- English and German README.
