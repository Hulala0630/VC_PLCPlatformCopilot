# Task 5B Agent Plan: Attachment Intelligence Before RAG

## Purpose / 目标

Task 5B defines how attachment intelligence should enter the PLC decision copilot before implementing real file parsing, Excel reading, Chroma, or RAG.

Task 5B 的目标是在真正实现文件解析、Excel 读取、Chroma 或 RAG 之前，先定义附件智能化如何进入 PLC 决策 Copilot。

This is a planning and contract phase. It should produce stable concepts for later frontend, backend, and prompt work.

这是一个规划与契约阶段。它应先产出稳定概念，再分发给前端、后端和 Prompt 工作流实现。

## Product Principle / 产品原则

The application remains a strategic decision-support platform.

本应用仍然是战略决策支持平台。

It does not become:

它不会变成：

- a PLC programming tool / PLC 编程工具
- a PLC code converter / PLC 代码转换工具
- a live PLC connection tool / PLC 在线连接工具
- an uncontrolled document ingestion system / 不受控的文档摄取系统

Attachments should help the system understand project maturity, engineering effort, risk, and report evidence. They should not automatically override deterministic benchmark results.

附件应帮助系统理解项目成熟度、工程量、风险和报告依据，但不得自动覆盖确定性 Benchmark 结果。

## Attachment Classes / 附件类别

The first structured attachment intelligence layer should recognize these document classes:

第一层结构化附件智能化应识别以下文档类别：

- `io_list`: I/O list, terminal list, signal list.
- `electrical_bom`: electrical bill of material, cabinet BOM, device list.
- `requirements_spec`: user requirement specification, functional requirement document.
- `architecture_description`: system architecture, control architecture, network topology.
- `safety_concept`: safety requirement, risk assessment, safety function description.
- `hmi_concept`: HMI screen list, alarm concept, operator workflow.
- `test_plan`: FAT/SAT plan, validation checklist, commissioning plan.
- `legacy_code_inventory`: existing PLC program inventory, block list, library list. Metadata only at first.
- `vendor_documentation`: vendor manuals, datasheets, migration notes.
- `internal_standard`: internal engineering standard, naming rules, programming guideline.
- `other`: registered but not classified.

## Phase 5B Scope / 5B 范围

Task 5B should not parse actual file content yet. It should prepare the system for future parsing by adding structure around attachment intent, expected extraction fields, user confirmation, and AI explanation.

Task 5B 不应立即解析真实文件内容。它应先围绕附件用途、未来提取字段、用户确认和 AI 解释建立结构。

In scope:

范围内：

- richer attachment metadata
- attachment class selection
- declared purpose
- parsing readiness state
- expected extraction schema per document class
- user confirmation workflow
- AI questions about missing documents and unclear declared purposes
- deterministic maturity impact from registered/confirmed metadata only

Out of scope:

范围外：

- reading Excel rows
- parsing PDF/DOCX content
- embedding documents
- vector search
- RAG answers
- automatic benchmark score replacement
- automatic report mutation from parsed content

## Proposed Data Concepts / 建议数据概念

### Attachment Registration

Current attachment metadata should evolve toward:

当前附件元信息建议演进为：

- `id`
- `project_id`
- `file_name`
- `file_type`
- `document_class`
- `declared_purpose`
- `business_relevance`
- `uploaded_at`
- `content_status`
- `user_confirmed`
- `notes`

`content_status` should use:

`content_status` 建议使用：

- `registered_only`: file is only registered.
- `pending_parse`: user marked it as suitable for future parsing.
- `parsed_pending_review`: future parser produced structured extraction, not yet accepted.
- `accepted`: user accepted extracted structured facts.
- `rejected`: user rejected extracted structured facts.
- `parse_failed`: future parser failed safely.

For Task 5B implementation, only `registered_only` and `pending_parse` are required.

Task 5B 实现时只需要 `registered_only` 和 `pending_parse`。

### Expected Extraction Schema

