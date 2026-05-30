# PLC Platform Benchmark & Migration Decision Copilot

PLC 平台基准与迁移决策副驾驶。

This is a local-first consulting workspace for PLC ecosystem selection, project intake, weighted benchmarking, and report drafting.

这是一个本地优先的咨询式工作台，用于 PLC 生态选型、项目资料收集、倾向权重 benchmark 和报告草稿生成。

## Current Workflow

当前工作流：

1. Create a project.
2. Fill lightweight project intake.
3. Register mature project documents as attachment metadata.
4. Set platform preference sliders.
5. Run deterministic benchmark analysis.
6. Use agent placeholder text for explanation and report prose.
7. Edit and regenerate report sections.

## Product Boundary

- Not a PLC programming tool.
- Not a PLC code converter.
- Not a direct PLC connection tool.
- V1 does not parse files, read Excel, run RAG, or call real AI.

## Project Structure

- `frontend/`: React + TypeScript + Vite + Tailwind CSS.
- `backend/`: FastAPI mock backend.
- `docs/`: Product and agent context.
- `infra/`: Deployment notes.

## Backend API

The backend is currently an in-memory mock FastAPI service. It defines the API shape, service boundaries, and deterministic mock data source for future frontend integration.

V1 backend limits:

- No persistence. Restarting the server resets created and edited data.
- No SQLite or other database.
- No real file upload or file parsing. Attachment endpoints only receive metadata.
- No real AI calls. Benchmarking is deterministic and rule-based.

Current endpoints:

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
- `POST /api/benchmark` for direct benchmark of a submitted workspace payload

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

Open `http://localhost:5173`.
