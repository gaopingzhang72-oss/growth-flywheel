# -*- coding: utf-8 -*-
"""
notion_push.py —— 把复盘内容同步写进 Notion 数据库（和 record.py 的 Excel 台账并存）

用法：
  python notion_push.py daily  --json 条目.json
  python notion_push.py weekly --json 条目.json
  python notion_push.py repo   --name "owner/name" --why "为什么适合" --step "上手第一步" [--date 2026-09-13] [--status 待看]

需要的环境变量（写在 Hermes 的 .env 里，或临时 export）：
  NOTION_API_KEY     Notion 集成密钥（必填）
  NOTION_DAILY_DS    「每日复盘」数据源 id
  NOTION_WEEKLY_DS   「每周复盘」数据源 id
  NOTION_REPO_DS     「GitHub 项目收藏」数据源 id
  NOTION_PROXY       可选，例如 http://127.0.0.1:7897（本机代理）
  REVIEW_ENV_FILE    可选，.env 的位置（默认 %LOCALAPPDATA%\\hermes\\.env 或 ~/.hermes/.env）

设计原则：同一天/同一周重复推送时**更新那一行**，不会写重复；任何失败都只打印一行提示，
不影响 Excel 那条主线。
"""
import argparse
import datetime as dt
import json
import os
import sys
import urllib.error
import urllib.parse
import urllib.request

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

API = "https://api.notion.com/v1"
VERSION = "2025-09-03"
WEEKDAYS = ["一", "二", "三", "四", "五", "六", "日"]
NEEDS = {"daily": "NOTION_DAILY_DS", "weekly": "NOTION_WEEKLY_DS", "repo": "NOTION_REPO_DS"}


def load_env_file():
    """把 .env 里的键值读进 os.environ（已存在的环境变量优先）。"""
    path = os.environ.get("REVIEW_ENV_FILE")
    if not path:
        cand = [os.path.join(os.environ.get("LOCALAPPDATA", ""), "hermes", ".env"),
                os.path.join(os.path.expanduser("~"), ".hermes", ".env")]
        path = next((p for p in cand if os.path.exists(p)), "")
    if not path or not os.path.exists(path):
        return
    with open(path, encoding="utf-8", errors="replace") as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            k, v = line.split("=", 1)
            k, v = k.strip(), v.strip().strip('"').strip("'")
            # 注意：Hermes 会把技能声明的环境变量预先建成空字符串，
            # 所以「空值」要当成没设置，否则 .env 里的真值永远读不进来
            if k and not os.environ.get(k):
                os.environ[k] = v


def opener():
    proxy = os.environ.get("NOTION_PROXY") or ""
    handlers = []
    if proxy:
        handlers.append(urllib.request.ProxyHandler({"http": proxy, "https": proxy}))
    return urllib.request.build_opener(*handlers)


def call(method, path, body=None, op=None):
    req = urllib.request.Request(
        API + path, method=method,
        data=json.dumps(body, ensure_ascii=False).encode("utf-8") if body is not None else None,
        headers={"Authorization": "Bearer " + os.environ.get("NOTION_API_KEY", ""),
                 "Notion-Version": VERSION, "Content-Type": "application/json"})
    try:
        with (op or opener()).open(req, timeout=45) as r:
            raw = r.read().decode("utf-8")
            return json.loads(raw) if raw else {}
    except urllib.error.HTTPError as e:
        try:
            return {"_error": e.code, "_body": json.loads(e.read().decode("utf-8", "replace"))}
        except Exception:
            return {"_error": e.code, "_body": "?"}
    except Exception as e:
        return {"_error": "net", "_body": str(e)[:200]}


def rt(s, limit=1900):
    s = (s or "").strip()
    return [{"type": "text", "text": {"content": s[:limit]}}] if s else []


def parse_date(s):
    if not s:
        return dt.date.today()
    s = str(s).strip().replace("/", "-").replace(".", "-")
    for f in ("%Y-%m-%d", "%Y-%m-%d %H:%M", "%y-%m-%d"):
        try:
            return dt.datetime.strptime(s, f).date()
        except ValueError:
            pass
    return dt.date.today()


def find_existing(ds, prop, value, op=None):
    r = call("POST", "/data_sources/%s/query" % ds, {
        "filter": {"property": prop, "rich_text" if prop != "日期" else "date":
                   {"equals": value} if prop != "日期" else {"equals": value}},
        "page_size": 1}, op)
    if "_error" in r:
        return None
    res = r.get("results") or []
    return res[0]["id"] if res else None


