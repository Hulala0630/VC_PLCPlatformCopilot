# PLC Platform Benchmark & Migration Decision Copilot

PLC Platform Benchmark & Migration Decision Copilot is a local-first consulting workspace for PLC ecosystem selection, migration decision support, weighted benchmarking, and report drafting.

## Product Boundary

- This is a PLC decision-support platform.
- It is not a PLC programming tool.
- It is not a PLC code converter.
- It does not directly connect to PLCs.
- V1 does not parse files, read Excel content, run RAG, or call real AI.
- Attachments are metadata-only in V1.

## Current Workflow

1. Create a project.
2. Fill lightweight project intake.
3. Register project documents as attachment metadata.
4. Set platform preference sliders.
5. Run deterministic benchmark analysis.
6. Review assumptions and rationale.
7. Edit report sections.

## Project Structure

- `frontend/`: React, TypeScript, Vite, Tailwind CSS.
- `backend/`: FastAPI backend with SQLite local persistence.
- `docs/`: Product and agent development context.
- `infra/`: Deployment notes.

## Backend Persistence

The backend now uses SQLite as the local source of truth for project-loop data.

- Database path: `backend/data/plc_copilot.db`
- The database directory is created automatically on backend startup.
- The schema is initialized on startup.
- Initial mock projects are seeded only when the `projects` table is empty.
- PLC ecosystem profiles still live in memory in `backend/app/data.py`.
- Project, intake, preferences, attachment metadata, report drafts, and report sections are persisted.

No V1 workflow persists real file contents, parsed document content, RAG state, AI output, PLC connections, PLC code, or PLC conversion logic.

## Backend API

The existing API shape is preserved:

- `GET /health`
- `GET /api/ecosystems`
- `GET /api/platforms`
- `GET /api/projects`
- `GET /api/projects/{project_id}`
- `POST /api/projects`
- `PUT /api/projects/{project_id}/intake`
- `PUT /api/projects/{project_id}/preferences`
- `POST /api/projects/{project_id}/attachments`
- `POST /api/projects/{project_id}/benchmark`
- `PUT /api/projects/{project_id}/report/sections/{section_id}`
- `POST /api/benchmark`

Benchmark formula:

- `technical_score` is the average of a platform's mock score dimensions.
- `preference_score` comes from `PlatformPreference`.
- `weighted_score = technical_score * 0.72 + preference_score * 0.28`.
- Risk levels: `Low` for scores `>= 78`, `Medium` for scores `>= 65`, otherwise `High`.

## Run Locally

Backend:

```powershell
cd backend
.\.venv\Scripts\Activate.ps1
uvicorn app.main:app --reload --port 8000
```

Frontend:

```powershell
cd frontend
npm install
npm run dev
```

Open `http://localhost:5173` or `http://localhost:5174`, depending on the Vite port.
