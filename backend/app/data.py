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


DEFAULT_REPORT_SECTION_IDS = [
    "executive-summary",
    "project-inputs",
    "platform-benchmark",
    "preference-impact",
    "risk-assessment",
    "implementation-roadmap",
    "assumptions-uncertainty",
]


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


def _preferences(notes: dict[str, tuple[int, str]]) -> list[PlatformPreference]:
    return [
        PlatformPreference(
            platform_id=platform.id,
            preference_weight=notes.get(platform.id, (50, "No specific business preference captured yet."))[0],
            user_reason_note=notes.get(platform.id, (50, "No specific business preference captured yet."))[1],
        )
        for platform in ECOSYSTEMS
    ]


def build_report_sections(
    project_name: str,
    *,
    executive_summary: str,
    inputs: str,
    benchmark: str,
    preference: str,
    risk: str,
    roadmap: str,
    uncertainty: str,
    generated_at: str = "2026-06-01",
) -> list[ReportSection]:
    sections = [
        (
            "executive-summary",
            "执行摘要",
            "Executive Summary",
            executive_summary,
            f"{project_name} has enough structured inputs to compare PLC platforms and prepare a decision workshop.",
        ),
        (
            "project-inputs",
            "项目输入",
            "Project Inputs",
            inputs,
            "The current intake captures project scale, I/O count, motion, safety, budget sensitivity, existing platform, and candidate platforms.",
        ),
        (
            "platform-benchmark",
            "平台基准对比",
            "Platform Benchmark",
            benchmark,
            "The benchmark can be regenerated from deterministic platform scores and project preferences.",
        ),
        (
            "preference-impact",
            "偏好影响",
            "Preference Impact",
            preference,
            "User preference weights reflect business context such as team familiarity, supplier capacity, and standardization pressure.",
        ),
        (
            "risk-assessment",
            "风险评估",
            "Risk Assessment",
            risk,
            "Risk language is based on the current inputs and should be reviewed with controls, safety, maintenance, and procurement stakeholders.",
        ),
        (
            "implementation-roadmap",
            "迁移 / 实施路线图",
            "Migration / Implementation Roadmap",
            roadmap,
            "Roadmap content is a planning draft and should be validated against commissioning windows and supplier lead times.",
        ),
        (
            "assumptions-uncertainty",
            "假设与不确定性",
            "Assumptions & Uncertainty",
            uncertainty,
            "Attachment contents are not read in this version; only file names, types, declared purposes, and upload dates are registered.",
        ),
    ]
    return [
        ReportSection(
            id=section_id,
            title=LocalizedText(zh=title_zh, en=title_en),
            body=LocalizedText(zh=body_zh, en=body_en),
            assumptions=[
                LocalizedText(
                    zh="当前结论仅基于项目输入、平台资料和已登记附件信息；附件正文未被解析。",
                    en="Current conclusions use project inputs, platform profiles, and registered attachment information only; attachment contents are not parsed.",
                )
            ],
            last_generated_at=generated_at,
        )
        for section_id, title_zh, title_en, body_zh, body_en in sections
    ]


