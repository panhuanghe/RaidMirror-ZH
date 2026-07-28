# 战镜 ZhanJing 部署详细教程

本文档覆盖从发布到上线的完整流程：上传站点、申请 WarcraftLogs Client ID、替换代码、验证登录、排查常见问题。

## 0. 先确认仓库地址

本项目仓库：<https://github.com/panhuanghe/RaidMirror-ZH>

## 1. 准备部署文件

站点最少需要这些文件/目录：

- `index.html`
- `assets/`（至少 `logo.svg`、`favicon.svg`）
- `data/meta.json`
- `data/spells.json`（建议带上，全量中文技能名；缺失不影响基础功能）

注意：必须通过 HTTP/HTTPS 访问，不能直接用 `file://` 打开本地 `index.html`。

## 1.1 部署包命名规范（统一）

- 统一命名：`zhanjing-deploy-vX.Y.Z.zip`
- 示例：`zhanjing-deploy-v1.0.4.zip`
- 不再使用旧命名：`zhanjing-release.zip`

可直接用脚本打包（自动读取 README 里的当前版本号）：

```powershell
.package_release.ps1
```

也可手动指定版本号：

```powershell
.package_release.ps1 -Version 1.0.4
```

## 2. 宝塔面板部署

### 2.1 创建站点

1. 登录宝塔面板。
2. 打开「网站」→「添加站点」。
3. 新建纯静态站点并绑定你的域名（例如 `https://your-domain.com`）。

### 2.2 上传文件

1. 进入该站点根目录。
2. 上传第 1 步准备的文件。
3. 确认站点根目录存在 `index.html`。

可选优化：在宝塔里开启 gzip/br 压缩，能减少 `data/spells.json` 传输体积。

## 3. 申请 WarcraftLogs Client ID（PKCE）

战镜使用 PKCE OAuth，需要一个 Public Client。

1. 打开 <https://www.warcraftlogs.com/api/clients/> 并登录。
2. 点击右上角 `Create Client`（或 `+ Create Client`）。
3. 填写：

- `Application Name`：例如 `战镜 ZhanJing`
- `Redirect URL`：你的实际站点地址（例如 `https://your-domain.com`）
- 勾选 `Public Client`

4. 创建后复制 `Client ID`（UUID 格式）。

如果看不到 `Create Client`，通常是未登录，或页面太窄导致按钮不明显。

## 4. 在代码中替换 Client ID

必须修改：

- `index.html` 里的 `PKCE_CLIENT_ID`
- `index.html` 里的 `PKCE_REDIRECT`

示例：

```js
const PKCE_CLIENT_ID="你的ClientID";
const PKCE_REDIRECT="https://你的域名";
```

如果你会重新执行 `build_zh.py` 生成 `index.html`，还要同步改 `build_zh.py` 中对应替换值，否则会被构建覆盖。

## 5. 上线后验证

1. 用浏览器打开你的域名。
2. 点击「连接 WarcraftLogs 账号」。
3. 预期行为：跳到 WCL 授权页 → 授权后跳回你域名并登录成功。

## 6. 常见问题排查

### 6.1 点击登录后不回跳 / 回调失败

重点检查：

- `PKCE_REDIRECT` 是否与 WCL 后台 `Redirect URL` 一致
- 协议是否一致（`http`/`https`）
- 域名是否一致（含子域名）
- 末尾斜杠是否一致（建议统一）

### 6.2 本地能开，线上异常

优先检查：

- 是否缺少 `data/meta.json`
- 是否把文件传错目录（不是站点根目录）
- 是否通过 `file://` 打开（这会触发 CORS 导致数据加载失败）

### 6.3 重构建后 Client ID 被改回旧值

说明只改了 `index.html`，没改 `build_zh.py`。按第 4 节同步修改后再构建。
