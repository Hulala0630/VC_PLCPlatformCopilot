# PLC Platform Benchmark & Migration Decision Copilot

## Product Vision / 产品愿景

PLC Platform Benchmark & Migration Decision Copilot is a local-first strategic decision workspace for PLC ecosystem selection, project intake, weighted benchmarking, and consulting-style report drafting.

PLC Platform Benchmark & Migration Decision Copilot 是一个本地优先的 PLC 平台选型与迁移决策工作台，用于项目资料收集、平台偏好加权 benchmark、迁移风险判断，以及咨询式报告生成。

The product helps engineers, technical managers, consultants, and decision makers answer questions such as:

本产品帮助自动化工程师、技术经理、咨询顾问和决策者回答以下问题：

- Which PLC ecosystem should we choose for a new project?
- 新项目应该选择哪个 PLC 生态？
- What are the trade-offs between Siemens, TwinCAT, CODESYS, Rockwell, Mitsubishi, and Omron?
- Siemens、TwinCAT、CODESYS、Rockwell、Mitsubishi、Omron 等平台之间有什么取舍？
- What would it cost and risk to migrate from one platform to another?
- 从一个 PLC 平台迁移到另一个平台的成本和风险是什么？
- How mature is the current project for selection or migration?
- 当前项目对于选型或迁移的成熟度如何？
- What assumptions and uncertainties should be visible before making a decision?
- 在做决策前，应明确哪些假设和不确定性？

## Product Boundary / 产品边界

- This is a decision-support platform, not a PLC programming tool.
- 这是决策支持平台，不是 PLC 编程工具。
- This is not a PLC code converter.
- 这不是 PLC 代码转换工具。
- This does not directly connect to PLCs.
- 当前产品不直接连接 PLC。
- V1 does not parse uploaded files, read Excel content, run RAG, or call a real AI model.
- V1 不解析上传文件、不读取 Excel 内容、不运行 RAG、不调用真实 AI 模型。
- Deterministic automation owns scoring, ranking, risk labels, and report structure.
- 确定性自动化逻辑负责评分、排序、风险标签和报告结构。
- Agent behavior is reserved for explanations, follow-up questions, and report prose.
- Agent 能力预留给解释、追问和报告文字生成。

## Current Repo Baseline / 当前仓库基线

Current merged baseline:

当前已合并基线：

- Frontend workstation implemented with React, TypeScript, Vite, and Tailwind CSS.
- 前端工作台已用 React、TypeScript、Vite 和 Tailwind CSS 实现。
- Mock FastAPI backend has been merged into `master`.
- Mock FastAPI 后端已经合并进 `master`。
- The frontend still primarily uses local mock state.
- 前端当前仍主要使用本地 mock 状态。
- The backend exposes mock in-memory APIs that define the future source-of-truth shape.
- 后端提供内存态 mock API，用于定义未来事实数据源的接口形状。
- No SQLite persistence has been implemented yet.
- 尚未实现 SQLite 持久化。
- No real AI, RAG, or document parsing has been implemented yet.
- 尚未实现真实 AI、RAG 或文档解析。

## Current Product Loop / 当前产品闭环

The current information architecture is:

当前信息架构为：

`Create Project -> Fill Intake -> Register Attachments -> Set Platform Preferences -> Run Benchmark -> Review Agent Placeholder -> Edit Report Sections`

`创建项目 -> 填写项目信息 -> 登记附件元信息 -> 设置平台偏好 -> 运行 Benchmark -> 查看 Agent 占位解释 -> 编辑报告分区`

## Implemented Modules / 已实现模块

### Project Workspace / 项目工作台

- Create a new project.
- 创建新项目。
- Select an existing project.
- 选择已有项目。
- View project status and workflow progress.
- 查看项目状态与流程进度。

### Project Intake / 项目输入

