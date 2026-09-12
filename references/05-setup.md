# 05 从零搭建

## 0. 先想清楚三件事

1. **要哪几条线？** 三到四条最好维护（例：课内 / 专业能力 / 英语 / 运动）。线越多，周复盘越像报告。
2. **消息发到哪里？** 手机上的聊天工具（微信、Telegram…）比桌面应用好——能顺手回话。
3. **资料放哪？** 建议一个固定目录，例如 `<资料目录>`，里面放 `tools/record.py`、`每日复盘记录.xlsx`、`每日小复盘_记录.md`、`GitHub推荐记录.md`、`计划表.md`。

## 1. 放脚本、建表

```bash
mkdir -p <资料目录>/tools
cp scripts/record.py <资料目录>/tools/
python <资料目录>/tools/record.py init
```
（Windows 上如果 `python` 不在 PATH，用 `"$LOCALAPPDATA/hermes/hermes-agent/venv/Scripts/python"`。）

## 2. 建 4 个定时任务

在 Hermes 里直接对 Agent 说：「用 growth-flywheel 技能，把 references/01~04 里的模板建成 4 个 cron」，或者自己用 `cronjob_manage`：

| 任务 | schedule | deliver | 备注 |
|---|---|---|---|
| 晨间简报 | `30 8 * * *` | 你的消息目标 | 需要 `gh` 已登录或联网搜索 |
| 每日小复盘 | `every day at 22:30` | 你的消息目标 | 建议 `attach_to_session=True`，这样你能直接接着回 |
| 每周大复盘 | `every sunday 21:00` | 你的消息目标 | 同上 |
| 专项小练习 | `30 20 * * 2,6` | 你的消息目标 | 同上 |

**投递目标要写全**：Hermes 的 cron 发不到桌面应用，`deliver` 必须显式写平台目标（如 `weixin:<你的id>@im.wechat`）。

## 3. 准备这三个文件

- `GitHub推荐记录.md`：只有一行标题也行，任务会自己追加。
- `每日小复盘_记录.md`：见 `templates/每日小复盘_记录_模板.md`。
- `计划表.md`：见 `templates/计划表_模板.md`，把季度指标换成你自己的。

## 4. 验证（别跳过）

1. 手写一份 `_entry.json`，跑一次 `record.py daily`，确认「① 每日打卡」多了一行、③ 统计里的数字变了；
2. 跑 `record.py weekly`，确认「② 每周复盘」多了一周；
3. 用 `cronjob_manage(action='run', job_id=...)` 立刻试跑一次晨间简报和每日小复盘，确认消息真的到了你的手机；
4. 第二天早上看 ③ 统计的「连续打卡天数」是不是 1。

## 5. 隐私

公开分享这套东西时：路径换成 `<资料目录>` 占位符，去掉姓名、聊天 id、真实台账内容。台账和记录 md 永远不进仓库。
