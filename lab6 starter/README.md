# CISC 814 — Lab 3 starter repo

Skeleton code for the lab manual. Files map 1:1 to manual parts.

| File | Part | Purpose |
|------|------|---------|
| `tasks.json` | 3 | the fixed task suite (promptware artifact) |
| `run_eval.py` | 3 | runs the suite on each model (`--mock` for CI) |
| `prompt_lab.py` | 4B | one model, 7 prompt levers — behavior change demo |
| `score.py` | 5 | scores results -> `scorecard.csv` + matrix |
| `agent.py` / `AGENT.md` | 6 | ReAct tool-calling loop + agent context |
| `mcp_server.py` / `mcp_client.py` | 7 | MCP server + 5-step client |
| `data_pipeline.py` | 8 | collect -> clean -> label |
| `gate.py` | 9 | CD4ML quality gate |
| `.github/workflows/eval.yml` | 9 | CI that runs mock eval + gate |
| `fixtures/mock_responses.json` | 9 | deterministic outputs for offline CI |

## Quick start
```bash
pip install -r requirements.txt          # deps
ollama serve &                           # if not already running
ollama pull qwen2.5:3b llama3.2:3b       # at least one tool-capable model
python run_eval.py        # live   (needs Ollama + pulled models)
python run_eval.py --mock # offline (no GPU; used by CI)
python score.py
python prompt_lab.py --mock   # Part 4B prompt-lever demo
CHOSEN_MODEL=qwen2.5:3b python gate.py
python agent.py
python mcp_client.py
```
