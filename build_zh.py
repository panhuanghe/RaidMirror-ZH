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
    ('Bloodlust timing + who got it', '嗜血时机 + 覆盖人员'),
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
     '\u6700\u8fd1\u7684\u56e2\u672c\u65e5\u5fd7\u81ea\u52a8\u52a0\u8f7d\uff0c\u9009\u62e9\u4efb\u610f\u6218\u6597'),
    ('Get your raid verdict', '\u83b7\u53d6\u56e2\u961f\u88c1\u51b3'),
    ('Primary wipe cause, missed CDs, deaths, Discord summary \u2014 instant.',
     '\u4e3b\u8981\u706d\u56e2\u539f\u56e0\u3001\u6f0f\u6280\u80fd\u3001\u6b7b\u4ea1\u3001Discord \u603b\u7ed3 \u2014 \u5373\u65f6\u5448\u73b0'),

    # Showcase section headers
    ('What you get after every pull', '\u6bcf\u573a\u6218\u6597\u7ed3\u675f\u540e\u4f60\u5c06\u83b7\u5f97'),

    # Showcase card titles
    ('Raid Verdict \u2014 instantly know what killed your raid',
     '\u56e2\u961f\u88c1\u51b3 \u2014 \u4e00\u773c\u770b\u51fa\u8c01\u6740\u6b7b\u4e86\u56e2\u961f'),
    ('Deaths + Context + Top Killers', '\u6b7b\u4ea1\u8bb0\u5f55 + \u4e0a\u4e0b\u6587 + \u81f4\u547d\u6392\u884c'),
    ('Discord Copy \u2014 4 formats', 'Discord \u590d\u5236 \u2014 4 \u79cd\u683c\u5f0f'),
    ('Scorecard \u2014 per player, every pull', '\u8bc4\u5206\u5361 \u2014 \u6bcf\u4f4d\u73a9\u5bb6\uff0c\u6bcf\u573a\u6218\u6597'),
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
     '\u7cbe\u786e\u770b\u5230\u6bcf\u4e2a\u6280\u80fd\u5728\u6218\u6597\u4e2d\u7684\u4f7f\u7528\u65f6\u673a'),
    ('Built for live raid nights \u2014 minimal clicks, maximum clarity',
     '\u4e3a\u5b9e\u65f6\u5f00\u56e2\u8bbe\u8ba1 \u2014 \u6700\u5c11\u70b9\u51fb\uff0c\u6700\u5927\u4fe1\u606f\u91cf'),
    ('WoWAnalyzer opens directly to that player\'s log for deeper class analysis. Armory, Raider.io, and Raidbots sim also one click away.',
     'WoWAnalyzer \u76f4\u63a5\u6253\u5f00\u8be5\u73a9\u5bb6\u65e5\u5fd7\u8fdb\u884c\u6df1\u5165\u5206\u6790\u3002\u82f1\u96c4\u6bb5/Raider.io/Raidbots \u540c\u6837\u4e00\u952e\u5230\u4f4d'),
    ('See which mechanic is murdering the raid each pull',
     '\u770b\u6e05\u6bcf\u573a\u6218\u6597\u4e2d\u54ea\u4e2a\u673a\u5236\u5728\u5927\u9762\u79ef\u6295\u653e'),

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
     '\u8fd9 **\u4e0d** \u662f\u4f60\u7684 WCL \u7528\u6237\u540d\u6216\u5bc6\u7801\uff0c\u800c\u662f\u4e00\u4e2a\u5355\u72ec\u7684\u514d\u8d39 API Key\uff0c\u4e13\u95e8\u4e3a\u6b64\u7c7b\u5de5\u5177\u521b\u5efa'),

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
    ('Pick a fight', '\u9009\u62e9\u6218\u6597'),

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
     '\u6218\u6597\u4e2d\u4f7f\u7528\u7684\u4e2a\u4eba\u51cf\u4f24\u6280\u80fd \u2014 \u6765\u6e90\u4e8e\u6218\u6597\u65e5\u5fd7\u4e8b\u4ef6'),
    ('Potion and Healthstone usage per player during the fight.', '\u6bcf\u4f4d\u73a9\u5bb6\u7684\u836f\u6c34/\u6cbb\u7597\u77f3\u4f7f\u7528\u60c5\u51b5'),
    ('Offensive cooldowns each player used (or didn\'t use). Red = missed entirely.',
     '\u6bcf\u4f4d\u73a9\u5bb6\u7684\u7206\u53d1\u6280\u80fd\u4f7f\u7528\u60c5\u51b5(\u7ea2\u8272=\u5b8c\u5168\u6f0f\u6389)'),
    ('Who interrupted what and how many times.', '\u8c01\u6253\u65ad\u4e86\u4ec0\u4e48\uff0c\u6253\u65ad\u4e86\u591a\u5c11\u6b21'),
    ('Who dispelled what.', '\u8c01\u9a71\u6563\u4e86\u4ec0\u4e48'),
    ('Crowd control abilities used on adds or bosses during the fight.',
     '\u6218\u6597\u4e2d\u5bf9\u5c0f\u602a/Boss \u4f7f\u7528\u7684\u63a7\u5236\u6280\u80fd'),
    ('Damage taken per player, broken down by ability. Good for spotting who\'s standing in bad stuff or taking avoidable damage.',
     '\u6bcf\u4f4d\u73a9\u5bb6\u7684\u627f\u4f24\u660e\u7ec6(\u6309\u6cd5\u672f\u5206\u89e3)\uff0c\u53d1\u73b0\u8c01\u7ad9\u9519\u4f4d\u7f6e\u6216\u8eb2\u4e0d\u5f00\u578c\u5bb3'),
    ('DPS for the fight. Click any player to see their full breakdown.',
     '\u6218\u6597 DPS \u3002\u70b9\u51fb\u73a9\u5bb6\u540d\u67e5\u770b\u8be6\u7ec6\u5206\u89e3'),
    ('Detailed damage breakdown per DPS player \u2014 total damage, DPS, damage taken, and key CDs at a glance.',
     'DPS \u73a9\u5bb6\u8be6\u7ec6\u5206\u89e3 \u2014 \u603b\u4f24\u5bb3/DPS/\u627f\u4f24/\u5173\u952e\u6280\u80fd\u4e00\u89c8\u65e0\u997e'),
    ('Scorecard for this pull.', '\u672c\u573a\u6218\u6597\u8bc4\u5206\u5361'),
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
     '\u6bcf\u4f4d\u73a9\u5bb6\u7684\u7a7a\u6863\u65f6\u957f\u3002\U0001f7e2 \u6b63\u5e38\u8f93\u51fa \u00b7 \U0001f534 \u5212\u6c34\u3002 5 \u5206\u949f\u6218\u6597 10% \u7a7a\u6863 = \u6d6a\u8d39 30 \u79d2'),
    ('Seconds of zero damage output as a % of fight duration. &gt;10% on a long fight is a red flag.',
     '\u96f6\u8f93\u51fa\u65f6\u957f\u5360\u6218\u6597\u65f6\u957f\u7684\u767e\u5206\u6bd4\u3002\u8d85\u8fc7 10% \u9700\u8981\u5173\u6ce8'),
    ('Pull-over-pull comparison for this boss. Analyze multiple pulls and see DPS trends, death reduction, and CD improvement over attempts.',
     '\u540c Boss \u591a\u6b21\u5c1d\u8bd5\u5bf9\u6bd4 \u2014 DPS \u8d8b\u52bf\u3001\u6b7b\u4ea1\u51cf\u5c11\u3001\u6280\u80fd\u8986\u76d6\u7387\u53d8\u5316'),
    ('Analyze a second pull of the same boss to see the comparison.',
     '\u5206\u6790\u540c Boss \u7684\u7b2c\u4e8c\u573a\u6218\u6597\u8fdb\u884c\u5bf9\u6bd4'),
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

    # ── Round 3：全面补全遗漏的英文 UI 标签 / 图标标签 / 长句 ──
    ('% of Raid ↕', '团队占比 ↕'),
    ('Active ↕', '正常输出 ↕'),
    ('Activity', '活动'),
    ('Add DPS ↕', '附加 DPS ↕'),
    ('Add Damage', '附加伤害'),
    ('Aftershock', '余震'),
    ('Analyze Selected Fight', '分析选中战斗'),
    ('Applications', '职业'),
    ('Applications ↕', '职业 ↕'),
    ('Auto-generated pull summary — ready to paste into Discord.', '自动生成的战斗总结 — 可直接粘贴到 Discord'),
    ('Avoidable', '可避免'),
    ('Avoidable %', '可避免%'),
    ('Avoidable % ↕', '可避免% ↕'),
    ('Avoidable ↕', '可避免 ↕'),
    ('Build Links', '构建链接'),
    ('CC Used', '控制使用'),
    ('CC used per player — stuns, roots, incaps.', '每位玩家的控制技能 — 眩晕、定身、禁锢'),
    ('Client ID', '客户端 ID'),
    ('Client Secret', '客户端密钥'),
    ('Consumables', '消耗品'),
    ('Consumables ↕', '消耗品 ↕'),
    ('Counts are what Warcraft Logs reported in the snapshot, not guaranteed maximum possible slots. Consumables only show the auras Warcraft Logs exposed for that pull.', '数据来自 Warcraft Logs 快照中的记录，并非最大可能槽位数。消耗品仅显示该次战斗中 WCL 实际出现的光环'),
    ('Detailed', '详细'),
    ('Discord Detailed', 'Discord 详细'),
    ('Discord Short', 'Discord 简洁'),
    ('Dmg Taken ↕', '承伤 ↕'),
    ('DTPS', '死亡/秒'),
    ('DTPS ↕', '死亡/秒 ↕'),
    ('Effective ↕', '有效 ↕'),
    ('Enchant Count', '附魔数'),
    ('Enchant Count ↕', '附魔数 ↕'),
    ('Fix Next Pull / Why It Matters', '修正下一次开怪 / 为什么重要'),
    ('Format:', '格式:'),
    ('Go to', '跳转至'),
    ('Guild Logs', '公会日志'),
    ('Guild Search', '公会搜索'),
    ('Healer HPS for the fight.', '本场战斗治疗量 HPS'),
    ('Huntmaster', '猎人大师'),
    ('Load Fights', '加载战斗'),
    ('Loading Raider.io profiles...', '正在加载 Raider.io 档案...'),
    ('Longest Hold', '最长承受'),
    ('Longest Hold ↕', '最长承受 ↕'),
    ('Looks like:', '示例如:'),
    ('Main Target % ↕', '主目标% ↕'),
    ('Main Target DPS ↕', '主目标 DPS ↕'),
    ('Main Target Damage', '主目标伤害'),
    ('Mechanic ↕', '机制 ↕'),
    ('Missed ↕', '漏掉 ↕'),
    ('Missing Prep', '缺失准备'),
    ('Missing Prep ↕', '缺失准备 ↕'),
    ('Officer', '干部'),
    ('Officer Notes', '干部笔记'),
    ('Off CDs ↕', '防御冷却 ↕'),
    ('Overheal ↕', '过疗 ↕'),
    ('Parse % ↕', '分数% ↕'),
    ('Paste URL', '粘贴 URL'),
    ('Personal Profile', '个人档案'),
    ('Pick a Raid Night', '选择团本日'),
    ('Pings', '提示'),
    ('Player Detail', '玩家详情'),
    ('Player Pings', '玩家提示'),
    ('Player:', '玩家:'),
    ('Player ↕', '玩家 ↕'),
    ('Players Hit', '命中玩家'),
    ('Players ↕', '玩家 ↕'),
    ('Pull duration:', '战斗时长:'),
    ('Raid roster', '团队名册'),
    ('Rank ↕', '排名 ↕'),
    ('Ready Check+', '就位确认+'),
    ('Ready Check+ ↕', '就位确认+ ↕'),
    ('Reset Setup', '重置设置'),
    ('Role ↕', '定位 ↕'),
    ('Save &amp; Continue', '保存并继续'),
    ('Search', '搜索'),
    ('Short', '简洁'),
    ('Show:', '显示:'),
    ('Socketed Gems', '镶嵌宝石'),
    ('Socketed Gems ↕', '镶嵌宝石 ↕'),
    ('Sort by Avoidable or Avoidable % first when you want the fastest coaching read.', '想快速给出教练建议时，先按可避免或可避免%排序'),
    ('Sort by players hit or longest hold when the same mechanic keeps derailing pulls.', '当同一机制反复导致灭团时，按命中玩家或最长承受排序'),
    ('Sort:', '排序:'),
    ('Spec ↕', '专精 ↕'),
    ('Spell Detail', '技能详情'),
    ('Start with the first death, then switch to repeats if the same player or same mechanic keeps ending pulls.', '从第一次死亡开始，若同一玩家或同一机制反复导致灭团，再切换到重复死亡'),
    ('Time ↕', '时间 ↕'),
    ('Total Dmg ↕', '总伤害 ↕'),
    ('Total Taken', '总承受'),
    ('Total Taken ↕', '总承受 ↕'),
    ('Used ↕', '使用 ↕'),
    ('Void Eruption', '虚空爆发'),
    ('Watch', '查看'),
    ('Zoom:', '缩放:'),
    ('Prev:', '上一次:'),
    ('iLvl', '装等'),
    ('iLvl ↕', '装等 ↕'),
    ('Sim ↗', '模拟 ↗'),
    ('>Pot<', '>药水<'),
    ('Killing Ability', '击杀方式'),
    ('Killing Blow', '致命一击'),
    ('Killing blow', '致命一击'),
    ('All Players', '全部玩家'),
    ('All Reports', '全部报告'),
    ('All player deaths ordered by time. Killing Blow shown where available.', '按时间排序的全部玩家死亡记录，致命一击若可用则显示'),
    ('All player deaths ordered by time. Killing blow shown where available.', '按时间排序的全部玩家死亡记录，致命一击若可用则显示'),
    # 图标标签
    ('Open source', '开源'),
    ('🛑 CC', '🛑 控制'),
    ('⚔️ Offensive CDs', '⚔️ 爆发冷却'),
    ('🛡️ Defensives', '🛡️ 减伤'),
    ('💥 Dmg Taken', '💥 承伤'),
    ('🎯 Mechanic Deaths', '🎯 机制死亡'),
    ('🎯 Mechanic Deaths by Ability', '🎯 按技能分类的机制死亡'),
    ('🧿 Mechanics', '🧿 机制'),
    ('⚠️ Wipe Summary', '⚠️ 灭团总结'),
    ('🔁 Pull Compare', '🔁 拉怪对比'),
    ('🔄 CD Timeline', '🔄 冷却时间轴'),
    ('📊 DPS Breakdown', '📊 DPS 分解'),
    ('💊 Heal Breakdown', '💊 治疗分解'),
    ('💚 Raid CDs', '💚 团队冷却'),
    ('👹 Boss Abilities', '👹 首领技能'),
    ('📋 Copy to Clipboard', '📋 复制到剪贴板'),
    ('🔍 Open source', '🔍 开源'),
    ('🚫 Not your WCL login', '🚫 不是你的 WCL 登录'),
    ('🔑 3 steps — takes 2 minutes:', '🔑 3 步 — 只需 2 分钟：'),
    ('🧬 Build + Ready', '🧬 配置 + 就位'),
    ('🌿 Made by Sumanis — Resto Druid', '🌿 由 Sumanis 制作 — 恢复德鲁伊'),
    ('🛡️ Tank died — almost always the wipe cause', '🛡️ 坦克阵亡 — 几乎总是灭团原因'),
    ('🛡️ TANK DIED — almost always the wipe cause', '🛡️ 坦克阵亡 — 几乎总是灭团原因'),
    ('Wipefest-style mechanic clarity: dangerous debuffs, repeat offenders, and raid damage pressure without burying you in raw log spam.', '灭团风格的机制梳理：精准定位危险 debuff、重复犯错者，以及团伤压力，而不被原始日志淹没'),
    # 第四轮增补 — tab标签 / 表头 / hero feature
    ('Players Killed', '被击杀'),
    ('⚡ Interrupts', '⚡ 打断'),
    ('✨ Dispels', '✨ 驱散'),
    ('📈 Summary', '📈 汇总'),
    ('💚 Raid CDs', '💚 团队技能'),
    ('Mechanic death breakdown', '机制致死分解'),
    ('Mechanic Deaths', '机制死亡'),
    ('⚡ Bloodlust', '⚡ 嗜血'),
    ('Rank', '排名'),
    ('Player Detail', '玩家详情'),
    ('Personal Profile', '个人档案'),
    ('Player Pings', '玩家提示'),
    ('WarcraftLogs API Credentials', 'WarcraftLogs API 凭据'),
    ('WarcraftLogs username', 'WarcraftLogs 用户名'),
    ('and log in, then click', '登录后点击'),
    (', copy that URL.', '，复制该链接。'),
    ('in the top right', '点击右上角'),
    ('+ Create Client', '+ 创建客户端'),
    ('warcraftlogs.com/api/clients/', 'warcraftlogs.com/api/clients/（WCL 开发者页面）'),
    ('warcraftlogs.com', 'warcraftlogs.com'),
    ('RaidMirror', '战镜'),
    # 第四轮补强 — Discord 复制区与死亡次数
    ('Vorasius · ❌ Wipe · 3:51 · 4 deaths', 'Vorasius · ❌ 灭团 · 3:51 · 4 次死亡'),
    ('0 deaths · 4.2M DPS', '0 次死亡 · 4.2M DPS'),
    ('4 deaths · 3.8M DPS', '4 次死亡 · 3.8M DPS'),
    (' deaths', ' 次死亡'),
    # 碎片阻挡规则 — 防止短词规则误伤长词（必须比 Kill/Potion 等短规则长）
    ('Killing Spree', '杀戮盛筵'),
    ('Killing Blow', '致命一击'),
    ('Killing Ability', '击杀方式'),
    ('Top Killers', '致命 TOP3'),
    ('Potions are slipping', '有玩家漏用药水'),
    ('Potions ', '药水 '),
    ('Potions Used', '已用药水'),
    ('Potion and Healthstone usage per player during the fight.', '每位玩家的药水/治疗石使���情况'),
    ('Wipefest', '灭团风格'),
]

