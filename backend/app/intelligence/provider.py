from datetime import UTC, datetime
from hashlib import sha256
from typing import Protocol

from app.intelligence.models import (
    BenchmarkAnalysisRequest,
    BenchmarkAnalysisResponse,
    BenchmarkExplanationRequest,
    GeneratedReportSection,
    GlobalChatRequest,
    IntelligenceResponse,
    IntelligenceSource,
    ProjectAnalysisRequest,
    ProjectChatRequest,
    ProjectSummaryRequest,
    ProjectSummaryResponse,
    ReportGenerationRequest,
    ReportGenerationResponse,
    ReportSectionRewriteRequest,
    ReportSectionRewriteResponse,
)
from app.models import BenchmarkResult, LocalizedText, PlcEcosystem, ProjectWorkspace, ReportSection


class IntelligenceProvider(Protocol):
    mode: str

    def global_chat(self, request: GlobalChatRequest, platforms: list[PlcEcosystem]) -> IntelligenceResponse: ...

    def project_chat(
        self,
        request: ProjectChatRequest,
        workspace: ProjectWorkspace,
        benchmark: list[BenchmarkResult],
    ) -> IntelligenceResponse: ...

    def analyze_project(
        self,
        request: ProjectAnalysisRequest,
        workspace: ProjectWorkspace,
        benchmark: list[BenchmarkResult],
    ) -> IntelligenceResponse: ...

    def explain_benchmark(
        self,
        request: BenchmarkExplanationRequest,
        workspace: ProjectWorkspace,
        benchmark: list[BenchmarkResult],
    ) -> IntelligenceResponse: ...

    def analyze_benchmark(
        self,
        request: BenchmarkAnalysisRequest,
        workspace: ProjectWorkspace,
        benchmark: list[BenchmarkResult],
    ) -> BenchmarkAnalysisResponse: ...

    def summarize_project(
        self,
        request: ProjectSummaryRequest,
        workspace: ProjectWorkspace,
        benchmark: list[BenchmarkResult],
    ) -> ProjectSummaryResponse: ...

    def generate_report(
        self,
        request: ReportGenerationRequest,
        workspace: ProjectWorkspace,
        benchmark: list[BenchmarkResult],
    ) -> ReportGenerationResponse: ...

    def rewrite_report_section(
        self,
        request: ReportSectionRewriteRequest,
        workspace: ProjectWorkspace,
        section: ReportSection,
        benchmark: list[BenchmarkResult],
    ) -> ReportSectionRewriteResponse: ...


