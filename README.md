# PLC Platform Benchmark & Migration Decision Copilot

## API Key Setup / API 密钥配置

Never paste an API key into source code, frontend environment variables, Git commits, issues, or chat messages. Create a local `.env.local` file in the repository root and keep the real key only on your machine.

请勿将 API Key 粘贴到源代码、前端环境变量、Git 提交、Issue 或聊天消息中。请在仓库根目录创建本地 `.env.local` 文件，真实密钥只保存在你的电脑上。

```powershell
Copy-Item .env.example .env.local
notepad .env.local
```

Set these values in `.env.local` / 在 `.env.local` 中填写：

```dotenv
AI_PROVIDER=openai
OPENAI_API_KEY=replace-with-your-local-key
OPENAI_BASE_URL=https://api.openai.com/v1
AI_MODEL_FAST=your-fast-model
AI_MODEL_BALANCED=your-balanced-model
AI_MODEL_QUALITY=your-quality-model
```

`.env.local` and common private-key formats are excluded by `.gitignore`. Only `.env.example`, containing empty or non-secret example values, may be committed. If a real key is ever committed or shared, revoke it immediately and create a replacement.

`.env.local` 和常见私钥格式已被 `.gitignore` 排除。只能提交不含秘密信息的 `.env.example`。如果真实密钥曾被提交或分享，请立即撤销并重新创建密钥。

Local-first consulting workspace for PLC ecosystem selection, migration decision support, deterministic benchmarking, and report drafting.

## Product Boundary

- Decision support only, not PLC programming.
- No PLC code conversion.
- No direct PLC connection.
- V1 attachments are metadata-only.
- V1 does not parse files, read Excel content, or run RAG.
- Real OpenAI-compatible AI can be enabled from backend-only local configuration; the app also keeps a basic analysis path when AI is off or unavailable.

## Backend Source Of Truth

The FastAPI backend uses SQLite as the local source of truth for project-loop data.

- Database path: `backend/data/plc_copilot.db`
- The database directory and schema are created on backend startup.
- Initial mock projects are seeded only when the `projects` table is empty.
- PLC ecosystem profiles still live in memory.
- Projects, intakes, preferences, attachment metadata, report drafts, report sections, and project status persist across backend restarts.

## Project Status Lifecycle

Backend-owned status values:

- `Draft`
- `Analyzing`
- `Report Ready`
- `Finalized`

`Draft`, `Analyzing`, and `Report Ready` are computed from project readiness and report state. `Finalized` is user-controlled and is not overwritten by normal edits. Reopen a finalized project with `PUT /api/projects/{project_id}/status` and payload `{ "status": "Analyzing" }`.

## Readiness Scoring

`ProjectWorkspace` responses include:

- `readiness.score`
- `readiness.status`
- `readiness.missing_required`
- `readiness.recommended_missing`
- `readiness.next_action`
- `readiness.confidence_level`
- `readiness.reasons`

Required checks contribute 70%:

- Project name exists.
- Industry exists.
- Goal exists.
- I/O scale is greater than 0.
- At least two candidate platforms are selected.

Recommended checks contribute 30%:

- Team experience exists.
- Constraints exist.
- Existing platform exists.
- At least one attachment metadata record exists.
- Preferences exist for all candidate platforms.
- Report sections exist.

## Backend API

- `GET /health`
- `GET /api/ecosystems`
- `GET /api/platforms`
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
- `POST /api/benchmark`

## Intelligence Provider Foundation / 智能化 Provider 基础

The backend exposes a frozen intelligence contract backed by `DeterministicPlaceholderProvider`. It is a deterministic suggestion service, not an AI provider.

后端提供由 `DeterministicPlaceholderProvider` 实现的固定智能化契约。它是确定性建议服务，不是 AI provider。

- `POST /api/intelligence/global/chat`
- `GET /api/intelligence/status`
- `POST /api/projects/{project_id}/intelligence/chat`
- `POST /api/projects/{project_id}/intelligence/analyze`
- `POST /api/projects/{project_id}/benchmark/explain`
- `POST /api/projects/{project_id}/report/generate`
- `POST /api/projects/{project_id}/report/sections/{section_id}/rewrite`

All responses are bilingual and include sources, assumptions, uncertainty, missing inputs, and explicit provider metadata.

所有响应均包含中英双语内容、来源、假设、不确定性、缺失输入和明确的 provider 元数据。

