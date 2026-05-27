from app.models import MigrationEstimate, MigrationEstimateRequest


def estimate_migration(request: MigrationEstimateRequest) -> MigrationEstimate:
    effort = round(
        request.rewrite_effort * 0.34
        + request.testing_effort * 0.22
        + request.validation_effort * 0.18
        + request.training_effort * 0.14
        + request.downtime_risk * 0.12
        - request.reusable_assets * 0.18
    )
    normalized = max(15, min(95, effort))
    cost_level = "高 / High" if normalized > 70 else "中 / Medium" if normalized > 45 else "低 / Low"

    return MigrationEstimate(
        engineering_effort_index=normalized,
        cost_level=cost_level,
        uncertainty="中 / Medium",
        assumptions=[
            "当前估算基于 MVP mock 权重，不代表正式报价。 / Current estimate uses MVP mock weights and is not a formal quote.",
            "真实项目需要补充 I/O、HMI、安全、测试与停机窗口数据。 / Real projects need I/O, HMI, safety, test, and downtime-window data.",
        ],
    )
