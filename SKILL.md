---
name: growth-flywheel
description: "Use when 搭建或维护个人成长飞轮：晨简报+GitHub 项目推荐、日/周复盘、Excel 台账。"
version: 1.0.0
author: 张高平 (gaopingzhang72-oss)
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [growth, review, cron, automation, journaling, self-improvement, productivity]
    category: productivity
    homepage: https://github.com/gaopingzhang72-oss/growth-flywheel
---

# 成长飞轮（Growth Flywheel）

一句话：用「每天有人问你一句 + 每周有人给你算一次账」的轻量自动化，把学习从「靠自觉」变成「靠系统」。

这套东西由 4 个定时任务 + 1 个台账脚本组成，全部记录落进同一张 Excel，可以随时回头看「这几周我到底动了哪几条线」。

## 什么时候用这个技能

- 用户想搭一套「晨间简报 → 每日复盘 → 每周复盘 → 阶段总结」的个人成长闭环；
- 用户已有的定时复盘要改内容（加一栏、换时间、换投递目标、改口吻）；
- 用户问「我最近做得怎么样」「哪条线断了」——**先去读台账**（xlsx / 记录 md），不要凭印象回答。

## 闭环的四段（每段的成功标准）

| 段 | 默认时间 | 成功标准 |
|---|---|---|
| 晨间简报 | 每天 08:30 | 新闻 5~8 条；末尾固定【今日 GitHub 项目】1~2 个，必须和用户最近在学的东西相关、star 数与活跃度过关、且和去重文件里记过的不重复 |
| 每日小复盘 | 每天 22:30 | 一条**简短**消息（7 行内），只要用户回四行：今天学了什么 / 卡在哪 / 明天第一件事 / 今天动了吗；他回复后写台账 |
| 每周大复盘 | 周日 21:00 | 每条线一句评价 + 一个最该改的问题 + 下周三个可验证目标；全文 15 行内，不要写成十页报告 |
| 专项小练习 | 每周 2 次 | 一道小题 + 提示；用户答了就逐句纠错 + 给示范答案，没答就放过，不追不催 |

默认的四条线：① 课内/绩点 ② 专业能力（编程语言 / 实验室 / 项目）③ 英语 ④ 运动。
运动永远单列，不要混进「今天动了哪几条线」里。

## 核心规则（改任务内容前先读）

1. **一条消息只干一件事**。晚上那条只问四行，不点评、不算账、不列长清单、不催进度。用户没回就是没回，第二天照常发。
2. **不编造**。用户没汇报的内容不写进台账；这周完全没记录到运动就写「这周没记到运动」，不要替他说好话，也不要借机说教。
3. **只追加、同日覆盖**。台账绝不删历史；同一天/同一周重复写入只覆盖那一行。
4. **疲劳期降级**。用户进入压力期（开学、考试周、实习、生病）时，「点一条没动的线」降级成「记录 + 鼓励一句」，唯一目标是别断线。默认给两周窗口，到期问用户要不要继续。
5. **运动是加餐不是任务**。每周目标里最多一个是运动项，且要小到不可能失败（「跑 3 次，每次 20 分钟」比「每周健身」好一百倍）。
6. **口吻和个人信息写在任务 prompt 里**，不要写进这个技能：不同用户要不同的称呼、语气、身份描述。

## 台账：scripts/record.py

独立 Python 脚本，只依赖 `openpyxl`。台账文件位置取环境变量 `REVIEW_XLSX`，没设就用脚本所在目录的上一级（即把脚本放在 `<资料目录>/tools/` 下，台账就是 `<资料目录>/每日复盘记录.xlsx`）。

```bash
python record.py init                                   # 建表（已存在则不动）
python record.py daily  --json 条目.json                 # 追加/覆盖某一天
python record.py weekly --json 条目.json                 # 追加/覆盖某一周
python record.py stats                                  # 只重算「③ 统计」
```

`daily` 的 JSON 字段：`date`(默认今天) / `summary` / `blocker` / `tomorrow` / `lines`(如 `"C语言、打字"`) / `sport`(如 `"跑步 30 分钟"`，明确没动写 `无`) / `score`(1~5，用户明说才填) / `raw`(原话摘录 ≤500 字) / `note`。
`weekly` 的 JSON 字段：`date` / `grade` / `clab` / `english` / `sport` / `problem` / `goals` / `last` / `extra`。

表结构：

- `① 每日打卡`：日期 / 星期 / 今天学了什么 / 卡在哪 / 明天第一件事 / 动了哪几条线 / 运动 / 自评(1-5) / 原始汇报摘录 / 备注
- `② 每周复盘`：周次 / 日期区间 / 绩点·课内 / 专业+实验室 / 英语 / 运动 / 本周主要问题 / 下周三个目标 / 上周目标达成情况 / 打卡天数 / 备注
- `③ 统计`：总打卡天数、连续打卡、平均自评、写成周复盘的周数、有运动的天数、累计运动时长(分钟)、各条线出现次数、按周折线图（打卡天数 / 平均自评 / 运动天数）

