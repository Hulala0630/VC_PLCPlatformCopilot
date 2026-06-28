# AGENT Development Context

## Working Method / 工作方式

The user is the product architect and industrial automation domain expert. Codex acts as senior full-stack implementation engineer and technical architect.

用户是产品架构师和工业自动化领域专家。Codex 作为高级全栈实现工程师和技术架构师协作。

Development should stay incremental:

开发应保持增量式：

1. Preserve existing API paths once the frontend depends on them.
2. Keep frontend/backend concepts aligned.
3. Keep deterministic backend behavior central.
4. Run local verification after implementation.
5. Report files changed, behavior changes, and remaining limits.

1. 前端依赖某个 API 后，优先保持路径稳定。
2. 保持前后端概念一致。
3. 以确定性后端行为作为事实中心。
4. 实现后运行本地验证。
5. 汇报修改文件、行为变化和剩余限制。

## Current Baseline / 当前基线

- Frontend project-loop workstation exists.
- Frontend API integration exists.
- FastAPI backend uses SQLite local persistence.
- Project deletion exists.
- Backend owns project readiness and status lifecycle.
- Frontend report preview supports Markdown, browser PDF, and local PowerPoint export.
- Real OpenAI-compatible provider integration exists behind the intelligence provider boundary.
- Prompt quality boundaries and user-safe output tests exist.

- 前端项目闭环工作台已存在。
- 前端 API 集成已存在。
- FastAPI 后端使用 SQLite 本地持久化。
- 项目删除已存在。
- 后端负责项目成熟度和状态生命周期。
- 前端报告预览支持 Markdown、浏览器 PDF 和本地 PowerPoint 导出。
- 真实 OpenAI 兼容 provider 已通过 intelligence provider 边界接入。
- Prompt 质量边界和用户安全输出测试已存在。

## Product Limits / 产品限制

Do not implement or imply:

不得实现或暗示：

- RAG in the current version.
- File parsing in the current version.
- Excel reading in the current version.
- PLC connection.
- PLC programming.
- PLC code conversion.
- AI replacement of deterministic benchmark calculations.
- Automatic persistence of AI-generated report suggestions.

- 当前版本不做 RAG。
- 当前版本不做文件解析。
- 当前版本不读取 Excel。
- 不连接 PLC。
- 不编写 PLC 程序。
- 不转换 PLC 代码。
- AI 不替代确定性 Benchmark 计算。
- AI 生成的报告建议不自动持久化。

Attachments remain metadata-only.

附件仍仅登记元信息。

## Backend Responsibilities / 后端职责

Deterministic backend automation owns:

确定性后端自动化负责：

- Project readiness scoring.
- Automatic `Draft`, `Analyzing`, and `Report Ready` status derivation.
- User-controlled `Finalized` status preservation.
- Platform scoring and benchmark ranking.
- Attachment metadata persistence.
- Report section persistence.

- 项目成熟度评分。
- 自动派生 `Draft`、`Analyzing` 和 `Report Ready` 状态。
- 保留用户控制的 `Finalized` 状态。
- 平台评分和 Benchmark 排名。
- 附件元信息持久化。
- 报告分区持久化。

## Readiness Rules / 成熟度规则

Required checks:

必要检查：

- Project name exists.
- Industry exists.
- Goal exists.
- I/O scale is greater than 0.
- At least two candidate platforms exist.

- 项目名称存在。
- 行业存在。
- 目标存在。
- I/O 规模大于 0。
- 至少有两个候选平台。

Recommended checks:

建议检查：

- Team experience exists.
- Constraints exist.
- Existing platform exists.
- At least one attachment metadata record exists.
- Preferences exist for all candidate platforms.
- Report sections exist.

- 团队经验存在。
- 约束条件存在。
- 现有平台存在。
- 至少有一条附件元信息记录。
- 所有候选平台都有偏好设置。
- 报告分区存在。

## Verification Expectations / 验证要求

Backend tasks should verify:

后端任务应验证：

- `GET /api/projects`
- `GET /api/projects/{project_id}`
- `GET /api/projects/{project_id}/readiness`
- `PUT /api/projects/{project_id}/status`
- Create, update intake, update preferences, add attachment, benchmark, update report section, finalize, reopen, delete.
- Persistence of `Finalized` across repository reload or backend restart.

