# AGENT Development Context

## Working Method / 工作方式

This project uses a vibe-coding workflow.

本项目采用 vibe-coding 工作流。

The user acts as product architect and industrial automation domain expert. Codex acts as senior full-stack implementation engineer and technical architect.

用户是产品架构师与工业自动化领域专家。Codex 是资深全栈实现工程师与技术架构师。

Development proceeds incrementally:

开发按增量方式推进：

1. Clarify requirements.
   明确需求。
2. Implement the smallest useful slice.
   实现最小但有价值的功能切片。
3. Keep the app runnable.
   保持应用可运行。
4. Run local verification.
   进行本地验证。
5. Explain decisions and next steps.
   解释架构决策和下一步。

## Current Baseline / 当前基线

The current repository has merged:

当前仓库已合并：

- Frontend project-loop workstation.
- 前端项目闭环工作台。
- Mock FastAPI backend API workflow.
- Mock FastAPI 后端 API 工作流。
- Shared conceptual models for project, intake, preferences, attachments, benchmark, and report drafts.
- 项目、输入、偏好、附件、benchmark 和报告草稿的共享概念模型。

Current limitation:

当前限制：

- Frontend still primarily uses local mock state.
- 前端仍主要使用本地 mock 状态。
- Backend data is in-memory only.
- 后端数据仅保存在内存中。
- No SQLite persistence yet.
- 尚无 SQLite 持久化。
- No real AI, RAG, file parsing, or PLC connection.
- 尚无真实 AI、RAG、文件解析或 PLC 连接。

## Architecture / 架构

- `frontend/`: React, TypeScript, Vite, Tailwind CSS workstation UI.
- `frontend/`：React、TypeScript、Vite、Tailwind CSS 工作台界面。
- `backend/`: FastAPI mock backend with ecosystem, project, benchmark, attachment metadata, and report section endpoints.
- `backend/`：FastAPI mock 后端，包含生态、项目、benchmark、附件元信息和报告分区接口。
- `docs/`: Product and development context.
- `docs/`：产品与开发上下文。
- `infra/`: Deployment notes and Docker-related structure.
- `infra/`：部署说明与 Docker 相关结构。

Do not recreate the removed `apps/` prototype directory unless explicitly requested.

除非用户明确要求，不要重新创建已移除的 `apps/` 原型目录。

## Development Rules / 开发规则

- Focus on decision support, not PLC programming.
- 聚焦决策支持，不做 PLC 编程。
- Do not build PLC code conversion.
- 不做 PLC 代码转换。
- Do not build direct PLC connection.
- 不做 PLC 直连。
- Prefer deterministic automation for scoring, ranking, risk, and report structure.
- 评分、排序、风险和报告结构优先使用确定性自动化逻辑。
- Use agent behavior only for explanation, prose, follow-up questions, and section rewriting.
- Agent 只用于解释、文字生成、追问和报告分区改写。
- V1 attachment handling is metadata-only.
- V1 附件处理仅登记元信息。
- Keep Chinese/English language switching readable and maintainable.
- 保持中英文切换可读、可维护。
- Keep the app runnable after each meaningful implementation task.
- 每个有意义的实现任务完成后保持应用可运行。
- After implementation tasks, start the frontend/backend preview when feasible and provide the preview URL.
- 实现任务完成后，尽可能启动前后端预览并提供 URL。

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

## Workstream Split / 工作流拆分

The next stage is split into four implementation workstreams. Each workstream must preserve the product boundary: this is a PLC decision-support Copilot, not a PLC programming, code conversion, or direct PLC connection tool.

下一阶段拆成四个实现工作流。每个工作流都必须遵守产品边界：这是 PLC 决策支持 Copilot，不是 PLC 编程、代码转换或 PLC 直连工具。

### 1. Frontend & Interaction Design / 前端与交互设计

Goal:

目标：

- Turn the current functional workstation into a clear, smooth, executive-grade consulting interface.
- 将当前可用工作台提升为清晰、顺滑、具有咨询式高级感的界面。

Responsibilities:

职责：

- Project workspace layout.
- 项目工作台布局。
- Left PLC ecosystem sidebar and current project Query panel.
- 左侧 PLC 生态侧边栏与当前项目 Query 面板。
- Main tabs: Overview, Intake, Preferences, Attachments, Benchmark, Report.
- 主区 Tabs：Overview、Intake、Preferences、Attachments、Benchmark、Report。
- Project creation and project selection flow.
- 项目创建与项目选择流程。
- Language switch UX.
- 中英文切换体验。
- Benchmark, risk, assumptions, and recommendation hierarchy.
- Benchmark、风险、假设和推荐结论的视觉层级。
- Report section editing experience.
- 报告分区编辑体验。

Success criteria:

成功标准：

- Users can understand the full workflow without reading documentation.
- 用户不读文档也能理解完整流程。
- Project creation, intake, preference sliders, attachment register, benchmark, and report editing feel like one continuous flow.
- 新建项目、填写信息、偏好滑块、附件登记、benchmark 和报告编辑形成连续流程。
- UI remains usable in Chinese and English.
- 中英文状态下界面都可读可用。

