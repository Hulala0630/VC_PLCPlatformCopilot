import {
  AlertTriangle,
  BarChart3,
  Check,
  CheckCircle2,
  ChevronRight,
  ClipboardList,
  Copy as CopyIcon,
  Cpu,
  Download,
  ExternalLink,
  FileText,
  FolderPlus,
  Info as InfoIcon,
  Languages,
  MessageSquareText,
  PanelLeftClose,
  PanelLeftOpen,
  Paperclip,
  Plus,
  Presentation,
  Printer,
  RefreshCw,
  Save,
  Send,
  SlidersHorizontal,
  Sparkles,
  Trash2,
} from "lucide-react";
import { useEffect, useMemo, useRef, useState } from "react";
import {
  addProjectAttachment,
  analyzeProjectIntelligence,
  chatGlobalIntelligence,
  chatProjectIntelligence,
  createProject as apiCreateProject,
  deleteProject as apiDeleteProject,
  finalizeProject,
  explainProjectBenchmark,
  generateProjectReport,
  getEcosystems,
  getProjects,
  reopenProject,
  rewriteProjectReportSection,
  runProjectBenchmark,
  updateProjectIntake,
  updateProjectPreferences,
  updateProjectStatus as apiUpdateProjectStatus,
  updateReportSection as apiUpdateReportSection,
} from "./api/client";
import { ecosystems as fallbackEcosystems, reportSections, workspaces as seedWorkspaces } from "./data/platforms";
import type {
  BenchmarkResult,
  ChatMessage,
  IntelligenceResult,
  Language,
  LocalizedText,
  PlcEcosystem,
  ProjectAttachment,
  ProjectReadiness,
  ProjectStatus,
  ProjectWorkspace,
  ReportGenerationResult,
  ReportSection,
  ReportSectionRewriteResult,
  WorkspaceTab,
} from "./types";

const copy = {
  zh: {
    title: "PLC 平台基准与迁移决策工作台",
    subtitle: "项目闭环：创建项目、登记输入、设置偏好、生成排名、撰写报告",
    language: "English",
    newProject: "新建项目",
    ecosystems: "PLC 生态侧边栏",
    officialWebsite: "打开官方产品页",
    query: "当前项目 Query",
    send: "发送",
    askPlaceholder: "输入项目约束、选型问题或报告修改意见",
    project: "项目",
    projectList: "项目列表",
    projectGoalSummary: "项目目标摘要",
    industry: "行业",
    status: "状态",
    updated: "更新",
    overview: "Overview",
    intake: "Intake",
    preferences: "Preferences",
    attachments: "Attachments",
    benchmark: "Benchmark",
    report: "Report",
    save: "保存",
    regenerateSection: "重算当前分区",
    addAttachment: "登记附件",
    fileNote: "当前仅使用文件名称、类型和声明用途进行分析，尚未读取文件正文或表格内容。",
    technicalScore: "技术评分",
    preferenceScore: "用户倾向",
    weightedImpact: "加权影响",
    finalScore: "最终评分",
    weightedScore: "加权总分",
    risk: "风险",
    assumptions: "分析依据",
    uncertainty: "结论限制",
    dataSources: "参考信息",
    reportSections: "报告目录",
    sectionEditor: "文档编辑器",
    rightPanel: "依据面板",
    candidatePlatforms: "候选平台",
    registeredMaterials: "已登记资料数量",
    attachmentReadLimit: "不读取正文 / 尚未解析",
    keyInputCompleteness: "关键输入完整度",
    projectInputs: "项目输入",
    emptyQuestion: "请输入内容后再发送。",
    completion: "项目完成度",
    nextStep: "下一步建议",
    workflow: "决策流程",
    required: "必填",
    optional: "可选",
    complete: "已完成",
    missing: "待补充",
    validation: "输入完整度",
    reason: "倾向原因",
    registeredOnly: "已登记",
    emptyAttachments: "还没有登记附件。请先记录文件名称、类型和声明用途。",
    futureExport: "PDF / PPT 导出入口（未来版本）",
    topRecommendation: "当前首选",
    reasonPlaceholder: "例如：以前用过、客户指定、团队熟悉、供应链稳定、成本原因",
    attachmentPurpose: "用途",
    fileName: "文件名",
    fileType: "文件类型",
    created: "创建",
    projectEntrance: "项目入口",
    portfolioIntro: "从项目列表进入不同 PLC 决策工作流。",
    listView: "列表",
    typeView: "按类型",
    openProject: "打开项目",
    byType: "项目类型",
    apiConnected: "API 已连接",
    mockFallback: "离线工作模式",
    checkingApi: "检查 API",
    saving: "保存中",
    saved: "已保存",
    saveFailed: "暂时无法同步，当前修改已保留",
    savePreferences: "保存偏好",
    deleteProject: "删除项目",
    deleteProjectConfirm: "确认删除这个项目？该操作会删除本地 SQLite 中的项目数据。",
    global: "全局",
    projectScope: "当前项目",
    globalQuery: "全局 Query",
    projectQuery: "当前项目 Query",
    globalPlaceholder: "询问 PLC 生态选型、平台比较、供应商锁定或长期维护问题",
    projectPlaceholder: "询问当前项目的推荐原因、缺失信息或报告改写",
    aiToggle: "AI",
    aiEnabled: "AI 已开启",
    aiDisabled: "AI 已关闭",
    globalAiToggle: "切换全局 Query 的 AI 分析",
    projectAiToggle: "切换当前项目 Query 的 AI 分析",
    queryEmpty: "还没有对话。输入问题以获得后端分析结果。",
    queryLoading: "正在分析...",
    queryFailed: "暂时无法连接分析服务。您的问题和上一次结果已保留。",
    retry: "重试",
    aiAnalysis: "AI 智能分析",
    deterministic: "基础分析",
    fallback: "AI 暂时不可用",
    qualityProfile: "质量档位",
    fastQuality: "快速",
    balancedQuality: "平衡",
    qualityQuality: "高质量",
    responseContext: "分析依据与结论限制",
    attachmentsNotParsed: "当前仅使用文件名称、类型和声明用途进行分析，尚未读取文件正文或表格内容。",
    missingInputsQuery: "缺失输入",
    analyzeRegisteredInfo: "分析已登记资料",
    explainRanking: "查看推荐原因",
    generateReportDraft: "生成报告草稿",
    analysisResult: "分析结果",
    followUpQuestions: "后续问题",
    actionFailed: "暂时无法连接分析服务。上一次成功结果已保留。",
    intelligenceUsesProjectSwitch: "当前分析方式",
    reportSuggestions: "报告草稿建议",
    suggestionsNotSaved: "确认采用后，此建议将更新当前报告内容。",
    acceptSection: "接受建议",
    acceptAll: "接受全部",
    discardSuggestions: "放弃建议",
    currentContent: "当前内容",
    suggestedContent: "建议内容",
    rewriteInstruction: "改写要求",
    rewritePlaceholder: "例如：更精炼地面向管理层说明推荐理由和主要风险",
    suggestRewrite: "生成改写建议",
    accept: "接受建议",
    discard: "放弃建议",
    sectionRewrite: "分区改写建议",
    noPersistenceBeforeAccept: "确认采用前，当前报告内容保持不变。",
    useBasicAnalysis: "使用基础分析",
    fallbackHint: "已根据当前项目数据提供基础分析。",
    benchmarkExplanation: "基于当前评分结果说明平台优势、偏好影响和主要风险。",
    benchmarkScoreTooltip: "推荐说明不会改变已计算的评分结果。",
    analysisScope: "分析范围",
    unreadAttachments: "尚未读取的附件",
    accepted: "已接受",
    currentWorkResults: "当前工作结果",
    workspaceOverview: "从项目列表继续当前 PLC 决策工作，查看状态、推荐平台和下一步操作。",
    createPLCDecisionProject: "创建 PLC 决策项目",
    noProjects: "还没有项目。",
    noProjectsHint: "创建第一个 PLC 决策项目，开始平台选型与迁移分析。",
    backToWorkspace: "返回工作台",
    lastUpdated: "最近更新",
    recommendedNextAction: "推荐下一步",
    lifecycleStatus: "生命周期状态",
    readiness: "成熟度",
    missingRequired: "缺失必填",
    recommendedInputs: "建议补充",
    confidence: "置信度",
    reasons: "原因",
    missingItems: "缺失",
    localReadiness: "成熟度根据当前已填写信息估算。",
    finalizedReport: "已确认最终版报告",
    markFinalized: "标记为最终版",
    reopenAnalysis: "重新进入分析",
    statusWillUpdate: "保存后状态和成熟度会根据后端规则更新。",
    reportMode: "报告模式",
    edit: "编辑",
    preview: "预览",
    deliveryContext: "交付上下文",
    reportPreview: "报告预览",
    exportPreparation: "导出准备",
    copyMarkdown: "复制 Markdown",
    downloadMarkdown: "下载 Markdown",
    printBrowserPdf: "打印 / 浏览器另存 PDF",
    exportPdf: "生成 PDF / 打印",
    exportPpt: "导出 PowerPoint",
    exporting: "正在生成...",
    exportFailed: "导出失败，请重试",
    copied: "已复制",
    projectMetadata: "项目概况",
    benchmarkSummary: "Benchmark 摘要",
    preferenceImpact: "偏好影响",
    riskAssessment: "风险评估",
    roadmapNextSteps: "路线图 / 下一步",
    attachmentMetadata: "附件登记信息",
    missingInputs: "缺失输入",
    reportDraftWarning: "当前报告仍是草稿，因为项目必填信息尚未完整。",
    reportAnalyzingWarning: "分析正在进行中。报告可以审阅，但推荐置信度仍可能变化。",
    reportReadyNotice: "报告已准备好进入审阅。",
    finalizedReportNotice: "已定稿报告。",
    sectionContext: "分区上下文",
    noMissingInputs: "当前没有影响该分区的缺失输入。",
  },
  en: {
    title: "PLC Platform Benchmark & Migration Decision Copilot",
    subtitle: "Closed-loop workspace: create, intake, prefer, rank, and write the recommendation",
    language: "中文",
    newProject: "New Project",
    ecosystems: "PLC Ecosystems",
    officialWebsite: "Open official product page",
    query: "Current Project Query",
    send: "Send",
    askPlaceholder: "Enter project constraints, selection questions, or report revision requests",
    project: "Project",
    projectList: "Project List",
    projectGoalSummary: "Project Goal Summary",
    industry: "Industry",
    status: "Status",
    updated: "Updated",
    overview: "Overview",
    intake: "Intake",
    preferences: "Preferences",
    attachments: "Attachments",
    benchmark: "Benchmark",
    report: "Report",
    save: "Save",
    regenerateSection: "Regenerate Section",
    addAttachment: "Register Attachment",
    fileNote: "This analysis currently uses only file names, types, and declared purposes. File contents and spreadsheet data have not been read.",
    technicalScore: "Technical Score",
    preferenceScore: "User Preference",
    weightedImpact: "Weighted Impact",
    finalScore: "Final Score",
    weightedScore: "Weighted Score",
    risk: "Risk",
    assumptions: "Analysis basis",
    uncertainty: "Conclusion limits",
    dataSources: "Reference information",
    reportSections: "Report Sections",
    sectionEditor: "Document Editor",
    rightPanel: "Evidence Panel",
    candidatePlatforms: "Candidate Platforms",
    registeredMaterials: "Registered Materials",
    attachmentReadLimit: "Content not read / not parsed",
    keyInputCompleteness: "Key Input Completeness",
    projectInputs: "Project Inputs",
    emptyQuestion: "Enter content before sending.",
    completion: "Project Completeness",
    nextStep: "Next Step",
    workflow: "Decision Flow",
    required: "Required",
    optional: "Optional",
    complete: "Complete",
    missingItems: "Missing",
    validation: "Input Completeness",
    reason: "Preference Reason",
    registeredOnly: "Registered",
    emptyAttachments: "No attachments registered yet. Add a file name, type, and declared purpose.",
    futureExport: "PDF / PPT export entry (future)",
    topRecommendation: "Current Lead",
    reasonPlaceholder: "Examples: used before, customer mandated, team familiarity, supply stability, cost reason",
    attachmentPurpose: "Purpose",
    fileName: "File name",
    fileType: "File type",
    created: "Created",
    projectEntrance: "Project Entrance",
    portfolioIntro: "Enter each PLC decision workflow from the project portfolio.",
    listView: "List",
    typeView: "By Type",
    openProject: "Open Project",
    byType: "Project Type",
    apiConnected: "API connected",
    mockFallback: "Offline mode",
    checkingApi: "Checking API",
    saving: "Saving...",
    saved: "Saved",
    saveFailed: "Sync unavailable; current changes are preserved",
    savePreferences: "Save Preferences",
    deleteProject: "Delete Project",
    deleteProjectConfirm: "Delete this project? This removes the project data from local SQLite.",
    global: "Global",
    projectScope: "Project",
    globalQuery: "Global Query",
    projectQuery: "Project Query",
    globalPlaceholder: "Ask about PLC ecosystem selection, platform comparison, vendor lock-in, or maintainability",
    projectPlaceholder: "Ask about this project's recommendation, missing inputs, or report wording",
    aiToggle: "AI",
    aiEnabled: "AI on",
    aiDisabled: "AI off",
    globalAiToggle: "Toggle AI analysis for Global Query",
    projectAiToggle: "Toggle AI analysis for this Project Query",
    queryEmpty: "No conversation yet. Ask a question to receive a backend analysis result.",
    queryLoading: "Analyzing...",
    queryFailed: "Unable to connect to the analysis service right now. Your question and previous result are preserved.",
    retry: "Retry",
    aiAnalysis: "AI Analysis",
    deterministic: "Basic analysis",
    fallback: "AI temporarily unavailable",
    qualityProfile: "Quality profile",
    fastQuality: "Fast",
    balancedQuality: "Balanced",
    qualityQuality: "Quality",
    responseContext: "Analysis basis & conclusion limits",
    attachmentsNotParsed: "This analysis currently uses only file names, types, and declared purposes. File contents and spreadsheet data have not been read.",
    missingInputsQuery: "Missing inputs",
    analyzeRegisteredInfo: "Analyze registered information",
    explainRanking: "View recommendation reasons",
    generateReportDraft: "Generate report draft",
    analysisResult: "Analysis result",
    followUpQuestions: "Follow-up questions",
    actionFailed: "Unable to connect to the analysis service right now. The last successful result is preserved.",
    intelligenceUsesProjectSwitch: "Current analysis mode",
    reportSuggestions: "Report draft suggestions",
    suggestionsNotSaved: "Once confirmed, this suggestion will update the current report content.",
    acceptSection: "Accept suggestion",
    acceptAll: "Accept all",
    discardSuggestions: "Discard suggestions",
    currentContent: "Current content",
    suggestedContent: "Suggested content",
    rewriteInstruction: "Rewrite instruction",
    rewritePlaceholder: "Example: explain the recommendation and key risks more concisely for management",
    suggestRewrite: "Suggest rewrite",
    accept: "Accept suggestion",
    discard: "Discard suggestion",
    sectionRewrite: "Section rewrite suggestion",
    noPersistenceBeforeAccept: "The current report remains unchanged until you confirm the suggestion.",
    useBasicAnalysis: "Use basic analysis",
    fallbackHint: "A basic analysis has been provided using the current project data.",
    benchmarkExplanation: "Explains platform strengths, preference impact, and key risks using the current scores.",
    benchmarkScoreTooltip: "Recommendation reasons do not change the calculated scores.",
    analysisScope: "Analysis scope",
    unreadAttachments: "Attachments not yet read",
    accepted: "Accepted",
    currentWorkResults: "Current Work Results",
    workspaceOverview: "Continue PLC decision work from the project list, with status, recommended platform, and next action visible.",
    createPLCDecisionProject: "Create PLC Decision Project",
    noProjects: "No projects yet.",
    noProjectsHint: "Create your first PLC decision project to begin platform selection and migration analysis.",
    backToWorkspace: "Back to Workspace",
    lastUpdated: "Last Updated",
    recommendedNextAction: "Recommended Next Action",
    lifecycleStatus: "Lifecycle Status",
    readiness: "Readiness",
    missingRequired: "Missing Required",
    recommendedInputs: "Recommended Inputs",
    confidence: "Confidence",
    reasons: "Reasons",
    missing: "Missing",
    localReadiness: "Readiness is estimated from the information currently provided.",
    finalizedReport: "Finalized report",
    markFinalized: "Mark as Finalized",
    reopenAnalysis: "Reopen for Analysis",
    statusWillUpdate: "Status and readiness will update from backend rules after save.",
    reportMode: "Report Mode",
    edit: "Edit",
    preview: "Preview",
    deliveryContext: "Delivery Context",
    reportPreview: "Report Preview",
    exportPreparation: "Export Preparation",
    copyMarkdown: "Copy Markdown",
    downloadMarkdown: "Download Markdown",
    printBrowserPdf: "Print / Browser PDF",
    exportPdf: "Generate PDF / Print",
    exportPpt: "Export PowerPoint",
    exporting: "Generating...",
    exportFailed: "Export failed. Please retry.",
    copied: "Copied",
    projectMetadata: "Project Overview",
    benchmarkSummary: "Benchmark Summary",
    preferenceImpact: "Preference Impact",
    riskAssessment: "Risk Assessment",
    roadmapNextSteps: "Roadmap / Next Steps",
    attachmentMetadata: "Registered Attachments",
    missingInputs: "Missing Inputs",
    reportDraftWarning: "This report is still a draft because required project inputs are missing.",
    reportAnalyzingWarning: "Analysis is in progress. Report can be reviewed, but recommendation confidence may still change.",
    reportReadyNotice: "Report is ready for review.",
    finalizedReportNotice: "Finalized report.",
    sectionContext: "Section Context",
    noMissingInputs: "No missing inputs are currently affecting this section.",
  },
} as const;

const tabOrder: WorkspaceTab[] = ["overview", "intake", "preferences", "attachments", "benchmark", "report"];
const tabs: { id: WorkspaceTab; icon: React.ReactNode }[] = [
  { id: "overview", icon: <ClipboardList size={16} /> },
  { id: "intake", icon: <FileText size={16} /> },
  { id: "preferences", icon: <SlidersHorizontal size={16} /> },
  { id: "attachments", icon: <Paperclip size={16} /> },
  { id: "benchmark", icon: <BarChart3 size={16} /> },
  { id: "report", icon: <Sparkles size={16} /> },
];

const attachmentTypes: ProjectAttachment["fileType"][] = ["Electrical List", "I/O List", "Requirements", "Architecture", "Other"];
const today = "2026-05-30";

const riskClass = {
  Low: "bg-emerald-50 text-emerald-700 ring-emerald-200",
  Medium: "bg-amber-50 text-amber-800 ring-amber-200",
  High: "bg-rose-50 text-rose-700 ring-rose-200",
};

const riskLabel = {
  zh: { Low: "低", Medium: "中", High: "高" },
  en: { Low: "Low", Medium: "Medium", High: "High" },
} as const;

const statusClass: Record<ProjectStatus, string> = {
  Draft: "bg-slate-100 text-slate-700 ring-slate-200",
  Analyzing: "bg-cyan-50 text-cyan-800 ring-cyan-200",
  "Report Ready": "bg-emerald-50 text-emerald-700 ring-emerald-200",
  Finalized: "bg-slate-900 text-white ring-slate-900",
};

function localize(value: LocalizedText, language: Language): string {
  return value[language];
}

