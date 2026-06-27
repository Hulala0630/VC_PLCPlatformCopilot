import type {
  BenchmarkResult,
  IntelligenceMode,
  IntelligenceExecutionStatus,
  IntelligenceQuality,
  IntelligenceResult,
  IntelligenceSource,
  Language,
  LocalizedText,
  PlatformPreference,
  PlcEcosystem,
  Project,
  ProjectAttachment,
  ProjectIntake,
  ProjectReadiness,
  ProjectStatus,
  ProjectWorkspace,
  ReportAudience,
  ReportGenerationResult,
  ReportSection,
  ReportSectionRewriteResult,
} from "../types";

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL ?? "http://127.0.0.1:8000";

type BackendPlcEcosystem = Omit<PlcEcosystem, "regionStrength" | "officialUrl"> & {
  official_url: string;
  region_strength: LocalizedText;
};

type BackendProject = Omit<Project, "createdAt" | "updatedAt"> & {
  created_at: string;
  updated_at: string;
};

type BackendProjectIntake = {
  project_size: ProjectIntake["projectSize"];
  io_scale: number;
  motion_requirement: number;
  safety_requirement: number;
  budget_sensitivity: number;
  team_experience: string;
  existing_platform: string;
  candidate_platforms: string[];
  constraints: string;
};

type BackendPlatformPreference = {
  platform_id: string;
  preference_weight: number;
  user_reason_note: string;
};

type BackendProjectAttachment = {
  id: string;
  project_id: string;
  file_name: string;
  file_type: ProjectAttachment["fileType"];
  declared_purpose: string;
  uploaded_at: string;
};

type BackendBenchmarkResult = {
  platform_id: string;
  technical_score: number;
  preference_score: number;
  weighted_score: number;
  risk_level: BenchmarkResult["riskLevel"];
  rationale: LocalizedText;
  assumptions: LocalizedText[];
};

type BackendReportSection = {
  id: string;
  title: LocalizedText;
  body: LocalizedText;
  assumptions?: LocalizedText[];
  uncertainty?: LocalizedText;
  data_sources_used?: LocalizedText[];
  last_generated_at: string;
};

type BackendProjectReadiness = {
  score: number;
  status: ProjectStatus;
  missing_required: LocalizedText[];
  recommended_missing: LocalizedText[];
  next_action: LocalizedText;
  confidence_level: ProjectReadiness["confidenceLevel"];
  reasons: LocalizedText[];
};

type BackendProjectWorkspace = {
  project: BackendProject;
  intake: BackendProjectIntake;
  preferences: BackendPlatformPreference[];
  attachments: BackendProjectAttachment[];
  report: {
    project_id: string;
    sections: BackendReportSection[];
    version: number;
    status: ProjectWorkspace["report"]["status"];
  };
  readiness?: BackendProjectReadiness;
};

type BackendIntelligenceSource = {
  id: string;
  type: string;
  label: LocalizedText;
  detail: LocalizedText;
};

type BackendIntelligenceResponse = {
  id: string;
  execution_status?: IntelligenceExecutionStatus;
  mode: IntelligenceMode;
  retryable?: boolean;
  model_profile: IntelligenceQuality | null;
  answer: LocalizedText;
  sources: BackendIntelligenceSource[];
  assumptions: LocalizedText[];
  uncertainty: LocalizedText[];
  missing_inputs: LocalizedText[];
  follow_up_questions: LocalizedText[];
  ai_used: boolean;
  document_parsing_used: false;
  generated_at: string;
};

type BackendBenchmarkAnalysisResponse = {
  id: string;
  execution_status?: IntelligenceExecutionStatus;
  mode: IntelligenceMode;
  retryable?: boolean;
  model_profile: IntelligenceQuality | null;
  recommended_platform: string | null;
  ranking_rationale: LocalizedText;
  technical_fit_analysis: LocalizedText;
  preference_impact: LocalizedText;
  risk_assessment: LocalizedText;
  assumptions: LocalizedText[];
  uncertainty: LocalizedText[];
  next_actions: LocalizedText[];
  sources: BackendIntelligenceSource[];
  ai_used: boolean;
  document_parsing_used: false;
  generated_at: string;
};

