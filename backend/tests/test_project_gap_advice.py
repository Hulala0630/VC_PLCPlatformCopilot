from pathlib import Path
import sys
import unittest
from unittest.mock import patch


BACKEND_ROOT = Path(__file__).resolve().parents[1]
if str(BACKEND_ROOT) not in sys.path:
    sys.path.insert(0, str(BACKEND_ROOT))

from app.intelligence import service
from app.intelligence.models import ProjectAnalysisRequest, ProjectChatRequest
from app.intelligence.openai_provider import ProviderCallError
from app.intelligence.prompts import project_analysis_prompt, project_chat_prompt
from app.intelligence.provider import DeterministicPlaceholderProvider
from app.intelligence.provider_factory import ProviderSelection
from app.services import compute_project_readiness, create_benchmark
from tests.test_openai_provider import workspace_fixture


class FailingProjectProvider:
    def project_chat(self, request, workspace, benchmark):
        raise ProviderCallError("timeout", "balanced")

    def analyze_project(self, request, workspace, benchmark):
        raise ProviderCallError("timeout", "balanced")


def incomplete_workspace():
    workspace = workspace_fixture().model_copy(deep=True)
    project = workspace.project.model_copy(update={"industry": "", "goal": ""})
    intake = workspace.intake.model_copy(
        update={
            "io_scale": 0,
            "candidate_platforms": ["siemens-tia"],
            "team_experience": "",
            "constraints": "",
            "existing_platform": "",
        }
    )
    workspace = workspace.model_copy(update={"project": project, "intake": intake, "attachments": []})
    return workspace.model_copy(update={"readiness": compute_project_readiness(workspace)})


def fallback_selection() -> ProviderSelection:
    placeholder = DeterministicPlaceholderProvider()
    return ProviderSelection(
        primary=FailingProjectProvider(),
        placeholder=placeholder,
        fallback_enabled=True,
        openai_active=True,
        configuration_valid=True,
    )


def combined_text(response) -> str:
    values = [response.answer, *response.assumptions, *response.uncertainty, *response.missing_inputs, *response.follow_up_questions]
    return "\n".join(f"{item.zh}\n{item.en}" for item in values).lower()


class ProjectGapAdviceTests(unittest.TestCase):
    def assert_gap_advice_contract(self, response) -> None:
        content = combined_text(response)
        self.assertIn("gap", content)
        self.assertIn("plc platform", content)
        self.assertIn("migration", content)
        self.assertIn("attachment bodies have not", content)
        self.assertIn("fixed", content)
        self.assertIn("benchmark", content)
        self.assertIn("does not change scores or rankings", content)
        for banned in ("placeholder", "mock", "internal", "dev wording"):
            self.assertNotIn(banned, content)

    def test_ai_off_project_answers_are_useful_gap_advice(self) -> None:
        workspace = incomplete_workspace()
        with (
            patch("app.intelligence.service.get_workspace", return_value=workspace),
            patch(
                "app.intelligence.service.get_provider_selection",
                side_effect=AssertionError("AI provider factory must not be invoked"),
            ),
        ):
            chat = service.project_chat(
                workspace.project.id,
                ProjectChatRequest(question="What is missing?", language="en", use_ai=False),
            )
            analysis = service.analyze_project(
                workspace.project.id,
                ProjectAnalysisRequest(language="en", use_ai=False),
            )

        self.assert_gap_advice_contract(chat)
        self.assert_gap_advice_contract(analysis)
        self.assertTrue(chat.missing_inputs)
        self.assertTrue(analysis.follow_up_questions)

    def test_failure_fallback_project_answers_remain_actionable(self) -> None:
        workspace = incomplete_workspace()
        with (
            patch("app.intelligence.service.get_workspace", return_value=workspace),
            patch("app.intelligence.service.get_provider_selection", return_value=fallback_selection()),
        ):
            chat = service.project_chat(
                workspace.project.id,
                ProjectChatRequest(question="What is missing?", language="en", use_ai=True),
            )
            analysis = service.analyze_project(
                workspace.project.id,
                ProjectAnalysisRequest(language="en", use_ai=True),
            )

        self.assertEqual(chat.execution_status, "ai_fallback")
        self.assertEqual(analysis.execution_status, "ai_fallback")
        self.assert_gap_advice_contract(chat)
        self.assert_gap_advice_contract(analysis)

    def test_project_prompts_require_gap_impact_and_boundary_statements(self) -> None:
        workspace = incomplete_workspace()
        benchmark = create_benchmark(workspace)
        prompts = [
            project_chat_prompt(ProjectChatRequest(question="What is missing?", language="en"), workspace, benchmark),
            project_analysis_prompt(ProjectAnalysisRequest(language="en"), workspace, benchmark),
        ]
        for prompt in prompts:
            lowered = prompt.instructions.lower()
            self.assertIn("why", lowered)
            self.assertIn("plc platform selection", lowered)
            self.assertIn("migration", lowered)
            self.assertIn("attachment file bodies have not been parsed", lowered)
            self.assertIn("fixed benchmark calculation rules", lowered)
            self.assertIn("does not change scores or rankings", lowered)


if __name__ == "__main__":
    unittest.main()