### 2. Backend Project Overview / 后端项目总览

Goal:

目标：

- Turn the backend into the source of truth for project-loop data.
- 将后端升级为项目闭环数据的事实来源。

Responsibilities:

职责：

- Project APIs.
- 项目 API。
- PLC ecosystem APIs.
- PLC 生态 API。
- Intake, preference, attachment metadata, benchmark, and report draft APIs.
- Intake、偏好、附件元信息、benchmark 和报告草稿 API。
- SQLite persistence design and implementation.
- SQLite 持久化设计与实现。
- Backend-owned deterministic benchmark service.
- 后端负责确定性 benchmark 服务。
- Keep frontend/backend shared concepts aligned.
- 保持前后端共享概念一致。

Success criteria:

成功标准：

- Frontend can load and update project-loop data through FastAPI.
- 前端可以通过 FastAPI 加载和更新项目闭环数据。
- API shapes match shared concepts.
- API 结构与共享概念一致。
- Mock data can be replaced by SQLite without redesigning the UI.
- Mock 数据可以替换为 SQLite，而不需要重做 UI。

### 3. Input / Output Fallbacks / 输入输出兜底

Goal:

目标：

- Make the app robust when information is incomplete, documents are not parsed, AI is unavailable, or report generation is partial.
- 当信息不完整、文档未解析、AI 不可用或报告生成不完整时，应用仍然稳定可用。

Responsibilities:

职责：

- Empty states and missing-field guidance.
- 空状态与缺失字段提示。
- Attachment metadata-only behavior.
- 附件仅登记元信息的行为。
- Deterministic fallback when AI is unavailable.
- AI 不可用时的确定性兜底。
- Benchmark assumptions and uncertainty display.
- Benchmark 假设与不确定性展示。
- Report section regeneration fallback.
- 报告分区重算兜底。
- Export-ready report structure before PDF/PPT exists.
- 在 PDF/PPT 未实现前保持报告结构接近可导出状态。

Success criteria:

成功标准：

- Users always see what is missing and what assumption is being used.
- 用户始终能看到缺失信息和当前采用的假设。
- No V1 workflow depends on real AI, RAG, Excel parsing, or PLC connection.
- V1 没有任何流程依赖真实 AI、RAG、Excel 解析或 PLC 连接。
- The product remains useful with partial project information.
- 即使项目信息不完整，产品仍有价值。

### 4. Intelligence Layer / 智能化

Goal:

目标：

- Add AI only where it improves explanations, follow-up questions, report prose, and future document-grounded reasoning.
- 只在解释、追问、报告文字和未来文档依据推理上增加 AI。

Responsibilities:

职责：

- OpenAI-compatible chat service.
- OpenAI-compatible 聊天服务。
- Agent prompt boundaries.
- Agent 提示词边界。
- Explain benchmark scores without replacing deterministic scoring.
- 解释 benchmark 得分，但不替代确定性评分。
- Suggest missing inputs and follow-up questions.
- 建议缺失输入和追问问题。
- Rewrite individual report sections.
- 重写单个报告分区。
- Future document parsing and Chroma RAG.
- 后续文档解析与 Chroma RAG。
- Future LangGraph workflows.
- 后续 LangGraph 工作流。

Success criteria:

成功标准：

- AI outputs are grounded in project inputs, benchmark results, assumptions, and attached metadata.
- AI 输出基于项目输入、benchmark 结果、假设和附件元信息。
- AI never claims to have parsed documents unless parsing/RAG is actually implemented.
- 除非已经实现解析/RAG，否则 AI 不声称已经读取文档内容。
- AI never generates PLC code or conversion logic.
- AI 不生成 PLC 代码或转换逻辑。

## Recommended Next Tasks / 推荐下一步任务

1. Frontend API integration.
   前端接入 FastAPI mock backend，并保留 mock fallback。
2. Backend SQLite persistence.
   后端加入 SQLite 持久化。
3. Input/output fallback hardening.
   加强缺失字段、空状态、假设、不确定性和报告兜底。
4. Intelligence placeholder API.
   建立智能化接口占位层，先不接真实模型。

## Verification Expectations / 验证要求

For frontend tasks:

前端任务：

- Run `npm.cmd run build` in `frontend/`.
- 在 `frontend/` 中运行 `npm.cmd run build`。
- Start the Vite preview/dev server when possible.
- 尽可能启动 Vite 预览或开发服务器。

For backend tasks:

后端任务：

- Run FastAPI smoke checks for key endpoints.
- 对关键接口运行 FastAPI smoke 检查。
- Keep API responses deterministic.
- 保持 API 响应确定性。

For docs-only tasks:

纯文档任务：

- Confirm files render as readable UTF-8.
- 确认文件以可读 UTF-8 内容呈现。
- Confirm repository status before committing.
- 提交前确认仓库状态。