const GLOBAL_AI_STORAGE_KEY = "plc-copilot-global-ai-enabled";
const PROJECT_AI_STORAGE_KEY = "plc-copilot-project-ai-enabled";

function readStoredGlobalAi() {
  try {
    return window.localStorage.getItem(GLOBAL_AI_STORAGE_KEY) === "true";
  } catch {
    return false;
  }
}

function readStoredProjectAi() {
  try {
    const stored = JSON.parse(window.localStorage.getItem(PROJECT_AI_STORAGE_KEY) ?? "{}") as Record<string, unknown>;
    return Object.fromEntries(Object.entries(stored).filter((entry): entry is [string, boolean] => typeof entry[1] === "boolean"));
  } catch {
    return {};
  }
}

function persistStorage(key: string, value: string) {
  try {
    window.localStorage.setItem(key, value);
  } catch {
    // Storage can be unavailable in privacy-restricted browser contexts.
  }
}

function averageScore(platform: PlcEcosystem) {
  const values = Object.values(platform.scores);
  return Math.round(values.reduce((sum, value) => sum + value, 0) / values.length);
}

function calculateCompleteness(workspace: ProjectWorkspace) {
  const checks = [
    Boolean(workspace.project.name.trim()),
    Boolean(workspace.project.industry.trim()),
    Boolean(workspace.project.goal.trim()),
    workspace.intake.ioScale > 0,
    Boolean(workspace.intake.teamExperience.trim()),
    Boolean(workspace.intake.constraints.trim()),
    workspace.intake.candidatePlatforms.length >= 2,
    workspace.preferences.some((item) => item.preferenceWeight !== 50 || item.userReasonNote.trim()),
    workspace.attachments.length > 0,
    workspace.report.sections.some((section) => section.body.en.trim() || section.body.zh.trim()),
  ];
  const done = checks.filter(Boolean).length;
  return { done, total: checks.length, percent: Math.round((done / checks.length) * 100) };
}

function calculateKeyInputCompleteness(workspace: ProjectWorkspace) {
  const checks = [
    Boolean(workspace.project.name.trim()),
    Boolean(workspace.project.industry.trim()),
    Boolean(workspace.project.goal.trim()),
    workspace.intake.ioScale > 0,
    workspace.intake.candidatePlatforms.length >= 2,
    Boolean(workspace.intake.teamExperience.trim()),
    Boolean(workspace.intake.constraints.trim()),
  ];
  const done = checks.filter(Boolean).length;
  return { done, total: checks.length, percent: Math.round((done / checks.length) * 100) };
}

function nextStepFor(workspace: ProjectWorkspace, language: Language): string {
  if (!workspace.project.goal.trim() || !workspace.project.industry.trim()) {
    return language === "zh" ? "先补齐项目目标与行业背景。" : "Complete project goal and industry context first.";
  }
  if (!workspace.intake.teamExperience.trim() || !workspace.intake.constraints.trim()) {
    return language === "zh" ? "补充团队经验和硬约束，让排名解释更可靠。" : "Add team experience and hard constraints to improve ranking context.";
  }
  if (workspace.intake.candidatePlatforms.length < 2) {
    return language === "zh" ? "至少选择两个候选平台用于对比。" : "Select at least two candidate platforms for comparison.";
  }
  if (!workspace.preferences.some((item) => item.userReasonNote.trim())) {
    return language === "zh" ? "为关键平台填写倾向原因，区分技术分和业务偏好。" : "Add preference reasons for key platforms to separate technical fit from business preference.";
  }
  if (workspace.attachments.length === 0) {
    return language === "zh" ? "登记附件信息，明确可参考资料；当前不会读取文件内容。" : "Register attachment information to clarify available references; file contents are not read yet.";
  }
  return language === "zh" ? "进入 Benchmark 与 Report，检查首选平台、风险、分析依据和结论限制。" : "Review Benchmark and Report for the lead platform, risks, analysis basis, and conclusion limits.";
}

function getWorkspaceReadiness(workspace: ProjectWorkspace): { readiness: ProjectReadiness; isLocal: boolean } {
  if (workspace.readiness) {
    return { readiness: workspace.readiness, isLocal: false };
  }

  const completeness = calculateCompleteness(workspace);
  const missingRequired: LocalizedText[] = [];
  const recommendedMissing: LocalizedText[] = [];

  if (!workspace.project.industry.trim()) missingRequired.push({ zh: "行业", en: "Industry" });
  if (!workspace.project.goal.trim()) missingRequired.push({ zh: "项目目标", en: "Project goal" });
  if (workspace.intake.candidatePlatforms.length < 2) missingRequired.push({ zh: "至少两个候选 PLC 生态", en: "At least two candidate PLC ecosystems" });
  if (!workspace.intake.teamExperience.trim()) recommendedMissing.push({ zh: "团队经验", en: "Team experience" });
  if (!workspace.intake.constraints.trim()) recommendedMissing.push({ zh: "项目约束", en: "Project constraints" });
  if (workspace.attachments.length === 0) recommendedMissing.push({ zh: "附件登记信息", en: "Registered attachment information" });

  return {
    isLocal: true,
    readiness: {
      score: completeness.percent,
      status: workspace.project.status,
      missingRequired,
      recommendedMissing,
      nextAction: { zh: nextStepFor(workspace, "zh"), en: nextStepFor(workspace, "en") },
      confidenceLevel: completeness.percent >= 80 ? "High" : completeness.percent >= 50 ? "Medium" : "Low",
      reasons: [
        { zh: "成熟度根据当前已填写信息估算。", en: "Readiness is estimated from the information currently provided." },
      ],
    },
  };
}

function calculateBenchmark(workspace: ProjectWorkspace, platformCatalog: PlcEcosystem[] = fallbackEcosystems): BenchmarkResult[] {
  return platformCatalog
    .filter((platform) => workspace.intake.candidatePlatforms.includes(platform.id))
    .map((platform) => {
      const preference = workspace.preferences.find((item) => item.platformId === platform.id)?.preferenceWeight ?? 50;
      const technical = averageScore(platform);
      const weighted = Math.round(technical * 0.72 + preference * 0.28);
      const riskLevel = weighted >= 78 ? "Low" : weighted >= 65 ? "Medium" : "High";
      return {
        platformId: platform.id,
        technicalScore: technical,
        preferenceScore: preference,
        weightedScore: weighted,
        riskLevel,
        rationale: {
          zh: `${platform.name} 的技术评分为 ${technical}，用户倾向为 ${preference}，综合后最终评分为 ${weighted}。`,
          en: `${platform.name} has a technical score of ${technical}, user preference of ${preference}, and final score of ${weighted}.`,
        },
        assumptions: [
          { zh: "技术评分来自当前平台基础资料。", en: "Technical scores come from the current platform reference information." },
          { zh: "用户倾向占最终评分 28%。", en: "User preference contributes 28% of the final score." },
        ],
      } satisfies BenchmarkResult;
    })
    .sort((a, b) => b.weightedScore - a.weightedScore);
}

function platformName(platformId: string, platformCatalog: PlcEcosystem[]) {
  return platformCatalog.find((platform) => platform.id === platformId)?.name ?? platformId;
}

function uniqueStrings(items: string[]) {
  return Array.from(new Set(items.filter((item) => item.trim().length > 0)));
}

function missingInputLabels(readiness: ProjectReadiness, language: Language) {
  return uniqueStrings([...readiness.missingRequired, ...readiness.recommendedMissing].map((item) => localize(item, language)));
}

function reportStatusNotice(status: ProjectStatus, labels: (typeof copy)[Language]) {
  if (status === "Draft") return labels.reportDraftWarning;
  if (status === "Analyzing") return labels.reportAnalyzingWarning;
  if (status === "Report Ready") return labels.reportReadyNotice;
  return labels.finalizedReportNotice;
}

