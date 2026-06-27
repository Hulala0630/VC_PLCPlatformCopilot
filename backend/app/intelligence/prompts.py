from dataclasses import dataclass
import json

from app.intelligence.models import (
    BenchmarkAnalysisRequest,
    BenchmarkExplanationRequest,
    GlobalChatRequest,
    ProjectAnalysisRequest,
    ProjectChatRequest,
    ProjectSummaryRequest,
    ReportGenerationRequest,
    ReportSectionRewriteRequest,
)
from app.models import BenchmarkResult, PlcEcosystem, ProjectWorkspace, ReportSection


@dataclass(frozen=True)
class PromptBundle:
    instructions: str
    input: str


COMMON_BOUNDARIES = """
You are a senior industrial automation consultant and PLC platform selection and migration decision advisor.
This product is for PLC platform selection, benchmark interpretation, migration evaluation, and consulting report drafting only.
It is not a PLC programming tool, not a PLC code converter, and not connected to any PLC or control network.
Never generate PLC program code, PLC code conversion output, online PLC operations, commissioning commands, or direct controller-connection instructions.
Use only the supplied platform profiles, project intake, preferences, readiness, report sections, benchmark results, and attachment registration records.
Attachment files have not been opened, parsed, read, summarized, or understood. You may discuss file name, type, declared purpose, upload time, and gaps only.
Treat benchmark scores, rankings, risk levels, and readiness values as fixed source facts. Explain them; do not recalculate, change, normalize, override, or replace them.
Separate facts, auditable assumptions, uncertainties, and recommendations. Make assumptions specific enough that a project team can verify or reject them.
Write like a professional industrial automation consulting advisor: concise, decision-oriented, balanced, and readable in both Chinese and English.
The output must be not promotional: avoid inflated claims, generic chat filler, and vague best-practice lists. Prefer concrete engineering tradeoffs, missing inputs, risk checks, and next actions.
Structure the answer for streaming display: use short complete semantic paragraphs, give the conclusion first, then expand into evidence, risks, assumptions, and recommended next actions.
Return only the requested structured response. Fill every LocalizedText with natural zh and en. Prefer the requested language in substance and emphasis.
Do not expose internal implementation terms in user-facing fields, including mock, placeholder, deterministic, deterministic_fallback, provider, model id, API key, fallback, persistence, internal, dev wording, or scoring logic. Refer to the benchmark as the fixed benchmark baseline or fixed calculation rules instead.
""".strip()


def global_chat_prompt(request: GlobalChatRequest, platforms: list[PlcEcosystem]) -> PromptBundle:
    context = {
        "question": request.question,
        "requested_language": request.language,
        "platform_profiles": [
            {
                "id": item.id,
                "name": item.name,
                "summary": item.summary.model_dump(),
                "strengths": [value.model_dump() for value in item.strengths],
                "cautions": [value.model_dump() for value in item.cautions],
                "scores": item.scores.model_dump(),
            }
            for item in platforms
        ],
    }
    return _bundle(
        "Answer the global PLC ecosystem selection question using platform profiles only. Distinguish practical ecosystem differences between Siemens TIA Portal, Beckhoff TwinCAT, CODESYS, Rockwell Studio 5000, and other selected platforms when they are present: engineering workflow, motion fit, safety ecosystem, openness, talent availability, integration style, lifecycle risk, and cost pressure. Keep the answer useful for an automation engineer trialing the tool: concrete, restrained, and not promotional. Do not discuss PLC programming, PLC code conversion, direct PLC connections, online diagnostics, or commissioning commands.",
        context,
    )


def project_chat_prompt(
    request: ProjectChatRequest,
    workspace: ProjectWorkspace,
    benchmark: list[BenchmarkResult],
) -> PromptBundle:
    context = _project_context(workspace, benchmark)
    context.update({"question": request.question, "requested_language": request.language})
    return _bundle(
        "Answer the project question using only the supplied structured project facts. If the project has missing inputs, explain what is missing, why each gap affects PLC platform selection or migration decisions, and what information should be collected next. State that attachment file bodies have not been parsed. State that benchmark scores come from fixed benchmark calculation rules and that the advisory answer does not change scores or rankings. Keep the answer concise, engineering-oriented, and focused on PLC selection and migration decisions.",
        context,
    )


