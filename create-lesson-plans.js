const { Document, Packer, Paragraph, TextRun, Table, TableRow, TableCell, Header, Footer, 
        AlignmentType, LevelFormat, HeadingLevel, WidthType, BorderStyle, ShadingType,
        PageOrientation, PageBreak } = require('docx');
const fs = require('fs');

// 教案数据 - 8 节课
const lessonPlans = [
    {
        title: "羟基化合物 (Hydroxyl Compounds) - 第 1 课",
        subtitle: "醇类 (Alcohols) - 命名、分类与物理性质",
        duration: "45 分钟",
        objectives: [
            "理解醇类的定义和官能团结构 (-OH)",
            "掌握醇类的系统命名法 (IUPAC)",
            "能够区分伯醇、仲醇、叔醇",
            "理解醇类物理性质与氢键的关系"
        ],
        keyPoints: [
            "醇的通式：R-OH，官能团为羟基 (-OH)",
            "命名规则：选择含-OH 的最长碳链，编号使-OH 位置最小",
            "分类：伯醇 (1°)、仲醇 (2°)、叔醇 (3°)",
            "氢键导致醇的沸点高于相应烷烃",
            "低级醇与水互溶，随碳链增长溶解度降低"
        ],
        activities: [
            "展示甲醇、乙醇、丙醇的分子模型",
            "对比乙醇与乙烷的沸点数据",
            "练习：命名给定的醇类结构"
        ],
        homework: "完成课本 P.156 习题 1-5；预习醇的化学反应"
    },
    {
        title: "羟基化合物 (Hydroxyl Compounds) - 第 2 课",
        subtitle: "醇类的化学反应 (Chemical Reactions of Alcohols)",
        duration: "45 分钟",
        objectives: [
            "掌握醇与钠的反应",
            "理解醇的氧化反应及产物",
            "掌握醇的脱水反应",
            "了解醇与卤化氢的反应"
        ],
        keyPoints: [
            "与 Na 反应：2R-OH + 2Na → 2R-ONa + H₂↑",
            "氧化反应：伯醇→醛→羧酸；仲醇→酮；叔醇不氧化",
            "氧化剂：酸性 K₂Cr₂O₇ (橙→绿)",
            "脱水反应：分子内脱水生成烯烃；分子间脱水生成醚",
            "与 HX 反应：R-OH + HX → R-X + H₂O"
        ],
        activities: [
            "演示乙醇与钠反应的实验视频",
            "分析乙醇氧化为乙醛的反应机理",
            "练习：预测不同醇的氧化产物"
        ],
        homework: "完成课本 P.162 习题 1-8；整理醇的反应类型思维导图"
    },
    {
        title: "羟基化合物 (Hydroxyl Compounds) - 第 3 课",
        subtitle: "酚类 (Phenols)",
        duration: "45 分钟",
        objectives: [
            "理解酚的定义和结构特点",
            "掌握酚的命名和物理性质",
            "理解酚的酸性强弱",
            "掌握酚的特征反应"
        ],
        keyPoints: [
            "酚：-OH 直接连在苯环上",
            "苯酚结构：C₆H₅OH，苯环与羟基相互影响",
            "弱酸性：苯酚 > 水 > 醇，但不能使指示剂变色",
            "与 FeCl₃显色反应：紫色 (酚的特征检验)",
            "苯环上的取代反应：邻对位定位，易溴代生成 2,4,6-三溴苯酚↓"
        ],
        activities: [
            "对比苯酚、乙醇、水的酸性",
            "演示苯酚与 FeCl₃的显色反应",
            "讨论：为什么酚羟基使苯环活化"
        ],
        homework: "完成课本 P.168 习题 1-6；复习羟基化合物全章"
    },
    {
        title: "羰基化合物 (Carbonyl Compounds) - 第 4 课",
        subtitle: "醛和酮 (Aldehydes and Ketones) - 结构与命名",
        duration: "45 分钟",
        objectives: [
            "理解羰基的结构和极性",
            "区分醛和酮的结构差异",
            "掌握醛酮的系统命名法",
            "了解醛酮的物理性质"
        ],
        keyPoints: [
            "羰基：C=O 双键，碳氧电负性差异导致极性",
            "醛：R-CHO，羰基在链端；酮：R-CO-R'，羰基在链中",
            "命名：醛为'某醛'；酮为'某酮'，需标位置",
            "甲醛 HCHO 是最简单的醛",
            "丙酮是最常见的酮，优良有机溶剂"
        ],
        activities: [
            "展示甲醛、乙醛、丙酮的分子模型",
            "对比醛酮与醇的沸点差异",
            "练习：命名给定的醛酮结构"
        ],
        homework: "完成课本 P.178 习题 1-5；预习醛酮的化学反应"
    },
    {
        title: "羰基化合物 (Carbonyl Compounds) - 第 5 课",
        subtitle: "醛酮的氧化还原反应",
        duration: "45 分钟",
        objectives: [
            "掌握醛的氧化反应及检验方法",
            "理解酮不易氧化的特点",
            "掌握醛酮的还原反应",
            "了解 Tollens 试剂和 Fehling 试剂"
        ],
        keyPoints: [
            "醛易氧化：R-CHO → R-COOH",
            "Tollens 试剂：银镜反应，R-CHO + 2[Ag(NH₃)₂]⁺ → R-COO⁻ + 2Ag↓",
            "Fehling 试剂：砖红色 Cu₂O↓，只与脂肪醛反应",
            "酮不易氧化 (无α-H 的酮除外)",
            "还原反应：醛→伯醇；酮→仲醇 (NaBH₄或 H₂/Ni)"
        ],
        activities: [
            "演示银镜反应实验视频",
            "对比乙醛与丙酮的氧化性差异",
            "练习：设计实验鉴别醛和酮"
        ],
        homework: "完成课本 P.184 习题 1-7；整理醛酮氧化还原反应方程式"
    },
    {
        title: "羰基化合物 (Carbonyl Compounds) - 第 6 课",
        subtitle: "醛酮的亲核加成反应",
        duration: "45 分钟",
        objectives: [
            "理解羰基亲核加成的反应机理",
            "掌握与 HCN 的加成反应",
            "掌握与格氏试剂的反应",
            "了解与醇的加成 (缩醛形成)"
        ],
        keyPoints: [
            "反应机理：亲核试剂进攻带正电的羰基碳",
            "与 HCN：R-CHO + HCN → R-CH(OH)CN (增长碳链)",
            "与 RMgX：生成醇，是制备醇的重要方法",
            "与 ROH：形成半缩醛→缩醛 (保护羰基)",
            "醛的反应活性 > 酮 (空间位阻和电子效应)"
        ],
        activities: [
            "动画演示亲核加成反应机理",
            "分析乙醛与 HCN 加成的产物结构",
            "练习：完成给定的亲核加成反应方程式"
        ],
        homework: "完成课本 P.190 习题 1-6；预习羧酸章节"
    },
    {
        title: "羧酸及其衍生物 (Carboxylic Acids & Derivatives) - 第 7 课",
        subtitle: "羧酸 (Carboxylic Acids)",
        duration: "45 分钟",
        objectives: [
            "掌握羧酸的结构和命名",
            "理解羧酸的酸性及影响因素",
            "掌握羧酸的制备和主要反应",
            "了解常见羧酸的性质和用途"
        ],
        keyPoints: [
            "官能团：羧基 (-COOH)",
            "命名：选择含-COOH 的最长碳链，编号从羧基碳开始",
            "酸性：羧酸 > 碳酸 > 酚 > 水 > 醇",
            "制备：醇/醛氧化；腈水解；格氏试剂与 CO₂反应",
            "反应：成盐、酯化、还原、脱羧"
        ],
        activities: [
            "对比乙酸、苯酚、乙醇的酸性",
            "演示乙酸与碳酸钠反应产生 CO₂",
            "练习：完成羧酸的转化反应方程式"
        ],
        homework: "完成课本 P.200 习题 1-8；预习羧酸衍生物"
    },
    {
        title: "羧酸及其衍生物 (Carboxylic Acids & Derivatives) - 第 8 课",
        subtitle: "羧酸衍生物 (Carboxylic Acid Derivatives)",
        duration: "45 分钟",
        objectives: [
            "了解羧酸衍生物的分类",
            "掌握酰氯、酸酐、酯、酰胺的结构和命名",
            "理解衍生物的水解反应",
            "掌握酯化反应和酯的水解"
        ],
        keyPoints: [
            "四大衍生物：酰氯 (-COCl)、酸酐 (-CO-O-CO-)、酯 (-COOR)、酰胺 (-CONH₂)",
            "反应活性：酰氯 > 酸酐 > 酯 > 酰胺",
            "酯化：R-COOH + R'OH ⇌ R-COOR' + H₂O (浓 H₂SO₄催化)",
            "酯的水解：酸性→羧酸 + 醇；碱性→羧酸盐 + 醇 (皂化)",
            "油脂是高级脂肪酸甘油酯，皂化反应制肥皂"
        ],
        activities: [
            "展示乙酸乙酯的制备实验",
            "对比不同衍生物的水解速率",
            "讨论：油脂皂化反应的应用"
        ],
        homework: "完成课本 P.208 习题 1-7；复习有机化学全章"
    }
];

