# 更新日志

本文档记录本项目的重要变更。

格式参考 Keep a Changelog，并遵循语义化版本思路（不严格绑定标签）。

## [Unreleased]

### 变更

- 暂无（下一次修改后继续迭代版本）

## [v1.0.6] - 2026-07-28

### 工作流增强

- Release 资产工作流新增主分支校验：若存在代码改动，必须同步更新 `README.md` 与 `CHANGELOG.md`，否则 CI 失败。

### 文档同步

- README / DEPLOY 更新版本示例到 `v1.0.6`，并补充文档同步校验说明。

## [v1.0.5] - 2026-07-28

### Release 资产自动化

- 新增 GitHub Actions 工作流 `.github/workflows/release_assets.yml`。
- 推送 `v*` tag 时，自动创建/更新 Release 并上传标准命名部署包 `zhanjing-deploy-vX.Y.Z.zip`。
- 自动为历史 tag 回填标准命名 zip 资产，并清理旧命名（如 `zhanjing-release.zip`）以统一格式。

### 文档与流程

- README / DEPLOY 更新为“发布包走 GitHub Release 资产”的统一流程。

## [v1.0.4] - 2026-07-28

### 发布与命名规范

- 统一部署包命名风格为 `zhanjing-deploy-vX.Y.Z.zip`。
- 新增 `package_release.ps1`，支持按 README 当前版本自动打包，或手动指定版本号。
- README / DEPLOY 同步更新命名规则与打包指令。

## [v1.0.3] - 2026-07-28

### 链接与页面

- 将页面中的 GitHub 链接统一更新为当前仓库 `panhuanghe/RaidMirror-ZH`。
- 删除页面中的 `☕ Support RaidLens` 入口。

### 文档

- README 调整为精简结构：部署详细步骤迁移到 `DEPLOY.md`，README 仅保留入口链接。
- 重写 `DEPLOY.md`，补充 Client ID 申请、代码替换、上线验证与常见问题排查。

### 构建脚本

- 更新 `build_zh.py`，确保重构建后链接替换与 Support 链接移除可持续生效。

## [v1.0.2] - 2026-07-28

### 配置

- 更新 index.html 与 build_zh.py 中的 PKCE_CLIENT_ID 为当前发布使用的 WarcraftLogs Public Client。

### 仓库与发布

- 迭代源码版本到 v1.0.2，用于本次配置更新发布。

## [v1.0.1] - 2026-07-28

### UI

- Hero 区恢复望远镜图标风格，同时保留中文文案（“团本分析工具 / 战镜”）。

### 仓库与发布

- 删除仓库中的历史部署压缩包 `zhanjing-deploy-20260728-013441.zip`。
- 明确发布约定：只要有修改就迭代版本，并同步更新 Changelog / README / GitHub Releases。

## [2026-07-28]

### 构建与仓库规范

- 以字节方式提取 hero-gnome 资源，修复 UTF-8 误读导致的缺字节问题
- 补充仓库约定说明
- 调整大文件策略（二进制资源与大体积数据文件的管理说明）

对应提交：`a64f02f`

## [2026-07-27]

### 文档

- 新增 GitHub 与宝塔部署指南

对应提交：`07ea82a`

## [2026-07-26]

### 功能

- 完成全面中文化（UI / Discord 文案 / 职业专精等覆盖）

### 修复

- 修复 Logo 资源问题
- 补全遗漏英文翻译文案
- 修复部分乱码显示

对应提交：`c95ef34`、`3b73e13`

## [2026-07-25]

### 首次发布

- 发布战镜（ZhanJing / RaidMirror-ZH）初版
- 提供中文化 WarcraftLogs 战斗日志分析体验

对应提交：`b3ad7f7`
