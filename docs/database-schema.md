# SynapseMeet — Database Schema

## PostgreSQL ERD

### users
| Column | Type | Notes |
|--------|------|-------|
| id | UUID PK | |
| email | VARCHAR(255) UNIQUE | indexed |
| hashed_password | VARCHAR(255) | bcrypt |
| full_name | VARCHAR(255) | |
| avatar_url | TEXT | |
| is_active | BOOLEAN | default true |
| is_verified | BOOLEAN | default false |
| workspace_id | UUID | nullable, indexed |
| created_at | TIMESTAMPTZ | |
| updated_at | TIMESTAMPTZ | |

### meetings
| Column | Type | Notes |
|--------|------|-------|
| id | UUID PK | |
| title | VARCHAR(500) | |
| description | TEXT | nullable |
| owner_id | UUID FK(users) | |
| workspace_id | UUID | nullable, indexed |
| status | ENUM | scheduled/live/processing/completed/failed |
| started_at | TIMESTAMPTZ | nullable |
| ended_at | TIMESTAMPTZ | nullable |
| duration_seconds | INTEGER | nullable |
| transcript | TEXT | full transcript |
| summary | TEXT | AI-generated |
| language | VARCHAR(10) | default 'en' |
| speakers | JSONB | {speaker_id: name} |
| sentiment_data | JSONB | per-speaker scores |
| topics | JSONB | string array |
| keywords | JSONB | string array |
| audio_url | TEXT | GCS path |
| embedding_id | VARCHAR(255) | Pinecone ID |
| created_at | TIMESTAMPTZ | |
| updated_at | TIMESTAMPTZ | |

### action_items
| Column | Type | Notes |
|--------|------|-------|
| id | UUID PK | |
| meeting_id | UUID FK(meetings) | indexed |
| title | VARCHAR(500) | |
| description | TEXT | nullable |
| assignee_id | UUID | nullable |
| assignee_name | VARCHAR(255) | nullable |
| status | ENUM | pending/in_progress/done/cancelled |
| priority | ENUM | low/medium/high/critical |
| due_date | DATE | nullable |
| jira_issue_id | VARCHAR(100) | nullable |
| notion_page_id | VARCHAR(100) | nullable |
| slack_message_ts | VARCHAR(100) | nullable |
| transcript_excerpt | TEXT | where it was mentioned |
| timestamp_seconds | FLOAT | position in recording |
| created_at | TIMESTAMPTZ | |
| updated_at | TIMESTAMPTZ | |

## Neo4j Graph Schema

### Node Labels
- `Meeting` — id, title, date, workspace_id
- `Person` — name, user_id (nullable)
- `Topic` — name
- `Decision` — text, meeting_id

### Relationship Types
- `(Person)-[:PARTICIPATED_IN {role}]->(Meeting)`
- `(Topic)-[:DISCUSSED_IN]->(Meeting)`
- `(Person)-[:ASSIGNED_TO]->(ActionItem)`
- `(Meeting)-[:FOLLOWS]->(Meeting)` — recurring meeting series
- `(Topic)-[:RELATED_TO]->(Topic)` — topic clustering

## Alembic Migration Commands

```bash
# Initialize (first time)
cd backend
alembic init alembic

# Create a new migration
alembic revision --autogenerate -m "create_initial_tables"

# Apply migrations
alembic upgrade head

# Rollback one step
alembic downgrade -1
```
