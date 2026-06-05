# PLC Platform Benchmark & Migration Decision Copilot

## Product Vision

This project is a local-first strategic decision workspace for PLC ecosystem selection, project intake, weighted benchmarking, migration-risk discussion, and consulting-style report drafting.

It helps engineers, technical managers, consultants, and decision makers compare ecosystems such as Siemens TIA Portal, CODESYS, Beckhoff TwinCAT, Rockwell Studio 5000, Mitsubishi GX Works, and Omron Sysmac.

## Product Boundary

- Decision support only, not PLC programming.
- No PLC code conversion.
- No direct PLC connection.
- V1 attachments are metadata-only.
- V1 does not parse uploaded files, read Excel content, run RAG, or call real AI.
- Deterministic automation owns scoring, ranking, risk labels, and report structure.

## Current Product Loop

`Create Project -> Fill Intake -> Register Attachments -> Set Platform Preferences -> Run Benchmark -> Review Rationale -> Edit Report Sections`

## Current Backend State

The FastAPI backend is now the local source of truth for project-loop data.

- SQLite database path: `backend/data/plc_copilot.db`
- Database schema initializes on startup.
- Initial mock projects seed only when the database is empty.
- PLC ecosystem profiles remain in memory.
- Projects, intakes, preferences, attachment metadata, report drafts, and report sections persist across backend restarts.
- API paths and response shapes remain compatible with the frontend API integration.

## Shared Concepts

These concepts stay aligned between frontend and backend:

- `Project`
- `ProjectIntake`
- `PlatformPreference`
- `ProjectAttachment`
- `BenchmarkResult`
- `ReportDraft`
- `ReportSection`
- `ProjectWorkspace`

The backend uses snake_case JSON. The frontend normalizes backend snake_case into frontend camelCase.

## Current API

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

## Next Milestones

1. Input/output fallback hardening for incomplete project data.
2. Intelligence placeholder APIs for deterministic explanation prose.
3. Future document parsing, RAG, and report export after the V1 boundary is stable.
