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
        region_strength=LocalizedText(zh="欧洲与中国制造业基础强", en="Strong base in Europe and China manufacturing"),
        summary=LocalizedText(zh="适合标准化工厂、长期生命周期管理和大型组织的端到端自动化生态。", en="End-to-end automation ecosystem for standardized plants, lifecycle management, and large organizations."),
        strengths=[
            LocalizedText(zh="安全、HMI、驱动和 PLC 生态完整", en="Integrated safety, HMI, drives, and PLC ecosystem"),
            LocalizedText(zh="工程团队与供应商资源丰富", en="Strong engineering talent and supplier availability"),
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
        region_strength=LocalizedText(zh="跨厂商 OEM 与开放控制器生态", en="Cross-vendor OEM and open controller ecosystem"),
        summary=LocalizedText(zh="适合开放硬件策略、多硬件路线和 OEM 控制平台。", en="Suited for open hardware strategies, multi-hardware roadmaps, and OEM control platforms."),
        strengths=[
            LocalizedText(zh="开放性强，硬件选择广", en="High openness with broad hardware choice"),
            LocalizedText(zh="成本效率较好", en="Good cost efficiency"),
        ],
        cautions=[
            LocalizedText(zh="项目质量取决于具体硬件厂商", en="Project quality depends on the selected hardware vendor"),
        ],
        scores=PlatformScores(productivity=76, motion=70, safety=68, simulation=72, openness=93, talent=60, cost=86),
    ),
    PlcEcosystem(
        id="twincat",
        name="Beckhoff TwinCAT",
        vendor="Beckhoff",
        software="TwinCAT 3",
        region_strength=LocalizedText(zh="高性能机器控制和 PC-based control", en="High-performance machine control and PC-based control"),
        summary=LocalizedText(zh="适合高速运动控制、虚拟调试和软件定义自动化。", en="Suited for high-speed motion, virtual commissioning, and software-defined automation."),
        strengths=[
            LocalizedText(zh="运动控制与实时性能强", en="Strong motion control and real-time performance"),
            LocalizedText(zh="软件架构开放", en="Open software architecture"),
        ],
        cautions=[
            LocalizedText(zh="对团队软件工程能力要求高", en="Requires stronger software engineering capability"),
        ],
        scores=PlatformScores(productivity=80, motion=96, safety=78, simulation=86, openness=90, talent=64, cost=77),
    ),
    PlcEcosystem(
        id="rockwell",
        name="Rockwell Studio 5000",
        vendor="Rockwell Automation",
        software="Studio 5000 / ControlLogix",
        region_strength=LocalizedText(zh="北美大型工厂与资产密集型行业", en="Large North American plants and asset-intensive industries"),
        summary=LocalizedText(zh="适合北美装机基础、大型产线和混合自动化场景。", en="Suited for North American installed bases, large production lines, and hybrid automation."),
        strengths=[
            LocalizedText(zh="大型控制系统扩展能力强", en="Strong scalability for large control systems"),
            LocalizedText(zh="安全与工业网络生态成熟", en="Mature safety and industrial network ecosystem"),
        ],
        cautions=[
            LocalizedText(zh="总体拥有成本偏高", en="Higher total cost of ownership"),
        ],
        scores=PlatformScores(productivity=77, motion=80, safety=87, simulation=70, openness=58, talent=78, cost=54),
    ),
    PlcEcosystem(
        id="mitsubishi",
        name="Mitsubishi GX Works",
        vendor="Mitsubishi Electric",
        software="GX Works / MELSEC",
        region_strength=LocalizedText(zh="亚洲设备制造与离散自动化", en="Asian machine building and discrete automation"),
        summary=LocalizedText(zh="适合成本敏感、设备制造导向、亚洲供应链强相关的项目。", en="Suited for cost-sensitive, machine-builder-oriented projects tied to Asian supply chains."),
        strengths=[
            LocalizedText(zh="硬件稳定，设备制造应用广", en="Stable hardware with broad machine-building adoption"),
            LocalizedText(zh="成本与交付周期有竞争力", en="Competitive cost and delivery profile"),
        ],
        cautions=[
            LocalizedText(zh="高阶软件生态和开放集成不如 TwinCAT/CODESYS", en="Advanced software ecosystem and openness trail TwinCAT/CODESYS"),
        ],
        scores=PlatformScores(productivity=72, motion=74, safety=70, simulation=62, openness=55, talent=66, cost=82),
    ),
    PlcEcosystem(
        id="omron",
        name="Omron Sysmac",
        vendor="Omron",
        software="Sysmac Studio",
        region_strength=LocalizedText(zh="机器自动化、视觉和运动控制集成", en="Machine automation, vision, and motion integration"),
        summary=LocalizedText(zh="适合机器自动化、运动控制、视觉检测与紧凑型产线控制。", en="Suited for machine automation, motion control, vision inspection, and compact line control."),
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
        preferences=_preferences({"siemens-tia": 85, "twincat": 55, "codesys": 45, "rockwell": 60}),
        attachments=[
            ProjectAttachment(
                id="att-io-list",
                project_id="ev-line-standardization",
                file_name="Battery_Line_IO_List.xlsx",
                file_type="I/O List",
                declared_purpose="I/O scale and cabinet planning reference",
                uploaded_at="2026-05-27",
            )
        ],
        report=ReportDraft(
            project_id="ev-line-standardization",
            version=1,
            status="Ready",
            sections=[
                ReportSection(
                    id="executive-summary",
                    title=LocalizedText(zh="执行摘要", en="Executive Summary"),
                    body=LocalizedText(zh="当前建议优先评估 Siemens TIA Portal。", en="Current recommendation is to evaluate Siemens TIA Portal first."),
                    assumptions=[LocalizedText(zh="附件仅登记元信息，尚未解析。", en="Attachments are metadata-only and not parsed yet.")],
                    last_generated_at="2026-05-27",
                )
            ],
        ),
    )
]
