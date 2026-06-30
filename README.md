# PLC Platform Benchmark & Migration Decision Copilot

## Overview / 项目概览

PLC Platform Benchmark & Migration Decision Copilot is a local-first decision-support application for PLC platform selection, migration assessment, and consulting-style report generation.

PLC Platform Benchmark & Migration Decision Copilot 是一个本地优先的 PLC 平台选型、迁移评估与顾问式报告生成应用。

It helps automation engineers, controls engineers, engineering managers, and technical decision makers compare PLC ecosystems such as Siemens TIA Portal, Beckhoff TwinCAT, CODESYS, and Rockwell Studio 5000 from both technical and business perspectives.

它面向自动化工程师、控制工程师、工程经理和技术决策者，用于从技术与业务两个角度比较 Siemens TIA Portal、Beckhoff TwinCAT、CODESYS、Rockwell Studio 5000 等 PLC 生态。

This is not a PLC programming tool, not a PLC code converter, and not a tool for connecting to live controllers. Its purpose is to support strategic engineering decisions.

它不是 PLC 编程工具，不做 PLC 代码转换，也不直接连接现场控制器。它的目标是辅助工程团队完成战略层面的选型与迁移决策。

## Quick Start / 快速使用

### 1. Clone The Repository / 克隆项目

```powershell
git clone https://github.com/Hulala0630/VC_PLCPlatformCopilot.git
cd VC_PLCPlatformCopilot
```

### 2. Configure Environment Variables / 配置环境变量

Copy the example environment file and keep all real secrets in your local `.env.local`.

复制示例环境文件，并只在本地 `.env.local` 中保存真实密钥。

```powershell
Copy-Item .env.example .env.local
```

The app can run without a real AI provider by using the placeholder mode.

应用可以在不接入真实 AI Provider 的情况下运行，此时使用 placeholder 模式。

```dotenv
AI_PROVIDER=placeholder
```

To enable an OpenAI-compatible provider, configure the following values in `.env.local`.

如需启用 OpenAI-compatible Provider，请在 `.env.local` 中配置以下变量。

```dotenv
AI_PROVIDER=openai
OPENAI_API_KEY=your-local-api-key
OPENAI_BASE_URL=https://api.openai.com/v1
AI_MODEL_FAST=your-fast-model
AI_MODEL_BALANCED=your-balanced-model
AI_MODEL_QUALITY=your-quality-model
```

Never commit real API keys to Git, README files, issues, screenshots, or chat messages. `.env.local` is ignored by Git.

不要将真实 API key 写入 Git、README、Issue、截图或聊天消息中。`.env.local` 已被 Git 忽略。

### 3. Start The Backend / 启动后端

