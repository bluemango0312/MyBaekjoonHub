# -*- coding: utf-8 -*-
"""
MyBaekjoonHub 분석 스크립트 (루트 README 자동 생성)
- 전 폴더 재귀 탐색
- git 로그 기반 날짜/시간/요일 집계
- 알고리즘 키워드 추정
- 파스텔/라운드/SVG 차트(QuickChart)
- 최근 30일 평균 티어/도전지수, 알고리즘 트렌드 비교
- 루트 README.md 갱신 + scripts/metrics.json 저장
주의: 코드 주석에 이모지 사용 금지
"""
import os, re, json, subprocess, datetime
from collections import Counter
from pathlib import Path
from urllib.parse import quote

BASE = Path(__file__).resolve().parent.parent
TEMPLATE = BASE / "scripts" / "README.template.md"
OUTPUT = BASE / "README.md"
METRICS = BASE / "scripts" / "metrics.json"

ALLOWED_EXT = (".java", ".kt", ".py", ".cpp", ".c", ".cc")
TIER_NAMES = {"Bronze":"B", "Silver":"S", "Gold":"G", "Platinum":"P", "Diamond":"D"}
TIER_SCORE = {"Bronze":1, "Silver":2, "Gold":3, "Platinum":4, "Diamond":5}

ID_PAT = re.compile(r'(?P<id>\d{3,6})')
TITLE_PAT = re.compile(r'^\s*\d{3,6}[.\s_-]*(.*)$')

ALGOS = {
    "BFS": [r"Queue<", r"ArrayDeque<", r"LinkedList<", r"\.offer\(", r"while\s*\(\s*!\s*queue\.isEmpty\("],
    "DFS": [r"void\s+dfs\(", r"\bdfs\(", r"Stack<"],
    "DP": [r"\bdp\s*\[", r"memo", r"cache", r"Arrays\.fill\(", r"long\[\]"],
    "BinarySearch": [r"binarySearch", r"while\s*\(\s*low\s*<=\s*high\)", r"upperBound", r"lowerBound"],
    "TwoPointers": [r"while\s*\(\s*i\s*<\s*j\)", r"\bi\s*\+\+", r"\bj\s*--"],
    "Greedy": [r"PriorityQueue<", r"Collections\.sort\(", r"Arrays\.sort\(", r"comparator"],
    "StackQueue": [r"Stack<", r"Deque<", r"Queue<"],
    "Heap": [r"PriorityQueue<"],
    "Sorting": [r"Arrays\.sort\(", r"Collections\.sort\("],
    "Graph": [r"ArrayList<.*>\[\]", r"\badj", r"edges", r"\bgraph\b"],
    "Tree": [r"TreeSet<", r"TreeMap<", r"segment", r"Fenwick", r"binary\s*tree"],
}

# 파스텔 팔레트
PALETTE = ["#CFE3FF", "#AFCBFF", "#8FB5FF", "#6D9EFF", "#4D86F5", "#2E6DDB"]

def quickchart_svg(cfg: dict, w=360, h=140):
    from urllib.parse import quote
    return (
        "https://quickchart.io/chart"
        f"?c={quote(json.dumps(cfg, ensure_ascii=False))}"
        f"&format=svg&devicePixelRatio=2&backgroundColor=transparent&width={w}&height={h}"
    )

def base_opts():
    return {
        "plugins": {"legend": {"display": False}},
        "layout": {"padding": 6},
        "elements": {"line": {"tension": 0.35, "borderWidth": 3}, "point": {"radius": 0}},
        "scales": {
            "x": {"grid": {"color": "rgba(0,0,0,0.06)"}, "ticks": {"font": {"size": 9}}},
            "y": {"grid": {"color": "rgba(0,0,0,0.06)"}, "beginAtZero": True, "ticks": {"font": {"size": 9}}}
        }
    }

# 영어 알고리즘 키 → 한글 라벨
ALGO_LABELS = {
    "BFS":"BFS", "DFS":"DFS", "DP":"DP", "BinarySearch":"이분탐색",
    "TwoPointers":"투포인터", "Greedy":"그리디", "StackQueue":"스택/큐",
    "Heap":"힙", "Sorting":"정렬", "Graph":"그래프", "Tree":"트리"
}


