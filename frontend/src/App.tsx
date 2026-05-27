import {
  AlertTriangle,
  BarChart3,
  ClipboardList,
  Cpu,
  FileText,
  FolderPlus,
  Languages,
  MessageSquareText,
  PanelLeftClose,
  PanelLeftOpen,
  Paperclip,
  Save,
  Send,
  SlidersHorizontal,
  Sparkles,
} from "lucide-react";
import { useEffect, useMemo, useState } from "react";
import { ecosystems, initialMessages, workspaces as seedWorkspaces } from "./data/platforms";
import type {
  BenchmarkResult,
  ChatMessage,
  Language,
  LocalizedText,
  PlcEcosystem,
  ProjectAttachment,
  ProjectWorkspace,
  ReportSection,
  WorkspaceTab,
} from "./types";

const copy = {
  zh: {
    title: "PLC 平台基准与迁移决策副驾驶",
    subtitle: "创建项目、登记资料、设置平台倾向、自动分析并生成报告",
    language: "English",
    newProject: "新建项目",
    ecosystems: "PLC 生态",
    query: "当前项目 Query",
    send: "发送",
    askPlaceholder: "输入项目约束、选型问题或报告修改意见",
    project: "项目",
    status: "状态",
    updated: "更新",
    overview: "总览",
    intake: "项目信息",
    preferences: "平台倾向",
    attachments: "资料附件",
    benchmark: "Benchmark",
    report: "报告",
    projectGoal: "项目目标",
    deterministic: "确定性自动化",
    agentRole: "Agent 角色",
    automationList: "表单校验、平台评分、偏好加权、风险初判、报告结构生成。",
    agentList: "解释得分、补全追问、生成报告草稿、说明假设与不确定性。",
    save: "保存",
    generateReport: "生成报告草稿",
    regenerateSection: "重算当前分区",
    addAttachment: "登记附件",
    fileNote: "第一版只记录附件元信息，不解析文件内容，也不接 RAG。",
    technicalScore: "技术评分",
    preferenceScore: "倾向评分",
    weightedScore: "加权总分",
    risk: "风险",
    assumptions: "假设与不确定性",
    reportSections: "报告目录",
    sectionEditor: "分区编辑",
    rightPanel: "依据面板",
    candidatePlatforms: "候选平台",
    projectInputs: "轻量输入",
    emptyQuestion: "请输入内容后再发送。",
  },
  en: {
    title: "PLC Platform Benchmark & Migration Decision Copilot",
    subtitle: "Create projects, register documents, set platform preference, run analysis, and generate reports",
    language: "中文",
    newProject: "New Project",
    ecosystems: "PLC Ecosystems",
    query: "Current Project Query",
    send: "Send",
    askPlaceholder: "Enter project constraints, selection questions, or report revision requests",
    project: "Project",
    status: "Status",
    updated: "Updated",
    overview: "Overview",
    intake: "Intake",
    preferences: "Preferences",
    attachments: "Attachments",
    benchmark: "Benchmark",
    report: "Report",
    projectGoal: "Project Goal",
    deterministic: "Deterministic Automation",
    agentRole: "Agent Role",
    automationList: "Form validation, platform scoring, preference weighting, risk estimate, and report structure generation.",
    agentList: "Explain scores, ask follow-ups, draft report text, and state assumptions and uncertainty.",
    save: "Save",
    generateReport: "Generate Report Draft",
    regenerateSection: "Regenerate Section",
    addAttachment: "Register Attachment",
    fileNote: "V1 only records attachment metadata. It does not parse files or run RAG.",
    technicalScore: "Technical Score",
    preferenceScore: "Preference Score",
    weightedScore: "Weighted Score",
    risk: "Risk",
    assumptions: "Assumptions & Uncertainty",
    reportSections: "Report Sections",
    sectionEditor: "Section Editor",
    rightPanel: "Evidence Panel",
    candidatePlatforms: "Candidate Platforms",
    projectInputs: "Lightweight Inputs",
    emptyQuestion: "Enter content before sending.",
  },
};

