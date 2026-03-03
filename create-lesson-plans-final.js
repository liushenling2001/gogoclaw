const { Document, Packer, Paragraph, TextRun, Table, TableRow, TableCell, Header, Footer, 
        AlignmentType, LevelFormat, HeadingLevel, WidthType, BorderStyle, ShadingType,
        PageOrientation, PageBreak } = require('docx');
const fs = require('fs');

// 8 节课完整教案数据
const lessonPlans = [
    {
        lessonNumber: 1,
        unit: "Unit 10: Hydroxyl Compounds",
        title: "醇类 (Alcohols) - 命名、分类与物理性质",
        duration: "45 分钟",
        learningObjectives: [
            "理解醇类的定义和官能团结构 (-OH 羟基)",
            "掌握醇类的 IUPAC 系统命名法",
            "能够区分伯醇 (1°)、仲醇 (2°)、叔醇 (3°)",
            "理解氢键对醇类物理性质的影响",
            "解释低级醇与水互溶的原因"
        ],
        keyContent: [
            "醇的通式：R-OH，官能团为羟基 (-OH)",
            "命名规则：选择含-OH 的最长碳链为主链，编号使-OH 位置最小，后缀为'-ol'",
            "分类标准：根据-OH 连接的碳原子类型分为伯醇、仲醇、叔醇",
            "物理性质：沸点高于相应烷烃（氢键作用）；低级醇（C1-C4）与水互溶",
            "实例：甲醇 CH₃OH、乙醇 C₂H₅OH、丙醇 C₃H₇OH、异丙醇 (CH₃)₂CHOH"
        ],
        activities: [
            "【导入 5 分钟】展示乙醇消毒液、酒精饮料，引出醇类在日常生活中的应用",
            "【讲解 15 分钟】使用分子模型展示甲醇、乙醇、丙醇的结构，讲解命名规则",
            "【活动 15 分钟】学生练习：给出结构式写出名称，给出名称画出结构",
            "【讨论 10 分钟】对比乙醇与乙烷的沸点数据（78°C vs -89°C），讨论氢键的作用"
        ],
        homework: "1. 完成课本 P.156 习题 1-5；2. 预习醇的化学反应；3. 画出 C₄H₉OH 的所有同分异构体并命名",
        assessment: "课堂练习正确率；同分异构体绘制完整性"
    },
    {
        lessonNumber: 2,
        unit: "Unit 10: Hydroxyl Compounds",
        title: "醇类的化学反应 (Chemical Reactions of Alcohols)",
        duration: "45 分钟",
        learningObjectives: [
            "掌握醇与金属钠的反应及产物",
            "理解醇的氧化反应机理及不同醇的氧化产物",
            "掌握醇的脱水反应（分子内和分子间）",
            "了解醇与卤化氢 (HX) 的取代反应"
        ],
        keyContent: [
            "与 Na 反应：2R-OH + 2Na → 2R-ONa + H₂↑（醇钠生成，用于鉴别醇）",
            "氧化反应：伯醇 → 醛 → 羧酸；仲醇 → 酮；叔醇不被氧化",
            "氧化剂：酸性 K₂Cr₂O₇（橙红色→绿色），可用于醇的鉴别",
            "脱水反应：浓 H₂SO₄催化，170°C 分子内脱水生成烯烃；140°C 分子间脱水生成醚",
            "与 HX 反应：R-OH + HX → R-X + H₂O（Lucas 试剂鉴别伯仲叔醇）"
        ],
        activities: [
            "【演示 10 分钟】播放乙醇与钠反应实验视频，观察氢气产生",
            "【讲解 15 分钟】分析乙醇氧化为乙醛、乙醛氧化为乙酸的反应方程式",
            "【练习 15 分钟】预测不同醇（1-丁醇、2-丁醇、2-甲基 -2-丙醇）的氧化产物",
            "【总结 5 分钟】整理醇的反应类型思维导图"
        ],
        homework: "1. 完成课本 P.162 习题 1-8；2. 写出乙醇所有反应的化学方程式；3. 设计实验鉴别三种未知醇",
        assessment: "反应方程式书写正确性；产物预测准确性"
    },
    {
        lessonNumber: 3,
        unit: "Unit 10: Hydroxyl Compounds",
        title: "酚类 (Phenols)",
        duration: "45 分钟",
        learningObjectives: [
            "理解酚的定义和结构特点（-OH 直接连在苯环上）",
            "掌握苯酚的命名和物理性质",
            "理解酚的酸性及与醇、水的酸性比较",
            "掌握酚的特征反应（显色反应、溴代反应）"
        ],
        keyContent: [
            "酚的定义：羟基 (-OH) 直接连接在苯环上的化合物，最简单的是苯酚 C₆H₅OH",
            "结构特点：苯环与羟基相互影响，羟基使苯环活化（邻对位定位基）",
            "弱酸性：苯酚 > 水 > 醇，但不能使指示剂变色；C₆H₅OH + NaOH → C₆H₅ONa + H₂O",
            "显色反应：与 FeCl₃溶液反应显紫色（酚的特征检验方法）",
            "溴代反应：苯酚 + 3Br₂ → 2,4,6-三溴苯酚↓（白色沉淀，用于鉴别）"
        ],
        activities: [
            "【对比 10 分钟】对比苯酚、乙醇、水的结构，讨论苯环对羟基的影响",
            "【演示 10 分钟】播放苯酚与 FeCl₃显色反应、溴代反应实验视频",
            "【讨论 15 分钟】为什么酚羟基使苯环活化？为什么苯酚酸性强于醇？",
            "【练习 10 分钟】完成苯酚与 NaOH、Na₂CO₃、Br₂的反应方程式"
        ],
        homework: "1. 完成课本 P.168 习题 1-6；2. 复习羟基化合物全章，整理醇与酚的性质对比表；3. 预习羰基化合物",
        assessment: "酚的性质理解；反应方程式书写"
    },
    {
        lessonNumber: 4,
        unit: "Unit 11: Carbonyl Compounds",
        title: "醛和酮 (Aldehydes and Ketones) - 结构与命名",
        duration: "45 分钟",
        learningObjectives: [
            "理解羰基 (C=O) 的结构和极性",
            "区分醛和酮的结构差异",
            "掌握醛酮的 IUPAC 系统命名法",
            "了解常见醛酮的物理性质和用途"
        ],
        keyContent: [
            "羰基结构：C=O 双键，碳氧电负性差异（O:3.5, C:2.5）导致极性，碳带部分正电荷",
            "醛：R-CHO，羰基在碳链末端，至少有一个 H 原子；酮：R-CO-R'，羰基在碳链中间",
            "命名：醛为'某醛'（醛基碳为 C1）；酮为'某酮'，需标羰基位置",
            "常见醛：甲醛 HCHO（防腐剂）、乙醛 CH₃CHO；常见酮：丙酮 CH₃COCH₃（优良溶剂）",
            "物理性质：沸点高于烷烃但低于醇（有极性但无氢键）；低级醛酮与水互溶"
        ],
        activities: [
            "【导入 5 分钟】展示福尔马林（甲醛溶液）、指甲油去除剂（丙酮），引出醛酮的应用",
            "【讲解 15 分钟】使用球棍模型展示甲醛、乙醛、丙酮的结构，对比醛酮差异",
            "【活动 15 分钟】学生练习：命名给定的醛酮结构，画出 C₅H₁₀O 的醛酮同分异构体",
            "【讨论 10 分钟】对比乙醛、丙酮、丙烷的沸点数据，讨论极性对物理性质的影响"
        ],
        homework: "1. 完成课本 P.178 习题 1-5；2. 画出 C₅H₁₀O 的所有醛酮同分异构体并命名；3. 预习醛酮的化学反应",
        assessment: "命名正确性；同分异构体完整性"
    },
    {
        lessonNumber: 5,
        unit: "Unit 11: Carbonyl Compounds",
        title: "醛酮的氧化还原反应 (Oxidation and Reduction)",
        duration: "45 分钟",
        learningObjectives: [
            "掌握醛的氧化反应及常用氧化剂",
            "理解酮不易氧化的特点及应用",
            "掌握 Tollens 试剂和 Fehling 试剂的反应",
            "掌握醛酮的还原反应及产物"
        ],
        keyContent: [
            "醛易氧化：R-CHO + [O] → R-COOH（醛→羧酸）",
            "Tollens 试剂：[Ag(NH₃)₂]⁺，R-CHO + 2[Ag(NH₃)₂]⁺ + 2OH⁻ → R-COO⁻ + 2Ag↓ + 4NH₃ + H₂O（银镜反应）",
            "Fehling 试剂：Cu²⁺（蓝色）→ Cu₂O↓（砖红色），只与脂肪醛反应，不与芳香醛、酮反应",
            "酮不易氧化：无α-H 的酮不被氧化，可用于鉴别醛酮",
            "还原反应：醛→伯醇；酮→仲醇（还原剂：NaBH₄或 H₂/Ni）"
        ],
        activities: [
            "【演示 10 分钟】播放银镜反应实验视频，观察银镜形成过程",
            "【讲解 15 分钟】分析 Tollens、Fehling 试剂的反应方程式及应用",
            "【活动 15 分钟】设计实验方案鉴别乙醛、丙酮、苯甲醛三种未知物",
            "【练习 5 分钟】写出乙醛、丙酮分别与 NaBH₄反应的产物"
        ],
        homework: "1. 完成课本 P.184 习题 1-7；2. 整理醛酮氧化还原反应方程式；3. 总结醛酮的鉴别方法",
        assessment: "鉴别方案设计；反应方程式书写"
    },
    {
        lessonNumber: 6,
        unit: "Unit 11: Carbonyl Compounds",
        title: "醛酮的亲核加成反应 (Nucleophilic Addition)",
        duration: "45 分钟",
        learningObjectives: [
            "理解羰基亲核加成的反应机理",
            "掌握与 HCN 的加成反应及应用",
            "了解与 2,4-二硝基苯肼 (2,4-DNPH) 的反应",
            "理解醛酮反应活性的差异"
        ],
        keyContent: [
            "反应机理：亲核试剂进攻带部分正电荷的羰基碳，π键断裂，氧带负电荷后结合 H⁺",
            "与 HCN 加成：R-CHO + HCN → R-CH(OH)CN（氰醇），用于增长碳链",
            "与 2,4-DNPH 反应：生成黄色或橙色沉淀（羰基的鉴别和提纯）",
            "反应活性：醛 > 酮（空间位阻：醛的羰基碳更易接近；电子效应：酮的两个给电子基团降低羰基碳正电性）",
            "与格氏试剂 RMgX：生成醇，是制备醇的重要方法"
        ],
        activities: [
            "【动画 10 分钟】播放亲核加成反应机理动画，理解电子转移过程",
            "【讲解 15 分钟】分析乙醛与 HCN 加成的产物结构，讨论立体化学",
            "【演示 10 分钟】播放 2,4-DNPH 与丙酮反应生成沉淀的实验视频",
            "【练习 10 分钟】完成给定的亲核加成反应方程式，比较乙醛与丙酮的反应活性"
        ],
        homework: "1. 完成课本 P.190 习题 1-6；2. 写出乙醛与 HCN、CH₃MgBr 反应的产物；3. 预习羧酸章节",
        assessment: "机理理解；产物预测准确性"
    },
    {
        lessonNumber: 7,
        unit: "Unit 12: Carboxylic Acids and Derivatives",
        title: "羧酸 (Carboxylic Acids)",
        duration: "45 分钟",
        learningObjectives: [
            "掌握羧酸的结构特点和命名规则",
            "理解羧酸的酸性及影响因素",
            "掌握羧酸的制备方法和主要反应",
            "了解常见羧酸的性质和用途"
        ],
        keyContent: [
            "官能团：羧基 (-COOH)，羰基与羟基直接相连，存在 p-π共轭",
            "命名：选择含-COOH 的最长碳链为主链，羧基碳为 C1，后缀为'-oic acid'",
            "酸性：羧酸 > 碳酸 > 酚 > 水 > 醇；R-COOH ⇌ R-COO⁻ + H⁺",
            "制备：醇/醛氧化；腈水解；格氏试剂与 CO₂反应",
            "反应：成盐（与碱、碳酸盐）、酯化、还原（LiAlH₄→醇）、脱羧（加热→CO₂）"
        ],
        activities: [
            "【对比 10 分钟】对比乙酸、苯酚、乙醇的酸性，讨论结构对酸性的影响",
            "【演示 10 分钟】播放乙酸与碳酸钠反应产生 CO₂的实验视频",
            "【讲解 15 分钟】分析羧酸的制备方法，重点讲解酯化反应机理",
            "【练习 10 分钟】完成羧酸的转化反应方程式，设计乙酸乙酯的制备方案"
        ],
        homework: "1. 完成课本 P.200 习题 1-8；2. 整理羧酸的制备和反应方程式；3. 预习羧酸衍生物",
        assessment: "酸性比较理解；反应方程式书写"
    },
    {
        lessonNumber: 8,
        unit: "Unit 12: Carboxylic Acids and Derivatives",
        title: "羧酸衍生物 (Carboxylic Acid Derivatives)",
        duration: "45 分钟",
        learningObjectives: [
            "了解羧酸衍生物的分类和结构",
            "掌握酰氯、酸酐、酯、酰胺的命名",
            "理解衍生物的水解反应及活性顺序",
            "掌握酯化反应和酯的水解（皂化反应）"
        ],
        keyContent: [
            "四大衍生物：酰氯 (-COCl)、酸酐 (-CO-O-CO-)、酯 (-COOR)、酰胺 (-CONH₂)",
            "反应活性顺序：酰氯 > 酸酐 > 酯 > 酰胺（离去基团碱性越弱，活性越强）",
            "酯化反应：R-COOH + R'OH ⇌ R-COOR' + H₂O（浓 H₂SO₄催化，可逆反应）",
            "酯的水解：酸性→羧酸 + 醇；碱性→羧酸盐 + 醇（皂化反应，不可逆）",
            "油脂：高级脂肪酸甘油酯，碱性水解制肥皂；酰胺：蛋白质中的肽键"
        ],
        activities: [
            "【展示 10 分钟】展示乙酸乙酯、乙酰氯、乙酸酐、乙酰胺的结构模型",
            "【实验 15 分钟】播放乙酸乙酯制备实验视频，讲解实验要点",
            "【对比 10 分钟】对比不同衍生物的水解速率，讨论活性差异原因",
            "【讨论 10 分钟】油脂皂化反应制肥皂的原理；酰胺在蛋白质结构中的作用"
        ],
        homework: "1. 完成课本 P.208 习题 1-7；2. 复习有机化学全章，整理三大单元知识网络；3. 准备单元测试",
        assessment: "衍生物命名；水解反应方程式；知识网络完整性"
    }
];

