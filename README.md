# SmartLearn.AI

SmartLearn.AI monorepo initialized with:

- **Backend:** FastAPI
- **Frontend:** React + TypeScript (Vite)

## Repository structure

```text
SmartLearn.AI/
├── backend/
│   ├── app/
│   │   ├── api/
│   │   ├── core/
│   │   ├── db/
│   │   ├── middleware/
│   │   ├── models/
│   │   ├── repositories/
│   │   ├── schemas/
│   │   ├── services/
│   │   ├── utils/
│   │   ├── workers/
│   │   └── main.py
│   ├── tests/
│   ├── requirements.txt
│   └── requirements-dev.txt
├── frontend/
│   ├── public/
│   ├── src/
│   │   ├── components/
│   │   ├── features/
│   │   ├── hooks/
│   │   ├── layouts/
│   │   ├── pages/
│   │   ├── routes/
│   │   ├── services/
│   │   ├── store/
│   │   ├── types/
│   │   └── utils/
│   └── package.json
├── ai-services/
├── docs/
└── shared/
```

## Environment variables

Copy and configure:

```bash
cp .env.example .env
```

## Backend setup

```bash
cd backend
python -m venv .venv
source .venv/bin/activate
pip install -r requirements-dev.txt
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

Health endpoint: `GET http://localhost:8000/health`

## Frontend setup

```bash
cd frontend
npm install
npm run dev
```

Frontend default URL: `http://localhost:5173`

## Linting and formatting

### Backend

```bash
cd backend
ruff check .
black --check .
pytest
```

### Frontend

```bash
cd frontend
npm run lint
npm run format
npm run build
```