const tabs: { id: WorkspaceTab; icon: React.ReactNode }[] = [
  { id: "overview", icon: <ClipboardList size={16} /> },
  { id: "intake", icon: <FileText size={16} /> },
  { id: "preferences", icon: <SlidersHorizontal size={16} /> },
  { id: "attachments", icon: <Paperclip size={16} /> },
  { id: "benchmark", icon: <BarChart3 size={16} /> },
  { id: "report", icon: <Sparkles size={16} /> },
];

const riskClass = {
  Low: "bg-emerald-50 text-emerald-700 ring-emerald-200",
  Medium: "bg-amber-50 text-amber-800 ring-amber-200",
  High: "bg-rose-50 text-rose-700 ring-rose-200",
};

function localize(value: LocalizedText, language: Language): string {
  return value[language];
}

function averageScore(platform: PlcEcosystem) {
  const values = Object.values(platform.scores);
  return Math.round(values.reduce((sum, value) => sum + value, 0) / values.length);
}

function calculateBenchmark(workspace: ProjectWorkspace): BenchmarkResult[] {
  return ecosystems
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
          zh: `${platform.name} 的技术评分为 ${technical}，用户倾向为 ${preference}，综合后为 ${weighted}。`,
          en: `${platform.name} has a technical score of ${technical}, preference score of ${preference}, and weighted score of ${weighted}.`,
        },
        assumptions: [
          { zh: "技术评分来自 mock 平台 profile。", en: "Technical score comes from mock platform profiles." },
          { zh: "用户倾向权重占综合评分 28%。", en: "User preference contributes 28% of the weighted score." },
        ],
      } satisfies BenchmarkResult;
    })
    .sort((a, b) => b.weightedScore - a.weightedScore);
}

