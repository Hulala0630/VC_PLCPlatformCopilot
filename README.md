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
- Attachments are metadata-only in V1.
- V1 附件仅保存元信息。

## Current Workflow / 当前工作流

1. Create a project.
   创建项目。
2. Fill lightweight project intake.
   填写轻量项目信息。
3. Register project documents as attachment metadata.
   将项目资料登记为附件元信息。
4. Set platform preference sliders.
   设置 PLC 平台偏好滑块。
5. Run deterministic benchmark analysis.
   运行确定性 benchmark 分析。
6. Review assumptions and rationale.
   查看假设与推荐理由。
7. Edit report sections.
   编辑报告分区。

## Current Repo Status / 当前仓库状态

- Frontend project-loop workstation is implemented and integrated with the backend API.
- 前端项目闭环工作台已实现，并已接入后端 API。
- Backend now uses SQLite as the local source of truth for project-loop data.
- 后端现在使用 SQLite 作为项目闭环数据的本地事实来源。
- PLC ecosystem profiles still live in memory.
- PLC 生态 profile 仍保存在内存 mock 数据中。
- Project, intake, preferences, attachment metadata, report drafts, and report sections persist across backend restarts.
- 项目、输入、偏好、附件元信息、报告草稿和报告分区可以跨后端重启持久化。

## Project Structure / 项目结构

- `frontend/`: React, TypeScript, Vite, Tailwind CSS.
- `frontend/`：React、TypeScript、Vite、Tailwind CSS。
- `backend/`: FastAPI backend with SQLite local persistence.
- `backend/`：带 SQLite 本地持久化的 FastAPI 后端。
- `docs/`: Product and agent development context.
- `docs/`：产品与 agent 开发上下文。
- `infra/`: Deployment notes.
- `infra/`：部署说明。

## Backend Persistence / 后端持久化

The backend uses SQLite as the local source of truth for project-loop data.

后端使用 SQLite 作为项目闭环数据的本地事实来源。

- Database path: `backend/data/plc_copilot.db`
- 数据库路径：`backend/data/plc_copilot.db`
- The database directory is created automatically on backend startup.
- 后端启动时会自动创建数据库目录。
- The schema is initialized on startup.
- 后端启动时会初始化 schema。
- Initial mock projects are seeded only when the `projects` table is empty.
- 仅当 `projects` 表为空时才写入初始 mock 项目。
- No V1 workflow persists real file contents, parsed document content, RAG state, AI output, PLC connections, PLC code, or PLC conversion logic.
- V1 不持久化真实文件内容、解析后的文档内容、RAG 状态、AI 输出、PLC 连接、PLC 代码或 PLC 转换逻辑。

## Backend API / 后端 API

The existing API shape is preserved:

现有 API 形状保持不变：

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
http://localhost:5174
```

## Next Development Steps / 下一步开发

1. Input/output fallback hardening for incomplete project data.
   完善项目信息不完整时的输入输出兜底。
2. Intelligence placeholder APIs for deterministic explanation prose.
   建立智能化占位 API，用确定性方式生成解释文字。
3. Future document parsing, RAG, and report export after the V1 boundary is stable.
   在 V1 边界稳定后，再进入文档解析、RAG 与报告导出。
