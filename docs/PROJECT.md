# PLC Platform Benchmark & Migration Decision Copilot

## Product Vision / 产品愿景

This project is a local-first strategic decision workspace for PLC ecosystem selection, project intake, weighted benchmarking, migration-risk discussion, and consulting-style report drafting.

本项目是一个本地优先的战略决策工作台，用于 PLC 生态选型、项目输入、偏好加权 benchmark、迁移风险讨论和咨询式报告草稿生成。

It helps engineers, technical managers, consultants, and decision makers compare ecosystems such as Siemens TIA Portal, CODESYS, Beckhoff TwinCAT, Rockwell Studio 5000, Mitsubishi GX Works, and Omron Sysmac.

它帮助工程师、技术经理、咨询顾问和决策者比较 Siemens TIA Portal、CODESYS、Beckhoff TwinCAT、Rockwell Studio 5000、Mitsubishi GX Works、Omron Sysmac 等 PLC 生态。

## Product Boundary / 产品边界

- Decision support only, not PLC programming.
- 仅用于决策支持，不做 PLC 编程。
- No PLC code conversion.
- 不做 PLC 代码转换。
- No direct PLC connection.
- 不直接连接 PLC。
- V1 attachments are metadata-only.
- V1 附件仅保存元信息。
- V1 does not parse uploaded files, read Excel content, run RAG, or call real AI.
- V1 不解析上传文件、不读取 Excel 内容、不运行 RAG、不调用真实 AI。
- Deterministic automation owns scoring, ranking, risk labels, and report structure.
- 确定性自动化负责评分、排序、风险标签和报告结构。

## Current Product Loop / 当前产品闭环

`Create Project -> Fill Intake -> Register Attachments -> Set Platform Preferences -> Run Benchmark -> Review Rationale -> Edit Report Sections`

`创建项目 -> 填写输入 -> 登记附件 -> 设置平台偏好 -> 运行 Benchmark -> 查看理由 -> 编辑报告分区`

## Current Backend State / 当前后端状态

The FastAPI backend is now the local source of truth for project-loop data.

FastAPI 后端现在是项目闭环数据的本地事实来源。

- SQLite database path: `backend/data/plc_copilot.db`
- SQLite 数据库路径：`backend/data/plc_copilot.db`
- Database schema initializes on startup.
- 数据库 schema 在启动时初始化。
- Initial mock projects seed only when the database is empty.
- 仅当数据库为空时写入初始 mock 项目。
- PLC ecosystem profiles remain in memory.
- PLC 生态 profile 仍保存在内存中。
- Projects, intakes, preferences, attachment metadata, report drafts, and report sections persist across backend restarts.
- 项目、输入、偏好、附件元信息、报告草稿和报告分区可以跨后端重启持久化。
- API paths and response shapes remain compatible with the frontend API integration.
- API 路径和响应形状保持与前端 API integration 兼容。

## Shared Concepts / 共享概念

These concepts stay aligned between frontend and backend:

以下概念需要在前后端保持一致：

- `Project`
- `ProjectIntake`
- `PlatformPreference`
- `ProjectAttachment`
- `BenchmarkResult`
- `ReportDraft`
- `ReportSection`
- `ProjectWorkspace`

The backend uses snake_case JSON. The frontend normalizes backend snake_case into frontend camelCase.

后端 API 使用 snake_case JSON。前端将后端 snake_case 规范化为前端 camelCase。

## Current API / 当前 API

- `GET /health`
- `GET /api/ecosystems`
- `GET /api/platforms`
- `GET /api/projects`
- `GET /api/projects/{project_id}`
- `POST /api/projects`
- `DELETE /api/projects/{project_id}`
- `PUT /api/projects/{project_id}/intake`
- `PUT /api/projects/{project_id}/preferences`
- `POST /api/projects/{project_id}/attachments`
- `POST /api/projects/{project_id}/benchmark`
- `PUT /api/projects/{project_id}/report/sections/{section_id}`
- `POST /api/benchmark`

## Agent vs Automation Boundary / Agent 与自动化边界

Deterministic automation owns:

确定性自动化负责：

- Form validation.
- 表单校验。
- Platform scoring and ranking.
- 平台评分和排序。
- Preference weighting.
- 偏好权重计算。
- First-pass risk level.
- 初步风险等级。
- Report structure and fallback sections.
- 报告结构和兜底分区。
- Attachment metadata management.
- 附件元信息管理。

Agent behavior is reserved for future:

Agent 能力留给未来阶段：

- Explaining high/low scores.
- 解释高低分原因。
- Asking follow-up questions.
- 提出追问。
- Drafting and rewriting report prose.
- 生成和重写报告文字。
- Future document-grounded reasoning after parsing/RAG exists.
- 在解析/RAG 存在后进行文档依据推理。

## Next Milestones / 下一阶段里程碑

1. Input/output fallback hardening for incomplete project data.
   完善项目信息不完整时的输入输出兜底。
2. Intelligence placeholder APIs for deterministic explanation prose.
   建立智能化占位 API，用确定性方式生成解释文字。
3. Future document parsing, RAG, and report export after the V1 boundary is stable.
   在 V1 边界稳定后，再进入文档解析、RAG 与报告导出。
