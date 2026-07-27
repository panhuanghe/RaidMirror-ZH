#!/usr/bin/env python3
"""
战镜 (ZhanJing / RaidMirror-ZH) — 全量中文化 + UI 美化 转换器
===========================================================
基于 RaidLens_public.html 原版，生成:
  1. 全中文 UI（Hero/设���/标签页/教练话术/错误消息）
  2. 美化后的 CSS（中文字体/配色/间距/动画）
  3. 战镜品牌替换（Logo/Slogan/链接）
  4. SPELL_ZH 技能中文名映射层
  5. 外部 spells.json 加载支持（41万+法术名）
  6. PKCE_CLIENT_ID / PKCE_REDIRECT 可配置占位符

用法: python build_zh.py
输出: ../zhanjing/index.html
"""

import re, os, json, base64, html as html_mod

# ─── 路径 ───────────────────────────────────────────────
SRC = os.path.join(os.path.dirname(__file__), "vendor", "RaidLens_public.html")
DST = os.path.join(os.path.dirname(__file__), "index.html")
ASSETS = os.path.join(os.path.dirname(__file__), "assets")

# ─── 读取原始 HTML ───────────────────────────────────────
with open(SRC, "r", encoding="utf-8") as f:
    content = f.read()

print(f"[1/7] 读取原文件: {len(content):,} 字符")