export default function App() {
  const [language, setLanguage] = useState<Language>("zh");
  const [sidebarOpen, setSidebarOpen] = useState(true);
  const [workspaces, setWorkspaces] = useState<ProjectWorkspace[]>(seedWorkspaces);
  const [selectedProjectId, setSelectedProjectId] = useState(seedWorkspaces[0].project.id);
  const [selectedEcosystemId, setSelectedEcosystemId] = useState("siemens-tia");
  const [activeTab, setActiveTab] = useState<WorkspaceTab>("overview");
  const [activeReportSectionId, setActiveReportSectionId] = useState("executive-summary");
  const [draft, setDraft] = useState("");
  const [draftError, setDraftError] = useState("");
  const [threads, setThreads] = useState<Record<string, ChatMessage[]>>(initialMessages);

  const t = copy[language];
  const workspace = workspaces.find((item) => item.project.id === selectedProjectId) ?? workspaces[0];
  const selectedEcosystem = ecosystems.find((item) => item.id === selectedEcosystemId) ?? ecosystems[0];
  const benchmarkResults = useMemo(() => calculateBenchmark(workspace), [workspace]);
  const topResult = benchmarkResults[0];
  const topPlatform = ecosystems.find((item) => item.id === topResult?.platformId) ?? ecosystems[0];
  const messages = threads[selectedProjectId] ?? initialMessages[selectedEcosystemId] ?? [];

  useEffect(() => {
    document.documentElement.lang = language === "zh" ? "zh-CN" : "en";
  }, [language]);

  function updateWorkspace(next: ProjectWorkspace) {
    setWorkspaces((current) => current.map((item) => (item.project.id === next.project.id ? next : item)));
  }

  function createProject() {
    const id = `project-${workspaces.length + 1}`;
    const now = "2026-05-27";
    const next: ProjectWorkspace = {
      project: {
        id,
        name: language === "zh" ? "新建 PLC 决策项目" : "New PLC Decision Project",
        industry: "General Manufacturing",
        goal: language === "zh" ? "填写项目目标并运行 benchmark 分析。" : "Fill in the project goal and run benchmark analysis.",
        status: "Draft",
        createdAt: now,
        updatedAt: now,
      },
      intake: {
        projectSize: "Medium",
        ioScale: 300,
        motionRequirement: 50,
        safetyRequirement: 50,
        budgetSensitivity: 50,
        teamExperience: "",
        existingPlatform: "siemens-tia",
        candidatePlatforms: ecosystems.slice(0, 4).map((item) => item.id),
        constraints: "",
      },
      preferences: ecosystems.map((platform) => ({ platformId: platform.id, preferenceWeight: 50, userReasonNote: "" })),
      attachments: [],
      report: {
        projectId: id,
        version: 1,
        status: "Draft",
        sections: [],
      },
    };
    setWorkspaces([next, ...workspaces]);
    setSelectedProjectId(id);
    setActiveTab("intake");
  }

  function sendMessage() {
    const question = draft.trim();
    if (!question) {
      setDraftError(t.emptyQuestion);
      return;
    }
    const assistant: ChatMessage = {
      role: "assistant",
      content: {
        zh: `已记录。当前项目推荐先完善轻量输入、确认候选平台，再查看 ${topPlatform.name} 的 benchmark 解释。`,
        en: `Noted. For this project, complete lightweight inputs, confirm candidates, then review the benchmark explanation for ${topPlatform.name}.`,
      },
    };
    const user: ChatMessage = { role: "user", content: { zh: question, en: question } };
    setThreads({ ...threads, [selectedProjectId]: [...messages, user, assistant] });
    setDraft("");
    setDraftError("");
  }

  return (
    <main className="flex h-screen min-h-[760px] overflow-hidden bg-slate-100 text-slate-950">
      <aside className={`${sidebarOpen ? "w-full max-w-[400px]" : "w-[76px]"} flex shrink-0 flex-col border-r border-slate-200 bg-slate-950 text-white transition-all duration-300`}>
        <div className="flex min-h-[88px] items-center justify-between gap-3 border-b border-white/10 p-4">
          {sidebarOpen ? (
            <div className="min-w-0">
              <p className="text-xs font-semibold uppercase tracking-wide text-cyan-300">{t.project}</p>
              <h1 className="mt-1 text-lg font-semibold leading-6">{t.title}</h1>
            </div>
          ) : (
            <Cpu className="mx-auto text-cyan-300" size={24} />
          )}
          <button className="rounded-md bg-white/10 p-2 hover:bg-white/15" onClick={() => setSidebarOpen(!sidebarOpen)}>
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
                {ecosystems.map((platform) => (
                  <button
                    key={platform.id}
                    className={`rounded-md border p-3 text-left transition ${selectedEcosystemId === platform.id ? "border-cyan-400 bg-cyan-400/15" : "border-white/10 bg-white/5 hover:bg-white/10"}`}
                    onClick={() => setSelectedEcosystemId(platform.id)}
                  >
                    <div className="flex items-center justify-between gap-3">
                      <div className="min-w-0">
                        <p className="truncate text-sm font-semibold">{platform.name}</p>
                        <p className="truncate text-xs text-slate-400">{platform.software}</p>
                      </div>
                      <Cpu className="shrink-0 text-cyan-300" size={18} />
                    </div>
                  </button>
                ))}
              </div>
            </section>

            <section className="flex min-h-0 flex-1 flex-col p-4">
              <div className="flex items-center gap-2">
                <MessageSquareText className="text-cyan-300" size={18} />
                <h2 className="text-sm font-semibold">{t.query}</h2>
              </div>
              <div className="mt-3 rounded-md border border-white/10 bg-white/5 p-3">
                <p className="text-sm font-semibold">{workspace.project.name}</p>
                <p className="mt-1 text-xs text-slate-400">{workspace.project.goal}</p>
              </div>
              <div className="mt-3 min-h-0 flex-1 space-y-3 overflow-y-auto pr-1">
                {messages.map((message, index) => (
                  <div key={`${message.role}-${index}`} className={`rounded-md p-3 text-sm leading-6 ${message.role === "assistant" ? "bg-cyan-400/10 text-cyan-50" : "bg-white text-slate-900"}`}>
                    <p className="mb-1 text-xs font-semibold opacity-70">{message.role === "assistant" ? "Copilot" : "You"}</p>
                    {localize(message.content, language)}
                  </div>
                ))}
              </div>
              <div className="mt-3">
                {draftError ? <p className="mb-2 text-xs font-medium text-amber-300">{draftError}</p> : null}
                <div className="flex gap-2">
                  <textarea className="h-20 min-w-0 flex-1 resize-none rounded-md border border-white/10 bg-slate-900 p-3 text-sm text-white outline-none ring-cyan-400 placeholder:text-slate-500 focus:ring-2" placeholder={t.askPlaceholder} value={draft} onChange={(event) => setDraft(event.target.value)} />
                  <button className="inline-flex w-12 items-center justify-center rounded-md bg-cyan-500 text-slate-950 hover:bg-cyan-400" onClick={sendMessage} aria-label={t.send}>
                    <Send size={18} />
                  </button>
                </div>
              </div>
            </section>
          </div>
        ) : null}
      </aside>

      <section className="min-w-0 flex-1 overflow-y-auto">
        <header className="border-b border-slate-200 bg-white px-5 py-5 lg:px-6">
          <div className="flex flex-col gap-4 xl:flex-row xl:items-center xl:justify-between">
            <div>
              <p className="text-xs font-semibold uppercase tracking-wide text-cyan-700">{t.subtitle}</p>
              <div className="mt-2 flex flex-wrap items-center gap-3">
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
              </div>
            </div>
            <div className="grid grid-cols-3 gap-3 text-sm">
              <Kpi label={t.status} value={workspace.project.status} />
              <Kpi label={t.updated} value={workspace.project.updatedAt} />
              <Kpi label={t.weightedScore} value={`${topResult?.weightedScore ?? 0}/100`} />
            </div>
          </div>

          <nav className="mt-5 flex gap-2 overflow-x-auto pb-1">
            {tabs.map((tab) => (
              <button key={tab.id} className={`inline-flex shrink-0 items-center gap-2 rounded-md px-3 py-2 text-sm font-semibold transition ${activeTab === tab.id ? "bg-cyan-700 text-white" : "bg-slate-100 text-slate-700 hover:bg-slate-200"}`} onClick={() => setActiveTab(tab.id)}>
                {tab.icon}
                {t[tab.id]}
              </button>
            ))}
          </nav>
        </header>

        <div className="p-5 lg:p-6">
          {activeTab === "overview" ? <Overview workspace={workspace} topPlatform={topPlatform} topResult={topResult} language={language} labels={t} /> : null}
          {activeTab === "intake" ? <Intake workspace={workspace} updateWorkspace={updateWorkspace} labels={t} /> : null}
          {activeTab === "preferences" ? <Preferences workspace={workspace} updateWorkspace={updateWorkspace} labels={t} /> : null}
          {activeTab === "attachments" ? <Attachments workspace={workspace} updateWorkspace={updateWorkspace} labels={t} /> : null}
          {activeTab === "benchmark" ? <Benchmark results={benchmarkResults} labels={t} language={language} /> : null}
          {activeTab === "report" ? <ReportBuilder workspace={workspace} updateWorkspace={updateWorkspace} labels={t} language={language} activeSectionId={activeReportSectionId} setActiveSectionId={setActiveReportSectionId} benchmarkResults={benchmarkResults} /> : null}
        </div>
      </section>
    </main>
  );
}

