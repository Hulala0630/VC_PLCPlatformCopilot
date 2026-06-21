import type { ChatMessage, PlcEcosystem, ProjectWorkspace, ReportSection } from "../types";

export const ecosystems: PlcEcosystem[] = [
  {
    id: "siemens-tia",
    name: "Siemens TIA Portal",
    vendor: "Siemens",
    software: "TIA Portal / SIMATIC",
    officialUrl: "https://www.siemens.com/en-us/products/tia-portal/",
    regionStrength: { zh: "欧洲与中国制造业基础强", en: "Strong base in Europe and China manufacturing" },
    summary: {
      zh: "适合标准化工厂、长期生命周期管理和大型组织的端到端自动化生态。",
      en: "End-to-end automation ecosystem for standardized plants, lifecycle management, and large organizations.",
    },
    strengths: [
      { zh: "安全、HMI、驱动和 PLC 生态完整", en: "Integrated safety, HMI, drives, and PLC ecosystem" },
      { zh: "工程团队与供应商资源丰富", en: "Strong engineering talent and supplier availability" },
      { zh: "适合集团级标准化", en: "Well suited for enterprise standardization" },
    ],
    cautions: [
      { zh: "授权和硬件成本偏高", en: "Licensing and hardware cost can be high" },
      { zh: "生态锁定风险中等偏高", en: "Medium-high ecosystem lock-in risk" },
    ],
    scores: { productivity: 84, motion: 78, safety: 90, simulation: 76, openness: 64, talent: 86, cost: 58 },
  },
  {
    id: "codesys",
    name: "CODESYS",
    vendor: "CODESYS Group / OEM",
    software: "CODESYS Development System",
    officialUrl: "https://www.codesys.com/products/engineering/",
    regionStrength: { zh: "跨厂商 OEM 与开放控制器生态", en: "Cross-vendor OEM and open controller ecosystem" },
    summary: {
      zh: "适合希望降低厂商绑定、采用多硬件策略或构建 OEM 控制平台的团队。",
      en: "Suited for teams reducing vendor lock-in, adopting multi-hardware strategies, or building OEM control platforms.",
    },
    strengths: [
      { zh: "开放性强，硬件选择广", en: "High openness with broad hardware choice" },
      { zh: "成本效率较好", en: "Good cost efficiency" },
      { zh: "IEC 61131-3 标准化体验", en: "Standard IEC 61131-3 engineering experience" },
    ],
    cautions: [
      { zh: "项目质量取决于具体硬件厂商", en: "Project quality depends on the selected hardware vendor" },
      { zh: "人才市场不如 Siemens/Rockwell 集中", en: "Talent market is less concentrated than Siemens/Rockwell" },
    ],
    scores: { productivity: 76, motion: 70, safety: 68, simulation: 72, openness: 93, talent: 60, cost: 86 },
  },
  {
    id: "twincat",
    name: "Beckhoff TwinCAT",
    vendor: "Beckhoff",
    software: "TwinCAT 3",
    officialUrl: "https://www.beckhoff.com/en-en/products/automation/twincat/",
    regionStrength: { zh: "高性能机器控制和 PC-based control", en: "High-performance machine control and PC-based control" },
    summary: {
      zh: "适合高速运动控制、软件定义自动化、虚拟调试和复杂机器控制项目。",
      en: "Suited for high-speed motion, software-defined automation, virtual commissioning, and complex machine control.",
    },
    strengths: [
      { zh: "运动控制与实时性能强", en: "Strong motion control and real-time performance" },
      { zh: "软件架构开放，适合高级工程团队", en: "Open software architecture for advanced engineering teams" },
      { zh: "与仿真和数字孪生结合空间大", en: "Good fit for simulation and digital twin workflows" },
    ],
    cautions: [
      { zh: "学习曲线较陡", en: "Steeper learning curve" },
      { zh: "对团队软件工程能力要求高", en: "Requires stronger software engineering capability" },
    ],
    scores: { productivity: 80, motion: 96, safety: 78, simulation: 86, openness: 90, talent: 64, cost: 77 },
  },
  {
    id: "rockwell",
    name: "Rockwell Studio 5000",
    vendor: "Rockwell Automation",
    software: "Studio 5000 / ControlLogix",
    officialUrl: "https://www.rockwellautomation.com/en-us/products/software/factorytalk/designsuite/studio-5000.html",
    regionStrength: { zh: "北美大型工厂与资产密集型行业", en: "Large North American plants and asset-intensive industries" },
    summary: {
      zh: "适合北美装机基础、大型产线、过程与离散混合自动化场景。",
      en: "Suited for North American installed bases, large production lines, and hybrid process-discrete automation.",
    },
    strengths: [
      { zh: "大型控制系统扩展能力强", en: "Strong scalability for large control systems" },
      { zh: "安全与工业网络生态成熟", en: "Mature safety and industrial network ecosystem" },
      { zh: "北美工程与维护资源丰富", en: "Strong North American engineering and maintenance resources" },
    ],
    cautions: [
      { zh: "总体拥有成本偏高", en: "Higher total cost of ownership" },
      { zh: "跨生态迁移成本较高", en: "Higher cross-ecosystem migration cost" },
    ],
    scores: { productivity: 77, motion: 80, safety: 87, simulation: 70, openness: 58, talent: 78, cost: 54 },
  },
  {
    id: "mitsubishi",
    name: "Mitsubishi GX Works",
    vendor: "Mitsubishi Electric",
    software: "GX Works / MELSEC",
    officialUrl: "https://www.mitsubishielectric.com/fa/products/cnt/plceng/smerit/gx_works3/",
    regionStrength: { zh: "亚洲设备制造与离散自动化", en: "Asian machine building and discrete automation" },
    summary: {
      zh: "适合成本敏感、设备制造导向、亚洲供应链强相关的项目。",
      en: "Suited for cost-sensitive, machine-builder-oriented projects tied to Asian supply chains.",
    },
    strengths: [
      { zh: "硬件稳定，设备制造应用广", en: "Stable hardware with broad machine-building adoption" },
      { zh: "成本与交付周期有竞争力", en: "Competitive cost and delivery profile" },
    ],
    cautions: [
      { zh: "高级软件生态和开放集成不如 TwinCAT/CODESYS", en: "Advanced software ecosystem and openness trail TwinCAT/CODESYS" },
    ],
    scores: { productivity: 72, motion: 74, safety: 70, simulation: 62, openness: 55, talent: 66, cost: 82 },
  },
  {
    id: "omron",
    name: "Omron Sysmac",
    vendor: "Omron",
    software: "Sysmac Studio",
    officialUrl: "https://automation.omron.com/en/us/products/family/SYSSTDIO",
    regionStrength: { zh: "机器自动化、视觉和运动控制集成", en: "Machine automation, vision, and motion integration" },
    summary: {
      zh: "适合机器自动化、运动控制、视觉检测与紧凑型产线控制。",
      en: "Suited for machine automation, motion control, vision inspection, and compact line control.",
    },
    strengths: [
      { zh: "运动、视觉与控制集成体验好", en: "Good integrated motion, vision, and control experience" },
      { zh: "适合中小型机器控制项目", en: "Good fit for small and mid-sized machine control" },
    ],
    cautions: [
      { zh: "大型企业级生态覆盖不如 Siemens/Rockwell", en: "Enterprise ecosystem coverage trails Siemens/Rockwell" },
    ],
    scores: { productivity: 74, motion: 82, safety: 75, simulation: 68, openness: 60, talent: 62, cost: 74 },
  },
];