print(f"[2/7] UI \u6587\u6848\u7ffb\u8bd1: {len(UI_REPLACEMENTS)} \u6761")
# 长串优先：避免短词规则先把长句拆碎导致整句匹配失败
for old, new in sorted(UI_REPLACEMENTS, key=lambda kv: -len(kv[0])):
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
     '\u8be5\u62a5\u544a\u4e2d\u6ca1\u6709\u627e\u5230\u6218\u6597'),
    ('Please select a fight to analyze.',
     '\u8bf7\u9009\u62e9\u4e00\u573a\u6218\u6597\u8fdb\u884c\u5206\u6790'),
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
    ('prepots not trackable', '\u5f00\u6218\u836f\u6c34\u65e0\u6cd5\u8ddf\u8e2a'),

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
     '\u4e00\u952e\u81ea\u52a8\u52a0\u8f7d\u6700\u65b0\u6218\u6597'),
    ('Auto-scan: On', '\u81ea\u52a8\u626b\u63cf: \u5df2\u5f00\u542f'),
    ('Polls every 90s for new pulls while you raid',
     '\u5f00\u56e2\u671f\u95f4\u6bcf 90 \u79d2\u81ea\u52a8\u68c0\u6d4b\u65b0\u6218\u6597'),
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

    # JS \u6a21\u677f\u5b57\u7b26\u4e32 (运行时动态拼接)
    (' \u00b7 Boss at ', ' \u00b7 Boss \u8840\u91cf '),
    (' \u00b7 first @ ', ' \u00b7 \u9996\u6b21 @ '),
    ('\U0001f6e1\ufe0f Tank death: ', '\U0001f6e1\ufe0f \u5766\u514b\u9635\u4ea1: '),
    (' \u2014 almost always the wipe cause', ' \u2014 \u51e0\u4e4e\u603b\u662f\u706d\u56e2\u539f\u56e0'),
    (' \U0001f6e1\ufe0f TANK DIED', ' \U0001f6e1\ufe0f \u5766\u514b\u9635\u4ea1'),
    ('\U0001f525 Primary wipe cause: ', '\U0001f525 \u4e3b\u8981\u706d\u56e2\u539f\u56e0: '),
    ('\U0001f480 First death: ', '\U0001f480 \u9996\u6b21\u6b7b\u4ea1: '),
    ('\u2694\ufe0f Critical CD failures: ', '\u2694\ufe0f \u5173\u952e\u6280\u80fd\u9057\u6f0f: '),
    ('\U0001f9ea No potion detected: ', '\U0001f9ea \u672a\u68c0\u6d4b\u5230\u836f\u6c34: '),
    (' (prepots may not always be visible in logs)', ' (\u5f00\u6218\u836f\u6c34\u53ef\u80fd\u4e0d\u53ef\u89c1)'),
    ('\u2139\ufe0f Short pull (', '\u2139\ufe0f \u77ed\u6682\u6218\u6597 ('),
    ('\u2705 Clean pull \u2014 no major issues detected', '\u2705 \u5e72\u51c0\u6218\u6597 \u2014 \u672a\u53d1\u73b0\u91cd\u5927\u95ee\u9898'),
    ('\U0001f480 Wipe', '\U0001f480 \u706d\u56e2'),

    # Discord 复制区 — 死亡次数
    ('+deathList.length+\' deaths\'', '+deathList.length+\' \u6b21\u6b7b\u4ea1\''),
    ('\' death\'+(p.deaths.length>1?\'s\':\'\')', '\' \u6b21\u6b7b\u4ea1\''),

    # Analysis page localization contract
    ('This is the short list to talk through before diving into raw tables.', '本区域列出进入原始表格前最值得讨论的事项。'),
    ('This log did not expose usable prep-aura snapshots.', '该日志未提供可用的战前增益快照。'),
    ('No obvious raid-lead action items on this pull.', '本次尝试未发现明确的团队指挥事项。'),
    ('No repeated debuff mechanic stood out on this pull.', '本次战斗未发现反复出现的减益机制问题。'),
    ('No clear boss-event coverage windows were detected for this pull.', '本次战斗未识别到明确的 Boss 技能覆盖窗口。'),
    ('No cooldown or boss-ability timeline data detected', '未检测到冷却或 Boss 技能时间轴数据'),
    ('No spell breakdown available.', '暂无法术分解数据。'),
    ('No healing breakdown available.', '暂无治疗分解数据。'),
    ('Generated by 🔭 RaidLens', '由 🔭 战镜生成'),
    ('Raid Lead Summary', '团长摘要'),
    ('Pull Trend Summary', '尝试趋势'),
    ('Mechanic Failures', '机制失误'),
    ('Cooldown Coverage', '冷却覆盖'),
    ('Death Context', '死亡上下文'),
    ('Consumable Snapshot', '消耗品快照'),
    ('Missed Off CDs', '遗漏爆发技能'),
    ('Off CDs', '爆发技能'),
    ('🔄 Timeline', '🔄 时间轴'),
    ('⚠️ Summary', '⚠️ 战斗总结'),
    ('Total Deaths', '死亡总数'),
    ('Potion Users', '药水使用'),
    ('Healthstone Users', '治疗石使用'),
    ('Avg DPS', '平均 DPS'),
    ('Avg HPS', '平均 HPS'),
    ('Recent hits:', '死亡前承伤：'),
    ('No recent hit context', '无死亡前承伤记录'),
    ('No recent defensive', '最近未使用减伤'),
    ('No HS', '未使用治疗石'),
    ('Pot ✓', '药水 ✓'),
    ('Boss window:', 'Boss 技能窗口：'),
    ('Coverage gap near', '减伤空缺靠近'),
    ('FILTER', '筛选'),
    ('COPY FORMAT', '复制格式'),
    ('Snapshot unavailable', '快照不可用'),
    ('No readiness data', '无就位数据'),
    ('No flagged issues', '未发现问题'),
    ('Player Modal', '玩家详情'),
    ('Session trend:', '本次会话趋势：'),
    ('First death:', '首次死亡：'),
    ('No deaths', '无死亡'),
    ('No pots:', '未用药水：'),
    ('None — clean pull!', '无——本次尝试很干净！'),
]

