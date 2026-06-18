# AGENT Development Context

## Working Method

The user is the product architect and industrial automation domain expert. Codex acts as senior full-stack implementation engineer and technical architect.

Development should stay incremental:

1. Preserve existing API paths once the frontend depends on them.
2. Keep frontend/backend concepts aligned.
3. Keep deterministic backend behavior central.
4. Run local verification after implementation.
5. Report files changed, behavior changes, and remaining limits.

## Current Baseline

- Frontend project-loop workstation exists.
- Frontend API integration exists.
- FastAPI backend uses SQLite local persistence.
- Project deletion exists.
- Backend now owns project readiness and status lifecycle.

## Product Limits

Do not implement or imply:

- Real AI
- RAG
- File parsing
- Excel reading
- PLC connection
- PLC programming
- PLC code conversion

Attachments remain metadata-only.

## Backend Responsibilities

Deterministic backend automation owns:

- Project readiness scoring.
- Automatic `Draft`, `Analyzing`, and `Report Ready` status derivation.
- User-controlled `Finalized` status preservation.
- Platform scoring and benchmark ranking.
- Attachment metadata persistence.
- Report section persistence.

## Readiness Rules

Required checks:

- Project name exists.
- Industry exists.
- Goal exists.
- I/O scale is greater than 0.
- At least two candidate platforms exist.

Recommended checks:

- Team experience exists.
- Constraints exist.
- Existing platform exists.
- At least one attachment metadata record exists.
- Preferences exist for all candidate platforms.
- Report sections exist.

## Verification Expectations

Backend tasks should verify:

- `GET /api/projects`
- `GET /api/projects/{project_id}`
- `GET /api/projects/{project_id}/readiness`
- `PUT /api/projects/{project_id}/status`
- Create, update intake, update preferences, add attachment, benchmark, update report section, finalize, reopen, delete.
- Persistence of `Finalized` across repository reload or backend restart.

Frontend compatibility should be checked with `npm.cmd run build` when feasible.