type BackendProjectSummaryResponse = {
  id: string;
  execution_status?: IntelligenceExecutionStatus;
  mode: IntelligenceMode;
  retryable?: boolean;
  model_profile: IntelligenceQuality | null;
  summary: LocalizedText;
  recommended_focus: LocalizedText[];
  assumptions: LocalizedText[];
  uncertainty: LocalizedText[];
  next_actions: LocalizedText[];
  sources: BackendIntelligenceSource[];
  ai_used: boolean;
  document_parsing_used: false;
  generated_at: string;
};

type IntelligenceStreamEvent<T> =
  | { type: "chunk"; done?: false; content?: LocalizedText }
  | { type: "done"; done: true; result: T };

type BackendReportGenerationResponse = {
  id: string;
  execution_status?: IntelligenceExecutionStatus;
  mode: IntelligenceMode;
  retryable?: boolean;
  model_profile: IntelligenceQuality | null;
  audience: ReportAudience;
  sections: Array<{
    section_id: string;
    title: LocalizedText;
    draft_body: LocalizedText;
  }>;
  sources: BackendIntelligenceSource[];
  assumptions: LocalizedText[];
  uncertainty: LocalizedText[];
  missing_inputs: LocalizedText[];
  ai_used: boolean;
  document_parsing_used: false;
  generated_at: string;
};

type BackendReportSectionRewriteResponse = {
  id: string;
  execution_status?: IntelligenceExecutionStatus;
  section_id: string;
  suggested_body: LocalizedText;
  assumptions: LocalizedText[];
  uncertainty: LocalizedText[];
  sources: BackendIntelligenceSource[];
  mode: IntelligenceMode;
  retryable?: boolean;
  model_profile: IntelligenceQuality | null;
  ai_used: boolean;
  document_parsing_used: false;
  generated_at: string;
};

export type ProjectCreatePayload = {
  name: string;
  industry: string;
  goal: string;
};

export type GlobalIntelligenceChatPayload = {
  question: string;
  language: Language;
  platformIds: string[];
  quality: IntelligenceQuality;
  useAi: boolean;
};

export type ProjectIntelligenceChatPayload = {
  question: string;
  language: Language;
  quality: IntelligenceQuality;
  useAi: boolean;
};

export type ProjectIntelligenceActionPayload = {
  language: Language;
  quality: IntelligenceQuality;
  useAi: boolean;
};

export type ReportGenerationPayload = ProjectIntelligenceActionPayload & {
  audience: ReportAudience;
};

export type ReportSectionRewritePayload = ReportGenerationPayload & {
  instruction: string;
};

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  const response = await fetch(`${API_BASE_URL}${path}`, {
    ...init,
    headers: {
      "Content-Type": "application/json",
      ...init?.headers,
    },
  });

  if (!response.ok) {
    let detail = response.statusText;
    try {
      const body = await response.json();
      detail = typeof body.detail === "string" ? body.detail : JSON.stringify(body);
    } catch {
      detail = await response.text();
    }
    throw new Error(`API ${response.status} ${response.statusText}: ${detail}`);
  }

  if (response.status === 204) {
    return undefined as T;
  }

  return response.json() as Promise<T>;
}