print(f"[3/7] JS \u5b57\u7b26\u4e32\u7ffb\u8bd1: {len(JS_REPLACEMENTS)} \u6761")
# 长串优先：避免短词规则先把长句拆碎导致整句匹配失败
for old, new in sorted(JS_REPLACEMENTS, key=lambda kv: -len(kv[0])):
    content = content.replace(old, new)


# ══════════════════════════════════════════════════════════
#  ③ 职业/专精 → 国服中文 (显示层替换, 不改变 SPEC_OFFS 判定用的英文键)
# ══════════════════════════════════════════════════════════
CLASS_DISP = [
    ('${p.spec||p.cls}', '${znSpec(p.spec)||znCls(p.cls)}'),
    ('${player.spec||player.cls}', '${znSpec(player.spec)||znCls(player.cls)}'),
    ('${r.spec||""} ${r.class||""}', '${znSpec(r.spec)||""} ${znCls(r.class)||""}'),
    ('${p.cls||"?"}${p.spec?" · "+p.spec:""}', '${znCls(p.cls)||"?"}${p.spec?" · "+znSpec(p.spec):""}'),
    ('const ROLE_LABEL = {tanks:"Tank", healers:"Healer", dps:"DPS"};',
     'const ROLE_LABEL = {tanks:"\u5766\u514b", healers:"\u6cbb\u7597", dps:"\u8f93\u51fa"};'),
]
for old, new in CLASS_DISP:
    content = content.replace(old, new)