# ══════════════════════════════════════════════════════════
#  ① UI 文案翻译表 (HTML 层 — 按出现顺序排列)
# ══════════════════════════════════════════════════════════
UI_REPLACEMENTS = [
    # ── Hero 区域 ──
    ('<div class="hero-brand-badge">Raid Tool</div>',
     '<div class="hero-brand-badge">团本分析工具</div>'),
    ('<span class="hero-title-raid">Raid</span><span class="hero-title-lens">Lens</span>',
     '<span class="hero-title-raid" style="color:#00d4ff">战</span><span class="hero-title-lens" style="background:linear-gradient(135deg,#00d4ff,#7b68ee);-webkit-background-clip:text;-webkit-text-fill-color transparent;background-clip:text">镜</span>'),
    ('Connect your WarcraftLogs account and instantly analyze your latest raid pull.<br>No setup. No config. No API keys. Just results.',
     '连接你的 WarcraftLogs 账号，即刻分析最新团本战斗记录。<br>无需安装 · 无需配置 · 无需 API Key · 即刻出结果'),
    ('Built For', '面向用户'),
    ('Raid Leaders', '团长 / RL'),
    ('Fast wipe reviews, missed cooldowns, death causes, and who actually pressed their buttons.',
     '快速灭团复盘、遗漏技能检测、死亡原因追踪、谁按了谁没按一目了然'),
    ('Best At', '核心优势'),
    ('One Pull Clarity', '一场战斗，全面洞察'),
    ('Cleaner than Warcraft Logs for quick raid calls, with direct drill-downs when you need more detail.',
     '比 WCL 原站更清晰的战斗概览，需要深入时一键跳转详情'),

    # Hero features
    ('Per-player scorecard with grades', '每位玩家评分卡 + 等级评定'),
    ('Deaths + killing blow per pull', '每场死亡记录 + 致命一击'),
    ('Missed offensive CDs flagged', '遗漏爆发技能标红提醒'),
    ('Defensive CD tracking', '防御技能使用追踪'),
    ('Bloodlust timing + who got it', '嗜血时◆◆ + 覆盖人员'),
    ('Potion &amp; healthstone usage', '合剂 / 药水 / 治疗石使用'),
    ('Mechanic death breakdown', '机制致死分类统计'),
    ('Downtime \u2014 who wasn\u2019t hitting', '空档期 — 谁在划水'),
    ('Pull-over-pull comparison', '逐次拉怪对比分析'),
    ('Discord wipe summary \u2014 one click', 'Discord 灭团总结 — 一键复制'),
    ('DPS / HPS / Raid totals', 'DPS / HPS / 团队总计'),
    ('Raidbots sim button per player', '每位玩家 Raidbots 模拟入口'),

    # Badges
    ('\u2713 Free forever', '\u2713 永久免费'),
    ('\u2713 No install', '\u2713 无需安装'),
    ('\u2713 Open source', '\u2713 完全开源'),
    ('\u2713 Works on any browser', '\u2713 支持所有浏览器'),
    ('\U0001f3f3\ufe0f Made by Sumanis \u2014 Resto Druid',
     '\U0001f3f3\ufe0f 基于 RaidLens 开源项目 \u2014 战镜中文版'),

    # Links
    ('Full Guide &amp; FAQ \u2014 all info here \u2197',
     '\U0001f4d6 使用说明与常见问题 \u2197'),
    ('Feedback, Suggestions or Issues',
     '反馈 / 建议 / 问题报告'),

    # Preview cards
    ('What You Get Fast', '你将立刻获得'),
    ('Immediate wipe diagnosis', '即时灭团诊断'),
    ('Primary wipe cause:', '主要灭团原因：'),
    ('Open one pull, see what killed the raid, who missed cooldowns, and which abilities deserve a click for deeper context.',
     '打开任意一场战斗，查看灭团原因、谁漏了技能、哪些技能值得深入分析'),
    ('Mythic+ Ready', '大秘境支持'),
    ('Overall + Boss by Boss', '总览 + 逐 Boss 分析'),
    ('Full key summary first, then jump straight into any boss attempt that needs a closer look.',
     '先看整趟大米总结，再一键跳入需要仔细看的 Boss 尝试'),
    ('Clickable Context', '可交互上下文'),
    ('Spell popups', '法术悬浮提示'),
    ('Deaths, offensives, damage taken, DPS and HPS breakdowns all surface real spell context through Wowhead tooltips.',
     '死亡、爆发、承伤、DPS/HPS 分解均通过 Wowhead 提示框展示真实法术信息'),

    # What's new bar
    ("What's new in this version:", "\u672c\u7248\u66f4\u65b0\u5185\u5bb9\uff1a"),
    ('Raid verdict summary', '\u56e2\u961f\u88c1\u51b3\u603b\u7ed3'),
    ('Death context', '\u6b7b\u4ea1\u4e0a\u4e0b\u6587'),
    ('4 Discord copy formats', '4 \u79cd Discord \u590d\u5236\u683c\u5f0f'),
    ('Timeline filters', '\u65f6\u95f4\u8f74\u8fc7\u6ee4'),
    ('Auto-scan', '\u81ea\u52a8\u626b\u63cf'),
    ('Focus mode', '\u805a\u7126\u6a21\u5f0f'),
    ('WoWAnalyzer links', 'WoWAnalyzer \u94fe\u63a5'),

    # How it works
    ('How it works', '\u4f7f\u7528\u65b9\u6cd5'),
    ('Connect WarcraftLogs', '\u8fde\u63a5 WarcraftLogs'),
    ('One click \u2014 WCL handles the login. No API keys, no config.',
     '\u4e00\u952e\u767b\u5f55 \u2014 WCL \u5904\u7406\u8ba4\u8bc1\uff0c\u65e0\u9700 API Key'),
    ('Pick a report & pull', '\u9009\u62e9\u62a5\u544a\u4e0e\u6218\u6597'),
    ('Your recent raid logs load automatically. Pick any fight.',
     '\u6700\u8fd1\u7684\u56e2\u672c\u65e5\u5fd7\u81ea\u52a8\u52a0\u8f7d\uff0c\u9009\u62e9\u4efb\u610f\u621d\u6597'),
    ('Get your raid verdict', '\u83b7\u53d6\u56e2\u961f\u88c1\u51b3'),
    ('Primary wipe cause, missed CDs, deaths, Discord summary \u2014 instant.',
     '\u4e3b\u8981\u706d\u56e2\u539f\u56e0\u3001\u6f0f\u6280\u80fd\u3001\u6b7b\u4ea1\u3001Discord \u603b\u7ed3 \u2014 \u5373\u65f6\u5448\u73b0'),

    # Showcase section headers
    ('What you get after every pull', '\u6bcf\u573a\u621d\u6597\u7ed3\u675f\u540e\u4f60\u5c06\u83b7\u5f97'),

    # Showcase card titles
    ('Raid Verdict \u2014 instantly know what killed your raid',
     '\u56e2\u961f\u88c1\u51b3 \u2014 \u4e00\u773c\u770b\u51fa\u8c01\u6740\u6b7b\u4e86\u56e2\u961f'),
    ('Deaths + Context + Top Killers', '\u6b7b\u4ea1\u8bb0\u5f55 + \u4e0a\u4e0b\u6587 + \u81f4\u547d\u6392\u884c'),
    ('Discord Copy \u2014 4 formats', 'Discord \u590d\u5236 \u2014 4 \u79cd\u683c\u5f0f'),
    ('Scorecard \u2014 per player, every pull', '\u8bc4\u5206\u5361 \u2014 \u6bcf\u4f4d\u73a9\u5bb6\uff0c\u6bcf\u573a\u621d\u6597'),
    ('Pull-over-Pull Comparison', '\u9010\u6b21\u62c9\u602a\u5bf9\u6bd4'),
    ('Timeline \u2014 filterable CD view', '\u65f6\u95f4\u8f74 \u2014 \u53ef\u8fc7\u6ee4\u7684\u6280\u80fd\u89c6\u56fe'),
    ('Auto-scan + Focus Mode', '\u81ea\u52a8\u626b\u63cf + \u805a\u7126\u6a21\u5f0f'),
    ('Per-Player Links + WoWAnalyzer', '\u73a9\u5bb6\u94fe\u63a5 + WoWAnalyzer'),

    # Showcase descriptions
    ('Boss %, tank death flag, pull trend, and next-pull suggestion \u2014 all from one glance',
     'Boss \u8840\u91cf\u3001\u5766\u514b\u6b7b\u4ea1\u6807\u5fd7\u3001\u8d8b\u52bf\u3001\u4e0b\u4e00\u6b21\u5efa\u8bae \u2014 \u4e00\u7739\u5168\u77e5'),
    ('Last defensive used, pot status, HS status \u2014 context for every death',
     '\u6700\u540e\u4f7f\u7528\u7684\u51cf\u4f24\u3001\u836f\u6c34\u72b6\u6001\u3001\u6cbb\u7597\u77f3\u72b6\u6001 \u2014 \u6bcf\u4e2a\u6b7b\u4ea1\u90fd\u6709\u4e0a\u4e0b\u6587'),
    ('Short, Detailed, Officer notes, or ping-by-name \u2014 paste into #raid-logs in one click',
     '\u7b80\u6d01/\u8be6\u7ec6/\u56e2\u957f\u7b14\u8bb0/@\u73a9\u5bb6 \u2014 \u4e00\u952e\u7c98\u8d34\u5230 Discord'),
    ('Grades, totals, downtime tiers (\U0001f7e2\U0001f7e1\U0001f7e0\U0001f534), missed CDs \u2014 all at a glance',
     '\u7b49\u7ea7\u3001\u603b\u8ba1\u3001\u7a7a\u6863\u7ea7\u522b\u3001\u6f0f\u6280\u80fd \u2014 \u4e00\u773c\u5168\u89c1'),
    ('See if the raid is actually improving pull to pull',
     '\u770b\u770b\u56e2\u961f\u662f\u5426\u5728\u9010\u6b21\u8fdb\u6b65'),
    ('Filter by player, by CD type, or both',
     '\u6309\u73a9\u5bb6\u3001\u6309\u6280\u80fd\u7c7b\u578b\uff0c\u6216\u4e24\u8005\u7ec4\u5408\u8fc7\u6ee4'),
    ('See exactly when every CD was used across the whole pull',
     '\u7cbe\u786e\u770b\u5230\u6bcf\u4e2a\u6280\u80fd\u5728\u621d\u6597\u4e2d\u7684\u4f7f\u7528\u65f6\u673a'),
    ('Built for live raid nights \u2014 minimal clicks, maximum clarity',
     '\u4e3a\u5b9e\u65f6\u5f00\u56e2\u8bbe\u8ba1 \u2014 \u6700\u5c11\u70b9\u51fb\uff0c\u6700\u5927\u4fe1\u606f\u91cf'),
    ('WoWAnalyzer opens directly to that player\'s log for deeper class analysis. Armory, Raider.io, and Raidbots sim also one click away.',
     'WoWAnalyzer \u76f4\u63a5\u6253\u5f00\u8be5\u73a9\u5bb6\u65e5\u5fd7\u8fdb\u884c\u6df1\u5165\u5206\u6790\u3002\u82f1\u96c4\u6bb5/Raider.io/Raidbots \u540c\u6837\u4e00\u952e\u5230\u4f4d'),
    ('See which mechanic is murdering the raid each pull',
     '\u770b\u6e05\u6bcf\u573a\u621d\u6597\u4e2d\u54ea\u4e2a\u673a\u5236\u5728\u5927\u9762\u79ef\u6295\u653e'),

    # Setup area
    ('Connect with WarcraftLogs', '\u8fde\u63a5 WarcraftLogs \u8d26\u53f7'),
    ('One click. No setup. WCL handles the login \u2014 you\'re sent straight to the app.',
     '\u4e00\u952e\u64cd\u4f5c\u3002WCL \u5904\u7406\u767b\u5f55 \u2014 \u8df3\u8f6c\u56de\u672c\u9875'),
    ('No API client', '\u65e0\u9700 API Client'),
    ('Auto login', '\u81ea\u52a8\u767b\u5f55'),
    ('Read-only access', '\u53ea\u8bfb\u6743\u9650'),
    ('Analyze My Raid (via WarcraftLogs) \u2197',
     '\u2192 \u5f00\u59cb\u5206\u6790\u6211\u7684\u56e2\u672c (\u901a\u8fc7 WCL) \u2197'),
    ('Having trouble? Click here', '\u9047\u5230\u95ee\u9898\uff1f\u70b9\u8fd9\u91cc'),
    ("You'll be redirected to WarcraftLogs to approve read-only access, then sent straight back here.",
     '\u4f1a\u8df3\u8f6c\u5230 WCL \u6388\u6743\u53ea\u8bfb\u8bbf\u95ee\uff0c\u7136\u540e\u81ea\u52a8\u8df3\u56de'),

    # Legacy setup welcome
    ('Welcome to RaidLens!', '\u6b22\u8fce\u4f7f\u7528 \u6218\u955c\uff01'),
    ('One-time setup, takes about 2 minutes.',
     '\u521d\u59cb\u8bbe\u7f6e\uff0c\u5927\u7ea6 2 \u5206\u949f'),
    ("You'll need a free WarcraftLogs API Client ID and Secret. Instructions below \u2014 less scary than it sounds.",
     '\u4f60\u9700\u8981\u4e00\u4e2a\u514d\u8d39\u7684 WCL API Client ID\u3002\u4e0b\u9762\u6709\u8be6\u7ec6\u6307\u5355 \u2014 \u6bd4\u60f3\u8c61\u4e2d\u7b80\u5355'),

    # Safety section
    ('Is this safe? Yes \u2014 here\'s exactly why:',
     '\u5b89\u5168\u5417\uff1f\u5b85\u5168\u5b89\u5168 \u2014 \u539f\u56e0\u5982\u4e0b\uff1a'),
    ('Stays on your computer', '\u6570\u636e\u4ece\u4e0d\u79bb\u5f00\u4f60\u7684\u6d4f\u89c8\u5668'),
    ('Your Client ID and Secret are stored in your browser\'s localStorage only. They never touch any server \u2014 not mine, not anyone\'s.',
     'Client ID \u53ea\u5b58\u50a8\u5728\u4f60\u672c\u5730\u6d4f\u89c8\u5668\u7684 localStorage \u4e2d\uff0c\u4e0d\u4f1a\u53d1\u9001\u5230\u4efb\u4f55\u670d\u52a1\u5668'),
    ('A WCL API client can only read public log data \u2014 the same data anyone can see on warcraftlogs.com. It cannot modify, delete, or access anything private.',
     'WCL API \u53ea\u80fd\u8bfb\u53d6\u516c\u5f00\u65e5\u5fd7\u6570\u636e(\u548c\u6240\u6709\u4eba\u5728 WCL \u7f51\u7ad9\u4e0a\u80fd\u770b\u5230\u7684\u4e00\u6837)\uff0c\u65e0\u6cd5\u4fee\u6539/\u5220\u9664/\u8bbf\u95ee\u4efb\u4f55\u79c1\u5bc6\u5185\u5bb9'),
    ('Every line of code is public at ', '\u6bcf\u4e00\u884c\u4ee3\u7901\u90fd\u662f\u516c\u5f00\u7684\uff1a'),
    ('You can verify exactly what it does \u2014 nothing hidden.',
     '\u4f60\u53ef\u4ee5\u6838\u5b9e\u5b83\u7684\u6bcf\u4e00\u4e2a\u884c\u4e3a \u2014 \u5b8c\u5168\u900f\u660e'),
    ('This is NOT your WarcraftLogs username or password. It\'s a separate free API key you create specifically for tools like this.',
     '\u8fd9 **\u4e0d** \u662f\u4f60\u7684 WCL \u7528\u540d\u6216\u5bc6\u7801\uff0c\u800c\u662f\u4e00\u4e2a\u5355\u72ec\u7684\u514d\u8d39 API Key\uff0c\u4e13\u95e8\u4e3a\u6b64\u7c7b\u5de5\u5177\u521b\u5efa'),

    # Setup steps
    ('Name it anything. Set redirect URL to ',
     '\u540d\u5b57\u968f\u4fbf\u586b\u3002\u91cd\u5b9a\u5411 URL \u8bbe\u4e3a '),
    ('Leave <strong style="color:#f85149">Public Client unchecked</strong>. Click Create.',
     '\u2705 <b>\u52fe\u9009 Public Client(\u516c\u5171\u5ba2\u6237\u7aef)</b>\u3002\u70b9\u51fb\u521b\u5efa'),
    ('After clicking Create, WCL shows your <strong style="color:#ffd700">Client ID</strong> and <strong style="color:#ffd700">Client Secret</strong> once \u2014 <strong style="color:#f85149">copy both immediately</strong>, the secret is never shown again. Paste them into the fields below.',
     '\u521b\u5efa\u540e WCL \u4f1a\u663e\u793a <b style="color:#ffd700">Client ID</b> \u548c <b style="color:#ffd700">Client Secret</b>(**\u53ea\u663e\u793a\u4e00\u6b21!**) \u2014 <b style="color:#f85149">\u7acb\u5373\u590d\u5236\u4e24\u8005!</b>\uff0c\u7136\u540e\u7c98\u8d34\u5230\u4e0b\u9762\u8f93\u5165\u6846'),

    # Report loading methods
    ('How do you want to load reports?', '\u9009\u62e9\u65e5\u5fd7\u52a0\u8f7d\u65b9\u5f0f'),
    ('Paste your WarcraftLogs profile URL. Your logs show up automatically every time.',
     '\u7c98\u8d34\u4f60\u7684 WCL \u4e2a\u4eba\u9875\u94fe\u63a5\uff0c\u65e5\u5fd7\u4f1a\u81ea\u52a8\u52a0\u8f7d'),
    ('Enter your guild name and server. Pulls fresh guild logs on every load.',
     '\u8f93\u5165\u516c\u4f1a\u540d\u548c\u670d\u52a1\u5668\uff0c\u6bcf\u6b21\u5237\u65b0\u83b7\u53d6\u6700\u65b0\u516c\u4f1a\u65e5\u5fd7'),
    ('Paste a report link when you need it. Saves to My Logs automatically.',
     '\u624b\u52a8\u7c98\u8d34\u62a5\u544a\u94fe\u63a5\uff0c\u81ea\u52a8\u4fdd\u5b58\u5230\u6211\u7684\u65e5\u5fd7'),
    ('Use the <strong>Paste URL</strong> tab to load reports manually. Each one saves to My Logs automatically.',
     '\u4f7f\u7528 <b>\u7c98\u8d34 URL</b> \u6807\u7b7e\u9875\u624b\u52a8\u52a0\u8f7d\u62a5\u544a\uff0c\u81ea\u52a8\u4fdd\u5b58'),

    # Step indicators
    ('Pick a log source', '\u9009\u62e9\u65e5\u5fd7\u6765\u6e90'),
    ('Nothing here yet. Load a report and it\'ll show up.', '\u8fd8\u6ca1\u6709\u65e5\u5fd7\u3002\u52a0\u8f7d\u4e00\u4efd\u62a5\u544a\u5373\u53ef\u67e5\u770b'),
    ('Pick a fight', '\u9009\u62e9\u621d\u6597'),

    # Tab labels (table headers)
    ('Player \u2195', '\u73a9\u5bb6 \u2195'),
    ('Class/Spec \u2195', '\u804c\u4e1a/\u4e13\u7cbe \u2195'),
    ('Def CDs \u24d8', '\u51cf\u4f24\u6280\u80fd \u24d8'),
    ('Total \u2195', '\u603b\u8ba1 \u2195'),
    ('Potion', '\u836f\u6c34'),
    ('Healthstone', '\u6cbb\u7597\u77f3'),
    ('Offensive CDs \u24d8', '\u7206\u53d1\u6280\u80fd \u24d8'),
    ('Spells Interrupted', '\u6253\u65ad\u7684\u6cd5\u672f'),
    ('Spells Dispelled', '\u9a71\u6563\u7684\u6cd5\u672f'),
    ('Visual', '\u89c6\u89c9\u5316'),
    ('Total Damage \u2195', '\u603b\u4f24\u5bb3 \u2195'),
    ('DPS \u2195', 'DPS \u2195'),
    ('Total Healing \u2195', '\u603b\u6cbb\u7597 \u2195'),
    ('HPS \u2195', 'HPS \u2195'),
    ('Overheal %', '\u8fc7\u6cbb %'),
    ('Absorbs', '\u5438\u6536'),
    ('Downtime% \u24d8 \u2195', '\u7a7a\u6863% \u24d8 \u2195'),
    ('Outcome', '\u7ed3\u679c'),
    ('Deaths', '\u6b7b\u4ea1'),
    ('Missed CDs', '\u6f0f\u6280\u80fd'),
    ('Raid DPS', '\u56e2\u961f DPS'),
    ('Potions Used', '\u5df2\u7528\u836f\u6c34'),
    ('Raid HPS', '\u56e2\u961f HPS'),

    # Tab descriptions
    ('Personal defensive cooldowns cast during the fight \u2014 tracked from combat log cast events.',
     '\u621d\u6597\u4e2d\u4f7f\u7528\u7684\u4e2a\u4eba\u51cf\u4f24\u6280\u80fd \u2014 \u6765\u6e90\u4e8e\u6218\u6597\u65e5\u5fd7\u4e8b\u4ef6'),
    ('Potion and Healthstone usage per player during the fight.', '\u6bcf\u4f4d\u73a9\u5bb6\u7684\u836f\u6c34/\u6cbb\u7597\u77f3\u4f7f\u7528\u60c5\u51b5'),
    ('Offensive cooldowns each player used (or didn\'t use). Red = missed entirely.',
     '\u6bcf\u4f4d\u73a9\u5bb6\u7684\u7206\u53d1\u6280\u80fd\u4f7f\u7528\u60c5\u51b5(\u7ea2\u8272=\u5b8c\u5168\u6f0f\u6389)'),
    ('Who interrupted what and how many times.', '\u8c01\u6253\u65ad\u4e86\u4ec0\u4e48\uff0c\u6253\u65ad\u4e86\u591a\u5c11\u6b21'),
    ('Who dispelled what.', '\u8c01\u9a71\u6563\u4e86\u4ec0\u4e48'),
    ('Crowd control abilities used on adds or bosses during the fight.',
     '\u621d\u6597\u4e2d\u5bf9\u5c0f\u602a/Boss \u4f7f\u7528\u7684\u63a7\u5236\u6280\u80fd'),
    ('Damage taken per player, broken down by ability. Good for spotting who\'s standing in bad stuff or taking avoidable damage.',
     '\u6bcf\u4f4d\u73a9\u5bb6\u7684\u627f\u4f24\u660e\u7ec6(\u6309\u6cd5\u672f\u5206\u89e3)\uff0c\u53d1\u73b0\u8c01\u7ad9\u9519\u4f4d\u7f6e\u6216\u8eb2\u4e0d\u5f00\u578c\u5bb3'),
    ('DPS for the fight. Click any player to see their full breakdown.',
     '\u621d\u6597 DPS \u3002\u70b9\u51fb\u73a9\u5bb6\u540d\u67e5\u770b\u8be6\u7ec6\u5206\u89e3'),
    ('Detailed damage breakdown per DPS player \u2014 total damage, DPS, damage taken, and key CDs at a glance.',
     'DPS \u73a9\u5bb6\u8be6\u7ec6\u5206\u89e3 \u2014 \u603b\u4f24\u5bb3/DPS/\u627f\u4f24/\u5173\u952e\u6280\u80fd\u4e00\u89c8\u65e0\u997e'),
    ('Scorecard for this pull.', '\u672c\u573a\u621d\u6597\u8bc4\u5206\u5361'),
    ('Deaths grouped by what killed them. Good for spotting which mechanic is murdering the raid.',
     '\u6309\u81f4\u547d\u539f\u56e0\u5206\u7c7b\u7684\u6b7b\u4ea1\u8bb0\u5f55\uff0c\u5feb\u901f\u5b9a\u4f4d\u706d\u56e2\u5143\u51f6'),
    ('Detailed healing breakdown per healer \u2014 effective healing, overhealing, and absorbs.',
     '\u6cbb\u7597\u8005\u8be6\u7ec6\u5206\u89e3 \u2014 \u6709\u6548\u6cbb\u7597/\u8fc7\u6c34/\u5438\u6536'),
    ('Visual timeline of major cooldowns used during the fight, plus boss-ability lanes so you can see whether personals and raid CDs lined up with the dangerous moments.',
     '\u6280\u80fd\u65f6\u95f4\u8f74 + Boss \u6280\u80fd\u8f68\u9053\uff0c\u770b\u6e05\u51cf\u4f24\u662f\u5426\u8986\u76d6\u4e86\u5371\u9669\u65f6\u523b'),
    ('When Bloodlust/Heroism/Time Warp was used and who was alive to benefit.',
     '\u55dc\u8840/\u82f1\u96c4\u4e4b\u9b42/\u65f6\u95f4\u626d\u66f2\u7684\u4f7f\u7528\u65f6\u673a\u5488\u8986\u76d6\u4eba\u5458'),
    ('Parse percentages for each player this fight, pulled directly from WarcraftLogs rankings. Updated after kills are processed by WCL.',
     '\u6bcf\u4f4d\u73a9\u5bb6\u7684 Parse \u767e\u5206\u6bd4(\u6765\u6e90: WCL \u6392\u884c)\uff0c\u6740\u6b7b Boss \u540e\u66f4\u65b0'),
    ('Loading parse data...', '\u6b63\u5728\u52a0\u8f7d Parse \u6570\u636e...'),
    ('Estimated main-target vs other NPC damage per player. Good for a fast read on boss focus, but treat it as an encounter-level estimate rather than a perfect enemy-name split.',
     '\u6bcf\u4f4d\u73a9\u5bb6\u7684 Boss \u4f24\u5bb3 vs \u5c0f\u602a\u4f24\u5bb3\u4f30\u8ba1(\u4ec5\u4f5c\u53c2\u8003)'),
    ('Estimated seconds each player spent doing zero damage. \U0001f7e2 Active \u00b7 \U0001f534 Downtime. Even 10% downtime on a 5-minute fight is 30 wasted seconds.',
     '\u6bcf\u4f4d\u73a9\u5bb6\u7684\u7a7a\u6863\u65f6\u957f\u3002\U0001f7e2 \u6b63\u5e38\u8f93\u51fa \u00b7 \U0001f534 \u5212\u6c34\u3002 5 \u5206\u949f\u621d\u6597 10% \u7a7a\u6863 = \u6d6a\u8d39 30 \u79d2'),
    ('Seconds of zero damage output as a % of fight duration. &gt;10% on a long fight is a red flag.',
     '\u96f6\u8f93\u51fa\u65f6\u957f\u5360\u621d\u6597\u65f6\u957f\u7684\u767e\u5206\u6bd4\u3002\u8d85\u8fc7 10% \u9700\u8981\u5173\u6ce8'),
    ('Pull-over-pull comparison for this boss. Analyze multiple pulls and see DPS trends, death reduction, and CD improvement over attempts.',
     '\u540c Boss \u591a\u6b21\u5c1d\u8bd5\u5bf9\u6bd4 \u2014 DPS \u8d8b\u52bf\u3001\u6b7b\u4ea1\u51cf\u5c11\u3001\u6280\u80fd\u8986\u76d6\u7387\u53d8\u5316'),
    ('Analyze a second pull of the same boss to see the comparison.',
     '\u5206\u6790\u540c Boss \u7684\u7b2c\u4e8c\u573a\u621d\u6597\u8fdb\u884c\u5bf9\u6bd4'),
    ('Data is stored per session \u2014 refreshing the page resets it.',
     '\u6570\u636e\u4ec5\u4fdd\u5b58\u5728\u5f53\u524d\u4f1a\u8bdd\uff0c\u5237\u65b0\u9875\u9762\u4f1a\u91cd\u7f6e'),

    # Missing translations (round 2 - from screenshot audit)
    ('Raid Verdict', '\u6218\u6597\u88c1\u51b3'),
    ('\u23f1\ufe0f Downtime', '\u23f1\ufe0f \u7a7a\u6863\u671f'),
    ('Downtime \u2014 who wasn\'t hitting', '\u7a7a\u6863\u671f \u2014 \u8c01\u5728\u5212\u6c34'),
    ('Shadowclaw Slam', '\u6697\u5f71\u722a\u51fb'),
    ('\U0001f525 Main killer:', '\U0001f525 \u4e3b\u8981\u6740\u624b\uff1a'),
    ('Main killer:', '\u4e3b\u8981\u6740\u624b\uff1a'),
    ('\U0001f525 Primary wipe cause: Shadowclaw Slam', '\U0001f525 \u4e3b\u8981\u706d\u56e2\u539f\u56e0\uff1a\u6697\u5f71\u722a\u51fb'),
    ('\ud83d\udc80 Main killer: Shadowclaw Slam \u00d7', '\ud83d\udc80 \u4e3b\u8981\u6740\u624b\uff1a\u6697\u5f71\u722a\u51fb \u00d7'),
    ('Downtime ↕', '\u7a7a\u6863\u671f ↕'),
]

