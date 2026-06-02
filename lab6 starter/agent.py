#!/usr/bin/env python3
"""Part 6: a ReAct (reason->act->observe) loop using Ollama tool calling.
Run: python agent.py        (requires a tool-capable model, e.g. qwen2.5:3b, llama3.1)
"""
import os, json, ollama

MODEL = os.environ.get("AGENT_MODEL", "qwen2.5:3b")
ORDERS = {"A100": {"status": "shipped", "total": 240.0},
          "B200": {"status": "processing", "total": 80.0}}

def lookup_order(order_id: str) -> str:
    """Return the shipping status of a customer order. Args: order_id: the order identifier."""
    o = ORDERS.get(order_id)
    return json.dumps(o) if o else "unknown"

def calculate(expr: str) -> str:
    """Evaluate a simple arithmetic expression for the order. Args: expr: e.g. '240 * 0.05'."""
    if not all(ch in "0123456789.+-*/() " for ch in expr):
        return "error: only arithmetic allowed"
    try: return str(eval(expr, {"__builtins__": {}}, {}))
    except Exception as e: return f"error: {e}"

TOOLS = {"lookup_order": lookup_order, "calculate": calculate}

def run(user_msg, use_context=True, max_steps=6):
    msgs = []
    if use_context and os.path.exists("AGENT.md"):
        msgs.append({"role": "system", "content": open("AGENT.md").read()})
    msgs.append({"role": "user", "content": user_msg})
    for step in range(max_steps):
        resp = ollama.chat(model=MODEL, messages=msgs, tools=list(TOOLS.values()))
        m = resp.message
        msgs.append(m)
        if not m.tool_calls:
            print(f"FINAL: {m.content}")
            return m.content
        for tc in m.tool_calls:
            name = tc.function.name
            args = tc.function.arguments
            result = TOOLS[name](**args)
            print(f"  ACT  step {step}: {name}({args}) -> OBSERVE: {result}")
            msgs.append({"role": "tool", "name": name, "content": result})
    print("FINAL: (max steps reached)")
    return None

if __name__ == "__main__":
    print("== with AGENT.md ==")
    run("If order A100 has shipped, what is the 5% loyalty credit on its total?", use_context=True)
    print("\n== without AGENT.md ==")
    run("If order A100 has shipped, what is the 5% loyalty credit on its total?", use_context=False)
