# 战镜 ZhanJing 部署指南

## 一、上传到 GitHub

### 1. 创建仓库
在 github.com 登录你的账号，点击右上角 `+` → `New repository`：
- **Repository name**: `RaidMirror-ZH`（或你喜欢的名字）
- **Description**: 战镜 ZhanJing — 全中文魔兽世界战斗日志分析工具
- **Public** ✓（建议公开，GPLv3 协议）
- **不要勾选** "Add a README file" / "Add .gitignore" / "Choose a license"
- 点击 **Create repository**

### 2. 推送代码
创建仓库后，GitHub 会显示推送命令。在你的命令行执行：

```bash
cd zhanjing
git remote add origin https://github.com/你的用户名/RaidMirror-ZH.git
git push -u origin main
```

第一次推送会要求登录 GitHub（用户名 + Personal Access Token）。

> ⚠️ 注意：`data/spells.json` 有 21MB，推送可能需要几分钟。

---

## 二、部署到宝塔面板

### 方案 A：上传 ZIP 包（推荐）

1. **准备部署包**：
   ```bash
   cd zhanjing
   mkdir ../deploy
   cp index.html ../deploy/
   cp -r assets/ ../deploy/
   cp -r data/ ../deploy/
   cp -r data_core/ ../deploy/
   cd ../deploy
   zip -r ../zhanjing-deploy.zip .
   ```

2. **宝塔面板操作**：
   - 登录宝塔面板 → **网站** → **添加站点**
   - 填写你的域名（如 zhanjing.你的域名.com）
   - 创建后进入**网站目录**
   - 上传 `zhanjing-deploy.zip` 并解压到网站根目录

### 方案 B：Git 克隆部署

如果你服务器装了 git：
```bash
cd /www/wwwroot/你的网站目录
git clone https://github.com/你的用户名/RaidMirror-ZH.git .
# 只保留生产文件
rm -rf vendor/ build_zh.py README.md .git/
```

### 3. 配置 WarcraftLogs API（重要！）

部署后还需要在 WCL 注册 API Client：
1. 打开 https://www.warcraftlogs.com/api/clients/
2. 点击 **+ Create Client**
3. 填写：
   - **Name**: 战镜 ZhanJing
   - **Redirect URL**: `https://你的域名/`
   - 勾选 **Public Client**
4. 创建后会显示 **Client ID**，修改 `index.html` 里的：
   - `PKCE_CLIENT_ID` → 你的 Client ID
   - `PKCE_REDIRECT` → 你的域名

### 4. 验证部署

访问你的域名，点击「连接 WarcraftLogs 账号」测试 OAuth 登录是否正常。

---

## 项目结构（部署后）

```
/
├── index.html           # 主页面（427KB）
├── assets/
│   ├── favicon.svg      # 网站图标
│   ├── hero-gnome.png   # 装饰图（2.6MB）
│   └── logo.svg         # 战镜 Logo
├── data/
│   ├── spells.json      # 法术中英文对照（21MB）
│   └── meta.json        # 副本/Boss 元数据（37KB）
└── data_core/
    └── spell_zh_core.json  # 核心技能翻译（163条）
```