print(f"[2/7] UI \u6587\u6848\u7ffb\u8bd1: {len(UI_REPLACEMENTS)} \u6761")
for old, new in UI_REPLACEMENTS:
    content = content.replace(old, new)


# ══════════════════════════════════════════════════════════
#  ② JavaScript 字符串翻译 (JS 层的提示/错误/教练话术)
# ══════════════════════════════════════════════════════════
JS_REPLACEMENTS = [
    # Error messages
    ('Please enter a valid WarcraftLogs report URL or code.',
     '\u8bf7\u8f93\u5165\u6709\u6548\u7684 WarcraftLogs \u62a5\u544a URL \u6216\u4ee3\u7801'),
    ('No report found. Check the URL and try again.',
     '\u672a\u627e\u5230\u62a5\u544a\uff0c\u8bf7\u68c0\u67e5 URL \u540e\u91cd\u8bd5'),
    ('Error fetching report data. Please try again.',
     '\u83b7\u53d6\u62a5\u544a\u6570\u636e\u5931\u8d25\uff0c\u8bf7\u91cd\u8bd5'),
    ('No fights found in this report.',
     '\u8be5\u62a5\u544a\u4e2d\u6ca1\u6709\u627e\u5230\u621d\u6597'),
    ('Please select a fight to analyze.',
     '\u8bf7\u9009\u62e9\u4e00\u573a\u621d\u6597\u8fdb\u884c\u5206\u6790'),
    ('Analyzing...', '\u6b63\u5728\u5206\u6790...'),
    ('Loading...', '\u6b63\u5728\u52a0\u8f7d...'),
    ('No data available for this tab.',
     '\u8be5\u6807\u7b7e\u9875\u6682\u65e0\u6570\u636e'),
    ('Copied to clipboard!', '\u5df2\u590d\u5236\u5230\u526a\u8d34\u677f!'),
    ('Copy failed', '\u590d\u5236\u5931\u8d25'),

    # Coach / analysis text
    ('Primary wipe cause:', '\u4e3b\u8981\u706d\u56e2\u539f\u56e0:'),
    ('TANK DIED', '\u5766\u514b\u9635\u4ea1'),
    ('Critical CD failures:', '\u4e25\u91cd\u6f0f\u6280\u80fd:'),
    ('No in-fight pot:', '\u6218\u6597\u4e2d\u672a\u4f7f\u7528\u836f\u6c34:'),
    ('Next pull focus:', '\u4e0b\u4e00\u6b21\u5c1d\u8bd5\u91cd\u70b9:'),
    ('assign tank defensive coverage', '\u5b9a\u4e49\u5766\u514b\u51cf\u4f24\u8986\u76d6'),
    ('enforce offensive CDs', '\u5f3a\u5316\u7206\u53d1\u6280\u80fd\u4f7f\u7528'),
    ('missed', '\u6f0f\u6389'),
    ('Last def:', '\u6700\u540e\u51cf\u4f24:'),
    ('No in-fight pot', '\u672a\u4f7f\u7528\u6218\u6597\u836f\u6c34'),
    ('HS \u2713', '\u6cbb\u7597\u77f3 \u2713'),
    ('HS \u2717', '\u6cbb\u7597\u77f3 \u2717'),
    ('Survived', '\u5b58\u6d3b'),
    ('Kill', '\u51fb\u6740'),
    ('Wipe', '\u706d\u56e2'),
    ('Top Killers', '\u81f4\u547d TOP3'),
    ('prepots not trackable', '\u5f00\u57ce\u836f\u6c34\u65e0\u6cd5\u8ddf\u8e2a'),

    # Pull compare
    ('trending right', '\u8d8b\u52bf\u826f\u597d'),
    ('DPS up', 'DPS \u2191'),
    ('deaths down', '\u6b7b\u4ea1\u2193'),

    # Timeline filter labels
    ('All', '\u5168\u90e8'),
    ('Offensive', '\u7206\u53d1'),
    ('Defensive', '\u51cf\u4f24'),
    ('Bloodlust', '\u55dc\u8840'),

    # Auto-scan labels
    ('Auto: Latest Pull', '\u81ea\u52a8: \u6700\u65b0\u4e00\u573A'),
    ('One click \u2014 pulls the most recent fight automatically',
     '\u4e00\u952e\u81ea\u52a8\u52a0\u8f7d\u6700\u65b0\u621d\u6597'),
    ('Auto-scan: On', '\u81ea\u52a8\u626b\u63cf: \u5df2\u5f00\u542f'),
    ('Polls every 90s for new pulls while you raid',
     '\u5f00\u56e2\u671f\u95f4\u6bcf 90 \u79d2\u81ea\u52a8\u68c0\u6d4b\u65b0\u621d\u6597'),
    ('Focus Mode', '\u805a\u7126\u6a21\u5f0f'),
    ('Hides landing content, sticks tabs \u2014 just the data',
     '\u9690\u85cf\u9996\u9875\uff0c\u56fa\u5b9a\u6807\u7b7e\u9875 \u2014 \u53ea\u7559\u6570\u636e'),

    # Scorecard grades context
    ('Outcome', '\u7ed3\u679c'),
    ('Deaths', '\u6b7b\u4ea1'),
    ('Missed CDs', '\u6f0f\u6280\u80fd'),
    ('Raid DPS', '\u56e2\u961f DPS'),
    ('Potions Used', '\u5df2\u7528\u836f\u6c34'),
    ('Raid HPS', '\u56e2\u961f HPS'),

    # Misc
    ('or use manual API credentials below (for advanced users / existing setup)',
     '\u6216\u4f7f\u7528\u4e0b\u65b9\u624b\u52a8 API \u51ed\u636e(\u9ad8\u7ea7\u7528\u6237)'),
]

