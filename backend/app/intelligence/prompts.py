from dataclasses import dataclass
import json

from app.intelligence.models import (
    BenchmarkExplanationRequest,
    GlobalChatRequest,
    ProjectAnalysisRequest,
    ProjectChatRequest,
    ReportGenerationRequest,
    ReportSectionRewriteRequest,
)
from app.models import BenchmarkResult, PlcEcosystem, ProjectWorkspace, ReportSection


@dataclass(frozen=True)
class PromptBundle:
    instructions: str
    input: str


COMMON_BOUNDARIES = """
You are a PLC platform decision-support writing assistant.
Treat all deterministic benchmark scores as immutable source data: explain them, never recalculate or replace them.
State assumptions and uncertainty clearly.
Attachments are metadata only; never claim file content was parsed or understood.
Do not generate PLC code, PLC code conversion, or claim direct PLC connectivity.
Return only the requested structured response. Output both zh and en LocalizedText fields; prioritize the requested language.
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
    return _bundle("Answer the global platform comparison question using platform profiles only.", context)


def project_chat_prompt(
    request: ProjectChatRequest,
    workspace: ProjectWorkspace,
    benchmark: list[BenchmarkResult],
) -> PromptBundle:
    context = _project_context(workspace, benchmark)
    context.update({"question": request.question, "requested_language": request.language})
    return _bundle("Answer the project question using only the supplied structured project facts.", context)


def project_analysis_prompt(
    request: ProjectAnalysisRequest,
    workspace: ProjectWorkspace,
    benchmark: list[BenchmarkResult],
) -> PromptBundle:
    context = _project_context(workspace, benchmark)
    context["requested_language"] = request.language
    return _bundle(
        "Summarize lifecycle, readiness, missing inputs, candidates, preference influence, benchmark lead, risks, attachment metadata status, and next action.",
        context,
    )


def benchmark_explanation_prompt(
    request: BenchmarkExplanationRequest,
    workspace: ProjectWorkspace,
    benchmark: list[BenchmarkResult],
) -> PromptBundle:
    context = {
        "requested_language": request.language,
        "project_id": workspace.project.id,
        "candidate_platforms": workspace.intake.candidate_platforms,
        "benchmark_results": [item.model_dump() for item in benchmark],
    }
    return _bundle("Explain the supplied benchmark scores and preference influence without changing any score.", context)


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
        "Draft one suggestion for every supplied report section. Preserve section_id and title exactly. Suggestions are not persisted automatically.",
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
        "requested_section": {
            "section_id": section.id,
            "title": section.title.model_dump(),
            "current_body": section.body.model_dump(),
            "assumptions": [item.model_dump() for item in section.assumptions],
        },
        "attachment_metadata_count": len(workspace.attachments),
    }
    return _bundle(
        "Rewrite only the requested section. Return a suggestion only; do not propose mutations to other sections.",
        context,
    )


def connection_test_prompt() -> PromptBundle:
    return PromptBundle(
        instructions="Return a minimal response confirming the provider request can complete. Do not include project data.",
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
        "readiness": workspace.readiness.model_dump(),
        "report_status": {
            "status": workspace.report.status,
            "version": workspace.report.version,
        },
        "attachments": [
            {
                "id": item.id,
                "file_name": item.file_name,
                "file_type": item.file_type,
                "declared_purpose": item.declared_purpose,
                "uploaded_at": item.uploaded_at,
                "content_parsed": False,
            }
            for item in workspace.attachments
        ],
    }


def _bundle(task: str, context: dict[str, object]) -> PromptBundle:
    return PromptBundle(
        instructions=f"{COMMON_BOUNDARIES}\n\nTask: {task}",
        input=json.dumps(context, ensure_ascii=False, separators=(",", ":")),
    )
