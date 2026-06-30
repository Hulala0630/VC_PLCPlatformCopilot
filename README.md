# PLC Platform Benchmark & Migration Decision Copilot

## English Overview

PLC Platform Benchmark & Migration Decision Copilot is a local-first decision-support application for PLC platform selection, migration assessment, and consulting-style report generation.

The application helps automation engineers, controls engineers, engineering managers, and technical decision makers compare PLC ecosystems such as Siemens TIA Portal, Beckhoff TwinCAT, CODESYS, and Rockwell Studio 5000 from both technical and business perspectives. It combines structured project intake, platform preference weighting, deterministic benchmark scoring, attachment registration, optional AI-assisted analysis, and editable report drafts.

This is not a PLC programming environment, not a PLC code converter, and not a tool for connecting to live controllers. Its purpose is to support strategic engineering decisions such as:

- Which PLC ecosystem is most suitable for a new automation project?
- What are the trade-offs between Siemens, TwinCAT, CODESYS, and Rockwell?
- How much effort and risk may be involved in a platform migration?
- How mature is the current project information for making a decision?
- Which assumptions, missing inputs, and risks should be reviewed before committing to a platform?

The current MVP is designed for local engineer trials. Users can create or open a project, fill project inputs, register document metadata, adjust PLC platform preferences, run a benchmark, request AI or basic analysis, edit report sections, and export Markdown, PDF, or PowerPoint outputs.

Current limits are explicit: uploaded files are registered as metadata only; Excel/PDF/DOCX contents are not parsed; RAG is not implemented; AI output is advisory and does not overwrite benchmark scores, project inputs, or official report content unless the user accepts a suggested report section.

本项目是一个本地优先的 PLC 平台选型、迁移评估与报告生成工作台。它面向自动化工程师、控制工程师、技术经理和决策者，用于比较 Siemens TIA Portal、Beckhoff TwinCAT、CODESYS、Rockwell Studio 5000 等 PLC 生态，并围绕项目输入、平台偏好、附件登记、Benchmark、AI 辅助分析和报告输出形成完整决策闭环。

它不是 PLC 编程工具，不连接 PLC，不转换 PLC 代码。

## 快速使用

### 1. 克隆项目

```powershell
git clone https://github.com/Hulala0630/VC_PLCPlatformCopilot.git
cd VC_PLCPlatformCopilot
```

### 2. 配置本地环境变量

复制示例配置文件：

```powershell
Copy-Item .env.example .env.local
```

默认可以不启用真实 AI：

```dotenv
AI_PROVIDER=placeholder
```

如需启用 OpenAI-compatible API，请只在本机 `.env.local` 中填写密钥：

```dotenv
AI_PROVIDER=openai
OPENAI_API_KEY=your-local-api-key
OPENAI_BASE_URL=https://api.openai.com/v1
AI_MODEL_FAST=your-fast-model
AI_MODEL_BALANCED=your-balanced-model
AI_MODEL_QUALITY=your-quality-model
```

不要把真实 API key 写入源码、README、Issue、提交记录或聊天消息。`.env.local` 已被 `.gitignore` 排除。

### 3. 启动后端

