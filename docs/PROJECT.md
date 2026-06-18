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

## Current Report Output / 当前报告输出

- Report sections support Edit and Preview modes.
- 报告分区支持编辑与预览模式。
- Markdown copy and download are available.
- 已支持 Markdown 复制和下载。
- PDF is produced through a dedicated print view and browser Save as PDF.
- PDF 通过专用打印视图和浏览器“另存为 PDF”生成。
- PowerPoint is generated locally as `.pptx` from deterministic project data.
- PowerPoint 基于确定性项目数据在本地生成 `.pptx`。
- No export path uses real AI, RAG, or attachment parsing.
- 所有导出路径均不使用真实 AI、RAG 或附件解析。