def write(ds, props, key_prop, key_value, key_kind="title", op=None):
    """同 key 更新，否则新建。返回 (动作, 页面 id, url)"""
    existing = None
    if key_kind == "title":
        r = call("POST", "/data_sources/%s/query" % ds, {
            "filter": {"property": key_prop, "title": {"equals": key_value}},
            "page_size": 1}, op)
        if "_error" not in r and r.get("results"):
            existing = r["results"][0]["id"]
    else:
        existing = find_existing(ds, key_prop, key_value, op)

    if existing:
        out = call("PATCH", "/pages/%s" % existing, {"properties": props}, op)
        return ("updated", existing, out.get("url")) if "_error" not in out else ("fail", None, out)

    body = {"parent": {"type": "data_source_id", "data_source_id": ds}, "properties": props}
    out = call("POST", "/pages", body, op)
    if "_error" in out:
        ds_info = call("GET", "/data_sources/%s" % ds, None, op)
        db_id = ((ds_info.get("parent") or {}).get("database_id")) if "_error" not in ds_info else None
        if db_id:
            out = call("POST", "/pages", {"parent": {"database_id": db_id}, "properties": props}, op)
    if "_error" in out:
        return ("fail", None, out)
    return ("created", out.get("id"), out.get("url"))


def cmd_daily(a):
    item = json.load(open(a.json, encoding="utf-8")) if a.json else {}
    d = parse_date(item.get("date"))
    lines = item.get("lines") or ""
    if isinstance(lines, (list, tuple)):
        lines = "、".join(str(x) for x in lines)
    opts = [{"name": x.strip()} for x in str(lines).replace(",", "、").split("、") if x.strip()]
    props = {
        "复盘": {"title": rt("%s 周%s" % (d.isoformat(), WEEKDAYS[d.weekday()]))},
        "日期": {"date": {"start": d.isoformat()}},
        "学到": {"rich_text": rt(item.get("summary"))},
        "卡住": {"rich_text": rt(item.get("blocker"))},
        "明天第一件事": {"rich_text": rt(item.get("tomorrow"))},
        "运动": {"rich_text": rt(item.get("sport"))},
    }
    if opts:
        props["动的线"] = {"multi_select": opts}
    s = item.get("score")
    if isinstance(s, (int, float)) and s:
        props["自评(1-5)"] = {"number": s}
    return write(a.ds, props, "日期", d.isoformat(), "date")


def cmd_weekly(a):
    item = json.load(open(a.json, encoding="utf-8")) if a.json else {}
    d = parse_date(item.get("date"))
    iso = d.isocalendar()
    week_no = item.get("week") or "第%d周" % iso[1]
    monday = d - dt.timedelta(days=d.weekday())
    rng = item.get("range") or "%s ~ %s" % (monday.isoformat(), (monday + dt.timedelta(days=6)).isoformat())
    props = {
        "周次": {"title": rt(week_no)},
        "区间": {"rich_text": rt(rng)},
        "课内/绩点": {"rich_text": rt(item.get("grade"))},
        "专业+实验室": {"rich_text": rt(item.get("clab"))},
        "英语": {"rich_text": rt(item.get("english"))},
        "运动": {"rich_text": rt(item.get("sport"))},
        "主要问题": {"rich_text": rt(item.get("problem"))},
        "下周三个目标": {"rich_text": rt(item.get("goals"))},
    }
    n = item.get("days")
    if isinstance(n, (int, float)):
        props["打卡天数"] = {"number": n}
    return write(a.ds, props, "周次", week_no, "title")


def cmd_repo(a):
    props = {
        "项目": {"title": rt(a.name)},
        "为什么适合我": {"rich_text": rt(a.why)},
        "上手第一步": {"rich_text": rt(a.step)},
        "状态": {"select": {"name": a.status or "待看"}},
    }
    if a.date:
        props["日期"] = {"date": {"start": parse_date(a.date).isoformat()}}
    return write(a.ds, props, "项目", a.name, "title")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("cmd", choices=["daily", "weekly", "repo", "check"])
    ap.add_argument("--json")
    ap.add_argument("--db", help="数据源 id（不填就用环境变量里对应的那个）")
    ap.add_argument("--name"); ap.add_argument("--why"); ap.add_argument("--step")
    ap.add_argument("--date"); ap.add_argument("--status")
    a = ap.parse_args()

    load_env_file()
    if not os.environ.get("NOTION_API_KEY"):
        print("[notion] 没找到 NOTION_API_KEY，跳过同步（Excel 台账不受影响）")
        return 1
    if a.cmd == "check":
        me = call("GET", "/users/me")
        print("[notion] 身份:", me.get("name") if "_error" not in me else me)
        for k, env in NEEDS.items():
            ds = a.db or os.environ.get(env, "")
            t = call("GET", "/data_sources/%s" % ds) if ds else {"_error": "未配置 %s" % env}
            title = "".join(x.get("plain_text", "") for x in t.get("title", [])) if "_error" not in t else t
            print("  %-7s %s -> %s" % (k, env, title))
        return 0

    env_key = NEEDS[a.cmd]
    ds = a.db or os.environ.get(env_key, "")
    if not ds:
        print("[notion] 缺少 %s，跳过同步" % env_key)
        return 1
    a.ds = ds

    action, pid, info = {"daily": cmd_daily, "weekly": cmd_weekly, "repo": cmd_repo}[a.cmd](a)
    if action == "fail":
        print("[notion] 写入失败，已跳过：", json.dumps(info, ensure_ascii=False)[:300])
        return 1
    print("[notion] %s 成功（%s）：%s" % (a.cmd, action, info))
    return 0


if __name__ == "__main__":
    sys.exit(main())