function preferences(weights: Record<string, number>) {
  return ecosystems.map((platform) => ({
    platformId: platform.id,
    preferenceWeight: weights[platform.id] ?? 50,
    userReasonNote: "",
  }));
}

export function reportSections(projectName: string): ReportSection[] {
  const now = "2026-05-27";
  return [
    {
      id: "executive-summary",
      title: { zh: "执行摘要", en: "Executive Summary" },
      body: {
        zh: `${projectName} 当前处于基于 mock 数据的决策草稿阶段。建议先完善输入资料，再形成正式推荐结论。`,
        en: `${projectName} is currently in a mock-data decision draft stage. Complete the inputs before issuing a formal recommendation.`,
      },
      assumptions: [{ zh: "当前未解析附件内容。", en: "Attachment content is not parsed in this version." }],
      uncertainty: { zh: "完整性取决于人工录入的信息质量。", en: "Confidence depends on the quality of manually entered inputs." },
      dataSourcesUsed: [{ zh: "项目 Intake", en: "Project intake" }, { zh: "平台 mock profile", en: "Mock platform profiles" }],
      lastGeneratedAt: now,
    },
    {
      id: "project-inputs",
      title: { zh: "项目输入", en: "Project Inputs" },
      body: {
        zh: "报告将汇总行业、目标、I/O 规模、运动/安全需求、团队经验和候选平台。",
        en: "The report summarizes industry, goal, I/O scale, motion/safety needs, team experience, and candidate platforms.",
      },
      assumptions: [{ zh: "输入由用户手动维护。", en: "Inputs are maintained manually by the user." }],
      uncertainty: { zh: "未填写字段会降低建议可靠性。", en: "Unfilled fields reduce recommendation reliability." },
      dataSourcesUsed: [{ zh: "Intake 表单", en: "Intake form" }],
      lastGeneratedAt: now,
    },
    {
      id: "platform-benchmark",
      title: { zh: "平台基准对比", en: "Platform Benchmark" },
      body: {
        zh: "平台排序由技术评分和用户倾向权重共同决定。",
        en: "Platform ranking is determined by technical scores and user preference weights.",
      },
      assumptions: [{ zh: "基础平台评分来自 mock profile。", en: "Base platform scores come from mock profiles." }],
      uncertainty: { zh: "真实项目还需要供应商报价、交期与现场约束。", en: "A real project still needs vendor quotes, lead times, and site constraints." },
      dataSourcesUsed: [{ zh: "平台评分库", en: "Platform scoring library" }, { zh: "偏好滑块", en: "Preference sliders" }],
      lastGeneratedAt: now,
    },
    {
      id: "preference-impact",
      title: { zh: "倾向性影响", en: "Preference Impact" },
      body: {
        zh: "用户可对曾经使用过、客户指定、团队熟悉、供应链稳定或成本原因相关的平台设置更高倾向权重。",
        en: "Users can assign higher preference weights for prior use, customer mandate, team familiarity, supply stability, or cost reasons.",
      },
      assumptions: [{ zh: "倾向性是决策输入，不替代技术评分。", en: "Preference is a decision input and does not replace technical scoring." }],
      uncertainty: { zh: "倾向原因需要在正式决策前确认。", en: "Preference reasons should be confirmed before a formal decision." },
      dataSourcesUsed: [{ zh: "用户倾向原因", en: "User preference reasons" }],
      lastGeneratedAt: now,
    },
    {
      id: "risk-assessment",
      title: { zh: "风险评估", en: "Risk Assessment" },
      body: {
        zh: "风险由平台开放性、团队经验、迁移复杂度和资料完整度初步判断。",
        en: "Risk is initially estimated from openness, team experience, migration complexity, and input completeness.",
      },
      assumptions: [{ zh: "风险等级为自动化初判。", en: "Risk level is an automated first-pass estimate." }],
      uncertainty: { zh: "未接入真实采购、维护和合规数据。", en: "Real procurement, maintenance, and compliance data is not connected." },
      dataSourcesUsed: [{ zh: "Benchmark 排名", en: "Benchmark ranking" }, { zh: "项目约束", en: "Project constraints" }],
      lastGeneratedAt: now,
    },
    {
      id: "roadmap",
      title: { zh: "迁移与实施路线图", en: "Migration / Implementation Roadmap" },
      body: {
        zh: "建议按资料审计、平台确认、试点验证、模板化、上线切换的顺序推进。",
        en: "Recommended sequence: input audit, platform confirmation, pilot validation, template standardization, and rollout cutover.",
      },
      assumptions: [{ zh: "路线图会在接入真实估算模型后细化。", en: "Roadmap will be refined after real estimation models are connected." }],
      uncertainty: { zh: "当前不包含真实工期与资源负载估算。", en: "Current draft does not include real schedule or resourcing estimates." },
      dataSourcesUsed: [{ zh: "项目目标", en: "Project goal" }, { zh: "风险评估", en: "Risk assessment" }],
      lastGeneratedAt: now,
    },
    {
      id: "assumptions",
      title: { zh: "假设与不确定性", en: "Assumptions & Uncertainty" },
      body: {
        zh: "当前版本不解析附件、不调用真实 AI、不连接 PLC。所有结论用于早期决策讨论。",
        en: "This version does not parse attachments, call real AI, or connect to PLCs. All conclusions are for early decision discussion.",
      },
      assumptions: [{ zh: "关键假设需要用户确认。", en: "Key assumptions require user confirmation." }],
      uncertainty: { zh: "正式推荐前需要补充真实工程、成本和交付数据。", en: "Formal recommendation requires real engineering, cost, and delivery data." },
      dataSourcesUsed: [{ zh: "用户输入", en: "User input" }, { zh: "Mock 评分模型", en: "Mock scoring model" }],
      lastGeneratedAt: now,
    },
  ];
}

