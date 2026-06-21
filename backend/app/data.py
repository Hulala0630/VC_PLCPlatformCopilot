from app.models import (
    LocalizedText,
    PlatformPreference,
    PlatformScores,
    PlcEcosystem,
    Project,
    ProjectAttachment,
    ProjectIntake,
    ProjectWorkspace,
    ReportDraft,
    ReportSection,
)


ECOSYSTEMS: list[PlcEcosystem] = [
    PlcEcosystem(
        id="siemens-tia",
        name="Siemens TIA Portal",
        vendor="Siemens",
        software="TIA Portal / SIMATIC",
        official_url="https://www.siemens.com/en-us/products/tia-portal/",
        region_strength=LocalizedText(zh="欧洲、中国及大型制造业基础强", en="Strong base in Europe, China, and large manufacturing"),
        summary=LocalizedText(
            zh="适合标准化工厂、长期生命周期管理和大型组织的端到端自动化生态。",
            en="End-to-end automation ecosystem for standardized plants, lifecycle management, and large organizations.",
        ),
        strengths=[
            LocalizedText(zh="安全、HMI、驱动和 PLC 生态完整", en="Integrated safety, HMI, drives, and PLC ecosystem"),
            LocalizedText(zh="工程团队和供应商资源丰富", en="Strong engineering talent and supplier availability"),
        ],
        cautions=[
            LocalizedText(zh="授权和硬件成本偏高", en="Licensing and hardware cost can be high"),
            LocalizedText(zh="生态锁定风险中等偏高", en="Medium-high ecosystem lock-in risk"),
        ],
        scores=PlatformScores(productivity=84, motion=78, safety=90, simulation=76, openness=64, talent=86, cost=58),
    ),
    PlcEcosystem(
        id="codesys",
        name="CODESYS",
        vendor="CODESYS Group / OEM",
        software="CODESYS Development System",
        official_url="https://www.codesys.com/products/engineering/",
        region_strength=LocalizedText(zh="跨厂商 OEM 与开放控制器生态", en="Cross-vendor OEM and open controller ecosystem"),
        summary=LocalizedText(
            zh="适合开放硬件策略、多硬件路线和 OEM 控制平台。",
            en="Suited for open hardware strategies, multi-hardware roadmaps, and OEM control platforms.",
        ),
        strengths=[
            LocalizedText(zh="开放性强，硬件选择广", en="High openness with broad hardware choice"),
            LocalizedText(zh="成本效率较好", en="Good cost efficiency"),
        ],
        cautions=[
            LocalizedText(zh="项目质量取决于具体硬件厂商", en="Project quality depends on the selected hardware vendor"),
            LocalizedText(zh="人才市场不如 Siemens/Rockwell 集中", en="Talent market is less concentrated than Siemens/Rockwell"),
        ],
        scores=PlatformScores(productivity=76, motion=70, safety=68, simulation=72, openness=93, talent=60, cost=86),
    ),
    PlcEcosystem(
        id="twincat",
        name="Beckhoff TwinCAT",
        vendor="Beckhoff",
        software="TwinCAT 3",
        official_url="https://www.beckhoff.com/en-en/products/automation/twincat/",
        region_strength=LocalizedText(zh="高性能机器控制与 PC-based control", en="High-performance machine control and PC-based control"),
        summary=LocalizedText(
            zh="适合高速运动控制、虚拟调试和软件定义自动化。",
            en="Suited for high-speed motion, virtual commissioning, and software-defined automation.",
        ),
        strengths=[
            LocalizedText(zh="运动控制与实时性能强", en="Strong motion control and real-time performance"),
            LocalizedText(zh="软件架构开放", en="Open software architecture"),
        ],
        cautions=[
            LocalizedText(zh="学习曲线较陡", en="Steeper learning curve"),
            LocalizedText(zh="对团队软件工程能力要求高", en="Requires stronger software engineering capability"),
        ],
        scores=PlatformScores(productivity=80, motion=96, safety=78, simulation=86, openness=90, talent=64, cost=77),
    ),
    PlcEcosystem(
        id="rockwell",
        name="Rockwell Studio 5000",
        vendor="Rockwell Automation",
        software="Studio 5000 / ControlLogix",
        official_url="https://www.rockwellautomation.com/en-us/products/software/factorytalk/designsuite/studio-5000.html",
        region_strength=LocalizedText(zh="北美大型工厂与资产密集型行业", en="Large North American plants and asset-intensive industries"),
        summary=LocalizedText(
            zh="适合北美装机基础、大型产线和混合自动化场景。",
            en="Suited for North American installed bases, large production lines, and hybrid automation.",
        ),
        strengths=[
            LocalizedText(zh="大型控制系统扩展能力强", en="Strong scalability for large control systems"),
            LocalizedText(zh="安全与工业网络生态成熟", en="Mature safety and industrial network ecosystem"),
        ],
        cautions=[
            LocalizedText(zh="总体拥有成本偏高", en="Higher total cost of ownership"),
            LocalizedText(zh="跨生态迁移成本较高", en="Higher cross-ecosystem migration cost"),
        ],
        scores=PlatformScores(productivity=77, motion=80, safety=87, simulation=70, openness=58, talent=78, cost=54),
    ),
    PlcEcosystem(
        id="mitsubishi",
        name="Mitsubishi GX Works",
        vendor="Mitsubishi Electric",
        software="GX Works / MELSEC",
        official_url="https://www.mitsubishielectric.com/fa/products/cnt/plceng/smerit/gx_works3/",
        region_strength=LocalizedText(zh="亚洲设备制造与离散自动化", en="Asian machine building and discrete automation"),
        summary=LocalizedText(
            zh="适合成本敏感、设备制造导向和亚洲供应链强相关的项目。",
            en="Suited for cost-sensitive, machine-builder-oriented projects tied to Asian supply chains.",
        ),
        strengths=[
            LocalizedText(zh="硬件稳定，设备制造应用广", en="Stable hardware with broad machine-building adoption"),
            LocalizedText(zh="成本与交付周期有竞争力", en="Competitive cost and delivery profile"),
        ],
        cautions=[
            LocalizedText(zh="高级软件生态和开放集成弱于 TwinCAT/CODESYS", en="Advanced software ecosystem and openness trail TwinCAT/CODESYS"),
        ],
        scores=PlatformScores(productivity=72, motion=74, safety=70, simulation=62, openness=55, talent=66, cost=82),
    ),
    PlcEcosystem(
        id="omron",
        name="Omron Sysmac",
        vendor="Omron",
        software="Sysmac Studio",
        official_url="https://automation.omron.com/en/us/products/family/SYSSTDIO",
        region_strength=LocalizedText(zh="机器自动化、视觉和运动控制集成", en="Machine automation, vision, and motion integration"),
        summary=LocalizedText(
            zh="适合机器自动化、运动控制、视觉检测与紧凑型产线控制。",
            en="Suited for machine automation, motion control, vision inspection, and compact line control.",
        ),
        strengths=[
            LocalizedText(zh="运动、视觉与控制集成体验好", en="Good integrated motion, vision, and control experience"),
            LocalizedText(zh="适合中小型机器控制项目", en="Good fit for small and mid-sized machine control"),
        ],
        cautions=[
            LocalizedText(zh="大型企业级生态覆盖不如 Siemens/Rockwell", en="Enterprise ecosystem coverage trails Siemens/Rockwell"),
        ],
        scores=PlatformScores(productivity=74, motion=82, safety=75, simulation=68, openness=60, talent=62, cost=74),
    ),
]


