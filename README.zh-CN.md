<p align="center">
  <a href="README.md"><strong>🇬🇧 English</strong></a> · <strong>🇨🇳 中文</strong>
</p>

# asc-changelog-release-notes

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

一个**智能体技能（Agent Skill）**，自动化 App Store 版本发布说明的全流程——从 Git 历史到 App Store Connect 一步到位：提交分析 → 面向用户的文案打磨 → 多语言翻译 → `ChangeLog` 更新 → `whatsNew` 元数据 → `asc` 推送。

## 特性

- **提交驱动** — 分析两个标签之间的 Git 历史，将变更归类为功能、修复与维护。
- **面向用户的打磨** — 将开发者视角的输出（不含 "refactor"、"migration"、"enum" 等术语）改写为简洁、突出收益的发布说明。
- **语言覆盖灵活** — 语言集合从你的仓库现有 `ChangeLog` 版本块和元数据 locale 文件推导，而非硬编码。无论 1 种还是 50 种语言都能工作（参考默认：29 种 ChangeLog 语言、16 个 App Store 地区）。
- **默认安全** — 所有远端变更均先 dry-run 预览并要求显式确认；未经要求绝不使用 `--allow-deletes`。
- **超时恢复** — 从容处理 `asc` 超时，不假设部分回滚。
- **源语言驱动翻译** — 源语言从你的仓库约定读取（默认简体中文）；英文为主要翻译目标。

## 工作原理

```
git commits ──▶ 原始变更日志 ──▶ 打磨后文案 ──▶ 29 语言 ChangeLog
                                                    │
                                            16 地区 whatsNew
                                                    │
                                    校验 ─▶ dry-run ─▶ 推送
```

## 依赖

| 依赖 | 用途 | 安装 |
|---|---|---|
| [`asc`](https://asccli.sh) (≥ 3.x) | App Store Connect API CLI | `brew install asc` |
| `python3` | 提交分析脚本（`scripts/generate_changelog.py`） | 系统工具 |
| `git` | 提交历史分析 | 系统工具 |

### 认证

`asc` 使用 App Store Connect API 密钥：

```bash
asc auth login                    # 交互式，存入钥匙串
# 或使用环境变量：
export ASC_KEY_ID=...
export ASC_ISSUER_ID=...
export ASC_PRIVATE_KEY_PATH=...
export ASC_APP_ID=<你的应用ID>      # 你自己的 App Store Connect 应用 ID
```

> 请将 `<你的应用ID>` 替换为**你自己应用**的数字 ID（在 App Store Connect → 你的应用 → App 信息 → Apple ID 中查找）。示例中仅使用占位符，请勿复制其他项目的值。

## 安装

```bash
git clone https://github.com/hytaoist/asc-changelog-release-notes.git
```

将技能链接到智能体的技能目录：

```bash
mkdir -p ~/.claude/skills ~/.agents/skills
ln -s "$PWD/asc-changelog-release-notes" ~/.claude/skills/asc-changelog-release-notes
# 或：
ln -s "$PWD/asc-changelog-release-notes" ~/.agents/skills/asc-changelog-release-notes
```

> 支持按 URL 安装技能的智能体（如 opencode）可直接引用本仓库。

## 仓库约定

技能假定使用方应用仓库遵循以下约定：

- `ChangeLog` — 位于仓库根目录的面向用户的多语言发布历史
- `AppStoreConnect/metadata/version/<版本>/<地区>.json` — 各版本的 App Store 元数据
- `AppStoreConnect/metadata/app-info/` — 应用级元数据（名称、副标题、隐私政策 URL）
- 新版本元数据从上一版本复制，**仅更新 `whatsNew`**，除非用户明确要求修改其他字段。

### 语言配置

技能**不**硬编码固定语言列表，每次运行都会从你的仓库推导语言集合：

- **ChangeLog 语言** — 从上一版本块的 `## <语言>` 标题读取（语言名称与顺序严格保留）。
- **App Store 地区** — 从上一版本目录中实际的 `<地区>.json` 文件读取。
- `ChangeLog` 与元数据地区是两组独立集合：你的 ChangeLog 语言可以比 App Store 地区多（或少），技能不会自行新增或删除地区文件。
- 源语言默认为 `zh-Hans`；如果你的项目使用其他源语言，请与技能确认。

原项目以 29 种 ChangeLog 语言和 16 个元数据地区作为参考配置。

## 用法

用自然语言触发技能，例如：

> 为 1.16.4 生成发布说明并更新 App Store Connect。

技能将执行：

1. 查找最新 Git 标签并确定提交范围。
2. 运行 `python3 scripts/generate_changelog.py <起始> HEAD "<版本>"` 生成原始变更日志。
3. 将原始输出打磨为面向用户的发布说明（源语言遵循你的仓库约定，默认 `zh-Hans`）。
4. 翻译为推导出的 ChangeLog 语言集合中的每一种语言。
5. 在 `ChangeLog` 顶部插入新版本块。
6. 创建 `AppStoreConnect/metadata/version/<版本>/`（从上一版本复制），仅更新每个地区文件的 `whatsNew`。
7. 本地校验：`asc metadata validate --dir ./AppStoreConnect/metadata --output table`。
8. Dry-run 推送：`asc metadata push --app "$ASC_APP_ID" --version <v> --platform IOS --dir ... --dry-run`。
9. **仅在用户显式确认后**执行推送。

## 仓库结构

```
asc-changelog-release-notes/
├── SKILL.md                      # 技能定义
├── README.md                     # 英文说明
├── README.zh-CN.md               # 中文说明
├── LICENSE                       # MIT License
└── scripts/
    └── generate_changelog.py     # 原始提交 → 变更日志分析脚本
```

## 安全说明

- 未经 dry-run 预览和用户显式确认，绝不推送至 App Store Connect。
- 未经明确要求绝不删除远端地区（`--allow-deletes` 默认关闭）。
- 发布说明工作仅修改 `whatsNew`，保留其他所有元数据字段。
- 发布说明必须面向用户，不得使用开发者术语。

## 贡献

欢迎提交 Issue 和 Pull Request。

## 许可证

[MIT](LICENSE) © 2026 hytaoist