```powershell
cd backend
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

Backend health check:

后端健康检查：

```powershell
Invoke-RestMethod http://127.0.0.1:8000/health
```

### 4. Start The Frontend / 启动前端

Open another terminal and run:

另开一个终端并运行：

```powershell
cd frontend
npm install
npm run dev
```

Open the Vite URL printed in the terminal, usually:

打开 Vite 在终端输出的地址，通常为：

```text
http://127.0.0.1:5173/
```

If Vite selects another port, such as `5174`, use the printed URL.

如果 Vite 选择了其他端口，例如 `5174`，请以终端输出为准。

### 5. Optional Docker Run / 可选 Docker 运行

```powershell
docker compose up --build
```

## Typical Workflow / 典型使用流程

1. Open the local web application.
   打开本地 Web 应用。

2. Select an existing PLC selection or migration project, or create a new project.
   选择一个已有 PLC 选型或迁移评估项目，或者创建新项目。

3. Fill in project inputs such as industry, project goal, I/O scale, motion requirements, safety needs, budget sensitivity, team experience, existing platform, and candidate platforms.
   填写行业、项目目标、I/O 规模、运动控制、安全需求、预算敏感度、团队经验、现有平台和候选平台等项目输入。

4. Register attachments such as I/O lists, electrical bills of material, requirement documents, and architecture descriptions.
   登记 I/O 表、电气清单、需求文档和架构说明等附件。

5. Adjust platform preference weights for Siemens, TwinCAT, CODESYS, Rockwell, and other PLC ecosystems.
   调整 Siemens、TwinCAT、CODESYS、Rockwell 等 PLC 平台的偏好权重。

6. Run the benchmark to review technical scores, preference impact, weighted ranking, risks, and assumptions.
   运行 Benchmark，查看技术评分、偏好影响、加权排序、风险和假设。

7. Use AI or basic analysis to generate project summaries, gap suggestions, attachment review notes, benchmark explanations, and report draft suggestions.
   使用 AI 或基础分析生成项目摘要、缺口建议、附件审阅说明、Benchmark 解释和报告建议稿。

8. Review and accept report section suggestions, or manually edit the formal report content.
   审阅并接受报告分区建议，或手动编辑正式报告内容。

9. Export the report as Markdown, browser PDF, or PowerPoint.
   将报告导出为 Markdown、浏览器 PDF 或 PowerPoint。

## Core Features / 核心能力

- PLC ecosystem comparison: platform cards and official links for Siemens, TwinCAT, CODESYS, Rockwell, and other ecosystems.
  PLC 生态对比：提供 Siemens、TwinCAT、CODESYS、Rockwell 等平台卡片与官方网站链接。

- Project workspace: Overview, Intake, Preferences, Attachments, Benchmark, and Report tabs.
  项目工作台：包含 Overview、Intake、Preferences、Attachments、Benchmark 和 Report 标签页。

- Platform preference weighting: users can express practical preference or installed-base bias, and the benchmark separates baseline technical score from preference-adjusted score.
  平台偏好权重：用户可以表达实际倾向或既有装机基础偏好，Benchmark 会区分基础技术评分和偏好加权评分。

- Attachment register: the current MVP records file name, file type, declared purpose, upload time, and project association.
  附件登记：当前 MVP 记录文件名、文件类型、声明用途、上传时间和关联项目。

- AI-assisted analysis: global chat, project chat, attachment notes, benchmark analysis, project summary, report draft generation, and section rewrite suggestions.
  AI 辅助分析：支持全局问答、项目问答、附件说明、Benchmark 分析、项目摘要、报告建议稿生成和分区改写建议。

- Report export: Markdown, browser PDF, and PowerPoint outputs.
  报告导出：支持 Markdown、浏览器 PDF 和 PowerPoint 输出。

- Bilingual experience: the main UI and project-facing language support Chinese and English switching.
  双语体验：主要 UI 和面向项目的文本支持中英文切换。

## AI And Basic Analysis / AI 与基础分析

The system supports two execution modes.

系统支持两种执行模式。

- `AI_PROVIDER=placeholder`: uses deterministic fallback and basic analysis without calling a real model.
  `AI_PROVIDER=placeholder`：使用确定性兜底与基础分析，不调用真实模型。

- `AI_PROVIDER=openai`: uses the backend OpenAI-compatible provider for AI-assisted analysis and streaming output.
  `AI_PROVIDER=openai`：通过后端 OpenAI-compatible Provider 提供 AI 辅助分析和流式输出。

AI output is advisory. It does not automatically overwrite project inputs, preference weights, benchmark scores, ranking, charts, or formal report sections.

AI 输出是顾问建议。它不会自动覆盖项目输入、偏好权重、Benchmark 分数、排序、图表或正式报告分区。

For reports, AI creates suggestions. The user must accept a suggestion before it becomes formal report content.

对于报告，AI 生成的是建议稿。只有用户接受后，建议稿才会写入正式报告内容。

AI may recommend a different platform from the deterministic first-ranked platform when business constraints, installed base, team capability, downtime risk, lifecycle strategy, or missing inputs make that recommendation more defensible. The deterministic benchmark remains visible as the audit baseline.

当业务约束、既有装机、团队能力、停机风险、生命周期策略或缺失输入使另一平台更合理时，AI 可以推荐不同于确定性排名第一的平台。确定性 Benchmark 仍保留为可审计基线。

## Product Boundaries / 产品边界

The current version explicitly does not provide:

当前版本明确不提供：

- Live PLC connection.
  PLC 在线连接。

- PLC program generation.
  PLC 程序生成。

- PLC code conversion.
  PLC 代码转换。

- Excel, PDF, DOCX, or drawing content parsing.
  Excel、PDF、DOCX 或图纸正文解析。

- Chroma or RAG-based document Q&A.
  Chroma 或 RAG 文档问答。

- Multi-user permission management.
  多用户权限管理。

Attachments are metadata-only in the current MVP. The system may discuss what a file name, type, and declared purpose could support, but it must not claim that the file content has been read or understood.

当前 MVP 中附件仅做元信息登记。系统可以说明文件名、类型和声明用途可能支持哪些判断，但不能声称已经读取或理解附件正文。

## Architecture / 技术架构

Frontend:

前端：

- React
- TypeScript
- Vite
- Tailwind CSS
- pptxgenjs

Backend:

后端：

- FastAPI
- Pydantic
- SQLite
- OpenAI Python SDK

Future AI and RAG direction:

未来 AI 与 RAG 方向：

- LangGraph for multi-step agent workflows.
  使用 LangGraph 构建多步骤 Agent 工作流。

- Chroma for vector retrieval.
  使用 Chroma 做向量检索。

- Document parsing with explicit user review and confirmation.
  引入带用户审阅确认机制的文档解析流程。

## Project Structure / 项目结构

```text
.
|-- backend/
|   |-- app/
|   |   |-- intelligence/      # AI provider, prompts, streaming, fallback contract / AI Provider、Prompt、流式输出与兜底契约
|   |   |-- data.py            # PLC profiles and seed projects / PLC 平台资料与示例项目
|   |   |-- database.py        # SQLite schema and connection / SQLite 结构与连接
|   |   |-- models.py          # Domain models / 领域模型
|   |   |-- repository.py      # Persistence layer / 数据持久化层
|   |   |-- routes.py          # Project and benchmark API / 项目与 Benchmark API
|   |   `-- services.py        # Readiness, benchmark, lifecycle logic / 成熟度、Benchmark 与生命周期逻辑
|   `-- tests/
|-- frontend/
|   `-- src/
|       |-- api/client.ts      # Backend API adapter / 后端 API 适配器
|       |-- data/platforms.ts  # Frontend fallback data / 前端兜底数据
|       |-- App.tsx            # Main workstation UI / 主工作台界面
|       `-- types.ts
|-- docs/
|   |-- PROJECT.md             # Product architecture and contract / 产品架构与契约
|   |-- AGENT.md               # Development and AI boundary rules / 开发规则与 AI 边界
|   `-- MVP_ENGINEER_TRIAL.md  # Engineer trial checklist / 工程师试用验收清单
|-- docker-compose.yml
|-- .env.example
`-- README.md
```

## API Overview / 后端 API 概览

Common backend endpoints:

常用后端接口：

- `GET /health`
- `GET /api/ecosystems`
- `GET /api/projects`
- `POST /api/projects`
- `GET /api/projects/{project_id}`
- `PUT /api/projects/{project_id}/intake`
- `PUT /api/projects/{project_id}/preferences`
- `POST /api/projects/{project_id}/attachments`
- `POST /api/projects/{project_id}/benchmark`
- `PUT /api/projects/{project_id}/report/sections/{section_id}`
- `GET /api/intelligence/status`
- `POST /api/intelligence/connection-test`
- `POST /api/projects/{project_id}/intelligence/chat`
- `POST /api/projects/{project_id}/intelligence/analyze`
- `POST /api/projects/{project_id}/intelligence/benchmark/stream`
- `POST /api/projects/{project_id}/intelligence/summary/stream`
- `POST /api/projects/{project_id}/report/generate`
- `POST /api/projects/{project_id}/report/sections/{section_id}/generate`
- `POST /api/projects/{project_id}/report/sections/{section_id}/rewrite`

## Testing And Build / 测试与构建

Run backend tests:

运行后端测试：

```powershell
python -m unittest discover -s backend\tests
```

Run frontend build:

运行前端构建：

```powershell
cd frontend
npm run build
```

Run the full local Docker stack:

运行完整本地 Docker 编排：

```powershell
docker compose up --build
```

## Current Status / 当前状态

The current product target is `MVP v0.1 Engineer Trial Ready`: a real automation engineer should be able to complete a PLC selection or migration assessment trial in about 15 to 20 minutes and give feedback on scoring dimensions, risk judgment, AI explanations, and report usefulness.

当前产品目标是 `MVP v0.1 Engineer Trial Ready`：真实自动化工程师应能在约 15 到 20 分钟内完成一次 PLC 选型或迁移评估试用，并反馈评分维度、风险判断、AI 解释和报告输出是否有工程价值。

Useful project documents:

有用的项目文档：

- `docs/PROJECT.md`
- `docs/AGENT.md`
- `docs/MVP_ENGINEER_TRIAL.md`

## Roadmap / 后续路线

Near-term priorities:

近期优先事项：

- Improve benchmark evidence and engineering assumptions.
  增强 Benchmark 评分依据与工程假设表达。

- Harden AI prompts and streaming user experience.
  打磨 AI Prompt 与流式输出体验。

- Add reviewed document parsing before enabling RAG.
  在启用 RAG 前加入可审阅的文档解析流程。

- Improve PDF and PowerPoint report polish.
  优化 PDF 与 PowerPoint 报告输出质量。

- Prepare a structured engineer feedback loop.
  准备结构化工程师反馈闭环。
