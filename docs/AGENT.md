# AGENT Development Context

## Working Method

This project uses an incremental implementation workflow.

The user acts as product architect and industrial automation domain expert. Codex acts as senior full-stack implementation engineer and technical architect.

Development steps:

1. Clarify the smallest useful slice.
2. Keep API and UI concepts aligned.
3. Keep the app runnable.
4. Run local verification.
5. Report decisions, verification results, and remaining limits.

## Current Baseline

The repository has:

- React + TypeScript frontend workstation.
- FastAPI backend endpoints integrated by the frontend.
- SQLite-backed local persistence for project-loop data.
- Deterministic benchmark service.
- Shared models for project, intake, preferences, attachment metadata, benchmark results, report drafts, report sections, and project workspaces.

Current backend persistence:

- Database path: `backend/data/plc_copilot.db`
- Schema is initialized on startup.
- Seed data is inserted only when the project table is empty.
- Project changes survive backend restarts.
- Attachments remain metadata-only.

## Architecture

- `frontend/`: React, TypeScript, Vite, Tailwind CSS workstation UI.
- `backend/`: FastAPI backend with SQLite repository layer.
- `docs/`: Product and development context.
- `infra/`: Deployment notes and Docker-related structure.

Do not recreate the removed `apps/` prototype directory unless explicitly requested.

## Development Rules

- Focus on PLC decision support, not PLC programming.
- Do not build PLC code conversion.
- Do not build direct PLC connection.
- Do not claim attachments were parsed before parsing/RAG is implemented.
- Prefer deterministic automation for scoring, ranking, risk, and report structure.
- Use AI only later for explanation, prose, follow-up questions, and section rewriting.
- Keep API paths stable once the frontend depends on them.

## Verification Expectations

For backend tasks:

- Run FastAPI smoke checks for key endpoints.
- Verify persistence across repository reload or backend restart.
- Confirm API response shape stays compatible with frontend normalization.

For frontend compatibility:

- Run `npm.cmd run build` in `frontend/` when feasible.
- Start backend and frontend preview/dev servers when useful.

For docs:

- Keep files readable as UTF-8.
- Keep product boundary and current implementation state explicit.
