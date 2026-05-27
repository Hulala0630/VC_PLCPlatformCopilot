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
- `backend/`: FastAPI API skeleton.
- `docs/`: Product and agent context.
- `infra/`: Deployment notes.

## Backend API Skeleton

- `GET /health`
- `GET /api/ecosystems`
- `GET /api/platforms`
- `GET /api/projects`
- `GET /api/projects/{project_id}`
- `POST /api/benchmark`

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
