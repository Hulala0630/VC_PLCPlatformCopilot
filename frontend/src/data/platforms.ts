import type { ChatMessage, PlcEcosystem, PlcProject } from "../types";

export const ecosystems: PlcEcosystem[] = [
  {
    id: "siemens-tia",
    name: "Siemens TIA Portal",
    vendor: "Siemens",
    software: "TIA Portal / SIMATIC",
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
      { zh: "高阶软件生态和开放集成不如 TwinCAT/CODESYS", en: "Advanced software ecosystem and openness trail TwinCAT/CODESYS" },
    ],
    scores: { productivity: 72, motion: 74, safety: 70, simulation: 62, openness: 55, talent: 66, cost: 82 },
  },
  {
    id: "omron",
    name: "Omron Sysmac",
    vendor: "Omron",
    software: "Sysmac Studio",
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

export const initialMessages: Record<string, ChatMessage[]> = {
  "siemens-tia": [
    {
      role: "assistant",
      content: {
        zh: "如果你的目标是集团标准化、长期维护和供应链稳定，Siemens TIA Portal 是强候选。请告诉我项目规模、I/O 点数和现有装机基础。",
        en: "If your goal is enterprise standardization, long-term maintenance, and supply-chain stability, Siemens TIA Portal is a strong candidate. Tell me project size, I/O count, and installed base.",
      },
    },
  ],
  codesys: [
    {
      role: "assistant",
      content: {
        zh: "CODESYS 更适合开放硬件策略和 OEM 控制器路线。我们需要确认安全认证、供应商责任边界和长期维护团队能力。",
        en: "CODESYS fits open hardware strategies and OEM controller roadmaps. We should confirm safety certification, supplier responsibility boundaries, and long-term maintenance capability.",
      },
    },
  ],
  twincat: [
    {
      role: "assistant",
      content: {
        zh: "TwinCAT 对高速运动、虚拟调试和软件定义自动化很有吸引力。关键问题是团队是否具备足够的软件工程能力。",
        en: "TwinCAT is attractive for high-speed motion, virtual commissioning, and software-defined automation. The key question is whether the team has enough software engineering capability.",
      },
    },
  ],
  rockwell: [
    {
      role: "assistant",
      content: {
        zh: "Rockwell 适合北美装机基础和大型产线。迁移评估时需要特别关注 TCO、授权、备件和停机窗口。",
        en: "Rockwell fits North American installed bases and large lines. Migration assessment should focus on TCO, licensing, spare parts, and downtime windows.",
      },
    },
  ],
  mitsubishi: [
    {
      role: "assistant",
      content: {
        zh: "Mitsubishi 常见于亚洲设备制造场景。适合成本敏感项目，但需要评估开放集成、仿真和长期平台战略。",
        en: "Mitsubishi is common in Asian machine-building contexts. It fits cost-sensitive projects, but openness, simulation, and long-term platform strategy need review.",
      },
    },
  ],
  omron: [
    {
      role: "assistant",
      content: {
        zh: "Omron Sysmac 对运动、视觉和紧凑型机器控制友好。我们可以重点评估机器节拍、视觉检测和维护团队经验。",
        en: "Omron Sysmac is friendly for motion, vision, and compact machine control. We can focus on machine takt, vision inspection, and maintenance team experience.",
      },
    },
  ],
};

export const projects: PlcProject[] = [
  {
    id: "ev-line-standardization",
    title: { zh: "新能源电池产线 PLC 标准化", en: "EV Battery Line PLC Standardization" },
    plant: { zh: "华东新工厂", en: "East China Greenfield Plant" },
    selectedPlatformId: "siemens-tia",
    status: "Decision Ready",
    updatedAt: "2026-05-17",
    objective: {
      zh: "在集团新产线中统一 PLC 平台，并兼顾长期维护、供应商资源和安全标准。",
      en: "Standardize the PLC platform for new group production lines while balancing maintenance, supplier availability, and safety standards.",
    },
    recommendation: {
      zh: "建议优先采用 Siemens TIA Portal。主要理由是组织已有 Siemens 维护基础，安全与 HMI 生态完整，供应商资源更容易统一。",
      en: "Recommend Siemens TIA Portal first. The organization already has Siemens maintenance capability, the safety/HMI ecosystem is integrated, and supplier alignment is easier.",
    },
    decisionFactors: [
      { zh: "集团标准化收益高", en: "High enterprise standardization value" },
      { zh: "维护与备件体系成熟", en: "Mature maintenance and spare-parts ecosystem" },
      { zh: "迁移风险中等，可通过试点产线降低", en: "Medium migration risk, reducible through a pilot line" },
    ],
    migrationNotes: [
      { zh: "先完成 I/O 清单和 HMI 标签审计", en: "Audit I/O list and HMI tags first" },
      { zh: "将安全回路和停机窗口作为关键约束", en: "Treat safety loops and downtime windows as key constraints" },
    ],
    riskLevel: "Medium",
    effortIndex: 58,
  },
  {
    id: "high-speed-packaging",
    title: { zh: "高速包装机平台选型", en: "High-Speed Packaging Machine Selection" },
    plant: { zh: "OEM 设备项目", en: "OEM Machine Project" },
    selectedPlatformId: "twincat",
    status: "Reviewed",
    updatedAt: "2026-05-16",
    objective: {
      zh: "选择适合高速运动控制、视觉同步和虚拟调试的控制平台。",
      en: "Select a control platform for high-speed motion, vision synchronization, and virtual commissioning.",
    },
    recommendation: {
      zh: "建议优先评估 TwinCAT。它在实时性能、运动控制和软件开放性方面更适合该机器类型。",
      en: "Recommend evaluating TwinCAT first. It better fits this machine type through real-time performance, motion control, and software openness.",
    },
    decisionFactors: [
      { zh: "运动控制需求高", en: "High motion-control requirement" },
      { zh: "软件团队能力较强", en: "Strong software engineering team" },
      { zh: "虚拟调试价值明显", en: "Clear virtual commissioning value" },
    ],
    migrationNotes: [
      { zh: "需要建立 TwinCAT 工程模板", en: "Create a TwinCAT engineering template" },
      { zh: "需要定义实时任务、轴组和仿真接口规范", en: "Define real-time tasks, axis groups, and simulation interfaces" },
    ],
    riskLevel: "Medium",
    effortIndex: 63,
  },
  {
    id: "cost-sensitive-oem",
    title: { zh: "成本敏感型 OEM 控制器策略", en: "Cost-Sensitive OEM Controller Strategy" },
    plant: { zh: "出口设备产品线", en: "Export Machine Product Line" },
    selectedPlatformId: "codesys",
    status: "Draft",
    updatedAt: "2026-05-15",
    objective: {
      zh: "降低硬件绑定与整体成本，同时保持 IEC 61131-3 工程体验。",
      en: "Reduce hardware lock-in and total cost while keeping an IEC 61131-3 engineering experience.",
    },
    recommendation: {
      zh: "建议以 CODESYS 作为开放控制平台候选，但需建立硬件供应商认证清单和维护责任边界。",
      en: "Recommend CODESYS as an open control-platform candidate, with a certified hardware supplier list and clear maintenance responsibility boundaries.",
    },
    decisionFactors: [
      { zh: "开放性和成本效率强", en: "Strong openness and cost efficiency" },
      { zh: "供应商质量差异需要管理", en: "Supplier quality variance must be managed" },
      { zh: "安全认证路径需要提前确认", en: "Safety certification path must be confirmed early" },
    ],
    migrationNotes: [
      { zh: "先选定目标硬件族，再做软件模板", en: "Select target hardware family before software templates" },
      { zh: "建立跨硬件回归测试", en: "Create cross-hardware regression tests" },
    ],
    riskLevel: "Low",
    effortIndex: 44,
  },
];