async function requestStream<T>(path: string, init: RequestInit, onChunk: (chunk: LocalizedText) => void): Promise<T> {
  const response = await fetch(`${API_BASE_URL}${path}`, {
    ...init,
    headers: {
      "Content-Type": "application/json",
      Accept: "text/event-stream",
      ...init.headers,
    },
  });

  if (!response.ok) {
    let detail = response.statusText;
    try {
      const body = await response.json();
      detail = typeof body.detail === "string" ? body.detail : JSON.stringify(body);
    } catch {
      detail = await response.text();
    }
    throw new Error(`API ${response.status} ${response.statusText}: ${detail}`);
  }

  if (!response.body) {
    throw new Error("Streaming response body is not available.");
  }

  const reader = response.body.getReader();
  const decoder = new TextDecoder();
  let buffer = "";
  let result: T | null = null;

  function handleBlock(block: string) {
    const dataLines = block
      .split(/\r?\n/)
      .filter((line) => line.startsWith("data:"))
      .map((line) => line.slice(5).trim());
    if (dataLines.length === 0) return;
    const event = JSON.parse(dataLines.join("\n")) as IntelligenceStreamEvent<T>;
    if (event.type === "chunk" && event.content) {
      onChunk(normalizeLocalizedText(event.content));
    }
    if (event.type === "done") {
      result = event.result;
    }
  }

  while (true) {
    const { done, value } = await reader.read();
    buffer += decoder.decode(value ?? new Uint8Array(), { stream: !done });
    const blocks = buffer.split(/\r?\n\r?\n/);
    buffer = blocks.pop() ?? "";
    blocks.forEach(handleBlock);
    if (done) break;
  }

  if (buffer.trim()) {
    handleBlock(buffer);
  }

  if (!result) {
    throw new Error("Streaming response ended without a final result.");
  }

  return result;
}

function businessString(value: string, language: Language): string {
  if (language === "zh") {
    return value
      .replace(/响应由确定性 placeholder 生成，未调用 AI。/g, "当前结果基于已登记的项目数据和评分规则生成。")
      .replace(/附件元信息已登记，但文件内容未被解析。/g, "已使用附件名称、类型和声明用途，尚未读取文件内容。")
      .replace(/结论仅基于当前结构化项目数据和确定性 benchmark。/g, "结论基于当前项目资料和已计算的评分结果。")
      .replace(/评分由确定性 benchmark service 计算。/g, "评分来自当前项目的既有评估结果。")
      .replace(/mock profiles?/gi, "当前平台基础资料")
      .replace(/mock\s*平台\s*profiles?/gi, "当前平台基础资料")
      .replace(/mock 数据/g, "当前参考数据")
      .replace(/当前参考数据决策草稿/g, "初步决策草稿")
      .replace(/本分区由前端确定性逻辑重算，未调用真实 AI，未解析附件。/g, "本分区基于当前项目评分结果形成，需结合现场信息复核。")
      .replace(/附件仅登记 metadata，当前版本不解析文件内容。/g, "当前仅参考附件名称、类型和声明用途，尚未读取文件内容。")
      .replace(/当前仅登记附件元信息，不解析文件内容。/g, "当前仅参考附件名称、类型和声明用途，尚未读取文件内容。")
      .replace(/placeholder/gi, "基础分析")
      .replace(/metadata/gi, "登记信息")
      .replace(/附件仅作为元信息来源登记。/g, "当前仅参考附件名称、类型和声明用途。")
      .replace(/元信息/g, "登记信息")
      .replace(/附件\s+登记信息/g, "附件登记信息")
      .replace(/本分析未读取或解析任何文件内容。/g, "本分析尚未读取任何文件正文或表格内容。")
      .replace(/未读取或解析任何文件内容/g, "尚未读取任何文件正文或表格内容")
      .replace(/文件内容未被解析/g, "尚未读取文件内容")
      .replace(/未解析文件内容/g, "尚未读取文件内容")
      .replace(/不解析文件内容/g, "尚未读取文件内容")
      .replace(/未解析附件/g, "尚未读取附件内容")
      .replace(/mock/gi, "当前参考")
      .replace(/确定性/g, "规则化");
  }
  return value
    .replace(/The response was generated by a deterministic placeholder; no AI was called\./gi, "The result was generated from the registered project data and scoring rules.")
    .replace(/Attachment metadata is registered, but file contents were not parsed\./gi, "File names, types, and declared purposes were used; file contents have not been read.")
    .replace(/Conclusions use only current structured project data and the deterministic benchmark\./gi, "Conclusions use the current project information and calculated scoring results.")
    .replace(/Scores are calculated by the deterministic benchmark service\./gi, "Scores come from the project's existing evaluation results.")
    .replace(/mock profiles?/gi, "current platform reference information")
    .replace(/mock\s*platform\s*profiles?/gi, "current platform reference information")
    .replace(/mock data/gi, "current reference information")
    .replace(/current reference information decision draft/gi, "initial decision draft")
    .replace(/This section was recalculated by deterministic frontend logic, with no real AI call and no file parsing\./gi, "This section reflects the current project scoring results and should be reviewed against site information.")
    .replace(/Attachments are metadata-only and are not parsed in this version\./gi, "Only attachment names, types, and declared purposes are currently referenced; file contents have not been read.")
    .replace(/Attachments are metadata-only and not parsed\./gi, "Only attachment names, types, and declared purposes are currently referenced; file contents have not been read.")
    .replace(/Inputs are maintained manually and saved to local SQLite\./gi, "Inputs are maintained manually by the user.")
    .replace(/deterministic placeholder/gi, "basic analysis")
    .replace(/placeholder/gi, "basic analysis")
    .replace(/metadata/gi, "registered information")
    .replace(/attachments? (?:are|is) registered only as registered information sources?\.?/gi, "Only attachment names, types, and declared purposes are currently referenced.")
    .replace(/attachment\s+registered information/gi, "registered attachment information")
    .replace(/This analysis did not read or parse any file contents?\./gi, "This analysis has not read any file body or table content.")
    .replace(/did not read or parse any file contents?/gi, "has not read any file body or table content")
    .replace(/file contents? (?:were|was|are|is) not parsed/gi, "file contents have not been read")
    .replace(/mock/gi, "current reference")
    .replace(/deterministic/gi, "rule-based");
}

