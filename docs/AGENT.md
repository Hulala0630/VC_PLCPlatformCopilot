# AGENT Development Context

## Working Method

The user is the product architect and industrial automation domain expert. Codex acts as senior full-stack implementation engineer and technical architect.

Development should stay incremental:

1. Preserve existing API paths once the frontend depends on them.
2. Keep frontend/backend concepts aligned.
3. Keep deterministic backend behavior central.
4. Run local verification after implementation.
5. Report files changed, behavior changes, and remaining limits.

## Current Baseline

- Frontend project-loop workstation exists.
- Frontend API integration exists.
- FastAPI backend uses SQLite local persistence.
- Project deletion exists.
- Backend now owns project readiness and status lifecycle.
- Frontend report preview supports Markdown, browser PDF, and local PowerPoint export.
- 前端报告预览支持 Markdown、浏览器 PDF 和本地 PowerPoint 导出。

## Product Limits

Do not implement or imply:

- Real AI
- RAG
- File parsing
- Excel reading
- PLC connection
- PLC programming
- PLC code conversion

Attachments remain metadata-only.

## Backend Responsibilities

Deterministic backend automation owns:

- Project readiness scoring.
- Automatic `Draft`, `Analyzing`, and `Report Ready` status derivation.
- User-controlled `Finalized` status preservation.
- Platform scoring and benchmark ranking.
- Attachment metadata persistence.
- Report section persistence.

## Readiness Rules

Required checks:

- Project name exists.
- Industry exists.
- Goal exists.
- I/O scale is greater than 0.
- At least two candidate platforms exist.

Recommended checks:

- Team experience exists.
- Constraints exist.
- Existing platform exists.
- At least one attachment metadata record exists.
- Preferences exist for all candidate platforms.
- Report sections exist.

## Verification Expectations

Backend tasks should verify:

- `GET /api/projects`
- `GET /api/projects/{project_id}`
- `GET /api/projects/{project_id}/readiness`
- `PUT /api/projects/{project_id}/status`
- Create, update intake, update preferences, add attachment, benchmark, update report section, finalize, reopen, delete.
- Persistence of `Finalized` across repository reload or backend restart.

Frontend compatibility should be checked with `npm.cmd run build` when feasible.

## Intelligence Provider Rules / 智能化 Provider 规则

- Keep contracts in `backend/app/intelligence/models.py`.
- Keep provider implementations behind `IntelligenceProvider`.
- Keep context assembly and project boundaries in the intelligence service.
- Keep intelligence route handlers thin.
- Do not call the deterministic placeholder AI.
- Do not persist chat history, analysis responses, generated drafts, or rewrite suggestions.
- Do not let provider output replace benchmark calculations or mutate intake/report data.
- Always state that attachment metadata may be registered while file content was not parsed.

- 契约集中在 `backend/app/intelligence/models.py`。
- Provider 实现必须位于 `IntelligenceProvider` 边界之后。
- 项目上下文组装和业务边界放在 intelligence service。
- Intelligence route handler 保持轻薄。
- 不得把 deterministic placeholder 称为 AI。
- 不持久化聊天历史、分析结果、生成建议稿或改写建议。
- Provider 输出不得替代 benchmark 计算，也不得自动修改 intake 或 report。
- 必须明确说明附件只登记 metadata，文件内容未被解析。
