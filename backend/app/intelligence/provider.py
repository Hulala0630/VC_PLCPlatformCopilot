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
        lead_text = lead.platform_id if lead else "no benchmark lead"
        lead_zh = lead.platform_id if lead else "暂无 benchmark 领先平台"
        return self._response(
            scope="project",
            key=f"project-chat:{workspace.project.id}:{request.question}",
            answer=LocalizedText(
                zh=f"项目当前状态为 {workspace.readiness.status}，成熟度 {workspace.readiness.score}%。{lead_zh}。建议下一步：{workspace.readiness.next_action.zh}",
                en=f"The project is {workspace.readiness.status} with {workspace.readiness.score}% readiness. Benchmark lead: {lead_text}. Next action: {workspace.readiness.next_action.en}",
            ),
            sources=self._project_sources(workspace, benchmark),
            assumptions=self._project_assumptions(workspace),
            uncertainty=self._project_uncertainty(workspace),
            missing_inputs=self._missing_inputs(workspace),
            follow_up_questions=[
                LocalizedText(zh="是否需要进一步解释偏好权重对排名的影响？", en="Should the preference-weight impact on ranking be explained further?"),
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
        return self._response(
            scope="project_analysis",
            key=f"project-analysis:{workspace.project.id}:{workspace.project.updated_at}",
            answer=LocalizedText(
                zh=(
                    f"生命周期：{workspace.readiness.status}；成熟度：{workspace.readiness.score}%；"
                    f"候选平台：{zh_candidates}；报告状态：{workspace.report.status}；"
                    f"benchmark 领先：{lead.platform_id if lead else '暂无'}；领先平台偏好分：{preference_impact}；风险：{zh_risks}；"
                    f"附件记录：{len(workspace.attachments)} 条。下一步：{workspace.readiness.next_action.zh}"
                ),
                en=(
                    f"Lifecycle: {workspace.readiness.status}; readiness: {workspace.readiness.score}%; "
                    f"candidate platforms: {candidates}; report status: {workspace.report.status}; "
                    f"benchmark lead: {lead.platform_id if lead else 'none'}; lead preference score: {preference_impact}; risks: {risks}; "
                    f"attachments: {attachment_text}. Next action: {workspace.readiness.next_action.en}"
                ),
            ),
            sources=self._project_sources(workspace, benchmark),
            assumptions=self._project_assumptions(workspace),
            uncertainty=self._project_uncertainty(workspace),
            missing_inputs=self._missing_inputs(workspace),
            follow_up_questions=[
                LocalizedText(zh="哪些缺失输入应在决策评审前优先补齐？", en="Which missing inputs should be completed before the decision review?"),
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
            sensitivity = (
                "Preference changes can alter the ranking when weighted scores are close."
                if len(benchmark) > 1 and lead.weighted_score - benchmark[1].weighted_score <= 5
                else "The current lead is not highly sensitive to small preference changes."
            )
            answer = LocalizedText(
                zh=f"{lead.platform_id} 以加权分 {lead.weighted_score} 排名第一；技术分 {lead.technical_score} 占 72%，偏好分 {lead.preference_score} 占 28%，风险等级为 {lead.risk_level}。仅解释既有结果，不重新计算或替换评分。",
                en=f"{lead.platform_id} ranks first at {lead.weighted_score}; technical score {lead.technical_score} contributes 72%, preference score {lead.preference_score} contributes 28%, and risk is {lead.risk_level}. {sensitivity}",
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
                LocalizedText(zh="本说明采用当前 benchmark 结果及其已列出的假设。", en="This explanation uses the current benchmark results and their stated assumptions."),
            ] + [assumption for result in benchmark for assumption in result.assumptions],
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
                    zh=f"[{request.audience} 建议稿] {section.body.zh} 项目状态：{workspace.readiness.status}；成熟度：{workspace.readiness.score}%；领先平台：{lead.platform_id if lead else '暂无'}。",
                    en=f"[{request.audience} suggestion] {section.body.en} Project status: {workspace.readiness.status}; readiness: {workspace.readiness.score}%; benchmark lead: {lead.platform_id if lead else 'none'}.",
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
                zh=f"[{request.audience} 改写建议] {section.body.zh} 重点结论：{lead.platform_id if lead else '尚无 benchmark 领先平台'}。用户指令：{request.instruction}。",
                en=f"[{request.audience} rewrite suggestion] {section.body.en} Key conclusion: {lead.platform_id if lead else 'no benchmark lead yet'}. User instruction: {request.instruction}.",
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
                zh=f"已登记 {len(workspace.attachments)} 条附件记录，其中 {len(declared)} 条声明了用途。项目输入包含 {workspace.intake.io_scale} 个 I/O 和 {len(workspace.intake.candidate_platforms)} 个候选平台，成熟度为 {workspace.readiness.score}%。当前尚未读取附件内容。",
                en=f"{len(workspace.attachments)} attachment record(s) are registered and {len(declared)} include a declared purpose. Project inputs include {workspace.intake.io_scale} I/O points and {len(workspace.intake.candidate_platforms)} candidate platforms; readiness is {workspace.readiness.score}%. Attachment contents have not yet been read.",
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
        return assumptions

    def _project_uncertainty(self, workspace: ProjectWorkspace) -> list[LocalizedText]:
        uncertainty = [
            LocalizedText(zh="结论仅基于当前项目输入和 benchmark 结果。", en="Conclusions are based only on the current project inputs and benchmark results."),
            LocalizedText(zh="成本、供应链和停机约束仍需由项目团队确认。", en="Cost, supply-chain, and downtime constraints still require project-team confirmation."),
        ]
        if not workspace.attachments:
            uncertainty.append(LocalizedText(zh="当前没有已登记附件可供参考。", en="No registered attachments are currently available for reference."))
        return uncertainty

    def _missing_inputs(self, workspace: ProjectWorkspace) -> list[LocalizedText]:
        return workspace.readiness.missing_required + workspace.readiness.recommended_missing

    def _id(self, key: str) -> str:
        return f"intel-{sha256(key.encode('utf-8')).hexdigest()[:16]}"

    def _now(self) -> str:
        return datetime.now(UTC).isoformat()