print(f"[3/7] JS \u5b57\u7b26\u4e32\u7ffb\u8bd1: {len(JS_REPLACEMENTS)} \u6761")
for old, new in JS_REPLACEMENTS:
    content = content.replace(old, new)


# ══════════════════════════════════════════════════════════
#  ③ CSS 美化 (中文字体栈 / 配色微调 / 圆角增强)
# ══════════════════════════════════════════════════════════
CSS_ENHANCEMENTS = """
/* ===== 战镜 ZhanJing - 中文版样式增强 ===== */
:root {
  --zh-font: 'PingFang SC', 'Microsoft YaHei', 'Noto Sans SC', 'Helvetica Neue', Helvetica, Arial, sans-serif;
  --zh-accent: #00d4ff;
  --zh-accent2: #7b68ee;
  --zh-gradient: linear-gradient(135deg, #00d4ff, #7b68ee);
  --zh-bg-deep: #0a0e14;
  --zh-bg: #0d1117;
  --zh-surface: #161b22;
  --zh-border: #30363d;
  --zh-text: #e6edf3;
  --zh-text-secondary: #8b949e;
  --zh-success: #3fb950;
  --zh-danger: #f85149;
  --zh-warning: #d29922;
  --zh-info: #58a6ff;
}

/* 全局字体优化 */
body, * {
  font-family: var(--zh-font) !important;
  letter-spacing: 0.02em;
}

/* Hero 标题渐变 */
.hero-title-raid { color: var(--zh-accent) !important; }
.hero-title-lens {
  background: var(--zh-gradient);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

/* 表格��化 */
table { border-collapse: separate; border-spacing: 0; }
thead th {
  position: sticky; top: 0; z-index: 10;
  background: var(--zh-surface) !important;
  font-weight: 600 !important;
  font-size: 12px !important;
}
tbody tr:hover { background: #1c2128 !important; transition: background 0.15s ease; }

/* 卡片圆角统一 */
.hero-preview-card, .hero-mini, [style*='border-radius:10px'] {
  border-radius: 12px !important;
  transition: transform 0.2s ease, box-shadow 0.2s ease;
}
.hero-preview-card:hover, .hero-mini:hover {
  transform: translateY(-2px);
  box-shadow: 0 8px 24px rgba(0,0,0,0.4);
}

/* 按钮美化 */
button, .connect-cta {
  transition: all 0.2s ease !important;
  border-radius: 8px !important;
}
button:hover, .connect-cta:hover {
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(0,212,255,0.2);
}

/* 标签页激活态 */
.rtab.active {
  border-bottom-color: var(--zh-accent) !important;
  color: var(--zh-accent) !important;
  font-weight: 700 !important;
}

/* 滚动条美化 */
::-webkit-scrollbar { width: 8px; height: 8px; }
::-webkit-scrollbar-track { background: var(--zh-bg); }
::-webkit-scrollbar-thumb { background: #3d4450; border-radius: 4px; }
::-webkit-scrollbar-thumb:hover { background: #555; }

/* 动画: 渐入效果 */
@keyframes fadeInUp {
  from { opacity: 0; transform: translateY(12px); }
  to { opacity: 1; transform: translateY(0); }
}
.hero-feat, .hero-stat, .hero-mini, .hero-preview-card {
  animation: fadeInUp 0.4s ease forwards;
}

/* 数字高亮 */
.num { font-variant-numeric: tabular-nums !important; }
"""

