<p align="center">
  <strong>🇬🇧 English</strong> · <a href="README.zh-CN.md"><strong>🇨🇳 中文</strong></a>
</p>

# asc-changelog-release-notes

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

An **agent skill** that automates the App Store release-notes pipeline — from git history to App Store Connect — in one pass: commit analysis → user-facing polish → multi-language translation → `ChangeLog` update → `whatsNew` metadata → `asc` push.

## Features

- **Commit-driven** — analyzes the git history between two tags and groups changes into features, fixes, and maintenance.
- **User-facing polish** — rewrites developer-oriented output (no "refactor", "migration", "enum") into concise, benefit-focused release notes.
- **29 languages** in `ChangeLog`, **16 App Store locales** in metadata — kept in a consistent, documented order.
- **Safe by default** — every remote change is dry-run previewed first and requires explicit user confirmation; `--allow-deletes` is never used unless asked.
- **Timeout-resilient** — recovers cleanly from `asc` timeouts without assuming partial rollback.
- **Source-driven translation** — Simplified Chinese is the canonical source; English is the primary translation target.

## How it works

```
git commits ──▶ raw changelog ──▶ polished notes ──▶ 29-language ChangeLog
                                                       │
                                              16-locale whatsNew
                                                       │
                                              validate ─▶ dry run ─▶ push
```

## Dependencies

| Dependency | Purpose | Install |
|---|---|---|
| [`asc`](https://asccli.sh) (≥ 3.x) | App Store Connect API CLI | `brew install asc` |
| `python3` | Commit analysis script (`scripts/generate_changelog.py`) | system tool |
| `git` | Commit history analysis | system tool |

### Authentication

`asc` uses App Store Connect API keys:

```bash
asc auth login                    # interactive; stores in keychain
# or environment variables:
export ASC_KEY_ID=...
export ASC_ISSUER_ID=...
export ASC_PRIVATE_KEY_PATH=...
export ASC_APP_ID=6758697856      # default app ID used by the skill
```

## Installation

```bash
git clone https://github.com/hytaoist/asc-changelog-release-notes.git
```

Link the skill into your agent's skills directory:

```bash
mkdir -p ~/.claude/skills ~/.agents/skills
ln -s "$PWD/asc-changelog-release-notes" ~/.claude/skills/asc-changelog-release-notes
# or:
ln -s "$PWD/asc-changelog-release-notes" ~/.agents/skills/asc-changelog-release-notes
```

> Agents that support installing skills by URL (e.g., opencode) can reference this repository directly.

## Repository conventions

The skill assumes the consuming app repo follows these conventions:

- `ChangeLog` — human-facing, multi-language release history at the repo root
- `AppStoreConnect/metadata/version/<version>/<locale>.json` — per-version App Store metadata
- `AppStoreConnect/metadata/app-info/` — app-level metadata (name, subtitle, privacy policy URL)
- For a new version, metadata is copied from the previous version and **only `whatsNew` is updated**, unless the user explicitly asks to change other fields.

## Usage

Trigger the skill with a natural-language request, for example:

> Generate release notes for version 1.16.4 and update App Store Connect.

The skill will:

1. Find the latest git tag and determine the commit range.
2. Run `python3 scripts/generate_changelog.py <start> HEAD "<version>"` for a raw changelog.
3. Polish the raw output into user-facing release notes (source language: `zh-Hans`).
4. Translate into all 29 `ChangeLog` languages.
5. Insert the new version block at the top of `ChangeLog`.
6. Create `AppStoreConnect/metadata/version/<version>/` (copied from the previous version) and update only `whatsNew` in all 16 locales.
7. Validate locally: `asc metadata validate --dir ./AppStoreConnect/metadata --output table`.
8. Dry-run the push: `asc metadata push --app "$ASC_APP_ID" --version <v> --platform IOS --dir ... --dry-run`.
9. Apply the push **only after explicit user confirmation**.

## Repository structure

```
asc-changelog-release-notes/
├── SKILL.md                      # The skill definition
├── README.md                     # This file (English)
├── README.zh-CN.md               # Chinese version
├── LICENSE                       # MIT License
└── scripts/
    └── generate_changelog.py     # Raw commit → changelog analysis script
```

## Safety

- Never pushes to App Store Connect without a dry-run preview and explicit user confirmation.
- Never deletes remote locales unless explicitly requested (`--allow-deletes` is off by default).
- Release-note work only modifies `whatsNew`; all other metadata fields are preserved.
- Release notes must be user-facing, never developer-oriented.

## Contributing

Issues and pull requests are welcome.

## License

[MIT](LICENSE) © 2026 hytaoist
