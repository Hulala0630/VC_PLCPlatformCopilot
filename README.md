# PLC Platform Benchmark & Migration Decision Copilot

PLC 平台基准与迁移决策副驾驶

This is a local-first consulting workspace for comparing PLC ecosystems, discussing project constraints, and supporting platform selection and migration decisions.

这是一个本地优先的咨询式工作台，用于比较 PLC 生态、沟通项目约束，并支持平台选型与迁移决策。

## Product Boundary

产品边界：

- Not a PLC programming tool.
  不是 PLC 编程工具。
- Not a PLC code converter.
  不是 PLC 代码转换器。
- Not a direct PLC connection tool.
  不会直接连接 PLC。
- It is a strategic decision-support Copilot.
  它是战略决策支持 Copilot。

## Current Phase

当前阶段：Phase 1 completed.

阶段一已完成：

- Formal project structure is cleaned.
  正式项目结构已清理。
- Previous `apps/` prototype has been removed.
  旧 `apps/` 原型目录已移除。
- Frontend workstation UI is stabilized.
  前端工作台界面已稳定。
- Mock data is structured for future API integration.
  Mock 数据已整理为便于后续 API 接入的结构。
- Git repository has been initialized.
  Git 仓库已初始化。

## Project Structure

项目结构：

- `frontend/`: React, TypeScript, Vite, Tailwind CSS workstation UI.
  `frontend/`：React、TypeScript、Vite、Tailwind CSS 工作台前端。
- `backend/`: FastAPI skeleton for APIs, scoring, persistence, and future AI integration.
  `backend/`：FastAPI 后端骨架，用于 API、评分、持久化和未来 AI 集成。
- `docs/`: Product and agent development context.
  `docs/`：产品与开发上下文。
- `infra/`: Deployment notes and future infrastructure assets.
  `infra/`：部署说明与未来基础设施资产。

## Current Frontend

当前前端：

- Left expandable sidebar.
  左侧可展开侧边栏。
- Popular PLC ecosystem list.
  流行 PLC 生态列表。
- Query communication panel inside the sidebar.
  侧边栏内 Query 沟通区。
- Right-side discussed PLC project list.
  右侧已沟通过的 PLC 项目列表。
- Project decision result panel.
  项目决策结果面板。
- Platform benchmark snapshot.
  平台基准摘要。
- Chinese/English language switch button.
  中英文语言切换按钮。

## Run Locally

本地运行：

Backend / 后端:

```powershell
cd backend
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

Frontend / 前端:

```powershell
cd frontend
npm install
npm run dev
```

Then open `http://localhost:5173`.

然后打开 `http://localhost:5173`。

## Next Development Phase

下一阶段建议进入 Phase 2：

1. Move mock PLC ecosystem and project data behind FastAPI endpoints.
   将 mock PLC 生态与项目数据接入 FastAPI 接口。
2. Add frontend API client with graceful fallback.
   增加前端 API client，并保留降级 fallback。
3. Prepare SQLite schema for projects and chat messages.
   准备项目与聊天消息的 SQLite schema。
