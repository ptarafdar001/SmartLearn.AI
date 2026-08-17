# SmartLearn.AI – Backend API

FastAPI-powered backend for the SmartLearn.AI adaptive learning platform.

---

## Tech Stack

| Layer | Library |
|---|---|
| Framework | [FastAPI](https://fastapi.tiangolo.com/) |
| Server | [Uvicorn](https://www.uvicorn.org/) |
| Settings | [pydantic-settings](https://docs.pydantic.dev/latest/concepts/pydantic_settings/) |
| Validation | [Pydantic v2](https://docs.pydantic.dev/) |

---

## Project Structure

```
backend/
├── app/
│   ├── api/          # Route handlers (versioned routers go here)
│   ├── core/         # Config, security, shared dependencies
│   ├── models/       # ORM / DB models
│   ├── schemas/      # Pydantic request & response schemas
│   ├── services/     # Business logic layer
│   ├── utils/        # Helper functions & utilities
│   └── main.py       # FastAPI app factory & entry point
├── tests/            # Pytest test suite
├── .env.example      # Environment variable template
├── .gitignore
└── requirements.txt
```

---

## Getting Started

### 1. Create & activate virtual environment

```bash
python -m venv venv

# Windows
venv\Scripts\activate

# macOS / Linux
source venv/bin/activate
```

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

### 3. Configure environment

```bash
cp .env.example .env
# Edit .env and fill in your values
```

### 4. Run the development server

```bash
uvicorn app.main:app --reload
```

The API will be available at **http://localhost:8000**

| URL | Description |
|---|---|
| `http://localhost:8000/` | Welcome / health check |
| `http://localhost:8000/health` | Liveness probe |
| `http://localhost:8000/docs` | Swagger UI |
| `http://localhost:8000/redoc` | ReDoc documentation |

---

## Adding New Feature Modules

1. Create your router in `app/api/` (e.g., `app/api/users.py`)
2. Define schemas in `app/schemas/`
3. Add business logic in `app/services/`
4. Register the router in `app/main.py`:

```python
from app.api import users
app.include_router(users.router, prefix="/api/v1/users", tags=["Users"])
```

---

## Running Tests

```bash
pytest
```
