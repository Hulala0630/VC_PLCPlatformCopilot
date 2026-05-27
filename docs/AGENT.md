## Development Context

This project uses a vibe-coding workflow.

本项目采用 vibe-coding 工作流。

The user is product architect and industrial automation domain expert. Codex is senior full-stack implementation engineer and technical architect.

用户是产品架构师与工业自动化领域专家。Codex 是资深全栈实现工程师与技术架构师。

## Current Baseline

The current baseline implements the project-loop information architecture:

当前基线实现项目闭环信息架构：

- Create project.
- Fill lightweight project intake.
- Register attachment metadata.
- Set PLC platform preference weights.
- Run deterministic benchmark.
- Keep agent behavior as explanation/report placeholder.
- Generate and edit report sections.

## Architecture

- `frontend/`: React, TypeScript, Vite, Tailwind CSS workstation UI.
- `backend/`: FastAPI API skeleton with ecosystem, project, and benchmark endpoints.
- `docs/`: Product and development context.
- `infra/`: Deployment notes.

Do not recreate the removed `apps/` prototype directory unless explicitly requested.

## Development Rules

- Focus on decision support, not PLC programming.
- Do not build PLC code conversion.
- Do not build direct PLC connection.
- Prefer deterministic automation for scoring, ranking, risk, and report structure.
- Use agent behavior for explanation, prose, follow-up questions, and section rewriting.
- V1 attachment handling is metadata-only.
- Keep Chinese/English language switch behavior.
- Keep the app runnable after each meaningful change.

## Current Shared Concepts

- `Project`
- `ProjectIntake`
- `PlatformPreference`
- `ProjectAttachment`
- `BenchmarkResult`
- `ReportDraft`

These concepts should remain aligned between frontend and backend as implementation moves from mock data to API-backed data.

## Workstream Split

后续开发拆成四个独立计划来推进。每个计划都应保持当前产品边界：这是 PLC 决策支持 Copilot，不是 PLC 编程、代码转换或 PLC 直连工具。

The future work is split into four independent workstreams. Each workstream must preserve the current product boundary: this is a PLC decision-support Copilot, not a PLC programming, code conversion, or direct PLC connection tool.

### 1. Frontend & Interaction Design / 前端与交互设计

Goal:

目标：

- Make the project-loop workstation clear, smooth, and executive-grade.
- 让项目闭环工作台清晰、顺滑，并具备咨询式高级感。

Responsibilities:

职责：

- Project workspace layout.
- 项目工作台布局。
- Left PLC ecosystem sidebar and project Query panel.
- 左侧 PLC 生态侧边栏与项目 Query 面板。
- Main tabs: Overview, Intake, Preferences, Attachments, Benchmark, Report.
- 主区 Tabs：Overview、Intake、Preferences、Attachments、Benchmark、Report。
- Language switch UX.
- 中英文切换体验。
- Report section editing experience.
- 报告分区编辑体验。
- Visual hierarchy for benchmark, risk, assumptions, and recommendation.
- Benchmark、风险、假设与推荐结论的视觉层级。

Success Criteria:

成功标准：

- A user can understand the full workflow without reading documentation.
- 用户不读文档也能理解完整流程。
- Project creation, intake, preference sliders, attachment register, benchmark, and report editing feel like one continuous flow.
- 新建项目、填写信息、倾向滑块、附件登记、benchmark 和报告编辑形成连续流程。
- The UI remains usable in both Chinese and English.
- 中英文状态下界面都可读可用。

### 2. Backend Project Overview / 后端项目总览

Goal:

目标：

- Turn the backend from skeleton APIs into the source of truth for project-loop data.
- 将后端从 API 骨架升级为项目闭环数据的事实来源。

Responsibilities:

职责：

- Project APIs.
- 项目 API。
- PLC ecosystem APIs.
- PLC 生态 API。
- Intake, preference, attachment metadata, benchmark, and report draft APIs.
- Intake、倾向权重、附件元信息、benchmark 与报告草稿 API。
- SQLite persistence design.
- SQLite 持久化设计。
- Backend-owned deterministic benchmark service.
- 后端负责的确定性 benchmark 服务。
- Keep frontend/backend shared concepts aligned.
- 保持前后端共享概念一致。

Success Criteria:

成功标准：

- Frontend can load and update project-loop data through FastAPI.
- 前端可通过 FastAPI 加载与更新项目闭环数据。
- API shapes match `Project`, `ProjectIntake`, `PlatformPreference`, `ProjectAttachment`, `BenchmarkResult`, and `ReportDraft`.
- API 结构与上述共享模型一致。
- Mock data can be replaced by SQLite without redesigning the UI.
- Mock 数据可替换为 SQLite，而不需要重做 UI。

### 3. Input / Output Fallbacks / 输入输出兜底

Goal:

目标：

- Make the app robust when information is incomplete, documents are not parsed, AI is unavailable, or report generation is partial.
- 当信息不完整、文档未解析、AI 不可用或报告生成不完整时，应用仍然稳健可用。

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
- Export-ready report structure, even before PDF/PPT exists.
- 在 PDF/PPT 未实现前，也保持报告结构可输出。

Success Criteria:

成功标准：

- Users always see what is missing and what assumption is being used.
- 用户始终能看到缺失信息和当前使用的假设。
- No workflow depends on real AI, RAG, Excel parsing, or PLC connection in V1.
- V1 没有任何流程依赖真实 AI、RAG、Excel 解析或 PLC 连接。
- The product remains useful with partial project information.
- 即使项目信息不完整，产品仍有价值。

### 4. Intelligence Layer / 智能化

Goal:

目标：

- Add AI only where it improves explanation, follow-up questions, report prose, and document-grounded reasoning.
- 只在解释、追问、报告文字和文档依据推理上增加 AI。

Responsibilities:

职责：

- OpenAI-compatible chat service.
- OpenAI-compatible 聊天服务。
- Agent prompt boundaries.
- Agent 提示词边界。
- Explain benchmark scores without replacing deterministic scoring.
- 解释 benchmark 得分，但不替代确定性评分。
- Suggest missing inputs and follow-up questions.
- 建议缺失输入和追问。
- Rewrite individual report sections.
- 重写单个报告分区。
- Future document parsing and Chroma RAG.
- 未来文档解析与 Chroma RAG。
- Future LangGraph workflows.
- 未来 LangGraph 工作流。

Success Criteria:

成功标准：

- AI outputs are grounded in project inputs, benchmark results, assumptions, and attached metadata.
- AI 输出基于项目输入、benchmark 结果、假设和附件元信息。
- AI never claims to have parsed documents unless parsing/RAG is actually implemented.
- 除非已经实现解析/RAG，否则 AI 不声称已读取文件内容。
- AI never generates PLC code or conversion logic.
- AI 不生成 PLC 代码或转换逻辑。

## Cross-Workstream Rule

跨工作流规则：

- Each workstream should remain independently plannable and implementable.
- 每个工作流都应能独立规划和实现。
- Keep the app runnable after each completed task.
- 每次任务完成后保持应用可运行。
- After each implementation task, start the frontend/backend preview when possible and provide the preview URL.
- 每次实现任务结束后，尽可能启动前后端预览，并提供预览地址。