function normalizeLocalizedText(value: LocalizedText): LocalizedText {
  return { zh: businessString(value.zh, "zh"), en: businessString(value.en, "en") };
}

function normalizeEcosystem(item: BackendPlcEcosystem): PlcEcosystem {
  return {
    id: item.id,
    name: item.name,
    vendor: item.vendor,
    software: item.software,
    officialUrl: item.official_url,
    regionStrength: item.region_strength,
    summary: item.summary,
    strengths: item.strengths,
    cautions: item.cautions,
    scores: item.scores,
  };
}

function serializeIntake(intake: ProjectIntake): BackendProjectIntake {
  return {
    project_size: intake.projectSize,
    io_scale: intake.ioScale,
    motion_requirement: intake.motionRequirement,
    safety_requirement: intake.safetyRequirement,
    budget_sensitivity: intake.budgetSensitivity,
    team_experience: intake.teamExperience,
    existing_platform: intake.existingPlatform,
    candidate_platforms: intake.candidatePlatforms,
    constraints: intake.constraints,
  };
}

function normalizeIntake(intake: BackendProjectIntake): ProjectIntake {
  return {
    projectSize: intake.project_size,
    ioScale: intake.io_scale,
    motionRequirement: intake.motion_requirement,
    safetyRequirement: intake.safety_requirement,
    budgetSensitivity: intake.budget_sensitivity,
    teamExperience: intake.team_experience,
    existingPlatform: intake.existing_platform,
    candidatePlatforms: intake.candidate_platforms,
    constraints: intake.constraints,
  };
}

function serializePreferences(preferences: PlatformPreference[]): BackendPlatformPreference[] {
  return preferences.map((item) => ({
    platform_id: item.platformId,
    preference_weight: item.preferenceWeight,
    user_reason_note: item.userReasonNote,
  }));
}

function normalizePreferences(preferences: BackendPlatformPreference[]): PlatformPreference[] {
  return preferences.map((item) => ({
    platformId: item.platform_id,
    preferenceWeight: item.preference_weight,
    userReasonNote: item.user_reason_note,
  }));
}

function normalizeAttachment(attachment: BackendProjectAttachment): ProjectAttachment {
  return {
    id: attachment.id,
    projectId: attachment.project_id,
    fileName: attachment.file_name,
    fileType: attachment.file_type,
    declaredPurpose: attachment.declared_purpose,
    uploadedAt: attachment.uploaded_at,
  };
}

function normalizeBenchmarkResult(result: BackendBenchmarkResult): BenchmarkResult {
  return {
    platformId: result.platform_id,
    technicalScore: result.technical_score,
    preferenceScore: result.preference_score,
    weightedScore: result.weighted_score,
    riskLevel: result.risk_level,
    rationale: normalizeLocalizedText(result.rationale),
    assumptions: result.assumptions.map(normalizeLocalizedText),
  };
}