function Overview({ workspace, topPlatform, topResult, language, labels }: { workspace: ProjectWorkspace; topPlatform: PlcEcosystem; topResult?: BenchmarkResult; language: Language; labels: (typeof copy)[Language] }) {
  return (
    <div className="grid gap-5 xl:grid-cols-[1fr_360px]">
      <Panel title={workspace.project.name} description={workspace.project.goal}>
        <div className="grid gap-4 md:grid-cols-2">
          <Info title={labels.projectInputs} value={`${workspace.intake.projectSize} / ${workspace.intake.ioScale} I/O`} />
          <Info title={labels.candidatePlatforms} value={workspace.intake.candidatePlatforms.map((id) => ecosystems.find((item) => item.id === id)?.name).join(", ")} />
          <Info title={labels.deterministic} value={labels.automationList} />
          <Info title={labels.agentRole} value={labels.agentList} />
        </div>
      </Panel>
      <Panel title={labels.benchmark} description={topPlatform.name}>
        <MetricBar label={labels.technicalScore} value={topResult?.technicalScore ?? 0} />
        <MetricBar label={labels.preferenceScore} value={topResult?.preferenceScore ?? 0} />
        <MetricBar label={labels.weightedScore} value={topResult?.weightedScore ?? 0} />
        <p className="mt-4 text-sm leading-6 text-slate-600">{topResult ? localize(topResult.rationale, language) : ""}</p>
      </Panel>
    </div>
  );
}

