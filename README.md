# asc-changelog-release-notes

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

An **agent skill** that automates the full App Store release-notes pipeline: git commit analysis → user-facing polish → multi-language translation → `ChangeLog` update → App Store Connect `whatsNew` metadata → `asc` push.

一个**智能体技能（Agent Skill）**，自动化 App Store 版本发布说明全流程：Git 提交分析 → 面向用户的文案打磨 → 多语言翻译 → `ChangeLog` 更新 → App Store Connect `whatsNew` 元数据 → `asc` 推送。

---

## Features / 特性

- **Commit-driven** — analyzes git history between two tags and groups changes by feature/fix/chore（基于 git 提交历史生成原始变更日志）
- **User-facing polish** — rewrites developer-oriented output into concise release notes（将开发者视角输出润色为面向用户的内容）
- **29 languages** for `ChangeLog`（`ChangeLog` 支持 29 种语言）
- **16 App Store locales** for `whatsNew`（App Store 元数据支持 16 个地区）
- **Safe by default** — dry-run preview before any remote change, explicit confirmation required（默认安全：推送前先 dry-run 预览并需显式确认）
- **Timeout resilience** — handles `asc` timeouts without assuming rollback（对超时具备恢复能力）

## Dependencies / 依赖

| Dependency | Purpose | Install |
|---|---|---|
| [`asc`](https://asccli.sh) (≥ 3.x) | App Store Connect API CLI | `brew install asc` |
| `python3` | Commit analysis script (`scripts/generate_changelog.py`) | macOS / any Python 3 |
| `git` | Commit history analysis | system tool |

### Authentication / 认证

`asc` uses App Store Connect API keys:

```bash
asc auth login                    # interactive, stores in keychain
# or environment variables:
export ASC_KEY_ID=...
export ASC_ISSUER_ID=...
export ASC_PRIVATE_KEY_PATH=...
export ASC_APP_ID=6758697856      # default app ID used by the skill
```

## Installation / 安装

Clone this repo and install the skill into your agent skills directory:

```bash
git clone https://github.com/hytaoist/asc-changelog-release-notes.git
```

Copy or symlink into your agent's skill directory:

```bash
# Claude Code / opencode / other skill-based agents
mkdir -p ~/.claude/skills ~/.agents/skills
ln -s "$PWD/asc-changelog-release-notes" ~/.claude/skills/asc-changelog-release-notes
# or:
ln -s "$PWD/asc-changelog-release-notes" ~/.agents/skills/asc-changelog-release-notes
```

For agents that support installing skills by URL (e.g., opencode), you can also reference this repository directly.

## Repository conventions / 仓库约定

The skill assumes the consuming app repo follows these conventions:

- `ChangeLog` — human-facing multi-language release history at repo root
- `AppStoreConnect/metadata/version/<version>/<locale>.json` — per-version App Store metadata
- `AppStoreConnect/metadata/app-info/` — app-level metadata (name, subtitle, privacy policy URL)

## Usage / 用法

Trigger the skill with a natural-language request, for example:

> Generate release notes for version 1.16.4 and update App Store Connect.

The skill will:

1. Find the latest git tag and commit range
2. Run `python3 scripts/generate_changelog.py <start> HEAD "<version>"` to get a raw changelog
3. Polish the raw output into user-facing release notes (source language: `zh-Hans`)
4. Translate into all 29 `ChangeLog` languages
5. Insert the new version block at the top of `ChangeLog`
6. Create `AppStoreConnect/metadata/version/<version>/` (copied from the previous version) and update only `whatsNew` in all 16 locales
7. Validate locally: `asc metadata validate --dir ./AppStoreConnect/metadata --output table`
8. Dry-run the push: `asc metadata push --app "$ASC_APP_ID" --version <v> --platform IOS --dir ... --dry-run`
9. After explicit user confirmation, apply the push

## Repository structure / 目录结构

```
asc-changelog-release-notes/
├── SKILL.md                      # The skill definition (skill 定义)
├── README.md                     # This file (本说明)
├── LICENSE                       # MIT License
└── scripts/
    └── generate_changelog.py     # Raw commit → changelog analysis script
```

## Safety / 安全说明

- The skill **never** pushes to App Store Connect without a dry-run preview and explicit user confirmation.
- It never deletes remote locales unless explicitly requested (`--allow-deletes` is off by default).
- Release-note work only modifies `whatsNew`; all other metadata fields are preserved.
- Release notes must be user-facing, not developer-oriented (no "refactor", "migration", "enum" terminology).

## Contributing / 贡献

Issues and pull requests are welcome.

## License / 许可证

[MIT](LICENSE)