function normalizeReportSection(section: BackendReportSection): ReportSection {
  return {
    id: section.id,
    title: normalizeLocalizedText(section.title),
    body: normalizeLocalizedText(section.body),
    assumptions: (section.assumptions ?? []).map(normalizeLocalizedText),
    uncertainty: normalizeLocalizedText(section.uncertainty ?? {
      zh: "当前资料尚不能覆盖所有实施条件，结论需要结合现场情况复核。",
      en: "Current information does not cover every implementation condition; conclusions should be reviewed against site conditions.",
    }),
    dataSourcesUsed: (section.data_sources_used ?? [{ zh: "当前项目资料", en: "Current project information" }]).map(normalizeLocalizedText),
    lastGeneratedAt: section.last_generated_at,
  };
}

function normalizeReadiness(readiness: BackendProjectReadiness): ProjectReadiness {
  return {
    score: readiness.score,
    status: readiness.status,
    missingRequired: readiness.missing_required.map(normalizeLocalizedText),
    recommendedMissing: readiness.recommended_missing.map(normalizeLocalizedText),
    nextAction: normalizeLocalizedText(readiness.next_action),
    confidenceLevel: readiness.confidence_level,
    reasons: readiness.reasons.map(normalizeLocalizedText),
  };
}

function normalizeIntelligenceSource(source: BackendIntelligenceSource): IntelligenceSource {
  return {
    id: source.id,
    type: source.type,
    label: normalizeLocalizedText(source.label),
    detail: normalizeLocalizedText(source.detail),
  };
}

function normalizeExecutionStatus(status: IntelligenceExecutionStatus | undefined, mode: IntelligenceMode): IntelligenceExecutionStatus {
  if (status) return status;
  if (mode === "openai") return "ai_success";
  if (mode === "deterministic_fallback") return "ai_fallback";
  return "basic_analysis";
}

function normalizeIntelligenceResponse(response: BackendIntelligenceResponse, requestedQuality: IntelligenceQuality): IntelligenceResult {
  return {
    id: response.id,
    mode: response.mode,
    executionStatus: normalizeExecutionStatus(response.execution_status, response.mode),
    retryable: response.retryable ?? false,
    qualityProfile: response.model_profile ?? requestedQuality,
    answer: normalizeLocalizedText(response.answer),
    sources: response.sources.map(normalizeIntelligenceSource),
    assumptions: response.assumptions.map(normalizeLocalizedText),
    uncertainty: response.uncertainty.map(normalizeLocalizedText),
    missingInputs: response.missing_inputs.map(normalizeLocalizedText),
    followUpQuestions: response.follow_up_questions.map(normalizeLocalizedText),
    aiUsed: response.ai_used,
    documentParsingUsed: response.document_parsing_used,
    generatedAt: response.generated_at,
  };
}

function combineBenchmarkAnswer(response: BackendBenchmarkAnalysisResponse): LocalizedText {
  return normalizeLocalizedText({
    zh: [
      response.ranking_rationale.zh,
      response.technical_fit_analysis.zh,
      response.preference_impact.zh,
      response.risk_assessment.zh,
      ...response.next_actions.map((item) => item.zh),
    ].filter(Boolean).join("\n\n"),
    en: [
      response.ranking_rationale.en,
      response.technical_fit_analysis.en,
      response.preference_impact.en,
      response.risk_assessment.en,
      ...response.next_actions.map((item) => item.en),
    ].filter(Boolean).join("\n\n"),
  });
}

function normalizeBenchmarkAnalysisResponse(response: BackendBenchmarkAnalysisResponse, requestedQuality: IntelligenceQuality): IntelligenceResult {
  return {
    id: response.id,
    mode: response.mode,
    executionStatus: normalizeExecutionStatus(response.execution_status, response.mode),
    retryable: response.retryable ?? false,
    qualityProfile: response.model_profile ?? requestedQuality,
    answer: combineBenchmarkAnswer(response),
    sources: response.sources.map(normalizeIntelligenceSource),
    assumptions: response.assumptions.map(normalizeLocalizedText),
    uncertainty: response.uncertainty.map(normalizeLocalizedText),
    missingInputs: [],
    followUpQuestions: response.next_actions.map(normalizeLocalizedText),
    aiUsed: response.ai_used,
    documentParsingUsed: response.document_parsing_used,
    generatedAt: response.generated_at,
  };
}

