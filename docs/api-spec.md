# SynapseMeet API Reference

Base URL: `http://localhost:8000/api/v1`
Interactive docs: `http://localhost:8000/docs`

## Authentication

All endpoints (except `/auth/register` and `/auth/login`) require:
```
Authorization: Bearer <jwt_token>
```

---

## Auth

### POST /auth/register
Create a new user account.

**Body:** `{ email, password, full_name }`
**Returns:** `{ access_token, token_type, user }`

### POST /auth/login
Sign in with email + password.

**Body:** `{ email, password }`
**Returns:** `{ access_token, token_type, user }`

---

## Meetings

### GET /meetings/
List all meetings for the authenticated user.

**Query params:** `skip=0`, `limit=20`

### POST /meetings/
Create a new meeting.

**Body:** `{ title, description?, language? }`

### GET /meetings/{id}
Get a single meeting by ID.

### PATCH /meetings/{id}
Update meeting metadata.

### POST /meetings/{id}/start
Mark meeting as LIVE. Call this before starting audio recording.

### POST /meetings/{id}/end
End meeting and trigger AI processing pipeline.

### POST /meetings/{id}/upload-audio
Upload a pre-recorded audio file for async processing.

---

## Action Items

### GET /action-items/meeting/{meeting_id}
Get all action items for a meeting.

### POST /action-items/
Create an action item manually.

### PATCH /action-items/{id}
Update an action item (status, assignee, due date, etc).

### DELETE /action-items/{id}
Delete an action item.

### POST /action-items/{id}/sync-jira
Create a Jira issue from this action item.

---

## Search

### GET /search/?q={query}
Semantic search across all meeting transcripts.

**Query params:** `q` (required), `limit=10`

---

## WebSocket Events (Gateway port 4000)

### Client → Server
| Event | Payload | Description |
|-------|---------|-------------|
| `join_meeting` | `{ meetingId, token }` | Join meeting room |
| `leave_meeting` | `{ meetingId }` | Leave meeting room |
| `audio_chunk` | `{ meetingId, chunk: ArrayBuffer, sequence }` | Stream audio |
| `stop_audio` | `{ meetingId }` | End audio stream |
| `request_summary` | `{ meetingId }` | Fetch cached summary |

### Server → Client
| Event | Payload | Description |
|-------|---------|-------------|
| `joined_meeting` | `{ meetingId, socketId }` | Confirmed join |
| `transcript_update` | `{ meetingId, text, timestamp }` | New transcript chunk |
| `live_summary` | `{ meetingId, summary }` | Updated AI summary |
| `new_action_item` | `{ meetingId, item }` | Extracted action item |
| `recording_stopped` | `{ meetingId }` | Recording ended |
| `error` | `{ message }` | Error notification |
| `chunk_received` | `{ sequence, meetingId }` | Audio chunk ACK |
