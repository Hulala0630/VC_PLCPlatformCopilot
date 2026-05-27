## Product Vision

产品愿景

PLC Platform Benchmark & Migration Decision Copilot is a local-first web application for strategic PLC ecosystem decisions.

PLC 平台基准与迁移决策副驾驶是一个本地优先的 Web 应用，用于支持 PLC 生态选型、平台对比与迁移决策。

The product helps engineers, technical managers, consultants, sales engineers, and decision makers compare PLC platforms from both technical and business perspectives.

该产品帮助自动化工程师、技术经理、技术顾问、销售工程师与决策者，从技术和商业两个角度比较 PLC 平台。

## Product Boundary

产品边界

- This is not a PLC programming tool.
  它不是 PLC 编程工具。
- This is not a PLC code converter.
  它不是 PLC 代码转换器。
- This is not a tool for directly connecting to PLCs.
  它不会直接连接 PLC。
- The product is a strategic decision-support and consulting workspace.
  该产品是战略决策支持与咨询式工作台。

## Phase 1 Status

阶段一状态

Phase 1 is complete.

阶段一已完成。

Completed work:

已完成内容：

- Clean formal project structure.
  清理正式项目结构。
- Remove previous `apps/` prototype directory.
  移除旧 `apps/` 原型目录。
- Stabilize the frontend workstation layout.
  稳定前端工作台布局。
- Standardize mock data around PLC ecosystems, chat threads, and discussed projects.
  围绕 PLC 生态、聊天线程和已沟通过项目标准化 mock 数据。
- Keep Chinese/English content controlled by one language switch button.
  使用一个语言切换按钮控制中文/英文内容。
- Initialize Git repository.
  初始化 Git 仓库。

## Current Interaction Model

当前交互模型

The current frontend is a workstation-style interface rather than a traditional multi-page website.

当前前端采用工作台式交互，而不是传统多页面网站。

Core layout:

核心布局：

- Expandable left sidebar.
  可展开的左侧侧边栏。
- Popular PLC ecosystem list in the sidebar.
  侧边栏内展示当前流行 PLC 生态列表。
- Clicking a PLC ecosystem opens a query and communication panel inside the sidebar.
  点击某个 PLC 生态后，会在侧边栏内展开 Query 沟通区。
- Main workspace on the right shows the list of PLC projects that have already been discussed.
  右侧主工作区展示已经沟通过的 PLC 项目列表。
- Clicking a project shows the communication result, selected platform, decision factors, migration notes, risk level, and engineering effort index.
  点击项目后，显示沟通结果、推荐平台、决策依据、迁移信息、风险等级和工程量指数。

## Current Mock PLC Ecosystems

当前 Mock PLC 生态

- Siemens TIA Portal
- CODESYS
- Beckhoff TwinCAT
- Rockwell Studio 5000
- Mitsubishi GX Works
- Omron Sysmac

## Future Capabilities

未来能力

- Persist PLC ecosystems and project discussions in SQLite.
  使用 SQLite 持久化 PLC 生态与项目沟通记录。
- Move scoring and recommendation logic from frontend mock data into FastAPI services.
  将评分与推荐逻辑从前端 mock 数据下沉到 FastAPI 服务。
- Add project maturity assessment.
  增加项目成熟度评估。
- Add document upload and RAG-based Q&A with Chroma.
  增加文档上传与基于 Chroma 的 RAG 问答。
- Add OpenAI-compatible chat assistant.
  增加 OpenAI-compatible 聊天助手。
- Add LangGraph multi-agent workflows for selection, migration, risk, and report generation.
  使用 LangGraph 构建选型、迁移、风险与报告生成多智能体流程。
- Generate consulting-style PDF/PPT reports.
  生成咨询风格 PDF/PPT 报告。