PROJECT_WORKSPACES: list[ProjectWorkspace] = [
    ProjectWorkspace(
        project=Project(
            id="ev-line-standardization",
            name="新能源电池产线 PLC 标准化",
            industry="新能源电池制造",
            goal="为两条新建电芯装配与化成段产线建立统一 PLC 平台，兼顾安全、供应商交付、维护能力和集团长期标准。",
            status="Report Ready",
            created_at="2026-05-18",
            updated_at="2026-06-01",
        ),
        intake=ProjectIntake(
            project_size="Large",
            io_scale=1840,
            motion_requirement=62,
            safety_requirement=88,
            budget_sensitivity=54,
            team_experience="工厂维护团队以 Siemens TIA Portal 为主，集团自动化中心具备 Rockwell 审核经验，TwinCAT 经验较少。",
            existing_platform="siemens-tia",
            candidate_platforms=["siemens-tia", "rockwell", "twincat", "codesys"],
            constraints="需满足集团安全标准、备件长期可得性、产线复制能力、供应商驻场支持，以及 2026 年第四季度投产窗口。",
        ),
        preferences=_preferences(
            {
                "siemens-tia": (90, "现有维护团队熟悉，备件体系和集团模板可复用，是标准化首选。"),
                "twincat": (58, "运动和软件能力有吸引力，但现场团队经验不足，需要额外培训和供应商支持。"),
                "codesys": (46, "开放性较好，但集团对控制器品牌和安全认证链路仍需确认。"),
                "rockwell": (66, "安全生态成熟，集团北美工厂有经验，但本地供应链和成本压力较高。"),
                "mitsubishi": (32, "局部设备供应商熟悉，但不适合作为集团级电池产线标准。"),
                "omron": (38, "机器集成体验较好，但大型产线标准化和人才覆盖不足。"),
            }
        ),
        attachments=[
            ProjectAttachment(
                id="att-ev-io-master",
                project_id="ev-line-standardization",
                file_name="电芯装配线_IO点表_初版.xlsx",
                file_type="I/O List",
                declared_purpose="登记 I/O 规模、远程站数量和柜体划分；当前仅记录文件信息，不解析正文。",
                uploaded_at="2026-05-28",
            ),
            ProjectAttachment(
                id="att-ev-safety-standard",
                project_id="ev-line-standardization",
                file_name="集团自动化与安全标准_2026.pdf",
                file_type="Requirements",
                declared_purpose="说明安全等级、网络分区和供应商交付要求；当前仅记录文件信息，不解析正文。",
                uploaded_at="2026-05-29",
            ),
            ProjectAttachment(
                id="att-ev-architecture",
                project_id="ev-line-standardization",
                file_name="电芯产线控制网络架构草图.vsdx",
                file_type="Architecture",
                declared_purpose="用于描述 PLC、HMI、SCADA 与安全网络边界；当前仅记录文件信息，不解析正文。",
                uploaded_at="2026-06-01",
            ),
        ],
        report=ReportDraft(
            project_id="ev-line-standardization",
            sections=build_report_sections(
                "新能源电池产线 PLC 标准化",
                executive_summary="该项目更偏向稳定、可复制、便于维护的集团标准化决策。Siemens 具备明显组织适配优势，Rockwell 可作为安全与大型系统备选，TwinCAT / CODESYS 适合在特定设备或开放控制单元中继续验证。",
                inputs="当前输入显示项目 I/O 规模大、安全要求高、运动复杂度中等，主要约束来自投产窗口、备件体系、供应商驻场能力和集团模板复用。",
                benchmark="平台对比应重点关注安全生态、工程效率、供应商覆盖、长期维护和跨产线复制能力。确定性评分将基于平台 profile 与偏好权重重新生成。",
                preference="用户偏好明显倾向 Siemens，原因是团队经验、备件和集团标准。Rockwell 获得中等偏好，主要来自安全生态与既有集团经验；TwinCAT 的技术潜力受到团队经验限制。",
                risk="主要风险包括交付窗口压缩、供应商资源冲突、安全验收周期、备件策略确认不足，以及跨工段模板复用不充分。",
                roadmap="建议先完成标准 PLC 模板冻结，再进行关键工段 PoC、供应商能力评审、备件清单确认和 FAT/SAT 验证计划。",
                uncertainty="尚需确认最终安全等级、SCADA 接口边界、供应商驻场排期、关键模块交期、停机窗口和未来产线复制节奏。",
            ),
            version=1,
            status="Ready",
        ),
    ),
    ProjectWorkspace(
        project=Project(
            id="high-speed-packaging",
            name="高速包装设备平台选型",
            industry="包装设备制造",
            goal="为新一代高速枕式包装设备选择控制平台，重点提升多轴同步、视觉触发、虚拟调试和可复用软件模板能力。",
            status="Report Ready",
            created_at="2026-05-20",
            updated_at="2026-06-01",
        ),
        intake=ProjectIntake(
            project_size="Medium",
            io_scale=460,
            motion_requirement=96,
            safety_requirement=74,
            budget_sensitivity=58,
            team_experience="研发团队具备较强软件开发能力，熟悉 Siemens 基础项目，正在评估 TwinCAT 和 CODESYS 的机器模板能力。",
            existing_platform="siemens-tia",
            candidate_platforms=["twincat", "codesys", "siemens-tia", "omron"],
            constraints="设备节拍目标高，多轴同步和电子凸轮复杂，需要缩短调试周期并支持海外客户远程诊断。",
        ),
        preferences=_preferences(
            {
                "siemens-tia": (55, "现有项目可复用，但高速运动和软件架构灵活性不是最强。"),
                "twincat": (92, "运动控制、实时性能和软件工程化能力与设备路线高度匹配。"),
                "codesys": (70, "开放硬件和成本优势明显，可作为中端机型控制平台备选。"),
                "rockwell": (30, "目标客户区域和设备成本结构暂不支持优先采用。"),
                "mitsubishi": (50, "部分客户接受度高，但软件模板和虚拟调试能力需要进一步评估。"),
                "omron": (68, "运动、视觉和控制集成较好，适合中小型设备系列化。"),
            }
        ),
        attachments=[
            ProjectAttachment(
                id="att-pack-motion",
                project_id="high-speed-packaging",
                file_name="高速包装机_运动轴与节拍目标.xlsx",
                file_type="Requirements",
                declared_purpose="登记轴数、节拍目标、同步关系和关键性能指标；当前仅记录文件信息，不解析正文。",
                uploaded_at="2026-05-30",
            ),
            ProjectAttachment(
                id="att-pack-electrical",
                project_id="high-speed-packaging",
                file_name="包装设备电气清单_客户版.xlsx",
                file_type="Electrical List",
                declared_purpose="登记伺服、视觉、传感器和 HMI 范围；当前仅记录文件信息，不解析正文。",
                uploaded_at="2026-06-01",
            ),
        ],
        report=ReportDraft(
            project_id="high-speed-packaging",
            sections=build_report_sections(
                "高速包装设备平台选型",
                executive_summary="该项目的核心决策不是单纯 PLC 成本，而是高速运动性能、软件复用和调试效率。TwinCAT 在技术适配上最强，CODESYS 与 Omron 可作为分层产品线备选。",
                inputs="项目 I/O 规模中等，但运动要求接近满分，安全要求中高，团队软件能力较强，适合评估更开放的软件定义控制架构。",
                benchmark="平台对比应突出运动、仿真、开放性、软件生产率和现场服务能力。确定性 benchmark 会保留固定评分公式，不由智能解释改变。",
                preference="TwinCAT 获得最高偏好，反映研发团队对高速运动和模板化架构的需求；CODESYS 适合成本敏感机型；Omron 适合强调视觉和运动集成的版本。",
                risk="主要风险包括团队学习曲线、实时控制架构验证不足、客户指定品牌变更、海外服务网络和关键运动库封装质量。",
                roadmap="建议以 TwinCAT 建立一台样机验证多轴同步和虚拟调试，再为中端机型并行评估 CODESYS / Omron 的成本与维护模型。",
                uncertainty="尚需确认目标市场客户品牌偏好、远程诊断安全策略、运动控制库归属、软件模板维护责任和量产后的服务培训计划。",
            ),
            version=1,
            status="Ready",
        ),
    ),
    ProjectWorkspace(
        project=Project(
            id="legacy-line-siemens-rockwell-migration",
            name="老旧产线 Siemens / Rockwell 迁移评估",
            industry="离散制造产线改造",
            goal="评估一条 15 年以上老旧装配产线的 PLC 与 HMI 迁移路径，在 Siemens 与 Rockwell 现有资产之间选择低停机风险方案。",
            status="Analyzing",
            created_at="2026-05-22",
            updated_at="2026-06-01",
        ),
        intake=ProjectIntake(
            project_size="Large",
            io_scale=1260,
            motion_requirement=48,
            safety_requirement=82,
            budget_sensitivity=72,
            team_experience="维护团队同时接触过 Siemens S7 和 Rockwell ControlLogix，但老程序注释不足，外部系统接口依赖多。",
            existing_platform="rockwell",
            candidate_platforms=["siemens-tia", "rockwell", "codesys", "mitsubishi"],
            constraints="停机窗口只有两个周末，HMI 画面需逐步替换，历史配方、报警和 MES 接口必须保留，改造预算敏感。",
        ),
        preferences=_preferences(
            {
                "siemens-tia": (74, "区域供应商和新增产线以 Siemens 为主，有利于未来统一维护。"),
                "twincat": (36, "技术能力强，但本次改造不以高速运动或软件重构为目标。"),
                "codesys": (52, "开放性和成本有吸引力，但历史系统迁移风险需要额外验证。"),
                "rockwell": (82, "现有资产和团队经验较强，可能降低停机和程序迁移风险。"),
                "mitsubishi": (44, "部分设备可兼容，但对既有 Siemens/Rockwell 资产承接不足。"),
                "omron": (34, "不匹配当前老旧大型产线迁移场景。"),
            }
        ),
        attachments=[
            ProjectAttachment(
                id="att-legacy-inventory",
                project_id="legacy-line-siemens-rockwell-migration",
                file_name="老旧装配线控制柜盘点.xlsx",
                file_type="Electrical List",
                declared_purpose="登记 PLC、远程 I/O、变频器、HMI 与网络资产；当前仅记录文件信息，不解析正文。",
                uploaded_at="2026-05-31",
            ),
            ProjectAttachment(
                id="att-legacy-cutover",
                project_id="legacy-line-siemens-rockwell-migration",
                file_name="停机窗口与切换计划草案.docx",
                file_type="Requirements",
                declared_purpose="登记允许停机窗口、回退要求和验收节点；当前仅记录文件信息，不解析正文。",
                uploaded_at="2026-06-01",
            ),
            ProjectAttachment(
                id="att-legacy-network",
                project_id="legacy-line-siemens-rockwell-migration",
                file_name="现有网络与MES接口清单.pdf",
                file_type="Architecture",
                declared_purpose="登记上位系统接口、网络分区和历史报警依赖；当前仅记录文件信息，不解析正文。",
                uploaded_at="2026-06-01",
            ),
        ],
        report=ReportDraft(
            project_id="legacy-line-siemens-rockwell-migration",
            sections=build_report_sections(
                "老旧产线 Siemens / Rockwell 迁移评估",
                executive_summary="该项目的关键是降低停机和迁移风险，而不是追求最高技术评分。Rockwell 延续方案可能降低切换风险，Siemens 统一方案则更有利于未来区域标准化。",
                inputs="项目 I/O 规模大、安全要求高、预算敏感，运动要求中等。既有平台为 Rockwell，同时存在 Siemens 维护能力和新增产线统一压力。",
                benchmark="平台对比应重点审视历史程序迁移、HMI 替换、MES 接口保持、备件策略和分阶段切换能力。确定性评分只提供排序参考。",
                preference="Rockwell 偏好最高，来自既有资产和停机风险控制；Siemens 次之，来自区域标准化价值；CODESYS 和 Mitsubishi 更适合作为局部替换或成本参照。",
                risk="主要风险包括老程序资料缺失、停机窗口过短、历史报警与配方迁移遗漏、接口回归测试不足和安全回路改造审批。",
                roadmap="建议先完成资产盘点和接口冻结，再建立离线迁移测试台，分批替换 HMI 与远程 I/O，最后在计划停机窗口内切换主 PLC。",
                uncertainty="尚需确认原程序可读性、备份完整性、HMI 画面数量、MES 接口协议、回退方案、备件库存和周末施工资源。",
            ),
            version=1,
            status="Draft",
        ),
    ),
]
