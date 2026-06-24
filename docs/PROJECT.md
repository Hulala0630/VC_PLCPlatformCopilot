# PLC Platform Benchmark & Migration Decision Copilot

## Product Vision / 产品愿景

This project is a local-first strategic decision workspace for PLC ecosystem selection, project intake, weighted benchmarking, migration-risk discussion, readiness tracking, AI-assisted analysis, and consulting-style report drafting.

本项目是一个本地优先的 PLC 平台战略决策工作台，用于 PLC 生态选型、项目信息录入、偏好加权 Benchmark、迁移风险讨论、成熟度跟踪、AI 辅助分析和咨询式报告草稿生成。

## Product Boundary / 产品边界

- Decision support only. / 仅用于决策支持。
- Not a PLC programming tool. / 不是 PLC 编程工具。
- Not a PLC code converter. / 不是 PLC 代码转换工具。
- No direct PLC connection. / 不直接连接 PLC 或控制网络。
- Attachment handling is metadata-only in the current version. / 当前版本附件仅登记元信息。
- The current version does not parse uploaded files, read Excel content, or run RAG. / 当前版本不解析上传文件、不读取 Excel 内容、不运行 RAG。
- Real OpenAI-compatible AI calls are supported when local configuration is valid; deterministic baseline analysis remains available. / 当本地配置有效时，系统支持真实 OpenAI 兼容 AI 调用，同时保留确定性基础分析。

## Current Product Loop / 当前产品闭环

`Create Project -> Fill Intake -> Register Attachments -> Set Platform Preferences -> Run Benchmark -> Ask AI / Use Basic Analysis -> Review Report Suggestions -> Edit Report Sections -> Export / Finalize`

`创建项目 -> 填写项目信息 -> 登记附件 -> 设置平台偏好 -> 运行 Benchmark -> 使用 AI 或基础分析 -> 审阅报告建议 -> 编辑报告分区 -> 导出 / 定稿`

## Current Backend State / 当前后端状态

The FastAPI backend is the local source of truth for project-loop data.

FastAPI 后端是项目闭环数据的本地事实来源。

- SQLite database path: `backend/data/plc_copilot.db`
- Database schema initializes on startup.
- Initial mock projects seed only when the database is empty.
- PLC ecosystem profiles remain in memory.
- Projects, intakes, preferences, attachment metadata, report drafts, report sections, and project status persist across backend restarts.

- SQLite 数据库路径：`backend/data/plc_copilot.db`
- 数据库 schema 在启动时初始化。
- 仅当数据库为空时写入初始 mock 项目。
- PLC 生态 profile 当前保留在内存数据中。
- 项目、录入信息、偏好、附件元信息、报告草稿、报告分区和项目状态会跨后端重启持久化。

## Status Lifecycle / 状态生命周期

Backend-owned status values:

后端负责派生和维护以下状态：

- `Draft`: readiness is low, candidate platforms are insufficient, or project goal/industry is missing.
- `Analyzing`: core project inputs are present and benchmark can be prepared, but the report is not ready yet.
- `Report Ready`: readiness is high enough, report sections are ready, and benchmark generation validates.
- `Finalized`: explicitly set by the user and preserved until explicit reopen.

- `Draft`：成熟度较低、候选平台不足，或项目目标/行业缺失。
- `Analyzing`：核心输入已具备，可以准备 Benchmark，但报告尚未准备好。
- `Report Ready`：成熟度足够、报告分区已具备，并且 Benchmark 生成通过校验。
- `Finalized`：由用户显式设置，并在用户重新打开前保持。

`Finalized` is never assigned automatically.

`Finalized` 永远不会自动赋值。

## Readiness Model / 成熟度模型

`ProjectWorkspace` includes `readiness`:

`ProjectWorkspace` 包含 `readiness`：

- `score`: 0-100 readiness score.
- `status`: derived lifecycle status.
- `missing_required`: required gaps.
- `recommended_missing`: recommended gaps.
- `next_action`: the next useful action.
- `confidence_level`: `Low`, `Medium`, or `High`.
- `reasons`: deterministic explanation of the score.

