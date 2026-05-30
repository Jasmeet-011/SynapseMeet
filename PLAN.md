# SynapseMeet — AI-Powered Meeting Intelligence Platform
## Complete Phase-by-Phase Execution Plan

---

## Project Understanding

**Type:** Full-Stack SaaS Web Application
**Complexity:** High (Distributed Systems + Real-Time Streaming + AI Pipeline)
**Core Components:**
- Real-time audio streaming via WebSocket
- AI transcription + summarization pipeline
- Cross-meeting knowledge graph
- Multilingual NLP
- Third-party integrations (Slack, Jira, Notion)
- Semantic search over meeting history

---

## Phase-Based Development Plan

### Phase 1 — Architecture & Planning ✅ (Claude Code)
- Define system architecture
- Generate OpenAPI spec
- Define PostgreSQL schema + vector DB strategy
- Create project scaffold

### Phase 2 — Database Layer (Claude Code)
- PostgreSQL models (SQLAlchemy)
- Alembic migrations
- Redis session caching setup
- Pinecone index initialization
- Neo4j knowledge graph schema

### Phase 3 — Backend Core (Claude Code + Cursor)
- FastAPI app skeleton
- Auth (JWT + OAuth)
- REST endpoints for meetings, users, action items
- Celery worker setup for async AI tasks
- Background job queuing

### Phase 4 — WebSocket Gateway (Claude Code + Cursor)
- Node.js + Socket.IO gateway
- Redis Pub/Sub fan-out
- Audio chunk streaming handler
- Real-time event broadcasting to frontend

### Phase 5 — AI Pipeline (Claude Code + GPT-4o prompt engineering)
- OpenAI Whisper STT integration
- GPT-4o summarization + extraction
- AssemblyAI speaker diarization
- Sentence-transformer embeddings
- Custom NER for people/org detection

### Phase 6 — Frontend (v0.dev → Cursor → Claude Code)
- Next.js 14 app structure
- Real-time WebSocket hooks
- Meeting room UI with waveform visualizer
- D3.js knowledge graph viewer
- Dashboard with sentiment analytics
- shadcn/ui component library

### Phase 7 — Integrations (Claude Code + manual)
- Slack webhook push
- Jira REST API sync
- Notion API integration
- GDPR data retention controls

### Phase 8 — Testing (GitHub Copilot + Claude Code)
- Unit tests (Pytest + Jest)
- Integration tests
- WebSocket load testing
- AI pipeline accuracy evaluation

### Phase 9 — Infra & Deployment (Claude Code + Terraform)
- Docker Compose for local dev
- Kubernetes manifests
- GCP Cloud Run AI workers
- Terraform IaC
- GitHub Actions CI/CD

### Phase 10 — Iteration & Scaling
- Performance profiling
- Horizontal scaling strategy
- Custom vocabulary fine-tuning
- A/B testing for AI prompt optimization

---

## Tool Usage by Phase

| Phase | Tool | Task |
|-------|------|------|
| Architecture | Claude | System design, ERD, API spec |
| DB Schema | Claude Code | SQLAlchemy models, migrations |
| Backend | Claude Code + Cursor | FastAPI routes, services, workers |
| Gateway | Claude Code | Socket.IO, Redis Pub/Sub |
| AI Pipeline | Claude Code + GPT-4o | Prompt engineering, LangChain |
| Frontend | v0.dev → Cursor | UI scaffolding, component generation |
| Testing | Copilot | Unit/integration tests |
| Infra | Claude Code | Terraform, K8s manifests |
| Docs | Claude | README, API docs |

---

## Best Practices

1. **Never generate everything at once** — build and verify one service at a time
2. **Review all AI-generated code** — especially auth, data handling, and SQL
3. **Type everything** — use TypeScript on frontend, Pydantic on backend
4. **Keep AI pipeline stateless** — workers should be independently scalable
5. **Feature flags** — use env vars to toggle integrations during dev
6. **Commit often** — small, atomic commits tied to single features
7. **Separate concerns** — frontend/backend/gateway are independent services

---

## Workflow Loop

```
Plan → Scaffold → Implement → Review → Test → Integrate → Deploy → Iterate
```

**Rule:** AI generates the boilerplate. You own the logic.

---

## What Claude Code Handles Now

- [x] Project scaffold (all folders + config files)
- [x] Backend FastAPI skeleton
- [x] Database models + schemas
- [x] WebSocket gateway skeleton
- [x] Docker Compose setup
- [x] Environment config templates
- [x] API route definitions
- [x] Celery worker base
- [x] Frontend Next.js structure

## What Needs Other Tools (Later)

- [ ] UI layouts → **v0.dev** (generate dashboard mockups first)
- [ ] Prompt engineering → **GPT-4o** (optimize extraction prompts)
- [ ] Component polish → **Cursor** (autocomplete-heavy frontend work)
- [ ] Speaker diarization → **AssemblyAI** (external API integration)
- [ ] Graph visualization → **D3.js** (manual implementation)
- [ ] K8s manifests → **Claude** (after local dev is stable)
