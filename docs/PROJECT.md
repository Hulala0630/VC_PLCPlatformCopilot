# PLC Platform Benchmark & Migration Decision Copilot

## Product Vision

This project is a local-first strategic decision workspace for PLC ecosystem selection, project intake, weighted benchmarking, migration-risk discussion, readiness tracking, and consulting-style report drafting.

## Product Boundary

- Decision support only.
- Not a PLC programming tool.
- Not a PLC code converter.
- No direct PLC connection.
- V1 attachment handling is metadata-only.
- V1 does not parse uploaded files, read Excel content, run RAG, or call real AI.

## Current Product Loop

`Create Project -> Fill Intake -> Register Attachments -> Set Platform Preferences -> Run Benchmark -> Review Readiness -> Edit Report Sections -> Finalize`

## Current Backend State

The FastAPI backend is the local source of truth for project-loop data.

- SQLite database path: `backend/data/plc_copilot.db`
- Database schema initializes on startup.
- Initial mock projects seed only when the database is empty.
- PLC ecosystem profiles remain in memory.
- Projects, intakes, preferences, attachment metadata, report drafts, report sections, and project status persist across backend restarts.

## Status Lifecycle

Backend-owned status values:

- `Draft`: readiness is low, candidate platforms are insufficient, or project goal/industry is missing.
- `Analyzing`: core project inputs are present and benchmark can be prepared, but the report is not ready yet.
- `Report Ready`: readiness is high enough, report sections are ready, and benchmark generation validates.
- `Finalized`: explicitly set by the user and preserved until explicit reopen.

`Finalized` is never assigned automatically.

## Readiness Model

`ProjectWorkspace` includes `readiness`:

- `score`: 0-100 readiness score.
- `status`: derived lifecycle status.
- `missing_required`: required gaps.
- `recommended_missing`: recommended gaps.
- `next_action`: the next useful action.
- `confidence_level`: `Low`, `Medium`, or `High`.
- `reasons`: deterministic explanation of the score.

Required checks contribute 70% of the score. Recommended checks contribute 30%.

## API

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

The backend uses snake_case JSON. The frontend normalizes backend snake_case into frontend camelCase.
