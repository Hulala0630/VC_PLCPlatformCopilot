# AGENT Development Context

## Working Method / 工作方式

This project uses a vibe-coding workflow.

本项目采用 vibe-coding 工作流。

The user acts as product architect and industrial automation domain expert. Codex acts as senior full-stack implementation engineer and technical architect.

用户是产品架构师与工业自动化领域专家。Codex 是资深全栈实现工程师与技术架构师。

## Current Baseline / 当前基线

The current repository has:

当前仓库已经具备：

- Frontend project-loop workstation.
- 前端项目闭环工作台。
- Frontend API integration with FastAPI.
- 前端已接入 FastAPI API。
- FastAPI backend with SQLite local persistence.
- 带 SQLite 本地持久化的 FastAPI 后端。
- Shared concepts for project, intake, preferences, attachments, benchmark, report drafts, and report sections.
- 项目、输入、偏好、附件、benchmark、报告草稿和报告分区的共享概念。

Current limits:

当前限制：

- PLC ecosystem profiles are still mock data.
- PLC 生态 profile 仍是 mock 数据。
- Attachment handling is metadata-only.
- 附件处理仅保存元信息。
- No real AI, RAG, file parsing, Excel reading, PLC connection, PLC programming, or PLC code conversion.
- 尚无真实 AI、RAG、文件解析、Excel 读取、PLC 连接、PLC 编程或 PLC 代码转换。

## Architecture / 架构

- `frontend/`: React, TypeScript, Vite, Tailwind CSS workstation UI.
- `frontend/`：React、TypeScript、Vite、Tailwind CSS 工作台界面。
- `backend/`: FastAPI backend with SQLite persistence.
- `backend/`：带 SQLite 持久化的 FastAPI 后端。
- `backend/data/plc_copilot.db`: local SQLite database, ignored by Git.
- `backend/data/plc_copilot.db`：本地 SQLite 数据库，已被 Git 忽略。
- `docs/`: product and development context.
- `docs/`：产品与开发上下文。
- `infra/`: deployment notes.
- `infra/`：部署说明。

Do not recreate the removed `apps/` prototype directory unless explicitly requested.

除非用户明确要求，不要重新创建已移除的 `apps/` 原型目录。

## Development Rules / 开发规则

- Focus on PLC decision support, not PLC programming.
- 聚焦 PLC 决策支持，不做 PLC 编程。
- Do not build PLC code conversion.
- 不做 PLC 代码转换。
- Do not build direct PLC connection.
- 不做 PLC 直连。
- Do not claim attachments were parsed before parsing/RAG is implemented.
- 在解析/RAG 未实现前，不要声称附件已被解析。
- Prefer deterministic automation for scoring, ranking, risk, and report structure.
- 评分、排序、风险和报告结构优先使用确定性自动化逻辑。
- Use AI only later for explanation, prose, follow-up questions, and section rewriting.
- AI 只在后续用于解释、文字、追问和分区重写。
- Keep API paths stable once the frontend depends on them.
- 当前端依赖 API 后，保持 API 路径稳定。
- Keep Chinese/English language switching readable and maintainable.
- 保持中英文切换可读、可维护。
- Keep the app runnable after each meaningful implementation task.
- 每个有意义的实现任务完成后保持应用可运行。

## Shared Concepts / 共享概念

These concepts should stay aligned between frontend and backend:

以下概念需要在前后端保持一致：

- `Project`
- `ProjectIntake`
- `PlatformPreference`
- `ProjectAttachment`
- `BenchmarkResult`
- `ReportDraft`
- `ReportSection`
- `ProjectWorkspace`

## Verification Expectations / 验证要求

For backend tasks:

后端任务：

- Run FastAPI smoke checks for key endpoints.
- 对关键接口运行 FastAPI smoke 检查。
- Verify persistence across repository reload or backend restart.
- 验证跨 repository reload 或后端重启的数据持久化。
- Confirm API response shape stays compatible with frontend normalization.
- 确认 API 响应形状仍与前端 normalization 兼容。

For frontend compatibility:

前端兼容性：

- Run `npm.cmd run build` in `frontend/` when feasible.
- 可行时在 `frontend/` 中运行 `npm.cmd run build`。
- Start backend and frontend preview/dev servers when useful.
- 需要时启动后端与前端预览/开发服务器。

For docs:

文档：

- Keep files readable as UTF-8.
- 保持文件以可读 UTF-8 呈现。
- Keep product boundary and current implementation state explicit.
- 明确产品边界和当前实现状态。

## Next Workstreams / 下一步工作流

1. Input/output fallback hardening.
   输入输出兜底强化。
2. Intelligence placeholder API.
   智能化占位 API。
3. Report export preparation.
   报告导出准备。
