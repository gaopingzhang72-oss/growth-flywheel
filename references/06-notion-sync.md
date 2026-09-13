# 06 同步进 Notion（可选）

为什么：Excel 适合统计和画图，Notion 适合手机上翻、随手改、以后分享给别人看。
两边都写，谁挂了都不影响另一边。

## 一、准备（一次性）

1. **建集成**：浏览器打开 https://www.notion.so/developers/connections（旧地址 `notion.so/my-integrations` 会跳过来）
   → 「+ New connection」→ 选 **Internal** → 选你的 workspace → 创建 → 复制密钥（`ntn_` 开头，老的是 `secret_`）。
   注意：这个入口**只在网页版**，客户端里没有，而且名字已经从 Integrations 改成了 Connections。
2. **存密钥**：写进 `${HERMES_HOME}/.env`，一行 `NOTION_API_KEY=...`。**不要贴在聊天里**。
3. **授权页面**：在 Notion 里打开要放它的那一页 → 右上 `⋯` → **连接** → 选你的集成。
   少了这步，API 什么都看不到（查不到页面），不是密钥错。
4. **建三个数据库**（内嵌在那个页面里）：

| 数据库 | 字段（标题列在最前） |
|---|---|
| 每日复盘 | 复盘(标题) / 日期(date) / 学到 / 卡住 / 明天第一件事 / 运动 / 动的线(multi_select) / 自评(1-5)(number) |
| 每周复盘 | 周次(标题) / 区间 / 课内·绩点 / 专业+实验室 / 英语 / 运动 / 主要问题 / 下周三个目标 / 打卡天数(number) |
| 项目收藏 | 项目(标题) / 日期(date) / 为什么适合我 / 上手第一步 / 状态(select: 待看·在看·看完了) |

5. **把 id 写进 .env**：

```
NOTION_DAILY_DS=<每日复盘的数据源 id>
NOTION_WEEKLY_DS=<每周复盘的数据源 id>
NOTION_REPO_DS=<项目收藏的数据源 id>
NOTION_PROXY=http://127.0.0.1:7897     # 可选，需要代理时才加
```

6. **自检**：`python scripts/notion_push.py check` → 应打印身份和三个库的名字。

## 二、什么时候调用

```bash
python notion_push.py daily  --json _entry.json                                   # 写完 Excel 之后
python notion_push.py weekly --json _entry.json                                   # 周复盘
python notion_push.py repo --name "owner/name" --why "..." --step "..." --date 今天  # 早上推了项目
```

任何一步失败都**跳过**：不要重试、不要在消息里提、不要影响 Excel 那条主线。

## 三、踩过的坑（照抄即可）

1. **建库别用 `POST /v1/data_sources` 带 properties**——那样只会建出一个 `Name` 列，字段全丢。
   正确：`POST /v1/databases`，把字段放在 `initial_data_source.properties` 里。
   已经建错了就补：`PATCH /v1/data_sources/{data_source_id}`，`{"properties": {"Name": {"name": "复盘"}, "日期": {"date": {}}, ...}}`（改标题列名也是这个写法）。
2. **`data_source_id` 和 `database_id` 是两个 id**：查询、建页面都用 `data_source_id`；
   搜索接口返回的 `parent.database_id` 拿去做 query 会 404。
   建页面：`parent: {"type": "data_source_id", "data_source_id": "..."}`；不行再退回 `database_id`。
3. **往已有页面写内容**：`PATCH /v1/pages/{id}/markdown` 在 `Notion-Version: 2025-09-03` 会报
   `body failed validation: body.type should be defined`。改用 `PATCH /v1/blocks/{id}/children`，
   表格要写成 `table` 块（`table_width`、`has_column_header`）+ 若干 `table_row` 子块。
4. **Hermes 会把技能声明的环境变量预置成空字符串**：脚本里读 `.env` 时，「空值」要当成没设置
   （`if k and not os.environ.get(k)`），否则真值永远读不进来。
5. **代理只给这个脚本用**：设 `NOTION_PROXY`，别把 `HTTPS_PROXY` 写进 `.env`，那会污染 Hermes 自己的请求。
6. **同一天重复推送要更新而不是新建**：脚本按标题/日期先 query 再决定 create 还是 update，
   否则重跑一次就多一行。