print("[3.5/7] \u804c\u4e1a/\u4e13\u7cbe \u2192 \u56fd\u670d\u4e2d\u6587: 5 \u5904\u663e\u793a\u70b9")


# ══════════════════════════════════════════════════════════
#  ④ CSS 美化 (中文字体栈 / 配色微调 / 圆角增强)
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
function znName(en) {{ /* EN→ZH fallback for SPEC_OFFS matches */ const m={{"Recklessness":"鲁莽","Avenging Wrath":"复仇之怒","Arcane Power":"奥术强化","Tranquility":"宁静","Bloodlust":"嗜血","Heroism":"英勇","Time Warp":"时间扭曲","Power Infusion":"力量灌注","Dark Ascension":"黑暗飞升","Celestial Alignment":"星辰连结","Guardian of Azeroth":"艾泽拉斯的守护者","Synod Synapse":"突触神经","Barkskin":"树皮术","Survival Instincts":"生存本能","Frenzied Regeneration":"狂暴恢复","Shield Wall":"盾墙","Last Stand":"破釜沉舟","Icebound Fortitude":"冰封之韧","Divine Shield":"圣盾术","Metamorphosis":"恶魔变形"}}; return m[en] || (en || ""); }}
var ZN_ENC={{}}, ZN_ENC_NAME={{}}, ZN_INST={{}}, ZN_INST_NAME={{}};
function _fill(map,nameMap,obj){{ if(!obj) return; for(var k in obj){{ var v=obj[k]; if(k) map[k]=v; if(v) nameMap[v]=v; }} }}
function znEnc(id,en){{ return (id&&ZN_ENC[id])||(en&&ZN_ENC_NAME[en])||(en||""); }}
function znInst(id,en){{ return (id&&ZN_INST[id])||(en&&ZN_INST_NAME[en])||(en||""); }}
// ===== 职业/专精 → 国服中文名 (显示层, 不改 SPEC_OFFS 逻辑键) =====
const CLS_ZH={{"Warrior":"战士","Paladin":"圣骑士","Hunter":"猎人","Rogue":"盗贼","Priest":"牧师","DeathKnight":"死亡骑士","Death Knight":"死亡骑士","Shaman":"萨满祭司","Mage":"法师","Warlock":"术士","Monk":"武僧","Druid":"德鲁伊","DemonHunter":"恶魔猎手","Demon Hunter":"恶魔猎手","Evoker":"唤魔师"}};
const SPEC_ZH={{"Arms":"武器","Fury":"狂怒","Protection":"防护","Retribution":"惩戒","Holy":"神圣","Discipline":"戒律","Beast Mastery":"野兽控制","Marksmanship":"射击","Survival":"生存","Outlaw":"狂徒","Assassination":"刺杀","Subtlety":"敏锐","Shadow":"暗影","Unholy":"邪恶","Frost":"冰霜","Blood":"鲜血","Enhancement":"增强","Elemental":"元素","Restoration":"恢复","Fire":"火焰","Arcane":"奥术","Affliction":"痛苦","Demonology":"恶魔学识","Destruction":"毁灭","Windwalker":"踏风","Mistweaver":"织雾","Brewmaster":"酒仙","Balance":"平衡","Feral":"野性","Guardian":"守护","Havoc":"浩劫","Vengeance":"复仇","Devourer":"噬灭","Devastation":"毁灭","Augmentation":"增辉","Preservation":"恩护"}};
function znCls(en){{ return CLS_ZH[en] || (en||""); }}
function znSpec(en){{ return SPEC_ZH[en] || (en||""); }}
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
#    兼容有/无空格写法：const A="x"; 或 const A = "x";
# ══════════════════════════════════════════════════════════
content = re.sub(
    r'const\s+PKCE_CLIENT_ID\s*=\s*"[^"]*";',
    'const PKCE_CLIENT_ID="019fa737-306d-73f6-9327-1225f5b6edc6";',
    content,
    count=1
)
content = re.sub(
    r'const\s+PKCE_REDIRECT\s*=\s*"[^"]*";',
    'const PKCE_REDIRECT=window.location.origin; // auto use current domain',
    content,
    count=1
)