# 注入到 </style> 结束标签之前
if '</style>' in content:
    content = content.replace('</style>', CSS_ENHANCEMENTS + '\n</style>', 1)
    print("[4/7] CSS \u7f8e\u5316\u6ce8\u5165: \u4e2d\u6587\u5b57\u4f53/\u914d\u8272/\u52a8\u753b/\u6eda\u52a8\u6761")


# ══════════════════════════════════════════════════════════
#  ④ Logo 替换 (用内联 SVG 替换原来的 emoji + 英文标题)
# ══════════════════════════════════════════════════════════
LOGO_SVG = '''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 280 56" fill="none" style="display:block;max-width:320px;height:auto">
  <defs>
    <linearGradient id="lg" x1="0%" y1="0%" x2="100%" y2="100%"><stop offset="0%" stop-color="#00d4ff"/><stop offset="100%" stop-color="#7b68ee"/></linearGradient>
    <filter id="gl"><feGaussianBlur stdDeviation="1.5" result="b"/><feMerge><feMergeNode in="b"/><feMergeNode in="SourceGraphic"/></feMerge></filter>
  </defs>
  <circle cx="28" cy="28" r="22" fill="none" stroke="url(#lg)" stroke-width="2"/>
  <circle cx="28" cy="28" r="18" fill="#0a0e14" stroke="#21262d" stroke-width="1"/>
  <line x1="28" y1="10" x2="28" y2="15" stroke="#00d4ff" stroke-width="1.5" opacity="0.7" filter="url(#gl)"/>
  <line x1="28" y1="41" x2="28" y2="46" stroke="#00d4ff" stroke-width="1.5" opacity="0.7" filter="url(#gl)"/>
  <line x1="10" y1="28" x2="15" y2="28" stroke="#00d4ff" stroke-width="1.5" opacity="0.7" filter="url(#gl)"/>
  <line x1="41" y1="28" x2="46" y2="28" stroke="#00d4ff" stroke-width="1.5" opacity="0.7" filter="url(#gl)"/>
  <circle cx="28" cy="28" r="2.5" fill="#00d4ff" filter="url(#gl)"/>
  <circle cx="28" cy="28" r="11" fill="none" stroke="#00d4ff" stroke-width="0.5" opacity="0.25" stroke-dasharray="2 2"/>
  <text x="60" y="36" font-family="'PingFang SC','Microsoft YaHei',sans-serif" font-size="28" font-weight="900" fill="#ffffff" letter-spacing="3">\u6218\u955c</text>
  <text x="128" y="36" font-family="'SF Pro Display',sans-serif" font-size="14" font-weight="600" fill="#8b949e" letter-spacing="1">RaidMirror</text>
  <line x1="60" y1="44" x2="210" y2="44" stroke="url(#lg)" stroke-width="1.5" opacity="0.5"/>
</svg>'''