def project_analysis_prompt(
    request: ProjectAnalysisRequest,
    workspace: ProjectWorkspace,
    benchmark: list[BenchmarkResult],
) -> PromptBundle:
    if request.focus == "attachments":
        context = {
            "requested_language": request.language,
            "focus": request.focus,
            "project": {
                "id": workspace.project.id,
                "name": workspace.project.name,
                "industry": workspace.project.industry,
                "goal": workspace.project.goal,
            },
            "intake": workspace.intake.model_dump(),
            "readiness": workspace.readiness.model_dump(),
            "missing_inputs": [
                item.model_dump()
                for item in workspace.readiness.missing_required + workspace.readiness.recommended_missing
            ],
            "benchmark_results": [item.model_dump() for item in benchmark],
            "fixed_benchmark_baseline": [item.model_dump() for item in benchmark],
            "attachments": _attachment_metadata(workspace),
        }
        return _bundle(
            "Produce an attachment analysis note for PLC platform selection and migration decision review. Use only attachment registration records: file name, file type, declared purpose, and upload date. State clearly that attachment file bodies have not been read or parsed. Explain what the registered materials may support, such as requirements validation, I/O scope framing, architecture review, electrical/safety readiness, benchmark confidence, migration risk review, and report drafting. Identify key missing materials and missing declared purposes. Explain how better attachment registration would help benchmark review, migration planning, and the consulting report. Recommend next actions. Never infer, summarize, quote, or claim knowledge of Excel, PDF, drawing, or document contents.",
            context,
        )

    context = _project_context(workspace, benchmark)
    context["requested_language"] = request.language
    return _bundle(
        "Produce an executive-style project summary for PLC platform selection and migration decision review. Use the supplied project goal, industry, project size, I/O scale, motion requirement, safety requirement, budget sensitivity, team experience, existing platform, candidate platforms, platform preference weights and reasons, attachment registration records, fixed benchmark baseline, readiness, and status. Cover: recommended platform based on the current ranking, ranking rationale, technical fit analysis, business/preference impact, key risks, assumptions, uncertainty, missing inputs, and next recommended actions. Explain why missing inputs matter for PLC platform selection and migration planning. State that attachment file bodies have not been parsed. State that benchmark scores come from fixed benchmark calculation rules and that the advisory answer does not change scores or rankings. Keep the tone strategic, analytical, business-oriented, engineering-grounded, concise, bilingual-compatible, and suitable for an automation migration assessment memo.",
        context,
    )


def benchmark_explanation_prompt(
    request: BenchmarkExplanationRequest,
    workspace: ProjectWorkspace,
    benchmark: list[BenchmarkResult],
) -> PromptBundle:
    context = _project_context(workspace, benchmark)
    context["requested_language"] = request.language
    return _bundle(
        "Produce an AI benchmark consultant explanation for PLC platform selection and migration decision review. Use the supplied project goal, industry, project size, I/O scale, motion requirement, safety requirement, budget sensitivity, team experience, existing platform, candidate platforms, platform preference weights and reasons, attachment registration records, fixed benchmark baseline, readiness, and status. Cover: executive-style benchmark summary, recommended platform based on the current top-ranked result, ranking rationale, technical fit analysis, business/preference impact, key risks, assumptions, uncertainty, missing inputs, and next recommended actions. State that attachment file bodies have not been parsed. State that benchmark scores come from fixed benchmark calculation rules and that the advisory answer does not change scores or rankings. Do not recalculate, replace, tune, normalize, or propose changed scores or rankings. If the result is sensitive, describe what project inputs should be validated before a decision. Keep the tone strategic, analytical, business-oriented, engineering-grounded, concise, and bilingual-compatible. Keep each paragraph self-contained for streaming display: conclusion first, then evidence, risks, assumptions, and actions.",
        context,
    )


def benchmark_analysis_prompt(
    request: BenchmarkAnalysisRequest,
    workspace: ProjectWorkspace,
    benchmark: list[BenchmarkResult],
) -> PromptBundle:
    context = _project_context(workspace, benchmark)
    context["requested_language"] = request.language
    return _bundle(
        "Produce a consulting-style benchmark analysis for automation engineers trialing the tool. Use the supplied fixed benchmark baseline as the audit baseline. Return recommended platform, ranking rationale, technical fit, preference impact, risk assessment, assumptions, uncertainty, and next actions. Explain recommendation, risks, and assumptions without marketing language. Never change scores or ranking values, and do not expose internal implementation wording.",
        context,
    )


def project_summary_prompt(
    request: ProjectSummaryRequest,
    workspace: ProjectWorkspace,
    benchmark: list[BenchmarkResult],
) -> PromptBundle:
    context = _project_context(workspace, benchmark)
    context["requested_language"] = request.language
    return _bundle(
        "Produce a concise consulting-style project summary for automation engineers trialing the tool across Overview, Benchmark, and Report surfaces. Ground the summary in project intake, readiness, report status, attachment registration information, and the fixed benchmark baseline. Identify missing information, give executable next steps, state that attachment bodies have not been parsed, and avoid promotional or generic chat language.",
        context,
    )