# ══════════════════════════════════════════════════════════
#  ⑦ 仓库链接替换（统一指向当前项目）
# ══════════════════════════════════════════════════════════
OWN_REPO = "https://github.com/panhuanghe/RaidMirror-ZH"
OWN_README = OWN_REPO + "#readme"
content = content.replace(
    "https://github.com/Fisheye3D/Raidlenshosted/blob/main/README.md",
    OWN_README
)
content = content.replace(
    "https://github.com/Fisheye3D/Raidlenshosted",
    OWN_REPO
)
content = re.sub(
    r'\s*<a href="https://buymeacoffee\.com/Raidlens"[^>]*>☕ Support RaidLens</a>\s*',
    '',
    content
)


# ══════════════════════════════════════════════════════════
#  ⑧ 页面元信息更新
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
#  ⑨ 修复 Hero 区域破损图片: 3.5MB base64 PNG → 外部 PNG(原站图)
#     同时把 PNG 二进制提取到 assets/, 使 clone 后 `python build_zh.py`
#     即可自动还原, 仓库无需提交二进制文件
# ══════════════════════════════════════════════════════════
import re as _re
# 9a. 先提取 PNG 二进制 (替换 src 前, base64 仍在 vendor 中)
#     以【字节】方式读取 vendor, 直接对 base64 字节解码, 避免 UTF-8 把 base64 中的
#     高位字节误读为 multibyte 字符而被丢掉, 导致 PNG 缺字节损坏
with open(SRC, "rb") as _vf:
    _vraw = _vf.read()
