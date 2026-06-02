#!/usr/bin/env python3
"""Part 4B: PROMPT LAB — hold the MODEL fixed, change the PROMPT, watch behavior change.

Runs ONE model across 7 controlled prompt conditions on the same underlying task and
tabulates how the output changes (JSON? prose? word count? correct? latency?).

Usage:
  python prompt_lab.py                 # live; set MODEL env to a pulled model
  python prompt_lab.py --mock          # offline, deterministic (uses fixtures)
  MODEL=llama3.2:3b python prompt_lab.py
"""
import os, sys, json, time, re

MODEL = os.environ.get("MODEL", "qwen2.5:3b")
MOCK = "--mock" in sys.argv
CHAT = "http://localhost:11434/api/chat"

# The underlying TASK is held constant: extract city + date from a messy message.
USER_MSG = "hey -- i'll swing by the TORONTO office on 03/14/2026, talk soon"
# A second task, used only by the chain-of-thought condition:
REASON_MSG = "A train leaves 14:00, arrives 17:30, stopped 20 min total. Minutes moving? Number only."

# Each condition holds the model fixed and changes exactly ONE prompt lever.
CONDITIONS = [
    {"id": "C1_bare", "lever": "no system prompt",
     "system": None,
     "user": f"Extract the city and date: {USER_MSG}",
     "opts": {"temperature": 0}},

    {"id": "C2_role", "lever": "role system prompt",
     "system": "You are a precise data-extraction API. Reply with JSON only, no prose.",
     "user": f"Extract city and date: {USER_MSG}",
     "opts": {"temperature": 0}},

    {"id": "C3_fewshot", "lever": "few-shot examples",
     "system": "You extract fields as JSON.",
     "user": ("Examples:\n"
              "'meet in Paris on 2025-01-02' -> {\"city\":\"Paris\",\"date\":\"2025-01-02\"}\n"
              "'see you in Berlin 2025-05-09' -> {\"city\":\"Berlin\",\"date\":\"2025-05-09\"}\n"
              f"Now: '{USER_MSG}' ->"),
     "opts": {"temperature": 0}},

    {"id": "C4_format_json", "lever": "forced JSON (format=json)",
     "system": "Extract city and date.",
     "user": USER_MSG,
     "opts": {"temperature": 0}, "format": "json"},

    {"id": "C5_temp_high", "lever": "temperature 1.2 (x3 runs)",
     "system": "Extract the city and date in one sentence.",
     "user": USER_MSG,
     "opts": {"temperature": 1.2}, "repeat": 3},

    {"id": "C6_persona", "lever": "persona / tone shift",
     "system": "You are a cheerful support agent. Confirm the visit warmly in 2 sentences.",
     "user": USER_MSG,
     "opts": {"temperature": 0.4}},

    {"id": "C7_cot", "lever": "chain-of-thought (reasoning task)",
     "system": "Think step by step, then give the final number on its own last line.",
     "user": REASON_MSG,
     "opts": {"temperature": 0}},
]


def parse_json(text):
    m = re.search(r"\{.*\}", text, re.DOTALL)
    if not m:
        return None
    try:
        return json.loads(m.group(0))
    except Exception:
        return None


def behavior(text):
    """Cheap behavioral signals the TA can point at in the output table."""
    obj = parse_json(text)
    return {
        "chars": len(text),
        "words": len(text.split()),
        "is_json": obj is not None,
        "has_prose": parse_json(text) is None and bool(re.search(r"[.!?]\s", text)),
    }


def ask_live(system, user, opts, fmt=None):
    import requests
    msgs = ([{"role": "system", "content": system}] if system else []) + \
           [{"role": "user", "content": user}]
    body = {"model": MODEL, "messages": msgs, "stream": False, "options": opts}
    if fmt:
        body["format"] = fmt
    t0 = time.time()
    r = requests.post(CHAT, json=body, timeout=120)
    r.raise_for_status()
    return r.json()["message"]["content"].strip(), round(time.time() - t0, 2)


def ask_mock(cond, run_idx):
    fx = json.load(open("fixtures/mock_prompt_lab.json"))
    key = cond["id"] + (f"#{run_idx}" if cond.get("repeat") else "")
    return fx.get(key, fx["_default"]), 0.0


def run_condition(cond):
    reps = cond.get("repeat", 1)
    records = []
    for i in range(reps):
        if MOCK:
            text, lat = ask_mock(cond, i)
        else:
            text, lat = ask_live(cond.get("system"), cond["user"], cond["opts"], cond.get("format"))
        records.append({"run": i, "latency_s": lat, **behavior(text), "text": text})
    return records


def main():
    print(f"PROMPT LAB  model={MODEL}  (one model, seven prompt levers)\n")
    header = f"{'condition':<16}{'lever':<28}{'json':>5}{'prose':>6}{'words':>6}"
    print(header)
    print("-" * len(header))
    all_rows = []
    for cond in CONDITIONS:
        recs = run_condition(cond)
        for r in recs:
            all_rows.append({"condition": cond["id"], "lever": cond["lever"], **r})
        # one summary line per condition (first run shown; repeats noted)
        r0 = recs[0]
        tag = cond["id"] + (f" (x{len(recs)})" if len(recs) > 1 else "")
        print(f"{tag:<16}{cond['lever']:<28}{str(r0['is_json']):>5}{str(r0['has_prose']):>6}{r0['words']:>6}")
        # show variability for the high-temp condition
        if len(recs) > 1:
            uniq = len({r['text'] for r in recs})
            print(f"{'':<16}{'  -> distinct outputs across runs:':<28}{uniq:>5}")

    with open("prompt_lab_results.json", "w") as f:
        json.dump(all_rows, f, indent=2)
    print("\nwrote prompt_lab_results.json")
    print("Read the .json to see full texts: each lever changes the SAME model's behavior.")


if __name__ == "__main__":
    main()
