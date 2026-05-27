export type Language = "zh" | "en";

export interface LocalizedText {
  zh: string;
  en: string;
}

export interface PlcEcosystem {
  id: string;
  name: string;
  vendor: string;
  software: string;
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

export interface ChatMessage {
  role: "user" | "assistant";
  content: LocalizedText;
}

export interface PlcProject {
  id: string;
  title: LocalizedText;
  plant: LocalizedText;
  selectedPlatformId: string;
  status: "Draft" | "Reviewed" | "Decision Ready";
  updatedAt: string;
  objective: LocalizedText;
  recommendation: LocalizedText;
  decisionFactors: LocalizedText[];
  migrationNotes: LocalizedText[];
  riskLevel: "Low" | "Medium" | "High";
  effortIndex: number;
}