# 替换 hero 区域的 emoji logo
old_hero_logo = '<span style="font-size:56px;line-height:1;filter:drop-shadow(0 0 12px #ffd70060)">\U0001f52d</span>'
if old_hero_logo in content:
    content = content.replace(old_hero_logo, LOGO_SVG)
    print("[5/7] Logo \u66ff\u6362: \u6218\u955c SVG (RaidLens \u2192 ZhanJing)")


# ══════════════════════════════════════════════════════════
#  ⑤ SPELL_ZH 映射层注入 (技能ID → 中文名)
# ══════════════════════════════════════════════════════════
SPELL_ZH_DATA = json.load(open(os.path.join(os.path.dirname(__file__), "data_core", "spell_zh_core.json"), encoding="utf-8"))

# Build JS mapping injection
spell_zh_json = json.dumps(SPELL_ZH_DATA, ensure_ascii=False, separators=(',', ':'))
SPELL_ZH_JS = f'''
// ===== 战镜 ZhanJing - 技能中文名映射层 =====
const SPELL_ZH = {spell_zh_json};
function zn(id, fallback) {{ return SPELL_ZH[id] || (fallback ?? ""); }}
function znName(en) {{ /* EN→ZH fallback for SPEC_OFFS matches */ const m={{"Recklessness":"鲁莽","Avenging Wrath":"复仇之怒","Arcane Power":"奥术强化","Tranquility":"宁静","Bloodlust":"嗜血","Heroism":"英勇","Time Warp":"时间扭曲","Power Infusion":"力量灌注","Dark Ascension":"黑暗飞升","Celestial Alignment":"星辰连结","Guardian of Azeroth":"艾泽拉斯的守护者","Synod Synapse":"突触神经"}}; return m[en] || (en || ""); }}
var ZN_ENC={{}}, ZN_ENC_NAME={{}}, ZN_INST={{}}, ZN_INST_NAME={{}};
function _fill(map,nameMap,obj){{ if(!obj) return; for(var k in obj){{ var v=obj[k]; if(k) map[k]=v; if(v) nameMap[v]=v; }} }}
function znEnc(id,en){{ return (id&&ZN_ENC[id])||(en&&ZN_ENC_NAME[en])||(en||""); }}
function znInst(id,en){{ return (id&&ZN_INST[id])||(en&&ZN_INST_NAME[en])||(en||""); }}
// 外部全量法术名加载(可选): 将 spells.json 放到 data/ 目录下即可自动加载
(function(){{ try{{ fetch("data/spells.json").then(r=>r.json()).then(d=>{{ if(d&&Array.isArray(d)){{ d.forEach(function(s){{ if(s.id&&!SPELL_ZH[s.id]) SPELL_ZH[s.id]=(s.name_zhCN||s.name)||""; }}); }}
  else if(d&&d.items){{ Object.keys(d.items).forEach(function(k){{ var o=d.items[k]; var nm=o&&(o.name_zhCN||o.name); if(k&&nm&&!SPELL_ZH[k]) SPELL_ZH[k]=nm; }}); }}; }}).catch(()=>{{}});   fetch("data/meta.json").then(r=>r.json()).then(function(d){{ _fill(ZN_ENC,ZN_ENC_NAME,d&&d.encounters); _fill(ZN_INST,ZN_INST_NAME,d&&d.instances); }}).catch(function(){{}});
}}catch(e){{}} }})();
'''

