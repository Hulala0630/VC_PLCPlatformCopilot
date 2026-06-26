from pathlib import Path
import sys
import unittest


BACKEND_ROOT = Path(__file__).resolve().parents[1]
if str(BACKEND_ROOT) not in sys.path:
    sys.path.insert(0, str(BACKEND_ROOT))

from app.intelligence.models import (
    ProjectAnalysisRequest,
    ReportGenerationRequest,
    ReportSectionRewriteRequest,
)
from app.intelligence.provider import DeterministicPlaceholderProvider
from app.models import LocalizedText
from app.services import create_benchmark
from tests.test_openai_provider import workspace_fixture


BANNED_OUTPUT_TERMS = (
    "mock",
    "placeholder",
    "deterministic",
    "provider",
    "model id",
    "api key",
    "internal",
    "fallback",
)


def localized_text(values: list[LocalizedText]) -> str:
    return "\n".join(f"{item.zh}\n{item.en}" for item in values).lower()


class AttachmentReportOutputQualityTests(unittest.TestCase):
    def setUp(self) -> None:
        self.provider = DeterministicPlaceholderProvider()
        self.workspace = workspace_fixture()
        self.benchmark = create_benchmark(self.workspace)

    def assert_no_banned_terms(self, content: str) -> None:
        lowered = content.lower()
        for term in BANNED_OUTPUT_TERMS:
            self.assertNotIn(term, lowered)

    def test_attachment_analysis_reads_like_consultant_note(self) -> None:
        result = self.provider.analyze_project(
            ProjectAnalysisRequest(language="en", focus="attachments", use_ai=False),
            self.workspace,
            self.benchmark,
        )
        content = localized_text(
            [result.answer, *result.assumptions, *result.uncertainty, *result.follow_up_questions]
        )
        self.assertIn("attachment bodies have not been read or parsed", content)
        self.assertIn("registered materials may support", content)
        self.assertIn("requirements completeness", content)
        self.assertIn("migration risk", content)
        self.assertIn("report evidence", content)
        self.assertIn("next", content)
        self.assertIn("does not change scores or rankings", content)
        self.assert_no_banned_terms(content)

    def test_report_generation_reads_like_consultant_report_draft(self) -> None:
        result = self.provider.generate_report(
            ReportGenerationRequest(language="en", audience="executive", use_ai=False),
            self.workspace,
            self.benchmark,
        )
        content = localized_text(
            [section.draft_body for section in result.sections]
            + result.assumptions
            + result.uncertainty
        )
        for term in (
            "executive summary",
            "project inputs",
            "platform benchmark",
            "preference impact",
            "risk assessment",
            "implementation / migration roadmap",
            "assumptions & uncertainty",
            "attachment bodies have not been read or parsed",
            "does not change benchmark scores or rankings",
        ):
            self.assertIn(term, content)
        self.assert_no_banned_terms(content)

    def test_report_rewrite_preserves_section_boundary_and_facts(self) -> None:
        section = self.workspace.report.sections[0]
        result = self.provider.rewrite_report_section(
            ReportSectionRewriteRequest(
                instruction="Make it executive and concise",
                language="en",
                audience="management",
                use_ai=False,
            ),
            self.workspace,
            section,
            self.benchmark,
        )
        content = localized_text([result.suggested_body, *result.assumptions, *result.uncertainty])
        self.assertEqual(result.section_id, section.id)
        self.assertIn("requested section", content)
        self.assertIn("attachment bodies have not been read or parsed", content)
        self.assertIn("does not change them", content)
        self.assertIn("assumptions", content)
        self.assertIn("uncertainty", content)
        self.assert_no_banned_terms(content)


if __name__ == "__main__":
    unittest.main()
