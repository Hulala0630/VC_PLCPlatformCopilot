## Development Context

开发上下文

This project is built using a vibe-coding workflow.

本项目采用 vibe-coding 工作流构建。

The user acts as product architect and industrial automation domain expert.

用户担任产品架构师与工业自动化领域专家。

Codex acts as senior full-stack implementation engineer and technical architect.

Codex 担任资深全栈实现工程师与技术架构师。

## Current Project Name

当前项目名称

PLC Platform Benchmark & Migration Decision Copilot

PLC 平台基准与迁移决策副驾驶

## Current Architecture

当前架构

- `frontend/`: Current React + TypeScript + Vite + Tailwind CSS workstation UI.
  `frontend/`：当前 React + TypeScript + Vite + Tailwind CSS 工作台前端。
- `backend/`: FastAPI skeleton for future API, scoring, persistence, and AI integration.
  `backend/`：FastAPI 后端骨架，用于未来 API、评分、持久化与 AI 集成。
- `docs/`: Product and agent development context.
  `docs/`：产品与开发上下文。
- `infra/`: Deployment notes and infrastructure assets.
  `infra/`：部署说明与基础设施资产。

## Phase 1 Completion

阶段一完成状态

Phase 1 is complete. Treat the current state as the baseline for future feature work.

阶段一已完成。后续功能开发应以当前状态作为基线。

Do not reintroduce the removed `apps/` prototype directory unless explicitly requested.

除非明确要求，不要重新引入已移除的 `apps/` 原型目录。

## Current Frontend Interaction

当前前端交互

The frontend should prioritize the workstation layout:

前端应优先围绕工作台布局开发：

- Left expandable sidebar.
  左侧可展开侧边栏。
- PLC ecosystem list inside the sidebar.
  侧边栏内的 PLC 生态列表。
- Query conversation panel inside the sidebar after selecting a PLC ecosystem.
  选择 PLC 生态后，在侧边栏中显示 Query 沟通区。
- Right-side main workspace showing discussed PLC projects.
  右侧主工作区展示已沟通过的 PLC 项目。
- Project click reveals decision output and selection/migration information.
  点击项目后展示决策输出、选型和迁移信息。
- Chinese/English content is controlled by a language switch button.
  中文/英文由语言切换按钮控制。

## Development Rules

开发规则

- Focus on decision support, not PLC programming.
  聚焦决策支持，而不是 PLC 编程。
- Do not build PLC code conversion or direct PLC connection features unless explicitly requested later.
  除非之后明确要求，不要构建 PLC 代码转换或直接连接 PLC 的功能。
- Emphasize business and technical trade-offs.
  强调商业与技术取舍。
- Use assumptions and clearly state uncertainty.
  使用假设，并清楚说明不确定性。
- Keep architecture modular and local-first.
  保持架构模块化，并坚持本地优先。
- Build incrementally with mock data first.
  先使用 mock 数据进行增量构建。
- Keep the app runnable after each meaningful change.
  每次有意义的改动后保持应用可运行。
- Preserve the language-switch approach instead of showing all bilingual text side by side.
  保持语言切换方式，不要重新改回中英并列显示。

## Stack

技术栈

- Frontend / 前端: React, TypeScript, Vite, Tailwind CSS
- Backend / 后端: FastAPI
- AI Layer / AI 层: OpenAI-compatible API, LangGraph future
- Data / 数据: JSON/YAML profiles, SQLite future, Chroma future
- Deployment / 部署: Local-first, Docker-ready

## Next Development Priorities

下一步优先级

1. Connect frontend mock project data to FastAPI endpoints.
   将前端 mock 项目数据接入 FastAPI 接口。
2. Prepare SQLite persistence for project discussions and selected PLC ecosystem state.
   为项目沟通记录与所选 PLC 生态状态准备 SQLite 持久化。
3. Add real query assistant behavior with an OpenAI-compatible API.
   使用 OpenAI-compatible API 增加真实 Query 助手行为。
4. Add project maturity assessment and migration scoring forms.
   增加项目成熟度评估与迁移评分表单。
5. Add report generation workflow.
   增加报告生成工作流。
