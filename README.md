# 战镜 ZhanJing（RaidMirror-ZH）

> 专业战斗日志分析与团队复盘工具 · 魔兽世界（WarcraftLogs）全中文版

**战镜** 是一个全中文的魔兽世界团本战斗日志分析工具，复刻自开源项目
RaidLens（© Fisheye3D），
并进行了**完整中文化**与 **UI 美化**。

当前源码版本：**v1.0.12**（2026-07-28）

- 连接 WarcraftLogs 账号，一键分析最近一次（或任意指定）团本战斗日志
- 防御 / 进攻大招时间轴、减伤覆盖、打断 / 驱散统计、Boss 机制复盘建议
- **全中文技能名、首领名、副本名**（基于 41 万+ 法术映射 + 副本 / 首领映射）
- 角色评分（Raider.io）
- PKCE OAuth 登录（公开客户端，无需后端、无需 API Key）

---

## 功能说明

| 模块 | 说明 |
| --- | --- |
| 战报导入 | 支持按角色 / 公会导入 WarcraftLogs 战报列表，点击即可分析 |
| 大招时间轴 | 展示全团防御 / 进攻 / 嗜血类技能的施放时间轴，便于复盘覆盖 |
| Boss 机制复盘 | 自动识别 Boss 机制时间点，给出「谁该注意」「哪段时间没覆盖」等建议 |
| 技能明细 | 每个玩家的伤害 / 治疗构成（按技能拆分），全部中文显示 |
| 减伤 / 打断 / 驱散 | 统计坦克减伤链、关键打断与驱散，标记遗漏 |
| 评分 | 通过 Raider.io 拉取角色评分与装备等级 |

> 注：原版的「AI 教练话术」实为前端规则引擎（无 LLM / OpenAI 调用），
> 战镜完整保留该逻辑并汉化，因此**无需任何 AI Key**，纯本地计算。

---

## 与原版 RaidLens 的区别

1. **全中文本地化**：UI 文案（146 处）+ JS 字符串（47 处）全部汉化；技能名、首领名、副本名均显示中文。
2. **战镜品牌**：替换原站 Logo / 名称 / Slogan 为「战镜 ZhanJing」。
3. **UI 美化**：中文字体栈（PingFang SC / 微软雅黑 / Noto Sans SC）、配色与圆角、淡入动画、自定义滚动条、表格吸顶。
4. **本地化数据层**：内置 `data/spells.json`（413,692 条法术中文名）与 `data/meta.json`（副本 215 / 首领 1160 中文名）。
5. **零后端**：保持原版纯前端架构，可直接静态托管（宝塔 / GitHub Pages / Nginx 等）。

---

## 技术架构

- **纯前端单文件**：`index.html` 内联全部 CSS / JS，无框架、无构建步骤，开箱即用。
- **WarcraftLogs GraphQL API v2** + **PKCE OAuth**（Public Client，无 `client_secret`）。
- **Raider.io API**：角色评分。
- **中文化方案**：显示层字典映射（`spellID → 中文名`）。API 调用与内部逻辑键仍为 ID，**仅显示值中文化**，因此对原版逻辑零侵入。
- **外部数据加载**：页面加载时 `fetch` 同目录下的 `data/spells.json`、`data/meta.json`，自动填充中文名映射。

> WarcraftLogs v2 API 本身**不返回中文**（`cn.warcraftlogs.com` 已不可用），
> 因此采用「显示层字典映射」方案，逻辑与 API 调用完全不受影响。

---

## 目录结构

```
zhanjing/
├── index.html                 # 构建产物，可直接部署的站点首页
├── build_zh.py                # 中文化 + 美化转换器（由 vendor 原版生成 index.html）
├── README.md
├── .gitignore
├── assets/
│   ├── logo.svg               # 战镜 Logo（矢量）
│   ├── favicon.svg            # 站点图标
│   └── hero-gnome.png         # Hero 装饰图（构建时由 vendor 源码自动提取，不纳入版本库）
├── data/
│   ├── spells.json            # 41 万+ 法术中文名（约 21MB，可选，不纳入版本库；缺失不影响基础功能）
│   └── meta.json              # 副本(215) / 首领(1160) 中文名
├── data_core/
│   └── spell_zh_core.json     # 核心技能映射（163 条，构建时内嵌，fetch 完成前兜底）
└── vendor/
    └── RaidLens_public.html   # 原版开源源码（用于重新构建，含许可证说明）
```

