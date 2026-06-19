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
- V1 does not parse files, read Excel content, run RAG, or call real AI.

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

聊天、分析、报告建议稿和改写建议均不持久化；报告生成与改写不会自动修改报告分区；Benchmark 解释不会改变确定性评分。

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
