``` plaintext
SmartLearn.AI/
│
├── frontend/                      # React + Vite + TypeScript
│   ├── public/
│   ├── src/
│   │   ├── assets/
│   │   ├── components/
│   │   ├── features/
│   │   │   ├── auth/
│   │   │   ├── dashboard/
│   │   │   ├── student/
│   │   │   ├── teacher/
│   │   │   ├── parent/
│   │   │   ├── ai-tutor/
│   │   │   ├── assessment/
│   │   │   └── analytics/
│   │   ├── layouts/
│   │   ├── pages/
│   │   ├── routes/
│   │   ├── services/
│   │   ├── store/
│   │   ├── hooks/
│   │   ├── types/
│   │   └── utils/
│   ├── package.json
│   └── vite.config.ts
│
├── backend/                       # FastAPI
│   ├── app/
│   │   ├── api/
│   │   │   ├── auth/
│   │   │   ├── users/
│   │   │   ├── syllabus/
│   │   │   ├── learning/
│   │   │   ├── assessments/
│   │   │   ├── uploads/
│   │   │   ├── analytics/
│   │   │   └── ai/
│   │   ├── core/
│   │   ├── db/
│   │   ├── middleware/
│   │   ├── models/
│   │   ├── repositories/
│   │   ├── schemas/
│   │   ├── services/
│   │   ├── workers/
│   │   ├── utils/
│   │   └── main.py
│   ├── tests/
│   ├── requirements.txt
│   └── Dockerfile
│
├── ai-services/                   # AI Layer
│   ├── agents/
│   │   ├── tutor/
│   │   ├── planner/
│   │   ├── assessment/
│   │   ├── revision/
│   │   └── recommendation/
│   │
│   ├── rag/
│   │   ├── ingestion/
│   │   ├── retriever/
│   │   ├── reranker/
│   │   ├── vectorstore/
│   │   └── pipeline/
│   │
│   ├── prompts/
│   ├── embeddings/
│   ├── llm/
│   ├── memory/
│   └── evaluation/
│
├── shared/                        # Shared code
│   ├── constants/
│   ├── config/
│   ├── types/
│   └── utils/
│
├── docs/
│   ├── architecture/
│   ├── api/
│   ├── database/
│   ├── setup/
│   ├── roadmap/
│   └── meeting-notes/
│
├── infrastructure/
│   ├── docker/
│   ├── nginx/
│   ├── kubernetes/
│   ├── monitoring/
│   └── terraform/      # Optional
│
├── scripts/
│   ├── setup.sh
│   ├── seed.py
│   └── migrate.py
│
├── datasets/
│
├── .github/
│   ├── ISSUE_TEMPLATE/
│   ├── PULL_REQUEST_TEMPLATE.md
│   └── workflows/
│       ├── backend-ci.yml
│       ├── frontend-ci.yml
│       └── deploy.yml
│
├── docker-compose.yml
├── .env.example
├── .gitignore
├── README.md
├── CONTRIBUTING.md
├── LICENSE
└── Makefile


```