- 创建项目、更新 intake、更新 preferences、添加附件、运行 benchmark、更新报告分区、定稿、重新打开、删除。
- `Finalized` 在 repository reload 或后端重启后仍保留。

Frontend compatibility should be checked with `npm.cmd run build` when feasible.

可行时应使用 `npm.cmd run build` 检查前端兼容性。

## Intelligence Provider Rules / 智能化 Provider 规则

- Keep contracts in `backend/app/intelligence/models.py`.
- Keep provider implementations behind `IntelligenceProvider`.
- Keep context assembly and project boundaries in the intelligence service.
- Keep intelligence route handlers thin.
- Do not call deterministic baseline analysis "AI".
- Do not persist chat history, analysis responses, generated drafts, or rewrite suggestions automatically.
- Do not let provider output replace benchmark calculations or mutate intake/report data automatically.
- Always state that attachment metadata may be registered while file content was not parsed.
- AI benchmark analysis may recommend a candidate platform that differs from the fixed benchmark leader when migration continuity, installed base, team capability, downtime risk, lifecycle strategy, or business constraints justify it.
- This disagreement must be presented as an engineering review item. It must not change benchmark scores, ranking values, risk levels, charts, project inputs, preferences, or report content unless the user explicitly edits or accepts changes.
- Reject AI benchmark output when it recommends a platform outside the supplied benchmark candidates or violates the user-safe output boundary.

- 契约集中在 `backend/app/intelligence/models.py`。
- Provider 实现必须位于 `IntelligenceProvider` 边界之后。
- 项目上下文组装和业务边界放在 intelligence service。
- Intelligence route handler 保持轻薄。
- 不得把确定性基础分析称为 AI。
- 不自动持久化聊天历史、分析结果、生成建议稿或改写建议。
- Provider 输出不得替代 Benchmark 计算，也不得自动修改 intake 或 report。
- 必须明确说明附件只登记元信息，文件内容未被解析。

## AI Configuration Safety / AI 配置安全

- Business services must not read `os.environ` directly; use the cached settings dependency.
- Load repository-root `.env.local` explicitly so behavior does not depend on shell working directory.
- Process environment variables override `.env.local`.
- Keep `OPENAI_API_KEY` as `SecretStr` and exclude it from serialization and logs.
- Public status responses may expose only provider, configured state, profile names, fallback state, and safe errors.
- Never expose API key value, fragments, length, authorization headers, model IDs, or environment dumps.
- Tests must use fake process values or temporary env files only.
- Deterministic benchmark calculations remain the source of truth and must not be replaced by provider output.

- 业务 service 不得直接读取 `os.environ`，必须使用缓存的 settings dependency。
- 必须显式加载仓库根目录 `.env.local`，避免行为依赖 shell 工作目录。
- 进程环境变量优先于 `.env.local`。
- `OPENAI_API_KEY` 必须使用 `SecretStr`，并从序列化和日志中排除。
- 公开状态只能包含 provider、configured、profile 名称、fallback 和安全错误。
- 禁止暴露 key 内容、片段、长度、Authorization header、model ID 或完整环境变量。
- 测试只能使用 fake process values 或临时 env 文件。
- 确定性 Benchmark 始终是事实来源，provider 输出不得替代其计算。

## OpenAI Provider Runtime Rules / OpenAI Provider 运行规则

- Keep all SDK-specific calls inside `openai_provider.py`.
- Use `ModelRouter`; never branch on concrete model IDs in routes or business services.
- Use Responses API structured parsing and validate every parsed result.
- Retry only safe transient categories according to `AI_MAX_RETRIES`.
- Never expose raw SDK errors; map them to safe categories.
- Fallback responses must be explicit and user-safe.
- Fallback-disabled failures return a sanitized API error only.
- Report generation/rewrite must not mutate SQLite automatically.
- Automated tests mock every SDK call and use fake credentials only.
- Live tests may use an already-present ignored local configuration but must never print or copy its secrets.

