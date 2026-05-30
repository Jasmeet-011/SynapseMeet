# SynapseMeet

**Real-Time AI Meeting Intelligence Platform**

Transcribe, summarize, extract action items, and build a cross-meeting knowledge graph — automatically, across 40+ languages.

---

## Architecture

| Layer | Tech |
|-------|------|
| Frontend | Next.js 14, React, Tailwind CSS, shadcn/ui, D3.js |
| Backend | FastAPI (Python), Celery |
| Gateway | Node.js, Socket.IO |
| Databases | PostgreSQL, Pinecone, Neo4j, Redis |
| AI/ML | OpenAI Whisper, GPT-4o, sentence-transformers, AssemblyAI |
| Infra | Docker, Kubernetes, GCP, Terraform |

## Project Structure

```
SynapseMeet/
├── frontend/          # Next.js 14 app
├── backend/           # FastAPI + Celery AI pipeline
├── gateway/           # Node.js + Socket.IO WebSocket gateway
├── infra/
│   ├── terraform/     # GCP infrastructure as code
│   └── kubernetes/    # K8s deployment manifests
├── docs/              # Architecture, API spec, DB schema
├── .github/workflows/ # CI/CD
└── docker-compose.yml # Local development
```

## Quick Start (Local Dev)

### 1. Clone and configure environment
```bash
cp .env.example .env
# Fill in your API keys (OpenAI, Pinecone, AssemblyAI)
```

### 2. Start all services with Docker Compose
```bash
docker-compose up -d
```

### 3. Access the services
| Service | URL |
|---------|-----|
| Frontend | http://localhost:3000 |
| Backend API | http://localhost:8000/docs |
| WebSocket Gateway | http://localhost:4000 |
| Neo4j Browser | http://localhost:7474 |

### 4. Run database migrations (first time)
```bash
cd backend
alembic upgrade head
```

## Development (without Docker)

### Backend
```bash
cd backend
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
uvicorn main:app --reload --port 8000
```

### Celery Worker
```bash
cd backend
celery -A app.workers.celery_app worker --loglevel=info
```

### Gateway
```bash
cd gateway
npm install
npm run dev
```

### Frontend
```bash
cd frontend
npm install
npm run dev
```

## Running Tests

```bash
cd backend
pytest --cov=app -v
```

## Key Environment Variables

| Variable | Required | Description |
|----------|----------|-------------|
| `OPENAI_API_KEY` | Yes | GPT-4o + Whisper |
| `PINECONE_API_KEY` | Yes | Semantic search |
| `ASSEMBLYAI_API_KEY` | For diarization | Speaker labels |
| `DATABASE_URL` | Yes | PostgreSQL |
| `REDIS_URL` | Yes | Cache + Celery |
| `NEO4J_PASSWORD` | Yes | Knowledge graph |
| `SECRET_KEY` | Yes | App secret |
| `JWT_SECRET` | Yes | Auth tokens |

## Development Phases

See [`PLAN.md`](./PLAN.md) for the complete phase-by-phase execution plan.

- **Phase 1-2** (Claude Code): Architecture, scaffold, DB models ✅
- **Phase 3-5** (Claude Code + Cursor): Backend services, AI pipeline ✅ (skeleton)
- **Phase 6** (v0.dev → Cursor): Frontend UI polish
- **Phase 7** (Claude Code): Integrations (Slack, Jira, Notion)
- **Phase 8** (Copilot): Full test coverage
- **Phase 9** (Terraform + K8s): Production deployment
