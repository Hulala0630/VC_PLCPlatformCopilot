from datetime import UTC, datetime
from hashlib import sha256
from typing import Protocol

from app.intelligence.models import (
    BenchmarkExplanationRequest,
    GeneratedReportSection,
    GlobalChatRequest,
    IntelligenceResponse,
    IntelligenceSource,
    ProjectAnalysisRequest,
    ProjectChatRequest,
    ReportGenerationRequest,
    ReportGenerationResponse,
    ReportSectionRewriteRequest,
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
    ) -> IntelligenceResponse: ...


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
                en=f"Compare {names} using the platform profile dimensions for productivity, motion, safety, simulation, openness, talent, and cost. This answer uses deterministic platform data only.",
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
        lead = benchmark[0] if benchmark else None
        risks = ", ".join(f"{item.platform_id}: {item.risk_level}" for item in benchmark) or "not available"
        zh_risks = "；".join(f"{item.platform_id}: {item.risk_level}" for item in benchmark) or "暂无"
        attachment_text = f"{len(workspace.attachments)} metadata record(s)"
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
                    f"附件 metadata：{len(workspace.attachments)} 条。下一步：{workspace.readiness.next_action.zh}"
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
            answer = LocalizedText(
                zh=f"{lead.platform_id} 以加权分 {lead.weighted_score} 排名第一；技术分 {lead.technical_score} 占 72%，偏好分 {lead.preference_score} 占 28%。Provider 仅解释结果，不修改评分。",
                en=f"{lead.platform_id} ranks first at {lead.weighted_score}; technical score {lead.technical_score} contributes 72% and preference score {lead.preference_score} contributes 28%. The provider explains but does not modify scoring.",
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
                LocalizedText(zh="评分由确定性 benchmark service 计算。", en="Scores are calculated by the deterministic benchmark service."),
            ] + [assumption for result in benchmark for assumption in result.assumptions],
            uncertainty=self._project_uncertainty(workspace),
            missing_inputs=self._missing_inputs(workspace),
            follow_up_questions=[
                LocalizedText(zh="是否需要逐个平台解释技术分与偏好分差异？", en="Should the technical and preference score differences be explained platform by platform?"),
            ],
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
                LocalizedText(zh="生成内容是建议稿，不会自动保存。", en="Generated content is a suggestion and is not saved automatically."),
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
    ) -> IntelligenceResponse:
        lead = benchmark[0] if benchmark else None
        return self._response(
            scope="report_section",
            key=f"report-rewrite:{workspace.project.id}:{section.id}:{request.audience}:{request.instruction}",
            answer=LocalizedText(
                zh=f"[{request.audience} 改写建议] {section.body.zh} 重点结论：{lead.platform_id if lead else '尚无 benchmark 领先平台'}。用户指令：{request.instruction}。",
                en=f"[{request.audience} rewrite suggestion] {section.body.en} Key conclusion: {lead.platform_id if lead else 'no benchmark lead yet'}. User instruction: {request.instruction}.",
            ),
            sources=[self._report_source(section)] + [self._benchmark_source(item) for item in benchmark],
            assumptions=self._project_assumptions(workspace) + [
                LocalizedText(zh="改写建议不会自动保存到报告分区。", en="The rewrite suggestion is not saved to the report section automatically."),
            ],
            uncertainty=self._project_uncertainty(workspace),
            missing_inputs=self._missing_inputs(workspace),
            follow_up_questions=[
                LocalizedText(zh="是否由用户确认后再应用此改写？", en="Should the user review and apply this rewrite?"),
            ],
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
                zh="附件元信息已登记，但文件内容未被解析。",
                en="Attachment metadata was registered, but file content was not parsed.",
            ),
        )

    def _base_assumptions(self) -> list[LocalizedText]:
        return [
            LocalizedText(zh="响应由确定性 placeholder 生成，未调用 AI。", en="The response was generated by a deterministic placeholder; no AI was called."),
        ]

    def _project_assumptions(self, workspace: ProjectWorkspace) -> list[LocalizedText]:
        assumptions = self._base_assumptions()
        assumptions.append(
            LocalizedText(
                zh="附件元信息已登记，但文件内容未被解析。" if workspace.attachments else "未登记附件；也未解析任何文件内容。",
                en="Attachment metadata was registered, but file content was not parsed." if workspace.attachments else "No attachments were registered and no file content was parsed.",
            )
        )
        return assumptions

    def _project_uncertainty(self, workspace: ProjectWorkspace) -> list[LocalizedText]:
        uncertainty = [
            LocalizedText(zh="结论仅基于当前结构化项目数据和确定性 benchmark。", en="Conclusions use only current structured project data and the deterministic benchmark."),
        ]
        if not workspace.attachments:
            uncertainty.append(LocalizedText(zh="没有附件 metadata 可供参考。", en="No attachment metadata is available for reference."))
        return uncertainty

    def _missing_inputs(self, workspace: ProjectWorkspace) -> list[LocalizedText]:
        return workspace.readiness.missing_required + workspace.readiness.recommended_missing

    def _id(self, key: str) -> str:
        return f"intel-{sha256(key.encode('utf-8')).hexdigest()[:16]}"

    def _now(self) -> str:
        return datetime.now(UTC).isoformat()
