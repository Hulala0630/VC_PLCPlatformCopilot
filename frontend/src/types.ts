export type Language = "zh" | "en";
export type ProjectStatus = "Draft" | "Analyzing" | "Report Ready" | "Finalized";
export type RiskLevel = "Low" | "Medium" | "High";
export type ConfidenceLevel = "Low" | "Medium" | "High";
export type IntelligenceMode = "openai" | "deterministic_placeholder" | "deterministic_fallback";
export type IntelligenceQuality = "fast" | "balanced" | "quality";
export type ReportAudience = "executive" | "technical" | "management" | "sales";
export type WorkspaceTab = "overview" | "intake" | "preferences" | "attachments" | "benchmark" | "report";

export interface LocalizedText {
  zh: string;
  en: string;
}

export interface PlcEcosystem {
  id: string;
  name: string;
  vendor: string;
  software: string;
  officialUrl: string;
  regionStrength: LocalizedText;
  summary: LocalizedText;
  strengths: LocalizedText[];
  cautions: LocalizedText[];
  scores: {
    productivity: number;
    motion: number;
    safety: number;
    simulation: number;
    openness: number;
    talent: number;
    cost: number;
  };
}

export interface Project {
  id: string;
  name: string;
  industry: string;
  goal: string;
  status: ProjectStatus;
  createdAt: string;
  updatedAt: string;
}

export interface ProjectIntake {
  projectSize: "Small" | "Medium" | "Large";
  ioScale: number;
  motionRequirement: number;
  safetyRequirement: number;
  budgetSensitivity: number;
  teamExperience: string;
  existingPlatform: string;
  candidatePlatforms: string[];
  constraints: string;
}

export interface PlatformPreference {
  platformId: string;
  preferenceWeight: number;
  userReasonNote: string;
}

export interface ProjectAttachment {
  id: string;
  projectId: string;
  fileName: string;
  fileType: "Electrical List" | "I/O List" | "Requirements" | "Architecture" | "Other";
  declaredPurpose: string;
  uploadedAt: string;
}

export interface BenchmarkResult {
  platformId: string;
  technicalScore: number;
  preferenceScore: number;
  weightedScore: number;
  riskLevel: RiskLevel;
  rationale: LocalizedText;
  assumptions: LocalizedText[];
}

export interface ReportSection {
  id: string;
  title: LocalizedText;
  body: LocalizedText;
  assumptions: LocalizedText[];
  uncertainty: LocalizedText;
  dataSourcesUsed: LocalizedText[];
  lastGeneratedAt: string;
}

export interface ReportDraft {
  projectId: string;
  sections: ReportSection[];
  version: number;
  status: "Draft" | "Ready";
}

export interface ProjectReadiness {
  score: number;
  status: ProjectStatus;
  missingRequired: LocalizedText[];
  recommendedMissing: LocalizedText[];
  nextAction: LocalizedText;
  confidenceLevel: ConfidenceLevel;
  reasons: LocalizedText[];
}

export interface IntelligenceSource {
  id: string;
  type: string;
  label: LocalizedText;
  detail: LocalizedText;
}

export interface IntelligenceResult {
  id: string;
  mode: IntelligenceMode;
  qualityProfile: IntelligenceQuality;
  answer: LocalizedText;
  sources: IntelligenceSource[];
  assumptions: LocalizedText[];
  uncertainty: LocalizedText[];
  missingInputs: LocalizedText[];
  followUpQuestions: LocalizedText[];
  aiUsed: boolean;
  documentParsingUsed: false;
  generatedAt: string;
}

export interface GeneratedReportSection {
  sectionId: string;
  title: LocalizedText;
  draftBody: LocalizedText;
}

export interface ReportGenerationResult {
  id: string;
  mode: IntelligenceMode;
  qualityProfile: IntelligenceQuality;
  audience: ReportAudience;
  sections: GeneratedReportSection[];
  sources: IntelligenceSource[];
  assumptions: LocalizedText[];
  uncertainty: LocalizedText[];
  missingInputs: LocalizedText[];
  aiUsed: boolean;
  documentParsingUsed: false;
  generatedAt: string;
}

export interface ReportSectionRewriteResult {
  id: string;
  sectionId: string;
  suggestedBody: LocalizedText;
  assumptions: LocalizedText[];
  uncertainty: LocalizedText[];
  sources: IntelligenceSource[];
  mode: IntelligenceMode;
  qualityProfile: IntelligenceQuality;
  aiUsed: boolean;
  documentParsingUsed: false;
  generatedAt: string;
}

export interface ChatMessage {
  role: "user" | "assistant";
  content: LocalizedText;
  intelligence?: IntelligenceResult;
}

export interface ProjectWorkspace {
  project: Project;
  intake: ProjectIntake;
  preferences: PlatformPreference[];
  attachments: ProjectAttachment[];
  report: ReportDraft;
  readiness?: ProjectReadiness;
}