function normalizeProjectSummaryResponse(response: BackendProjectSummaryResponse, requestedQuality: IntelligenceQuality): IntelligenceResult {
  return {
    id: response.id,
    mode: response.mode,
    executionStatus: normalizeExecutionStatus(response.execution_status, response.mode),
    retryable: response.retryable ?? false,
    qualityProfile: response.model_profile ?? requestedQuality,
    answer: normalizeLocalizedText(response.summary),
    sources: response.sources.map(normalizeIntelligenceSource),
    assumptions: response.assumptions.map(normalizeLocalizedText),
    uncertainty: response.uncertainty.map(normalizeLocalizedText),
    missingInputs: response.recommended_focus.map(normalizeLocalizedText),
    followUpQuestions: response.next_actions.map(normalizeLocalizedText),
    aiUsed: response.ai_used,
    documentParsingUsed: response.document_parsing_used,
    generatedAt: response.generated_at,
  };
}

function normalizeReportGenerationResponse(response: BackendReportGenerationResponse, requestedQuality: IntelligenceQuality): ReportGenerationResult {
  return {
    id: response.id,
    mode: response.mode,
    executionStatus: normalizeExecutionStatus(response.execution_status, response.mode),
    retryable: response.retryable ?? false,
    qualityProfile: response.model_profile ?? requestedQuality,
    audience: response.audience,
    sections: response.sections.map((section) => ({
      sectionId: section.section_id,
      title: normalizeLocalizedText(section.title),
      draftBody: normalizeLocalizedText(section.draft_body),
    })),
    sources: response.sources.map(normalizeIntelligenceSource),
    assumptions: response.assumptions.map(normalizeLocalizedText),
    uncertainty: response.uncertainty.map(normalizeLocalizedText),
    missingInputs: response.missing_inputs.map(normalizeLocalizedText),
    aiUsed: response.ai_used,
    documentParsingUsed: response.document_parsing_used,
    generatedAt: response.generated_at,
  };
}

function normalizeReportSectionRewriteResponse(response: BackendReportSectionRewriteResponse, requestedQuality: IntelligenceQuality): ReportSectionRewriteResult {
  return {
    id: response.id,
    sectionId: response.section_id,
    suggestedBody: normalizeLocalizedText(response.suggested_body),
    assumptions: response.assumptions.map(normalizeLocalizedText),
    uncertainty: response.uncertainty.map(normalizeLocalizedText),
    sources: response.sources.map(normalizeIntelligenceSource),
    mode: response.mode,
    executionStatus: normalizeExecutionStatus(response.execution_status, response.mode),
    retryable: response.retryable ?? false,
    qualityProfile: response.model_profile ?? requestedQuality,
    aiUsed: response.ai_used,
    documentParsingUsed: response.document_parsing_used,
    generatedAt: response.generated_at,
  };
}

function normalizeWorkspace(workspace: BackendProjectWorkspace): ProjectWorkspace {
  return {
    project: {
      id: workspace.project.id,
      name: workspace.project.name,
      industry: workspace.project.industry,
      goal: workspace.project.goal,
      status: workspace.project.status,
      createdAt: workspace.project.created_at,
      updatedAt: workspace.project.updated_at,
    },
    intake: normalizeIntake(workspace.intake),
    preferences: normalizePreferences(workspace.preferences),
    attachments: workspace.attachments.map(normalizeAttachment),
    report: {
      projectId: workspace.report.project_id,
      sections: workspace.report.sections.map(normalizeReportSection),
      version: workspace.report.version,
      status: workspace.report.status,
    },
    readiness: workspace.readiness ? normalizeReadiness(workspace.readiness) : undefined,
  };
}

export async function getEcosystems(): Promise<PlcEcosystem[]> {
  const items = await request<BackendPlcEcosystem[]>("/api/ecosystems");
  return items.map(normalizeEcosystem);
}