function Intake({ workspace, updateWorkspace, labels }: { workspace: ProjectWorkspace; updateWorkspace: (workspace: ProjectWorkspace) => void; labels: (typeof copy)[Language] }) {
  const [draft, setDraft] = useState(workspace);
  return (
    <Panel title={labels.intake} description={labels.projectInputs}>
      <div className="grid gap-4 lg:grid-cols-2">
        <Field label="Project Name" value={draft.project.name} onChange={(value) => setDraft({ ...draft, project: { ...draft.project, name: value } })} />
        <Field label="Industry" value={draft.project.industry} onChange={(value) => setDraft({ ...draft, project: { ...draft.project, industry: value } })} />
        <Field label="Goal" value={draft.project.goal} onChange={(value) => setDraft({ ...draft, project: { ...draft.project, goal: value } })} wide />
        <Select label="Project Size" value={draft.intake.projectSize} options={["Small", "Medium", "Large"]} onChange={(value) => setDraft({ ...draft, intake: { ...draft.intake, projectSize: value as ProjectWorkspace["intake"]["projectSize"] } })} />
        <NumberField label="I/O Scale" value={draft.intake.ioScale} onChange={(value) => setDraft({ ...draft, intake: { ...draft.intake, ioScale: value } })} />
        <Range label="Motion Requirement" value={draft.intake.motionRequirement} onChange={(value) => setDraft({ ...draft, intake: { ...draft.intake, motionRequirement: value } })} />
        <Range label="Safety Requirement" value={draft.intake.safetyRequirement} onChange={(value) => setDraft({ ...draft, intake: { ...draft.intake, safetyRequirement: value } })} />
        <Range label="Budget Sensitivity" value={draft.intake.budgetSensitivity} onChange={(value) => setDraft({ ...draft, intake: { ...draft.intake, budgetSensitivity: value } })} />
        <Field label="Team Experience" value={draft.intake.teamExperience} onChange={(value) => setDraft({ ...draft, intake: { ...draft.intake, teamExperience: value } })} wide />
        <Field label="Constraints" value={draft.intake.constraints} onChange={(value) => setDraft({ ...draft, intake: { ...draft.intake, constraints: value } })} wide />
      </div>
      <button className="mt-5 inline-flex items-center gap-2 rounded-md bg-cyan-700 px-4 py-2 text-sm font-semibold text-white hover:bg-cyan-800" onClick={() => updateWorkspace({ ...draft, project: { ...draft.project, updatedAt: "2026-05-27" } })}>
        <Save size={16} />
        {labels.save}
      </button>
    </Panel>
  );
}

function Preferences({ workspace, updateWorkspace, labels }: { workspace: ProjectWorkspace; updateWorkspace: (workspace: ProjectWorkspace) => void; labels: (typeof copy)[Language] }) {
  return (
    <Panel title={labels.preferences} description="Preference sliders participate in the benchmark weighted score.">
      <div className="grid gap-4">
        {workspace.preferences.map((pref) => {
          const platform = ecosystems.find((item) => item.id === pref.platformId) ?? ecosystems[0];
          return (
            <div key={pref.platformId} className="rounded-md border border-slate-200 p-4">
              <Range label={platform.name} value={pref.preferenceWeight} onChange={(value) => updateWorkspace({ ...workspace, preferences: workspace.preferences.map((item) => (item.platformId === pref.platformId ? { ...item, preferenceWeight: value } : item)) })} />
              <input className="mt-3 w-full rounded-md border border-slate-300 px-3 py-2 text-sm" placeholder="Reason note / 倾向原因" value={pref.userReasonNote} onChange={(event) => updateWorkspace({ ...workspace, preferences: workspace.preferences.map((item) => (item.platformId === pref.platformId ? { ...item, userReasonNote: event.target.value } : item)) })} />
            </div>
          );
        })}
      </div>
    </Panel>
  );
}

