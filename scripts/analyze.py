# -*- coding: utf-8 -*-
"""
MyBaekjoonHub 분석 스크립트 (루트 README 자동 생성)
- 전 폴더 재귀 탐색
- git 로그 기반 날짜/시간/요일 집계 (KST 기준)
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

# 경로 설정
BASE = Path(__file__).resolve().parent.parent
TEMPLATE = BASE / "scripts" / "README.template.md"
OUTPUT = BASE / "README.md"
METRICS = BASE / "scripts" / "metrics.json"

# 타임존: KST 고정
KST = datetime.timezone(datetime.timedelta(hours=9))

# 확장자/티어 매핑
ALLOWED_EXT = (".java", ".kt", ".py", ".cpp", ".c", ".cc")
TIER_NAMES = {"Bronze": "B", "Silver": "S", "Gold": "G", "Platinum": "P", "Diamond": "D"}
TIER_SCORE = {"Bronze": 1, "Silver": 2, "Gold": 3, "Platinum": 4, "Diamond": 5}

# 파일명에서 ID/제목 추출
ID_PAT = re.compile(r'(?P<id>\d{3,6})', re.UNICODE)
TITLE_PAT = re.compile(r'^\s*\d{3,6}\D+(.*)$', re.UNICODE)

# 알고리즘 패턴(완화 버전)
ALGOS = {
    "BFS": [
        r"Queue<", r"ArrayDeque<", r"LinkedList<",
        r"\.(offer|poll|peek)\(",
        r"while\s*\(\s*!\s*[A-Za-z_]\w*\s*\.\s*isEmpty\s*\("
    ],
    "DFS": [r"\bvoid\s+dfs\s*\(", r"\bdfs\s*\(", r"Stack<"],
    "DP": [r"\bdp\s*\[", r"\bmemo\b", r"\bcache\b", r"Arrays\.fill\("],
    "BinarySearch": [r"binarySearch", r"while\s*\(\s*low\s*<=\s*high\s*\)"],
    "TwoPointers": [r"while\s*\(\s*i\s*<\s*j\s*\)", r"\bi\s*\+\+;?", r"\bj\s*--;?"],
    "Greedy": [r"PriorityQueue<", r"(Collections|Arrays)\.sort\(", r"comparator"],
    "StackQueue": [r"Stack<", r"Deque<", r"Queue<"],
    "Heap": [r"PriorityQueue<"],
    "Sorting": [r"(Collections|Arrays)\.sort\("],
    "Graph": [r"ArrayList<.*>\[\]", r"\badj\b", r"\bedges\b", r"\bgraph\b"],
    "Tree": [r"Tree(Set|Map)<", r"\bbinary\s*tree\b", r"\bsegment\b", r"\bFenwick\b"],
}

# 파스텔 팔레트
PALETTE = ["#CFE3FF", "#AFCBFF", "#8FB5FF", "#6D9EFF", "#4D86F5", "#2E6DDB"]

# 한국어 라벨
ALGO_LABELS = {
    "BFS": "BFS", "DFS": "DFS", "DP": "DP", "BinarySearch": "이분탐색",
    "TwoPointers": "투포인터", "Greedy": "그리디", "StackQueue": "스택/큐",
    "Heap": "힙", "Sorting": "정렬", "Graph": "그래프", "Tree": "트리"
}

def _normalize(s: str) -> str:
    """전각 기호/제로폭 공백 제거 및 기본 정리"""
    if not s:
        return ""
    return (
        s.replace("（", "(").replace("）", ")").replace("．", ".")
         .replace("\u200b", "").replace("\u2009", " ").replace("\u200a", " ")
         .replace("\u2002", " ").replace("\u2003", " ").replace("\u2060", "").replace("\ufeff", "")
         .strip()
    )

def quickchart_svg(cfg: dict, w=360, h=140):
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

def build_charts(month_counts, cum_points, algo_counts, hour_counts):
    # 1) 월별 추이
    labels = list(month_counts.keys()); data = list(month_counts.values())
    monthly_line = {
        "type": "line",
        "data": {"labels": labels, "datasets": [{
            "label": "월별 풀이 수", "data": data,
            "borderColor": PALETTE[3], "backgroundColor": PALETTE[3]
        }]},
        "options": base_opts()
    }

    # 2) 누적
    c_labels = [p[0] for p in cum_points]; c_data = [p[1] for p in cum_points]
    cumulative_line = {
        "type": "line",
        "data": {"labels": c_labels, "datasets": [{
            "label": "누적 풀이 수", "data": c_data,
            "borderColor": PALETTE[5], "backgroundColor": PALETTE[5]
        }]},
        "options": base_opts()
    }
    cum_opt = cumulative_line["options"]
    cum_opt["scales"]["y"]["display"] = False
    cum_opt["scales"]["y"]["ticks"]["display"] = False
    cum_opt["scales"]["y"]["grid"]["display"] = False
    cum_opt["layout"]["padding"] = {"left": 6, "right": 6, "top": 6, "bottom": 2}
    # 호환용(v2)
    cum_opt["scales"]["yAxes"] = [{
        "display": False,
        "ticks": {"display": False},
        "gridLines": {"display": False}
    }]

    # 3) 알고리즘 상위 분포(가로 막대)
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

    # 4) 시간대 분포
    hours = [str(h) for h in range(24)]; h_data = [hour_counts.get(h, 0) for h in range(24)]
    hour_bar = {
        "type": "bar",
        "data": {"labels": hours, "datasets": [{
            "label": "시간대별 활동", "data": h_data,
            "backgroundColor": PALETTE[1], "borderRadius": 8, "borderSkipped": False
        }]},
        "options": base_opts()
    }

    return {
        "monthly_line": quickchart_svg(monthly_line, w=360, h=140),
        "cumulative_line": quickchart_svg(cumulative_line, w=360, h=140),
        "algo_bar": quickchart_svg(algo_bar, w=360, h=180),
        "hour_bar": quickchart_svg(hour_bar, w=360, h=140),
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
    labels = ["월", "화", "수", "목", "금", "토", "일"]
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

def avg(lst): 
    return sum(lst) / len(lst) if lst else 0.0

def git_log_timestamp(path: Path):
    try:
        ts = subprocess.check_output(
            ["git", "log", "-1", "--format=%ct", "--", str(path)],
            text=True, cwd=str(BASE)
        ).strip()
        return int(ts) if ts else None
    except Exception:
        return None

def to_kst(ts: int) -> datetime.datetime:
    # git log epoch(sec) -> UTC -> KST
    return datetime.datetime.fromtimestamp(ts, tz=datetime.timezone.utc).astimezone(KST)

def git_date(path: Path):
    ts = git_log_timestamp(path)
    return to_kst(ts) if ts else None

def extract_id_title(name: str):
    """파일명 또는 폴더명에서 문제 ID와 제목 추출"""
    base = _normalize(Path(name).stem)

    m_id = ID_PAT.search(base)
    prob_id = m_id.group("id") if m_id else None

    m_title = TITLE_PAT.match(base)
    title = _normalize(m_title.group(1)) if m_title else None

    if not title:
        stripped = _normalize(re.sub(r'^\s*\d{3,6}\D+', '', base))
        title = stripped or base

    return prob_id, title

def find_tier_from_parts(parts):
    for p in parts:
        key = p.split()[0].strip()
        if key in TIER_NAMES:
            return TIER_NAMES[key], key
    return None, None

def score_algorithms(text: str):
    hits = Counter()
    for tag, pats in ALGOS.items():
        for pat in pats:
            if re.search(pat, text):
                hits[tag] += 1
                break
    return hits

def walk_solutions():
    items = []
    for root, _, files in os.walk(BASE):
        root_posix = Path(root).as_posix()
        if any(skip in root_posix for skip in ["/.git", "/.github", "/venv", "/.venv", "/__pycache__"]):
            continue

        rel_parts = Path(root).relative_to(BASE).parts
        tier_letter, tier_word = find_tier_from_parts(rel_parts)

        collected = False
        for fn in files:
            if not fn.endswith(ALLOWED_EXT):
                continue

            prob_id, title = extract_id_title(fn)

            if (not prob_id or not title) and rel_parts:
                pid2, title2 = extract_id_title(rel_parts[-1])
                prob_id = prob_id or pid2
                if not title:
                    title = _normalize(Path(rel_parts[-1]).stem)

            if not prob_id:
                continue

            file_path = Path(root, fn)
            d = git_date(file_path) or datetime.datetime.min.replace(tzinfo=KST)

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
                "ts": int(d.timestamp()) if d != datetime.datetime.min.replace(tzinfo=KST) else None,
                "algos": algo_hits,
                "lang": file_path.suffix.lstrip(".").lower()
            })
            collected = True

        # 폴더만 있고 파일이 없을 때 폴더 기준으로 한 줄 남기기
        if not collected and rel_parts:
            folder_name = rel_parts[-1]
            prob_id, title = extract_id_title(folder_name)
            if not prob_id:
                continue
            folder = Path(root)
            readme = folder / "README.md"
            target = readme if readme.exists() else folder
            d = git_date(target) or datetime.datetime.min.replace(tzinfo=KST)
            items.append({
                "path": target.relative_to(BASE).as_posix(),
                "file": target.name if target.is_file() else "",
                "id": prob_id,
                "title": title or _normalize(Path(folder_name).stem),
                "tier_code": tier_letter or "U",
                "tier": tier_word or "Unknown",
                "date": d,
                "ts": int(d.timestamp()) if d != datetime.datetime.min.replace(tzinfo=KST) else None,
                "algos": Counter(),
                "lang": ""
            })
    return items

def month_key(dt): 
    return dt.strftime("%Y-%m") if dt != datetime.datetime.min.replace(tzinfo=KST) else None

def make_calendar(dates, days=14):
    today = datetime.datetime.now(KST).date()
    s = set(dates)
    cells = []
    for i in range(days):
        day = today - datetime.timedelta(days=days - 1 - i)
        cells.append("█" if day in s else "░")
    return "".join(cells) + f" (최근 {days}일)"

def render_table(items, n=10):
    rows = ["| No. | Problem | Tier | Link | Date |", "|---:|:-------|:-----|:-----|:-----|"]
    for it in items[:n]:
        link = f"[📄]({it['path']})" if it["path"] else "-"
        date_str = it["date"].strftime("%Y-%m-%d") if it["date"] != datetime.datetime.min.replace(tzinfo=KST) else "-"
        title = (it.get("title") or "").replace("|", "¦").strip()
        if not title:
            title = f"BOJ {it['id']}"
        rows.append(f"| {it['id']} | {title} | {it['tier']} | {link} | {date_str} |")
    return "\n".join(rows)

def main():
    # 풀이 수집 및 정렬
    sols = sorted(walk_solutions(), key=lambda x: x["date"], reverse=True)
    total = len(sols)

    # 티어 분포
    tiers_cnt = Counter([s["tier"] for s in sols])
    order = ["Diamond", "Platinum", "Gold", "Silver", "Bronze", "Unknown"]
    tier_lines = [f"- {t}: **{tiers_cnt[t]}**" for t in order if tiers_cnt[t]]

    # 날짜/달/시/요일 집계 (KST)
    dates = [s["date"].date() for s in sols if s["date"] != datetime.datetime.min.replace(tzinfo=KST)]
    cal = make_calendar(dates)

    months = [month_key(s["date"]) for s in sols if month_key(s["date"])]
    month_counts = dict(sorted(Counter(months).items()))

    cum_points = []
    cum = 0
    for m, v in month_counts.items():
        cum += v
        cum_points.append((m, cum))

    hour_counts = Counter()
    weekday_counts = Counter()
    for s in sols:
        if s["ts"]:
            dt = datetime.datetime.fromtimestamp(s["ts"], tz=KST)
            hour_counts[dt.hour] += 1
            weekday_counts[dt.weekday()] += 1

    # 알고리즘 카운트
    algo_total_all = Counter()
    for s in sols:
        algo_total_all.update(s["algos"])
    algo_top8 = Counter(dict(algo_total_all.most_common(8)))

    # 보완 추천 계산(값이 전부 0인 경우 메시지)
    present = {k: v for k, v in algo_total_all.items() if v > 0}
    if present:
        target = ["BFS", "DFS", "DP", "BinarySearch", "TwoPointers", "Greedy", "Heap", "Sorting", "Graph", "Tree", "StackQueue"]
        ranked = sorted([(k, present.get(k, 0)) for k in target], key=lambda x: x[1])
        weakness_lines = [f"- {ALGO_LABELS.get(k, k)} 비중 낮음" for k, _ in ranked[:3]]
    else:
        weakness_lines = ["- 코드에서 알고리즘 단서를 찾지 못함(패턴 개선 또는 주석/코드 키워드 확인 필요)"]

    # 평균 티어/도전 지수 (최근 30일, KST 기준)
    now_dt = datetime.datetime.now(KST)
    recent_sols = [s for s in sols if s["date"] != datetime.datetime.min.replace(tzinfo=KST) and s["date"] >= now_dt - datetime.timedelta(days=30)]

    def tier_scores(items):
        return [TIER_SCORE.get(s["tier"], 0) for s in items]

    avg_all = avg(tier_scores(sols))
    avg_recent = avg(tier_scores(recent_sols))
    challenge_index = round(avg_recent - avg_all, 2)
    avg_recent_disp = f"{avg_recent:.2f}"

    # 최근/전체 알고리즘 비율 비교
    algo_total_recent = Counter()
    for s in recent_sols:
        algo_total_recent.update(s["algos"])

    compare_keys = [k for k, _ in (algo_total_all + algo_total_recent).most_common(12)][:8]
    all_sum = sum(algo_total_all.values()) or 1
    rc_sum = sum(algo_total_recent.values()) or 1
    all_ratio = [round(100 * algo_total_all.get(k, 0) / all_sum, 1) for k in compare_keys]
    rc_ratio = [round(100 * algo_total_recent.get(k, 0) / rc_sum, 1) for k in compare_keys]

    # 차트 생성
    charts = build_charts(month_counts, cum_points, algo_top8, hour_counts)
    algo_trend_url = build_compare_bar(compare_keys, rc_ratio, all_ratio)
    weekday_bar_url = build_weekday_bar(weekday_counts)
    recent_table = render_table(sols, 10)

    # streak 계산
    unique_days = sorted(set(dates))
    # 오늘부터 연속
    current_streak = 0
    d = datetime.datetime.now(KST).date()
    while d in unique_days:
        current_streak += 1
        d -= datetime.timedelta(days=1)
    # 최근 끊기지 않은 연속(마지막 활동일 기준)
    recent_streak = 0
    if unique_days:
        d = max(unique_days)
        recent_streak = 1
        while (d - datetime.timedelta(days=1)) in unique_days:
            recent_streak += 1
            d -= datetime.timedelta(days=1)

    # 메트릭 저장
    metrics = {
        "total": total,
        "tiers": tiers_cnt,
        "months": month_counts,
        "algo": algo_total_all,
        "hours": hour_counts,
        "weekday": weekday_counts,
        "avg_recent_tier": avg_recent,
        "challenge_index": challenge_index,
        "streak_today": current_streak,
        "streak_recent": recent_streak,
    }
    METRICS.write_text(json.dumps(metrics, ensure_ascii=False, indent=2), encoding="utf-8")

    # 템플릿 렌더링
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
        # 표시용 streak은 '최근 끊기지 않은 연속일수'로 교체
        .replace("{{STREAK}}", str(recent_streak))
        .replace("{{WEAKNESSES}}", "\n".join(weakness_lines) if weakness_lines else "_no data_")
        .replace("{{RECENT_AVG_TIER}}", avg_recent_disp)
        .replace("{{CHALLENGE_INDEX}}", f"{challenge_index:+.2f}")
        .replace("{{ALGO_TREND_BAR}}", f"![]({algo_trend_url})")
        .replace("{{WEEKDAY_BAR}}", f"![]({weekday_bar_url})")
    )
    out += f"\n\n<!-- generated-at: {datetime.datetime.now(KST).isoformat(timespec='seconds')} -->\n"
    OUTPUT.write_text(out, encoding="utf-8")

if __name__ == "__main__":
    main()