- `score`：0-100 成熟度分数。
- `status`：派生生命周期状态。
- `missing_required`：必要缺口。
- `recommended_missing`：建议补充项。
- `next_action`：下一步建议动作。
- `confidence_level`：`Low`、`Medium` 或 `High`。
- `reasons`：确定性成熟度解释。

Required checks contribute 70% of the score. Recommended checks contribute 30%.

必要检查贡献 70% 分数，建议检查贡献 30% 分数。

## API / API

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
- `POST /api/intelligence/global/chat`
- `POST /api/projects/{project_id}/intelligence/chat`
- `POST /api/projects/{project_id}/intelligence/analyze`
- `POST /api/projects/{project_id}/benchmark/explain`
- `POST /api/projects/{project_id}/report/generate`
- `POST /api/projects/{project_id}/report/sections/{section_id}/rewrite`

The backend uses snake_case JSON. The frontend normalizes backend snake_case into frontend camelCase.

后端使用 snake_case JSON，前端会转换为 camelCase。

## Intelligence Contract / 智能化接口契约

The intelligence layer has one provider boundary and can select either deterministic baseline analysis or a configured OpenAI-compatible provider.

智能化层通过统一 provider 边界工作，可以选择确定性基础分析，也可以在配置有效时使用 OpenAI 兼容 provider。

Supported scopes:

支持的业务范围：

- Global platform-profile chat / 全局平台 profile 问答
- Project chat / 项目问答
- Project analysis / 项目分析
- Attachment registration analysis / 附件登记分析
- Benchmark explanation / Benchmark 解释
- Full report draft suggestions / 完整报告建议稿
- Report section rewrite suggestions / 报告分区改写建议

Project intelligence is grounded in structured intake, preferences, deterministic benchmark results, readiness, report status, existing report sections, and attachment metadata. Attachment file content is never treated as parsed.

项目智能化仅基于结构化输入、平台偏好、确定性 Benchmark、成熟度、报告状态、现有报告分区和附件元信息。系统绝不会声称已解析附件正文。

Provider output is advisory and is not persisted automatically. Users remain responsible for applying report changes.

Provider 输出仅作为建议，不会自动持久化。报告修改仍由用户确认和应用。

## Secure AI Configuration / 安全 AI 配置

The backend owns all provider configuration and explicitly loads `.env.local` from the repository root. Process environment variables override local-file values. Frontend code never receives or manages `OPENAI_API_KEY`.

所有 provider 配置都由后端负责，并从仓库根目录显式加载 `.env.local`。进程环境变量覆盖本地文件值。前端代码不会接收或管理 `OPENAI_API_KEY`。

The OpenAI-compatible provider uses three named quality profiles:

OpenAI 兼容 provider 使用三档命名质量配置：

- `fast` via `AI_MODEL_FAST`
- `balanced` via `AI_MODEL_BALANCED`
- `quality` via `AI_MODEL_QUALITY`

The public status contract exposes only provider name, configured state, available profile names, fallback state, and safe errors. It never exposes the API key or concrete model IDs.

公开 status 契约只暴露 provider 名称、配置状态、可用 profile 名称、fallback 状态和安全错误；绝不暴露 API key 或具体 model ID。

## OpenAI Provider Runtime / OpenAI Provider 运行时

The provider factory selects one runtime safely:

Provider factory 会根据配置安全选择运行时：

- `AI_PROVIDER=placeholder`: deterministic baseline provider.
- Configured `AI_PROVIDER=openai`: real OpenAI Responses API provider.
- Invalid or incomplete OpenAI configuration: deterministic baseline provider.
- Provider failure with fallback enabled: explicitly labeled basic analysis fallback.
- Provider failure with fallback disabled: sanitized API error category.