def _preferences(weights: dict[str, int]) -> list[PlatformPreference]:
    return [
        PlatformPreference(platform_id=platform.id, preference_weight=weights.get(platform.id, 50))
        for platform in ECOSYSTEMS
    ]


def _report_sections(project_name: str, generated_at: str = "2026-05-27") -> list[ReportSection]:
    return [
        ReportSection(
            id="executive-summary",
            title=LocalizedText(zh="执行摘要", en="Executive Summary"),
            body=LocalizedText(
                zh=f"{project_name} 当前处于 mock 数据决策草稿阶段，建议先完善输入资料再发布正式推荐。",
                en=f"{project_name} is in a mock-data decision draft stage. Complete inputs before issuing a formal recommendation.",
            ),
            assumptions=[LocalizedText(zh="当前仅登记附件元信息，不解析文件内容。", en="Attachments are metadata-only and not parsed.")],
            last_generated_at=generated_at,
        ),
        ReportSection(
            id="project-inputs",
            title=LocalizedText(zh="项目输入", en="Project Inputs"),
            body=LocalizedText(
                zh="报告汇总行业、目标、I/O 规模、运动与安全需求、团队经验和候选平台。",
                en="The report summarizes industry, goal, I/O scale, motion and safety needs, team experience, and candidate platforms.",
            ),
            assumptions=[LocalizedText(zh="输入由用户手动维护。", en="Inputs are maintained manually by the user.")],
            last_generated_at=generated_at,
        ),
        ReportSection(
            id="platform-benchmark",
            title=LocalizedText(zh="平台基准对比", en="Platform Benchmark"),
            body=LocalizedText(
                zh="平台排序由技术评分和用户倾向权重共同决定。",
                en="Platform ranking is determined by technical scores and user preference weights.",
            ),
            assumptions=[LocalizedText(zh="基础平台评分来自 mock profile。", en="Base platform scores come from mock profiles.")],
            last_generated_at=generated_at,
        ),
    ]