```powershell
cd backend
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

后端健康检查：

```powershell
Invoke-RestMethod http://127.0.0.1:8000/health
```

### 4. 启动前端

另开一个终端：

```powershell
cd frontend
npm install
npm run dev
```

打开：

```text
http://127.0.0.1:5173/
```

如果本地使用了其他端口，例如 `5174`，以 Vite 输出为准。

## 典型使用流程

1. 打开本地 Web 应用。
2. 从项目列表进入一个 PLC 选型或迁移评估项目，或创建新项目。
3. 填写项目行业、目标、I/O 规模、运动控制、安全、预算敏感度、团队经验、既有平台和候选平台。
4. 登记附件，例如 I/O 表、电气清单、需求文档和架构说明。当前版本只记录附件名称、类型和用途，不读取正文。
5. 调整各 PLC 平台偏好权重。
6. 运行 Benchmark，查看技术评分、偏好影响、综合排序和风险等级。
7. 使用 AI 或基础分析获取项目摘要、附件缺口建议、Benchmark 解释和报告建议稿。
8. 审阅并接受报告分区建议，或手动编辑正式报告内容。
9. 导出 Markdown、浏览器 PDF 或 PowerPoint。

## 核心能力

- PLC 生态对比：Siemens、TwinCAT、CODESYS、Rockwell 等平台卡片与官方链接。
- 项目工作台：Overview、Intake、Preferences、Attachments、Benchmark、Report。
- 平台偏好权重：用户可调节各平台倾向性，并影响 Benchmark 综合分。
- Benchmark：保留技术评分、偏好评分、加权评分、风险等级和推荐排序。
- 附件登记：记录文件名、文件类型、声明用途和上传时间，当前不解析文件内容。
- AI 辅助分析：全局 Query、项目 Query、附件分析、Benchmark 分析、项目摘要、报告建议稿和分区改写。
- 报告输出：支持 Markdown、浏览器打印 PDF、PowerPoint。
- 中英双语：核心 UI 和主要输出支持中文/英文切换。

## AI 与基础分析模式

系统支持两种分析路径：

- `AI_PROVIDER=placeholder`：使用基础分析逻辑，不调用真实模型。
- `AI_PROVIDER=openai`：通过后端调用 OpenAI-compatible API。

AI 输出只作为顾问建议，不会自动修改项目输入、偏好权重、Benchmark 分数或正式报告内容。报告建议必须由用户接受后才会写入正式报告。

AI Benchmark 可以在业务约束、既有装机、团队能力、停机风险或生命周期策略更重要时，提出不同于固定排名第一的平台建议；但固定 Benchmark 分数、排名、风险等级和图表仍作为审计基线保留。

## 产品边界

当前版本明确不做：

- PLC 在线连接
- PLC 程序生成
- PLC 代码转换
- Excel/PDF/DOCX 正文解析
- Chroma/RAG 文档问答
- 多用户权限和商业报价

附件在当前版本中是 metadata-only：系统可以基于文件名、类型和声明用途讨论“这些资料可能支持什么判断”，但不会声称读取或理解了文件正文。

## 技术栈

Frontend:

- React
- TypeScript
- Vite
- Tailwind CSS
- pptxgenjs

Backend:

- FastAPI
- Pydantic
- SQLite
- OpenAI Python SDK

Future AI/RAG direction:

- LangGraph
- Chroma
- 文档解析与用户审阅确认流程

## 项目结构

```text
.
├── backend/
│   ├── app/
│   │   ├── intelligence/      # AI provider、prompt、streaming、fallback contract
│   │   ├── data.py            # PLC profiles and seed projects
│   │   ├── database.py        # SQLite schema and connection
│   │   ├── models.py          # Domain models
│   │   ├── repository.py      # Persistence layer
│   │   ├── routes.py          # Project and benchmark API
│   │   └── services.py        # Readiness, benchmark, lifecycle logic
│   └── tests/
├── frontend/
│   ├── src/
│   │   ├── api/client.ts      # Backend API adapter
│   │   ├── data/platforms.ts  # Frontend fallback mock data
│   │   ├── App.tsx            # Main workstation UI
│   │   └── types.ts
├── docs/
│   ├── PROJECT.md             # Product architecture and contract
│   ├── AGENT.md               # Development and AI boundary rules
│   └── MVP_ENGINEER_TRIAL.md  # Engineer trial checklist
├── docker-compose.yml
├── .env.example
└── README.md
```

## 后端 API 概览

常用接口：

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

## 测试与构建

后端测试：

```powershell
python -m unittest discover -s backend\tests
```

前端构建：

```powershell
cd frontend
npm run build
```

Docker 本地编排：

```powershell
docker compose up --build
```

## 当前状态

当前目标是 `MVP v0.1 Engineer Trial Ready`：让真实自动化工程师可以在 15-20 分钟内完成一次 PLC 选型或迁移评估试用，并反馈评分维度、风险判断、AI 解释和报告输出是否有工程价值。

更多产品边界和开发规则见：

- `docs/PROJECT.md`
- `docs/AGENT.md`
- `docs/MVP_ENGINEER_TRIAL.md`
