import {
  AlertTriangle,
  ChevronRight,
  Cpu,
  Languages,
  LayoutDashboard,
  MessageSquareText,
  PanelLeftClose,
  PanelLeftOpen,
  Send,
  Sparkles,
} from "lucide-react";
import { useEffect, useMemo, useState } from "react";
import { ecosystems, initialMessages, projects } from "./data/platforms";
import type { ChatMessage, Language, LocalizedText, PlcEcosystem, PlcProject } from "./types";

const copy = {
  zh: {
    appTitle: "PLC 平台基准与迁移决策副驾驶",
    appSubtitle: "战略选型、迁移评估与项目沟通工作台",
    language: "English",
    collapse: "收起侧边栏",
    expand: "展开侧边栏",
    sidebarHint: "点击 PLC 生态后，在侧栏内展开沟通区。",
    askPlaceholder: "输入项目背景、约束或选型问题",
    askButton: "发送",
    currentThread: "当前沟通",
    projectList: "已沟通过的 PLC 项目",
    projectListHint: "点击项目查看沟通结果、选型建议和迁移信息。",
    decisionResult: "项目沟通结果",
    selectedPlatform: "推荐平台",
    decisionFactors: "决策依据",
    migrationNotes: "迁移与落地信息",
    effort: "工程量指数",
    risk: "风险等级",
    status: "状态",
    objective: "项目目标",
    recommendation: "推荐结论",
    benchmark: "平台基准摘要",
    noProject: "当前 PLC 生态还没有关联项目。",
    dashboard: "决策工作台",
    queryPanel: "Query 沟通区",
    popular: "流行 PLC 生态",
    summary: "生态摘要",
    strengths: "优势",
    cautions: "注意点",
    you: "你",
    copilot: "Copilot",
    emptyDraft: "请输入问题后再发送。",
  },
  en: {
    appTitle: "PLC Platform Benchmark & Migration Decision Copilot",
    appSubtitle: "Strategic selection, migration assessment, and project communication workspace",
    language: "中文",
    collapse: "Collapse sidebar",
    expand: "Expand sidebar",
    sidebarHint: "Click a PLC ecosystem to open its query area inside the sidebar.",
    askPlaceholder: "Enter project context, constraints, or selection questions",
    askButton: "Send",
    currentThread: "Current conversation",
    projectList: "Discussed PLC Projects",
    projectListHint: "Click a project to view communication results, selection advice, and migration information.",
    decisionResult: "Project Communication Result",
    selectedPlatform: "Recommended Platform",
    decisionFactors: "Decision Factors",
    migrationNotes: "Migration Notes",
    effort: "Engineering Effort Index",
    risk: "Risk Level",
    status: "Status",
    objective: "Project Objective",
    recommendation: "Recommendation",
    benchmark: "Platform Benchmark Snapshot",
    noProject: "No project is linked to this PLC ecosystem yet.",
    dashboard: "Decision Workspace",
    queryPanel: "Query Panel",
    popular: "Popular PLC Ecosystems",
    summary: "Ecosystem Summary",
    strengths: "Strengths",
    cautions: "Cautions",
    you: "You",
    copilot: "Copilot",
    emptyDraft: "Enter a question before sending.",
  },
};

const riskClass = {
  Low: "bg-emerald-50 text-emerald-700 ring-emerald-200",
  Medium: "bg-amber-50 text-amber-800 ring-amber-200",
  High: "bg-rose-50 text-rose-700 ring-rose-200",
};

function localize(value: LocalizedText, language: Language): string {
  return value[language];
}