def build_charts(month_counts, cum_points, algo_counts, hour_counts):
    # 월별 추이
    labels = list(month_counts.keys()); data = list(month_counts.values())
    monthly_line = {
        "type": "line",
        "data": {"labels": labels, "datasets": [{
            "label": "월별 풀이 수", "data": data,
            "borderColor": PALETTE[3], "backgroundColor": PALETTE[3]
        }]},
        "options": base_opts()
    }

    # 누적
    c_labels = [p[0] for p in cum_points]
    c_data = [p[1] for p in cum_points]
    cumulative_line = {
        "type": "line",
        "data": {"labels": c_labels, "datasets": [{
            "label": "누적 풀이 수", "data": c_data,
            "borderColor": PALETTE[5], "backgroundColor": PALETTE[5]
        }]},
        "options": base_opts()
    }

    # ✅ Y축 완전 숨김 (Chart.js v3)
    cum_opt = cumulative_line["options"]
    cum_opt["scales"]["y"]["display"] = False
    cum_opt["scales"]["y"]["ticks"]["display"] = False
    cum_opt["scales"]["y"]["grid"]["display"] = False
    cum_opt["layout"]["padding"] = {"left": 6, "right": 6, "top": 6, "bottom": 2}

    # ✅ 호환용(혹시 v2로 렌더될 때)
    cum_opt["scales"]["yAxes"] = [{
        "display": False,
        "ticks": {"display": False},
        "gridLines": {"display": False}
    }]

    # 알고리즘 상위 분포(가로 막대)
    a_labels_en = list(algo_counts.keys())
    a_labels_ko = [ALGO_LABELS.get(k, k) for k in a_labels_en]
    a_data = list(algo_counts.values())
    algo_bar = {
        "type": "bar",
        "data": {"labels": a_labels_ko, "datasets": [{
            "label": "알고리즘 빈도", "data": a_data,
            "backgroundColor": PALETTE[2], "borderRadius": 10, "borderSkipped": False
        }]},
        "options": {**base_opts(), "indexAxis": "y"}
    }

    # 시간대 분포
    hours = [str(h) for h in range(24)]; h_data = [hour_counts.get(h, 0) for h in range(24)]
    hour_bar = {
        "type": "bar",
        "data": {"labels": hours, "datasets": [{
            "label": "시간대별 활동", "data": h_data,
            "backgroundColor": PALETTE[1], "borderRadius": 8, "borderSkipped": False
        }]},
        "options": base_opts()
    }

    # 각 차트는 카드 절반 폭 기준(작게)
    return {
        "monthly_line": quickchart_svg(monthly_line, w=360, h=140),
        "cumulative_line": quickchart_svg(cumulative_line, w=360, h=140),
        "algo_bar": quickchart_svg(algo_bar, w=360, h=180),
        "hour_bar": quickchart_svg(hour_bar, w=360, h=140),
        # 추가: 작은 버전
        "monthly_line_small": quickchart_svg(monthly_line, w=250, h=130),
        "cumulative_line_small": quickchart_svg(cumulative_line, w=250, h=130),
    }

def build_compare_bar(labels, a_data, b_data, a_label="최근(%)", b_label="전체(%)"):
    labels_ko = [ALGO_LABELS.get(k, k) for k in labels]
    cfg = {
        "type": "bar",
        "data": {
            "labels": labels_ko,
            "datasets": [
                {"label": a_label, "data": a_data, "backgroundColor": PALETTE[4], "borderRadius": 10, "borderSkipped": False},
                {"label": b_label, "data": b_data, "backgroundColor": PALETTE[0], "borderRadius": 10, "borderSkipped": False}
            ]
        },
        "options": {**base_opts(), "plugins": {"legend": {"display": True}}}
    }
    return quickchart_svg(cfg, w=360, h=180)

def build_weekday_bar(weekday_counts):
    labels = ["월","화","수","목","금","토","일"]
    data = [weekday_counts.get(i, 0) for i in range(7)]
    cfg = {
        "type": "bar",
        "data": {"labels": labels, "datasets": [{
            "label": "요일별 활동", "data": data,
            "backgroundColor": PALETTE[2], "borderRadius": 8, "borderSkipped": False
        }]},
        "options": base_opts()
    }
    return quickchart_svg(cfg, w=360, h=140)

def avg(lst): return sum(lst)/len(lst) if lst else 0.0

def git_log_timestamp(path: Path):
    try:
        ts = subprocess.check_output(["git","log","-1","--format=%ct","--",str(path)], text=True, cwd=str(BASE)).strip()
        return int(ts) if ts else None
    except Exception:
        return None

