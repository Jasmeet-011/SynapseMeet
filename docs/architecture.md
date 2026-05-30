# SynapseMeet — System Architecture

## High-Level Overview

```
Browser (Next.js)
    │
    ├── REST API calls ──────────────────► FastAPI Backend (port 8000)
    │                                           │
    └── WebSocket (Socket.IO) ───────► Node.js Gateway (port 4000)
                                                │
                                         Redis Pub/Sub
                                                │
                              ┌─────────────────┴──────────────────┐
                              │                                      │
                        FastAPI Backend                       Celery Workers
                              │                                      │
                    ┌─────────┼──────────┐              ┌───────────┴────────────┐
                    │         │          │              │                         │
                PostgreSQL  Pinecone   Neo4j        OpenAI Whisper          AssemblyAI
                 (users,   (vectors)  (graph)       GPT-4o (LLM)           (diarization)
                meetings)
```

## Service Responsibilities

### Next.js Frontend (port 3000)
- UI rendering + client state (Zustand)
- REST API calls via Axios + React Query
- WebSocket connection to gateway for real-time events
- MediaRecorder API for audio capture

### FastAPI Backend (port 8000)
- Auth (JWT), users, meetings, action items REST API
- Enqueues Celery tasks for AI processing
- Publishes events to Redis for gateway fan-out
- Direct DB access (PostgreSQL, Neo4j, Pinecone)

### Node.js Gateway (port 4000)
- WebSocket server (Socket.IO) for real-time clients
- Audio chunk relay from browser to backend
- Subscribes to Redis Pub/Sub and fans out to rooms
- Room management per meeting

### Celery Workers
- Post-meeting AI pipeline (transcription → summary → extraction → indexing)
- Live summary generation (every 30s, publishes to Redis)
- Integration sync (Slack, Jira, Notion)

## Data Flow — Live Meeting

1. User clicks "Start Recording" in browser
2. Frontend: `MediaRecorder` captures audio → sends chunks via WebSocket every 5s
3. Gateway: buffers chunks → flushes to Backend `/transcribe-chunk`
4. Backend: sends to Whisper API → returns transcript text
5. Backend: publishes `meeting:transcript_chunk` to Redis
6. Gateway: receives from Redis → broadcasts to all sockets in `meeting:{id}` room
7. Celery: every 30s, generates rolling summary → publishes `meeting:summary` to Redis
8. Gateway: fans out summary to frontend → UI updates live summary panel

## Data Flow — Post-Meeting

1. User clicks "End Meeting"
2. Backend marks meeting as `processing` → enqueues `process_meeting_audio` Celery task
3. Celery:
   a. Full Whisper transcription
   b. AssemblyAI speaker diarization
   c. GPT-4o summary + action item extraction (function calling)
   d. Topic/keyword extraction
   e. Sentiment analysis
   f. Pinecone vector indexing
   g. Neo4j knowledge graph update
   h. Action items saved to PostgreSQL
   i. Optional: Slack/Jira/Notion sync
4. Meeting marked as `completed`

## Database Schema Summary

### PostgreSQL
- `users` — auth, profile, workspace
- `meetings` — metadata, transcript, summary, AI outputs (JSONB)
- `action_items` — extracted tasks with assignees, deadlines, external IDs

### Pinecone
- Index: `synapsemeet-meetings`
- Vectors: 384-dim (all-MiniLM-L6-v2)
- Metadata: meeting_id, title, user_id, workspace_id, excerpt

### Neo4j
- Nodes: `Meeting`, `Person`, `Topic`, `Decision`
- Edges: `PARTICIPATED_IN`, `DISCUSSED_IN`, `MADE_DECISION`

### Redis
- Session cache, live summary cache, Celery broker/backend
- Pub/Sub channels: `meeting:summary`, `meeting:action_item`, `meeting:transcript_chunk`
