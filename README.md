<p align="center">
  <strong>🇬🇧 English</strong> · <a href="README.zh-CN.md"><strong>🇨🇳 中文</strong></a>
</p>

# asc-changelog-release-notes

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

An **agent skill** that automates the App Store release-notes pipeline — from git history to App Store Connect — in one pass: commit analysis → user-facing polish → multi-language translation → `ChangeLog` update → `whatsNew` metadata → `asc` push.

## Features

- **Commit-driven** — analyzes the git history between two tags and groups changes into features, fixes, and maintenance.
- **User-facing polish** — rewrites developer-oriented output (no "refactor", "migration", "enum") into concise, benefit-focused release notes.
- **Flexible language coverage** — the language set is derived from your repository's existing `ChangeLog` blocks and metadata locale files, not hardcoded. Works with 1 language or 50 (reference default: 29 ChangeLog languages, 16 App Store locales).
- **Safe by default** — every remote change is dry-run previewed first and requires explicit user confirmation; `--allow-deletes` is never used unless asked.
- **Timeout-resilient** — recovers cleanly from `asc` timeouts without assuming partial rollback.
- **Source-driven translation** — the source language is read from your repo conventions (Simplified Chinese by default); English is the primary translation target.

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
export ASC_APP_ID=<your-app-id>   # your own App Store Connect app ID
```

> Replace `<your-app-id>` with the numeric App ID of **your** app (find it in App Store Connect → your app → App Information → Apple ID). The example above uses a placeholder only — do not copy values from other projects.

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

The skill assumes the consuming app repo follows these conventions (missing pieces are handled gracefully — see below):

- `ChangeLog` — human-facing, multi-language release history at the repo root (**optional**; the skill works without it)
- `AppStoreConnect/metadata/version/<version>/<locale>.json` — per-version App Store metadata
- `AppStoreConnect/metadata/app-info/` — app-level metadata (name, subtitle, privacy policy URL)
- For a new version, metadata is copied from the previous version and **only `whatsNew` is updated**, unless the user explicitly asks to change other fields.

### Missing files (first-time adoption)

- **No `ChangeLog`** — the skill asks whether to create one (recommended: seed it with your source language + derived App Store locales) or skip the ChangeLog step and produce metadata only. It never assumes a file exists, never invents one silently, and never touches a different changelog file (e.g. `CHANGELOG.md`) without permission.
- **No `AppStoreConnect/metadata`** — the skill asks you to run `asc metadata pull` first so local metadata starts from the remote source of truth, or to specify locales manually.

### Language configuration

The skill does **not** hardcode a fixed language list. It derives the language set from your repository each run:

- **ChangeLog languages** — read from the previous version block's `## <language>` headings (names and order are preserved exactly).
- **App Store locales** — read from the actual `<locale>.json` files of the previous version directory.
- `ChangeLog` and metadata locales are independent sets: your ChangeLog may have more (or fewer) languages than your App Store locales, and the skill never adds or removes locale files on its own.
- Source language defaults to `zh-Hans`; confirm with the skill if your project uses another source.

The original project uses 29 ChangeLog languages and 16 metadata locales as its reference configuration.

## Usage

Trigger the skill with a natural-language request, for example:

> Generate release notes for version 1.16.4 and update App Store Connect.

The skill will:

1. Find the latest git tag and determine the commit range.
2. Run `python3 scripts/generate_changelog.py <start> HEAD "<version>"` for a raw changelog.
3. Polish the raw output into user-facing release notes (source language from your repo conventions, `zh-Hans` by default).
4. Translate into every language in the derived ChangeLog language set.
5. Insert the new version block at the top of `ChangeLog`.
6. Create `AppStoreConnect/metadata/version/<version>/` (copied from the previous version) and update only `whatsNew` in every locale file.
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
