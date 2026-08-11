---
name: asc-changelog-release-notes
description: Generate App Store release notes from git history, update ChangeLog with multi-language entries, and sync App Store Connect whatsNew metadata with asc. Use when asked to generate release notes, update ChangeLog, prepare App Store whatsNew metadata, or create a changelog for a new version.
---

# ASC changelog release notes

Use this skill when asked to generate release notes, update ChangeLog, prepare App Store whatsNew metadata, or create a changelog for a new version. Covers the full pipeline: git commit analysis → user-facing polish → multi-language translation → ChangeLog update → App Store metadata → asc push.

## Prerequisites

- `asc` CLI (https://asccli.sh) — install via Homebrew: `brew install asc`. Auth with `asc auth login` or `ASC_KEY_ID` / `ASC_ISSUER_ID` / `ASC_PRIVATE_KEY_PATH` env vars. Set `ASC_APP_ID` (or pass `--app`) for the target app.
- `python3` for the commit-analysis script.
- A repo following the conventions below (`ChangeLog` + `AppStoreConnect/metadata`).

## Repository conventions

- Human-facing release history lives in `ChangeLog`.
- App Store Connect canonical metadata lives in `AppStoreConnect/metadata`.
- Version release notes live under `AppStoreConnect/metadata/version/<version>/<locale>.json`.
- For a new version, copy the previous version's locale JSON files and update only `whatsNew` unless the user explicitly asks to change description, keywords, URLs, or other metadata.
- Keep `ChangeLog` language order consistent with the previous complete version.
- Keep App Store locale coverage consistent with existing metadata locales. Do not create extra locale files only because `ChangeLog` has more languages.
- Source language is `zh-Hans` (Simplified Chinese). English is the primary translation target.
- `whatsNew` in metadata must be concise (one paragraph, semicolons separating items).
- Raw commit analysis script: `scripts/generate_changelog.py` (relative to this skill's directory; developer-oriented output).

## Language configuration

Language coverage is **derived from the consuming repository**, not hardcoded. Different apps need different language sets — use the lists below only as a reference default, and always verify against the repo itself.

### 1. Derive the actual language set from the repo

- **ChangeLog languages**: read the previous complete version block in `ChangeLog` and mirror its `## <language>` headings exactly (names and order).
- **App Store locales**: list the actual `<locale>.json` files under `AppStoreConnect/metadata/version/<prev-version>/`.
- If the repo has no existing entries (first run), ask the user which languages/locales they need.

### 2. Rules that always apply

- Keep the derived language order identical to the previous version block — do not reorder.
- Keep App Store locale coverage identical to the previous version — do not add or remove locale files based on the ChangeLog language list. `ChangeLog` may have more languages than the metadata locales (or fewer); they are independent sets.
- Source language is `zh-Hans` (Simplified Chinese) by default; confirm with the user if their project uses a different source.

### Reference default (from the original project)

**ChangeLog (29 languages, in this order):**

`中文`, `English`, `日本語`, `한국어`, `Tiếng Việt`, `Deutsch`, `Français`, `Italiano`, `Русский`, `Polski`, `Nederlands`, `Svenska`, `ไทย`, `Bahasa Indonesia`, `Українська`, `Español`, `Português`, `Čeština`, `Magyar`, `Română`, `Hrvatski`, `Srpski`, `Slovenski`, `Ελληνικά`, `Türkçe`, `العربية`, `עברית`, `हिन्दी`, `中文（繁體）`

**App Store metadata (16 locales):**

`zh-Hans.json`, `en-US.json`, `ja.json`, `ko.json`, `vi.json`, `de-DE.json`, `fr-FR.json`, `it.json`, `ru.json`, `pl.json`, `nl-NL.json`, `sv.json`, `th.json`, `id.json`, `uk.json`, `es-ES.json`

## Workflow

### 1. Determine version and commit range

```bash
# Find latest tag
git describe --tags --abbrev=0

# List recent commits
git log --oneline -20
```

### 2. Generate raw changelog from git commits

```bash
python3 scripts/generate_changelog.py <start_tag> HEAD "<new_version>"
```

### 3. Polish for App Store (source: Chinese)

Rewrite the raw developer-oriented output into concise, user-facing release notes:

- Group changes into meaningful user-facing items (not developer terms like "refactor", "migration", "enum")
- Focus on benefits: what the user can now do, what got fixed
- Keep each bullet short (one line)
- Include a performance/stability item if there are maintenance changes
- Match the tone and style of existing ChangeLog entries

**Example transformation:**

| Raw commit | Polished for App Store |
|---|---|
| `refactor: 将customIndicator自定义指标迁移到CustomTestType实体` | `自定义指标管理升级：支持编辑、删除和取消归档` |
| `feat: 删除检测类型时列出关联数据详情供用户确认` | `删除检测类型时展示关联数据详情，供您确认后再操作` |
| `fix: 修复自定义类别下检测项无法置顶的问题` | `修复自定义类型下检测项无法置顶的问题` |
| `fix: 兼容 customIndicator 存量记录显示` | `修复自定义指标历史记录的兼容显示问题` |

### 4. Read ChangeLog and translate to all languages

Read the latest version block in `ChangeLog` to preserve language order and headings. Translate from the source language (Chinese by default) into **every language present in the derived language set** (see [Language configuration](#language-configuration)).

**Common translation keywords:**
- 修复 → Fixed / 修正 / 수정 / Risolto / Corrigido / etc.
- 新增 → Added / 追加 / 추가 / Ajouté / etc.
- 升级/优化 → Improved/Upgraded / 改善 / 개선 / Amélioré / etc.
- 支持 → Support / 対応 / 지원 / Supporto / etc.
- 自定义 → Custom / カスタム / 사용자 정의 / Personnalisé / etc.
- 检测类型 → Test type / 検査タイプ / 검사 유형 / Tipo di test / etc.
- 指标 → Indicator / 指標 / 지표 / Indicador / etc.
- 性能优化与稳定性提升 → Performance optimization and stability improvements / パフォーマンス最適化と安定性向上 / etc.

### 5. Update ChangeLog file

Insert the new version block BEFORE the current latest version (at top of file). Format:

```
# 版本 <version>    （<date>）
------------------------------
## 中文
* <item 1>
* <item 2>
...

## English
* <item 1>
...
```

Date format: `2026年, 07月22日` (Chinese locale style, matching existing entries)

### 6. Create App Store metadata

```bash
# Copy previous version's metadata
mkdir -p AppStoreConnect/metadata/version/<new-version>
cp AppStoreConnect/metadata/version/<prev-version>/*.json AppStoreConnect/metadata/version/<new-version>/
```

Update only `whatsNew` in each locale file (one per metadata locale, see [Language configuration](#language-configuration)). Condense the ChangeLog source-language entry into one paragraph with semicolons.

```python
# Example whatsNew style:
whatsnew = {
    "zh-Hans": "自定义指标管理升级：支持编辑、删除和取消归档；删除检测类型时展示关联数据详情；修复问题与性能优化",
    "en-US": "Upgraded custom indicator management: editing, deletion, and unarchiving; detailed data shown when deleting test types; bug fixes and performance improvements",
    "ja": "カスタム指標管理を強化：編集・削除・アーカイブ解除に対応；検査タイプ削除時に関連データ詳細を表示；不具合修正とパフォーマンス改善",
    # ...
}
```

### 7. Validate local metadata

```bash
asc metadata validate --dir "./AppStoreConnect/metadata" --output table
```

If full validation reports unrelated existing `app-info` errors, do a version-only validation in a temporary metadata root and call out that the unrelated errors still block a full metadata push until fixed.

### 8. Preview remote changes (dry run)

```bash
asc metadata push --app "$ASC_APP_ID" --version "<new-version>" --platform IOS --dir "./AppStoreConnect/metadata" --dry-run --output table
```

### 9. Apply (only after user confirmation)

```bash
asc metadata push --app "$ASC_APP_ID" --version "<new-version>" --platform IOS --dir "./AppStoreConnect/metadata"
```

## Timeout handling

If `asc metadata push` fails with `context deadline exceeded`, do not assume the failed locale was rolled back. Some earlier locale updates may already be applied, and the timed-out locale may also have succeeded remotely.

Retry with a longer request timeout and start with a dry run:

```bash
ASC_TIMEOUT=180s asc metadata push --app "$ASC_APP_ID" --version "<new-version>" --platform IOS --dir "./AppStoreConnect/metadata" --dry-run --output table
```

If the dry run shows only expected remaining changes, apply with the same timeout:

```bash
ASC_TIMEOUT=180s asc metadata push --app "$ASC_APP_ID" --version "<new-version>" --platform IOS --dir "./AppStoreConnect/metadata"
```

Use `ASC_TIMEOUT_SECONDS=180` instead if the shell or CI environment is easier to configure with numeric seconds. `ASC_UPLOAD_TIMEOUT` is for upload-style operations and is not usually needed for metadata PATCH requests.

## Download before editing

When syncing against App Store Connect, pull first so local metadata starts from the remote source of truth:

```bash
asc metadata pull --app "$ASC_APP_ID" --version "<version>" --platform IOS --dir "./AppStoreConnect/metadata" --force
```

Use `--app-info "APP_INFO_ID"` if the app has multiple app-info records.

## Safety rules

- Always run `asc --help` or the relevant subcommand `--help` when command behavior is uncertain.
- Never use `--allow-deletes` unless the user explicitly asks to delete remote locales.
- Treat omitted JSON fields as intentional no-ops; do not remove existing fields during release-note-only work.
- Keep `whatsNew` under App Store limits and avoid marketing claims not present in the source changelog.
- Do not upload remote changes without a dry run and explicit user confirmation.
- Release notes must be user-facing, not developer-oriented (no "refactor", "migration", "enum" terminology).

## Quality checklist

- [ ] Release notes polished for end users, not developers
- [ ] ChangeLog contains every language from the previous version block; metadata locale files match the previous version exactly
- [ ] `whatsNew` is concise enough for App Store display limits
- [ ] Metadata files only modified `whatsNew`, all other fields preserved
- [ ] Source language (Chinese by default) is written first and used as basis for translations
