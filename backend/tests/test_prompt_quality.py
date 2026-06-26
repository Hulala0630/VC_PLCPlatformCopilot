from pathlib import Path
import sys
import unittest


BACKEND_ROOT = Path(__file__).resolve().parents[1]
if str(BACKEND_ROOT) not in sys.path:
    sys.path.insert(0, str(BACKEND_ROOT))

from app.data import ECOSYSTEMS
from app.intelligence.models import (
    BenchmarkExplanationRequest,
    GlobalChatRequest,
    ProjectAnalysisRequest,
    ProjectChatRequest,
    ReportGenerationRequest,
    ReportSectionRewriteRequest,
)
from app.intelligence.prompts import (
    COMMON_BOUNDARIES,
    benchmark_explanation_prompt,
    global_chat_prompt,
    project_analysis_prompt,
    project_chat_prompt,
    report_generation_prompt,
    report_section_rewrite_prompt,
)
from app.services import create_benchmark
from tests.test_openai_provider import workspace_fixture


class PromptQualityTests(unittest.TestCase):
    def test_common_boundaries_explicitly_prohibit_plc_execution_work(self) -> None:
        lowered = COMMON_BOUNDARIES.lower()
        self.assertIn("not a plc programming tool", lowered)
        self.assertIn("not a plc code converter", lowered)
        self.assertIn("not connected to any plc", lowered)
        self.assertIn("never generate plc program code", lowered)
        self.assertIn("direct controller-connection instructions", lowered)

    def test_attachment_prompts_do_not_invite_body_content_claims(self) -> None:
        workspace = workspace_fixture()
        benchmark = create_benchmark(workspace)
        prompts = [
            project_chat_prompt(ProjectChatRequest(question="Review attachments", language="en"), workspace, benchmark),
            project_analysis_prompt(ProjectAnalysisRequest(language="en", focus="attachments"), workspace, benchmark),
            report_generation_prompt(ReportGenerationRequest(language="en", audience="technical"), workspace, benchmark),
            report_section_rewrite_prompt(
                ReportSectionRewriteRequest(instruction="Tighten", language="en", audience="technical"),
                workspace,
                workspace.report.sections[0],
                benchmark,
            ),
        ]
        for prompt in prompts:
            with self.subTest(instructions=prompt.instructions):
                lowered = prompt.instructions.lower()
                self.assertIn("attachment", lowered)
                self.assertIn("have not been opened, parsed, read, summarized, or understood", lowered)
                self.assertNotIn("analyze attachment content", lowered)
                self.assertNotIn("summarize attachment content", lowered)
                self.assertNotIn("extract from attachment", lowered)
                self.assertNotIn("quote attachment", lowered)
                self.assertIn('"content_parsed":false', prompt.input)
                self.assertNotIn("file_content", prompt.input)

    def test_workflow_prompts_use_consulting_output_shape(self) -> None:
        workspace = workspace_fixture()
        benchmark = create_benchmark(workspace)
        prompts = [
            global_chat_prompt(GlobalChatRequest(question="Compare", language="en"), ECOSYSTEMS[:2]),
            project_chat_prompt(ProjectChatRequest(question="Why?", language="en"), workspace, benchmark),
            project_analysis_prompt(ProjectAnalysisRequest(language="en"), workspace, benchmark),
            benchmark_explanation_prompt(BenchmarkExplanationRequest(language="en"), workspace, benchmark),
        ]
        for prompt in prompts:
            lowered = prompt.instructions.lower()
            self.assertIn("industrial automation consultant", lowered)
            self.assertIn("separate facts, auditable assumptions, uncertainties, and recommendations", lowered)
            self.assertIn("natural zh and en", lowered)
            self.assertIn("streaming display", lowered)
            self.assertIn("conclusion first", lowered)

    def test_benchmark_and_summary_prompts_are_consultant_prompts(self) -> None:
        workspace = workspace_fixture()
        benchmark = create_benchmark(workspace)
        prompts = [
            project_analysis_prompt(ProjectAnalysisRequest(language="en"), workspace, benchmark),
            benchmark_explanation_prompt(BenchmarkExplanationRequest(language="en"), workspace, benchmark),
        ]
        required_instruction_terms = (
            "senior industrial automation consultant",
            "plc platform selection and migration decision advisor",
            "executive-style",
            "recommended platform",
            "ranking rationale",
            "technical fit analysis",
            "business/preference impact",
            "key risks",
            "assumptions",
            "uncertainty",
            "missing inputs",
            "next recommended actions",
            "attachment file bodies have not been parsed",
            "fixed benchmark calculation rules",
            "does not change scores or rankings",
            "strategic",
            "analytical",
            "business-oriented",
            "engineering-grounded",
            "concise",
            "bilingual-compatible",
            "streaming",
            "conclusion first",
        )
        required_input_terms = (
            '"goal"',
            '"industry"',
            '"project_size"',
            '"io_scale"',
            '"motion_requirement"',
            '"safety_requirement"',
            '"budget_sensitivity"',
            '"team_experience"',
            '"existing_platform"',
            '"candidate_platforms"',
            '"candidate_preferences"',
            '"user_reason_note"',
            '"attachments"',
            '"content_parsed":false',
            '"deterministic_benchmark_baseline"',
            '"readiness"',
            '"status"',
        )
        boundary_terms = (
            "not connected to any plc",
            "never generate plc program code",
            "plc code conversion",
            "do not expose internal implementation terms",
        )
        for prompt in prompts:
            lowered = prompt.instructions.lower()
            with self.subTest(instructions=prompt.instructions):
                for term in required_instruction_terms:
                    self.assertIn(term, lowered)
                for term in required_input_terms:
                    self.assertIn(term, prompt.input)
                for term in boundary_terms:
                    self.assertIn(term, lowered)
        benchmark_lowered = prompts[1].instructions.lower()
        self.assertIn("do not recalculate", benchmark_lowered)
        self.assertIn("replace, tune, normalize", benchmark_lowered)

    def test_report_generation_prompt_requires_preserved_section_identity(self) -> None:
        workspace = workspace_fixture()
        prompt = report_generation_prompt(
            ReportGenerationRequest(language="en", audience="executive"),
            workspace,
            create_benchmark(workspace),
        )
        lowered = prompt.instructions.lower()
        self.assertIn("preserve every supplied section_id and title exactly", lowered)
        self.assertIn("same order", lowered)
        for section in workspace.report.sections:
            self.assertIn(section.id, prompt.input)
            self.assertIn(section.title.en, prompt.input)

    def test_section_rewrite_prompt_only_contains_target_section(self) -> None:
        workspace = workspace_fixture()
        target = workspace.report.sections[0]
        prompt = report_section_rewrite_prompt(
            ReportSectionRewriteRequest(instruction="Make concise", language="en", audience="management"),
            workspace,
            target,
            create_benchmark(workspace),
        )
        lowered = prompt.instructions.lower()
        self.assertIn("rewrite only the requested section", lowered)
        self.assertIn("do not include, rename, summarize, or modify any other report section", lowered)
        self.assertIn(target.id, prompt.input)
        for other in workspace.report.sections[1:]:
            self.assertNotIn(other.id, prompt.input)


if __name__ == "__main__":
    unittest.main()
