# 更新日志

本文档记录本项目的重要变更。  
格式参考 Keep a Changelog，并遵循语义化版本思路。

## [Unreleased]

### 变更

- 暂无（下一次修改后继续迭代版本）。

## [v1.0.14] - 2026-07-28

### 日志加载错误修复

- 修复点击日志时 WCL GraphQL 返回 `Unknown argument "translate" on field "report" of type "ReportData"` 的错误。
- 移除 `ReportData.report` 不支持的 `translate:true` 参数，保留受支持的 `masterData(translate:true)` 技能名称本地化查询。
- 新增 GraphQL 查询契约回归检查，并重新通过整页 JavaScript 语法与未定义变量扫描。

## [v1.0.13] - 2026-07-28

### 错误修复

- 修复趋势数据字段名不一致导致的运行时错误：`Cannot read properties of undefined (reading 'flat')`。
- 将趋势对象字段统一为 `deaths`，避免在趋势卡片和趋势摘要中读取到 undefined。

## [v1.0.12] - 2026-07-28

### 分析页错误修复

- 修复战斗分析汇总打分区变量名不一致导致的运行时错误：`deaths is not defined`。
- 统一该段统计变量为 `deaths`，恢复分析后汇总表渲染与后续流程。

## [v1.0.11] - 2026-07-28

### 交互与分析修复

- 修复多个 `querySelector全部(...)` 误替换为不存在 API 导致的点击无响应问题，统一恢复为 `querySelectorAll(...)`。
- 修复战斗分析阶段死亡事件查询参数，将 `events(dataType:"死亡")` 改为 `events(dataType:"Deaths")`。
- 修复死亡日志计数变量引用错误，`deaths.length` 更正为 `次死亡.length`，避免分析阶段异常中断。

## [v1.0.10] - 2026-07-28

### 登录回调修复（关键源码误替换）

- 对比初始源码（vendor/RaidLens_public.html）确认关键差异：
  - 正确应为 `URLSearchParams`
  - 当前被误替换为 `URL搜索Params`
- 该误替换会导致 OAuth 回调与 token 请求链路异常，表现为“登录后无法正常拉取 logs”。
- 已在 `index.html` 修复 3 处调用，并在 `build_zh.py` 增加防护，避免重建时再次被误替换。

## [v1.0.9] - 2026-07-28

### 登录修复（PKCE）

- 修复点击“开始分析我的团本（通过 WCL）”时报错：
  - Connect error: Cannot read properties of undefined (reading digest)
- 为 PKCE code challenge 增加 SHA-256 fallback：当 crypto.subtle 不可用时，自动走内置实现，不再直接报错。
- PKCE_REDIRECT 改为 window.location.origin，自动匹配当前访问域名。

### 构建一致性

- 在 build_zh.py 中同步注入上述 PKCE 兼容逻辑，避免重建后回退。

## [v1.0.8] - 2026-07-28

### 性能优化（图片加载）

- Hero 装饰图由单一大图加载升级为 `picture + srcset`：
  - `assets/hero-gnome-202x264.webp`（1x）
  - `assets/hero-gnome-404x528.webp`（2x）
  - 保留 `assets/hero-gnome.png` 作为回退
- 在 `build_zh.py` 中加入 WebP 自动生成逻辑，避免下次重建回退成旧方案。

### 更新日志整理

- 进一步修正历史更新日志中的显示不一致/乱码描述，保持条目可追溯且结构统一。

## [v1.0.7] - 2026-07-28

### 工作流（你要求的规则）

- 当检测到代码文件改动时，CI 强制要求同次提交包含：
  - README.md
  - CHANGELOG.md
- 主分支 push 后，工作流会按 README 当前版本号自动创建/更新对应 Release，并刷新部署包资产：
  - zhanjing-deploy-vX.Y.Z.zip

### 更新日志整理

- 清理并重写更新日志结构，移除旧的日期散段，统一归档到语义化版本条目。
- 修正历史条目中的乱码/显示不一致问题，保留可追溯变更内容。

## [v1.0.6] - 2026-07-28

### 工作流增强

- Release 资产工作流新增主分支校验：若存在代码改动，必须同步更新 README.md 与 CHANGELOG.md，否则 CI 失败。

### 文档同步

- README / DEPLOY 更新版本示例到 v1.0.6，并补充文档同步校验说明。

## [v1.0.5] - 2026-07-28

### Release 资产自动化

- 新增 GitHub Actions 工作流 .github/workflows/release_assets.yml。
- 推送 v* tag 时，自动创建/更新 Release 并上传标准命名部署包 zhanjing-deploy-vX.Y.Z.zip。
- 自动为历史 tag 回填标准命名 zip 资产，并清理旧命名（如 zhanjing-release.zip）以统一格式。

### 文档与流程

- README / DEPLOY 更新为“发布包走 GitHub Release 资产”的统一流程。

## [v1.0.4] - 2026-07-28

### 发布与命名规范

- 统一部署包命名风格为 zhanjing-deploy-vX.Y.Z.zip。
- 新增 package_release.ps1，支持按 README 当前版本自动打包，或手动指定版本号。
- README / DEPLOY 同步更新命名规则与打包指令。

## [v1.0.3] - 2026-07-28

### 链接与页面

- 将页面中的 GitHub 链接统一更新为当前仓库 panhuanghe/RaidMirror-ZH。
- 删除页面中的 ☕ Support RaidLens 入口。

### 文档

- README 调整为精简结构：部署详细步骤迁移到 DEPLOY.md，README 仅保留入口链接。
- 重写 DEPLOY.md，补充 Client ID 申请、代码替换、上线验证与常见问题排查。

### 构建脚本

- 更新 build_zh.py，确保重构建后链接替换与 Support 链接移除可持续生效。

## [v1.0.2] - 2026-07-28

### 配置

- 更新 index.html 与 build_zh.py 中的 PKCE_CLIENT_ID 为当前发布使用的 WarcraftLogs Public Client。

### 仓库与发布

- 迭代源码版本到 v1.0.2，用于本次配置更新发布。

## [v1.0.1] - 2026-07-28

### UI

- Hero 区恢复望远镜图标风格，同时保留中文文案（团本分析工具 / 战镜）。

### 仓库与发布

- 删除仓库中的历史部署压缩包 zhanjing-deploy-20260728-013441.zip。
- 明确发布约定：只要有修改就迭代版本，并同步更新 Changelog / README / GitHub Releases。

## [v1.0.0] - 2026-07-27

### 首次发布与中文化

- 发布战镜（ZhanJing / RaidMirror-ZH）初版。
- 完成核心中文化（UI / Discord 文案 / 职业专精等）。

### 修复与构建规范

- 修复 Logo 与若干遗漏翻译项。
- 修复部分乱码显示。
- 以字节方式提取 hero-gnome 资源，避免 UTF-8 误读造成缺字节问题。
- 明确二进制与大体积数据文件管理策略。

### 文档

- 新增 GitHub 与宝塔部署指南。