export async function getProjects(): Promise<ProjectWorkspace[]> {
  const items = await request<BackendProjectWorkspace[]>("/api/projects");
  return items.map(normalizeWorkspace);
}

export async function getProject(projectId: string): Promise<ProjectWorkspace> {
  return normalizeWorkspace(await request<BackendProjectWorkspace>(`/api/projects/${projectId}`));
}

export async function getProjectReadiness(projectId: string): Promise<ProjectReadiness> {
  return normalizeReadiness(await request<BackendProjectReadiness>(`/api/projects/${projectId}/readiness`));
}

export async function chatGlobalIntelligence(payload: GlobalIntelligenceChatPayload): Promise<IntelligenceResult> {
  const response = await request<BackendIntelligenceResponse>("/api/intelligence/global/chat", {
    method: "POST",
    body: JSON.stringify({
      question: payload.question,
      language: payload.language,
      platform_ids: payload.platformIds,
      quality: payload.quality,
      use_ai: payload.useAi,
    }),
  });
  return normalizeIntelligenceResponse(response, payload.quality);
}

export async function chatProjectIntelligence(projectId: string, payload: ProjectIntelligenceChatPayload): Promise<IntelligenceResult> {
  const response = await request<BackendIntelligenceResponse>(`/api/projects/${projectId}/intelligence/chat`, {
    method: "POST",
    body: JSON.stringify({
      question: payload.question,
      language: payload.language,
      quality: payload.quality,
      use_ai: payload.useAi,
    }),
  });
  return normalizeIntelligenceResponse(response, payload.quality);
}

function serializeIntelligenceAction(payload: ProjectIntelligenceActionPayload) {
  return {
    language: payload.language,
    quality: payload.quality,
    use_ai: payload.useAi,
  };
}

export async function analyzeProjectIntelligence(projectId: string, payload: ProjectIntelligenceActionPayload): Promise<IntelligenceResult> {
  const response = await request<BackendIntelligenceResponse>(`/api/projects/${projectId}/intelligence/analyze`, {
    method: "POST",
    body: JSON.stringify({ ...serializeIntelligenceAction(payload), focus: "attachments" }),
  });
  return normalizeIntelligenceResponse(response, payload.quality);
}

export async function explainProjectBenchmark(projectId: string, payload: ProjectIntelligenceActionPayload): Promise<IntelligenceResult> {
  const response = await request<BackendIntelligenceResponse>(`/api/projects/${projectId}/benchmark/explain`, {
    method: "POST",
    body: JSON.stringify(serializeIntelligenceAction(payload)),
  });
  return normalizeIntelligenceResponse(response, payload.quality);
}

export async function streamProjectSummary(
  projectId: string,
  payload: ProjectIntelligenceActionPayload,
  onChunk: (chunk: LocalizedText) => void,
): Promise<IntelligenceResult> {
  const response = await requestStream<BackendProjectSummaryResponse>(
    `/api/projects/${projectId}/intelligence/summary/stream`,
    {
      method: "POST",
      body: JSON.stringify(serializeIntelligenceAction(payload)),
    },
    onChunk,
  );
  return normalizeProjectSummaryResponse(response, payload.quality);
}

export async function streamProjectBenchmarkAnalysis(
  projectId: string,
  payload: ProjectIntelligenceActionPayload,
  onChunk: (chunk: LocalizedText) => void,
): Promise<IntelligenceResult> {
  const response = await requestStream<BackendBenchmarkAnalysisResponse>(
    `/api/projects/${projectId}/intelligence/benchmark/stream`,
    {
      method: "POST",
      body: JSON.stringify(serializeIntelligenceAction(payload)),
    },
    onChunk,
  );
  return normalizeBenchmarkAnalysisResponse(response, payload.quality);
}

export async function generateProjectReport(projectId: string, payload: ReportGenerationPayload): Promise<ReportGenerationResult> {
  const response = await request<BackendReportGenerationResponse>(`/api/projects/${projectId}/report/generate`, {
    method: "POST",
    body: JSON.stringify({ ...serializeIntelligenceAction(payload), audience: payload.audience }),
  });
  return normalizeReportGenerationResponse(response, payload.quality);
}