- `mode = deterministic_placeholder`
- `ai_used = false`
- `document_parsing_used = false`
- Chat, analysis, generated drafts, and rewrite suggestions are not persisted.
- Report generation and rewrite endpoints never mutate report sections automatically.
- Benchmark explanation never changes deterministic scores.
- AI Benchmark may recommend a different candidate platform than the fixed benchmark leader as an advisory consulting conclusion, but it must preserve the fixed scores, ranking values, risk levels, charts, and baseline data.

聊天、分析、报告建议稿和改写建议均不持久化；报告生成与改写不会自动修改报告分区；Benchmark 解释不会改变确定性评分。

## Backend AI Configuration / 后端 AI 配置

AI provider configuration is loaded only by the backend. The repository-root `.env.local` is loaded explicitly, while process environment variables take precedence. `OPENAI_API_KEY` is held as `SecretStr` and is never returned by the status endpoint.

AI provider 配置仅由后端加载。系统显式读取仓库根目录 `.env.local`，且进程环境变量具有更高优先级。`OPENAI_API_KEY` 使用 `SecretStr` 保存，status endpoint 绝不会返回密钥。

Quality profiles are configured independently through `AI_MODEL_FAST`, `AI_MODEL_BALANCED`, and `AI_MODEL_QUALITY`. `GET /api/intelligence/status` returns profile names only, never concrete model IDs.

三档质量配置分别由 `AI_MODEL_FAST`、`AI_MODEL_BALANCED` 和 `AI_MODEL_QUALITY` 管理。`GET /api/intelligence/status` 只返回 profile 名称，不返回具体 model ID。

When OpenAI configuration is valid, real AI calls are available through the backend provider boundary. `DeterministicPlaceholderProvider` remains available as the basic analysis path, and deterministic benchmark scoring remains the source of truth.

当 OpenAI 配置有效时，系统可以通过后端 provider 边界调用真实 AI。`DeterministicPlaceholderProvider` 仍作为基础分析路径保留，确定性 benchmark 评分继续作为事实来源。

## OpenAI Provider And Routing / OpenAI Provider 与路由

When `AI_PROVIDER=openai` and the backend configuration is complete, the provider factory selects `OpenAIProvider`, which uses the official Python SDK and Responses API structured outputs. Incomplete configuration continues safely with the placeholder.

当 `AI_PROVIDER=openai` 且后端配置完整时，provider factory 会选择使用官方 Python SDK 与 Responses API structured outputs 的 `OpenAIProvider`。配置不完整时会安全地继续使用 placeholder。

Default quality routing:

- Global chat and connection test: `fast`
- Project chat, project analysis, and benchmark explanation: `balanced`
- Report generation and report section rewrite: `quality`

客户端只能看到 `fast/balanced/quality` profile，具体 model ID 永不出现在公开响应或日志中。

If an OpenAI call fails and fallback is enabled, responses are explicitly marked `mode=deterministic_fallback`, `provider=placeholder`, and include a sanitized `fallback_reason`. With fallback disabled, the API returns only a safe error category.

OpenAI 调用失败且启用 fallback 时，响应会明确标记为 `deterministic_fallback` 和 `provider=placeholder`，并包含脱敏后的 `fallback_reason`。关闭 fallback 时，API 只返回安全错误类别。

- `POST /api/intelligence/connection-test`
- The connection response never includes model output, model ID, API key, headers, or raw SDK errors.
- Connection test 响应绝不包含模型输出、model ID、API key、headers 或原始 SDK 错误。

## Report Output / 报告输出

- Markdown can be copied or downloaded directly from the Report workspace.
- Markdown 可以从 Report 工作区直接复制或下载。
- PDF output uses a dedicated print document and the browser's Save as PDF capability.
- PDF 输出使用专用打印文档，并通过浏览器“另存为 PDF”完成。
- PowerPoint output generates a local `.pptx` file from project, readiness, benchmark, and report data.
- PowerPoint 根据项目、成熟度、benchmark 和报告数据在本地生成 `.pptx`。
- Export remains deterministic and does not claim AI or document parsing.
- 导出仍为确定性逻辑，不声称使用 AI 或解析文档。

## Run Locally

Backend:

```powershell
cd backend
uvicorn app.main:app --reload --port 8000
```

Frontend:

```powershell
cd frontend
npm install
npm run dev
```