Do not implement extraction yet. Define the expected future fields.

先不实现提取，只定义未来期望字段。

`io_list` future fields:

- total I/O count
- digital input count
- digital output count
- analog input count
- analog output count
- safety I/O count
- motion axis count if visible
- communication devices if visible
- missing signal metadata
- confidence and review notes

`requirements_spec` future fields:

- target machine/process
- operating modes
- performance requirements
- safety requirements
- motion requirements
- integration interfaces
- validation requirements
- open questions

`architecture_description` future fields:

- controller topology
- HMI/SCADA interfaces
- network protocols
- remote I/O strategy
- simulation/virtual commissioning references
- vendor dependencies
- migration constraints

`safety_concept` future fields:

- safety functions
- safety PLC requirement
- required performance level or SIL if present
- safety I/O dependencies
- validation obligations
- unresolved hazards

## Deterministic vs Agent Boundary / 确定性逻辑与 Agent 边界

Deterministic automation owns:

确定性自动化负责：

- attachment class validation
- required metadata checks
- maturity contribution from attachment registration
- parse readiness status
- future accepted extraction storage
- preventing unreviewed extraction from affecting benchmark

Agent owns:

Agent 负责：

- explaining what each attachment type can contribute
- asking targeted follow-up questions
- identifying missing document classes
- summarizing declared purpose gaps
- drafting report language from accepted facts
- clearly stating whether content has not been parsed

Agent does not own:

Agent 不负责：

- direct PLC interaction
- PLC program generation
- code conversion
- benchmark score calculation
- accepting extracted facts without user review
- claiming file content was read when it was not

## UX Workflow / 交互工作流

Recommended user flow:

推荐用户流程：

1. User registers attachment metadata.
2. User selects document class and declared purpose.
3. System shows whether the document can contribute to maturity, benchmark assumptions, or report evidence.
4. AI asks targeted questions about missing or unclear information.
5. Future parser produces structured facts only after user requests parsing.
6. User reviews parsed facts.
7. Only accepted facts become project evidence.
8. Benchmark remains deterministic; accepted facts may change intake/readiness inputs only through explicit user confirmation.

## Frontend Task Split / 前端任务拆分

Frontend should later implement:

前端后续应实现：

- attachment class selector
- content status badge
- "mark for future parsing" action
- attachment contribution panel
- missing document checklist
- AI follow-up questions panel
- review UI for future extracted facts
- clear message: "file content has not been read yet"

## Backend Task Split / 后端任务拆分

Backend should later implement:

后端后续应实现：

- extended attachment model
- attachment class enum
- content status enum
- migration for existing attachment records
- endpoints to update attachment classification/status
- deterministic attachment completeness scoring
- future table for accepted extracted facts
- tests proving unaccepted parsed facts cannot affect benchmark

## Prompt Task Split / Prompt 任务拆分

Prompt work should later implement:

Prompt 后续应实现：

- attachment-class aware analysis prompts
- missing-document question generation
- report evidence wording based only on accepted facts
- strict wording for registered-only attachments
- refusal boundary for questions asking the AI to infer file content before parsing

## RAG Readiness / RAG 准备

RAG should come after structured parsing and user confirmation.

RAG 应在结构化解析和用户确认之后再进入。

Recommended future order:

建议未来顺序：

1. Attachment metadata classification.
2. Structured parser contracts.
3. User review and accepted facts.
4. Project evidence store.
5. Document chunking and embeddings.
6. Chroma retrieval.
7. RAG answer grounding with citations.
8. Report generation grounded in accepted facts and cited document chunks.

## Acceptance Criteria / 验收标准

Task 5B planning is complete when:

Task 5B 规划在以下条件满足时完成：

- attachment classes are defined
- future extraction fields are defined
- deterministic vs agent boundary is explicit
- frontend/backend/prompt task splits are clear
- RAG is sequenced after structured parsing and user confirmation
- docs state that current version still does not parse file content