---

## 快速开始（本地预览）

必须通过 **HTTP 服务**访问（浏览器在 `file://` 下会因 CORS 拦截本地 `fetch`）：

```bash
cd zhanjing
python -m http.server 8080
# 浏览器打开 http://127.0.0.1:8080
```

首次打开后，页面会自动 `fetch` `data/spells.json`（约 21MB），稍等数秒即可全量中文。

---

## 部署教程

详细部署步骤（含宝塔发布、Client ID 申请、代码替换、常见问题）见：
[DEPLOY.md](DEPLOY.md)

部署包命名统一为：`zhanjing-deploy-vX.Y.Z.zip`（例如 `zhanjing-deploy-v1.0.12.zip`）。
发布时通过 GitHub Release 资产分发（推送 `v*` tag 后自动上传标准命名部署包）。
CI 会在主分支校验：若有代码改动，必须同步更新 `README.md` 与 `CHANGELOG.md`；并自动刷新当前版本 Release 部署包。
首屏 Hero 图已启用 WebP 多尺寸加载（并保留 PNG 回退），减少加载体积。
PKCE 登录已兼容 `crypto.subtle` 不可用场景（不再出现 `reading 'digest'` 报错）。
登录回调关键构造器 `URLSearchParams` 已修复（避免被中文替换误伤成 `URL搜索Params`）。

---

## 本地化数据说明

- **技能名**：WarcraftLogs API 返回英文 `ability.name`，按 `spellID` 在 `data/spells.json`（41 万+ 条 zhCN 映射）中查中文。
- **副本 / 首领名**：按 GraphQL 返回的 `id` 在 `data/meta.json` 中查中文。
- **更新 / 扩充映射**：直接替换 `data/spells.json` 与 `data/meta.json` 即可，**无需改动任何代码**。
- `data_core/spell_zh_core.json`（163 条）为构建时内嵌的核心映射，用于在 `fetch` 完成前兜底，保证关键大招名立即显示中文。

---

## 二次开发 / 重新构建

`index.html` 由 `build_zh.py` 从 `vendor/RaidLens_public.html` 转换生成：

```bash
cd zhanjing
python build_zh.py     # 输出 index.html, 并自动提取 assets/hero-gnome.png
```

> **版本库约定**：`assets/hero-gnome.png`（二进制）与 `data/spells.json`（21MB 可选数据）
> 已通过 `.gitignore` 排除，不纳入 Git。克隆本仓库后执行 `python build_zh.py` 即可自动还原
> `hero-gnome.png`；`spells.json` 为可选的全量法术名覆盖（站点内置 163 条核心映射可独立运行），
> 可从本地部署包复制或自行生成，缺失不影响基础功能。

## 版本发布流程（约定）

- 只要仓库有修改（代码 / 样式 / 文档），就迭代版本（建议语义化版本号，如 `v1.0.4`）。
- 发布时同步更新三处：
  - `CHANGELOG.md`
  - `README.md`（若本次改动影响说明）
  - GitHub Releases（新 tag + release notes）
- 部署压缩包作为发布产物放在 GitHub Releases，不直接留在仓库根目录长期跟踪。

转换包含：146 条 UI 文案、47 条 JS 字符串、CSS 美化注入、Logo 替换、SPELL_ZH 映射层
（163 条内嵌 + 外部 41 万+ 法术加载）、`meta.json` 副本 / 首领加载、PKCE 占位符。

若要重新生成 `data/spells.json` / `data/meta.json`，请使用社区整理的中文本地化数据包
（见「许可证与致谢」），保持 `{items:{id:{name}}}` 与 `{instances:{},encounters:{}}` 的格式即可。

---

## 许可证与致谢

- **项目仓库**：<https://github.com/panhuanghe/RaidMirror-ZH>
- **原项目**：RaidLens © Fisheye3D。本中文本地化（战镜 / RaidMirror-ZH）基于原项目复刻，遵循原项目许可证。
- 原版源码存放于本仓库 `vendor/RaidLens_public.html`，以保留署名与许可证。
- 中文法术 / 副本 / 首领映射数据来自社区整理的 zhCN 本地化数据，仅用于本地显示。

> 本仓库为个人学习 / 自用复刻，与 RaidLens 原作者无隶属关系。