function Attachments({ workspace, updateWorkspace, labels }: { workspace: ProjectWorkspace; updateWorkspace: (workspace: ProjectWorkspace) => void; labels: (typeof copy)[Language] }) {
  function addAttachment() {
    const next: ProjectAttachment = {
      id: `att-${workspace.attachments.length + 1}`,
      projectId: workspace.project.id,
      fileName: `New_Project_Document_${workspace.attachments.length + 1}.xlsx`,
      fileType: "I/O List",
      declaredPurpose: "Registered metadata only. File parsing is out of scope for V1.",
      uploadedAt: "2026-05-27",
    };
    updateWorkspace({ ...workspace, attachments: [...workspace.attachments, next] });
  }
  return (
    <Panel title={labels.attachments} description={labels.fileNote}>
      <button className="mb-4 inline-flex items-center gap-2 rounded-md bg-slate-950 px-4 py-2 text-sm font-semibold text-white hover:bg-slate-800" onClick={addAttachment}>
        <Paperclip size={16} />
        {labels.addAttachment}
      </button>
      <div className="grid gap-3">
        {workspace.attachments.map((attachment) => (
          <div key={attachment.id} className="rounded-md border border-slate-200 bg-white p-4">
            <div className="flex flex-wrap items-center justify-between gap-3">
              <h3 className="font-semibold">{attachment.fileName}</h3>
              <span className="rounded-full bg-slate-100 px-2 py-1 text-xs font-semibold text-slate-600">{attachment.fileType}</span>
            </div>
            <p className="mt-2 text-sm text-slate-600">{attachment.declaredPurpose}</p>
            <p className="mt-2 text-xs text-slate-400">{attachment.uploadedAt}</p>
          </div>
        ))}
      </div>
    </Panel>
  );
}

function Benchmark({ results, labels, language }: { results: BenchmarkResult[]; labels: (typeof copy)[Language]; language: Language }) {
  return (
    <Panel title={labels.benchmark} description="Deterministic ranking: technical score + platform preference weight.">
      <div className="grid gap-4">
        {results.map((result, index) => {
          const platform = ecosystems.find((item) => item.id === result.platformId) ?? ecosystems[0];
          return (
            <div key={result.platformId} className="rounded-md border border-slate-200 p-4">
              <div className="flex flex-wrap items-start justify-between gap-3">
                <div>
                  <p className="text-sm text-slate-500">#{index + 1}</p>
                  <h3 className="text-lg font-semibold">{platform.name}</h3>
                  <p className="mt-1 text-sm text-slate-600">{localize(result.rationale, language)}</p>
                </div>
                <span className={`rounded-full px-2.5 py-1 text-xs font-semibold ring-1 ${riskClass[result.riskLevel]}`}>{result.riskLevel}</span>
              </div>
              <div className="mt-4 grid gap-3 md:grid-cols-3">
                <MetricBar label={labels.technicalScore} value={result.technicalScore} />
                <MetricBar label={labels.preferenceScore} value={result.preferenceScore} />
                <MetricBar label={labels.weightedScore} value={result.weightedScore} />
              </div>
            </div>
          );
        })}
      </div>
    </Panel>
  );
}