def git_date(path: Path):
    ts = git_log_timestamp(path)
    return datetime.datetime.fromtimestamp(ts) if ts else None

def extract_id_title(name: str):
    base = Path(name).stem
    m_id = ID_PAT.search(base); prob_id = m_id.group("id") if m_id else None
    m_title = TITLE_PAT.match(base); title = m_title.group(1).strip() if m_title else base
    return prob_id, title

def find_tier_from_parts(parts):
    for p in parts:
        key = p.split()[0].strip()
        if key in TIER_NAMES: return TIER_NAMES[key], key
    return None, None

def score_algorithms(text: str):
    hits = Counter()
    for tag, pats in ALGOS.items():
        for pat in pats:
            if re.search(pat, text): hits[tag]+=1; break
    return hits

def walk_solutions():
    items = []
    for root, _, files in os.walk(BASE):
        root_posix = Path(root).as_posix()
        if any(skip in root_posix for skip in ["/.git","/.github","/venv","/.venv","/__pycache__"]): continue
        rel_parts = Path(root).relative_to(BASE).parts
        tier_letter, tier_word = find_tier_from_parts(rel_parts)
        collected = False
        for fn in files:
            if not fn.endswith(ALLOWED_EXT): continue
            prob_id, title = extract_id_title(fn)
            if not prob_id and rel_parts: prob_id, title = extract_id_title(rel_parts[-1])
            if not prob_id: continue
            file_path = Path(root, fn)
            d = git_date(file_path) or datetime.datetime.min
            algo_hits = Counter()
            try:
                text = file_path.read_text(encoding="utf-8", errors="ignore")
                algo_hits = score_algorithms(text)
            except Exception:
                pass
            items.append({
                "path": file_path.relative_to(BASE).as_posix(),
                "file": fn,
                "id": prob_id,
                "title": title,
                "tier_code": tier_letter or "U",
                "tier": tier_word or "Unknown",
                "date": d,
                "ts": int(d.timestamp()) if d != datetime.datetime.min else None,
                "algos": algo_hits,
                "lang": file_path.suffix.lstrip(".").lower()
            })
            collected = True
        if not collected and rel_parts:
            folder_name = rel_parts[-1]
            prob_id, title = extract_id_title(folder_name)
            if not prob_id: continue
            folder = Path(root); readme = folder / "README.md"
            target = readme if readme.exists() else folder
            d = git_date(target) or datetime.datetime.min
            items.append({
                "path": target.relative_to(BASE).as_posix(),
                "file": target.name if target.is_file() else "",
                "id": prob_id,
                "title": title,
                "tier_code": tier_letter or "U",
                "tier": tier_word or "Unknown",
                "date": d,
                "ts": int(d.timestamp()) if d != datetime.datetime.min else None,
                "algos": Counter(),
                "lang": ""
            })
    return items

def month_key(dt): return dt.strftime("%Y-%m") if dt != datetime.datetime.min else None

def make_calendar(dates, days=14):
    today = datetime.date.today(); s = set(dates); cells = []
    for i in range(days):
        day = today - datetime.timedelta(days=days-1-i)
        cells.append("█" if day in s else "░")
    return "".join(cells) + f" (최근 {days}일)"

def render_table(items, n=10):
    rows = ["| No. | Problem | Tier | Link | Date |","|---:|:-------|:-----|:-----|:-----|"]
    for it in items[:n]:
        link = f"[📄]({it['path']})" if it["path"] else "-"
        date_str = it["date"].strftime("%Y-%m-%d") if it["date"] != datetime.datetime.min else "-"
        title = (it.get("title") or "").replace("|","¦")
        rows.append(f"| {it['id']} | {title} | {it['tier']} | {link} | {date_str} |")
    return "\n".join(rows)

