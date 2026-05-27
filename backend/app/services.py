from app.data import ECOSYSTEMS
from app.models import BenchmarkResult, LocalizedText, ProjectWorkspace


def _average_score(values: list[int]) -> int:
    return round(sum(values) / len(values))


def create_benchmark(workspace: ProjectWorkspace) -> list[BenchmarkResult]:
    results: list[BenchmarkResult] = []
    for platform in ECOSYSTEMS:
        if platform.id not in workspace.intake.candidate_platforms:
            continue
        scores = platform.scores.model_dump()
        technical = _average_score(list(scores.values()))
        preference = next((item.preference_weight for item in workspace.preferences if item.platform_id == platform.id), 50)
        weighted = round(technical * 0.72 + preference * 0.28)
        risk = "Low" if weighted >= 78 else "Medium" if weighted >= 65 else "High"
        results.append(
            BenchmarkResult(
                platform_id=platform.id,
                technical_score=technical,
                preference_score=preference,
                weighted_score=weighted,
                risk_level=risk,
                rationale=LocalizedText(
                    zh=f"{platform.name} 技术评分 {technical}，用户倾向 {preference}，综合得分 {weighted}。",
                    en=f"{platform.name} technical score {technical}, preference score {preference}, weighted score {weighted}.",
                ),
                assumptions=[
                    LocalizedText(zh="技术评分来自 mock 平台 profile。", en="Technical score comes from mock platform profiles."),
                    LocalizedText(zh="用户倾向权重占综合评分 28%。", en="User preference contributes 28% of the weighted score."),
                ],
            )
        )
    return sorted(results, key=lambda item: item.weighted_score, reverse=True)