_m = _re.search(rb'<div class="hero-gnome"[^>]*>\s*<img src="data:image/png;base64,([^"]*)"', _vraw)
if _m:
    os.makedirs(ASSETS, exist_ok=True)
    with open(os.path.join(ASSETS, "hero-gnome.png"), "wb") as _pf:
        _pf.write(base64.b64decode(_m.group(1)))
    print("[9a] 提取 hero-gnome.png 二进制 -> assets/hero-gnome.png")
else:
    print("[9a] 未找到 hero-gnome base64, 跳过 PNG 提取")

# 9b. 将内联 base64 <img> 替换为外部引用（WebP + PNG 回退）
content = _re.sub(
    r'<div class="hero-gnome" aria-hidden="true">\s*<img src="data:image/png;base64,[^"]*"[^>]*>',
    "<div class=\"hero-gnome\" aria-hidden=\"true\"><picture><source type=\"image/webp\" srcset=\"assets/hero-gnome-202x264.webp 1x, assets/hero-gnome-404x528.webp 2x\"><img src=\"assets/hero-gnome.png\" alt=\"战镜\" width=\"202\" height=\"264\" decoding=\"async\" fetchpriority=\"high\"></picture>",
    content,
    flags=_re.S,
)
print("[9b] 替换 hero-gnome src: base64 → 外部 picture(WebP) + PNG 回退")