# Inject BEFORE the function definition (do NOT match the 'initV5()' substring
# inside 'function initV5(){', which would corrupt the definition into a syntax error)
if 'function initV5(){' in content:
    content = content.replace('function initV5(){', SPELL_ZH_JS + '\nfunction initV5(){', 1)
    print(f"[6/7] SPELL_ZH \u6620\u5c04\u5c42: {len(SPELL_ZH_DATA)} \u6761 + \u5916\u90e8 spells.json \u52a0\u8f7d\u652f\u6301")


# ══════════════════════════════════════════════════════════
#  ⑥ PKCE 配置占位符 (方便部署时修改)
# ══════════════════════════════════════════════════════════
content = content.replace(
    'const PKCE_CLIENT_ID = "a15ff79c-4eb3-49a8-9aa5-8ff9049308df"',
    'const PKCE_CLIENT_ID = "YOUR_CLIENT_ID_HERE" // ⬅ 请替换为你在 https://www.warcraftlogs.com/api/clients 注册的 Client ID'
)
content = content.replace(
    'const PKCE_REDIRECT = "https://raidlens.org"',
    'const PKCE_REDIRECT = window.location.origin // ⬅ 自动取当前域名，或改为你的实际域名如 "https://your-domain.com"'
)


# ══════════════════════════════════════════════════════════
#  ⑦ 页面元信息更新
# ══════════════════════════════════════════════════════════
content = content.replace(
    '<title>RaidLens</title>',
    '<title>\u6218\u955c ZhanJing | \u4e13\u4e1a\u6218\u6597\u65e5\u5fd7\u5206\u6790\u5de5\u5177</title>'
)