export const workspaces: ProjectWorkspace[] = [
  {
    project: {
      id: "test-migration-project",
      name: "测试迁移项目",
      industry: "Automotive",
      goal: "评估既有 PLC 平台迁移路径、供应链稳定性和实施风险。",
      status: "Draft",
      createdAt: "2026-05-30",
      updatedAt: "2026-05-30",
    },
    intake: {
      projectSize: "Medium",
      ioScale: 620,
      motionRequirement: 64,
      safetyRequirement: 78,
      budgetSensitivity: 66,
      teamExperience: "Team familiar with Siemens and CODESYS; limited Rockwell maintenance experience.",
      existingPlatform: "siemens-tia",
      candidatePlatforms: ["siemens-tia", "codesys", "twincat"],
      constraints: "Customer expects stable supply chain, reusable standards, and low migration disruption.",
    },
    preferences: preferences({ "siemens-tia": 78, codesys: 72, twincat: 58, rockwell: 35, mitsubishi: 42, omron: 46 }),
    attachments: [
      {
        id: "att-test-io",
        projectId: "test-migration-project",
        fileName: "Test_Project_IO_List.xlsx",
        fileType: "I/O List",
        declaredPurpose: "Baseline I/O count and cabinet planning reference",
        uploadedAt: "2026-05-30",
      },
    ],
    report: { projectId: "test-migration-project", sections: reportSections("测试迁移项目"), version: 1, status: "Draft" },
  },
  {
    project: {
      id: "ev-line-standardization",
      name: "新能源电池产线 PLC 标准化",
      industry: "Battery Manufacturing",
      goal: "统一新产线 PLC 平台，并兼顾长期维护、供应商资源和安全标准。",
      status: "Report Ready",
      createdAt: "2026-05-17",
      updatedAt: "2026-05-27",
    },
    intake: {
      projectSize: "Large",
      ioScale: 1800,
      motionRequirement: 58,
      safetyRequirement: 86,
      budgetSensitivity: 52,
      teamExperience: "Siemens maintenance team with limited TwinCAT experience",
      existingPlatform: "siemens-tia",
      candidatePlatforms: ["siemens-tia", "twincat", "codesys", "rockwell"],
      constraints: "Group standardization, spare-parts stability, safety approval, supplier availability.",
    },
    preferences: preferences({ "siemens-tia": 85, twincat: 55, codesys: 45, rockwell: 60, mitsubishi: 30, omron: 35 }),
    attachments: [
      {
        id: "att-io-list",
        projectId: "ev-line-standardization",
        fileName: "Battery_Line_IO_List.xlsx",
        fileType: "I/O List",
        declaredPurpose: "I/O scale and cabinet planning reference",
        uploadedAt: "2026-05-27",
      },
      {
        id: "att-standard",
        projectId: "ev-line-standardization",
        fileName: "Group_Automation_Standard.pdf",
        fileType: "Requirements",
        declaredPurpose: "Internal PLC standard and safety requirements",
        uploadedAt: "2026-05-27",
      },
    ],
    report: { projectId: "ev-line-standardization", sections: reportSections("新能源电池产线 PLC 标准化"), version: 1, status: "Ready" },
  },
  {
    project: {
      id: "high-speed-packaging",
      name: "高速包装机平台选型",
      industry: "Machine Building",
      goal: "选择适合高速运动控制、视觉同步和虚拟调试的控制平台。",
      status: "Analyzing",
      createdAt: "2026-05-16",
      updatedAt: "2026-05-27",
    },
    intake: {
      projectSize: "Medium",
      ioScale: 420,
      motionRequirement: 94,
      safetyRequirement: 72,
      budgetSensitivity: 58,
      teamExperience: "Strong software team, moderate Siemens background",
      existingPlatform: "siemens-tia",
      candidatePlatforms: ["twincat", "codesys", "siemens-tia", "omron"],
      constraints: "High-speed motion, virtual commissioning, reusable machine template.",
    },
    preferences: preferences({ "siemens-tia": 52, twincat: 88, codesys: 65, rockwell: 25, mitsubishi: 45, omron: 62 }),
    attachments: [
      {
        id: "att-sequence",
        projectId: "high-speed-packaging",
        fileName: "Packaging_Machine_Function_Target.docx",
        fileType: "Requirements",
        declaredPurpose: "Machine sequence and target throughput",
        uploadedAt: "2026-05-27",
      },
    ],
    report: { projectId: "high-speed-packaging", sections: reportSections("高速包装机平台选型"), version: 1, status: "Draft" },
  },
];

export const initialMessages: Record<string, ChatMessage[]> = {
  "siemens-tia": [
    {
      role: "assistant",
      content: {
        zh: "Siemens 适合重视标准化、长期维护和安全生态深度的项目。建议先补充项目规模、I/O 点数和现有装机基础。",
        en: "Siemens fits projects that value standardization, long-term maintenance, and safety ecosystem depth. Add project size, I/O count, and installed base.",
      },
    },
  ],
  codesys: [
    {
      role: "assistant",
      content: {
        zh: "CODESYS 适合开放硬件策略和 OEM 控制器路线。需要确认硬件供应商、认证路径和维护责任边界。",
        en: "CODESYS fits open hardware strategies and OEM controller roadmaps. Confirm hardware vendor, certification path, and maintenance ownership.",
      },
    },
  ],
  twincat: [
    {
      role: "assistant",
      content: {
        zh: "TwinCAT 对高速运动、虚拟调试和软件定义自动化很有吸引力。关键是团队软件工程能力。",
        en: "TwinCAT is attractive for high-speed motion, virtual commissioning, and software-defined automation. Team software capability is the key factor.",
      },
    },
  ],
};