# 9c. 生成 WebP 尺寸变体（显著降低首屏图片体积）
try:
    from PIL import Image
    _src = os.path.join(ASSETS, "hero-gnome.png")
    if os.path.exists(_src):
        _im = Image.open(_src).convert("RGB")

        def _make_variant(_w, _h, _name):
            _target_ratio = _w / _h
            _sw, _sh = _im.size
            _src_ratio = _sw / _sh
            if _src_ratio > _target_ratio:
                _new_w = int(_sh * _target_ratio)
                _left = int((_sw - _new_w) * 0.30)  # x 对齐 ~ object-position:30%
                _left = max(0, min(_left, _sw - _new_w))
                _box = (_left, 0, _left + _new_w, _sh)
            else:
                _new_h = int(_sw / _target_ratio)
                _top = (_sh - _new_h) // 2        # y 对齐 center
                _top = max(0, min(_top, _sh - _new_h))
                _box = (0, _top, _sw, _top + _new_h)
            _out = _im.crop(_box).resize((_w, _h), Image.Resampling.LANCZOS)
            _out_path = os.path.join(ASSETS, _name)
            _out.save(_out_path, "WEBP", quality=80, method=6)
            return _out_path

        _v1 = _make_variant(202, 264, "hero-gnome-202x264.webp")
        _v2 = _make_variant(404, 528, "hero-gnome-404x528.webp")
        print(f"[9c] 生成 WebP 变体: {_v1}, {_v2}")
    else:
        print("[9c] 未找到 hero-gnome.png，跳过 WebP 生成")
except Exception as _e:
    print(f"[9c] WebP 生成失败(已回退 PNG): {_e}")

# 9d. 防止中文文案替换误伤 JS 内置构造器名
#     e.g. URLSearchParams 被 "Search"→"搜索" 规则污染成 URL搜索Params
content = content.replace("URL搜索Params", "URLSearchParams")
print("[9d] 修复 URLSearchParams 标识符被误替换问题")

