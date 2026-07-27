# 战镜 ZhanJing（RaidMirror-ZH）

> 专业战斗日志分析与团队复盘工具 · 魔兽世界（WarcraftLogs）全中文版

**战镜** 是一个全中文的魔兽世界团本战斗日志分析工具，复刻自开源项目
[RaidLens](https://github.com/Fisheye3D/Raidlenshosted)（© Fisheye3D），
并进行了**完整中文化**与 **UI 美化**。

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

## 宝塔面板部署教程

1. 登录 **宝塔面板** → 「网站」→「添加站点」，创建一个**纯静态**站点（绑定你的域名 / 端口）。
2. 将 `zhanjing/` 目录下的全部内容上传到站点**根目录**：
   - `index.html`
   - `assets/`（logo.svg、favicon.svg）
   - `data/`（spells.json、meta.json）
   - （可选）`build_zh.py`、`vendor/`、`data_core/` 等源码，便于后续二次构建
3. 确认站点根目录存在 `index.html`（默认首页）。
4. **可选优化**：在「网站 → 设置 → 配置文件」中开启 `gzip` / `br` 压缩，`data/spells.json`（21MB）压缩后传输更小。
5. 浏览器访问你的域名即可使用。
6. **PKCE 回调无需配置**：代码已设为 `PKCE_REDIRECT = window.location.origin`，自动使用当前域名。

---

## 配置 WarcraftLogs API Client（获取 Client ID）

战镜通过 WarcraftLogs OAuth（PKCE，公开客户端）登录，需要一个 **Client ID**：

1. 打开 <https://www.warcraftlogs.com/api/clients> 并登录。
2. 点击 **Create Client**。
3. Application Name 填你的站点名（如 `战镜`）。
4. Redirect URL 可填任意合法 URL（如 `https://your-domain.com`），
   部署后会被 `window.location.origin` **自动覆盖**，无需精确匹配。
5. 记下生成的 Client ID（形如 UUID）。
6. 替换站点中的占位符：
   - 直接改 `index.html`：把 `const PKCE_CLIENT_ID = "YOUR_CLIENT_ID_HERE"` 换成你的 Client ID；
   - 或改 `build_zh.py` 中对应的占位字符串后重新构建。

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

转换包含：146 条 UI 文案、47 条 JS 字符串、CSS 美化注入、Logo 替换、SPELL_ZH 映射层
（163 条内嵌 + 外部 41 万+ 法术加载）、`meta.json` 副本 / 首领加载、PKCE 占位符。

若要重新生成 `data/spells.json` / `data/meta.json`，请使用社区整理的中文本地化数据包
（见「许可证与致谢」），保持 `{items:{id:{name}}}` 与 `{instances:{},encounters:{}}` 的格式即可。

---

## 许可证与致谢

- **原项目**：RaidLens © Fisheye3D，开源地址 <https://github.com/Fisheye3D/Raidlenshosted>。
  本中文本地化（战镜 / RaidMirror-ZH）基于原项目复刻，遵循原项目许可证。
- 原版源码存放于本仓库 `vendor/RaidLens_public.html`，以保留署名与许可证。
- 中文法术 / 副本 / 首领映射数据来自社区整理的 zhCN 本地化数据，仅用于本地显示。

> 本仓库为个人学习 / 自用复刻，与 RaidLens 原作者无隶属关系。
