# Backend

FastAPI backend for SmartLearn.AI.

## Run locally

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements-dev.txt
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

## Quality checks

```bash
ruff check .
black --check .
pytest
```