- Project name, industry, goal, current platform, candidate platforms.
- 项目名称、行业、目标、现有平台、候选平台。
- Project size, I/O scale, motion requirement, safety requirement, budget sensitivity, team experience, and constraints.
- 项目规模、I/O 规模、运动控制需求、安全需求、预算敏感度、团队经验和约束条件。

### Platform Preference / 平台倾向性

- One 0-100 preference slider per PLC platform.
- 每个 PLC 平台一个 0-100 偏好滑块。
- Preference participates in weighted benchmark scoring.
- 平台偏好参与加权 benchmark 评分。
- Technical score and preference score are displayed separately.
- 技术评分和用户偏好评分分开展示。

### Attachment Register / 附件登记

- Records file name, file type, declared purpose, upload date, and project association.
- 记录文件名、文件类型、声明用途、登记日期和关联项目。
- V1 stores metadata only.
- V1 仅保存附件元信息。
- V1 does not parse files or claim to understand uploaded document content.
- V1 不解析文件，也不声称已理解上传文档内容。

### Benchmark Analysis / Benchmark 分析

- Deterministic ranking based on platform profile scores and user preference weights.
- 基于平台基础评分和用户偏好权重进行确定性排序。
- Outputs technical score, preference score, weighted score, risk level, rationale, and assumptions.
- 输出技术评分、偏好评分、加权评分、风险等级、理由和假设。

### Report Builder / 报告构建器

- Report sections can be edited independently.
- 报告分区可以独立编辑。
- A section can be regenerated from deterministic benchmark output.
- 单个报告分区可以基于确定性 benchmark 输出重新生成。
- Current report generation is still mock and rule-based.
- 当前报告生成仍是 mock 与规则驱动。

## Current Mock PLC Ecosystems / 当前 Mock PLC 生态

- Siemens TIA Portal
- CODESYS
- Beckhoff TwinCAT
- Rockwell Studio 5000
- Mitsubishi GX Works
- Omron Sysmac

## Agent vs Automation Boundary / Agent 与自动化边界

Deterministic automation owns:

确定性自动化负责：

- Form validation.
- 表单校验。
- Platform base scoring.
- 平台基础评分。
- User preference weighting.
- 用户偏好加权。
- Benchmark ranking.
- Benchmark 排名。
- First-pass risk level.
- 初步风险等级。
- Engineering effort index in later phases.
- 后续阶段的工程量指数。
- Report structure generation.
- 报告结构生成。
- Attachment metadata management.
- 附件元信息管理。

Agent behavior will later own:

Agent 后续负责：

- Explaining why a platform scored high or low.
- 解释某个平台为何得分高或低。
- Asking follow-up questions based on missing inputs.
- 基于缺失输入提出追问。
- Drafting report prose.
- 生成报告文字草稿。
- Rewriting individual report sections.
- 重写单个报告分区。
- Stating assumptions and uncertainty clearly.
- 清楚说明假设和不确定性。

Agent must not:

Agent 不允许：

- Connect directly to PLCs.
- 直接连接 PLC。
- Generate PLC programs.
- 生成 PLC 程序。
- Convert PLC code.
- 转换 PLC 代码。
- Replace deterministic scoring logic.
- 替代确定性评分逻辑。
- Claim to parse attachments before parsing/RAG is implemented.
- 在解析/RAG 未实现前声称已解析附件。

## Next Development Milestones / 下一阶段里程碑

1. Documentation baseline repair.
   修复文档基线，确保中英双语内容可读。
2. Frontend API integration.
   前端接入 FastAPI mock backend，同时保留本地 mock fallback。
3. SQLite persistence.
   后端加入 SQLite，保存项目、输入、偏好、附件元信息和报告草稿。
4. Input/output fallback hardening.
   完善缺失字段、空状态、假设、不确定性和报告兜底逻辑。
5. Intelligence placeholder API.
   建立智能化接口边界，先返回 deterministic mock 文案。
6. Future RAG and agent workflows.
   后续再接入文档解析、Chroma、LangGraph 和真实 OpenAI-compatible API。