function safeFileName(value: string) {
  return value.trim().replace(/[\\/:*?"<>|]+/g, "-").replace(/\s+/g, "-").toLowerCase() || "plc-decision-report";
}

function reportAnalysisScope(workspace: ProjectWorkspace, language: Language) {
  return {
    references: uniqueStrings(workspace.report.sections.flatMap((section) => section.dataSourcesUsed.map((item) => localize(item, language)))),
    basis: uniqueStrings(workspace.report.sections.flatMap((section) => section.assumptions.map((item) => localize(item, language)))),
    limits: uniqueStrings(workspace.report.sections.map((section) => `${localize(section.title, language)}: ${localize(section.uncertainty, language)}`)),
    unreadAttachments: workspace.attachments.map((attachment) => `${attachment.fileName} (${attachment.fileType})`),
  };
}

function buildReportMarkdown(
  workspace: ProjectWorkspace,
  benchmarkResults: BenchmarkResult[],
  readiness: ProjectReadiness,
  language: Language,
  platformCatalog: PlcEcosystem[],
) {
  const labels = copy[language];
  const candidatePlatforms = workspace.intake.candidatePlatforms.map((id) => platformName(id, platformCatalog));
  const lead = benchmarkResults[0];
  const leadName = lead ? platformName(lead.platformId, platformCatalog) : "-";
  const analysisScope = reportAnalysisScope(workspace, language);
  const sectionById = (id: string) => workspace.report.sections.find((section) => section.id === id);
  const executiveSummary = sectionById("executive-summary") ?? workspace.report.sections[0];
  const risks = uniqueStrings(benchmarkResults.flatMap((result) => result.assumptions.map((item) => localize(item, language))));
  const preferenceLines = workspace.preferences
    .filter((preference) => workspace.intake.candidatePlatforms.includes(preference.platformId))
    .map((preference) => `- ${platformName(preference.platformId, platformCatalog)}: ${preference.preferenceWeight}/100${preference.userReasonNote ? ` - ${preference.userReasonNote}` : ""}`);

  return [
    `# ${workspace.project.name}`,
    "",
    `## ${language === "zh" ? "执行摘要" : "Executive Summary"}`,
    executiveSummary ? localize(executiveSummary.body, language) : "-",
    "",
    `## ${labels.projectInputs}`,
    `- ${labels.project}: ${workspace.project.name}`,
    `- ${language === "zh" ? "行业" : "Industry"}: ${workspace.project.industry || "-"}`,
    `- ${language === "zh" ? "目标" : "Goal"}: ${workspace.project.goal || "-"}`,
    `- ${labels.candidatePlatforms}: ${candidatePlatforms.join(", ") || "-"}`,
    `- ${labels.status}: ${readiness.status}`,
    `- ${labels.readiness}: ${readiness.score}%`,
    `- ${labels.confidence}: ${readiness.confidenceLevel}`,
    "",
    `## ${labels.benchmarkSummary}`,
    ...(benchmarkResults.length
      ? benchmarkResults.map((result, index) => `- ${index + 1}. ${platformName(result.platformId, platformCatalog)}: ${labels.technicalScore} ${result.technicalScore}, ${labels.preferenceScore} ${result.preferenceScore}, ${labels.finalScore} ${result.weightedScore}, ${labels.risk} ${result.riskLevel}`)
      : [`- ${language === "zh" ? "暂无 Benchmark 结果" : "No benchmark result available"}`]),
    "",
    `## ${labels.preferenceImpact}`,
    ...(preferenceLines.length ? preferenceLines : [`- ${language === "zh" ? "暂无用户倾向说明" : "No user preference notes yet"}`]),
    "",
    `## ${labels.riskAssessment}`,
    `- ${labels.topRecommendation}: ${leadName}`,
    ...(risks.length ? risks.map((item) => `- ${item}`) : [`- ${language === "zh" ? "风险仍需根据真实供应商、成本和交付约束确认。" : "Risks still need confirmation against real vendor, cost, and delivery constraints."}`]),
    "",
    `## ${labels.roadmapNextSteps}`,
    `- ${localize(readiness.nextAction, language)}`,
    "",
    `## ${labels.analysisScope}`,
    "",
    `### ${labels.dataSources}`,
    ...(analysisScope.references.length ? analysisScope.references.map((item) => `- ${item}`) : ["-"]),
    "",
    `### ${labels.assumptions}`,
    ...(analysisScope.basis.length ? analysisScope.basis.map((item) => `- ${item}`) : ["-"]),
    "",
    `### ${labels.uncertainty}`,
    ...(analysisScope.limits.length ? analysisScope.limits.map((item) => `- ${item}`) : ["-"]),
    "",
    `### ${labels.unreadAttachments}`,
    ...(analysisScope.unreadAttachments.length ? analysisScope.unreadAttachments.map((item) => `- ${item}`) : [`- ${language === "zh" ? "暂无登记附件" : "No registered attachments"}`]),
  ].join("\n");
}

function escapeHtml(value: string) {
  return value
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;")
    .replace(/'/g, "&#039;");
}

function buildReportPrintHtml(
  workspace: ProjectWorkspace,
  benchmarkResults: BenchmarkResult[],
  readiness: ProjectReadiness,
  language: Language,
  platformCatalog: PlcEcosystem[],
) {
  const candidatePlatforms = workspace.intake.candidatePlatforms.map((id) => platformName(id, platformCatalog)).join(", ") || "-";
  const lead = benchmarkResults[0];
  const leadName = lead ? platformName(lead.platformId, platformCatalog) : "-";
  const analysisScope = reportAnalysisScope(workspace, language);
  const benchmarkRows = benchmarkResults
    .map((result, index) => `<tr><td>${index + 1}</td><td>${escapeHtml(platformName(result.platformId, platformCatalog))}</td><td>${result.technicalScore}</td><td>${result.preferenceScore}</td><td>${result.weightedScore}</td><td>${escapeHtml(result.riskLevel)}</td></tr>`)
    .join("");
  const reportSectionsHtml = workspace.report.sections
    .map((section, index) => {
      return `<section class="report-section"><h2><span>${String(index + 1).padStart(2, "0")}</span>${escapeHtml(localize(section.title, language))}</h2><div class="body">${escapeHtml(localize(section.body, language) || "-").replace(/\n/g, "<br>")}</div></section>`;
    })
    .join("");
  const scopeList = (items: string[]) => `<ul>${(items.length ? items : ["-"]).map((item) => `<li>${escapeHtml(item)}</li>`).join("")}</ul>`;
  const analysisScopeHtml = `<section class="report-section analysis-scope"><h2>${language === "zh" ? "分析范围" : "Analysis Scope"}</h2><div class="evidence"><strong>${language === "zh" ? "参考信息" : "Reference Information"}</strong>${scopeList(analysisScope.references)}<strong>${language === "zh" ? "分析依据" : "Analysis Basis"}</strong>${scopeList(analysisScope.basis)}<strong>${language === "zh" ? "结论限制" : "Conclusion Limits"}</strong>${scopeList(analysisScope.limits)}<strong>${language === "zh" ? "尚未读取的附件" : "Attachments Not Yet Read"}</strong>${scopeList(analysisScope.unreadAttachments)}</div></section>`;

  return `<!doctype html><html lang="${language === "zh" ? "zh-CN" : "en"}"><head><meta charset="utf-8"><title>${escapeHtml(workspace.project.name)}</title><style>
    @page { size: A4; margin: 16mm; }
    * { box-sizing: border-box; }
    body { margin: 0; color: #0f172a; font-family: Inter, "Microsoft YaHei", "Noto Sans SC", Arial, sans-serif; font-size: 10.5pt; line-height: 1.55; }
    header { border-bottom: 3px solid #0e7490; padding-bottom: 18px; margin-bottom: 22px; }
    .eyebrow { color: #0e7490; font-size: 9pt; font-weight: 700; text-transform: uppercase; }
    h1 { margin: 6px 0 8px; font-size: 25pt; line-height: 1.2; }
    h2 { display: flex; gap: 10px; align-items: center; margin: 0 0 12px; font-size: 16pt; }
    h2 span { color: #64748b; font-size: 9pt; }
    .meta { display: grid; grid-template-columns: repeat(3, 1fr); gap: 10px; margin: 18px 0 24px; }
    .fact { border: 1px solid #cbd5e1; padding: 10px; border-radius: 4px; }
    .fact small { display: block; color: #64748b; font-weight: 700; margin-bottom: 4px; }
    table { width: 100%; border-collapse: collapse; margin: 12px 0 24px; }
    th, td { border-bottom: 1px solid #cbd5e1; padding: 8px; text-align: left; }
    th { background: #f1f5f9; font-size: 9pt; }
    .report-section { break-inside: avoid; page-break-inside: avoid; border-top: 1px solid #cbd5e1; padding-top: 18px; margin-top: 22px; }
    .body { white-space: normal; }
    .evidence { margin-top: 14px; padding: 12px; background: #f8fafc; border-left: 3px solid #0891b2; font-size: 9pt; }
    .evidence ul { margin: 4px 0 10px 18px; padding: 0; }
    footer { margin-top: 28px; border-top: 1px solid #cbd5e1; padding-top: 10px; color: #64748b; font-size: 8.5pt; }
  </style></head><body>
    <header><div class="eyebrow">PLC Platform Benchmark & Migration Decision Copilot</div><h1>${escapeHtml(workspace.project.name)}</h1><div>${escapeHtml(workspace.project.goal || "-")}</div></header>
    <div class="meta">
      <div class="fact"><small>${language === "zh" ? "行业" : "Industry"}</small>${escapeHtml(workspace.project.industry || "-")}</div>
      <div class="fact"><small>${language === "zh" ? "候选平台" : "Candidate Platforms"}</small>${escapeHtml(candidatePlatforms)}</div>
      <div class="fact"><small>${language === "zh" ? "首选平台" : "Top Recommendation"}</small>${escapeHtml(leadName)}</div>
      <div class="fact"><small>${language === "zh" ? "状态" : "Status"}</small>${escapeHtml(readiness.status)}</div>
      <div class="fact"><small>${language === "zh" ? "成熟度" : "Readiness"}</small>${readiness.score}%</div>
      <div class="fact"><small>${language === "zh" ? "置信度" : "Confidence"}</small>${escapeHtml(readiness.confidenceLevel)}</div>
    </div>
    <h2>${language === "zh" ? "平台 Benchmark" : "Platform Benchmark"}</h2>
    <table><thead><tr><th>#</th><th>${language === "zh" ? "平台" : "Platform"}</th><th>${language === "zh" ? "技术" : "Technical"}</th><th>${language === "zh" ? "偏好" : "Preference"}</th><th>${language === "zh" ? "总分" : "Final"}</th><th>${language === "zh" ? "风险" : "Risk"}</th></tr></thead><tbody>${benchmarkRows || `<tr><td colspan="6">-</td></tr>`}</tbody></table>
    ${reportSectionsHtml}
    ${analysisScopeHtml}
    <footer>PLC Platform Benchmark & Migration Decision Copilot</footer>
  </body></html>`;
}

async function exportReportPptx(
  workspace: ProjectWorkspace,
  benchmarkResults: BenchmarkResult[],
  readiness: ProjectReadiness,
  language: Language,
  platformCatalog: PlcEcosystem[],
) {
  const { default: PptxGenJS } = await import("pptxgenjs");
  const pptx = new PptxGenJS();
  pptx.layout = "LAYOUT_WIDE";
  pptx.author = "PLC Platform Benchmark & Migration Decision Copilot";
  pptx.company = "PLC Decision Copilot";
  pptx.subject = workspace.project.goal;
  pptx.title = workspace.project.name;
  const analysisScope = reportAnalysisScope(workspace, language);

  const addHeader = (slide: ReturnType<typeof pptx.addSlide>, title: string, subtitle?: string) => {
    slide.background = { color: "F8FAFC" };
    slide.addText(title, { x: 0.65, y: 0.45, w: 11.9, h: 0.45, fontFace: "Aptos Display", fontSize: 24, bold: true, color: "0F172A", margin: 0 });
    if (subtitle) slide.addText(subtitle, { x: 0.65, y: 0.95, w: 11.9, h: 0.3, fontFace: "Aptos", fontSize: 10, color: "64748B", margin: 0 });
    slide.addShape(pptx.ShapeType.line, { x: 0.65, y: 1.35, w: 12, h: 0, line: { color: "0891B2", width: 2 } });
  };
  const addFooter = (slide: ReturnType<typeof pptx.addSlide>) => {
    slide.addText("PLC Platform Benchmark & Migration Decision Copilot", { x: 0.65, y: 7.15, w: 8.5, h: 0.2, fontSize: 8, color: "64748B", margin: 0 });
  };

  const titleSlide = pptx.addSlide();
  titleSlide.background = { color: "0F172A" };
  titleSlide.addText("PLC PLATFORM DECISION REPORT", { x: 0.75, y: 0.7, w: 8.5, h: 0.35, fontSize: 13, bold: true, color: "22D3EE", charSpacing: 1.5, margin: 0 });
  titleSlide.addText(workspace.project.name, { x: 0.75, y: 1.4, w: 11.7, h: 1.35, fontFace: "Aptos Display", fontSize: 34, bold: true, color: "FFFFFF", breakLine: false, margin: 0 });
  titleSlide.addText(workspace.project.goal || "-", { x: 0.75, y: 3.05, w: 10.8, h: 0.9, fontSize: 18, color: "CBD5E1", margin: 0 });
  titleSlide.addText(`${readiness.status} · ${readiness.score}% · ${readiness.confidenceLevel}`, { x: 0.75, y: 5.8, w: 8, h: 0.35, fontSize: 15, bold: true, color: "FFFFFF", margin: 0 });
  titleSlide.addText(new Date().toLocaleDateString(language === "zh" ? "zh-CN" : "en-US"), { x: 0.75, y: 6.35, w: 4, h: 0.25, fontSize: 10, color: "94A3B8", margin: 0 });

  const overviewSlide = pptx.addSlide();
  addHeader(overviewSlide, language === "zh" ? "项目概览" : "Project Overview", workspace.project.goal || "-");
  const overviewFacts = [
    [language === "zh" ? "行业" : "Industry", workspace.project.industry || "-"],
    [language === "zh" ? "项目规模" : "Project Size", workspace.intake.projectSize],
    ["I/O", String(workspace.intake.ioScale)],
    [language === "zh" ? "成熟度" : "Readiness", `${readiness.score}%`],
    [language === "zh" ? "状态" : "Status", readiness.status],
    [language === "zh" ? "置信度" : "Confidence", readiness.confidenceLevel],
  ];
  overviewFacts.forEach(([label, value], index) => {
    const col = index % 3;
    const row = Math.floor(index / 3);
    overviewSlide.addText(label, { x: 0.75 + col * 4.1, y: 1.75 + row * 1.65, w: 3.65, h: 0.25, fontSize: 10, bold: true, color: "64748B", margin: 0 });
    overviewSlide.addText(value, { x: 0.75 + col * 4.1, y: 2.08 + row * 1.65, w: 3.65, h: 0.55, fontSize: 19, bold: true, color: "0F172A", margin: 0 });
  });
  overviewSlide.addText(language === "zh" ? "下一步" : "Next Action", { x: 0.75, y: 5.25, w: 2, h: 0.25, fontSize: 10, bold: true, color: "0891B2", margin: 0 });
  overviewSlide.addText(localize(readiness.nextAction, language), { x: 0.75, y: 5.6, w: 11.6, h: 0.75, fontSize: 16, color: "0F172A", margin: 0 });
  addFooter(overviewSlide);

  const benchmarkSlide = pptx.addSlide();
  addHeader(benchmarkSlide, language === "zh" ? "平台 Benchmark" : "Platform Benchmark", language === "zh" ? "技术评分、用户偏好与最终排序" : "Technical score, user preference, and final ranking");
  const benchmarkLines = benchmarkResults.slice(0, 6).map((result, index) => `${index + 1}. ${platformName(result.platformId, platformCatalog)}   ${result.weightedScore}/100   ${result.riskLevel}`);
  benchmarkSlide.addText(benchmarkLines.length ? benchmarkLines.join("\n") : "-", { x: 0.8, y: 1.75, w: 5.8, h: 4.65, fontSize: 20, bold: true, color: "0F172A", breakLine: false, margin: 0.08, valign: "middle" });
  const lead = benchmarkResults[0];
  benchmarkSlide.addText(language === "zh" ? "当前首选" : "Current Lead", { x: 7.1, y: 1.8, w: 2, h: 0.3, fontSize: 11, bold: true, color: "0891B2", margin: 0 });
  benchmarkSlide.addText(lead ? platformName(lead.platformId, platformCatalog) : "-", { x: 7.1, y: 2.25, w: 5, h: 0.8, fontSize: 28, bold: true, color: "0F172A", margin: 0 });
  benchmarkSlide.addText(lead ? localize(lead.rationale, language) : "-", { x: 7.1, y: 3.3, w: 5, h: 2.2, fontSize: 15, color: "334155", margin: 0 });
  addFooter(benchmarkSlide);

  workspace.report.sections.forEach((section, index) => {
    const slide = pptx.addSlide();
    addHeader(slide, `${String(index + 1).padStart(2, "0")}  ${localize(section.title, language)}`, `${readiness.status} · ${readiness.score}%`);
    const body = localize(section.body, language) || "-";
    slide.addText(body.length > 1800 ? `${body.slice(0, 1797)}...` : body, { x: 0.75, y: 1.7, w: 8.1, h: 4.9, fontSize: 15, color: "1E293B", margin: 0.08, breakLine: false, valign: "top" });
    slide.addText(language === "zh" ? "分析依据与结论限制" : "Analysis Basis & Conclusion Limits", { x: 9.25, y: 1.7, w: 3.3, h: 0.35, fontSize: 12, bold: true, color: "0891B2", margin: 0 });
    const context = [...section.assumptions.map((item) => `• ${localize(item, language)}`), `• ${localize(section.uncertainty, language)}`].join("\n");
    slide.addText(context || "-", { x: 9.25, y: 2.15, w: 3.3, h: 3.85, fontSize: 11, color: "475569", margin: 0.06, breakLine: false, valign: "top" });
    addFooter(slide);
  });

  const scopeSlide = pptx.addSlide();
  addHeader(scopeSlide, language === "zh" ? "分析范围" : "Analysis Scope");
  const scopeBlocks = [
    [language === "zh" ? "参考信息" : "Reference Information", analysisScope.references],
    [language === "zh" ? "分析依据" : "Analysis Basis", analysisScope.basis],
    [language === "zh" ? "结论限制" : "Conclusion Limits", analysisScope.limits],
    [language === "zh" ? "尚未读取的附件" : "Attachments Not Yet Read", analysisScope.unreadAttachments],
  ] as const;
  scopeBlocks.forEach(([title, items], index) => {
    const col = index % 2;
    const row = Math.floor(index / 2);
    const x = 0.75 + col * 6.15;
    const y = 1.7 + row * 2.55;
    scopeSlide.addText(title, { x, y, w: 5.55, h: 0.3, fontSize: 12, bold: true, color: "0891B2", margin: 0 });
    scopeSlide.addText((items.length ? items : ["-"]).map((item) => `• ${item}`).join("\n"), { x, y: y + 0.45, w: 5.55, h: 1.7, fontSize: 11, color: "475569", margin: 0.05, valign: "top" });
  });
  addFooter(scopeSlide);

  await pptx.writeFile({ fileName: `${safeFileName(workspace.project.name)}.pptx` });
}

export default function App() {
  const [language, setLanguage] = useState<Language>("zh");
  const [sidebarOpen, setSidebarOpen] = useState(true);
  const [platformCatalog, setPlatformCatalog] = useState<PlcEcosystem[]>(fallbackEcosystems);
  const [workspaces, setWorkspaces] = useState<ProjectWorkspace[]>(seedWorkspaces);
  const [selectedProjectId, setSelectedProjectId] = useState(seedWorkspaces[0].project.id);
  const [selectedEcosystemId, setSelectedEcosystemId] = useState("siemens-tia");
  const [workspaceView, setWorkspaceView] = useState<"home" | "project">("home");
  const [activeTab, setActiveTab] = useState<WorkspaceTab>("overview");
  const [projectHomeView, setProjectHomeView] = useState<"list" | "type">("list");
  const [activeReportSectionId, setActiveReportSectionId] = useState("executive-summary");
  const [apiMode, setApiMode] = useState<"checking" | "connected" | "fallback">("checking");
  const [saveState, setSaveState] = useState<"idle" | "saving" | "saved" | "failed">("idle");
  const [benchmarkByProject, setBenchmarkByProject] = useState<Record<string, BenchmarkResult[]>>({});
  const [queryScope, setQueryScope] = useState<"global" | "project">("project");
  const [globalMessages, setGlobalMessages] = useState<ChatMessage[]>([]);
  const [draft, setDraft] = useState("");
  const [draftError, setDraftError] = useState("");
  const [projectThreads, setProjectThreads] = useState<Record<string, ChatMessage[]>>({});
  const [globalAiEnabled, setGlobalAiEnabled] = useState(readStoredGlobalAi);
  const [projectAiEnabled, setProjectAiEnabled] = useState<Record<string, boolean>>(readStoredProjectAi);
  const [queryLoadingKey, setQueryLoadingKey] = useState("");
  const [queryErrors, setQueryErrors] = useState<Record<string, { question: string }>>({});
  const queryRequestInFlight = useRef(false);

  const t = copy[language];
  const workspace = workspaces.find((item) => item.project.id === selectedProjectId) ?? workspaces[0] ?? seedWorkspaces[0];
  const selectedEcosystem = platformCatalog.find((item) => item.id === selectedEcosystemId) ?? platformCatalog[0] ?? fallbackEcosystems[0];
  const fallbackBenchmarkResults = useMemo(() => calculateBenchmark(workspace, platformCatalog), [workspace, platformCatalog]);
  const benchmarkResults = benchmarkByProject[selectedProjectId] ?? fallbackBenchmarkResults;
  const topResult = benchmarkResults[0];
  const topPlatform = platformCatalog.find((item) => item.id === topResult?.platformId) ?? platformCatalog[0] ?? fallbackEcosystems[0];
  const projectMessages = projectThreads[selectedProjectId] ?? [];
  const messages = queryScope === "global" ? globalMessages : projectMessages;
  const activeQueryKey = queryScope === "global" ? "global" : `project:${selectedProjectId}`;
  const activeAiEnabled = queryScope === "global" ? globalAiEnabled : Boolean(projectAiEnabled[selectedProjectId]);
  const queryBusy = Boolean(queryLoadingKey);
  const queryLoading = queryLoadingKey === activeQueryKey;
  const activeQueryError = queryErrors[activeQueryKey];
  const completeness = calculateCompleteness(workspace);
  const currentReadiness = getWorkspaceReadiness(workspace).readiness;
  const currentProjectAiEnabled = Boolean(projectAiEnabled[workspace.project.id]);

  useEffect(() => {
    document.documentElement.lang = language === "zh" ? "zh-CN" : "en";
  }, [language]);

  useEffect(() => {
    persistStorage(GLOBAL_AI_STORAGE_KEY, String(globalAiEnabled));
  }, [globalAiEnabled]);

  useEffect(() => {
    persistStorage(PROJECT_AI_STORAGE_KEY, JSON.stringify(projectAiEnabled));
  }, [projectAiEnabled]);

  useEffect(() => {
    let cancelled = false;

    async function loadFromApi() {
      try {
        const [apiEcosystems, apiProjects] = await Promise.all([getEcosystems(), getProjects()]);
        if (cancelled) return;
        setPlatformCatalog(apiEcosystems);
        setWorkspaces(apiProjects);
        if (apiProjects.length > 0) {
          setSelectedProjectId((current) => (apiProjects.some((item) => item.project.id === current) ? current : apiProjects[0].project.id));
        }
        setApiMode("connected");
      } catch (error) {
        console.warn("Backend unavailable, using local mock fallback.", error);
        if (!cancelled) {
          setPlatformCatalog(fallbackEcosystems);
          setWorkspaces(seedWorkspaces);
          setApiMode("fallback");
        }
      }
    }

    loadFromApi();
    return () => {
      cancelled = true;
    };
  }, []);

  function updateWorkspace(next: ProjectWorkspace) {
    setWorkspaces((current) => current.map((item) => (item.project.id === next.project.id ? next : item)));
  }

  function replaceWorkspace(next: ProjectWorkspace) {
    setWorkspaces((current) => {
      const exists = current.some((item) => item.project.id === next.project.id);
      return exists ? current.map((item) => (item.project.id === next.project.id ? next : item)) : [next, ...current];
    });
  }

  function removeWorkspaceLocal(projectId: string) {
    setWorkspaces((current) => {
      const next = current.filter((item) => item.project.id !== projectId);
      setSelectedProjectId((selected) => {
        if (selected !== projectId) return selected;
        return next[0]?.project.id ?? "";
      });
      if (next.length === 0) {
        setWorkspaceView("home");
        setQueryScope("global");
      }
      return next;
    });
    setBenchmarkByProject((current) => {
      const nextMap = { ...current };
      delete nextMap[projectId];
      return nextMap;
    });
    setProjectThreads((current) => {
      const nextMap = { ...current };
      delete nextMap[projectId];
      return nextMap;
    });
    setProjectAiEnabled((current) => {
      const nextMap = { ...current };
      delete nextMap[projectId];
      return nextMap;
    });
    setQueryErrors((current) => {
      const nextMap = { ...current };
      delete nextMap[`project:${projectId}`];
      return nextMap;
    });
  }

  function noteSaved() {
    setSaveState("saved");
  }

  function noteFailed() {
    setSaveState("failed");
  }

  async function createProject() {
    const id = `project-${Date.now()}`;
    const projectName = language === "zh" ? "新建 PLC 决策项目" : "New PLC Decision Project";
    const fallbackWorkspace: ProjectWorkspace = {
      project: {
        id,
        name: projectName,
        industry: "",
        goal: "",
        status: "Draft",
        createdAt: today,
        updatedAt: today,
      },
      intake: {
        projectSize: "Medium",
        ioScale: 300,
        motionRequirement: 50,
        safetyRequirement: 50,
        budgetSensitivity: 50,
        teamExperience: "",
        existingPlatform: "siemens-tia",
        candidatePlatforms: platformCatalog.slice(0, 4).map((item) => item.id),
        constraints: "",
      },
      preferences: platformCatalog.map((platform) => ({ platformId: platform.id, preferenceWeight: 50, userReasonNote: "" })),
      attachments: [],
      report: {
        projectId: id,
        version: 1,
        status: "Draft",
        sections: reportSections(projectName),
      },
    };

    setSaveState("saving");
    try {
      if (apiMode !== "connected") throw new Error("API unavailable");
      const next = await apiCreateProject({ name: projectName, industry: "", goal: "" });
      replaceWorkspace(next);
      setSelectedProjectId(next.project.id);
      noteSaved();
    } catch (error) {
      console.warn("Project creation used local fallback.", error);
      setWorkspaces([fallbackWorkspace, ...workspaces]);
      setSelectedProjectId(id);
      noteFailed();
    } finally {
      setWorkspaceView("project");
      setActiveTab("intake");
      setActiveReportSectionId("executive-summary");
    }
  }

  async function deleteProject(projectId: string) {
    const project = workspaces.find((item) => item.project.id === projectId);
    if (!project) return;
    const confirmed = window.confirm(t.deleteProjectConfirm);
    if (!confirmed) return;

    setSaveState("saving");
    try {
      if (apiMode !== "connected") throw new Error("API unavailable");
      await apiDeleteProject(projectId);
      removeWorkspaceLocal(projectId);
      noteSaved();
    } catch (error) {
      console.warn("Project deletion used local fallback.", error);
      removeWorkspaceLocal(projectId);
      noteFailed();
    }
  }

  async function submitMessage(question: string, appendUser: boolean, forceUseAi?: boolean) {
    if (queryRequestInFlight.current) return;

    const requestScope = queryScope;
    const requestProjectId = selectedProjectId;
    const requestKey = requestScope === "global" ? "global" : `project:${requestProjectId}`;
    const useAi = forceUseAi ?? (requestScope === "global" ? globalAiEnabled : Boolean(projectAiEnabled[requestProjectId]));
    const user: ChatMessage = { role: "user", content: { zh: question, en: question } };

    if (appendUser) {
      if (requestScope === "global") {
        setGlobalMessages((current) => [...current, user]);
      } else {
        setProjectThreads((current) => ({ ...current, [requestProjectId]: [...(current[requestProjectId] ?? []), user] }));
      }
    }

    queryRequestInFlight.current = true;
    setQueryLoadingKey(requestKey);
    setQueryErrors((current) => {
      const next = { ...current };
      delete next[requestKey];
      return next;
    });
    setDraft("");
    setDraftError("");

    try {
      const result = requestScope === "global"
        ? await chatGlobalIntelligence({ question, language, platformIds: [], quality: "fast", useAi })
        : await chatProjectIntelligence(requestProjectId, { question, language, quality: "balanced", useAi });
      const assistant: ChatMessage = { role: "assistant", content: result.answer, intelligence: result };

      if (requestScope === "global") {
        setGlobalMessages((current) => [...current, assistant]);
      } else {
        setProjectThreads((current) => ({ ...current, [requestProjectId]: [...(current[requestProjectId] ?? []), assistant] }));
      }
    } catch (error) {
      console.warn("Intelligence request failed.", error);
      setQueryErrors((current) => ({ ...current, [requestKey]: { question } }));
    } finally {
      queryRequestInFlight.current = false;
      setQueryLoadingKey((current) => (current === requestKey ? "" : current));
    }
  }

  function sendMessage() {
    const question = draft.trim();
    if (!question) {
      setDraftError(t.emptyQuestion);
      return;
    }
    void submitMessage(question, true);
  }

  async function saveIntake(next: ProjectWorkspace) {
    setSaveState("saving");
    const localNext = { ...next, project: { ...next.project, updatedAt: today } };
    try {
      if (apiMode !== "connected") throw new Error("API unavailable");
      const saved = await updateProjectIntake(next.project.id, next.intake);
      replaceWorkspace(saved);
      noteSaved();
    } catch (error) {
      console.warn("Intake save used local fallback.", error);
      updateWorkspace(localNext);
      noteFailed();
    }
  }

  function updatePreferencesLocal(next: ProjectWorkspace) {
    updateWorkspace({ ...next, project: { ...next.project, updatedAt: today } });
    setBenchmarkByProject((current) => {
      const nextMap = { ...current };
      delete nextMap[next.project.id];
      return nextMap;
    });
  }

  async function savePreferences(next: ProjectWorkspace) {
    setSaveState("saving");
    try {
      if (apiMode !== "connected") throw new Error("API unavailable");
      const saved = await updateProjectPreferences(next.project.id, next.preferences);
      replaceWorkspace(saved);
      const results = await runProjectBenchmark(saved.project.id);
      setBenchmarkByProject((current) => ({ ...current, [saved.project.id]: results }));
      noteSaved();
    } catch (error) {
      console.warn("Preference save used local fallback.", error);
      updatePreferencesLocal(next);
      noteFailed();
    }
  }

  async function registerAttachment(projectId: string, attachment: Pick<ProjectAttachment, "fileName" | "fileType" | "declaredPurpose">, fallbackWorkspace: ProjectWorkspace) {
    setSaveState("saving");
    try {
      if (apiMode !== "connected") throw new Error("API unavailable");
      const saved = await addProjectAttachment(projectId, attachment);
      replaceWorkspace(saved);
      noteSaved();
    } catch (error) {
      console.warn("Attachment registration used local fallback.", error);
      updateWorkspace(fallbackWorkspace);
      noteFailed();
    }
  }

  async function runBenchmark(projectId: string) {
    try {
      if (apiMode !== "connected") throw new Error("API unavailable");
      const results = await runProjectBenchmark(projectId);
      setBenchmarkByProject((current) => ({ ...current, [projectId]: results }));
    } catch (error) {
      console.warn("Benchmark used frontend fallback.", error);
      setBenchmarkByProject((current) => {
        const nextMap = { ...current };
        delete nextMap[projectId];
        return nextMap;
      });
    }
  }

  async function saveReportSection(projectId: string, section: ReportSection, fallbackWorkspace: ProjectWorkspace) {
    setSaveState("saving");
    try {
      if (apiMode !== "connected") throw new Error("API unavailable");
      const saved = await apiUpdateReportSection(projectId, section.id, {
        body: section.body,
        assumptions: section.assumptions,
      });
      replaceWorkspace(saved);
      noteSaved();
      return saved;
    } catch (error) {
      console.warn("Report section save used local fallback.", error);
      updateWorkspace(fallbackWorkspace);
      noteFailed();
      return fallbackWorkspace;
    }
  }

  async function updateLifecycleStatus(projectId: string, status: ProjectStatus) {
    setSaveState("saving");
    try {
      const saved = status === "Finalized" ? await finalizeProject(projectId) : status === "Analyzing" ? await reopenProject(projectId) : await apiUpdateProjectStatus(projectId, status);
      replaceWorkspace(saved);
      noteSaved();
    } catch (error) {
      console.warn("Project status update failed.", error);
      noteFailed();
    }
  }

  return (
    <main className="flex h-screen min-h-[760px] overflow-hidden bg-slate-100 text-slate-950">
      <aside className={`${sidebarOpen ? "w-full max-w-[400px]" : "w-[76px]"} flex shrink-0 flex-col border-r border-slate-200 bg-slate-950 text-white transition-all duration-300`}>
        <div className="flex min-h-[92px] items-center justify-between gap-3 border-b border-white/10 p-4">
          {sidebarOpen ? (
            <div className="min-w-0">
              <p className="text-xs font-semibold uppercase tracking-wide text-cyan-300">{t.project}</p>
              <h1 className="mt-1 text-lg font-semibold leading-6">{t.title}</h1>
            </div>
          ) : (
            <Cpu className="mx-auto text-cyan-300" size={24} />
          )}
          <button className="rounded-md bg-white/10 p-2 hover:bg-white/15" onClick={() => setSidebarOpen(!sidebarOpen)} aria-label="Toggle sidebar">
            {sidebarOpen ? <PanelLeftClose size={18} /> : <PanelLeftOpen size={18} />}
          </button>
        </div>

        {sidebarOpen ? (
          <div className="flex min-h-0 flex-1 flex-col">
            <section className="border-b border-white/10 p-4">
              <div className="flex items-start justify-between gap-3">
                <div>
                  <h2 className="text-sm font-semibold">{t.ecosystems}</h2>
                  <p className="mt-1 text-xs leading-5 text-slate-400">{localize(selectedEcosystem.summary, language)}</p>
                </div>
                <button className="inline-flex shrink-0 items-center gap-2 rounded-md bg-white px-3 py-2 text-xs font-semibold text-slate-950 hover:bg-cyan-50" onClick={() => setLanguage(language === "zh" ? "en" : "zh")}>
                  <Languages size={15} />
                  {t.language}
                </button>
              </div>
              <div className="mt-4 grid max-h-[250px] gap-2 overflow-y-auto pr-1">
                {platformCatalog.map((platform) => (
                  <div
                    key={platform.id}
                    className={`flex min-h-[66px] items-stretch rounded-md border transition ${selectedEcosystemId === platform.id ? "border-cyan-400 bg-cyan-400/15" : "border-white/10 bg-white/5 hover:bg-white/10"}`}
                  >
                    <button
                      className="min-w-0 flex-1 p-3 text-left"
                      onClick={() => setSelectedEcosystemId(platform.id)}
                    >
                      <div className="flex items-center gap-3">
                        <Cpu className="shrink-0 text-cyan-300" size={18} />
                        <div className="min-w-0">
                          <p className="truncate text-sm font-semibold">{platform.name}</p>
                          <p className="truncate text-xs text-slate-400">{platform.software}</p>
                        </div>
                      </div>
                    </button>
                    <a
                      className="inline-flex w-11 shrink-0 items-center justify-center border-l border-white/10 text-slate-300 hover:bg-white/10 hover:text-cyan-200 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-inset focus-visible:ring-cyan-300"
                      href={platform.officialUrl}
                      target="_blank"
                      rel="noreferrer"
                      aria-label={`${t.officialWebsite}: ${platform.name}`}
                      title={`${t.officialWebsite}: ${platform.name}`}
                    >
                      <ExternalLink size={17} />
                    </a>
                  </div>
                ))}
              </div>
            </section>

            <section className="flex min-h-0 flex-1 flex-col p-4">
              <div className="flex flex-wrap items-center justify-between gap-3">
                <div className="flex items-center gap-2">
                  <MessageSquareText className="text-cyan-300" size={18} />
                  <h2 className="text-sm font-semibold">{queryScope === "global" ? t.globalQuery : t.projectQuery}</h2>
                </div>
                <div className="flex items-center gap-2">
                  <label className="inline-flex cursor-pointer items-center gap-2 rounded-md bg-white/10 px-2 py-1.5 text-xs font-semibold text-slate-200">
                    <span>{t.aiToggle}</span>
                    <input
                      className="peer sr-only"
                      type="checkbox"
                      checked={activeAiEnabled}
                      onChange={(event) => {
                        if (queryScope === "global") {
                          setGlobalAiEnabled(event.target.checked);
                        } else {
                          setProjectAiEnabled((current) => ({ ...current, [selectedProjectId]: event.target.checked }));
                        }
                      }}
                      aria-label={queryScope === "global" ? t.globalAiToggle : t.projectAiToggle}
                    />
                    <span className="relative h-5 w-9 rounded-full bg-slate-600 transition after:absolute after:left-0.5 after:top-0.5 after:h-4 after:w-4 after:rounded-full after:bg-white after:transition-transform after:content-[''] peer-checked:bg-cyan-400 peer-checked:after:translate-x-4 peer-focus-visible:ring-2 peer-focus-visible:ring-cyan-300" />
                    <span className="sr-only">{activeAiEnabled ? t.aiEnabled : t.aiDisabled}</span>
                  </label>
                  <div className="inline-flex rounded-md bg-white/10 p-1">
                    <button className={`rounded px-2 py-1 text-xs font-semibold ${queryScope === "global" ? "bg-white text-slate-950" : "text-slate-300 hover:text-white"}`} onClick={() => setQueryScope("global")}>
                      {t.global}
                    </button>
                    <button className={`rounded px-2 py-1 text-xs font-semibold ${queryScope === "project" ? "bg-white text-slate-950" : "text-slate-300 hover:text-white"}`} onClick={() => setQueryScope("project")}>
                      {t.projectScope}
                    </button>
                  </div>
                </div>
              </div>
              {queryScope === "project" ? (
                <div className="mt-3 rounded-md border border-white/10 bg-white/5 p-3">
                  <p className="text-sm font-semibold">{workspace.project.name}</p>
                  <p className="mt-1 text-xs leading-5 text-slate-400">{workspace.project.goal || nextStepFor(workspace, language)}</p>
                </div>
              ) : (
                <div className="mt-3 rounded-md border border-white/10 bg-white/5 p-3">
                  <p className="text-sm font-semibold">{language === "zh" ? "PLC 生态选型" : "PLC ecosystem selection"}</p>
                  <p className="mt-1 text-xs leading-5 text-slate-400">{language === "zh" ? "跨项目讨论平台比较、风险、成本和长期维护。" : "Cross-project discussion for platform comparison, risk, cost, and maintainability."}</p>
                </div>
              )}
              <div className="mt-3 min-h-0 flex-1 space-y-3 overflow-y-auto pr-1">
                {messages.length === 0 ? <p className="rounded-md border border-dashed border-white/15 p-3 text-xs leading-5 text-slate-400">{t.queryEmpty}</p> : null}
                {messages.map((message, index) => (
                  <ChatMessageCard key={message.intelligence?.id ?? `${message.role}-${index}`} message={message} labels={t} language={language} />
                ))}
                {queryLoading ? <div className="rounded-md bg-cyan-400/10 p-3 text-sm font-semibold text-cyan-100">{t.queryLoading}</div> : null}
              </div>
              <div className="mt-3">
                {draftError ? <p className="mb-2 text-xs font-medium text-amber-300">{draftError}</p> : null}
                {activeQueryError ? (
                  <div className="mb-2 rounded-md border border-rose-400/30 bg-rose-400/10 p-2 text-xs text-rose-100">
                    <span>{t.queryFailed}</span>
                    <div className="mt-2 flex flex-wrap gap-2">
                      <button className="shrink-0 rounded-md bg-white px-2 py-1 font-semibold text-rose-800 hover:bg-rose-50 disabled:cursor-not-allowed disabled:opacity-60" onClick={() => void submitMessage(activeQueryError.question, false)} disabled={queryBusy}>{t.retry}</button>
                      <button className="shrink-0 rounded-md bg-slate-950 px-2 py-1 font-semibold text-white hover:bg-slate-800 disabled:cursor-not-allowed disabled:opacity-60" onClick={() => void submitMessage(activeQueryError.question, false, false)} disabled={queryBusy}>{t.useBasicAnalysis}</button>
                    </div>
                  </div>
                ) : null}
                <div className="flex gap-2">
                  <textarea className="h-20 min-w-0 flex-1 resize-none rounded-md border border-white/10 bg-slate-900 p-3 text-sm text-white outline-none ring-cyan-400 placeholder:text-slate-500 focus:ring-2 disabled:cursor-not-allowed disabled:opacity-60" placeholder={queryScope === "global" ? t.globalPlaceholder : t.projectPlaceholder} value={draft} onChange={(event) => { setDraft(event.target.value); setDraftError(""); }} disabled={queryBusy} />
                  <button className="inline-flex w-12 items-center justify-center rounded-md bg-cyan-500 text-slate-950 hover:bg-cyan-400 disabled:cursor-not-allowed disabled:bg-slate-600 disabled:text-slate-300" onClick={sendMessage} aria-label={t.send} disabled={queryBusy || !draft.trim()}>
                    <Send size={18} />
                  </button>
                </div>
              </div>
            </section>
          </div>
        ) : null}
      </aside>

      <section className="min-w-0 flex-1 overflow-y-auto">
        {workspaceView === "project" ? (
        <header className="border-b border-slate-200 bg-white px-5 py-5 lg:px-6">
          <div className="flex flex-col gap-4 xl:flex-row xl:items-center xl:justify-between">
            <div>
              <p className="text-xs font-semibold uppercase tracking-wide text-cyan-700">{t.subtitle}</p>
              <div className="mt-2 flex flex-wrap items-center gap-3">
                <button className="inline-flex items-center gap-2 rounded-md bg-slate-100 px-3 py-2 text-sm font-semibold text-slate-700 hover:bg-slate-200" onClick={() => setWorkspaceView("home")}>
                  <ChevronRight className="rotate-180" size={16} />
                  {t.backToWorkspace}
                </button>
                <select className="max-w-full rounded-md border border-slate-300 bg-white px-3 py-2 text-lg font-semibold" value={selectedProjectId} onChange={(event) => setSelectedProjectId(event.target.value)}>
                  {workspaces.map((item) => (
                    <option key={item.project.id} value={item.project.id}>
                      {item.project.name}
                    </option>
                  ))}
                </select>
                <button className="inline-flex items-center gap-2 rounded-md bg-slate-950 px-3 py-2 text-sm font-semibold text-white hover:bg-slate-800" onClick={createProject}>
                  <FolderPlus size={16} />
                  {t.newProject}
                </button>
                <StatusPill apiMode={apiMode} saveState={saveState} labels={t} />
              </div>
            </div>
            <div className="grid grid-cols-3 gap-3 text-sm">
              <Kpi label={t.status} value={workspace.project.status} />
              <Kpi label={t.readiness} value={`${currentReadiness.score}%`} />
              <Kpi label={t.weightedScore} value={`${topResult?.weightedScore ?? 0}/100`} />
            </div>
          </div>

          <FlowNav activeTab={activeTab} setActiveTab={setActiveTab} language={language} completeness={completeness.percent} />

          <nav className="mt-4 flex gap-2 overflow-x-auto pb-1">
            {tabs.map((tab) => (
              <button key={tab.id} className={`inline-flex shrink-0 items-center gap-2 rounded-md px-3 py-2 text-sm font-semibold transition ${activeTab === tab.id ? "bg-cyan-700 text-white" : "bg-slate-100 text-slate-700 hover:bg-slate-200"}`} onClick={() => setActiveTab(tab.id)}>
                {tab.icon}
                {t[tab.id]}
              </button>
            ))}
          </nav>
        </header>
        ) : null}

        <div className="p-5 lg:p-6">
          {workspaceView === "home" ? (
            <ProjectHome
              workspaces={workspaces}
              selectedProjectId={selectedProjectId}
              setSelectedProjectId={setSelectedProjectId}
              setActiveTab={setActiveTab}
              setWorkspaceView={setWorkspaceView}
              createProject={createProject}
              deleteProject={deleteProject}
              language={language}
              labels={t}
              apiMode={apiMode}
              saveState={saveState}
              platformCatalog={platformCatalog}
              view={projectHomeView}
              setView={setProjectHomeView}
            />
          ) : null}
          {workspaceView === "project" && activeTab === "overview" ? <ProjectOverview workspace={workspace} topPlatform={topPlatform} topResult={topResult} language={language} labels={t} platformCatalog={platformCatalog} setActiveTab={setActiveTab} /> : null}
          {workspaceView === "project" && activeTab === "intake" ? <Intake workspace={workspace} updateWorkspace={saveIntake} platformCatalog={platformCatalog} language={language} labels={t} /> : null}
          {workspaceView === "project" && activeTab === "preferences" ? <Preferences workspace={workspace} updateWorkspace={updatePreferencesLocal} savePreferences={savePreferences} platformCatalog={platformCatalog} language={language} labels={t} /> : null}
          {workspaceView === "project" && activeTab === "attachments" ? <Attachments key={workspace.project.id} workspace={workspace} registerAttachment={registerAttachment} language={language} labels={t} useAi={currentProjectAiEnabled} /> : null}
          {workspaceView === "project" && activeTab === "benchmark" ? <Benchmark key={workspace.project.id} results={benchmarkResults} workspace={workspace} platformCatalog={platformCatalog} labels={t} language={language} onRunBenchmark={runBenchmark} useAi={currentProjectAiEnabled} /> : null}
          {workspaceView === "project" && activeTab === "report" ? <ReportBuilder key={workspace.project.id} workspace={workspace} updateWorkspace={updateWorkspace} saveReportSection={saveReportSection} updateLifecycleStatus={updateLifecycleStatus} labels={t} language={language} activeSectionId={activeReportSectionId} setActiveSectionId={setActiveReportSectionId} benchmarkResults={benchmarkResults} platformCatalog={platformCatalog} useAi={currentProjectAiEnabled} /> : null}
        </div>
      </section>
    </main>
  );
}

function FlowNav({ activeTab, setActiveTab, language, completeness }: { activeTab: WorkspaceTab; setActiveTab: (tab: WorkspaceTab) => void; language: Language; completeness: number }) {
  const names = language === "zh" ? ["创建项目", "Intake", "Preferences", "Attachments", "Benchmark", "Report"] : ["Create", "Intake", "Preferences", "Attachments", "Benchmark", "Report"];
  return (
    <div className="mt-5 flex items-center gap-2 overflow-x-auto rounded-md border border-slate-200 bg-slate-50 p-2">
      {tabOrder.map((tab, index) => {
        const passed = completeness >= Math.min(100, index * 18);
        return (
          <button key={tab} className={`inline-flex shrink-0 items-center gap-2 rounded-md px-3 py-2 text-xs font-semibold ${activeTab === tab ? "bg-white text-cyan-800 shadow-sm" : "text-slate-600 hover:bg-white"}`} onClick={() => setActiveTab(tab)}>
            <span className={`inline-flex h-5 w-5 items-center justify-center rounded-full ${passed ? "bg-emerald-100 text-emerald-700" : "bg-slate-200 text-slate-500"}`}>{passed ? <Check size={13} /> : index + 1}</span>
            {names[index]}
            {index < tabOrder.length - 1 ? <ChevronRight className="text-slate-300" size={14} /> : null}
          </button>
        );
      })}
    </div>
  );
}

function StatusPill({ apiMode, saveState, labels }: { apiMode: "checking" | "connected" | "fallback"; saveState: "idle" | "saving" | "saved" | "failed"; labels: (typeof copy)[Language] }) {
  const apiText = apiMode === "connected" ? labels.apiConnected : apiMode === "fallback" ? labels.mockFallback : labels.checkingApi;
  const saveText = saveState === "saving" ? labels.saving : saveState === "saved" ? labels.saved : saveState === "failed" ? labels.saveFailed : "";
  const tone = apiMode === "connected" ? "bg-emerald-50 text-emerald-700 ring-emerald-200" : apiMode === "fallback" ? "bg-amber-50 text-amber-800 ring-amber-200" : "bg-slate-50 text-slate-600 ring-slate-200";

  return (
    <div className={`inline-flex items-center gap-2 rounded-md px-3 py-2 text-xs font-semibold ring-1 ${tone}`}>
      <span>{apiText}</span>
      {saveText ? <span className="border-l border-current/20 pl-2">{saveText}</span> : null}
    </div>
  );
}

function StatusBadge({ status }: { status: ProjectStatus }) {
  return <span className={`rounded-full px-2.5 py-1 text-xs font-semibold ring-1 ${statusClass[status]}`}>{status}</span>;
}

function ReadinessList({ title, items, language, empty }: { title: string; items: LocalizedText[]; language: Language; empty: string }) {
  return (
    <div className="rounded-md bg-slate-50 p-4">
      <p className="text-sm font-semibold">{title}</p>
      {items.length > 0 ? (
        <ul className="mt-2 space-y-1 text-sm leading-6 text-slate-600">
          {items.map((item) => (
            <li key={localize(item, language)}>{localize(item, language)}</li>
          ))}
        </ul>
      ) : (
        <p className="mt-2 text-sm text-slate-500">{empty}</p>
      )}
    </div>
  );
}

function ProjectHome({
  workspaces,
  selectedProjectId,
  setSelectedProjectId,
  setActiveTab,
  setWorkspaceView,
  createProject,
  deleteProject,
  language,
  labels,
  apiMode,
  saveState,
  platformCatalog,
  view,
  setView,
}: {
  workspaces: ProjectWorkspace[];
  selectedProjectId: string;
  setSelectedProjectId: (id: string) => void;
  setActiveTab: (tab: WorkspaceTab) => void;
  setWorkspaceView: (view: "home" | "project") => void;
  createProject: () => void | Promise<void>;
  deleteProject: (projectId: string) => void | Promise<void>;
  language: Language;
  labels: (typeof copy)[Language];
  apiMode: "checking" | "connected" | "fallback";
  saveState: "idle" | "saving" | "saved" | "failed";
  platformCatalog: PlcEcosystem[];
  view: "list" | "type";
  setView: (view: "list" | "type") => void;
}) {
  const groups = workspaces.reduce<Record<string, ProjectWorkspace[]>>((acc, item) => {
    const key = item.project.industry || (language === "zh" ? "未分类" : "Unclassified");
    acc[key] = [...(acc[key] ?? []), item];
    return acc;
  }, {});

  return (
    <div className="grid gap-5">
      <Panel title={labels.currentWorkResults} description={labels.workspaceOverview}>
        <div className="flex flex-col gap-4 md:flex-row md:items-center md:justify-between">
          <div className="grid gap-3 md:grid-cols-3">
            <Kpi label={labels.projectList} value={`${workspaces.length}`} />
            <Kpi label={labels.status} value={`${workspaces.filter((item) => item.project.status === "Report Ready").length} Ready`} />
            <Kpi label={labels.byType} value={`${Object.keys(groups).length}`} />
          </div>
          <div className="flex flex-wrap items-center gap-3">
            <button className="inline-flex items-center gap-2 rounded-md bg-slate-950 px-4 py-2 text-sm font-semibold text-white hover:bg-slate-800" onClick={createProject}>
              <FolderPlus size={16} />
              {labels.createPLCDecisionProject}
            </button>
            <div className="inline-flex w-fit rounded-md border border-slate-200 bg-slate-50 p-1">
              <button className={`rounded px-3 py-2 text-sm font-semibold ${view === "list" ? "bg-white text-cyan-800 shadow-sm" : "text-slate-600 hover:text-slate-900"}`} onClick={() => setView("list")}>
                {labels.listView}
              </button>
              <button className={`rounded px-3 py-2 text-sm font-semibold ${view === "type" ? "bg-white text-cyan-800 shadow-sm" : "text-slate-600 hover:text-slate-900"}`} onClick={() => setView("type")}>
                {labels.typeView}
              </button>
            </div>
            <StatusPill apiMode={apiMode} saveState={saveState} labels={labels} />
          </div>
        </div>
      </Panel>

      {workspaces.length === 0 ? (
        <Panel title={labels.noProjects} description={labels.noProjectsHint}>
          <button className="inline-flex items-center gap-2 rounded-md bg-cyan-700 px-4 py-2 text-sm font-semibold text-white hover:bg-cyan-800" onClick={createProject}>
            <FolderPlus size={16} />
            {labels.newProject}
          </button>
        </Panel>
      ) : null}

      {view === "list" ? (
        <div className="grid gap-4">
          {workspaces.map((item) => (
            <ProjectEntryCard key={item.project.id} workspace={item} selected={item.project.id === selectedProjectId} language={language} labels={labels} platformCatalog={platformCatalog} setSelectedProjectId={setSelectedProjectId} setActiveTab={setActiveTab} setWorkspaceView={setWorkspaceView} deleteProject={deleteProject} />
          ))}
        </div>
      ) : (
        <div className="grid gap-5">
          {Object.entries(groups).map(([type, items]) => (
            <Panel key={type} title={type} description={`${items.length} ${language === "zh" ? "个项目" : "projects"}`}>
              <div className="grid gap-4">
                {items.map((item) => (
                  <ProjectEntryCard key={item.project.id} workspace={item} selected={item.project.id === selectedProjectId} language={language} labels={labels} platformCatalog={platformCatalog} setSelectedProjectId={setSelectedProjectId} setActiveTab={setActiveTab} setWorkspaceView={setWorkspaceView} deleteProject={deleteProject} />
                ))}
              </div>
            </Panel>
          ))}
        </div>
      )}
    </div>
  );
}

function ProjectEntryCard({
  workspace,
  selected,
  language,
  labels,
  platformCatalog,
  setSelectedProjectId,
  setActiveTab,
  setWorkspaceView,
  deleteProject,
}: {
  workspace: ProjectWorkspace;
  selected: boolean;
  language: Language;
  labels: (typeof copy)[Language];
  platformCatalog: PlcEcosystem[];
  setSelectedProjectId: (id: string) => void;
  setActiveTab: (tab: WorkspaceTab) => void;
  setWorkspaceView: (view: "home" | "project") => void;
  deleteProject: (projectId: string) => void | Promise<void>;
}) {
  const { readiness, isLocal } = getWorkspaceReadiness(workspace);
  const keyInputs = calculateKeyInputCompleteness(workspace);
  const benchmark = calculateBenchmark(workspace, platformCatalog);
  const topResult = benchmark[0];
  const topPlatform = platformCatalog.find((item) => item.id === topResult?.platformId);
  const candidatePlatformNames = workspace.intake.candidatePlatforms.map((id) => platformCatalog.find((item) => item.id === id)?.name ?? id);

  function open(tab: WorkspaceTab) {
    setSelectedProjectId(workspace.project.id);
    setWorkspaceView("project");
    setActiveTab(tab);
  }

  return (
    <section className={`cursor-pointer rounded-md border bg-white p-4 shadow-sm transition ${selected ? "border-cyan-400 ring-1 ring-cyan-200" : "border-slate-200 hover:border-slate-300 hover:shadow"}`} onClick={() => setSelectedProjectId(workspace.project.id)}>
      <div className={`grid gap-4 ${selected ? "xl:grid-cols-[minmax(0,1fr)_320px]" : ""}`}>
        <div>
          <div className="flex flex-wrap items-start justify-between gap-3">
            <div className="min-w-0 flex-1">
              <p className="text-xs font-semibold uppercase tracking-wide text-slate-500">{workspace.project.industry || labels.byType}</p>
              <h3 className="mt-1 text-lg font-semibold">{workspace.project.name}</h3>
              <p className="mt-3 text-xs font-semibold uppercase tracking-wide text-slate-500">{labels.projectGoalSummary}</p>
              <p className="mt-2 max-w-4xl text-sm leading-6 text-slate-700">{workspace.project.goal || nextStepFor(workspace, language)}</p>
              <div className="mt-4 grid gap-3 text-sm text-slate-600 md:grid-cols-2">
                <p><span className="font-semibold text-slate-800">{labels.lastUpdated}: </span>{workspace.project.updatedAt}</p>
                <p><span className="font-semibold text-slate-800">{labels.keyInputCompleteness}: </span>{keyInputs.percent}% ({keyInputs.done}/{keyInputs.total})</p>
                <p><span className="font-semibold text-slate-800">{labels.candidatePlatforms}: </span>{candidatePlatformNames.join(", ") || "-"}</p>
                <p><span className="font-semibold text-slate-800">{labels.topRecommendation}: </span>{topPlatform?.name ?? "-"}</p>
                {workspace.attachments.length > 0 ? (
                  <p className="md:col-span-2">
                    <span className="font-semibold text-slate-800">{labels.registeredMaterials}: </span>
                    {workspace.attachments.length}
                    {" "}
                    <span className="ml-2 text-xs font-semibold text-slate-500">({labels.attachmentReadLimit})</span>
                  </p>
                ) : null}
                <p className="md:col-span-2"><span className="font-semibold text-slate-800">{labels.recommendedNextAction}: </span>{localize(readiness.nextAction, language)}</p>
                {isLocal ? <p className="text-xs text-amber-700 md:col-span-2">{labels.localReadiness}</p> : null}
              </div>
            </div>
            <div className="flex flex-col items-start gap-2 sm:items-end">
              <span className="text-xs font-semibold uppercase tracking-wide text-slate-500">{labels.status}</span>
              <StatusBadge status={readiness.status} />
              <span className="rounded-full bg-cyan-50 px-2.5 py-1 text-xs font-semibold text-cyan-800">{labels.readiness} {readiness.score}%</span>
            </div>
          </div>
          {selected ? (
            <div className="mt-4 flex flex-wrap gap-2">
              <button className="rounded-md bg-cyan-700 px-3 py-2 text-sm font-semibold text-white hover:bg-cyan-800" onClick={() => open("overview")}>
                {labels.openProject}
              </button>
              <button className="rounded-md bg-slate-100 px-3 py-2 text-sm font-semibold text-slate-700 hover:bg-slate-200" onClick={() => open("benchmark")}>
                Benchmark
              </button>
              <button className="rounded-md bg-slate-100 px-3 py-2 text-sm font-semibold text-slate-700 hover:bg-slate-200" onClick={() => open("report")}>
                Report
              </button>
              <button
                className="inline-flex items-center gap-2 rounded-md bg-red-50 px-3 py-2 text-sm font-semibold text-red-700 ring-1 ring-red-100 hover:bg-red-100"
                onClick={(event) => {
                  event.stopPropagation();
                  deleteProject(workspace.project.id);
                }}
              >
                <Trash2 size={15} />
                {labels.deleteProject}
              </button>
            </div>
          ) : null}
        </div>
        {selected ? (
          <div className="grid gap-3">
            <MetricBar label={labels.readiness} value={readiness.score} tone="cyan" />
            <MetricBar label={labels.finalScore} value={topResult?.weightedScore ?? 0} tone="emerald" />
            <Info title={labels.topRecommendation} value={topPlatform?.name ?? "-"} />
          </div>
        ) : null}
      </div>
    </section>
  );
}

function ProjectOverview({
  workspace,
  topPlatform,
  topResult,
  language,
  labels,
  platformCatalog,
  setActiveTab,
}: {
  workspace: ProjectWorkspace;
  topPlatform: PlcEcosystem;
  topResult?: BenchmarkResult;
  language: Language;
  labels: (typeof copy)[Language];
  platformCatalog: PlcEcosystem[];
  setActiveTab: (tab: WorkspaceTab) => void;
}) {
  const { readiness, isLocal } = getWorkspaceReadiness(workspace);
  const keyInputs = calculateKeyInputCompleteness(workspace);
  const candidatePlatformNames = workspace.intake.candidatePlatforms.map((id) => platformCatalog.find((item) => item.id === id)?.name ?? id);
  return (
    <div className="grid gap-5 xl:grid-cols-[minmax(0,1fr)_360px]">
      <Panel title={labels.lifecycleStatus} description={workspace.project.name}>
        <div className="mb-5 rounded-md border border-slate-200 bg-white p-4">
          <p className="text-xs font-semibold uppercase tracking-wide text-slate-500">{labels.projectGoalSummary}</p>
          <p className="mt-2 text-sm leading-6 text-slate-700">{workspace.project.goal || "-"}</p>
          <div className="mt-4 grid gap-3 text-sm text-slate-600 lg:grid-cols-2">
            <p><span className="font-semibold text-slate-800">{labels.industry}: </span>{workspace.project.industry || "-"}</p>
            <p><span className="font-semibold text-slate-800">{labels.keyInputCompleteness}: </span>{keyInputs.percent}% ({keyInputs.done}/{keyInputs.total})</p>
            <p className="lg:col-span-2"><span className="font-semibold text-slate-800">{labels.candidatePlatforms}: </span>{candidatePlatformNames.join(", ") || "-"}</p>
            {workspace.attachments.length > 0 ? (
              <p className="lg:col-span-2">
                <span className="font-semibold text-slate-800">{labels.registeredMaterials}: </span>
                {workspace.attachments.length}
                {" "}
                <span className="ml-2 text-xs font-semibold text-slate-500">({labels.attachmentReadLimit})</span>
              </p>
            ) : null}
          </div>
        </div>
        <div className="grid gap-4 md:grid-cols-3">
          <div className="rounded-md bg-slate-50 p-4">
            <p className="text-sm font-semibold">{labels.status}</p>
            <div className="mt-2"><StatusBadge status={readiness.status} /></div>
          </div>
          <Info title={labels.lastUpdated} value={workspace.project.updatedAt} />
          <ScoreDial label={labels.readiness} value={readiness.score} />
        </div>
        {isLocal ? <p className="mt-3 text-sm font-semibold text-amber-700">{labels.localReadiness}</p> : null}
        <div className="mt-5 grid gap-4 lg:grid-cols-2">
          <ReadinessList title={labels.reasons} items={readiness.reasons} language={language} empty="-" />
          <ReadinessList title={labels.missingRequired} items={readiness.missingRequired} language={language} empty="-" />
          <ReadinessList title={labels.recommendedInputs} items={readiness.recommendedMissing} language={language} empty="-" />
          <div className="rounded-md bg-cyan-50 p-4">
            <p className="text-sm font-semibold text-cyan-900">{labels.nextStep}</p>
            <p className="mt-2 text-sm leading-6 text-cyan-950">{localize(readiness.nextAction, language)}</p>
            <p className="mt-3 text-xs font-semibold uppercase tracking-wide text-cyan-800">{labels.confidence}: {readiness.confidenceLevel}</p>
          </div>
        </div>
        <div className="mt-5 rounded-md border border-cyan-100 bg-cyan-50 p-4">
          <p className="text-sm font-semibold text-cyan-900">{labels.recommendedNextAction}</p>
          <p className="mt-2 text-sm leading-6 text-cyan-950">{localize(readiness.nextAction, language)}</p>
          <div className="mt-4 flex flex-wrap gap-2">
            <button className="rounded-md bg-cyan-700 px-3 py-2 text-sm font-semibold text-white hover:bg-cyan-800" onClick={() => setActiveTab("intake")}>
              Intake
            </button>
            <button className="rounded-md bg-white px-3 py-2 text-sm font-semibold text-cyan-800 ring-1 ring-cyan-200 hover:bg-cyan-50" onClick={() => setActiveTab("benchmark")}>
              Benchmark
            </button>
          </div>
        </div>
      </Panel>
      <Panel title={labels.topRecommendation} description={topPlatform.name}>
        <p className="mb-4 text-sm leading-6 text-slate-600">{labels.recommendedNextAction}: {localize(readiness.nextAction, language)}</p>
        <MetricBar label={labels.technicalScore} value={topResult?.technicalScore ?? 0} tone="slate" />
        <MetricBar label={labels.preferenceScore} value={topResult?.preferenceScore ?? 0} tone="cyan" />
        <MetricBar label={labels.finalScore} value={topResult?.weightedScore ?? 0} tone="emerald" />
      </Panel>
    </div>
  );
}

function Intake({ workspace, updateWorkspace, platformCatalog, labels, language }: { workspace: ProjectWorkspace; updateWorkspace: (workspace: ProjectWorkspace) => void | Promise<void>; platformCatalog: PlcEcosystem[]; labels: (typeof copy)[Language]; language: Language }) {
  const [draft, setDraft] = useState(workspace);
  const { readiness, isLocal } = getWorkspaceReadiness(workspace);

  useEffect(() => {
    setDraft(workspace);
  }, [workspace]);

  const required = [
    { label: language === "zh" ? "项目名称" : "Project name", ok: Boolean(draft.project.name.trim()) },
    { label: language === "zh" ? "行业" : "Industry", ok: Boolean(draft.project.industry.trim()) },
    { label: language === "zh" ? "项目目标" : "Project goal", ok: Boolean(draft.project.goal.trim()) },
    { label: "I/O", ok: draft.intake.ioScale > 0 },
    { label: language === "zh" ? "候选平台" : "Candidates", ok: draft.intake.candidatePlatforms.length >= 2 },
  ];
  const optional = [
    { label: language === "zh" ? "团队经验" : "Team experience", ok: Boolean(draft.intake.teamExperience.trim()) },
    { label: language === "zh" ? "约束条件" : "Constraints", ok: Boolean(draft.intake.constraints.trim()) },
    { label: language === "zh" ? "现有平台" : "Existing platform", ok: Boolean(draft.intake.existingPlatform) },
  ];
  const completion = Math.round((required.filter((item) => item.ok).length / required.length) * 100);

  function toggleCandidate(platformId: string) {
    const exists = draft.intake.candidatePlatforms.includes(platformId);
    const candidatePlatforms = exists ? draft.intake.candidatePlatforms.filter((id) => id !== platformId) : [...draft.intake.candidatePlatforms, platformId];
    setDraft({ ...draft, intake: { ...draft.intake, candidatePlatforms } });
  }

  return (
    <div className="grid gap-5 xl:grid-cols-[minmax(0,1fr)_320px]">
      <Panel title={labels.intake} description={language === "zh" ? "像咨询访谈一样收集足够的决策输入。" : "Capture enough decision inputs like a consulting intake."}>
        <div className="grid gap-5">
          <section>
            <SectionTitle title={language === "zh" ? "1. 项目画像" : "1. Project profile"} />
            <div className="mt-3 grid gap-4 lg:grid-cols-2">
              <Field label={language === "zh" ? "项目名称" : "Project Name"} badge={labels.required} value={draft.project.name} onChange={(value) => setDraft({ ...draft, project: { ...draft.project, name: value } })} />
              <Field label={language === "zh" ? "行业" : "Industry"} badge={labels.required} value={draft.project.industry} onChange={(value) => setDraft({ ...draft, project: { ...draft.project, industry: value } })} />
              <Field label={language === "zh" ? "项目目标" : "Goal"} badge={labels.required} value={draft.project.goal} onChange={(value) => setDraft({ ...draft, project: { ...draft.project, goal: value } })} wide />
            </div>
          </section>

          <section>
            <SectionTitle title={language === "zh" ? "2. 工程规模与约束" : "2. Engineering scale and constraints"} />
            <div className="mt-3 grid gap-4 lg:grid-cols-2">
              <Select label={language === "zh" ? "项目规模" : "Project Size"} value={draft.intake.projectSize} options={["Small", "Medium", "Large"]} onChange={(value) => setDraft({ ...draft, intake: { ...draft.intake, projectSize: value as ProjectWorkspace["intake"]["projectSize"] } })} />
              <NumberField label="I/O Scale" badge={labels.required} value={draft.intake.ioScale} onChange={(value) => setDraft({ ...draft, intake: { ...draft.intake, ioScale: value } })} />
              <Range label={language === "zh" ? "运动控制要求" : "Motion Requirement"} value={draft.intake.motionRequirement} onChange={(value) => setDraft({ ...draft, intake: { ...draft.intake, motionRequirement: value } })} />
              <Range label={language === "zh" ? "安全要求" : "Safety Requirement"} value={draft.intake.safetyRequirement} onChange={(value) => setDraft({ ...draft, intake: { ...draft.intake, safetyRequirement: value } })} />
              <Range label={language === "zh" ? "预算敏感度" : "Budget Sensitivity"} value={draft.intake.budgetSensitivity} onChange={(value) => setDraft({ ...draft, intake: { ...draft.intake, budgetSensitivity: value } })} />
              <Select label={language === "zh" ? "现有平台" : "Existing Platform"} value={draft.intake.existingPlatform} options={platformCatalog.map((item) => item.id)} optionLabel={(id) => platformCatalog.find((item) => item.id === id)?.name ?? id} onChange={(value) => setDraft({ ...draft, intake: { ...draft.intake, existingPlatform: value } })} />
              <Field label={language === "zh" ? "团队经验" : "Team Experience"} badge={labels.optional} value={draft.intake.teamExperience} onChange={(value) => setDraft({ ...draft, intake: { ...draft.intake, teamExperience: value } })} wide />
              <Field label={language === "zh" ? "硬约束" : "Constraints"} badge={labels.optional} value={draft.intake.constraints} onChange={(value) => setDraft({ ...draft, intake: { ...draft.intake, constraints: value } })} wide />
            </div>
          </section>

          <section>
            <SectionTitle title={language === "zh" ? "3. 候选平台" : "3. Candidate platforms"} />
            <div className="mt-3 grid gap-3 md:grid-cols-2 xl:grid-cols-3">
              {platformCatalog.map((platform) => {
                const selected = draft.intake.candidatePlatforms.includes(platform.id);
                return (
                  <button key={platform.id} className={`rounded-md border p-3 text-left ${selected ? "border-cyan-500 bg-cyan-50" : "border-slate-200 bg-white hover:bg-slate-50"}`} onClick={() => toggleCandidate(platform.id)}>
                    <div className="flex items-start justify-between gap-3">
                      <div>
                        <p className="text-sm font-semibold">{platform.name}</p>
                        <p className="mt-1 text-xs text-slate-500">{platform.vendor}</p>
                      </div>
                      {selected ? <CheckCircle2 className="text-cyan-700" size={18} /> : null}
                    </div>
                  </button>
                );
              })}
            </div>
          </section>
        </div>
        <button className="mt-5 inline-flex items-center gap-2 rounded-md bg-cyan-700 px-4 py-2 text-sm font-semibold text-white hover:bg-cyan-800" onClick={() => updateWorkspace({ ...draft, project: { ...draft.project, updatedAt: today } })}>
          <Save size={16} />
          {labels.save}
        </button>
      </Panel>

      <Panel title={labels.validation} description={`${completion}%`}>
        <p className="mb-4 rounded-md bg-cyan-50 p-3 text-sm font-medium text-cyan-900">{labels.statusWillUpdate}</p>
        {isLocal ? <p className="mb-4 rounded-md bg-amber-50 p-3 text-sm font-medium text-amber-800">{labels.localReadiness}</p> : null}
        <ReadinessList title={labels.missingRequired} items={readiness.missingRequired} language={language} empty="-" />
        <div className="mt-4">
          <ReadinessList title={labels.recommendedInputs} items={readiness.recommendedMissing} language={language} empty="-" />
        </div>
        <div className="mt-5 border-t border-slate-200 pt-5">
        <ValidationList title={labels.required} items={required} labels={labels} />
        <div className="mt-5">
          <ValidationList title={labels.optional} items={optional} labels={labels} />
        </div>
        </div>
      </Panel>
    </div>
  );
}

function Preferences({
  workspace,
  updateWorkspace,
  savePreferences,
  platformCatalog,
  labels,
  language,
}: {
  workspace: ProjectWorkspace;
  updateWorkspace: (workspace: ProjectWorkspace) => void;
  savePreferences: (workspace: ProjectWorkspace) => void | Promise<void>;
  platformCatalog: PlcEcosystem[];
  labels: (typeof copy)[Language];
  language: Language;
}) {
  const reasonOptions = language === "zh" ? ["以前用过", "客户指定", "团队熟悉", "供应链稳定", "成本原因"] : ["Used before", "Customer mandated", "Team familiarity", "Supply stability", "Cost reason"];

  function updatePreference(platformId: string, patch: { preferenceWeight?: number; userReasonNote?: string }) {
    updateWorkspace({
      ...workspace,
      project: { ...workspace.project, updatedAt: today },
      preferences: workspace.preferences.map((item) => (item.platformId === platformId ? { ...item, ...patch } : item)),
    });
  }

  return (
    <Panel title={labels.preferences} description={language === "zh" ? "技术评分保持独立；用户倾向只影响加权结果。" : "Technical scores stay independent; user preference changes only the weighted result."}>
      <div className="grid gap-4">
        {workspace.preferences.map((pref) => {
          const platform = platformCatalog.find((item) => item.id === pref.platformId) ?? platformCatalog[0] ?? fallbackEcosystems[0];
          const technical = averageScore(platform);
          const impact = Math.round(pref.preferenceWeight * 0.28);
          const selected = workspace.intake.candidatePlatforms.includes(pref.platformId);
          return (
            <div key={pref.platformId} className={`rounded-md border p-4 ${selected ? "border-cyan-200 bg-white" : "border-slate-200 bg-slate-50 opacity-75"}`}>
              <div className="flex flex-wrap items-start justify-between gap-3">
                <div>
                  <h3 className="font-semibold">{platform.name}</h3>
                  <p className="mt-1 text-xs text-slate-500">{selected ? labels.candidatePlatforms : language === "zh" ? "未纳入当前候选集" : "Not in current candidate set"}</p>
                </div>
                <div className="grid grid-cols-3 gap-2 text-center text-xs">
                  <MiniScore label={labels.technicalScore} value={technical} />
                  <MiniScore label={labels.preferenceScore} value={pref.preferenceWeight} />
                  <MiniScore label={labels.weightedImpact} value={impact} />
                </div>
              </div>
              <div className="mt-4">
                <Range label={labels.preferenceScore} value={pref.preferenceWeight} onChange={(value) => updatePreference(pref.platformId, { preferenceWeight: value })} />
              </div>
              <div className="mt-3 flex flex-wrap gap-2">
                {reasonOptions.map((reason) => (
                  <button key={reason} className="rounded-full bg-slate-100 px-3 py-1.5 text-xs font-semibold text-slate-700 hover:bg-cyan-50 hover:text-cyan-800" onClick={() => updatePreference(pref.platformId, { userReasonNote: pref.userReasonNote ? `${pref.userReasonNote}; ${reason}` : reason })}>
                    <Plus size={12} className="inline" /> {reason}
                  </button>
                ))}
              </div>
              <input className="mt-3 w-full rounded-md border border-slate-300 px-3 py-2 text-sm" placeholder={labels.reasonPlaceholder} value={pref.userReasonNote} onChange={(event) => updatePreference(pref.platformId, { userReasonNote: event.target.value })} />
            </div>
          );
        })}
      </div>
      <button className="mt-5 inline-flex items-center gap-2 rounded-md bg-cyan-700 px-4 py-2 text-sm font-semibold text-white hover:bg-cyan-800" onClick={() => savePreferences(workspace)}>
        <Save size={16} />
        {labels.savePreferences}
      </button>
    </Panel>
  );
}

function useIntelligenceAction<T>() {
  const [result, setResult] = useState<T | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(false);
  const lastAction = useRef<(() => Promise<T>) | null>(null);
  const busy = useRef(false);

  async function run(action: () => Promise<T>) {
    if (busy.current) return undefined;
    busy.current = true;
    lastAction.current = action;
    setLoading(true);
    setError(false);
    try {
      const next = await action();
      setResult(next);
      return next;
    } catch (actionError) {
      console.warn("Project intelligence action failed.", actionError);
      setError(true);
      return undefined;
    } finally {
      busy.current = false;
      setLoading(false);
    }
  }

  function retry() {
    if (lastAction.current) void run(lastAction.current);
  }

  function reset() {
    setResult(null);
    setError(false);
    lastAction.current = null;
  }

  return { result, setResult, loading, error, run, retry, reset };
}

function analysisStatusPresentation(status: IntelligenceResult["executionStatus"], labels: (typeof copy)[Language]) {
  if (status === "ai_success") return { label: labels.aiAnalysis, lightClass: "bg-cyan-100 text-cyan-900", darkClass: "bg-cyan-300 text-slate-950" };
  if (status === "ai_fallback") return { label: labels.fallback, lightClass: "bg-amber-100 text-amber-900", darkClass: "bg-amber-300 text-amber-950" };
  return { label: labels.deterministic, lightClass: "bg-slate-200 text-slate-800", darkClass: "bg-slate-200 text-slate-800" };
}

function IntelligenceModeBadge({ result, labels }: { result: Pick<IntelligenceResult, "executionStatus" | "qualityProfile">; labels: (typeof copy)[Language] }) {
  const presentation = analysisStatusPresentation(result.executionStatus, labels);
  const qualityLabel = result.qualityProfile === "fast" ? labels.fastQuality : result.qualityProfile === "balanced" ? labels.balancedQuality : labels.qualityQuality;
  return (
    <div className="flex flex-wrap items-center gap-2">
      <span className={`rounded-full px-2.5 py-1 text-xs font-semibold ${presentation.lightClass}`}>{presentation.label}</span>
      <span className="rounded-full bg-slate-100 px-2.5 py-1 text-xs font-semibold text-slate-600">{labels.qualityProfile}: {qualityLabel}</span>
    </div>
  );
}

function IntelligenceResultPanel({ result, labels, language }: { result: IntelligenceResult; labels: (typeof copy)[Language]; language: Language }) {
  return (
    <div className="rounded-md border border-cyan-200 bg-cyan-50/60 p-4">
      <IntelligenceModeBadge result={result} labels={labels} />
      {result.executionStatus === "ai_fallback" ? <p className="mt-3 rounded-md border border-amber-200 bg-amber-50 px-3 py-2 text-sm text-amber-900">{labels.fallbackHint}</p> : null}
      <p className="mt-4 whitespace-pre-wrap text-sm leading-7 text-slate-800">{localize(result.answer, language)}</p>
      {!result.documentParsingUsed ? <p className="mt-4 rounded-md bg-white px-3 py-2 text-xs font-semibold text-slate-600 ring-1 ring-slate-200">{labels.attachmentsNotParsed}</p> : null}
      <div className="mt-4 grid gap-3 lg:grid-cols-2">
        <LightEvidenceList title={labels.missingInputsQuery} items={result.missingInputs.map((item) => localize(item, language))} />
        <LightEvidenceList title={labels.followUpQuestions} items={result.followUpQuestions.map((item) => localize(item, language))} />
        <LightEvidenceList title={labels.assumptions} items={result.assumptions.map((item) => localize(item, language))} />
        <LightEvidenceList title={labels.uncertainty} items={result.uncertainty.map((item) => localize(item, language))} />
      </div>
    </div>
  );
}

function LightEvidenceList({ title, items }: { title: string; items: string[] }) {
  return (
    <div className="rounded-md bg-white p-3 ring-1 ring-slate-200">
      <p className="text-xs font-semibold uppercase tracking-wide text-slate-500">{title}</p>
      {items.length ? <ul className="mt-2 list-disc space-y-1 pl-4 text-sm leading-6 text-slate-600">{items.map((item) => <li key={item}>{item}</li>)}</ul> : <p className="mt-2 text-sm text-slate-400">-</p>}
    </div>
  );
}

function ActionError({ labels, retry, useBasicAnalysis, disabled }: { labels: (typeof copy)[Language]; retry: () => void; useBasicAnalysis: () => void; disabled: boolean }) {
  return (
    <div className="rounded-md border border-rose-200 bg-rose-50 p-3 text-sm text-rose-800">
      <span>{labels.actionFailed}</span>
      <div className="mt-3 flex flex-wrap gap-2">
        <button className="rounded-md bg-white px-3 py-1.5 font-semibold ring-1 ring-rose-200 hover:bg-rose-100 disabled:opacity-50" onClick={retry} disabled={disabled}>{labels.retry}</button>
        <button className="rounded-md bg-slate-950 px-3 py-1.5 font-semibold text-white hover:bg-slate-800 disabled:opacity-50" onClick={useBasicAnalysis} disabled={disabled}>{labels.useBasicAnalysis}</button>
      </div>
    </div>
  );
}

function Attachments({ workspace, registerAttachment, labels, language, useAi }: { workspace: ProjectWorkspace; registerAttachment: (projectId: string, attachment: Pick<ProjectAttachment, "fileName" | "fileType" | "declaredPurpose">, fallbackWorkspace: ProjectWorkspace) => void | Promise<void>; labels: (typeof copy)[Language]; language: Language; useAi: boolean }) {
  const [form, setForm] = useState({ fileName: "", fileType: "Requirements" as ProjectAttachment["fileType"], declaredPurpose: "" });
  const analysis = useIntelligenceAction<IntelligenceResult>();

  function addAttachment() {
    if (!form.fileName.trim()) return;
    const next: ProjectAttachment = {
      id: `att-${Date.now()}`,
      projectId: workspace.project.id,
      fileName: form.fileName.trim(),
      fileType: form.fileType,
      declaredPurpose: form.declaredPurpose.trim() || (language === "zh" ? "仅使用文件名称、类型和声明用途，尚未读取文件内容。" : "Only the file name, type, and declared purpose are used; file contents have not been read."),
      uploadedAt: today,
    };
    registerAttachment(
      workspace.project.id,
      { fileName: next.fileName, fileType: next.fileType, declaredPurpose: next.declaredPurpose },
      { ...workspace, project: { ...workspace.project, updatedAt: today }, attachments: [...workspace.attachments, next] },
    );
    setForm({ fileName: "", fileType: "Requirements", declaredPurpose: "" });
  }

  return (
    <div className="grid gap-5 xl:grid-cols-[340px_minmax(0,1fr)]">
      <Panel title={labels.addAttachment} description={labels.fileNote}>
        <div className="grid gap-3">
          <Field label={labels.fileName} badge={labels.required} value={form.fileName} onChange={(value) => setForm({ ...form, fileName: value })} />
          <Select label={labels.fileType} value={form.fileType} options={attachmentTypes} onChange={(value) => setForm({ ...form, fileType: value as ProjectAttachment["fileType"] })} />
          <Field label={labels.attachmentPurpose} badge={labels.optional} value={form.declaredPurpose} onChange={(value) => setForm({ ...form, declaredPurpose: value })} />
          <button className="inline-flex items-center justify-center gap-2 rounded-md bg-slate-950 px-4 py-2 text-sm font-semibold text-white hover:bg-slate-800" onClick={addAttachment}>
            <Paperclip size={16} />
            {labels.addAttachment}
          </button>
        </div>
      </Panel>
      <Panel title={labels.attachments} description={`${workspace.attachments.length} ${language === "zh" ? "个已登记附件" : "registered attachments"}`}>
        {workspace.attachments.length === 0 ? (
          <div className="rounded-md border border-dashed border-slate-300 bg-slate-50 p-8 text-center">
            <Paperclip className="mx-auto text-slate-400" size={28} />
            <p className="mt-3 text-sm font-semibold text-slate-700">{labels.emptyAttachments}</p>
          </div>
        ) : (
          <div className="grid gap-3 md:grid-cols-2">
            {workspace.attachments.map((attachment) => (
              <div key={attachment.id} className="rounded-md border border-slate-200 bg-white p-4">
                <div className="flex flex-wrap items-center justify-between gap-3">
                  <h3 className="font-semibold">{attachment.fileName}</h3>
                  <span className="rounded-full bg-cyan-50 px-2 py-1 text-xs font-semibold text-cyan-800">{labels.registeredOnly}</span>
                </div>
                <div className="mt-3 grid gap-2 text-sm text-slate-600">
                  <p>
                    <span className="font-semibold text-slate-800">{labels.fileType}: </span>
                    {attachment.fileType}
                  </p>
                  <p>
                    <span className="font-semibold text-slate-800">{labels.attachmentPurpose}: </span>
                    {attachment.declaredPurpose}
                  </p>
                  <p className="text-xs text-slate-400">{attachment.uploadedAt}</p>
                </div>
              </div>
            ))}
          </div>
        )}
      </Panel>
      <div className="xl:col-span-2">
        <Panel title={labels.analysisResult} description={`${labels.intelligenceUsesProjectSwitch}: ${useAi ? labels.aiEnabled : labels.aiDisabled}`}>
          <div className="flex flex-wrap items-center gap-3">
            <button className="inline-flex items-center gap-2 rounded-md bg-cyan-700 px-4 py-2 text-sm font-semibold text-white hover:bg-cyan-800 disabled:cursor-not-allowed disabled:opacity-50" onClick={() => void analysis.run(() => analyzeProjectIntelligence(workspace.project.id, { language, quality: "balanced", useAi }))} disabled={analysis.loading}>
              <Sparkles size={16} />
              {analysis.loading ? labels.queryLoading : labels.analyzeRegisteredInfo}
            </button>
            <p className="text-xs font-semibold text-slate-500">{labels.attachmentsNotParsed}</p>
          </div>
          {analysis.error ? <div className="mt-4"><ActionError labels={labels} retry={analysis.retry} useBasicAnalysis={() => void analysis.run(() => analyzeProjectIntelligence(workspace.project.id, { language, quality: "balanced", useAi: false }))} disabled={analysis.loading} /></div> : null}
          {analysis.result ? <div className="mt-4"><IntelligenceResultPanel result={analysis.result} labels={labels} language={language} /></div> : null}
        </Panel>
      </div>
    </div>
  );
}

function Benchmark({ results, workspace, platformCatalog, labels, language, onRunBenchmark, useAi }: { results: BenchmarkResult[]; workspace: ProjectWorkspace; platformCatalog: PlcEcosystem[]; labels: (typeof copy)[Language]; language: Language; onRunBenchmark: (projectId: string) => void | Promise<void>; useAi: boolean }) {
  const explanation = useIntelligenceAction<IntelligenceResult>();
  return (
    <div className="space-y-5">
      <Panel title={labels.benchmark} description={language === "zh" ? "咨询 dashboard：技术分 + 用户倾向 = 最终排序。" : "Consulting dashboard: technical score + user preference = final ranking."}>
      <div className="mb-4 flex flex-wrap gap-3">
        <button className="inline-flex items-center gap-2 rounded-md bg-cyan-700 px-4 py-2 text-sm font-semibold text-white hover:bg-cyan-800" onClick={() => onRunBenchmark(workspace.project.id)}>
          <RefreshCw size={16} />
          {language === "zh" ? "运行 Benchmark" : "Run Benchmark"}
        </button>
        <button className="inline-flex items-center gap-2 rounded-md bg-slate-950 px-4 py-2 text-sm font-semibold text-white hover:bg-slate-800 disabled:cursor-not-allowed disabled:opacity-50" onClick={() => void explanation.run(() => explainProjectBenchmark(workspace.project.id, { language, quality: "balanced", useAi }))} disabled={explanation.loading || results.length === 0}>
          <Sparkles size={16} />
          {explanation.loading ? labels.queryLoading : labels.explainRanking}
        </button>
      </div>
      <div className="grid gap-4">
        {results.map((result, index) => {
          const platform = platformCatalog.find((item) => item.id === result.platformId) ?? platformCatalog[0] ?? fallbackEcosystems[0];
          const preference = workspace.preferences.find((item) => item.platformId === result.platformId);
          return (
            <div key={result.platformId} className={`rounded-md border p-4 ${index === 0 ? "border-cyan-400 bg-cyan-50/70 shadow-sm" : "border-slate-200 bg-white"}`}>
              <div className="flex flex-wrap items-start justify-between gap-3">
                <div>
                  <p className="text-sm font-semibold text-slate-500">#{index + 1} {index === 0 ? ` · ${labels.topRecommendation}` : ""}</p>
                  <h3 className="mt-1 text-xl font-semibold">{platform.name}</h3>
                  <p className="mt-1 max-w-3xl text-sm leading-6 text-slate-600">{localize(result.rationale, language)}</p>
                </div>
                <span className={`rounded-full px-2.5 py-1 text-xs font-semibold ring-1 ${riskClass[result.riskLevel]}`}>
                  {labels.risk}: {riskLabel[language][result.riskLevel]}
                </span>
              </div>
              <div className="mt-4 grid gap-3 md:grid-cols-3">
                <MetricBar label={labels.technicalScore} value={result.technicalScore} tone="slate" />
                <MetricBar label={labels.preferenceScore} value={result.preferenceScore} tone="cyan" />
                <MetricBar label={labels.finalScore} value={result.weightedScore} tone="emerald" />
              </div>
              <div className="mt-4 grid gap-3 lg:grid-cols-2">
                <div className="rounded-md bg-white/80 p-3 ring-1 ring-slate-200">
                  <p className="text-xs font-semibold uppercase tracking-wide text-slate-500">{labels.assumptions}</p>
                  <ul className="mt-2 space-y-1 text-sm text-slate-600">
                    {result.assumptions.map((item) => (
                      <li key={localize(item, language)}>{localize(item, language)}</li>
                    ))}
                  </ul>
                </div>
                <div className="rounded-md bg-white/80 p-3 ring-1 ring-slate-200">
                  <p className="text-xs font-semibold uppercase tracking-wide text-slate-500">{labels.reason}</p>
                  <p className="mt-2 text-sm text-slate-600">{preference?.userReasonNote || (language === "zh" ? "尚未填写用户倾向原因。" : "No user preference reason entered yet.")}</p>
                </div>
              </div>
            </div>
          );
        })}
      </div>
      </Panel>
      <Panel title={labels.explainRanking} description={`${labels.intelligenceUsesProjectSwitch}: ${useAi ? labels.aiEnabled : labels.aiDisabled}`}>
        <div className="mb-4 flex items-start gap-2 text-sm text-slate-600">
          <p>{labels.benchmarkExplanation}</p>
          <span className="inline-flex shrink-0 cursor-help text-slate-400" title={labels.benchmarkScoreTooltip} aria-label={labels.benchmarkScoreTooltip} tabIndex={0}><InfoIcon size={16} /></span>
        </div>
        {explanation.error ? <ActionError labels={labels} retry={explanation.retry} useBasicAnalysis={() => void explanation.run(() => explainProjectBenchmark(workspace.project.id, { language, quality: "balanced", useAi: false }))} disabled={explanation.loading} /> : null}
        {explanation.result ? <IntelligenceResultPanel result={explanation.result} labels={labels} language={language} /> : <p className="rounded-md border border-dashed border-slate-300 p-5 text-sm text-slate-500">{labels.explainRanking}</p>}
      </Panel>
    </div>
  );
}

function ChatMessageCard({ message, labels, language }: { message: ChatMessage; labels: (typeof copy)[Language]; language: Language }) {
  if (message.role === "user") {
    return (
      <div className="rounded-md bg-white p-3 text-sm leading-6 text-slate-900">
        <p className="mb-1 text-xs font-semibold text-slate-500">You</p>
        {localize(message.content, language)}
      </div>
    );
  }

  if (!message.intelligence) {
    return <div className="rounded-md bg-cyan-400/10 p-3 text-sm leading-6 text-cyan-50">{localize(message.content, language)}</div>;
  }

  const result = message.intelligence;
  const presentation = analysisStatusPresentation(result.executionStatus, labels);
  const qualityLabel = result.qualityProfile === "fast" ? labels.fastQuality : result.qualityProfile === "balanced" ? labels.balancedQuality : labels.qualityQuality;
  const assumptions = result.assumptions.map((item) => localize(item, language));
  const uncertainty = result.uncertainty.map((item) => localize(item, language));
  const missingInputs = result.missingInputs.map((item) => localize(item, language));

  return (
    <div className="rounded-md border border-white/10 bg-cyan-400/10 p-3 text-sm leading-6 text-cyan-50">
      <div className="mb-2 flex flex-wrap items-center gap-2">
        <p className="mr-auto text-xs font-semibold text-cyan-100">Copilot</p>
        <span className={`rounded-full px-2 py-0.5 text-[11px] font-semibold ${presentation.darkClass}`}>{presentation.label}</span>
        <span className="rounded-full bg-white/10 px-2 py-0.5 text-[11px] font-semibold text-slate-200">{labels.qualityProfile}: {qualityLabel}</span>
      </div>
      <p>{localize(message.content, language)}</p>
      {result.executionStatus === "ai_fallback" ? <p className="mt-3 rounded-md bg-amber-300/15 px-2 py-1.5 text-xs text-amber-100">{labels.fallbackHint}</p> : null}
      {!result.documentParsingUsed ? <p className="mt-3 rounded-md bg-slate-950/40 px-2 py-1.5 text-xs text-slate-300">{labels.attachmentsNotParsed}</p> : null}
      <details className="mt-3 rounded-md border border-white/10 bg-slate-950/30 p-2">
        <summary className="cursor-pointer text-xs font-semibold text-cyan-100">{labels.responseContext}</summary>
        <div className="mt-3 space-y-3 text-xs leading-5 text-slate-300">
          <QueryContextList title={labels.assumptions} items={assumptions} />
          <QueryContextList title={labels.uncertainty} items={uncertainty} />
          {missingInputs.length ? <QueryContextList title={labels.missingInputsQuery} items={missingInputs} /> : null}
        </div>
      </details>
    </div>
  );
}

function QueryContextList({ title, items }: { title: string; items: string[] }) {
  return (
    <div>
      <p className="font-semibold text-slate-100">{title}</p>
      {items.length ? (
        <ul className="mt-1 list-disc space-y-1 pl-4">
          {items.map((item) => <li key={item}>{item}</li>)}
        </ul>
      ) : <p className="mt-1">-</p>}
    </div>
  );
}

function ReportBuilder({
  workspace,
  updateWorkspace,
  saveReportSection,
  updateLifecycleStatus,
  labels,
  language,
  activeSectionId,
  setActiveSectionId,
  benchmarkResults,
  platformCatalog,
  useAi,
}: {
  workspace: ProjectWorkspace;
  updateWorkspace: (workspace: ProjectWorkspace) => void;
  saveReportSection: (projectId: string, section: ReportSection, fallbackWorkspace: ProjectWorkspace) => ProjectWorkspace | Promise<ProjectWorkspace>;
  updateLifecycleStatus: (projectId: string, status: ProjectStatus) => void | Promise<void>;
  labels: (typeof copy)[Language];
  language: Language;
  activeSectionId: string;
  setActiveSectionId: (id: string) => void;
  benchmarkResults: BenchmarkResult[];
  platformCatalog: PlcEcosystem[];
  useAi: boolean;
}) {
  const section = workspace.report.sections.find((item) => item.id === activeSectionId) ?? workspace.report.sections[0];
  const { readiness } = getWorkspaceReadiness(workspace);
  const [reportMode, setReportMode] = useState<"edit" | "preview">("edit");
  const [markdownCopied, setMarkdownCopied] = useState(false);
  const [exportState, setExportState] = useState<"idle" | "ppt" | "failed">("idle");
  const [rewriteInstruction, setRewriteInstruction] = useState("");
  const [rewriteSectionId, setRewriteSectionId] = useState("");
  const [acceptingSuggestions, setAcceptingSuggestions] = useState(false);
  const reportDraft = useIntelligenceAction<ReportGenerationResult>();
  const rewrite = useIntelligenceAction<ReportSectionRewriteResult>();
  const markdown = useMemo(() => buildReportMarkdown(workspace, benchmarkResults, readiness, language, platformCatalog), [benchmarkResults, language, platformCatalog, readiness, workspace]);
  const deliveryScope = reportAnalysisScope(workspace, language);
  const deliveryDataSources = deliveryScope.references;
  const deliveryAssumptions = uniqueStrings([
    ...deliveryScope.basis,
    ...readiness.reasons.map((reason) => localize(reason, language)),
  ]);
  const deliveryUncertainty = deliveryScope.limits;

  async function copyMarkdown() {
    try {
      await navigator.clipboard.writeText(markdown);
    } catch {
      const textarea = document.createElement("textarea");
      textarea.value = markdown;
      textarea.setAttribute("readonly", "true");
      textarea.style.position = "fixed";
      textarea.style.left = "-9999px";
      document.body.appendChild(textarea);
      textarea.focus();
      textarea.select();
      document.execCommand("copy");
      document.body.removeChild(textarea);
    }
    setMarkdownCopied(true);
  }

  function downloadMarkdown() {
    const blob = new Blob([markdown], { type: "text/markdown;charset=utf-8" });
    const url = URL.createObjectURL(blob);
    const anchor = document.createElement("a");
    anchor.href = url;
    anchor.download = `${safeFileName(workspace.project.name)}.md`;
    anchor.click();
    URL.revokeObjectURL(url);
    setMarkdownCopied(false);
  }

  function printReportPdf() {
    const printWindow = window.open("", "_blank", "width=1100,height=820");
    if (!printWindow) {
      setExportState("failed");
      return;
    }
    printWindow.document.open();
    printWindow.document.write(buildReportPrintHtml(workspace, benchmarkResults, readiness, language, platformCatalog));
    printWindow.document.close();
    printWindow.focus();
    window.setTimeout(() => printWindow.print(), 300);
    setExportState("idle");
  }

  async function downloadPowerPoint() {
    setExportState("ppt");
    try {
      await exportReportPptx(workspace, benchmarkResults, readiness, language, platformCatalog);
      setExportState("idle");
    } catch (error) {
      console.error("PowerPoint export failed.", error);
      setExportState("failed");
    }
  }

  function updateSection(next: ReportSection) {
    updateWorkspace({
      ...workspace,
      project: { ...workspace.project, updatedAt: today },
      report: { ...workspace.report, sections: workspace.report.sections.map((item) => (item.id === next.id ? next : item)) },
    });
  }

  function applySectionToWorkspace(base: ProjectWorkspace, next: ReportSection): ProjectWorkspace {
    return {
      ...base,
      project: { ...base.project, updatedAt: today },
      report: { ...base.report, sections: base.report.sections.map((item) => (item.id === next.id ? next : item)) },
    };
  }

  function sectionFromSuggestion(base: ReportSection, body: LocalizedText, assumptions: LocalizedText[], uncertainty: LocalizedText[]) {
    return {
      ...base,
      body,
      assumptions: assumptions.length ? assumptions : base.assumptions,
      uncertainty: uncertainty[0] ?? base.uncertainty,
      lastGeneratedAt: today,
    };
  }

  async function acceptGeneratedSection(sectionId: string) {
    const suggestion = reportDraft.result?.sections.find((item) => item.sectionId === sectionId);
    const current = workspace.report.sections.find((item) => item.id === sectionId);
    if (!suggestion || !current || acceptingSuggestions) return;
    setAcceptingSuggestions(true);
    const next = sectionFromSuggestion(current, suggestion.draftBody, reportDraft.result?.assumptions ?? [], reportDraft.result?.uncertainty ?? []);
    await saveReportSection(workspace.project.id, next, applySectionToWorkspace(workspace, next));
    reportDraft.setResult((existing) => {
      if (!existing) return existing;
      const remaining = existing.sections.filter((item) => item.sectionId !== sectionId);
      return remaining.length ? { ...existing, sections: remaining } : null;
    });
    setAcceptingSuggestions(false);
  }

  async function acceptAllGeneratedSections() {
    if (!reportDraft.result || acceptingSuggestions) return;
    setAcceptingSuggestions(true);
    let rollingWorkspace = workspace;
    for (const suggestion of reportDraft.result.sections) {
      const current = rollingWorkspace.report.sections.find((item) => item.id === suggestion.sectionId);
      if (!current) continue;
      const next = sectionFromSuggestion(current, suggestion.draftBody, reportDraft.result.assumptions, reportDraft.result.uncertainty);
      const fallback = applySectionToWorkspace(rollingWorkspace, next);
      rollingWorkspace = await saveReportSection(workspace.project.id, next, fallback);
    }
    reportDraft.reset();
    setAcceptingSuggestions(false);
  }

  async function acceptRewriteSuggestion() {
    if (!section || !rewrite.result || rewriteSectionId !== section.id || acceptingSuggestions) return;
    setAcceptingSuggestions(true);
    const next = sectionFromSuggestion(section, rewrite.result.suggestedBody, rewrite.result.assumptions, rewrite.result.uncertainty);
    await saveReportSection(workspace.project.id, next, applySectionToWorkspace(workspace, next));
    rewrite.reset();
    setRewriteInstruction("");
    setAcceptingSuggestions(false);
  }

  function selectReportSection(sectionId: string) {
    setActiveSectionId(sectionId);
    setRewriteInstruction("");
    setRewriteSectionId("");
    rewrite.reset();
  }

  if (!section) {
    return <Panel title={labels.report} description={language === "zh" ? "暂无报告分区。" : "No report sections available yet."} />;
  }

  return (
    <div className="space-y-5">
      <Panel title={labels.reportSuggestions} description={`${labels.intelligenceUsesProjectSwitch}: ${useAi ? labels.aiEnabled : labels.aiDisabled}`}>
        <div className="flex flex-wrap items-center gap-3">
          <button className="inline-flex items-center gap-2 rounded-md bg-cyan-700 px-4 py-2 text-sm font-semibold text-white hover:bg-cyan-800 disabled:cursor-not-allowed disabled:opacity-50" onClick={() => void reportDraft.run(() => generateProjectReport(workspace.project.id, { language, audience: "executive", quality: "quality", useAi }))} disabled={reportDraft.loading || acceptingSuggestions}>
            <Sparkles size={16} />
            {reportDraft.loading ? labels.queryLoading : labels.generateReportDraft}
          </button>
          <p className="text-sm text-slate-600">{labels.suggestionsNotSaved}</p>
        </div>
        {reportDraft.error ? <div className="mt-4"><ActionError labels={labels} retry={reportDraft.retry} useBasicAnalysis={() => void reportDraft.run(() => generateProjectReport(workspace.project.id, { language, audience: "executive", quality: "quality", useAi: false }))} disabled={reportDraft.loading} /></div> : null}
        {reportDraft.result ? (
          <div className="mt-5 space-y-4">
            <div className="flex flex-wrap items-center justify-between gap-3">
              <IntelligenceModeBadge result={reportDraft.result} labels={labels} />
              <div className="flex flex-wrap gap-2">
                <button className="rounded-md bg-slate-950 px-3 py-2 text-sm font-semibold text-white hover:bg-slate-800 disabled:opacity-50" onClick={() => void acceptAllGeneratedSections()} disabled={acceptingSuggestions}>{labels.acceptAll}</button>
                <button className="rounded-md border border-slate-300 px-3 py-2 text-sm font-semibold text-slate-700 hover:bg-slate-50 disabled:opacity-50" onClick={reportDraft.reset} disabled={acceptingSuggestions}>{labels.discardSuggestions}</button>
              </div>
            </div>
            {reportDraft.result.executionStatus === "ai_fallback" ? <p className="rounded-md border border-amber-200 bg-amber-50 px-3 py-2 text-sm text-amber-900">{labels.fallbackHint}</p> : null}
            <p className="rounded-md bg-amber-50 px-3 py-2 text-xs font-semibold text-amber-900 ring-1 ring-amber-200">{labels.noPersistenceBeforeAccept}</p>
            <div className="grid gap-4 xl:grid-cols-2">
              {reportDraft.result.sections.map((suggestion) => {
                const current = workspace.report.sections.find((item) => item.id === suggestion.sectionId);
                return (
                  <div key={suggestion.sectionId} className="rounded-md border border-slate-200 bg-slate-50 p-4">
                    <h3 className="font-semibold text-slate-950">{localize(suggestion.title, language)}</h3>
                    <div className="mt-3 grid gap-3 lg:grid-cols-2">
                      <div className="rounded-md bg-white p-3 ring-1 ring-slate-200"><p className="text-xs font-semibold uppercase text-slate-500">{labels.currentContent}</p><p className="mt-2 line-clamp-6 whitespace-pre-wrap text-sm leading-6 text-slate-600">{current ? localize(current.body, language) : "-"}</p></div>
                      <div className="rounded-md bg-cyan-50 p-3 ring-1 ring-cyan-200"><p className="text-xs font-semibold uppercase text-cyan-800">{labels.suggestedContent}</p><p className="mt-2 line-clamp-6 whitespace-pre-wrap text-sm leading-6 text-slate-700">{localize(suggestion.draftBody, language)}</p></div>
                    </div>
                    <button className="mt-3 rounded-md bg-cyan-700 px-3 py-2 text-sm font-semibold text-white hover:bg-cyan-800 disabled:opacity-50" onClick={() => void acceptGeneratedSection(suggestion.sectionId)} disabled={acceptingSuggestions}>{labels.acceptSection}</button>
                  </div>
                );
              })}
            </div>
            <div className="grid gap-3 lg:grid-cols-3">
              <LightEvidenceList title={labels.assumptions} items={reportDraft.result.assumptions.map((item) => localize(item, language))} />
              <LightEvidenceList title={labels.uncertainty} items={reportDraft.result.uncertainty.map((item) => localize(item, language))} />
              <LightEvidenceList title={labels.missingInputsQuery} items={reportDraft.result.missingInputs.map((item) => localize(item, language))} />
            </div>
          </div>
        ) : null}
      </Panel>
      <div className="grid gap-5 xl:grid-cols-[260px_minmax(0,1fr)_300px]">
      <Panel title={labels.reportSections} description={`v${workspace.report.version} · ${workspace.report.status}`}>
        <div className="mb-4 rounded-md bg-slate-50 p-2">
          <p className="px-1 pb-2 text-xs font-semibold uppercase tracking-wide text-slate-500">{labels.reportMode}</p>
          <div className="grid grid-cols-2 gap-1">
            {(["edit", "preview"] as const).map((mode) => (
              <button key={mode} className={`rounded-md px-3 py-2 text-sm font-semibold ${reportMode === mode ? "bg-white text-cyan-800 shadow-sm ring-1 ring-cyan-200" : "text-slate-600 hover:bg-white/70"}`} onClick={() => setReportMode(mode)}>
                {mode === "edit" ? labels.edit : labels.preview}
              </button>
            ))}
          </div>
        </div>
        <div className="space-y-2">
          {workspace.report.sections.map((item, index) => (
            <button key={item.id} className={`w-full rounded-md px-3 py-2 text-left text-sm font-semibold ${item.id === section.id ? "bg-cyan-50 text-cyan-800 ring-1 ring-cyan-200" : "bg-slate-50 text-slate-700 hover:bg-slate-100"}`} onClick={() => selectReportSection(item.id)}>
              <span className="mr-2 text-xs text-slate-400">{String(index + 1).padStart(2, "0")}</span>
              {localize(item.title, language)}
            </button>
          ))}
        </div>
        <div className="mt-5 space-y-2 rounded-md border border-slate-200 bg-white p-3">
          <p className="text-xs font-semibold uppercase tracking-wide text-slate-500">{labels.exportPreparation}</p>
          <button className="inline-flex w-full items-center justify-center gap-2 rounded-md bg-slate-950 px-3 py-2 text-sm font-semibold text-white hover:bg-slate-800" onClick={() => void copyMarkdown()}>
            <CopyIcon size={15} />
            {labels.copyMarkdown}
          </button>
          <button className="inline-flex w-full items-center justify-center gap-2 rounded-md bg-cyan-700 px-3 py-2 text-sm font-semibold text-white hover:bg-cyan-800" onClick={downloadMarkdown}>
            <Download size={15} />
            {labels.downloadMarkdown}
          </button>
          <button className="inline-flex w-full items-center justify-center gap-2 rounded-md border border-slate-300 px-3 py-2 text-sm font-semibold text-slate-700 hover:bg-slate-50" onClick={printReportPdf}>
            <Printer size={15} />
            {labels.exportPdf}
          </button>
          <button className="inline-flex w-full items-center justify-center gap-2 rounded-md border border-cyan-300 bg-cyan-50 px-3 py-2 text-sm font-semibold text-cyan-900 hover:bg-cyan-100 disabled:cursor-wait disabled:opacity-60" onClick={() => void downloadPowerPoint()} disabled={exportState === "ppt"}>
            <Presentation size={15} />
            {exportState === "ppt" ? labels.exporting : labels.exportPpt}
          </button>
          {markdownCopied ? <p className="text-center text-xs font-semibold text-emerald-700">{labels.copied}</p> : null}
          {exportState === "failed" ? <p className="text-center text-xs font-semibold text-red-700">{labels.exportFailed}</p> : null}
        </div>
      </Panel>
      <Panel title={reportMode === "edit" ? labels.sectionEditor : labels.reportPreview} description={reportMode === "edit" ? localize(section.title, language) : reportStatusNotice(readiness.status, labels)}>
        <div className={`mb-4 rounded-md p-3 text-sm font-semibold ${readiness.status === "Draft" ? "bg-amber-50 text-amber-900 ring-1 ring-amber-200" : readiness.status === "Finalized" ? "bg-slate-900 text-white" : "bg-cyan-50 text-cyan-900 ring-1 ring-cyan-200"}`}>
          {reportStatusNotice(readiness.status, labels)}
        </div>
        <div className="mb-4 flex flex-wrap items-center gap-3 rounded-md bg-slate-50 p-3">
          <StatusBadge status={readiness.status} />
          <span className="text-sm font-semibold text-slate-700">{labels.readiness}: {readiness.score}%</span>
          <span className="text-sm font-semibold text-slate-700">{labels.confidence}: {readiness.confidenceLevel}</span>
          {readiness.status === "Finalized" ? <span className="rounded-full bg-slate-900 px-2.5 py-1 text-xs font-semibold text-white">{labels.finalizedReport}</span> : null}
          {readiness.status === "Report Ready" ? (
            <button className="rounded-md bg-slate-950 px-3 py-2 text-sm font-semibold text-white hover:bg-slate-800" onClick={() => updateLifecycleStatus(workspace.project.id, "Finalized")}>
              {labels.markFinalized}
            </button>
          ) : null}
          {readiness.status === "Finalized" ? (
            <button className="rounded-md bg-cyan-700 px-3 py-2 text-sm font-semibold text-white hover:bg-cyan-800" onClick={() => updateLifecycleStatus(workspace.project.id, "Analyzing")}>
              {labels.reopenAnalysis}
            </button>
          ) : null}
        </div>
        {reportMode === "edit" ? (
          <>
            <textarea className="min-h-[420px] w-full resize-y rounded-md border border-slate-300 bg-white p-5 text-sm leading-7 shadow-inner outline-none focus:ring-2 focus:ring-cyan-400" value={localize(section.body, language)} onChange={(event) => updateSection({ ...section, body: { ...section.body, [language]: event.target.value } })} />
            <div className="mt-4 flex flex-wrap items-center gap-3">
              <button className="inline-flex items-center gap-2 rounded-md bg-slate-950 px-4 py-2 text-sm font-semibold text-white hover:bg-slate-800" onClick={() => saveReportSection(workspace.project.id, section, workspace)}>
                <Save size={16} />
                {labels.save}
              </button>
              <p className="text-xs text-slate-500">{labels.updated}: {section.lastGeneratedAt}</p>
            </div>
            <div className="mt-5 rounded-md border border-slate-200 bg-slate-50 p-4">
              <div className="flex flex-wrap items-start justify-between gap-3">
                <div>
                  <h3 className="font-semibold text-slate-950">{labels.sectionRewrite}</h3>
                  <p className="mt-1 text-xs text-slate-500">{labels.noPersistenceBeforeAccept} · {labels.intelligenceUsesProjectSwitch}: {useAi ? labels.aiEnabled : labels.aiDisabled}</p>
                </div>
                {rewrite.result && rewriteSectionId === section.id ? <IntelligenceModeBadge result={rewrite.result} labels={labels} /> : null}
              </div>
              {rewrite.result?.executionStatus === "ai_fallback" && rewriteSectionId === section.id ? <p className="mt-3 rounded-md border border-amber-200 bg-amber-50 px-3 py-2 text-sm text-amber-900">{labels.fallbackHint}</p> : null}
              <label className="mt-4 grid gap-2 text-sm font-semibold text-slate-700">
                {labels.rewriteInstruction}
                <textarea className="min-h-24 resize-y rounded-md border border-slate-300 bg-white p-3 font-normal outline-none focus:ring-2 focus:ring-cyan-400" value={rewriteInstruction} placeholder={labels.rewritePlaceholder} onChange={(event) => setRewriteInstruction(event.target.value)} />
              </label>
              <button className="mt-3 inline-flex items-center gap-2 rounded-md bg-cyan-700 px-4 py-2 text-sm font-semibold text-white hover:bg-cyan-800 disabled:cursor-not-allowed disabled:opacity-50" onClick={() => { setRewriteSectionId(section.id); void rewrite.run(() => rewriteProjectReportSection(workspace.project.id, section.id, { instruction: rewriteInstruction.trim(), language, audience: "executive", quality: "quality", useAi })); }} disabled={rewrite.loading || acceptingSuggestions || !rewriteInstruction.trim()}>
                <Sparkles size={16} />
                {rewrite.loading ? labels.queryLoading : labels.suggestRewrite}
              </button>
              {rewrite.error && rewriteSectionId === section.id ? <div className="mt-4"><ActionError labels={labels} retry={rewrite.retry} useBasicAnalysis={() => void rewrite.run(() => rewriteProjectReportSection(workspace.project.id, section.id, { instruction: rewriteInstruction.trim(), language, audience: "executive", quality: "quality", useAi: false }))} disabled={rewrite.loading} /></div> : null}
              {rewrite.result && rewriteSectionId === section.id ? (
                <div className="mt-4 space-y-4">
                  <div className="grid gap-4 lg:grid-cols-2">
                    <div className="rounded-md bg-white p-4 ring-1 ring-slate-200"><p className="text-xs font-semibold uppercase text-slate-500">{labels.currentContent}</p><p className="mt-2 whitespace-pre-wrap text-sm leading-7 text-slate-700">{localize(section.body, language)}</p></div>
                    <div className="rounded-md bg-cyan-50 p-4 ring-1 ring-cyan-200"><p className="text-xs font-semibold uppercase text-cyan-800">{labels.suggestedContent}</p><p className="mt-2 whitespace-pre-wrap text-sm leading-7 text-slate-700">{localize(rewrite.result.suggestedBody, language)}</p></div>
                  </div>
                  <div className="grid gap-3 lg:grid-cols-2">
                    <LightEvidenceList title={labels.assumptions} items={rewrite.result.assumptions.map((item) => localize(item, language))} />
                    <LightEvidenceList title={labels.uncertainty} items={rewrite.result.uncertainty.map((item) => localize(item, language))} />
                  </div>
                  <div className="flex flex-wrap gap-2">
                    <button className="rounded-md bg-slate-950 px-3 py-2 text-sm font-semibold text-white hover:bg-slate-800 disabled:opacity-50" onClick={() => void acceptRewriteSuggestion()} disabled={acceptingSuggestions}>{labels.accept}</button>
                    <button className="rounded-md border border-slate-300 bg-white px-3 py-2 text-sm font-semibold text-slate-700 hover:bg-slate-100 disabled:opacity-50" onClick={() => { rewrite.reset(); setRewriteInstruction(""); setRewriteSectionId(""); }} disabled={acceptingSuggestions}>{labels.discard}</button>
                  </div>
                </div>
              ) : null}
            </div>
            <SectionContextPanel section={section} readiness={readiness} labels={labels} language={language} />
          </>
        ) : (
          <ReportPreview workspace={workspace} benchmarkResults={benchmarkResults} readiness={readiness} platformCatalog={platformCatalog} labels={labels} language={language} />
        )}
      </Panel>
      <Panel title={labels.analysisScope}>
        <div className="mb-5 space-y-2 rounded-md bg-slate-50 p-3">
          <FactRow label={labels.status} value={readiness.status} />
          <FactRow label={labels.readiness} value={`${readiness.score}%`} />
          <FactRow label={labels.confidence} value={readiness.confidenceLevel} />
        </div>
        <EvidenceBlock title={labels.dataSources} items={deliveryDataSources} />
        <EvidenceBlock title={labels.assumptions} items={deliveryAssumptions} />
        <EvidenceBlock title={labels.uncertainty} items={deliveryUncertainty} />
        <EvidenceBlock title={labels.unreadAttachments} items={deliveryScope.unreadAttachments.length ? deliveryScope.unreadAttachments : [language === "zh" ? "暂无登记附件" : "No registered attachments"]} />
      </Panel>
    </div>
    </div>
  );
}

function ReportPreview({
  workspace,
  benchmarkResults,
  readiness,
  platformCatalog,
  labels,
  language,
}: {
  workspace: ProjectWorkspace;
  benchmarkResults: BenchmarkResult[];
  readiness: ProjectReadiness;
  platformCatalog: PlcEcosystem[];
  labels: (typeof copy)[Language];
  language: Language;
}) {
  const lead = benchmarkResults[0];
  const candidatePlatforms = workspace.intake.candidatePlatforms.map((id) => platformName(id, platformCatalog)).join(", ");

  return (
    <article className="rounded-md border border-slate-200 bg-white">
      <div className="border-b border-slate-200 p-6">
        <p className="text-xs font-semibold uppercase tracking-wide text-cyan-700">{labels.reportPreview}</p>
        <h1 className="mt-2 text-2xl font-semibold text-slate-950">{workspace.project.name}</h1>
        <p className="mt-2 max-w-3xl text-sm leading-6 text-slate-600">{workspace.project.goal || "-"}</p>
        <div className="mt-5 grid gap-3 md:grid-cols-2 xl:grid-cols-3">
          <FactCard label={language === "zh" ? "行业" : "Industry"} value={workspace.project.industry || "-"} />
          <FactCard label={labels.candidatePlatforms} value={candidatePlatforms || "-"} />
          <FactCard label={labels.topRecommendation} value={lead ? platformName(lead.platformId, platformCatalog) : "-"} />
          <FactCard label={labels.status} value={readiness.status} />
          <FactCard label={labels.readiness} value={`${readiness.score}%`} />
          <FactCard label={labels.confidence} value={readiness.confidenceLevel} />
        </div>
      </div>
      <div className="space-y-6 p-6">
        {workspace.report.sections.map((section, index) => (
          <section key={section.id} className="rounded-md border border-slate-200 p-5">
            <div className="mb-3 flex items-center gap-3">
              <span className="rounded-full bg-slate-100 px-2 py-1 text-xs font-semibold text-slate-500">{String(index + 1).padStart(2, "0")}</span>
              <h2 className="text-lg font-semibold text-slate-950">{localize(section.title, language)}</h2>
            </div>
            <p className="whitespace-pre-wrap text-sm leading-7 text-slate-700">{localize(section.body, language) || "-"}</p>
            <SectionContextPanel section={section} readiness={readiness} labels={labels} language={language} compact />
          </section>
        ))}
      </div>
    </article>
  );
}

function SectionContextPanel({
  section,
  readiness,
  labels,
  language,
  compact = false,
}: {
  section: ReportSection;
  readiness: ProjectReadiness;
  labels: (typeof copy)[Language];
  language: Language;
  compact?: boolean;
}) {
  const missingInputs = missingInputLabels(readiness, language);
  return (
    <div className={`${compact ? "mt-4" : "mt-5"} rounded-md bg-slate-50 p-4`}>
      <p className="text-xs font-semibold uppercase tracking-wide text-slate-500">{labels.sectionContext}</p>
      <div className="mt-3 grid gap-3 md:grid-cols-2">
        <EvidenceBlock title={labels.dataSources} items={section.dataSourcesUsed.map((item) => localize(item, language))} />
        <EvidenceBlock title={labels.assumptions} items={section.assumptions.map((item) => localize(item, language))} />
        <EvidenceBlock title={labels.uncertainty} items={[localize(section.uncertainty, language)]} />
        <EvidenceBlock title={labels.missingInputs} items={missingInputs.length ? missingInputs : [labels.noMissingInputs]} />
      </div>
    </div>
  );
}

function FactCard({ label, value }: { label: string; value: string }) {
  return (
    <div className="rounded-md bg-slate-50 p-3">
      <p className="text-xs font-semibold uppercase tracking-wide text-slate-500">{label}</p>
      <p className="mt-1 text-sm font-semibold text-slate-900">{value}</p>
    </div>
  );
}

function FactRow({ label, value }: { label: string; value: string }) {
  return (
    <div className="flex items-center justify-between gap-3 text-sm">
      <span className="text-slate-500">{label}</span>
      <span className="text-right font-semibold text-slate-900">{value}</span>
    </div>
  );
}

function Panel({ title, description, children }: { title: string; description?: string; children?: React.ReactNode }) {
  return (
    <section className="rounded-md border border-slate-200 bg-white p-5 shadow-sm">
      <div className="mb-4">
        <h2 className="text-lg font-semibold">{title}</h2>
        {description ? <p className="mt-1 text-sm leading-6 text-slate-500">{description}</p> : null}
      </div>
      {children}
    </section>
  );
}

function Kpi({ label, value }: { label: string; value: string }) {
  return (
    <div className="rounded-md border border-slate-200 bg-slate-50 px-4 py-3">
      <p className="text-xs font-semibold uppercase tracking-wide text-slate-500">{label}</p>
      <p className="mt-1 text-lg font-semibold">{value}</p>
    </div>
  );
}

function Info({ title, value }: { title: string; value: string }) {
  return (
    <div className="rounded-md bg-slate-50 p-4">
      <p className="text-sm font-semibold">{title}</p>
      <p className="mt-2 text-sm leading-6 text-slate-600">{value || "-"}</p>
    </div>
  );
}

function SectionTitle({ title }: { title: string }) {
  return <h3 className="text-sm font-semibold uppercase tracking-wide text-slate-500">{title}</h3>;
}

function ValidationList({ title, items, labels }: { title: string; items: { label: string; ok: boolean }[]; labels: (typeof copy)[Language] }) {
  return (
    <div>
      <p className="text-sm font-semibold">{title}</p>
      <div className="mt-2 space-y-2">
        {items.map((item) => (
          <div key={item.label} className="flex items-center justify-between gap-3 rounded-md bg-slate-50 px-3 py-2 text-sm">
            <span>{item.label}</span>
            <span className={`inline-flex items-center gap-1 rounded-full px-2 py-1 text-xs font-semibold ${item.ok ? "bg-emerald-50 text-emerald-700" : "bg-amber-50 text-amber-800"}`}>
              {item.ok ? <CheckCircle2 size={13} /> : <AlertTriangle size={13} />}
              {item.ok ? labels.complete : labels.missing}
            </span>
          </div>
        ))}
      </div>
    </div>
  );
}

function ScoreDial({ label, value }: { label: string; value: number }) {
  return (
    <div className="rounded-md bg-slate-50 p-4">
      <p className="text-sm font-semibold">{label}</p>
      <div className="mt-3 flex items-end gap-2">
        <span className="text-4xl font-semibold text-cyan-800">{value}</span>
        <span className="pb-1 text-sm font-semibold text-slate-500">%</span>
      </div>
      <div className="mt-3 h-2 rounded-full bg-slate-200">
        <div className="h-2 rounded-full bg-cyan-600" style={{ width: `${Math.max(0, Math.min(100, value))}%` }} />
      </div>
    </div>
  );
}

function MetricBar({ label, value, tone = "cyan" }: { label: string; value: number; tone?: "cyan" | "emerald" | "slate" }) {
  const color = tone === "emerald" ? "bg-emerald-600" : tone === "slate" ? "bg-slate-600" : "bg-cyan-600";
  return (
    <div>
      <div className="mb-1 flex items-center justify-between gap-3 text-sm">
        <span>{label}</span>
        <span className="font-semibold text-slate-900">{value}</span>
      </div>
      <div className="h-2.5 rounded-full bg-slate-200">
        <div className={`h-2.5 rounded-full ${color}`} style={{ width: `${Math.max(0, Math.min(100, value))}%` }} />
      </div>
    </div>
  );
}

function MiniScore({ label, value }: { label: string; value: number }) {
  return (
    <div className="min-w-[82px] rounded-md bg-slate-50 px-2 py-2">
      <p className="truncate text-[11px] font-semibold text-slate-500">{label}</p>
      <p className="mt-1 text-base font-semibold text-slate-900">{value}</p>
    </div>
  );
}

function EvidenceBlock({ title, items }: { title: string; items: string[] }) {
  return (
    <div className="mb-5">
      <p className="text-xs font-semibold uppercase tracking-wide text-slate-500">{title}</p>
      <ul className="mt-2 space-y-2 text-sm leading-6 text-slate-600">
        {items.map((item) => (
          <li key={item} className="rounded-md bg-slate-50 p-2">{item}</li>
        ))}
      </ul>
    </div>
  );
}

function Field({ label, value, onChange, badge, wide = false }: { label: string; value: string; onChange: (value: string) => void; badge?: string; wide?: boolean }) {
  return (
    <label className={`grid gap-1 text-sm font-medium text-slate-700 ${wide ? "lg:col-span-2" : ""}`}>
      <span className="flex items-center justify-between gap-2">
        {label}
        {badge ? <span className="rounded-full bg-slate-100 px-2 py-0.5 text-[11px] font-semibold text-slate-500">{badge}</span> : null}
      </span>
      <input className="rounded-md border border-slate-300 px-3 py-2 outline-none focus:ring-2 focus:ring-cyan-400" value={value} onChange={(event) => onChange(event.target.value)} />
    </label>
  );
}

function NumberField({ label, value, onChange, badge }: { label: string; value: number; onChange: (value: number) => void; badge?: string }) {
  return (
    <label className="grid gap-1 text-sm font-medium text-slate-700">
      <span className="flex items-center justify-between gap-2">
        {label}
        {badge ? <span className="rounded-full bg-slate-100 px-2 py-0.5 text-[11px] font-semibold text-slate-500">{badge}</span> : null}
      </span>
      <input type="number" className="rounded-md border border-slate-300 px-3 py-2 outline-none focus:ring-2 focus:ring-cyan-400" value={value} onChange={(event) => onChange(Number(event.target.value))} />
    </label>
  );
}

function Select({ label, value, options, onChange, optionLabel }: { label: string; value: string; options: string[]; onChange: (value: string) => void; optionLabel?: (value: string) => string }) {
  return (
    <label className="grid gap-1 text-sm font-medium text-slate-700">
      {label}
      <select className="rounded-md border border-slate-300 px-3 py-2 outline-none focus:ring-2 focus:ring-cyan-400" value={value} onChange={(event) => onChange(event.target.value)}>
        {options.map((option) => (
          <option key={option} value={option}>
            {optionLabel ? optionLabel(option) : option}
          </option>
        ))}
      </select>
    </label>
  );
}

function Range({ label, value, onChange }: { label: string; value: number; onChange: (value: number) => void }) {
  return (
    <label className="grid gap-2 text-sm font-medium text-slate-700">
      <span className="flex items-center justify-between gap-3">
        {label}
        <span className="font-semibold text-cyan-700">{value}</span>
      </span>
      <input className="accent-cyan-700" type="range" min="0" max="100" value={value} onChange={(event) => onChange(Number(event.target.value))} />
    </label>
  );
}