export default function App() {
  const [language, setLanguage] = useState<Language>("zh");
  const [sidebarOpen, setSidebarOpen] = useState(true);
  const [selectedEcosystemId, setSelectedEcosystemId] = useState("siemens-tia");
  const [selectedProjectId, setSelectedProjectId] = useState(projects[0].id);
  const [draft, setDraft] = useState("");
  const [draftError, setDraftError] = useState("");
  const [threads, setThreads] = useState<Record<string, ChatMessage[]>>(initialMessages);

  const t = copy[language];
  const selectedEcosystem = ecosystems.find((item) => item.id === selectedEcosystemId) ?? ecosystems[0];
  const selectedProject = projects.find((item) => item.id === selectedProjectId) ?? projects[0];
  const projectPlatform = ecosystems.find((item) => item.id === selectedProject.selectedPlatformId) ?? ecosystems[0];
  const messages = threads[selectedEcosystem.id] ?? [];

  const relatedProjects = useMemo(
    () => projects.filter((project) => project.selectedPlatformId === selectedEcosystem.id),
    [selectedEcosystem.id],
  );

  useEffect(() => {
    document.documentElement.lang = language === "zh" ? "zh-CN" : "en";
  }, [language]);

  function selectProject(project: PlcProject) {
    setSelectedProjectId(project.id);
    setSelectedEcosystemId(project.selectedPlatformId);
  }

  function sendMessage() {
    const question = draft.trim();
    if (!question) {
      setDraftError(t.emptyDraft);
      return;
    }

    const userMessage: ChatMessage = {
      role: "user",
      content: { zh: question, en: question },
    };
    const assistantMessage: ChatMessage = {
      role: "assistant",
      content: {
        zh: `已记录该约束。基于 ${selectedEcosystem.name}，下一步建议补充项目规模、I/O 点数、安全等级、停机窗口和团队经验。`,
        en: `Constraint recorded. For ${selectedEcosystem.name}, the next step is to add project size, I/O count, safety level, downtime window, and team experience.`,
      },
    };

    setThreads({
      ...threads,
      [selectedEcosystem.id]: [...messages, userMessage, assistantMessage],
    });
    setDraft("");
    setDraftError("");
  }

  return (
    <main className="flex h-screen min-h-[720px] overflow-hidden bg-slate-100 text-slate-950">
      <aside className={`${sidebarOpen ? "w-full max-w-[410px]" : "w-[76px]"} flex shrink-0 flex-col border-r border-slate-200 bg-slate-950 text-white transition-all duration-300 lg:w-auto`}>
        <div className="flex min-h-[88px] items-center justify-between gap-3 border-b border-white/10 p-4">
          {sidebarOpen ? (
            <div className="min-w-0">
              <p className="text-xs font-semibold uppercase tracking-wide text-cyan-300">{t.dashboard}</p>
              <h1 className="mt-1 text-lg font-semibold leading-6">{t.appTitle}</h1>
            </div>
          ) : (
            <LayoutDashboard className="mx-auto text-cyan-300" size={24} />
          )}
          <button
            className="rounded-md bg-white/10 p-2 text-white transition hover:bg-white/15"
            onClick={() => setSidebarOpen(!sidebarOpen)}
            aria-label={sidebarOpen ? t.collapse : t.expand}
            title={sidebarOpen ? t.collapse : t.expand}
          >
            {sidebarOpen ? <PanelLeftClose size={18} /> : <PanelLeftOpen size={18} />}
          </button>
        </div>

        {sidebarOpen ? (
          <div className="flex min-h-0 flex-1 flex-col">
            <section className="border-b border-white/10 p-4">
              <div className="flex items-start justify-between gap-3">
                <div>
                  <h2 className="text-sm font-semibold">{t.popular}</h2>
                  <p className="mt-1 text-xs leading-5 text-slate-400">{t.sidebarHint}</p>
                </div>
                <button
                  className="inline-flex shrink-0 items-center gap-2 rounded-md bg-white px-3 py-2 text-xs font-semibold text-slate-950 transition hover:bg-cyan-50"
                  onClick={() => setLanguage(language === "zh" ? "en" : "zh")}
                >
                  <Languages size={15} />
                  {t.language}
                </button>
              </div>

              <div className="mt-4 grid max-h-[280px] gap-2 overflow-y-auto pr-1">
                {ecosystems.map((ecosystem) => (
                  <button
                    key={ecosystem.id}
                    className={`w-full rounded-md border p-3 text-left transition ${
                      selectedEcosystem.id === ecosystem.id
                        ? "border-cyan-400 bg-cyan-400/15"
                        : "border-white/10 bg-white/5 hover:border-white/25 hover:bg-white/10"
                    }`}
                    onClick={() => setSelectedEcosystemId(ecosystem.id)}
                  >
                    <div className="flex items-start justify-between gap-3">
                      <div className="min-w-0">
                        <p className="truncate font-semibold">{ecosystem.name}</p>
                        <p className="mt-1 truncate text-xs text-slate-400">{ecosystem.software}</p>
                      </div>
                      <Cpu className="shrink-0 text-cyan-300" size={18} />
                    </div>
                    {selectedEcosystem.id === ecosystem.id ? (
                      <div className="mt-3 rounded-md bg-slate-900/80 p-3 text-xs leading-5 text-slate-300">
                        {localize(ecosystem.regionStrength, language)}
                      </div>
                    ) : null}
                  </button>
                ))}
              </div>
            </section>

            <section className="flex min-h-0 flex-1 flex-col p-4">
              <div className="flex items-center gap-2">
                <MessageSquareText className="text-cyan-300" size={18} />
                <h2 className="text-sm font-semibold">{t.queryPanel}</h2>
              </div>
              <div className="mt-3 rounded-md border border-white/10 bg-white/5 p-3">
                <p className="text-sm font-semibold">{selectedEcosystem.name}</p>
                <p className="mt-2 text-xs leading-5 text-slate-400">{localize(selectedEcosystem.summary, language)}</p>
              </div>

              <div className="mt-3 min-h-0 flex-1 space-y-3 overflow-y-auto pr-1">
                {messages.map((message, index) => (
                  <ChatBubble key={`${message.role}-${index}`} message={message} language={language} labels={t} />
                ))}
              </div>

              <div className="mt-3">
                {draftError ? <p className="mb-2 text-xs font-medium text-amber-300">{draftError}</p> : null}
                <div className="flex gap-2">
                  <textarea
                    className="h-20 min-w-0 flex-1 resize-none rounded-md border border-white/10 bg-slate-900 p-3 text-sm text-white outline-none ring-cyan-400 placeholder:text-slate-500 focus:ring-2"
                    placeholder={t.askPlaceholder}
                    value={draft}
                    onChange={(event) => {
                      setDraft(event.target.value);
                      setDraftError("");
                    }}
                  />
                  <button
                    className="inline-flex w-12 items-center justify-center rounded-md bg-cyan-500 text-slate-950 transition hover:bg-cyan-400"
                    onClick={sendMessage}
                    aria-label={t.askButton}
                    title={t.askButton}
                  >
                    <Send size={18} />
                  </button>
                </div>
              </div>
            </section>
          </div>
        ) : (
          <CollapsedSidebar
            ecosystems={ecosystems}
            selectedEcosystemId={selectedEcosystem.id}
            onSelect={(id) => {
              setSelectedEcosystemId(id);
              setSidebarOpen(true);
            }}
          />
        )}
      </aside>

      <section className="min-w-0 flex-1 overflow-y-auto">
        <header className="border-b border-slate-200 bg-white px-5 py-5 lg:px-6">
          <div className="flex flex-col gap-4 xl:flex-row xl:items-center xl:justify-between">
            <div>
              <p className="text-xs font-semibold uppercase tracking-wide text-cyan-700">{t.appSubtitle}</p>
              <h2 className="mt-1 text-2xl font-semibold tracking-normal">{selectedEcosystem.name}</h2>
            </div>
            <div className="grid grid-cols-1 gap-3 text-sm sm:grid-cols-3">
              <Kpi label={t.effort} value={`${selectedProject.effortIndex}/100`} />
              <Kpi label={t.risk} value={selectedProject.riskLevel} />
              <Kpi label={t.status} value={selectedProject.status} />
            </div>
          </div>
        </header>

        <div className="grid gap-5 p-5 xl:grid-cols-[420px_minmax(0,1fr)] lg:p-6">
          <div className="space-y-5">
            <Panel title={t.projectList} description={t.projectListHint}>
              <div className="space-y-3">
                {projects.map((project) => (
                  <ProjectListItem
                    key={project.id}
                    project={project}
                    platform={ecosystems.find((item) => item.id === project.selectedPlatformId) ?? ecosystems[0]}
                    language={language}
                    active={project.id === selectedProject.id}
                    onClick={() => selectProject(project)}
                  />
                ))}
              </div>
            </Panel>

            <Panel title={t.currentThread} description={selectedEcosystem.name}>
              {relatedProjects.length > 0 ? (
                <div className="space-y-2">
                  {relatedProjects.map((project) => (
                    <button
                      key={project.id}
                      className="flex w-full items-center justify-between gap-3 rounded-md bg-slate-50 px-3 py-2 text-left text-sm transition hover:bg-cyan-50"
                      onClick={() => setSelectedProjectId(project.id)}
                    >
                      <span>{localize(project.title, language)}</span>
                      <ChevronRight size={16} className="shrink-0 text-slate-400" />
                    </button>
                  ))}
                </div>
              ) : (
                <p className="text-sm leading-6 text-slate-500">{t.noProject}</p>
              )}
            </Panel>
          </div>

          <div className="space-y-5">
            <ProjectResult project={selectedProject} platform={projectPlatform} language={language} labels={t} />
            <EcosystemBenchmark ecosystem={selectedEcosystem} language={language} labels={t} />
          </div>
        </div>
      </section>
    </main>
  );
}