# ══════════════════════════════════════════════════════════
#  ⑩ PKCE 兼容修复：crypto.subtle 不可用时提供 SHA-256 fallback
# ══════════════════════════════════════════════════════════
_pkce_block = '''
// PKCE crypto helpers -- generate verifier + challenge
function _pkceRightRotate(v,a){ return (v>>>a) | (v<<(32-a)); }
function _pkceSha256AsciiBuffer(ascii){
  // Fallback SHA-256 for environments where crypto.subtle is unavailable (e.g. some HTTP contexts).
  const mathPow=Math.pow,maxWord=mathPow(2,32),lengthProperty="length";
  let i,j,words=[],asciiBitLength=ascii[lengthProperty]*8;
  let hash=_pkceSha256AsciiBuffer.h=_pkceSha256AsciiBuffer.h||[];
  let k=_pkceSha256AsciiBuffer.k=_pkceSha256AsciiBuffer.k||[];
  let primeCounter=k[lengthProperty];
  const isComposite={};
  if(primeCounter===0){
    for(let candidate=2; primeCounter<64; candidate++){
      if(!isComposite[candidate]){
        for(i=0; i<313; i+=candidate) isComposite[i]=candidate;
        hash[primeCounter]=((mathPow(candidate,.5)*maxWord)|0);
        k[primeCounter++]=((mathPow(candidate,1/3)*maxWord)|0);
      }
    }
  }
  ascii += "\\x80";
  while(ascii[lengthProperty]%64 - 56) ascii += "\\x00";
  for(i=0;i<ascii[lengthProperty];i++){
    j=ascii.charCodeAt(i);
    if(j>>8) throw new Error("PKCE verifier contains non-ASCII chars");
    words[i>>2] |= j << ((3 - i) % 4) * 8;
  }
  words[words[lengthProperty]] = ((asciiBitLength / maxWord) | 0);
  words[words[lengthProperty]] = (asciiBitLength);
  for(j=0; j<words[lengthProperty];){
    const w = words.slice(j, j += 16);
    const oldHash = hash;
    hash = hash.slice(0,8);
    for(i=0;i<64;i++){
      const w15 = w[i-15], w2 = w[i-2];
      const a = hash[0], e = hash[4];
      const temp1 = hash[7]
        + (_pkceRightRotate(e,6) ^ _pkceRightRotate(e,11) ^ _pkceRightRotate(e,25))
        + ((e & hash[5]) ^ ((~e) & hash[6]))
        + k[i]
        + (w[i] = (i<16) ? w[i] : (
            w[i-16]
            + (_pkceRightRotate(w15,7) ^ _pkceRightRotate(w15,18) ^ (w15>>>3))
            + w[i-7]
            + (_pkceRightRotate(w2,17) ^ _pkceRightRotate(w2,19) ^ (w2>>>10))
          ) | 0
        );
      const temp2 = (_pkceRightRotate(a,2) ^ _pkceRightRotate(a,13) ^ _pkceRightRotate(a,22))
        + ((a & hash[1]) ^ (a & hash[2]) ^ (hash[1] & hash[2]));
      hash = [(temp1 + temp2) | 0].concat(hash);
      hash[4] = (hash[4] + temp1) | 0;
      hash.pop();
    }
    for(i=0;i<8;i++) hash[i] = (hash[i] + oldHash[i]) | 0;
  }
  const out = new Uint8Array(32);
  for(i=0;i<8;i++){
    out[i*4]   = (hash[i]>>>24) & 0xff;
    out[i*4+1] = (hash[i]>>>16) & 0xff;
    out[i*4+2] = (hash[i]>>>8) & 0xff;
    out[i*4+3] = hash[i] & 0xff;
  }
  return out.buffer;
}

async function _pkceSha256BufferFromVerifier(verifier){
  const subtle = window.crypto && window.crypto.subtle;
  if(subtle && typeof subtle.digest === "function"){
    const enc = new TextEncoder().encode(verifier);
    return await subtle.digest("SHA-256", enc);
  }
  // fallback path
  return _pkceSha256AsciiBuffer(verifier);
}

async function pkceChallenge(){
  // generate a 32-byte random verifier, base64url encoded
  if(!(window.crypto && typeof window.crypto.getRandomValues==="function")){
    throw new Error("Browser crypto not available. Please use a modern browser.");
  }
  const arr=new Uint8Array(32);
  window.crypto.getRandomValues(arr);
  const verifier=btoa(String.fromCharCode.apply(null,arr))
    .replace(/[+]/g,"-").replace(/[/]/g,"_").replace(/[=]/g,"");
  // S256 only -- WCL requires this, plain is not accepted
  const hash=await _pkceSha256BufferFromVerifier(verifier);
  const challenge=btoa(String.fromCharCode.apply(null,new Uint8Array(hash)))
    .replace(/[+]/g,"-").replace(/[/]/g,"_").replace(/[=]/g,"");
  return {verifier,challenge,method:"S256"};
}
'''
content = re.sub(
    r'// PKCE crypto helpers -- generate verifier \+ challenge\s*async function pkceChallenge\(\)\{.*?return \{verifier,challenge,method:"S256"\};\s*\}',
    _pkce_block,
    content,
    count=1,
    flags=re.S
)
print("[10] PKCE fallback: crypto.subtle 不可用时改用内置 SHA-256")

# ─── 写入输出 ─────────────────────────────────────────────
os.makedirs(os.path.dirname(DST), exist_ok=True)
with open(DST, "w", encoding="utf-8") as f:
    f.write(content)

print(f"[7/7] \u8f93\u51fa: {DST} ({os.path.getsize(DST)//1024} KB)")
print("\n\u2705 \u6218\u955c ZhanJing \u4e2d\u6587\u7248\u6784\u5efa\u5b8c\u6210!")