# Favicon
favicon_svg_inline = open(os.path.join(ASSETS, "favicon.svg"), "r", encoding="utf-8").read()
content = content.replace(
    '<title>',
    f'<link rel="icon" type="image/svg+xml" href="assets/favicon.svg">\n<title>'
)

# Google Analytics 移除(中文版用自己的)
content = content.replace(
    '<script async src="https://www.googletagmanager.com/gtag/js?id=G-XXXXXXXXXX"></script>',
    '<!-- GA placeholder: replace G-XXXXXXXXXX with your own GA ID if needed -->'
)
content = content.replace(
    "window.dataLayer=window.dataLayer||[];function gtag(){dataLayer.push(arguments)}gtag('js',new Date());gtag('config','G-XXXXXXXXXX');",
    "// GA: configure your own tracking ID if needed"
)



# ══════════════════════════════════════════════════════════
#  ⑧ 中文显示接入: 技能名 / 首领名 / 副本名 全部走映射层
# ══════════════════════════════════════════════════════════
# 技能名: aName 改为中文(保留英文副本 aNameEN 供逻辑匹配)
content = content.replace("const aName={},potIDs=new Set();", "const aName={},aNameEN={},potIDs=new Set();")
content = content.replace("abilities.forEach(a=>{aName[a.gameID]=a.name;",
                          "abilities.forEach(a=>{aNameEN[a.gameID]=a.name;aName[a.gameID]=zn(a.gameID,a.name);")
# 保留 English 名称喂给 detectRaidCD 的 RAID_CD_HINTS 启发式
content = content.replace("detectRaidCD(aName[sid]||DEFS[sid]||OFFS[sid]||",
                          "detectRaidCD(aNameEN[sid]||DEFS[sid]||OFFS[sid]||")
# 战斗列表首领名 -> znEnc
content = content.replace('<span class="fi-name">${f.name}</span>',
                          '<span class="fi-name">${znEnc(f.encounterID,f.name)}</span>')
# 副本名: GraphQL 增加 id, 显示时按 id 映射中文(JS 数字键会 coerce 成字符串, 与 meta.json 的 "63" 匹配)
content = content.replace("zone{name}", "zone{id,name}")
content = content.replace('zone:r.zone?.name||"Unknown Zone"',
                          'zone:znInst(r.zone?.id,r.zone?.name)||"Unknown Zone"')

# ══════════════════════════════════════════════════════════
#  ⑨ 修复 Hero 区域破损图片: 3.5MB base64 PNG → 轻量 SVG
# ══════════════════════════════════════════════════════════
import re as _re
content = _re.sub(
    r'<div class="hero-gnome" aria-hidden="true">\s*<img src="data:image/png;base64,[^"]+"\s*/?\s*>',
    r'''<div class="hero-gnome" aria-hidden="true">
    <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 202 264" fill="none" style="width:100%;height:100%">
      <rect width="202" height="264" rx="20" fill="#0d1117" stroke="#30363d"/>
      <circle cx="101" cy="110" r="60" fill="none" stroke="url(#lg2)" stroke-width="3" opacity="0.6"/>
      <circle cx="101" cy="110" r="40" fill="none" stroke="url(#lg2)" stroke-width="2" opacity="0.4"/>
      <line x1="101" y1="50" x2="101" y2="170" stroke="#00d4ff" stroke-width="1" opacity="0.3"/>
      <line x1="41" y1="110" x2="161" y2="110" stroke="#7b68ee" stroke-width="1" opacity="0.3"/>
      <text x="101" y="200" text-anchor="middle" fill="#8b949e" font-size="14" font-family="PingFang SC,Microsoft YaHei,sans-serif">战镜</text>
      <defs><linearGradient id="lg2" x1="0%" y1="0%" x2="100%" y2="100%"><stop offset="0%" stop-color="#00d4ff"/><stop offset="100%" stop-color="#7b68ee"/></linearGradient></defs>
    </svg>''',
    content,
    flags=_re.S,
)
print("[9/9] \\u6c42\\u66ff\\u6362 hero-gnome: 3.5MB PNG \\u2192 \\u8f7b\\u91cf SVG")

# ─── 写入输出 ─────────────────────────────────────────────
os.makedirs(os.path.dirname(DST), exist_ok=True)
with open(DST, "w", encoding="utf-8") as f:
    f.write(content)

print(f"[7/7] \u8f93\u51fa: {DST} ({os.path.getsize(DST)//1024} KB)")
print("\n\u2705 \u6218\u955c ZhanJing \u4e2d\u6587\u7248\u6784\u5efa\u5b8c\u6210!")
