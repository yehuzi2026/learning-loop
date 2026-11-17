# -*- coding: utf-8 -*-
"""学习闭环·六能力加速器 —— 学习档案落盘工具。

纯标准库。档案只追加，不覆盖已有主题；日期用 date 加减，不手算时间戳。
"""
import argparse
import json
import os
import sys
from datetime import date, timedelta

if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DEFAULT_STATE = os.path.join(BASE_DIR, "state", "learning.json")
REVIEW_OFFSETS = [1, 3, 7, 14]
VALID_SOURCES = {"1", "2", "3", "4", "5", "6", "①", "②", "③", "④", "⑤", "⑥"}
VALID_STATUS = {"open", "passed", "archived"}


def today():
    return date.today().isoformat()


def plus(days):
    return (date.today() + timedelta(days=days)).isoformat()


def norm_source(value):
    mapping = {"1": "①", "2": "②", "3": "③", "4": "④", "5": "⑤", "6": "⑥"}
    return mapping.get(value, value)


def load(path):
    if not os.path.exists(path):
        return {"version": 1, "created": today(), "topics": {}}
    with open(path, "r", encoding="utf-8") as fh:
        return json.load(fh)


def save(path, data):
    parent = os.path.dirname(path)
    if parent:
        os.makedirs(parent, exist_ok=True)
    with open(path, "w", encoding="utf-8") as fh:
        json.dump(data, fh, ensure_ascii=False, indent=2)


def ensure_topic(data, name, create=False, goal=""):
    topics = data.setdefault("topics", {})
    if name in topics:
        return topics[name], False
    if not create:
        return None, False
    topics[name] = {
        "created": today(),
        "goal": goal,
        "gaps": [],
        "rounds": [],
        "events": [],
    }
    return topics[name], True


def log_event(topic, action, detail):
    topic.setdefault("events", []).append({"at": today(), "action": action, "detail": detail})


def next_gap_id(topic):
    return max([g.get("id", 0) for g in topic.get("gaps", [])], default=0) + 1


def find_gap(topic, gap_id):
    for gap in topic.get("gaps", []):
        if gap.get("id") == gap_id:
            return gap
    return None


def cmd_init(args, data, path):
    topic, created = ensure_topic(data, args.topic, create=True, goal=args.goal or "")
    if created:
        log_event(topic, "init", "建立学习档案")
        save(path, data)
        print("✅ 已建档：%s" % args.topic)
        if args.goal:
            print("   目标：%s" % args.goal)
        print("   下一步：Step 1 加速进场，给最小完整任务，不铺大纲")
    else:
        print("🟡 已有档案，续作（不覆盖）：%s" % args.topic)
        gaps = topic.get("gaps", [])
        opened = [g for g in gaps if g.get("status") == "open"]
        print("   未通过卡点：%d 个" % len(opened))
        for g in opened[:5]:
            print("     #%s %s（来源 %s）" % (g["id"], g["text"], g.get("source", "-")))
        print("   下一步：先跑 due 查到期复习，再跑 next 重排本轮")
    return 0


def cmd_add(args, data, path):
    topic, _ = ensure_topic(data, args.topic)
    if topic is None:
        print("🔴 主题不存在：%s；先执行 init" % args.topic)
        return 1
    source = norm_source(args.source or "②")
    if source not in VALID_SOURCES:
        print("🔴 来源不合法：%s；应为 ①~⑥" % args.source)
        return 1
    gap = {
        "id": next_gap_id(topic),
        "text": args.text,
        "source": source,
        "note": args.note or "",
        "status": "open",
        "created": today(),
        "base_date": None,
        "review_stage": 0,
        "review_due": None,
        "fails": 0,
    }
    topic.setdefault("gaps", []).append(gap)
    log_event(topic, "add", "记录卡点 #%s：%s" % (gap["id"], args.text))
    save(path, data)
    print("✅ 卡点 #%s 已落盘：%s" % (gap["id"], args.text))
    print("   来源：%s ｜ 状态：open ｜ 下一步：回 Step 2 或进入 Step 3 费曼验证" % source)
    return 0


def cmd_pass(args, data, path):
    topic, _ = ensure_topic(data, args.topic)
    if topic is None:
        print("🔴 主题不存在：%s" % args.topic)
        return 1
    gap = find_gap(topic, args.gap)
    if gap is None:
        print("🔴 找不到卡点 #%s" % args.gap)
        return 1
    gap["status"] = "passed"
    gap["base_date"] = today()
    gap["review_stage"] = 0
    gap["review_due"] = plus(REVIEW_OFFSETS[0])
    log_event(topic, "pass", "卡点 #%s 判定通过，进入留存排程" % args.gap)
    save(path, data)
    print("✅ 卡点 #%s 标记通过：%s" % (args.gap, gap["text"]))
    print("⚠️ 脚本不替用户判懂没懂。落盘前须逐条核对通过线：")
    print("   T1 不查资料　T2 不用术语（或术语能翻成大白话且外行能懂）")
    print("   T3 换没练过的场景仍能讲通　T4 过一道变式题")
    print("   四条任缺一条 → 不要执行 pass，卡点应留在 open")
    print("   留存排程：1 / 3 / 7 / 14 天复查，首次到期 %s" % gap["review_due"])
    return 0


