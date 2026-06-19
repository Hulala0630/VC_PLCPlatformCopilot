import type {
  BenchmarkResult,
  IntelligenceMode,
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
  ReportSection,
} from "../types";

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL ?? "http://127.0.0.1:8000";

type BackendPlcEcosystem = Omit<PlcEcosystem, "regionStrength"> & {
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
  mode: IntelligenceMode;
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

function normalizeEcosystem(item: BackendPlcEcosystem): PlcEcosystem {
  return {
    id: item.id,
    name: item.name,
    vendor: item.vendor,
    software: item.software,
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
    rationale: result.rationale,
    assumptions: result.assumptions,
  };
}

function normalizeReportSection(section: BackendReportSection): ReportSection {
  return {
    id: section.id,
    title: section.title,
    body: section.body,
    assumptions: section.assumptions ?? [],
    uncertainty: section.uncertainty ?? {
      zh: "后端当前未返回不确定性字段；前端使用占位说明。",
      en: "Backend did not return uncertainty yet; the frontend is using a placeholder.",
    },
    dataSourcesUsed: section.data_sources_used ?? [{ zh: "后端 mock API", en: "Backend mock API" }],
    lastGeneratedAt: section.last_generated_at,
  };
}

function normalizeReadiness(readiness: BackendProjectReadiness): ProjectReadiness {
  return {
    score: readiness.score,
    status: readiness.status,
    missingRequired: readiness.missing_required,
    recommendedMissing: readiness.recommended_missing,
    nextAction: readiness.next_action,
    confidenceLevel: readiness.confidence_level,
    reasons: readiness.reasons,
  };
}

function normalizeIntelligenceSource(source: BackendIntelligenceSource): IntelligenceSource {
  return {
    id: source.id,
    type: source.type,
    label: source.label,
    detail: source.detail,
  };
}

function normalizeIntelligenceResponse(response: BackendIntelligenceResponse, requestedQuality: IntelligenceQuality): IntelligenceResult {
  return {
    id: response.id,
    mode: response.mode,
    qualityProfile: response.model_profile ?? requestedQuality,
    answer: response.answer,
    sources: response.sources.map(normalizeIntelligenceSource),
    assumptions: response.assumptions,
    uncertainty: response.uncertainty,
    missingInputs: response.missing_inputs,
    followUpQuestions: response.follow_up_questions,
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