PROJECT_WORKSPACES: list[ProjectWorkspace] = [
    ProjectWorkspace(
        project=Project(
            id="ev-line-standardization",
            name="新能源电池产线 PLC 标准化",
            industry="Battery Manufacturing",
            goal="统一新产线 PLC 平台，并兼顾长期维护、供应商资源和安全标准。",
            status="Report Ready",
            created_at="2026-05-17",
            updated_at="2026-05-27",
        ),
        intake=ProjectIntake(
            project_size="Large",
            io_scale=1800,
            motion_requirement=58,
            safety_requirement=86,
            budget_sensitivity=52,
            team_experience="Siemens maintenance team with limited TwinCAT experience",
            existing_platform="siemens-tia",
            candidate_platforms=["siemens-tia", "twincat", "codesys", "rockwell"],
            constraints="Group standardization, spare-parts stability, safety approval, supplier availability.",
        ),
        preferences=_preferences({"siemens-tia": 85, "twincat": 55, "codesys": 45, "rockwell": 60, "mitsubishi": 30, "omron": 35}),
        attachments=[
            ProjectAttachment(
                id="att-io-list",
                project_id="ev-line-standardization",
                file_name="Battery_Line_IO_List.xlsx",
                file_type="I/O List",
                declared_purpose="I/O scale and cabinet planning reference",
                uploaded_at="2026-05-27",
            ),
            ProjectAttachment(
                id="att-standard",
                project_id="ev-line-standardization",
                file_name="Group_Automation_Standard.pdf",
                file_type="Requirements",
                declared_purpose="Internal PLC standard and safety requirements",
                uploaded_at="2026-05-27",
            ),
        ],
        report=ReportDraft(project_id="ev-line-standardization", sections=_report_sections("新能源电池产线 PLC 标准化"), version=1, status="Ready"),
    ),
    ProjectWorkspace(
        project=Project(
            id="high-speed-packaging",
            name="高速包装机平台选型",
            industry="Machine Building",
            goal="选择适合高速运动控制、视觉同步和虚拟调试的控制平台。",
            status="Analyzing",
            created_at="2026-05-16",
            updated_at="2026-05-27",
        ),
        intake=ProjectIntake(
            project_size="Medium",
            io_scale=420,
            motion_requirement=94,
            safety_requirement=72,
            budget_sensitivity=58,
            team_experience="Strong software team, moderate Siemens background",
            existing_platform="siemens-tia",
            candidate_platforms=["twincat", "codesys", "siemens-tia", "omron"],
            constraints="High-speed motion, virtual commissioning, reusable machine template.",
        ),
        preferences=_preferences({"siemens-tia": 52, "twincat": 88, "codesys": 65, "rockwell": 25, "mitsubishi": 45, "omron": 62}),
        attachments=[
            ProjectAttachment(
                id="att-sequence",
                project_id="high-speed-packaging",
                file_name="Packaging_Machine_Function_Target.docx",
                file_type="Requirements",
                declared_purpose="Machine sequence and target throughput",
                uploaded_at="2026-05-27",
            ),
        ],
        report=ReportDraft(project_id="high-speed-packaging", sections=_report_sections("高速包装机平台选型"), version=1, status="Draft"),
    ),
]