export async function generateProjectReportSection(projectId: string, sectionId: string, payload: ReportGenerationPayload): Promise<ReportSectionRewriteResult> {
  const response = await request<BackendReportSectionRewriteResponse>(`/api/projects/${projectId}/report/sections/${sectionId}/generate`, {
    method: "POST",
    body: JSON.stringify({ ...serializeIntelligenceAction(payload), audience: payload.audience }),
  });
  return normalizeReportSectionRewriteResponse(response, payload.quality);
}

export async function rewriteProjectReportSection(projectId: string, sectionId: string, payload: ReportSectionRewritePayload): Promise<ReportSectionRewriteResult> {
  const response = await request<BackendReportSectionRewriteResponse>(`/api/projects/${projectId}/report/sections/${sectionId}/rewrite`, {
    method: "POST",
    body: JSON.stringify({ ...serializeIntelligenceAction(payload), audience: payload.audience, instruction: payload.instruction }),
  });
  return normalizeReportSectionRewriteResponse(response, payload.quality);
}

export async function createProject(payload: ProjectCreatePayload): Promise<ProjectWorkspace> {
  return normalizeWorkspace(
    await request<BackendProjectWorkspace>("/api/projects", {
      method: "POST",
      body: JSON.stringify(payload),
    }),
  );
}

export async function deleteProject(projectId: string): Promise<void> {
  await request<void>(`/api/projects/${projectId}`, {
    method: "DELETE",
  });
}

export async function updateProjectStatus(projectId: string, status: ProjectStatus): Promise<ProjectWorkspace> {
  return normalizeWorkspace(
    await request<BackendProjectWorkspace>(`/api/projects/${projectId}/status`, {
      method: "PUT",
      body: JSON.stringify({ status }),
    }),
  );
}

export async function finalizeProject(projectId: string): Promise<ProjectWorkspace> {
  return updateProjectStatus(projectId, "Finalized");
}

export async function reopenProject(projectId: string): Promise<ProjectWorkspace> {
  return updateProjectStatus(projectId, "Analyzing");
}

export async function updateProjectIntake(projectId: string, intake: ProjectIntake): Promise<ProjectWorkspace> {
  return normalizeWorkspace(
    await request<BackendProjectWorkspace>(`/api/projects/${projectId}/intake`, {
      method: "PUT",
      body: JSON.stringify(serializeIntake(intake)),
    }),
  );
}

export async function updateProjectPreferences(projectId: string, preferences: PlatformPreference[]): Promise<ProjectWorkspace> {
  return normalizeWorkspace(
    await request<BackendProjectWorkspace>(`/api/projects/${projectId}/preferences`, {
      method: "PUT",
      body: JSON.stringify(serializePreferences(preferences)),
    }),
  );
}

export async function addProjectAttachment(projectId: string, attachment: Pick<ProjectAttachment, "fileName" | "fileType" | "declaredPurpose">): Promise<ProjectWorkspace> {
  return normalizeWorkspace(
    await request<BackendProjectWorkspace>(`/api/projects/${projectId}/attachments`, {
      method: "POST",
      body: JSON.stringify({
        file_name: attachment.fileName,
        file_type: attachment.fileType,
        declared_purpose: attachment.declaredPurpose,
      }),
    }),
  );
}

export async function runProjectBenchmark(projectId: string): Promise<BenchmarkResult[]> {
  const results = await request<BackendBenchmarkResult[]>(`/api/projects/${projectId}/benchmark`, {
    method: "POST",
  });
  return results.map(normalizeBenchmarkResult);
}

export async function updateReportSection(projectId: string, sectionId: string, payload: Pick<ReportSection, "body" | "assumptions">): Promise<ProjectWorkspace> {
  return normalizeWorkspace(
    await request<BackendProjectWorkspace>(`/api/projects/${projectId}/report/sections/${sectionId}`, {
      method: "PUT",
      body: JSON.stringify({
        body: payload.body,
        assumptions: payload.assumptions,
      }),
    }),
  );
}
