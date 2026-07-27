# 关于战镜（ZhanJing / RaidMirror-ZH）

战镜是一个面向《魔兽世界》团队复盘的中文化战斗日志分析工具，基于 WarcraftLogs 数据进行可视化分析，帮助团长、指挥和队员快速定位问题并复盘改进。

## 项目定位

- 完整中文化：UI 文案、技能名、首领名、副本名等核心展示内容中文可读
- 纯前端部署：静态文件即可运行，无需后端服务
- 快速复盘：支持按战斗查看死亡原因、技能覆盖、关键事件等信息

## 核心能力

- WarcraftLogs OAuth 登录（PKCE）
- 战斗日志导入与战斗选择
- 团队/玩家维度的复盘信息展示
- 技能与副本元数据中文映射（含核心兜底映射）

## 技术与结构

- 主应用：`index.html`（单页前端）
- 构建脚本：`build_zh.py`
- 中文数据：
  - `data/meta.json`
  - `data/spells.json`（可选大文件）
  - `data_core/spell_zh_core.json`（核心兜底）
- 上游参考源：`vendor/RaidLens_public.html`

## 部署说明

部署时建议至少包含以下内容：

- `index.html`
- `assets/`
- `data/`
- `data_core/`

可参考仓库内 `DEPLOY.md` 获取部署细节。

## 许可与致谢

本项目基于开源项目 RaidLens 的公开代码进行中文化与本地化适配。  
请在二次分发时保留原始许可与来源说明，并遵守相关开源协议条款。
