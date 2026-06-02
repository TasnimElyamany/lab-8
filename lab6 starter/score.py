#!/usr/bin/env python3
"""Part 5: score results.csv against the checks in tasks.json -> scorecard.csv + matrix."""
import json, csv, re
from collections import defaultdict

def extract_json(text):
    m = re.search(r"\{.*\}", text, re.DOTALL)
    if not m: return None
    try: return json.loads(m.group(0))
    except Exception: return None

def score_row(check, expected, text):
    if check == "json_match":
        obj = extract_json(text)
        if not obj: return 0.0
        ok = all(str(obj.get(k)).strip().lower() == str(v).strip().lower() for k, v in expected.items())
        return 1.0 if ok else 0.5  # parsed but wrong values = partial
    if check == "max_words":
        return 1.0 if len(text.split()) <= expected else 0.0
    if check == "contains":
        return 1.0 if str(expected) in text else 0.0
    if check == "three_bullets":
        lines = [l for l in text.strip().splitlines() if l.strip()]
        return 1.0 if len(lines) == expected and all(l.strip().startswith("-") for l in lines) else 0.0
    if check == "unit_test":
        ns = {}
        try:
            exec(text, ns); exec(expected, ns); return 1.0
        except Exception:
            return 0.0
    return 0.0

def main():
    tasks = {t["id"]: t for t in json.load(open("tasks.json"))}
    rows = list(csv.DictReader(open("results.csv")))
    out, by_model_cat = [], defaultdict(list)
    for r in rows:
        t = tasks[r["task_id"]]
        s = score_row(t["check"], t["expected"], r["text"])
        out.append({**r, "score": s})
        by_model_cat[(r["model"], r["category"])].append(s)
    with open("scorecard.csv", "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=out[0].keys()); w.writeheader(); w.writerows(out)
    models = sorted({r["model"] for r in rows}); cats = sorted({r["category"] for r in rows})
    print("\nAVG SCORE  " + "  ".join(f"{c[:6]:>6}" for c in cats))
    for m in models:
        cells = []
        for c in cats:
            v = by_model_cat.get((m, c), [])
            cells.append(f"{sum(v)/len(v):.2f}" if v else "  -  ")
        print(f"{m:<16} " + "  ".join(f"{x:>6}" for x in cells))
    print("\nwrote scorecard.csv")

if __name__ == "__main__":
    main()
