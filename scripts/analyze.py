# scripts/analyze.py
import json, re, subprocess, pathlib, datetime, collections

ROOT = pathlib.Path(".")
SRC_EXT = (".java", ".kt", ".py", ".cpp")
# 예) B_S3_17484_Title.java / S2_1234_*.kt / G_5_9999.* 등 폭넓게 인식
FILE_RE = re.compile(r"(?i)(?P<tier>[BSGPD])[_-]?(?P<sub>S?\d)?[_-]?(?P<id>\d{3,6})")

def iter_solutions():
    for f in ROOT.rglob("*"):
        if f.is_file() and f.suffix in SRC_EXT:
            m = FILE_RE.search(f.name)
            yield f, (m.groupdict() if m else None)

def git_dates(path):
    out = subprocess.check_output(
        ["git","log","--follow","--date=short","--pretty=%ad","--", str(path)],
        text=True
    ).strip().splitlines()
    return [datetime.date.fromisoformat(d) for d in out if d]

def main():
    items = []
    for f, meta in iter_solutions():
        dates = git_dates(f)
        when = min(dates) if dates else None
        tier = None
        sub = None
        pid = None
        if meta:
            tier = meta.get("tier")
            sub = meta.get("sub")
            pid = meta.get("id")
        items.append({
            "path": str(f),
            "date": when.isoformat() if when else None,
            "tier": tier,
            "sub": sub,
            "id": int(pid) if pid else None,
            "lang": f.suffix.lstrip(".")
        })

    by_day = collections.Counter()
    for it in items:
        if it["date"]:
            by_day[it["date"]] += 1

    timeline = sorted((datetime.date.fromisoformat(d), c) for d,c in by_day.items())
    cum = 0
    cum_series = []
    for d,c in sorted(timeline):
        cum += c
        cum_series.append({"date": d.isoformat(), "count": cum})

    # 누락된 날짜 0 보정 (스파크라인 안정화)
    daily_series = []
    if cum_series:
        start = datetime.date.fromisoformat(cum_series[0]["date"])
        end = datetime.date.today()
        cur = start
        while cur <= end:
            daily_series.append({"date": cur.isoformat(), "count": by_day[cur.isoformat()]})
            cur += datetime.timedelta(days=1)

    tier_map = {"B":"Bronze","S":"Silver","G":"Gold","P":"Platinum","D":"Diamond", None:"Unknown"}
    tier_counts = collections.Counter(tier_map[it["tier"]] for it in items)
    lang_counts = collections.Counter(it["lang"] for it in items)

    spark = [s["count"] for s in cum_series[-60:]] or [0]

    data = {
        "total": len(items),
        "since": cum_series[0]["date"] if cum_series else None,
        "cum_series": cum_series,
        "daily_series": daily_series,
        "tiers": tier_counts,
        "langs": lang_counts,
        "spark": spark,
    }
    pathlib.Path("metrics.json").write_text(json.dumps(data, ensure_ascii=False, indent=2))

    tpl_path = pathlib.Path("README.template.md")
    if not tpl_path.exists():
        print("README.template.md not found"); return
    tpl = tpl_path.read_text()

    spark_url = f"https://quickchart.io/chart/render/sparkline?data1={','.join(map(str,data['spark']))}"
    donut_tier = "https://quickchart.io/chart?c=" + json.dumps({
        "type":"doughnut",
        "data":{"labels":list(data["tiers"].keys()), "datasets":[{"data": list(data["tiers"].values())}]},
        "options":{"plugins":{"legend":{"display":False}},"cutout":"70%"}
    })

    tpl = tpl.replace("{{TOTAL_SOLVED}}", str(data["total"]))
    tpl = tpl.replace("{{SPARK_URL}}", spark_url)
    tpl = tpl.replace("{{TIER_DONUT_URL}}", donut_tier)
    pathlib.Path("README.md").write_text(tpl)

if __name__ == "__main__":
    main()