function CollapsedSidebar({
  ecosystems,
  selectedEcosystemId,
  onSelect,
}: {
  ecosystems: PlcEcosystem[];
  selectedEcosystemId: string;
  onSelect: (id: string) => void;
}) {
  return (
    <div className="flex flex-1 flex-col items-center gap-3 overflow-y-auto py-4">
      {ecosystems.map((ecosystem) => (
        <button
          key={ecosystem.id}
          className={`rounded-md p-3 transition ${selectedEcosystemId === ecosystem.id ? "bg-cyan-400 text-slate-950" : "bg-white/10 text-white hover:bg-white/15"}`}
          onClick={() => onSelect(ecosystem.id)}
          title={ecosystem.name}
        >
          <Cpu size={20} />
        </button>
      ))}
    </div>
  );
}

function ChatBubble({ message, language, labels }: { message: ChatMessage; language: Language; labels: (typeof copy)[Language] }) {
  const isAssistant = message.role === "assistant";

  return (
    <div className={`rounded-md p-3 text-sm leading-6 ${isAssistant ? "bg-cyan-400/10 text-cyan-50" : "bg-white text-slate-900"}`}>
      <p className="mb-1 text-xs font-semibold opacity-70">{isAssistant ? labels.copilot : labels.you}</p>
      {localize(message.content, language)}
    </div>
  );
}

