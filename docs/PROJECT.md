## Product Vision

PLC Platform Benchmark & Migration Decision Copilot is a local-first strategic decision workspace for PLC ecosystem selection, project intake, weighted benchmarking, and consulting-style report generation.

PLC 平台基准与迁移决策副驾驶是一个本地优先的战略决策工作台，用于 PLC 生态选型、项目资料收集、带倾向权重的 benchmark 分析和咨询式报告生成。

## Product Boundary

- Not a PLC programming tool.
  不是 PLC 编程工具。
- Not a PLC code converter.
  不是 PLC 代码转换器。
- Not a direct PLC connection tool.
  不直接连接 PLC。
- The product supports strategic analysis, assumptions, recommendations, and report generation.
  产品支持战略分析、假设说明、推荐结论和报告生成。

## Current Product Loop

The current information architecture is:

当前信息架构为：

`Create Project -> Fill Lightweight Intake -> Register Attachments -> Set PLC Platform Preference -> Run Deterministic Benchmark -> Agent Explanation Placeholder -> Generate Report -> Edit Report Sections`

`创建项目 -> 填写轻量信息 -> 登记附件资料 -> 设置 PLC 平台倾向 -> 运行确定性 Benchmark -> Agent 解释占位 -> 生成报告 -> 分区调整报告`

## Implemented Modules

- Project Workspace
  - Create project.
  - Select existing project.
  - Manage project status.
- Project Intake
  - Project name, industry, goal.
  - Project size, I/O scale, motion, safety, budget sensitivity, team experience, constraints.
- Platform Preference
  - One 0-100 preference slider per PLC platform.
  - Preference participates in weighted benchmark score.
  - Technical score and preference score are displayed separately.
- Attachment Register
  - Records file name, type, declared purpose, upload date, and project association.
  - V1 does not parse files, read Excel, or run RAG.
- Benchmark Analysis
  - Deterministic ranking based on platform profile score and user preference.
  - Risk level, rationale, and assumptions are generated from rule logic.
- Report Builder
  - Report sections can be edited independently.
  - A section can be regenerated from deterministic benchmark output.

## Agent vs Automation Boundary

Deterministic automation owns:

- Form validation.
- Platform base scoring.
- User preference weighting.
- Benchmark ranking.
- First-pass risk level.
- Report structure generation.
- Attachment metadata management.

Agent behavior is currently a placeholder and will later own:

- Explaining high/low platform scores.
- Asking follow-up questions based on missing project inputs.
- Drafting report prose.
- Rewriting individual report sections.
- Stating assumptions and uncertainty.

Agent must not:

- Connect directly to PLCs.
- Generate PLC programs.
- Convert PLC code.
- Replace deterministic scoring logic.
- Parse attachments in V1.

## Current Mock PLC Ecosystems

- Siemens TIA Portal
- CODESYS
- Beckhoff TwinCAT
- Rockwell Studio 5000
- Mitsubishi GX Works
- Omron Sysmac

## Next Capabilities

- Persist projects, intake, preferences, attachments, benchmark results, and report drafts in SQLite.
- Move frontend data reads to FastAPI endpoints.
- Add real OpenAI-compatible agent service.
- Add document parsing and Chroma RAG in a later phase.
- Add PDF/PPT report export.