function ReportBuilder({
  workspace,
  updateWorkspace,
  labels,
  language,
  activeSectionId,
  setActiveSectionId,
  benchmarkResults,
}: {
  workspace: ProjectWorkspace;
  updateWorkspace: (workspace: ProjectWorkspace) => void;
  labels: (typeof copy)[Language];
  language: Language;
  activeSectionId: string;
  setActiveSectionId: (id: string) => void;
  benchmarkResults: BenchmarkResult[];
}) {
  const section = workspace.report.sections.find((item) => item.id === activeSectionId) ?? workspace.report.sections[0];
  const topPlatform = ecosystems.find((item) => item.id === benchmarkResults[0]?.platformId);

  function regenerateSection() {
    if (!section) return;
    const generated: ReportSection = {
      ...section,
      body: {
        zh: `基于当前输入和偏好权重，${topPlatform?.name ?? "候选平台"} 是当前排序最高的平台。本段由确定性分析结果生成，Agent 只负责文字组织和假设说明。`,
        en: `Based on current inputs and preference weights, ${topPlatform?.name ?? "the candidate platform"} ranks highest. This section is generated from deterministic analysis; the agent only drafts wording and states assumptions.`,
      },
      lastGeneratedAt: "2026-05-27",
    };
    updateWorkspace({ ...workspace, report: { ...workspace.report, sections: workspace.report.sections.map((item) => (item.id === section.id ? generated : item)), status: "Ready" } });
  }

  if (!section) {
    return <Panel title={labels.report} description="No report sections available yet." />;
  }

  return (
    <div className="grid gap-5 xl:grid-cols-[260px_minmax(0,1fr)_280px]">
      <Panel title={labels.reportSections}>
        <div className="space-y-2">
          {workspace.report.sections.map((item) => (
            <button key={item.id} className={`w-full rounded-md px-3 py-2 text-left text-sm font-semibold ${item.id === section.id ? "bg-cyan-50 text-cyan-800" : "bg-slate-50 text-slate-700 hover:bg-slate-100"}`} onClick={() => setActiveSectionId(item.id)}>
              {localize(item.title, language)}
            </button>
          ))}
        </div>
      </Panel>
      <Panel title={labels.sectionEditor} description={localize(section.title, language)}>
        <textarea className="h-[360px] w-full resize-none rounded-md border border-slate-300 p-4 text-sm leading-6" value={localize(section.body, language)} onChange={(event) => updateWorkspace({ ...workspace, report: { ...workspace.report, sections: workspace.report.sections.map((item) => (item.id === section.id ? { ...item, body: { ...item.body, [language]: event.target.value } } : item)) } })} />
        <button className="mt-4 inline-flex items-center gap-2 rounded-md bg-cyan-700 px-4 py-2 text-sm font-semibold text-white hover:bg-cyan-800" onClick={regenerateSection}>
          <Sparkles size={16} />
          {labels.regenerateSection}
        </button>
      </Panel>
      <Panel title={labels.rightPanel} description={labels.assumptions}>
        <ul className="list-disc space-y-2 pl-5 text-sm leading-6 text-slate-600">
          {section.assumptions.map((item) => (
            <li key={localize(item, language)}>{localize(item, language)}</li>
          ))}
        </ul>
      </Panel>
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
      <p className="mt-2 text-sm leading-6 text-slate-600">{value}</p>
    </div>
  );
}

function MetricBar({ label, value }: { label: string; value: number }) {
  return (
    <div>
      <div className="mb-1 flex items-center justify-between text-sm">
        <span>{label}</span>
        <span className="font-semibold text-cyan-700">{value}</span>
      </div>
      <div className="h-2.5 rounded-full bg-slate-200">
        <div className="h-2.5 rounded-full bg-cyan-600" style={{ width: `${Math.max(0, Math.min(100, value))}%` }} />
      </div>
    </div>
  );
}

function Field({ label, value, onChange, wide = false }: { label: string; value: string; onChange: (value: string) => void; wide?: boolean }) {
  return (
    <label className={`grid gap-1 text-sm font-medium text-slate-700 ${wide ? "lg:col-span-2" : ""}`}>
      {label}
      <input className="rounded-md border border-slate-300 px-3 py-2" value={value} onChange={(event) => onChange(event.target.value)} />
    </label>
  );
}

function NumberField({ label, value, onChange }: { label: string; value: number; onChange: (value: number) => void }) {
  return (
    <label className="grid gap-1 text-sm font-medium text-slate-700">
      {label}
      <input type="number" className="rounded-md border border-slate-300 px-3 py-2" value={value} onChange={(event) => onChange(Number(event.target.value))} />
    </label>
  );
}

function Select({ label, value, options, onChange }: { label: string; value: string; options: string[]; onChange: (value: string) => void }) {
  return (
    <label className="grid gap-1 text-sm font-medium text-slate-700">
      {label}
      <select className="rounded-md border border-slate-300 px-3 py-2" value={value} onChange={(event) => onChange(event.target.value)}>
        {options.map((option) => (
          <option key={option} value={option}>
            {option}
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
      <input type="range" min="0" max="100" value={value} onChange={(event) => onChange(Number(event.target.value))} />
    </label>
  );
}
