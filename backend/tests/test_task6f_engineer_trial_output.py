from pathlib import Path
import sys
import unittest


BACKEND_ROOT = Path(__file__).resolve().parents[1]
if str(BACKEND_ROOT) not in sys.path:
    sys.path.insert(0, str(BACKEND_ROOT))

from app.data import ECOSYSTEMS
from app.intelligence.models import BenchmarkAnalysisRequest, GlobalChatRequest, ProjectSummaryRequest
from app.intelligence.prompts import (
    benchmark_analysis_prompt,
    global_chat_prompt,
    project_summary_prompt,
)
from app.intelligence.provider import DeterministicPlaceholderProvider
from app.models import LocalizedText
from app.services import create_benchmark
from tests.test_openai_provider import workspace_fixture


BANNED_USER_TERMS = (
    "mock",
    "placeholder",
    "deterministic",
    "provider",
    "api key",
    "model id",
    "internal",
    "fallback",
)

MARKETING_TERMS = (
    "revolutionary",
    "world-class",
    "game-changing",
    "best-in-class",
    "seamless",
)


def localized(values: list[LocalizedText]) -> str:
    return "\n".join(f"{value.zh}\n{value.en}" for value in values).lower()


class Task6FEngineerTrialOutputTests(unittest.TestCase):
    def setUp(self) -> None:
        self.provider = DeterministicPlaceholderProvider()
        self.workspace = workspace_fixture()
        self.benchmark = create_benchmark(self.workspace)

    def assert_engineer_safe(self, content: str) -> None:
        lowered = content.lower()
        for term in BANNED_USER_TERMS:
            self.assertNotIn(term, lowered)
        for term in MARKETING_TERMS:
            self.assertNotIn(term, lowered)

    def test_global_query_distinguishes_ecosystems_without_plc_execution_scope(self) -> None:
        result = self.provider.global_chat(
            GlobalChatRequest(question="Compare Siemens TwinCAT CODESYS Rockwell", language="en", use_ai=False),
            ECOSYSTEMS[:4],
        )
        content = localized([result.answer, *result.uncertainty, *result.follow_up_questions])
        for term in (
            "engineering workflow",
            "motion",
            "safety",
            "openness",
            "talent",
            "cost",
            "plc ecosystem selection advice only",
            "does not cover plc programming",
            "code conversion",
            "direct plc connection",
        ):
            self.assertIn(term, content)
        self.assert_engineer_safe(content)

    def test_benchmark_and_summary_outputs_are_trial_ready(self) -> None:
        analysis = self.provider.analyze_benchmark(
            BenchmarkAnalysisRequest(language="en", use_ai=False),
            self.workspace,
            self.benchmark,
        )
        summary = self.provider.summarize_project(
            ProjectSummaryRequest(language="en", use_ai=False),
            self.workspace,
            self.benchmark,
        )
        content = localized(
            [
                analysis.ranking_rationale,
                analysis.technical_fit_analysis,
                analysis.preference_impact,
                analysis.risk_assessment,
                summary.summary,
                *summary.recommended_focus,
                *analysis.assumptions,
                *analysis.uncertainty,
                *analysis.next_actions,
                *summary.assumptions,
                *summary.uncertainty,
                *summary.next_actions,
            ]
        )
        for term in (
            "review",
            "i/o scale",
            "motion",
            "safety",
            "team experience",
            "existing platform",
            "cost",
            "supply-chain",
            "downtime",
            "fixed benchmark",
            "does not change scores or rankings",
            "attachment",
            "not read or parsed",
        ):
            self.assertIn(term, content)
        self.assert_engineer_safe(content)

    def test_task6f_prompts_require_concrete_engineering_output(self) -> None:
        prompts = [
            global_chat_prompt(GlobalChatRequest(question="Compare ecosystems", language="en"), ECOSYSTEMS[:4]),
            benchmark_analysis_prompt(BenchmarkAnalysisRequest(language="en"), self.workspace, self.benchmark),
            project_summary_prompt(ProjectSummaryRequest(language="en"), self.workspace, self.benchmark),
        ]
        for prompt in prompts:
            lowered = prompt.instructions.lower()
            self.assertIn("automation engineer", lowered)
            self.assertIn("concrete", lowered)
            self.assertIn("not promotional", lowered)
            self.assertIn("do not expose internal implementation terms", lowered)
            self.assertIn("plc", lowered)


if __name__ == "__main__":
    unittest.main()
