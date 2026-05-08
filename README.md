# Secure AI Insights Assistant

## Overview
A secure internal analytics assistant that answers business questions using SQL, CSV, and internal report documents through approved backend tools.

## Architecture
```mermaid
flowchart LR
UI[Frontend Chat + Charts] --> API[FastAPI Orchestrator]
API --> SQL[SQL Tool (whitelisted queries)]
API --> CSV[CSV Tool (allowlisted files)]
API --> DOC[Document Retrieval Tool]
SQL --> DB[(SQLite)]
CSV --> FILES[(CSV files)]
DOC --> REPORTS[(Internal reports)]
```

## Security Choices
- Tool-only access (no arbitrary SQL from user prompts)
- Allowlisted queries and CSV files
- Basic input validation with Pydantic
- Source trace returned for explainability

## Setup
```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
python scripts/generate_data.py
uvicorn backend.app.main:app --reload
```
Open http://localhost:8000

## Docker
```bash
docker build -t secure-ai-insights .
docker run -p 8000:8000 secure-ai-insights
```

## Example Questions
1. Which titles performed best in 2025?
2. Why is Stellar Run trending recently?
3. Compare Dark Orbit vs Last Kingdom.
4. Which city had the strongest engagement last month?
5. What explains weak comedy performance?
6. What recommendations for leadership next quarter?

## Assumptions / Tradeoffs
- Uses deterministic summarization instead of external LLM for offline reproducibility.
- Internal documents are represented as text reports in `data/pdfs` for demo retrieval.
- SQLite chosen for fast local setup.
