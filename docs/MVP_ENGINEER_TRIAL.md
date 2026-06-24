# MVP Engineer Trial Readiness

Target date: 2026-06-30

## Goal

Prepare the PLC Platform Benchmark & Migration Decision Copilot for a real automation engineer trial.

This is not a commercial release. It is an MVP v0.1 checkpoint where an engineer can complete one realistic PLC selection or migration assessment and give useful feedback on the workflow, scoring, AI explanations, and report output.

## Trial Definition

An engineer should be able to complete the following flow in 15-20 minutes:

1. Open the local web app.
2. Start from a prepared sample project or create a new project.
3. Review or fill project intake:
   - industry
   - project goal
   - I/O scale
   - motion requirement
   - safety requirement
   - budget sensitivity
   - team experience
   - existing platform
   - candidate platforms
   - constraints
4. Register available documents by name, type, and declared purpose.
5. Adjust PLC platform preference weights.
6. Run or review Benchmark ranking.
7. Use AI or basic analysis to explain:
   - missing inputs
   - attachment gaps
   - benchmark ranking
   - preference impact
   - main technical and organizational risks
8. Generate or edit report sections.
9. Export Markdown, browser PDF, or PowerPoint.
10. Provide feedback on whether the recommendation is useful and credible.

## MVP Scope

Included in MVP v0.1:

- Local-first React/FastAPI/SQLite app.
- Project portfolio and single-project workspace.
- PLC ecosystem profile comparison.
- Weighted benchmark with user preference sliders.
- Project readiness/status lifecycle.
- Attachment registration metadata.
- Global and project Query.
- Project analysis, attachment-gap analysis, benchmark explanation, report generation, and report section rewrite.
- AI on/off behavior with basic-analysis fallback.
- Markdown, PDF print view, and PowerPoint export.
- English and Chinese UI coverage for core workflows.

Excluded from MVP v0.1:

- Real Excel parsing.
- PDF/DOCX content extraction.
- Chroma/RAG.
- Multi-user login or permissions.
- PLC connection.
- PLC code generation.
- PLC code conversion.
- Commercial quote or procurement integration.

## Acceptance Checklist

The MVP is ready for engineer trial when:

- The app starts locally without manual code changes.
- The home screen has a clear engineer-trial entry point.
- At least one sample project can demonstrate the full loop.
- New project creation works.
- Intake saving works.
- Preference sliders affect ranking.
- Attachment registration works and clearly states that file contents are not read.
- Benchmark ranking is visible and explainable.
- AI enabled and AI disabled modes both produce usable results.
- Report sections can be edited.
- Report suggestions are not persisted until accepted.
- Markdown export works.
- Browser PDF print view works.
- PowerPoint export works.
- Backend tests pass.
- Frontend build passes.
- No API keys, model IDs, or provider diagnostics are exposed in user-facing content.

## Suggested Trial Projects

Use these scenarios for feedback sessions:

- Battery line PLC standardization:
  Compare Siemens, TwinCAT, CODESYS, and Rockwell for a large production line with high safety requirements.

- High-speed packaging machine:
  Compare TwinCAT, CODESYS, Siemens, and Omron for high-speed motion, vision integration, and virtual commissioning.

- Legacy migration assessment:
  Compare staying with Siemens against CODESYS/TwinCAT migration for an existing medium-size system with reusable standards.

## Feedback Questions

Ask trial engineers:

- Are the benchmark dimensions relevant to your real PLC platform decisions?
- Are any major PLC ecosystem trade-offs missing?
- Do the preference sliders reflect how engineers and managers actually make decisions?
- Are the risk levels believable?
- Is the report useful enough for an internal technical decision meeting?
- Which project inputs should be mandatory before trusting the recommendation?
- Which documents would you expect the next version to parse first?
- Did the AI answer stay within the correct boundary and avoid overclaiming?

## Release Note Template

MVP v0.1 Engineer Trial:

- Purpose: PLC platform selection and migration decision support.
- Status: local engineer-trial MVP.
- Known limitation: attachments are registered only; file contents are not parsed.
- Known limitation: AI explains and drafts, but deterministic scoring remains the source of truth.
- Recommended trial duration: 15-20 minutes.
- Requested feedback: scoring relevance, risk usefulness, report quality, missing inputs, and next parsing priorities.