def iter_gaps(data, topic_name=None):
    for name, topic in data.get("topics", {}).items():
        if topic_name and name != topic_name:
            continue
        for gap in topic.get("gaps", []):
            yield name, topic, gap


def cmd_due(args, data, path):
    now = today()
    items = []
    for name, topic, gap in iter_gaps(data, args.topic):
        due = gap.get("review_due")
        if gap.get("status") == "passed" and due and due <= now:
            items.append((name, gap, due))
    if not items:
        print("✅ 今日无到期复习项")
        return 0
    print("🟡 到期复习 %d 项（复查失败要退回 open 重新排程）：" % len(items))
    for name, gap, due in items:
        print("   [%s] #%s %s ｜ 应复习日 %s ｜ 第 %s/%s 档" % (
            name, gap["id"], gap["text"], due,
            gap.get("review_stage", 0) + 1, len(REVIEW_OFFSETS)))
    print("   复查命令：review --topic \"<主题>\" --gap <编号> --result ok|fail")
    return 0


def cmd_review(args, data, path):
    topic, _ = ensure_topic(data, args.topic)
    if topic is None:
        print("🔴 主题不存在：%s" % args.topic)
        return 1
    gap = find_gap(topic, args.gap)
    if gap is None:
        print("🔴 找不到卡点 #%s" % args.gap)
        return 1
    if gap.get("status") != "passed":
        print("🔴 卡点 #%s 当前状态为 %s，只有 passed 能复查" % (args.gap, gap.get("status")))
        return 1
    if args.result == "fail":
        gap["fails"] = gap.get("fails", 0) + 1
        gap["status"] = "open"
        gap["review_stage"] = 0
        gap["review_due"] = None
        log_event(topic, "review_fail", "卡点 #%s 留存复查失败，退回 open" % args.gap)
        save(path, data)
        print("🔴 复查未过：#%s 退回 open（累计失败 %s 次）" % (args.gap, gap["fails"]))
        print("   下一步：回 Step 2 重新暴露卡点，优先级按失败次数上浮")
        return 0
    stage = gap.get("review_stage", 0) + 1
    gap["review_stage"] = stage
    if stage >= len(REVIEW_OFFSETS):
        gap["status"] = "archived"
        gap["review_due"] = None
        log_event(topic, "review_ok", "卡点 #%s 四档留存全过，归档" % args.gap)
        save(path, data)
        print("✅ 卡点 #%s 四档留存全过，已归档（不删除记录）" % args.gap)
    else:
        gap["review_due"] = plus(REVIEW_OFFSETS[stage])
        log_event(topic, "review_ok", "卡点 #%s 通过第 %s 档" % (args.gap, stage))
        save(path, data)
        print("✅ 通过第 %s/%s 档，下次复查 %s" % (stage, len(REVIEW_OFFSETS), gap["review_due"]))
    return 0


def cmd_next(args, data, path):
    topic, _ = ensure_topic(data, args.topic)
    if topic is None:
        print("🔴 主题不存在：%s" % args.topic)
        return 1
    opened = [g for g in topic.get("gaps", []) if g.get("status") == "open"]
    opened.sort(key=lambda g: (-g.get("fails", 0), g.get("id", 0)))
    round_no = len(topic.get("rounds", [])) + 1
    if opened:
        focus = opened[0]
        plan = "攻克卡点 #%s：%s（失败 %s 次，优先上浮）" % (
            focus["id"], focus["text"], focus.get("fails", 0))
        entry = "③ 若用户仍说不懂 / ⑤ 若用户以为已懂（单通道，不同时开火）"
    else:
        plan = "无未通过卡点：换未练过的场景做迁移验证，或开新主题"
        entry = "① 给新的最小完整任务"
    topic.setdefault("rounds", []).append({
        "n": round_no, "at": today(), "plan": plan, "entry": entry,
    })
    log_event(topic, "next", "第 %s 轮重排：%s" % (round_no, plan))
    save(path, data)
    print("✅ 第 %s 轮路径已重排" % round_no)
    print("   本轮任务：%s" % plan)
    print("   建议入口：%s" % entry)
    print("   剩余未通过卡点：%d 个；到期复习请先跑 due" % len(opened))
    if len(topic.get("rounds", [])) >= 2:
        prev = topic["rounds"][-2].get("plan", "")
        if prev == plan:
            print("⚠️ 本轮任务与上一轮相同 —— 回流没生效，检查卡点是否真的落盘了")
    return 0