// 创建单个教案文档
function createLessonPlan(lesson, index) {
    const doc = new Document({
        styles: {
            default: {
                document: {
                    run: { font: "Arial", size: 24 } // 12pt
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
                    run: { size: 28, bold: true, font: "Arial" },
                    paragraph: { spacing: { before: 160, after: 120 }, outlineLevel: 2 }
                }
            ]
        },
        sections: [{
            properties: {
                page: {
                    size: { width: 11906, height: 16838 }, // A4
                    margin: { top: 1440, right: 1440, bottom: 1440, left: 1440 }
                }
            },
            headers: {
                default: new Header({
                    children: [
                        new Paragraph({
                            children: [
                                new TextRun({
                                    text: `A-Level Chemistry Lesson Plan ${index + 1}/8`,
                                    size: 20,
                                    italics: true
                                })
                            ],
                            alignment: AlignmentType.RIGHT
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
                                    text: "Cambridge International AS & A Level Chemistry (9701)",
                                    size: 18,
                                    italics: true
                                })
                            ],
                            alignment: AlignmentType.CENTER
                        })
                    ]
                })
            },
            children: [
                // 标题
                new Paragraph({
                    heading: HeadingLevel.HEADING_1,
                    children: [new TextRun(lesson.title)]
                }),
                
                // 副标题
                new Paragraph({
                    heading: HeadingLevel.HEADING_2,
                    children: [new TextRun(lesson.subtitle)]
                }),
                
                // 课时
                new Paragraph({
                    children: [
                        new TextRun({
                            text: `课时 Duration: ${lesson.duration}`,
                            bold: true,
                            size: 24
                        })
                    ],
                    spacing: { after: 200 }
                }),
                
                // 教学目标
                new Paragraph({
                    heading: HeadingLevel.HEADING_3,
                    children: [new TextRun("教学目标 Learning Objectives")]
                }),
                ...lesson.objectives.map((obj, i) => 
                    new Paragraph({
                        numbering: { reference: "numbers", level: 0 },
                        children: [new TextRun(obj)]
                    })
                ),
                
                // 重点内容
                new Paragraph({
                    heading: HeadingLevel.HEADING_3,
                    children: [new TextRun("重点内容 Key Points")],
                    spacing: { before: 200 }
                }),
                ...lesson.keyPoints.map((point, i) => 
                    new Paragraph({
                        numbering: { reference: "bullets", level: 0 },
                        children: [new TextRun(point)]
                    })
                ),
                
                // 课堂活动
                new Paragraph({
                    heading: HeadingLevel.HEADING_3,
                    children: [new TextRun("课堂活动 Classroom Activities")],
                    spacing: { before: 200 }
                }),
                ...lesson.activities.map((act, i) => 
                    new Paragraph({
                        numbering: { reference: "bullets", level: 0 },
                        children: [new TextRun(act)]
                    })
                ),
                
                // 课后作业
                new Paragraph({
                    heading: HeadingLevel.HEADING_3,
                    children: [new TextRun("课后作业 Homework")],
                    spacing: { before: 200 }
                }),
                new Paragraph({
                    children: [new TextRun(lesson.homework)],
                    spacing: { after: 200 }
                }),
                
                // 分页符 (除了最后一个教案)
                ...(index < lessonPlans.length - 1 ? [new Paragraph({ children: [new PageBreak()] })] : [])
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

// 主函数 - 创建所有教案
async function createAllLessonPlans() {
    console.log("开始创建 8 节课教案...");
    
    // 创建合并文档（所有教案在一个文件中）
    const mergedChildren = [];
    
    for (let i = 0; i < lessonPlans.length; i++) {
        const lesson = lessonPlans[i];
        console.log(`创建教案 ${i + 1}/8: ${lesson.title}`);
        
        // 创建单个教案文件
        const doc = createLessonPlan(lesson, i);
        const buffer = await Packer.toBuffer(doc);
        const fileName = `Lesson_Plan_${i + 1}_Hydroxyl_Carbonyl_Carboxylic.docx`;
        fs.writeFileSync(`/home/22607104_wy/openclaw/workspace/${fileName}`, buffer);
        console.log(`  ✓ 已保存：${fileName}`);
        
        // 添加到合并文档的内容
        const sectionDoc = createLessonPlan(lesson, i);
        // 这里简化处理，实际合并需要更复杂的逻辑
    }
    
    console.log("\n✅ 所有教案创建完成！");
    console.log("文件已保存到 workspace 目录");
}

createAllLessonPlans().catch(console.error);
