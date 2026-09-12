# 成长飞轮 Growth Flywheel

> 用「每天有人问你一句 + 每周有人给你算一次账」的轻量自动化，把学习从**靠自觉**变成**靠系统**。
> 4 个定时任务 + 1 个台账脚本，所有记录落进同一张 Excel，随时能回头看「这几周我到底动了哪几条线」。

作者：张高平（GitHub [@gaopingzhang72-oss](https://github.com/gaopingzhang72-oss)）· MIT License

---

## 它长什么样

| 时间 | 任务 | 干什么 |
|---|---|---|
| 每天 08:30 | 晨间简报 | AI / 科技 / 数码新闻 5~8 条；末尾固定【今日 GitHub 项目】1~2 个——和你最近在学的东西相关，带 star 数、为什么适合你、怎么上手，推过的不会重复推 |
| 每天 22:30 | 每日小复盘 | 一句话回顾上次汇报 → 请你回四行：今天学了什么 / 卡在哪 / 明天第一件事 / **今天动了吗** → 点一条没动的线（疲劳期自动降级成「只记录 + 鼓励」） |
| 每周日 21:00 | 每周大复盘 | 四条线各一句评价（课内 / 专业能力 / 英语 / 运动），指出**一个**最该改的问题，给下周三个可验证目标 |
| 每周二、周六 20:30 | 专项小练习 | 一道初学者友好的口语题 + 词汇句型提示；你答题后逐句纠错并给示范答案，没答就放过 |

你回复之后，Agent 会把内容提炼成结构化数据写进《每日复盘记录.xlsx》：

- `① 每日打卡`：日期 / 星期 / 今天学了什么 / 卡在哪 / 明天第一件事 / 动了哪几条线 / **运动** / 自评 / 原话摘录 / 备注
- `② 每周复盘`：周次 / 区间 / 四条线各一句 / 本周主要问题 / 下周三个目标 / 上周达成情况 / 打卡天数
- `③ 统计`：总打卡、连续打卡、平均自评、有运动的天数、累计运动时长、各条线出现次数，外加一张按周的折线图

## 目录

```
SKILL.md              给 Agent 看的技能说明：流程、规则、维护手册、已知坑
references/           四条定时任务的 prompt 模板（可直接粘贴使用）
  01-morning-news.md      晨间简报 + GitHub 项目推荐
  02-daily-review.md      每日小复盘（含记账 JSON 字段）
  03-weekly-review.md     每周大复盘
  04-speaking-practice.md 专项小练习（以英语口语为例）
  05-setup.md             从零搭建的分步清单
scripts/record.py     台账写入脚本（openpyxl，只依赖这一个库）
templates/            计划表模板 / 每日记录模板 / 个人配置示例
```

## 快速开始（Hermes Agent）

```bash
# 1. 装上技能（或者 clone 到 $HERMES_HOME/skills/productivity/growth-flywheel/）
hermes skills install https://raw.githubusercontent.com/gaopingzhang72-oss/growth-flywheel/main/SKILL.md --yes

# 2. 找地方放资料，并建表
mkdir -p ~/growth-flywheel/tools && cp scripts/record.py ~/growth-flywheel/tools/
python ~/growth-flywheel/tools/record.py init

# 3. 建 4 个定时任务：把 references/01~04 里的 prompt 贴进 cron
#    （在 Hermes 里直接说：「用 growth-flywheel 技能，把 references/01~04 建成 4 个 cron」）
```

**投递目标一定要显式写**：Hermes 的 cron 发不到桌面应用，`deliver` 要写成你手机上能收到的目标（`weixin:<id>@im.wechat`、`telegram:<chat_id>` …），想直接在消息里接着回话就再开 `attach_to_session=True`。

细节和验证清单一律见 [`references/05-setup.md`](references/05-setup.md)。

## 不用 Hermes 也能用

`references/` 里的 prompt 是纯文本，任何「定时器 + 大模型 + 能读写文件」的工具都能照搬；
`scripts/record.py` 是独立 Python 脚本，只要 `openpyxl`：

```bash
python record.py daily  --json 条目.json     # 追加/覆盖某一天
python record.py weekly --json 条目.json     # 追加/覆盖某一周
python record.py stats                       # 重算统计与图表
```

台账位置取环境变量 `REVIEW_XLSX`，没设就用脚本上一级目录的 `每日复盘记录.xlsx`。
旧表格加新列不用手工改——下次写入时会自动插列，老数据右移不丢（改表头前仍建议备份）。

## 设计上的几条取舍

- **一条消息只干一件事**：晚上那条只问四行，不点评、不算账、不列长清单。任务一重，人就断了。
- **不编造**：用户没汇报的内容不写进台账；这周没记录到运动就写「这周没记到运动」。
- **运动是加餐不是任务**：每周目标里最多一个是运动项，且小到不可能失败。
- **疲劳期降级**：开学、考试周、实习期间，「点没动的线」换成「记录 + 鼓励」，唯一目标是别断线。

## 隐私

仓库里没有任何个人资料：路径一律写成 `<资料目录>` 占位符，姓名、聊天 id、真实台账内容都不进仓库。
你自己那份台账和记录 md 留在本地就好。

## 许可

MIT License，见 [LICENSE](LICENSE)。
