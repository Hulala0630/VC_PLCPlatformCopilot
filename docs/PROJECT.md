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

## Intelligence Contract / 智能化接口契约

The intelligence layer has one provider boundary and currently uses `DeterministicPlaceholderProvider` only.

智能化层通过统一 provider 边界工作，当前仅使用 `DeterministicPlaceholderProvider`。

Supported scopes:

支持的业务范围：

- Global platform-profile chat / 全局平台 profile 问答
- Project chat / 项目问答
- Project analysis / 项目分析
- Benchmark explanation / Benchmark 解释
- Full report draft suggestions / 完整报告建议稿
- Report section rewrite suggestions / 报告分区改写建议

Project intelligence is grounded in structured intake, preferences, deterministic benchmark results, readiness, report status, existing report sections, and attachment metadata. Attachment file content is never treated as parsed.

项目智能化仅基于结构化输入、偏好、确定性 benchmark、成熟度、报告状态、现有报告分区和附件元信息。系统绝不会声称已解析附件文件内容。

Provider output is advisory and is not persisted. Users remain responsible for applying report changes.

Provider 输出仅作为建议且不持久化，报告修改仍由用户确认和应用。

## Secure AI Configuration / 安全 AI 配置

The backend owns all provider configuration and explicitly loads `.env.local` from the repository root. Process environment variables override local-file values. Frontend code never receives or manages `OPENAI_API_KEY`.

所有 provider 配置都由后端负责，并从仓库根目录显式加载 `.env.local`。进程环境变量覆盖本地文件值。前端代码不会接收或管理 `OPENAI_API_KEY`。

The future OpenAI provider has three named quality profiles:

未来 OpenAI provider 使用三档命名质量配置：

- `fast` via `AI_MODEL_FAST`
- `balanced` via `AI_MODEL_BALANCED`
- `quality` via `AI_MODEL_QUALITY`

The public status contract exposes only provider name, configured state, available profile names, fallback state, and safe errors. It never exposes the API key or concrete model IDs.

公开 status 契约只暴露 provider 名称、配置状态、可用 profile 名称、fallback 状态和安全错误；绝不暴露 API key 或具体 model ID。

Phase 1 adds configuration only. It performs no real model calls. Deterministic benchmark scoring remains the authoritative source of truth.

Phase 1 只增加配置基础，不执行真实模型调用。确定性 benchmark 评分继续作为权威事实来源。

## OpenAI Provider Runtime / OpenAI Provider 运行时

The provider factory selects one runtime safely:

- `AI_PROVIDER=placeholder`: deterministic placeholder.
- Configured `AI_PROVIDER=openai`: real OpenAI Responses API provider.
- Invalid or incomplete OpenAI configuration: deterministic placeholder.
- Provider failure with fallback enabled: explicitly labeled deterministic fallback.
- Provider failure with fallback disabled: sanitized API error category.

Provider factory 会根据配置安全选择运行时；fallback 输出不会伪装成真实 AI 输出。

Task routing uses profile names only:

- `fast`: global chat and connection test.
- `balanced`: project chat, project analysis, benchmark explanation.
- `quality`: report generation and section rewrite.

Structured responses are validated before return. Report generation preserves the existing section IDs and titles. Rewrite requests return only one section suggestion and never persist automatically.

所有 structured response 都在返回前通过 Pydantic 校验。报告生成保留既有 section ID/title；分区改写只返回目标分区建议且不会自动持久化。

Deterministic benchmark scores remain immutable source data. OpenAI may explain them but cannot recalculate or replace them. Attachments remain metadata-only.

确定性 benchmark 分数是不可变事实数据；OpenAI 只能解释，不能重新计算或替代。附件仍仅作为 metadata 使用。

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
