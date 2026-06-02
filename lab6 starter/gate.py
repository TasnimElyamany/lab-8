#!/usr/bin/env python3
"""Part 9: CD4ML quality gate. Exits non-zero if the chosen model's avg score < THRESHOLD."""
import csv, sys, os
from collections import defaultdict

THRESHOLD = float(os.environ.get("QUALITY_THRESHOLD", "0.8"))
CHOSEN = os.environ.get("CHOSEN_MODEL", "qwen2.5:3b")

def main():
    if not os.path.exists("scorecard.csv"):
        print("no scorecard.csv (run score.py first)"); sys.exit(2)
    scores = [float(r["score"]) for r in csv.DictReader(open("scorecard.csv")) if r["model"] == CHOSEN]
    if not scores:
        print(f"no rows for {CHOSEN}"); sys.exit(2)
    avg = sum(scores) / len(scores)
    print(f"chosen={CHOSEN} avg={avg:.3f} threshold={THRESHOLD}")
    if avg < THRESHOLD:
        print("QUALITY GATE FAILED"); sys.exit(1)
    print("QUALITY GATE PASSED")

if __name__ == "__main__":
    main()