- `AI_PROVIDER=placeholder`：确定性基础分析 provider。
- 配置有效的 `AI_PROVIDER=openai`：真实 OpenAI Responses API provider。
- OpenAI 配置无效或不完整：回到确定性基础分析 provider。
- provider 失败且 fallback 开启：返回明确标记的基础分析兜底。
- provider 失败且 fallback 关闭：返回脱敏 API 错误类别。

Task routing uses profile names only:

任务路由只使用 profile 名称：

- `fast`: global chat and connection test.
- `balanced`: project chat, project analysis, benchmark explanation.
- `quality`: report generation and section rewrite.

Structured responses are validated before return. Report generation preserves existing section IDs and titles. Rewrite requests return only one section suggestion and never persist automatically.

所有 structured response 都在返回前通过 Pydantic 校验。报告生成保留既有 section ID/title；分区改写只返回目标分区建议且不会自动持久化。

Deterministic benchmark scores remain immutable source data. OpenAI may explain them but cannot recalculate or replace them. Attachments remain metadata-only.

确定性 Benchmark 分数是不可变事实数据；OpenAI 只能解释，不能重新计算或替代。附件仍仅作为元信息使用。

## Intelligence Execution Contract / 智能执行契约

All intelligence workflows expose the same frontend-facing execution fields:

所有智能工作流都暴露同一组面向前端的执行字段：

- `execution_status=ai_success`: AI completed successfully.
- `execution_status=basic_analysis`: the user disabled AI and received normal baseline analysis.
- `execution_status=ai_fallback`: AI was requested but baseline analysis was returned after a safe failure.
- `fallback_reason`: `timeout`, `rate_limit`, `authentication`, `unsupported_model`, `invalid_response`, `provider_unavailable`, or `null`.
- `retryable`: whether retrying the AI request may reasonably succeed.
- `request_id`: a safe correlation identifier for support and diagnostics.

- `execution_status=ai_success`：AI 成功完成。
- `execution_status=basic_analysis`：用户关闭 AI，收到基础分析。
- `execution_status=ai_fallback`：用户请求 AI，但安全失败后返回基础分析。
- `fallback_reason`：`timeout`、`rate_limit`、`authentication`、`unsupported_model`、`invalid_response`、`provider_unavailable` 或 `null`。
- `retryable`：重试 AI 请求是否可能成功。
- `request_id`：用于支持和诊断的安全关联 ID。

Fields such as `mode`, `provider`, `model_profile`, and `document_parsing_used` remain machine-facing diagnostics. They must not be rendered directly as consulting copy.

`mode`、`provider`、`model_profile` 和 `document_parsing_used` 属于机器诊断字段，不应直接渲染为咨询文案。

## Current Report Output / 当前报告输出

- Report sections support Edit and Preview modes.
- Markdown copy and download are available.
- PDF is produced through a dedicated print view and browser Save as PDF.
- PowerPoint is generated locally as `.pptx` from project data.
- Export paths use the current accepted report, deterministic benchmark results, and registered attachment metadata. They do not parse attachments or call AI during export.

- 报告分区支持编辑与预览模式。
- 已支持 Markdown 复制和下载。
- PDF 通过专用打印视图和浏览器“另存为 PDF”生成。
- PowerPoint 基于项目数据在本地生成 `.pptx`。
- 导出路径使用当前已接受报告、确定性 Benchmark 结果和附件登记元信息；导出时不解析附件，也不调用 AI。

## Next Phase: Task 5B / 下一阶段：Task 5B

Task 5B prepares attachment intelligence before real file parsing or RAG. The planning contract is documented in `docs/TASK_5B_AGENT_PLAN.md`.

Task 5B 会在真实文件解析或 RAG 之前，先准备附件智能化的业务与技术契约。规划文档位于 `docs/TASK_5B_AGENT_PLAN.md`。

The current product still treats attachments as registration records only. Future parsing results must be reviewed and accepted by the user before they can become project evidence.

当前产品仍只把附件视为登记记录。未来解析结果必须经过用户审阅和接受，才能成为项目证据。
