# PLC Platform Benchmark & Migration Decision Copilot

Local-first consulting workspace for PLC ecosystem selection, migration decision support, deterministic benchmarking, and report drafting.

## Product Boundary

- Decision support only, not PLC programming.
- No PLC code conversion.
- No direct PLC connection.
- V1 attachments are metadata-only.
- V1 does not parse files, read Excel content, run RAG, or call real AI.

## Backend Source Of Truth

The FastAPI backend uses SQLite as the local source of truth for project-loop data.

- Database path: `backend/data/plc_copilot.db`
- The database directory and schema are created on backend startup.
- Initial mock projects are seeded only when the `projects` table is empty.
- PLC ecosystem profiles still live in memory.
- Projects, intakes, preferences, attachment metadata, report drafts, report sections, and project status persist across backend restarts.

## Project Status Lifecycle

Backend-owned status values:

- `Draft`
- `Analyzing`
- `Report Ready`
- `Finalized`

`Draft`, `Analyzing`, and `Report Ready` are computed from project readiness and report state. `Finalized` is user-controlled and is not overwritten by normal edits. Reopen a finalized project with `PUT /api/projects/{project_id}/status` and payload `{ "status": "Analyzing" }`.

## Readiness Scoring

`ProjectWorkspace` responses include:

- `readiness.score`
- `readiness.status`
- `readiness.missing_required`
- `readiness.recommended_missing`
- `readiness.next_action`
- `readiness.confidence_level`
- `readiness.reasons`

Required checks contribute 70%:

- Project name exists.
- Industry exists.
- Goal exists.
- I/O scale is greater than 0.
- At least two candidate platforms are selected.

Recommended checks contribute 30%:

- Team experience exists.
- Constraints exist.
- Existing platform exists.
- At least one attachment metadata record exists.
- Preferences exist for all candidate platforms.
- Report sections exist.

## Backend API

- `GET /health`
- `GET /api/ecosystems`
- `GET /api/platforms`
- `GET /api/projects`
- `GET /api/projects/{project_id}`
- `GET /api/projects/{project_id}/readiness`
- `POST /api/projects`
- `DELETE /api/projects/{project_id}`
- `PUT /api/projects/{project_id}/status`
- `PUT /api/projects/{project_id}/intake`
- `PUT /api/projects/{project_id}/preferences`
- `POST /api/projects/{project_id}/attachments`
- `POST /api/projects/{project_id}/benchmark`
- `PUT /api/projects/{project_id}/report/sections/{section_id}`
- `POST /api/benchmark`

## Run Locally

Backend:

```powershell
cd backend
uvicorn app.main:app --reload --port 8000
```

Frontend:

```powershell
cd frontend
npm install
npm run dev
```