- 所有 SDK 调用必须隔离在 `openai_provider.py`。
- 必须通过 `ModelRouter` 路由；route/business service 不得依赖具体 model ID。
- 使用 Responses API structured parsing，并校验每个解析结果。
- 仅按 `AI_MAX_RETRIES` 重试安全的瞬时错误。
- 原始 SDK 错误不得暴露，必须映射为安全类别。
- 兜底响应必须明确且对用户安全。
- 关闭 fallback 时只能返回脱敏 API 错误。
- 报告生成和改写不得自动修改 SQLite。
- 自动测试必须 mock 所有 SDK 调用，并只使用 fake credential。
- Live test 可以使用已存在且被忽略的本地配置，但绝不能打印或复制 secret。

## Prompt Quality Rules / Prompt 质量规则

- AI should write like a senior industrial automation consultant.
- User-facing answers must distinguish facts, assumptions, uncertainties, and recommendations.
- Attachment files have not been opened, parsed, read, summarized, or understood.
- Benchmark scores, rankings, risk levels, and readiness values are fixed source facts.
- AI may challenge the first-ranked benchmark platform as an advisory recommendation, but only in business/engineering language and only while preserving the fixed source facts.
- Report generation must preserve supplied section IDs, titles, and order.
- Report section rewrite must return only the requested section.
- User-facing fields must not expose implementation terms such as placeholder, provider, fallback, model id, API key, metadata, persistence, or scoring logic.

- AI 应像高级工业自动化咨询顾问一样表达。
- 面向用户的回答必须区分事实、假设、不确定性和建议。
- 附件文件没有被打开、解析、读取、总结或理解。
- Benchmark 分数、排名、风险等级和成熟度是固定事实来源。
- 报告生成必须保留传入的 section ID、标题和顺序。
- 报告分区改写只能返回目标分区。
- 面向用户字段不得暴露 placeholder、provider、fallback、model id、API key、metadata、persistence、scoring logic 等实现术语。

## User-Safe Intelligence Messaging / 用户安全文案

- Keep `execution_status`, public fallback reason, retryability, and request ID consistent across every intelligence response shape.
- Map SDK/provider diagnostics to the public fallback enum in the service layer.
- Keep implementation terminology out of answers, assumptions, uncertainty, and report suggestions.
- Describe attachment, scoring, and report boundaries in business language.
- Reject structured AI output containing internal implementation language and retry or fall back safely.

- 所有 intelligence response shape 必须统一执行状态、公开兜底原因、可重试性和 request ID。
- SDK 诊断信息必须在 service 层映射到公开枚举。
- answer、assumptions、uncertainty 和报告建议不得出现内部实现术语。
- 附件、评分和报告边界应使用业务语言表达。
- AI structured output 若包含内部实现文案，必须拒绝并安全重试或兜底。

## Task 5B Planning Boundary / Task 5B 规划边界

Task 5B is an Agent/architecture planning phase before implementation. Use `docs/TASK_5B_AGENT_PLAN.md` as the source of truth for attachment intelligence planning.

Task 5B 是实现前的 Agent/架构规划阶段。附件智能化规划以 `docs/TASK_5B_AGENT_PLAN.md` 为事实来源。

Do not implement RAG, Excel parsing, PDF parsing, or Chroma before the attachment classification, expected extraction schema, user review workflow, and deterministic/agent boundary are agreed.

在附件分类、预期提取 schema、用户审阅流程、确定性逻辑与 Agent 边界明确之前，不要实现 RAG、Excel 解析、PDF 解析或 Chroma。

## MVP Engineer Trial Target / 工程师试用 MVP 目标

The current delivery target is `MVP v0.1 Engineer Trial Ready` by 2026-06-30. Use `docs/MVP_ENGINEER_TRIAL.md` as the acceptance checklist.

当前交付目标是在 2026-06-30 前达到 `MVP v0.1 Engineer Trial Ready`。验收清单以 `docs/MVP_ENGINEER_TRIAL.md` 为准。

Prioritize demo stability, sample-project clarity, benchmark explainability, AI/basic-analysis usability, and report export quality over new feature expansion.

优先级应放在演示稳定性、样例项目清晰度、Benchmark 可解释性、AI/基础分析可用性和报告导出质量上，而不是继续扩大功能范围。