def cmd_show(args, data, path):
    names = [args.topic] if args.topic else sorted(data.get("topics", {}).keys())
    if not names:
        print("⚪ 暂无学习档案，先用 init 建档")
        return 0
    print("学习档案全景（%s）" % today())
    print("=" * 56)
    for name in names:
        topic = data.get("topics", {}).get(name)
        if topic is None:
            print("🔴 主题不存在：%s" % name)
            continue
        gaps = topic.get("gaps", [])
        cnt = {s: len([g for g in gaps if g.get("status") == s]) for s in VALID_STATUS}
        print("主题：%s ｜ 建档 %s ｜ 目标 %s" % (name, topic.get("created", "-"), topic.get("goal") or "未设"))
        print("  卡点：共 %d ｜ open %d ｜ passed %d ｜ archived %d ｜ 轮次 %d" % (
            len(gaps), cnt["open"], cnt["passed"], cnt["archived"], len(topic.get("rounds", []))))
        dues = [g for g in gaps if g.get("status") == "passed" and g.get("review_due")]
        if dues:
            soonest = min(g["review_due"] for g in dues)
            print("  下次到期复习：%s（共 %d 项在排程中）" % (soonest, len(dues)))
        total_fails = sum(g.get("fails", 0) for g in gaps)
        if total_fails:
            print("  留存失败累计：%d 次" % total_fails)
        for g in [x for x in gaps if x.get("status") == "open"][:5]:
            print("    open #%s [%s] %s" % (g["id"], g.get("source", "-"), g["text"]))
        print("-" * 56)
    return 0


def cmd_check(args, data, path):
    issues = []
    if data.get("version") != 1:
        issues.append("version 应为 1")
    seen = set()
    for name, topic in data.get("topics", {}).items():
        ids = set()
        for gap in topic.get("gaps", []):
            gid = gap.get("id")
            if gid in ids:
                issues.append("[%s] 卡点编号重复：%s" % (name, gid))
            ids.add(gid)
            if gap.get("status") not in VALID_STATUS:
                issues.append("[%s] #%s 状态非法：%s" % (name, gid, gap.get("status")))
            if gap.get("source") not in VALID_SOURCES:
                issues.append("[%s] #%s 来源非法：%s" % (name, gid, gap.get("source")))
            if gap.get("status") == "passed" and not gap.get("review_due"):
                issues.append("[%s] #%s 已通过但无复习排程" % (name, gid))
            if gap.get("review_stage", 0) > len(REVIEW_OFFSETS):
                issues.append("[%s] #%s 复习档位越界" % (name, gid))
        seen.add(name)
    if issues:
        print("🔴 档案自检未通过，共 %d 项：" % len(issues))
        for item in issues:
            print("   - %s" % item)
        return 1
    print("✅ 档案自检通过：%d 个主题，%d 条卡点，结构/编号/状态/日期均合法" % (
        len(seen), sum(len(t.get("gaps", [])) for t in data.get("topics", {}).values())))
    return 0


def build_parser():
    parser = argparse.ArgumentParser(description="学习闭环档案工具")
    parser.add_argument("--state", default=DEFAULT_STATE, help="档案路径")
    sub = parser.add_subparsers(dest="command")

    p = sub.add_parser("init", help="建档或续作")
    p.add_argument("--topic", required=True)
    p.add_argument("--goal", default="")

    p = sub.add_parser("add", help="记录卡点")
    p.add_argument("--topic", required=True)
    p.add_argument("--text", required=True)
    p.add_argument("--source", default="②")
    p.add_argument("--note", default="")

    p = sub.add_parser("pass", help="判定通过并进入留存排程")
    p.add_argument("--topic", required=True)
    p.add_argument("--gap", type=int, required=True)

    p = sub.add_parser("due", help="列出到期复习")
    p.add_argument("--topic", default=None)

    p = sub.add_parser("review", help="留存复查")
    p.add_argument("--topic", required=True)
    p.add_argument("--gap", type=int, required=True)
    p.add_argument("--result", choices=["ok", "fail"], required=True)

    p = sub.add_parser("next", help="卡点回流，重排下一轮")
    p.add_argument("--topic", required=True)

    p = sub.add_parser("show", help="全景")
    p.add_argument("--topic", default=None)

    p = sub.add_parser("check", help="档案自检")
    return parser


def main():
    parser = build_parser()
    args = parser.parse_args()
    if not args.command:
        parser.print_help()
        return 0
    data = load(args.state)
    handlers = {
        "init": cmd_init, "add": cmd_add, "pass": cmd_pass, "due": cmd_due,
        "review": cmd_review, "next": cmd_next, "show": cmd_show, "check": cmd_check,
    }
    return handlers[args.command](args, data, args.state)


if __name__ == "__main__":
    sys.exit(main())