def main():
    sols = sorted(walk_solutions(), key=lambda x: x["date"], reverse=True)
    total = len(sols)

    tiers_cnt = Counter([s["tier"] for s in sols])
    order = ["Diamond","Platinum","Gold","Silver","Bronze","Unknown"]
    tier_lines = [f"- {t}: **{tiers_cnt[t]}**" for t in order if tiers_cnt[t]]

    dates = [s["date"].date() for s in sols if s["date"] != datetime.datetime.min]
    cal = make_calendar(dates)

    months = [month_key(s["date"]) for s in sols if month_key(s["date"])]
    month_counts = dict(sorted(Counter(months).items()))

    cum_points = []; cum = 0
    for m, v in month_counts.items():
        cum += v; cum_points.append((m, cum))

    hour_counts = Counter(); weekday_counts = Counter()
    for s in sols:
        if s["ts"]:
            dt = datetime.datetime.fromtimestamp(s["ts"])
            hour_counts[dt.hour] += 1; weekday_counts[dt.weekday()] += 1

    algo_total_all = Counter()
    for s in sols: algo_total_all.update(s["algos"])
    algo_top8 = Counter(dict(algo_total_all.most_common(8)))

    weakness = sorted([(t, algo_total_all.get(t,0)) for t in ["DP","BinarySearch","TwoPointers","Greedy"]],
                      key=lambda x: x[1])[:3]
    weakness_lines = [f"- {w[0]} 비중 낮음" for w in weakness]

    now_dt = datetime.datetime.now()
    recent_sols = [s for s in sols if s["date"] != datetime.datetime.min and s["date"] >= now_dt - datetime.timedelta(days=30)]
    def tier_scores(items): return [TIER_SCORE.get(s["tier"], 0) for s in items]
    avg_all = avg(tier_scores(sols))
    avg_recent = avg(tier_scores(recent_sols))
    challenge_index = round(avg_recent - avg_all, 2); avg_recent_disp = f"{avg_recent:.2f}"

    algo_total_recent = Counter()
    for s in recent_sols: algo_total_recent.update(s["algos"])
    compare_keys = [k for k,_ in (algo_total_all + algo_total_recent).most_common(12)][:8]
    all_sum = sum(algo_total_all.values()) or 1; rc_sum = sum(algo_total_recent.values()) or 1
    all_ratio = [round(100*algo_total_all.get(k,0)/all_sum,1) for k in compare_keys]
    rc_ratio  = [round(100*algo_total_recent.get(k,0)/rc_sum,1) for k in compare_keys]

    charts = build_charts(month_counts, cum_points, algo_top8, hour_counts)
    algo_trend_url = build_compare_bar(compare_keys, rc_ratio, all_ratio)
    weekday_bar_url = build_weekday_bar(weekday_counts)
    recent_table = render_table(sols, 10)

    metrics = {
        "total": total, "tiers": tiers_cnt, "months": month_counts,
        "algo": algo_total_all, "hours": hour_counts, "weekday": weekday_counts,
        "avg_recent_tier": avg_recent, "challenge_index": challenge_index
    }

    unique_days = sorted(set(dates)); streak = 0; d = datetime.date.today()
    while d in unique_days: streak += 1; d = d - datetime.timedelta(days=1)
    metrics["streak"] = streak

    METRICS.write_text(json.dumps(metrics, ensure_ascii=False, indent=2), encoding="utf-8")

    tpl = TEMPLATE.read_text(encoding="utf-8")
    out = (tpl
        .replace("{{TOTAL_SOLVED}}", str(total))
        .replace("{{RECENT_CALENDAR}}", cal)
        .replace("{{TIER_BREAKDOWN}}", "\n".join(tier_lines) if tier_lines else "_no data_")
        .replace("{{RECENT_TABLE}}", recent_table)
        .replace("{{MONTHLY_LINE}}", f"![]({charts['monthly_line']})")
        .replace("{{CUMULATIVE_LINE}}", f"![]({charts['cumulative_line']})")
        .replace("{{MONTHLY_LINE_SMALL_URL}}", charts['monthly_line_small'])
    .replace("{{CUMULATIVE_LINE_SMALL_URL}}", charts['cumulative_line_small'])
        .replace("{{ALGO_BAR}}", f"![]({charts['algo_bar']})")
        .replace("{{HOUR_BAR}}", f"![]({charts['hour_bar']})")
        .replace("{{STREAK}}", str(streak))
        .replace("{{WEAKNESSES}}", "\n".join(weakness_lines) if weakness_lines else "_no data_")
        .replace("{{RECENT_AVG_TIER}}", avg_recent_disp)
        .replace("{{CHALLENGE_INDEX}}", f"{challenge_index:+.2f}")
        .replace("{{ALGO_TREND_BAR}}", f"![]({algo_trend_url})")
        .replace("{{WEEKDAY_BAR}}", f"![]({weekday_bar_url})")
    )
    out += f"\n\n<!-- generated-at: {datetime.datetime.now().isoformat(timespec='seconds')} -->\n"
    OUTPUT.write_text(out, encoding="utf-8")

if __name__ == "__main__":
    main()
