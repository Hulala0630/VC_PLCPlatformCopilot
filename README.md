# PLC Platform Benchmark & Migration Decision Copilot

PLC Platform Benchmark & Migration Decision Copilot is a local-first consulting workspace for PLC ecosystem selection, migration decision support, weighted benchmarking, and report drafting.

PLC Platform Benchmark & Migration Decision Copilot 是一个本地优先的咨询式工作台，用于 PLC 生态选型、迁移决策支持、偏好加权 benchmark 和报告草稿生成。

## Product Boundary / 产品边界

- This is a PLC decision-support platform.
- 这是 PLC 决策支持平台。
- It is not a PLC programming tool.
- 它不是 PLC 编程工具。
- It is not a PLC code converter.
- 它不是 PLC 代码转换工具。
- It does not directly connect to PLCs.
- 它不直接连接 PLC。
- V1 does not parse files, read Excel content, run RAG, or call real AI.
- V1 不解析文件、不读取 Excel 内容、不运行 RAG、不调用真实 AI。

## Current Workflow / 当前工作流

1. Create a project.
   创建项目。
2. Fill lightweight project intake.
   填写轻量项目信息。
3. Register mature project documents as attachment metadata.
   将成熟资料登记为附件元信息。
4. Set platform preference sliders.
   设置 PLC 平台偏好滑块。
5. Run deterministic benchmark analysis.
   运行确定性 benchmark 分析。
6. Review agent placeholder explanations.
   查看 agent 占位解释。
7. Edit and regenerate report sections.
   编辑并重算报告分区。

## Current Repo Status / 当前仓库状态

- Frontend project-loop workstation is implemented.
- 前端项目闭环工作台已实现。
- Mock FastAPI backend API workflow is merged into `master`.
- Mock FastAPI 后端 API 工作流已合并进 `master`。
- Frontend still primarily uses local mock state.
- 前端仍主要使用本地 mock 状态。
- Backend currently uses in-memory mock data.
- 后端当前使用内存态 mock 数据。
- SQLite persistence is not implemented yet.
- 尚未实现 SQLite 持久化。

## Project Structure / 项目结构

- `frontend/`: React, TypeScript, Vite, Tailwind CSS.
- `frontend/`：React、TypeScript、Vite、Tailwind CSS。
- `backend/`: FastAPI mock backend.
- `backend/`：FastAPI mock 后端。
- `docs/`: Product and agent development context.
- `docs/`：产品与 agent 开发上下文。
- `infra/`: Deployment notes.
- `infra/`：部署说明。

## Backend API / 后端 API

The backend is currently an in-memory mock FastAPI service. It defines the API shape, service boundaries, and deterministic mock data source for future frontend integration.

后端当前是内存态 mock FastAPI 服务。它定义了未来前端集成所需的 API 形状、服务边界和确定性 mock 数据源。

Current endpoints:

当前接口：

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

Benchmark 公式：

- `technical_score` is the average of a platform's mock score dimensions.
- `technical_score` 是平台 mock 评分维度的平均值。
- `preference_score` comes from `PlatformPreference`.
- `preference_score` 来自 `PlatformPreference`。
- `weighted_score = technical_score * 0.72 + preference_score * 0.28`.
- `weighted_score = technical_score * 0.72 + preference_score * 0.28`。
- Risk levels: `Low` for scores `>= 78`, `Medium` for scores `>= 65`, otherwise `High`.
- 风险等级：分数 `>= 78` 为 `Low`，`>= 65` 为 `Medium`，否则为 `High`。

## Run Locally / 本地运行

Backend:

后端：

```powershell
cd backend
.\.venv\Scripts\Activate.ps1
uvicorn app.main:app --reload --port 8000
```

Frontend:

前端：

```powershell
cd frontend
npm install
npm run dev
```

Open:

打开：

```text
http://localhost:5173
```

## Next Development Steps / 下一步开发

1. Frontend API integration with FastAPI mock backend.
   前端接入 FastAPI mock backend。
2. SQLite persistence for project-loop data.
   为项目闭环数据加入 SQLite 持久化。
3. Input/output fallback hardening.
   完善输入输出兜底。
4. Intelligence placeholder API.
   建立智能化接口占位层。
5. Future document parsing, Chroma RAG, LangGraph, and report export.
   后续接入文档解析、Chroma RAG、LangGraph 和报告导出。