「运动」时长能自动解析「30 分钟」「1.5 小时」这类写法；写「无 / 没动 / 休息」不计入运动天数。

记录 md（`每日小复盘_记录.md`）与 xlsx 是**两套并存**的落地：md 给人逐条翻，xlsx 给统计和图表用，两边都要写。

## 同步进 Notion（可选，和 Excel 并存）

Excel 是主账本（统计和图表靠它），Notion 是手机端翻看、随手改的镜像。两个都写，互不依赖——
Notion 挂了不允许影响 Excel 记账。

脚本 `scripts/notion_push.py`：自己从 `.env` 读 `NOTION_API_KEY` 和
`NOTION_DAILY_DS / NOTION_WEEKLY_DS / NOTION_REPO_DS`，按「同一天/同一周更新，否则新建」写入，
失败只打印一行提示。完整搭建步骤 + 踩过的坑见 `references/06-notion-sync.md`。

## 维护手册

- **加/换/删一条学习线**：改 `record.py` 里的 `LINES`（统计口径）+ 每日任务的第 3 步提示 + 每周任务的评价条数。
- **加一个新栏目（如「睡眠」）**：① 在 `DAILY_HDR` 里按位置插入列名，并在 `DAILY_W` 加对应列宽；② 在 `daily()` 的 `values` 里按同样位置插入取值；③ 统计表里加口径。旧表格不用手工改，`_ensure_new_columns()` 会在下一次写入时自动插列，老数据右移不丢。
- **列号不要写死数字**：用 `D_DATE / D_SPORT / D_SCORE / D_LINES` 这类常量（`DAILY_HDR.index(名字)+1`）。
- **改时间/投递目标**：`cronjob_manage(action='update', job_id=..., schedule=..., deliver=...)`。
- **查「哪条线断了」**：读 xlsx 的 `③ 统计`（各条线出现次数）比读聊天记录靠谱；不要凭印象下结论。

## 已知坑

- **cron 在全新会话里跑，没有聊天上下文**：任务 prompt 必须自包含——把身份、路径、规则全写进去；不要指望它记得昨天说了什么。
- **Hermes cron 投递不到桌面应用**：`deliver` 要显式写目标（如 `telegram:<chat_id>`、`weixin:<id>@im.wechat`），否则消息发不出去，任务看起来「成功」但用户收不到。需要在微信/Telegram 里能接着回话的，再开 `attach_to_session=True`。
- **Windows 上 cron 里 `python` 可能不在 PATH**：退回用 Hermes 自带解释器 `"$LOCALAPPDATA/hermes/hermes-agent/venv/Scripts/python"`。
- **改表头前先备份 xlsx**：迁移逻辑只加列、不删列，但备份仍是最便宜的保险（`tools/backup/` 下留一份）。
- **去重文件必须写**：GitHub 项目推荐要落到 `GitHub推荐记录.md`，否则每天早上都会推同一个热门仓库。
- **Notion 建库别用 `POST /v1/data_sources` + properties**：那样只建出一个 `Name` 列；要 `POST /v1/databases`，字段放在 `initial_data_source.properties` 里（已建错就 `PATCH /v1/data_sources/{id}` 补字段）。
- **`data_source_id ≠ database_id`**：查询和建页面都用 `data_source_id`；搜索接口给的 `parent.database_id` 拿去做 query 会 404。往已有页面写内容用 `PATCH /v1/blocks/{id}/children`（`PATCH /v1/pages/{id}/markdown` 在 2025-09-03 会报 `body.type should be defined`）。
- **Hermes 会把技能声明的环境变量预置成空字符串**（例如 `NOTION_API_KEY=""`）：脚本读 `.env` 时必须把「空值」当作没设置，否则永远读不到真值。这条对任何自己读 .env 的脚本都成立。
- **折线图按 ISO 周聚合**，跨年时周次号会重复（第 1 周出现两次）。长期用建议把周标签换成「年-周」，或在 `rebuild_stats` 里改用日期做横轴。

## 参考文件

- `references/01-morning-news.md`：晨间简报 + GitHub 项目推荐的 prompt 模板
- `references/02-daily-review.md`：每日小复盘的 prompt 模板与 JSON 字段
- `references/03-weekly-review.md`：每周大复盘的 prompt 模板
- `references/04-speaking-practice.md`：专项小练习的 prompt 模板
- `references/05-setup.md`：从零搭建（建 cron、放资料、验证）的分步清单
- `references/06-notion-sync.md`：把复盘同步进 Notion 的搭建步骤与坑
- `templates/`：计划表模板、每日记录模板、个人配置示例
- `references/99-personal-config.local.md`：本机的真实路径、任务 id、口吻约定（**私人文件，不进公开仓库**）
