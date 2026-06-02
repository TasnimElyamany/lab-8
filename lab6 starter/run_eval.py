#!/usr/bin/env python3
"""Part 3: send a fixed task suite to each model; record output + latency + tokens.
Usage: python run_eval.py            # uses live Ollama at localhost:11434
       python run_eval.py --mock     # uses fixtures/mock_responses.json (no GPU/CI)
"""
import json, time, csv, hashlib, sys, os

GEN = "http://localhost:11434/api/generate"
MODELS = ["llama3.2:3b", "qwen2.5:3b", "phi4-mini:3.8b", "deepseek-r1:1.5b"]
MOCK = "--mock" in sys.argv

def ask_live(model, prompt, seed=42):
    import requests
    t0 = time.time()
    r = requests.post(GEN, json={"model": model, "prompt": prompt, "stream": False,
                                 "options": {"temperature": 0, "seed": seed}}, timeout=120)
    r.raise_for_status()
    d = r.json()
    return {"text": d.get("response", "").strip(),
            "latency_s": round(time.time() - t0, 2),
            "eval_count": d.get("eval_count"),
            "tokens_per_s": round(d.get("eval_count", 0) / max(d.get("eval_duration", 1) / 1e9, 1e-9), 1)}

def ask_mock(model, prompt):
    fx = json.load(open(os.path.join("fixtures", "mock_responses.json")))
    key = hashlib.sha1((model + prompt).encode()).hexdigest()[:8]
    text = fx.get(key, fx.get("_default", ""))
    return {"text": text, "latency_s": 0.0, "eval_count": len(text.split()), "tokens_per_s": 0.0}

def ask(model, prompt):
    return ask_mock(model, prompt) if MOCK else ask_live(model, prompt)

def main():
    tasks = json.load(open("tasks.json"))
    rows = []
    for m in MODELS:
        for t in tasks:
            res = ask(m, t["prompt"])
            rows.append({"model": m, "task_id": t["id"], "category": t["category"],
                         "prompt_hash": hashlib.sha1(t["prompt"].encode()).hexdigest()[:8], **res})
            print(f"[{m}] {t['id']:<10} {res['latency_s']:>5}s  {res['tokens_per_s']:>5} tok/s")
    with open("results.csv", "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=rows[0].keys())
        w.writeheader(); w.writerows(rows)
    print(f"\nwrote results.csv ({len(rows)} rows)")

if __name__ == "__main__":
    main()