def report_generation_prompt(
    request: ReportGenerationRequest,
    workspace: ProjectWorkspace,
    benchmark: list[BenchmarkResult],
) -> PromptBundle:
    context = _project_context(workspace, benchmark)
    context.update(
        {
            "requested_language": request.language,
            "audience": request.audience,
            "report_sections": [
                {
                    "section_id": section.id,
                    "title": section.title.model_dump(),
                    "current_body": section.body.model_dump(),
                }
                for section in workspace.report.sections
            ],
        }
    )
    return _bundle(
        "Draft one formal PLC platform selection and migration consulting-report suggestion for every supplied report section. Preserve every supplied section_id and title exactly, in the same order. The report should read as a consultant report draft, not a chat reply. Across the supplied sections, cover Executive Summary, Project Inputs, Platform Benchmark, Preference Impact, Risk Assessment, Implementation / Migration Roadmap, and Assumptions & Uncertainty. Use professional, engineering-grounded, business-oriented language. State that attachment file bodies have not been parsed when attachments are referenced. Do not change benchmark scores or rankings. Do not expose mock, placeholder, deterministic, provider, model, API, internal, or fallback wording.",
        context,
    )


def report_section_rewrite_prompt(
    request: ReportSectionRewriteRequest,
    workspace: ProjectWorkspace,
    section: ReportSection,
    benchmark: list[BenchmarkResult],
) -> PromptBundle:
    context = {
        "requested_language": request.language,
        "audience": request.audience,
        "instruction": request.instruction,
        "project": {
            "name": workspace.project.name,
            "status": workspace.readiness.status,
            "readiness_score": workspace.readiness.score,
        },
        "benchmark_results": [item.model_dump() for item in benchmark],
        "deterministic_benchmark_baseline": [item.model_dump() for item in benchmark],
        "requested_section": {
            "section_id": section.id,
            "title": section.title.model_dump(),
            "current_body": section.body.model_dump(),
            "assumptions": [item.model_dump() for item in section.assumptions],
        },
        "attachments": _attachment_metadata(workspace),
    }
    return _bundle(
        "Rewrite only the requested section. Rewrite only the requested report section according to the user instruction and audience. Return exactly the requested section_id, one bilingual suggested_body, assumptions, and uncertainty. Preserve the factual boundary: do not change benchmark scores or rankings, do not claim attachment file bodies were read or parsed, and keep uncertainty visible. Do not include, rename, summarize, or modify any other report section. The rewrite should sound like a concise automation / PLC platform selection consulting report section, not a chat reply. Do not expose mock, placeholder, deterministic, provider, model, API, internal, or fallback wording.",
        context,
    )


def connection_test_prompt() -> PromptBundle:
    return PromptBundle(
        instructions="Return a minimal technical health response. Do not include project data or user-facing advisory language.",
        input="Connection test.",
    )


def _project_context(workspace: ProjectWorkspace, benchmark: list[BenchmarkResult]) -> dict[str, object]:
    candidate_ids = set(workspace.intake.candidate_platforms)
    return {
        "project": {
            "id": workspace.project.id,
            "name": workspace.project.name,
            "industry": workspace.project.industry,
            "goal": workspace.project.goal,
            "status": workspace.project.status,
        },
        "intake": workspace.intake.model_dump(),
        "candidate_preferences": [
            item.model_dump() for item in workspace.preferences if item.platform_id in candidate_ids
        ],
        "benchmark_results": [item.model_dump() for item in benchmark],
        "deterministic_benchmark_baseline": [item.model_dump() for item in benchmark],
        "readiness": workspace.readiness.model_dump(),
        "report_status": {
            "status": workspace.report.status,
            "version": workspace.report.version,
        },
        "attachments": _attachment_metadata(workspace),
    }


def _attachment_metadata(workspace: ProjectWorkspace) -> list[dict[str, object]]:
    return [
        {
            "id": item.id,
            "file_name": item.file_name,
            "file_type": item.file_type,
            "declared_purpose": item.declared_purpose,
            "uploaded_at": item.uploaded_at,
            "content_parsed": False,
        }
        for item in workspace.attachments
    ]


def _bundle(task: str, context: dict[str, object]) -> PromptBundle:
    return PromptBundle(
        instructions=f"{COMMON_BOUNDARIES}\n\nTask: {task}",
        input=json.dumps(context, ensure_ascii=False, separators=(",", ":")),
    )
