#!/usr/bin/env python3
"""Part 8: a tiny Data Pipeline: collect -> clean/normalize -> select/label."""
import csv, json, re

RAW = [
    {"msg": "Visiting TORONTO office on 03/14/2026", "city": "Toronto", "date": "2026-03-14"},
    {"msg": "order a100 charged $240", "order_id": "A100", "amount": "240"},
    {"msg": "  see you in toronto  ", "city": "Toronto", "date": ""},
]

def normalize(rec):
    out = dict(rec)
    if out.get("city"): out["city"] = out["city"].strip().title()
    if out.get("date"):
        m = re.match(r"(\d{2})/(\d{2})/(\d{4})", out["date"])
        if m: out["date"] = f"{m.group(3)}-{m.group(1)}-{m.group(2)}"
    if out.get("order_id"): out["order_id"] = out["order_id"].upper()
    return out

def main():
    with open("raw.csv", "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=sorted({k for r in RAW for k in r})); w.writeheader(); w.writerows(RAW)
    labeled = [normalize(r) for r in RAW if r.get("city") or r.get("order_id")]
    with open("labeled.csv", "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=sorted({k for r in labeled for k in r})); w.writeheader(); w.writerows(labeled)
    print(f"raw.csv ({len(RAW)} rows) -> labeled.csv ({len(labeled)} rows)")

if __name__ == "__main__":
    main()