function ProjectListItem({
  project,
  platform,
  language,
  active,
  onClick,
}: {
  project: PlcProject;
  platform: PlcEcosystem;
  language: Language;
  active: boolean;
  onClick: () => void;
}) {
  return (
    <button
      className={`w-full rounded-md border p-4 text-left transition ${
        active ? "border-cyan-500 bg-cyan-50 shadow-sm" : "border-slate-200 bg-white hover:border-cyan-200 hover:bg-slate-50"
      }`}
      onClick={onClick}
    >
      <div className="flex items-start justify-between gap-3">
        <div className="min-w-0">
          <h3 className="font-semibold text-slate-950">{localize(project.title, language)}</h3>
          <p className="mt-1 text-sm text-slate-500">{localize(project.plant, language)}</p>
        </div>
        <span className={`shrink-0 rounded-full px-2 py-1 text-xs font-semibold ring-1 ${riskClass[project.riskLevel]}`}>{project.riskLevel}</span>
      </div>
      <div className="mt-3 flex items-center justify-between gap-3 text-xs text-slate-500">
        <span className="truncate">{platform.name}</span>
        <span className="shrink-0">{project.updatedAt}</span>
      </div>
    </button>
  );
}

function ProjectResult({
  project,
  platform,
  language,
  labels,
}: {
  project: PlcProject;
  platform: PlcEcosystem;
  language: Language;
  labels: (typeof copy)[Language];
}) {
  return (
    <Panel title={labels.decisionResult} description={localize(project.title, language)}>
      <div className="grid gap-4 lg:grid-cols-[1fr_280px]">
        <div>
          <InfoBlock title={labels.objective} body={localize(project.objective, language)} />
          <InfoBlock title={labels.recommendation} body={localize(project.recommendation, language)} highlight />
          <div className="mt-4 grid gap-4 md:grid-cols-2">
            <ListBlock title={labels.decisionFactors} items={project.decisionFactors.map((item) => localize(item, language))} icon={<Sparkles size={17} />} />
            <ListBlock title={labels.migrationNotes} items={project.migrationNotes.map((item) => localize(item, language))} icon={<AlertTriangle size={17} />} />
          </div>
        </div>
        <div className="rounded-md bg-slate-950 p-4 text-white">
          <p className="text-xs font-semibold uppercase tracking-wide text-cyan-300">{labels.selectedPlatform}</p>
          <h3 className="mt-2 text-xl font-semibold">{platform.name}</h3>
          <p className="mt-2 text-sm leading-6 text-slate-300">{localize(platform.summary, language)}</p>
          <div className="mt-5 space-y-3">
            <MetricBar label={labels.effort} value={project.effortIndex} />
            <MetricBar label="Productivity" value={platform.scores.productivity} />
            <MetricBar label="Openness" value={platform.scores.openness} />
          </div>
        </div>
      </div>
    </Panel>
  );
}