class DeterministicPlaceholderProvider:
    mode = "deterministic_placeholder"

    def global_chat(self, request: GlobalChatRequest, platforms: list[PlcEcosystem]) -> IntelligenceResponse:
        names = ", ".join(platform.name for platform in platforms) or "no selected platforms"
        zh_names = "、".join(platform.name for platform in platforms) or "未选择平台"
        return self._response(
            scope="global",
            key=f"global:{request.question}:{','.join(item.id for item in platforms)}",
            answer=LocalizedText(
                zh=f"可基于平台 profile 比较 {zh_names} 的生产率、运动控制、安全、仿真、开放性、人才和成本评分。此回答仅使用确定性平台资料。",
                en=f"Compare {names} using the platform profile dimensions for productivity, motion, safety, simulation, openness, talent, and cost. The comparison uses the currently available platform information.",
            ),
            sources=[self._platform_source(platform) for platform in platforms],
            assumptions=self._base_assumptions(),
            uncertainty=[
                LocalizedText(zh="未结合具体项目约束，因此不能形成项目级推荐。", en="No project constraints were provided, so this is not a project-specific recommendation."),
            ],
            missing_inputs=[],
            follow_up_questions=[
                LocalizedText(zh="是否需要在具体项目的 I/O、运动、安全和团队背景下比较？", en="Should the comparison be grounded in a project's I/O, motion, safety, and team context?"),
            ],
        )

    def project_chat(
        self,
        request: ProjectChatRequest,
        workspace: ProjectWorkspace,
        benchmark: list[BenchmarkResult],
    ) -> IntelligenceResponse:
        lead = benchmark[0] if benchmark else None
        lead_text = lead.platform_id if lead else "no benchmark leader yet"
        lead_zh = lead.platform_id if lead else "暂无 benchmark 领先平台"
        required_count = len(workspace.readiness.missing_required)
        recommended_count = len(workspace.readiness.recommended_missing)
        gap_summary = self._gap_summary(workspace)
        return self._response(
            scope="project",
            key=f"project-chat:{workspace.project.id}:{request.question}",
            answer=LocalizedText(
                zh=(
                    f"当前项目处于 {workspace.readiness.status}，成熟度 {workspace.readiness.score}%。"
                    f"必补缺口 {required_count} 项，建议补充 {recommended_count} 项；优先动作：{workspace.readiness.next_action.zh} "
                    f"这些缺口会影响候选 PLC 平台的适配判断、迁移风险评估、停机窗口和团队实施可行性。"
                    f"当前 benchmark 领先项为 {lead_zh}；分数来自固定 benchmark 计算规则，本回答只解释项目状态，不改变评分或排名。"
                    f"附件正文当前未解析，只能参考附件名称、类型和用途登记。{gap_summary.zh}"
                ),
                en=(
                    f"The project is {workspace.readiness.status} with {workspace.readiness.score}% readiness. "
                    f"There are {required_count} required gap(s) and {recommended_count} recommended gap(s); priority action: {workspace.readiness.next_action.en} "
                    f"These gaps affect PLC platform fit, migration risk, downtime planning, and team execution feasibility. "
                    f"Current benchmark leader: {lead_text}. Scores come from fixed benchmark calculation rules; this answer explains the project state and does not change scores or rankings. "
                    f"Attachment bodies have not been parsed; only registered names, types, and purposes are available. {gap_summary.en}"
                ),
            ),
            sources=self._project_sources(workspace, benchmark),
            assumptions=self._project_assumptions(workspace),
            uncertainty=self._project_uncertainty(workspace),
            missing_inputs=self._missing_inputs(workspace),
            follow_up_questions=[
                LocalizedText(zh="请确认 I/O 规模、现有 PLC 平台、停机窗口、团队经验和强制约束是否已经完整。", en="Please confirm whether I/O scale, existing PLC platform, downtime window, team experience, and hard constraints are complete."),
                LocalizedText(zh="是否需要按缺口优先级整理一份选型评审资料清单？", en="Should the missing inputs be turned into a prioritized decision-review checklist?"),
            ],
        )

    def analyze_project(
        self,
        request: ProjectAnalysisRequest,
        workspace: ProjectWorkspace,
        benchmark: list[BenchmarkResult],
    ) -> IntelligenceResponse:
        if request.focus == "attachments":
            return self._analyze_attachments(request, workspace)

        lead = benchmark[0] if benchmark else None
        risks = ", ".join(f"{item.platform_id}: {item.risk_level}" for item in benchmark) or "not available"
        zh_risks = "；".join(f"{item.platform_id}: {item.risk_level}" for item in benchmark) or "暂无"
        attachment_text = f"{len(workspace.attachments)} registered attachment reference(s)"
        candidates = ", ".join(workspace.intake.candidate_platforms) or "none"
        zh_candidates = "、".join(workspace.intake.candidate_platforms) or "暂无"
        preference_impact = lead.preference_score if lead else 0
        gap_summary = self._gap_summary(workspace)
        return self._response(
            scope="project_analysis",
            key=f"project-analysis:{workspace.project.id}:{workspace.project.updated_at}",
            answer=LocalizedText(
                zh=(
                    f"项目状态：{workspace.readiness.status}；成熟度：{workspace.readiness.score}%；候选平台：{zh_candidates}。"
                    f"当前 benchmark 领先：{lead.platform_id if lead else '暂无'}；领先平台偏好分：{preference_impact}；风险分布：{zh_risks}。"
                    f"主要缺口：{gap_summary.zh} 缺口会削弱对 PLC 平台适配性、迁移工作量、停机风险、人员能力和约束条件的判断。"
                    f"建议下一步补齐：{workspace.readiness.next_action.zh} 同时核对需求说明、I/O 清单、现有架构、停机窗口、供应链/成本约束和团队经验。"
                    f"附件记录 {len(workspace.attachments)} 条；附件正文当前未解析。Benchmark 分数来自固定计算规则，本分析不改变评分或排名。"
                ),
                en=(
                    f"Project state: {workspace.readiness.status}; readiness: {workspace.readiness.score}%; candidate platforms: {candidates}. "
                    f"Current benchmark leader: {lead.platform_id if lead else 'none'}; leader preference score: {preference_impact}; risk distribution: {risks}. "
                    f"Main gaps: {gap_summary.en} These gaps reduce confidence in PLC platform fit, migration effort, downtime risk, team capability, and hard constraints. "
                    f"Next, complete: {workspace.readiness.next_action.en} Also confirm requirements, I/O list, current architecture, downtime window, supply/cost constraints, and team experience. "
                    f"Attachments: {attachment_text}; attachment bodies have not been parsed. Benchmark scores come from fixed calculation rules; this analysis does not change scores or rankings."
                ),
            ),
            sources=self._project_sources(workspace, benchmark),
            assumptions=self._project_assumptions(workspace),
            uncertainty=self._project_uncertainty(workspace),
            missing_inputs=self._missing_inputs(workspace),
            follow_up_questions=[
                LocalizedText(zh="哪些缺口会成为本次 PLC 迁移的硬约束：停机窗口、预算、供应链、标准化要求还是人员能力？", en="Which gaps are hard constraints for this PLC migration: downtime, budget, supply chain, standardization, or team capability?"),
                LocalizedText(zh="是否已有需求说明、I/O 清单、现有控制架构和风险/停机计划可登记？", en="Are requirements, I/O list, current control architecture, and risk/downtime plans available to register?"),
            ],
        )

    def explain_benchmark(
        self,
        request: BenchmarkExplanationRequest,
        workspace: ProjectWorkspace,
        benchmark: list[BenchmarkResult],
    ) -> IntelligenceResponse:
        if benchmark:
            lead = benchmark[0]
            runner_up = benchmark[1] if len(benchmark) > 1 else None
            sensitivity = (
                "Preference changes can alter the ranking when weighted scores are close."
                if runner_up and lead.weighted_score - runner_up.weighted_score <= 5
                else "The current lead is not highly sensitive to small preference changes."
            )
            margin_text = (
                f" It leads {runner_up.platform_id} by {lead.weighted_score - runner_up.weighted_score} point(s)."
                if runner_up
                else ""
            )
            margin_zh = (
                f" 相比第二名 {runner_up.platform_id} 领先 {lead.weighted_score - runner_up.weighted_score} 分。"
                if runner_up
                else ""
            )
            answer = LocalizedText(
                zh=(
                    f"建议优先评审 {lead.platform_id}：它以加权分 {lead.weighted_score} 排名第一，风险等级为 {lead.risk_level}。{margin_zh}"
                    f"排名依据是固定 benchmark 基线：技术分 {lead.technical_score} 按 72% 权重、业务/偏好分 {lead.preference_score} 按 28% 权重进入计算；本说明不改变评分或排名。"
                    f"工程上应复核 I/O 规模、运动/安全要求、现有平台、团队经验和约束条件；业务上应确认预算敏感度、供应链、标准化要求和停机窗口。附件正文当前未解析。"
                    f"下一步建议补齐缺失输入，并对前两名平台做迁移风险和实施资源评审。"
                ),
                en=(
                    f"Recommended platform for review: {lead.platform_id}. It ranks first at {lead.weighted_score} with {lead.risk_level} risk.{margin_text} "
                    f"The ranking uses the fixed benchmark baseline: technical score {lead.technical_score} is weighted at 72% and business/preference score {lead.preference_score} at 28%; this explanation does not change scores or rankings. "
                    f"Engineering validation should focus on I/O scale, motion/safety requirements, existing platform, team experience, and hard constraints; business validation should confirm budget sensitivity, supply chain, standardization, and downtime window. Attachment bodies have not been parsed. "
                    f"Next action: close missing inputs and review migration risk and implementation resources for the top-ranked platforms. {sensitivity}"
                ),
            )
        else:
            answer = LocalizedText(
                zh="当前没有候选平台可生成 benchmark；请先补充候选平台。",
                en="No candidate platforms are available for benchmarking; add candidates first.",
            )
        return self._response(
            scope="benchmark_explanation",
            key=f"benchmark-explanation:{workspace.project.id}:{workspace.project.updated_at}",
            answer=answer,
            sources=[self._benchmark_source(item) for item in benchmark],
            assumptions=self._base_assumptions() + [
                LocalizedText(zh="本说明采用当前 benchmark 结果；评分和排名由固定计算规则产生。", en="This explanation uses the current benchmark results; scores and rankings are produced by fixed calculation rules."),
            ],
            uncertainty=self._project_uncertainty(workspace),
            missing_inputs=self._missing_inputs(workspace),
            follow_up_questions=[
                LocalizedText(zh="是否需要逐个平台解释技术分与偏好分差异？", en="Should the technical and preference score differences be explained platform by platform?"),
            ],
        )

    def analyze_benchmark(
        self,
        request: BenchmarkAnalysisRequest,
        workspace: ProjectWorkspace,
        benchmark: list[BenchmarkResult],
    ) -> BenchmarkAnalysisResponse:
        lead = benchmark[0] if benchmark else None
        second = benchmark[1] if len(benchmark) > 1 else None
        margin = lead.weighted_score - second.weighted_score if lead and second else None
        response_id = self._id(f"benchmark-analysis:{workspace.project.id}:{workspace.project.updated_at}")
        return BenchmarkAnalysisResponse(
            id=response_id,
            request_id=response_id,
            recommended_platform=lead.platform_id if lead else None,
            ranking_rationale=LocalizedText(
                zh=(
                    f"当前排序建议优先审阅 {lead.platform_id}，加权分 {lead.weighted_score}。"
                    f"{' 与第二名差距为 ' + str(margin) + ' 分。' if margin is not None else ''}"
                    if lead
                    else "当前缺少候选平台，尚不能形成平台排序建议。"
                ),
                en=(
                    f"Review {lead.platform_id} first; it leads with weighted score {lead.weighted_score}."
                    f"{' The margin to second place is ' + str(margin) + ' point(s).' if margin is not None else ''}"
                    if lead
                    else "No candidate platform is available, so no platform ranking can be recommended yet."
                ),
            ),
            technical_fit_analysis=LocalizedText(
                zh=(
                    f"{lead.platform_id} 的技术分为 {lead.technical_score}，需结合 I/O 规模 {workspace.intake.io_scale}、运动需求 {workspace.intake.motion_requirement} 和安全需求 {workspace.intake.safety_requirement} 复核。"
                    if lead
                    else "请先补充候选平台，再评估技术适配度。"
                ),
                en=(
                    f"{lead.platform_id} has technical score {lead.technical_score}; review it against I/O scale {workspace.intake.io_scale}, motion need {workspace.intake.motion_requirement}, and safety need {workspace.intake.safety_requirement}."
                    if lead
                    else "Add candidate platforms before assessing technical fit."
                ),
            ),
            preference_impact=LocalizedText(
                zh=(
                    f"{lead.platform_id} 的偏好分为 {lead.preference_score}，反映团队经验、既有平台和业务约束对排序的影响。"
                    if lead
                    else "偏好影响将在候选平台和权重完整后生成。"
                ),
                en=(
                    f"{lead.platform_id} has preference score {lead.preference_score}, reflecting team experience, existing platform context, and business constraints."
                    if lead
                    else "Preference impact will be available after candidate platforms and weights are complete."
                ),
            ),
            risk_assessment=LocalizedText(
                zh=(
                    f"{lead.platform_id} 当前风险等级为 {lead.risk_level}。仍需确认成本、供应链、停机窗口和安全验收约束。"
                    if lead
                    else "风险评估需要候选平台和基础输入后才能形成。"
                ),
                en=(
                    f"{lead.platform_id} currently has {lead.risk_level} risk. Cost, supply-chain, downtime, and safety approval constraints still need confirmation."
                    if lead
                    else "Risk assessment requires candidate platforms and core inputs."
                ),
            ),
            assumptions=self._project_assumptions(workspace) + [assumption for item in benchmark for assumption in item.assumptions],
            uncertainty=self._project_uncertainty(workspace),
            next_actions=[
                workspace.readiness.next_action,
                LocalizedText(
                    zh="复核领先平台与第二名的分差，并确认偏好权重是否反映真实采购和维护约束。",
                    en="Review the margin between the leading platform and runner-up, and confirm preference weights reflect real procurement and maintenance constraints.",
                ),
            ],
            sources=self._project_sources(workspace, benchmark),
            baseline=[item.model_dump() for item in benchmark],
            generated_at=self._now(),
        )

    def summarize_project(
        self,
        request: ProjectSummaryRequest,
        workspace: ProjectWorkspace,
        benchmark: list[BenchmarkResult],
    ) -> ProjectSummaryResponse:
        lead = benchmark[0] if benchmark else None
        response_id = self._id(f"project-summary:{workspace.project.id}:{workspace.project.updated_at}")
        summary = (
            LocalizedText(
                zh=(
                    f"{workspace.project.name} 当前状态为 {workspace.readiness.status}，成熟度 {workspace.readiness.score}%。"
                    f"首要平台建议审阅 {lead.platform_id}，报告状态为 {workspace.report.status}。"
                    f"已登记 {len(workspace.attachments)} 条附件信息；当前未读取或解析附件正文。"
                ),
                en=(
                    f"{workspace.project.name} is {workspace.readiness.status} with {workspace.readiness.score}% readiness. "
                    f"Review {lead.platform_id} first; report status is {workspace.report.status}. "
                    f"{len(workspace.attachments)} attachment information record(s) are registered; attachment contents are not read or parsed."
                ),
            )
            if lead
            else LocalizedText(
                zh=(
                    f"{workspace.project.name} 当前状态为 {workspace.readiness.status}，成熟度 {workspace.readiness.score}%。"
                    "请先补齐候选平台以生成 benchmark。"
                ),
                en=(
                    f"{workspace.project.name} is {workspace.readiness.status} with {workspace.readiness.score}% readiness. "
                    "Add candidate platforms before generating the benchmark."
                ),
            )
        )
        return ProjectSummaryResponse(
            id=response_id,
            request_id=response_id,
            summary=summary,
            recommended_focus=[
                LocalizedText(zh="补齐缺失输入并复核 readiness 下一步。", en="Complete missing inputs and review the readiness next action."),
                LocalizedText(zh="用确定性 benchmark 作为平台讨论基线。", en="Use the deterministic benchmark as the platform discussion baseline."),
            ],
            assumptions=self._project_assumptions(workspace),
            uncertainty=self._project_uncertainty(workspace),
            next_actions=[workspace.readiness.next_action],
            sources=self._project_sources(workspace, benchmark),
            generated_at=self._now(),
        )

    def generate_report(
        self,
        request: ReportGenerationRequest,
        workspace: ProjectWorkspace,
        benchmark: list[BenchmarkResult],
    ) -> ReportGenerationResponse:
        lead = benchmark[0] if benchmark else None
        sections = [
            GeneratedReportSection(
                section_id=section.id,
                title=section.title,
                draft_body=LocalizedText(
                    zh=f"{self._safe_text(section.body.zh)} 项目状态：{workspace.readiness.status}；成熟度：{workspace.readiness.score}%；benchmark 领先平台：{lead.platform_id if lead else '暂无'}。附件正文当前未解析；评分和排名来自固定 benchmark 计算规则，本报告建议不改变评分或排名。",
                    en=f"{self._safe_text(section.body.en)} Project status: {workspace.readiness.status}; readiness: {workspace.readiness.score}%; benchmark leader: {lead.platform_id if lead else 'none'}. Attachment bodies have not been parsed; scores and rankings come from fixed benchmark calculation rules, and this report suggestion does not change them.",
                ),
            )
            for section in workspace.report.sections
        ]
        response_id = self._id(f"report-generation:{workspace.project.id}:{request.audience}:{workspace.report.version}")
        return ReportGenerationResponse(
            id=response_id,
            request_id=response_id,
            audience=request.audience,
            sections=sections,
            sources=self._project_sources(workspace, benchmark, include_report=True),
            assumptions=self._project_assumptions(workspace) + [
                LocalizedText(zh="报告内容是待确认建议，需审核后采用。", en="Report content is a suggestion pending review and approval."),
            ],
            uncertainty=self._project_uncertainty(workspace),
            missing_inputs=self._missing_inputs(workspace),
            generated_at=self._now(),
        )

    def rewrite_report_section(
        self,
        request: ReportSectionRewriteRequest,
        workspace: ProjectWorkspace,
        section: ReportSection,
        benchmark: list[BenchmarkResult],
    ) -> ReportSectionRewriteResponse:
        lead = benchmark[0] if benchmark else None
        response_id = self._id(
            f"report-rewrite:{workspace.project.id}:{section.id}:{request.audience}:{request.instruction}"
        )
        return ReportSectionRewriteResponse(
            id=response_id,
            request_id=response_id,
            section_id=section.id,
            suggested_body=LocalizedText(
                zh=f"{self._safe_text(section.body.zh)} 重点结论：{lead.platform_id if lead else '尚无 benchmark 领先平台'}。改写要求：{request.instruction}。附件正文当前未解析；评分和排名来自固定 benchmark 计算规则，本改写不改变评分或排名。",
                en=f"{self._safe_text(section.body.en)} Key conclusion: {lead.platform_id if lead else 'no benchmark leader yet'}. Rewrite instruction: {request.instruction}. Attachment bodies have not been parsed; scores and rankings come from fixed benchmark calculation rules, and this rewrite does not change them.",
            ),
            sources=[self._report_source(section)] + [self._benchmark_source(item) for item in benchmark],
            assumptions=self._project_assumptions(workspace) + [
                LocalizedText(zh="改写内容是待确认建议，需审核后采用。", en="The rewritten content is a suggestion pending review and approval."),
            ],
            uncertainty=self._project_uncertainty(workspace),
            generated_at=self._now(),
        )

    def _analyze_attachments(
        self,
        request: ProjectAnalysisRequest,
        workspace: ProjectWorkspace,
    ) -> IntelligenceResponse:
        declared = [item for item in workspace.attachments if item.declared_purpose.strip()]
        missing_purpose = [item.file_name for item in workspace.attachments if not item.declared_purpose.strip()]
        registered_types = {item.file_type for item in workspace.attachments}
        expected_types = ["Requirements", "I/O List", "Architecture", "Electrical List"]
        missing_types = [item for item in expected_types if item not in registered_types]
        questions: list[LocalizedText] = []
        if missing_types:
            questions.append(
                LocalizedText(
                    zh=f"是否需要登记这些尚缺的文档类型：{'、'.join(missing_types)}？",
                    en=f"Should these missing document types be registered: {', '.join(missing_types)}?",
                )
            )
        if missing_purpose:
            questions.append(
                LocalizedText(
                    zh=f"请说明这些附件的预期用途：{'、'.join(missing_purpose)}。",
                    en=f"What are the declared purposes for: {', '.join(missing_purpose)}?",
                )
            )
        if not workspace.attachments:
            questions.append(
                LocalizedText(
                    zh="决策评审还需要登记哪些需求、I/O、架构或电气文档？",
                    en="Which requirements, I/O, architecture, or electrical documents should be registered for the decision review?",
                )
            )
        return self._response(
            scope="project_analysis",
            key=f"attachment-analysis:{workspace.project.id}:{workspace.project.updated_at}",
            answer=LocalizedText(
                zh=f"已登记 {len(workspace.attachments)} 条附件记录，其中 {len(declared)} 条声明了用途。项目输入包含 {workspace.intake.io_scale} 个 I/O 和 {len(workspace.intake.candidate_platforms)} 个候选平台，成熟度为 {workspace.readiness.score}%。当前尚未读取附件正文；因此只能判断资料登记完整性，不能引用文件内容。Benchmark 分数来自固定计算规则，本分析不改变评分或排名。",
                en=f"{len(workspace.attachments)} attachment record(s) are registered and {len(declared)} include a declared purpose. Project inputs include {workspace.intake.io_scale} I/O points and {len(workspace.intake.candidate_platforms)} candidate platforms; readiness is {workspace.readiness.score}%. Attachment contents have not yet been read; attachment bodies have not been parsed, so this can assess registration completeness only and cannot cite file content. Benchmark scores come from fixed calculation rules; this analysis does not change scores or rankings.",
            ),
            sources=self._project_sources(workspace, []),
            assumptions=self._project_assumptions(workspace),
            uncertainty=self._project_uncertainty(workspace),
            missing_inputs=self._missing_inputs(workspace),
            follow_up_questions=questions,
        )

    def _response(
        self,
        *,
        scope: str,
        key: str,
        answer: LocalizedText,
        sources: list[IntelligenceSource],
        assumptions: list[LocalizedText],
        uncertainty: list[LocalizedText],
        missing_inputs: list[LocalizedText],
        follow_up_questions: list[LocalizedText],
    ) -> IntelligenceResponse:
        response_id = self._id(key)
        return IntelligenceResponse(
            id=response_id,
            request_id=response_id,
            scope=scope,
            answer=answer,
            sources=sources,
            assumptions=assumptions,
            uncertainty=uncertainty,
            missing_inputs=missing_inputs,
            follow_up_questions=follow_up_questions,
            generated_at=self._now(),
        )

    def _project_sources(
        self,
        workspace: ProjectWorkspace,
        benchmark: list[BenchmarkResult],
        *,
        include_report: bool = False,
    ) -> list[IntelligenceSource]:
        sources = [
            IntelligenceSource(
                id=f"intake:{workspace.project.id}",
                type="project_intake",
                label=LocalizedText(zh="项目输入", en="Project intake"),
                detail=LocalizedText(
                    zh=f"I/O {workspace.intake.io_scale}，候选平台 {len(workspace.intake.candidate_platforms)} 个。",
                    en=f"I/O {workspace.intake.io_scale}; {len(workspace.intake.candidate_platforms)} candidate platform(s).",
                ),
            ),
            IntelligenceSource(
                id=f"preferences:{workspace.project.id}",
                type="platform_preference",
                label=LocalizedText(zh="平台偏好", en="Platform preferences"),
                detail=LocalizedText(
                    zh=f"已登记 {len(workspace.preferences)} 个偏好权重。",
                    en=f"{len(workspace.preferences)} preference weight(s) registered.",
                ),
            ),
            IntelligenceSource(
                id=f"readiness:{workspace.project.id}",
                type="project_readiness",
                label=LocalizedText(zh="项目成熟度", en="Project readiness"),
                detail=LocalizedText(
                    zh=f"{workspace.readiness.score}% / {workspace.readiness.status}",
                    en=f"{workspace.readiness.score}% / {workspace.readiness.status}",
                ),
            ),
            IntelligenceSource(
                id=f"report-status:{workspace.project.id}",
                type="report_section",
                label=LocalizedText(zh="报告状态", en="Report status"),
                detail=LocalizedText(
                    zh=f"报告状态 {workspace.report.status}，版本 {workspace.report.version}。",
                    en=f"Report status {workspace.report.status}, version {workspace.report.version}.",
                ),
            ),
        ]
        sources.extend(self._benchmark_source(item) for item in benchmark)
        sources.extend(self._attachment_source(item.id, item.file_name) for item in workspace.attachments)
        if include_report:
            sources.extend(self._report_source(section) for section in workspace.report.sections)
        return sources

    def _platform_source(self, platform: PlcEcosystem) -> IntelligenceSource:
        return IntelligenceSource(
            id=f"platform:{platform.id}",
            type="platform_profile",
            label=LocalizedText(zh=platform.name, en=platform.name),
            detail=platform.summary,
        )

    def _benchmark_source(self, result: BenchmarkResult) -> IntelligenceSource:
        return IntelligenceSource(
            id=f"benchmark:{result.platform_id}",
            type="benchmark_result",
            label=LocalizedText(zh=f"{result.platform_id} benchmark", en=f"{result.platform_id} benchmark"),
            detail=LocalizedText(
                zh=f"技术 {result.technical_score}，偏好 {result.preference_score}，加权 {result.weighted_score}，风险 {result.risk_level}。",
                en=f"Technical {result.technical_score}, preference {result.preference_score}, weighted {result.weighted_score}, risk {result.risk_level}.",
            ),
        )

    def _report_source(self, section: ReportSection) -> IntelligenceSource:
        return IntelligenceSource(
            id=f"report:{section.id}",
            type="report_section",
            label=section.title,
            detail=LocalizedText(zh="现有报告分区内容。", en="Existing report section content."),
        )

    def _attachment_source(self, attachment_id: str, file_name: str) -> IntelligenceSource:
        return IntelligenceSource(
            id=f"attachment:{attachment_id}",
            type="attachment_metadata",
            label=LocalizedText(zh=file_name, en=file_name),
            detail=LocalizedText(
                zh="附件已按名称、类型和用途登记，当前尚未读取其内容。",
                en="The attachment is registered by name, type, and purpose; its content has not been read.",
            ),
        )

    def _base_assumptions(self) -> list[LocalizedText]:
        return [
            LocalizedText(zh="分析基于当前可用的项目输入。", en="The analysis is based on the currently available project inputs."),
        ]

    def _project_assumptions(self, workspace: ProjectWorkspace) -> list[LocalizedText]:
        assumptions = self._base_assumptions()
        assumptions.append(
            LocalizedText(
                zh="附件已按名称、类型和用途登记，当前尚未读取其内容。" if workspace.attachments else "当前未登记附件，因此没有附件内容可供评审。",
                en="Attachments are registered by name, type, and purpose; their contents have not been read." if workspace.attachments else "No attachments are registered, so no attachment content was available for review.",
            )
        )
        assumptions.append(
            LocalizedText(
                zh="Benchmark 分数和排名来自固定计算规则；本建议只解释结果，不改变评分或排名。",
                en="Benchmark scores and rankings come from fixed calculation rules; this advisory output explains the results and does not change scores or rankings.",
            )
        )
        return assumptions

    def _project_uncertainty(self, workspace: ProjectWorkspace) -> list[LocalizedText]:
        uncertainty = [
            LocalizedText(zh="结论仅基于当前项目输入和 benchmark 结果。", en="Conclusions are based only on the current project inputs and benchmark results."),
            LocalizedText(zh="成本、供应链和停机约束仍需由项目团队确认。", en="Cost, supply-chain, and downtime constraints still require project-team confirmation."),
        ]
        if not workspace.attachments:
            uncertainty.append(LocalizedText(zh="当前没有已登记附件可供参考。", en="No registered attachments are currently available for reference."))
        return uncertainty

    def _gap_summary(self, workspace: ProjectWorkspace) -> LocalizedText:
        missing = self._missing_inputs(workspace)
        if not missing:
            return LocalizedText(
                zh="当前没有必补缺口；建议复核约束、附件登记和报告结论是否足以支持评审。",
                en="No required gap is currently open; review constraints, attachment registration, and report conclusions before decision review.",
            )
        top = missing[:4]
        zh_items = "、".join(item.zh for item in top)
        en_items = "; ".join(item.en for item in top)
        remaining = len(missing) - len(top)
        if remaining > 0:
            return LocalizedText(
                zh=f"{zh_items}，另有 {remaining} 项待补。",
                en=f"{en_items}; plus {remaining} additional gap(s).",
            )
        return LocalizedText(zh=f"{zh_items}。", en=f"{en_items}.")

    def _safe_text(self, value: str) -> str:
        replacements = {
            "mock-data": "decision-support",
            "mock data": "decision-support",
            "mock": "baseline",
            "internal": "project",
            "dev wording": "draft wording",
            "developer wording": "draft wording",
        }
        cleaned = value
        for source, target in replacements.items():
            cleaned = cleaned.replace(source, target)
            cleaned = cleaned.replace(source.title(), target)
            cleaned = cleaned.replace(source.upper(), target.upper())
        return cleaned

    def _missing_inputs(self, workspace: ProjectWorkspace) -> list[LocalizedText]:
        return workspace.readiness.missing_required + workspace.readiness.recommended_missing

    def _id(self, key: str) -> str:
        return f"intel-{sha256(key.encode('utf-8')).hexdigest()[:16]}"

    def _now(self) -> str:
        return datetime.now(UTC).isoformat()
