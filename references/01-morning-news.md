# 01 晨间简报 + GitHub 项目推荐

- 默认时间：每天 08:30（cron `30 8 * * *`）
- 默认投递：用户自己的消息目标（微信 / Telegram / …）
- 取完简报直接就是最终回复，不要输出过程

必要准备：

1. 一个用来记录「已推过的仓库」的文件，默认 `<资料目录>/GitHub推荐记录.md`，不存在就当空的。不写这个文件，每天早上都会推同一个热门仓库。
2. 能搜 GitHub 的手段：Hermes 里直接 `terminal` 跑已登录的 `gh`（需要 `gh auth login`）；没有 gh 就用 `web_search` + `site:github.com`。

## Prompt 模板（可直接粘贴）

```text
搜索并整理过去24小时（重点是昨天一天）AI 与科技领域的重要新闻，包括：新发布的大模型或重要模型更新；主要科技公司（OpenAI、Google、Anthropic、Meta、微软、字节、阿里、百度、腾讯等）的重大动态；AI 领域的重要突破或论文；以及数码圈消息（新发布的手机/笔记本/平板/耳机/手表、芯片、系统更新）。如果当天有存储与内存的行情动态（内存条/SSD 涨价降价、存储芯片价格、AI 抢产能导致硬件涨价），单独列一条。

用中文整理成简洁简报：5~8 条，每条【小标题】+ 一句话概述，尽量注明来源；开头加一句简短的日期问候；语气轻松自然。

简报之后加固定栏目【今日 GitHub 项目】，推荐 1~2 个和用户最近在学的东西相关、质量高的开源项目。做法：
1) 先看他在学什么：读 <资料目录>/每日小复盘_记录.md 最后 3~5 条（看「学到 / 卡住 / 明天第一件事 / 动的线」），必要时再读 <资料目录>/计划表.md。他现在的线是：<在这里写下他的学习线，例如 C 语言、单片机、AI、英语、打字>。
2) 找项目：在 terminal 用已登录的 gh 按「topic + star 门槛」搜，比随便搜关键词准得多，例如：
   gh search repos --topic c-programming --stars '>500' --sort stars --limit 10 --json fullName,stargazersCount,pushedAt,description
   gh search repos --topic embedded-c --stars '>200' --sort updated --limit 10 --json fullName,stargazersCount,pushedAt,description
   gh search repos --topic machine-learning --stars '>5000' --sort stars --limit 10 --json fullName,stargazersCount,pushedAt,description
   再用 gh api repos/<owner>/<name> --jq '.stargazers_count, .pushed_at, .description' 核实 star 数和最近更新时间。一次搜不到合适的就换关键词或 topic（beginner-project / awesome / algorithms / stm32 / micropython / llm / c-programming）。gh 用不了（没网、没登录）才改用 web_search 搜 site:github.com。
3) 质量门槛：star 一般 500 以上（冷门但很好的嵌入式/教学项目 100 以上也行）；最近一年内有提交；README 说人话、对初学者真的有用；宁缺勿滥，挑不出好的就只推 1 个，实在没有就写一句「今天没找到特别合适的」。不推爬虫脚本、薅羊毛、破解类项目。
4) 不重复推：先读 <资料目录>/GitHub推荐记录.md（不存在就当空的），里面记过的仓库不要再提；推完把这次的项目追加进去，每行：- YYYY-MM-DD owner/name（一句话为什么推荐）。
5) 每个项目写：
【项目名】owner/name ⭐ 1234（最近更新 2026-08）
它是什么：一句话。
为什么适合你：结合他正在学的那条线说一句。
怎么上手：clone 下来先看/先跑哪个文件或哪一章（要具体）。

整条消息保持简洁：新闻 5~8 条 + 项目 1~2 个，末尾不用总结、不用客套。只输出最终简报，不要输出过程。
```

**同步 Notion**（如果接了，见 `references/06-notion-sync.md`）：每个推荐项目跑一次
`python <资料目录>/tools/notion_push.py repo --name "owner/name" --why "为什么适合" --step "上手第一步" --date 今天`，失败跳过。

## 验收标准

- 项目和他最近两周的复盘内容真的对得上（不是随便推热榜）；
- star 数、最近更新写的是真查到的数字，不是编的；
- 去重文件里能查到这次推的项目。