function EcosystemBenchmark({ ecosystem, language, labels }: { ecosystem: PlcEcosystem; language: Language; labels: (typeof copy)[Language] }) {
  const metrics = [
    ["Productivity", ecosystem.scores.productivity],
    ["Motion", ecosystem.scores.motion],
    ["Safety", ecosystem.scores.safety],
    ["Simulation", ecosystem.scores.simulation],
    ["Openness", ecosystem.scores.openness],
    ["Talent", ecosystem.scores.talent],
    ["Cost", ecosystem.scores.cost],
  ] as const;

  return (
    <Panel title={labels.benchmark} description={ecosystem.software}>
      <div className="grid gap-5 lg:grid-cols-[280px_1fr]">
        <div className="rounded-md bg-slate-50 p-4">
          <p className="text-sm font-semibold">{labels.summary}</p>
          <p className="mt-2 text-sm leading-6 text-slate-600">{localize(ecosystem.summary, language)}</p>
          <p className="mt-4 text-sm font-semibold">{labels.strengths}</p>
          <ul className="mt-2 list-disc space-y-1 pl-5 text-sm leading-6 text-slate-600">
            {ecosystem.strengths.map((item) => (
              <li key={localize(item, language)}>{localize(item, language)}</li>
            ))}
          </ul>
          <p className="mt-4 text-sm font-semibold">{labels.cautions}</p>
          <ul className="mt-2 list-disc space-y-1 pl-5 text-sm leading-6 text-slate-600">
            {ecosystem.cautions.map((item) => (
              <li key={localize(item, language)}>{localize(item, language)}</li>
            ))}
          </ul>
        </div>
        <div className="grid content-start gap-3">
          {metrics.map(([label, value]) => (
            <MetricBar key={label} label={label} value={value} />
          ))}
        </div>
      </div>
    </Panel>
  );
}

function Panel({ title, description, children }: { title: string; description?: string; children: React.ReactNode }) {
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

function InfoBlock({ title, body, highlight = false }: { title: string; body: string; highlight?: boolean }) {
  return (
    <div className={`rounded-md p-4 ${highlight ? "bg-cyan-50 text-cyan-950" : "bg-slate-50 text-slate-700"}`}>
      <p className="text-sm font-semibold text-slate-950">{title}</p>
      <p className="mt-2 text-sm leading-6">{body}</p>
    </div>
  );
}

function ListBlock({ title, items, icon }: { title: string; items: string[]; icon: React.ReactNode }) {
  return (
    <div className="rounded-md border border-slate-200 p-4">
      <div className="flex items-center gap-2 text-sm font-semibold">
        <span className="text-cyan-700">{icon}</span>
        {title}
      </div>
      <ul className="mt-3 list-disc space-y-2 pl-5 text-sm leading-6 text-slate-600">
        {items.map((item) => (
          <li key={item}>{item}</li>
        ))}
      </ul>
    </div>
  );
}

function Kpi({ label, value }: { label: string; value: string }) {
  return (
    <div className="rounded-md border border-slate-200 bg-slate-50 px-4 py-3">
      <p className="text-xs font-semibold uppercase tracking-wide text-slate-500">{label}</p>
      <p className="mt-1 text-lg font-semibold text-slate-950">{value}</p>
    </div>
  );
}

function MetricBar({ label, value }: { label: string; value: number }) {
  return (
    <div>
      <div className="mb-1 flex items-center justify-between gap-3 text-sm">
        <span className="font-medium">{label}</span>
        <span className="font-semibold text-cyan-700">{value}</span>
      </div>
      <div className="h-2.5 rounded-full bg-slate-200">
        <div className="h-2.5 rounded-full bg-cyan-600" style={{ width: `${value}%` }} />
      </div>
    </div>
  );
}