// 创建单个教案文档
function createLessonPlan(lesson) {
    const doc = new Document({
        styles: {
            default: {
                document: {
                    run: { font: "Arial", size: 24, color: "000000" }
                }
            },
            paragraphStyles: [
                {
                    id: "Heading1",
                    name: "Heading 1",
                    basedOn: "Normal",
                    next: "Normal",
                    quickFormat: true,
                    run: { size: 44, bold: true, font: "Arial", color: "1F4E78" },
                    paragraph: { spacing: { before: 240, after: 240 }, outlineLevel: 0 }
                },
                {
                    id: "Heading2",
                    name: "Heading 2",
                    basedOn: "Normal",
                    next: "Normal",
                    quickFormat: true,
                    run: { size: 32, bold: true, font: "Arial", color: "2E75B6" },
                    paragraph: { spacing: { before: 200, after: 160 }, outlineLevel: 1 }
                },
                {
                    id: "Heading3",
                    name: "Heading 3",
                    basedOn: "Normal",
                    next: "Normal",
                    quickFormat: true,
                    run: { size: 28, bold: true, font: "Arial", color: "000000" },
                    paragraph: { spacing: { before: 160, after: 120 }, outlineLevel: 2 }
                },
                {
                    id: "TableHeader",
                    name: "Table Header",
                    basedOn: "Normal",
                    quickFormat: true,
                    run: { size: 24, bold: true, font: "Arial", color: "FFFFFF" },
                    paragraph: { spacing: { before: 80, after: 80 } }
                }
            ]
        },
        sections: [{
            properties: {
                page: {
                    size: { width: 11906, height: 16838 }, // A4
                    margin: { top: 1440, right: 1440, bottom: 1440, left: 1440 } // 1 inch
                }
            },
            headers: {
                default: new Header({
                    children: [
                        new Paragraph({
                            children: [
                                new TextRun({
                                    text: `Cambridge A-Level Chemistry (9701) - Lesson ${lesson.lessonNumber}/8`,
                                    size: 20,
                                    italics: true,
                                    color: "666666"
                                })
                            ],
                            alignment: AlignmentType.RIGHT
                        }),
                        new Paragraph({
                            children: [
                                new TextRun({
                                    text: lesson.unit,
                                    size: 20,
                                    bold: true,
                                    color: "1F4E78"
                                })
                            ],
                            alignment: AlignmentType.LEFT
                        })
                    ]
                })
            },
            footers: {
                default: new Footer({
                    children: [
                        new Paragraph({
                            children: [
                                new TextRun({
                                    text: `Page ${lesson.lessonNumber} | `,
                                    size: 18,
                                    color: "666666"
                                }),
                                new TextRun({
                                    children: ["Hydroxyl, Carbonyl & Carboxylic Compounds"],
                                    size: 18,
                                    italics: true,
                                    color: "666666"
                                })
                            ],
                            alignment: AlignmentType.CENTER
                        })
                    ]
                })
            },
            children: [
                // 课程标题
                new Paragraph({
                    heading: HeadingLevel.HEADING_1,
                    children: [new TextRun(lesson.title)],
                    spacing: { after: 100 }
                }),
                
                // 课时信息表格
                new Table({
                    width: { size: 9360, type: WidthType.DXA },
                    columnWidths: [2340, 2340, 2340, 2340],
                    rows: [
                        new TableRow({
                            tableHeader: true,
                            children: [
                                new TableCell({
                                    borders: { top: {style: BorderStyle.SINGLE, size: 1}, bottom: {style: BorderStyle.SINGLE, size: 1}, left: {style: BorderStyle.SINGLE, size: 1}, right: {style: BorderStyle.SINGLE, size: 1} },
                                    shading: { fill: "1F4E78", type: ShadingType.CLEAR },
                                    children: [new Paragraph({ children: [new TextRun({ text: "课时 Duration", color: "FFFFFF", bold: true })] })]
                                }),
                                new TableCell({
                                    borders: { top: {style: BorderStyle.SINGLE, size: 1}, bottom: {style: BorderStyle.SINGLE, size: 1}, left: {style: BorderStyle.SINGLE, size: 1}, right: {style: BorderStyle.SINGLE, size: 1} },
                                    shading: { fill: "1F4E78", type: ShadingType.CLEAR },
                                    children: [new Paragraph({ children: [new TextRun({ text: "单元 Unit", color: "FFFFFF", bold: true })] })]
                                }),
                                new TableCell({
                                    borders: { top: {style: BorderStyle.SINGLE, size: 1}, bottom: {style: BorderStyle.SINGLE, size: 1}, left: {style: BorderStyle.SINGLE, size: 1}, right: {style: BorderStyle.SINGLE, size: 1} },
                                    shading: { fill: "1F4E78", type: ShadingType.CLEAR },
                                    children: [new Paragraph({ children: [new TextRun({ text: "课次 Lesson", color: "FFFFFF", bold: true })] })]
                                }),
                                new TableCell({
                                    borders: { top: {style: BorderStyle.SINGLE, size: 1}, bottom: {style: BorderStyle.SINGLE, size: 1}, left: {style: BorderStyle.SINGLE, size: 1}, right: {style: BorderStyle.SINGLE, size: 1} },
                                    shading: { fill: "1F4E78", type: ShadingType.CLEAR },
                                    children: [new Paragraph({ children: [new TextRun({ text: "评估 Assessment", color: "FFFFFF", bold: true })] })]
                                })
                            ]
                        }),
                        new TableRow({
                            children: [
                                new TableCell({
                                    borders: { top: {style: BorderStyle.SINGLE, size: 1}, bottom: {style: BorderStyle.SINGLE, size: 1}, left: {style: BorderStyle.SINGLE, size: 1}, right: {style: BorderStyle.SINGLE, size: 1} },
                                    children: [new Paragraph({ children: [new TextRun(lesson.duration)] })]
                                }),
                                new TableCell({
                                    borders: { top: {style: BorderStyle.SINGLE, size: 1}, bottom: {style: BorderStyle.SINGLE, size: 1}, left: {style: BorderStyle.SINGLE, size: 1}, right: {style: BorderStyle.SINGLE, size: 1} },
                                    children: [new Paragraph({ children: [new TextRun(lesson.unit.split(":")[0])] })]
                                }),
                                new TableCell({
                                    borders: { top: {style: BorderStyle.SINGLE, size: 1}, bottom: {style: BorderStyle.SINGLE, size: 1}, left: {style: BorderStyle.SINGLE, size: 1}, right: {style: BorderStyle.SINGLE, size: 1} },
                                    children: [new Paragraph({ children: [new TextRun(`${lesson.lessonNumber}/8`)] })]
                                }),
                                new TableCell({
                                    borders: { top: {style: BorderStyle.SINGLE, size: 1}, bottom: {style: BorderStyle.SINGLE, size: 1}, left: {style: BorderStyle.SINGLE, size: 1}, right: {style: BorderStyle.SINGLE, size: 1} },
                                    children: [new Paragraph({ children: [new TextRun(lesson.assessment || "课堂练习与作业")] })]
                                })
                            ]
                        })
                    ]
                }),
                
                new Paragraph({ text: "", spacing: { before: 100 } }),
                
                // 教学目标
                new Paragraph({
                    heading: HeadingLevel.HEADING_2,
                    children: [new TextRun("📚 教学目标 Learning Objectives")],
                    spacing: { before: 50 }
                }),
                ...lesson.learningObjectives.map((obj) => 
                    new Paragraph({
                        numbering: { reference: "numbers", level: 0 },
                        children: [new TextRun(obj)],
                        spacing: { after: 50 }
                    })
                ),
                
                new Paragraph({ text: "", spacing: { before: 100 } }),
                
                // 重点内容
                new Paragraph({
                    heading: HeadingLevel.HEADING_2,
                    children: [new TextRun("📝 重点内容 Key Content")],
                    spacing: { before: 50 }
                }),
                ...lesson.keyContent.map((point) => 
                    new Paragraph({
                        numbering: { reference: "bullets", level: 0 },
                        children: [new TextRun(point)],
                        spacing: { after: 50 }
                    })
                ),
                
                new Paragraph({ text: "", spacing: { before: 100 } }),
                
                // 课堂活动
                new Paragraph({
                    heading: HeadingLevel.HEADING_2,
                    children: [new TextRun("🎯 课堂活动 Classroom Activities")],
                    spacing: { before: 50 }
                }),
                ...lesson.activities.map((act) => 
                    new Paragraph({
                        numbering: { reference: "bullets", level: 0 },
                        children: [new TextRun(act)],
                        spacing: { after: 50 }
                    })
                ),
                
                new Paragraph({ text: "", spacing: { before: 100 } }),
                
                // 课后作业
                new Paragraph({
                    heading: HeadingLevel.HEADING_2,
                    children: [new TextRun("📖 课后作业 Homework")],
                    spacing: { before: 50 }
                }),
                new Paragraph({
                    children: [new TextRun(lesson.homework)],
                    spacing: { after: 100 }
                }),
                
                // 分页符（除了最后一个教案）
                ...(lesson.lessonNumber < 8 ? [new Paragraph({ children: [new PageBreak()] })] : [])
            ]
        }],
        numbering: {
            config: [
                {
                    reference: "bullets",
                    levels: [{
                        level: 0,
                        format: LevelFormat.BULLET,
                        text: "•",
                        alignment: AlignmentType.LEFT,
                        style: {
                            paragraph: { indent: { left: 720, hanging: 360 } }
                        }
                    }]
                },
                {
                    reference: "numbers",
                    levels: [{
                        level: 0,
                        format: LevelFormat.DECIMAL,
                        text: "%1.",
                        alignment: AlignmentType.LEFT,
                        style: {
                            paragraph: { indent: { left: 720, hanging: 360 } }
                        }
                    }]
                }
            ]
        }
    });
    
    return doc;
}

// 主函数
async function createAllLessonPlans() {
    console.log("🚀 开始创建 8 节课教案...\n");
    
    for (let i = 0; i < lessonPlans.length; i++) {
        const lesson = lessonPlans[i];
        console.log(`📄 创建教案 ${i + 1}/8: ${lesson.title}`);
        
        const doc = createLessonPlan(lesson);
        const buffer = await Packer.toBuffer(doc);
        const fileName = `Lesson_Plan_${i + 1}_A_Level_Chemistry.docx`;
        fs.writeFileSync(`/home/22607104_wy/openclaw/workspace/${fileName}`, buffer);
        console.log(`   ✅ 已保存：${fileName}\n`);
    }
    
    console.log("=" * 60);
    console.log("✅ 所有 8 节课教案创建完成！");
    console.log("📁 文件位置：/home/22607104_wy/openclaw/workspace/");
    console.log("=" * 60);
}

createAllLessonPlans().catch(console.error);
