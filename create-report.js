const { Document, Packer, Paragraph, TextRun, Table, TableRow, TableCell, HeadingLevel,
        AlignmentType, BorderStyle, WidthType, ShadingType, LevelFormat, PageBreak,
        TableOfContents, Header, Footer, PageNumber } = require('docx');
const fs = require('fs');

const doc = new Document({
  styles: {
    default: { document: { run: { font: "Arial", size: 24 } } },
    paragraphStyles: [
      { id: "Heading1", name: "Heading 1", basedOn: "Normal", next: "Normal", quickFormat: true,
        run: { size: 40, bold: true, font: "Arial", color: "1F4E78" },
        paragraph: { spacing: { before: 400, after: 300 }, outlineLevel: 0 } },
      { id: "Heading2", name: "Heading 2", basedOn: "Normal", next: "Normal", quickFormat: true,
        run: { size: 32, bold: true, font: "Arial", color: "2E5C8A" },
        paragraph: { spacing: { before: 300, after: 200 }, outlineLevel: 1 } },
      { id: "Heading3", name: "Heading 3", basedOn: "Normal", next: "Normal", quickFormat: true,
        run: { size: 28, bold: true, font: "Arial", color: "3D6C99" },
        paragraph: { spacing: { before: 240, after: 160 }, outlineLevel: 2 } },
    ]
  },
  numbering: {
    config: [
      { reference: "bullets", levels: [{ level: 0, format: LevelFormat.BULLET, text: "•", alignment: AlignmentType.LEFT,
        style: { paragraph: { indent: { left: 720, hanging: 360 } } } }] },
      { reference: "numbers", levels: [{ level: 0, format: LevelFormat.DECIMAL, text: "%1.", alignment: AlignmentType.LEFT,
        style: { paragraph: { indent: { left: 720, hanging: 360 } } } }] },
    ]
  },
  sections: [{
    properties: {
      page: {
        size: { width: 12240, height: 15840 },
        margin: { top: 1440, right: 1440, bottom: 1440, left: 1440 }
      }
    },
    headers: {
      default: new Header({
        children: [new Paragraph({
          alignment: AlignmentType.RIGHT,
          children: [new TextRun({ text: "2026 中国创新电子产品海外销售分析报告", size: 20, color: "666666" })]
        })]
      })
    },
    footers: {
      default: new Footer({
        children: [new Paragraph({
          alignment: AlignmentType.CENTER,
          children: [new TextRun({ text: "第 ", size: 20 }), new TextRun({ children: [PageNumber.CURRENT], size: 20 }), new TextRun({ text: " 页", size: 20 })]
        })]
      })
    },
    children: [
      // Title Page
      new Paragraph({
        alignment: AlignmentType.CENTER,
        spacing: { after: 600 },
        children: [new TextRun({ text: "2026 中国创新电子产品", size: 48, bold: true, font: "Arial", color: "1F4E78" })]
      }),
      new Paragraph({
        alignment: AlignmentType.CENTER,
        spacing: { after: 200 },
        children: [new TextRun({ text: "海外销售分析报告", size: 40, bold: true, font: "Arial", color: "2E5C8A" })]
      }),
      new Paragraph({ spacing: { after: 800 }, children: [new TextRun({ text: "", size: 20 })] }),
      new Paragraph({
        alignment: AlignmentType.CENTER,
        spacing: { after: 400 },
        children: [new TextRun({ text: "报告生成时间：2026 年 2 月", size: 24, color: "666666" })]
      }),
      new Paragraph({
        alignment: AlignmentType.CENTER,
        children: [new TextRun({ text: "数据来源：百度搜索、行业报告、公开信息整理", size: 24, color: "666666" })]
      }),
      new Paragraph({ children: [new PageBreak()] }),

      // Table of Contents
      new Paragraph({ heading: HeadingLevel.HEADING_1, children: [new TextRun("目录")] }),
      new TableOfContents("目录", { hyperlink: true, headingStyleRange: "1-3" }),
      new Paragraph({ children: [new PageBreak()] }),

      // Executive Summary
      new Paragraph({ heading: HeadingLevel.HEADING_1, children: [new TextRun("📋 执行摘要")] }),
      new Paragraph({
        children: [new TextRun({ text: "基于 2026 年最新市场数据，本报告分析了中国（特别是深圳华强北）发布的创新电子产品，评估其在海外市场的销售潜力，并提供 TikTok 等社交电商平台的推广策略建议。", size: 24 })]
      }),
      new Paragraph({ children: [new PageBreak()] }),

      // Chapter 1
      new Paragraph({ heading: HeadingLevel.HEADING_1, children: [new TextRun("🔥 一、2026 年国内热门创新电子产品清单")] }),
      
      new Paragraph({ heading: HeadingLevel.HEADING_2, children: [new TextRun("1.1 核心爆款品类")] }),
      
      // Product Table
      (() => {
        const border = { style: BorderStyle.SINGLE, size: 1, color: "CCCCCC" };
        const borders = { top: border, bottom: border, left: border, right: border };
        const headerBorder = { style: BorderStyle.SINGLE, size: 2, color: "1F4E78" };
        const headerBorders = { top: headerBorder, bottom: headerBorder, left: border, right: border };
        
        return new Table({
          width: { size: 9360, type: WidthType.DXA },
          columnWidths: [2000, 2500, 1500, 1500, 1860],
          rows: [
            new TableRow({
              children: [
                new TableCell({ borders: headerBorders, shading: { fill: "1F4E78", type: ShadingType.CLEAR },
                  children: [new Paragraph({ alignment: AlignmentType.CENTER, children: [new TextRun({ text: "产品类别", size: 24, bold: true, color: "FFFFFF" })] })] }),
                new TableCell({ borders: headerBorders, shading: { fill: "1F4E78", type: ShadingType.CLEAR },
                  children: [new Paragraph({ alignment: AlignmentType.CENTER, children: [new TextRun({ text: "代表产品", size: 24, bold: true, color: "FFFFFF" })] })] }),
                new TableCell({ borders: headerBorders, shading: { fill: "1F4E78", type: ShadingType.CLEAR },
                  children: [new Paragraph({ alignment: AlignmentType.CENTER, children: [new TextRun({ text: "价格区间", size: 24, bold: true, color: "FFFFFF" })] })] }),
                new TableCell({ borders: headerBorders, shading: { fill: "1F4E78", type: ShadingType.CLEAR },
                  children: [new Paragraph({ alignment: AlignmentType.CENTER, children: [new TextRun({ text: "海外热度", size: 24, bold: true, color: "FFFFFF" })] })] }),
                new TableCell({ borders: headerBorders, shading: { fill: "1F4E78", type: ShadingType.CLEAR },
                  children: [new Paragraph({ alignment: AlignmentType.CENTER, children: [new TextRun({ text: "TikTok 潜力", size: 24, bold: true, color: "FFFFFF" })] })] }),
              ]
            }),
            new TableRow({
              children: [
                new TableCell({ borders, children: [new Paragraph({ children: [new TextRun({ text: "AI 智能眼镜", size: 22 })] })] }),
                new TableCell({ borders, children: [new Paragraph({ children: [new TextRun({ text: "实时翻译眼镜、AR 导航眼镜", size: 22 })] })] }),
                new TableCell({ borders, children: [new Paragraph({ children: [new TextRun({ text: "$50-150", size: 22 })] })] }),
                new TableCell({ borders, children: [new Paragraph({ alignment: AlignmentType.CENTER, children: [new TextRun({ text: "⭐⭐⭐⭐⭐", size: 22 })] })] }),
                new TableCell({ borders, children: [new Paragraph({ alignment: AlignmentType.CENTER, children: [new TextRun({ text: "极高", size: 22, bold: true, color: "C00000" })] })] }),
              ]
            }),
            new TableRow({
              children: [
                new TableCell({ borders, children: [new Paragraph({ children: [new TextRun({ text: "智能手表/手环", size: 22 })] })] }),
                new TableCell({ borders, children: [new Paragraph({ children: [new TextRun({ text: "多功能健康监测手表", size: 22 })] })] }),
                new TableCell({ borders, children: [new Paragraph({ children: [new TextRun({ text: "$30-100", size: 22 })] })] }),
                new TableCell({ borders, children: [new Paragraph({ alignment: AlignmentType.CENTER, children: [new TextRun({ text: "⭐⭐⭐⭐⭐", size: 22 })] })] }),
                new TableCell({ borders, children: [new Paragraph({ alignment: AlignmentType.CENTER, children: [new TextRun({ text: "高", size: 22, bold: true, color: "0070C0" })] })] }),
              ]
            }),
            new TableRow({
              children: [
                new TableCell({ borders, children: [new Paragraph({ children: [new TextRun({ text: "AI 翻译耳机", size: 22 })] })] }),
                new TableCell({ borders, children: [new Paragraph({ children: [new TextRun({ text: "科大讯飞 iFLYBUDS、时空壶 W4 Pro", size: 22 })] })] }),
                new TableCell({ borders, children: [new Paragraph({ children: [new TextRun({ text: "$80-200", size: 22 })] })] }),
                new TableCell({ borders, children: [new Paragraph({ alignment: AlignmentType.CENTER, children: [new TextRun({ text: "⭐⭐⭐⭐", size: 22 })] })] }),
                new TableCell({ borders, children: [new Paragraph({ alignment: AlignmentType.CENTER, children: [new TextRun({ text: "高", size: 22, bold: true, color: "0070C0" })] })] }),
              ]
            }),
            new TableRow({
              children: [
                new TableCell({ borders, children: [new Paragraph({ children: [new TextRun({ text: "创意小 gadget", size: 22 })] })] }),
                new TableCell({ borders, children: [new Paragraph({ children: [new TextRun({ text: "智能吉他、AI 图灵琴键", size: 22 })] })] }),
                new TableCell({ borders, children: [new Paragraph({ children: [new TextRun({ text: "$100-500", size: 22 })] })] }),
                new TableCell({ borders, children: [new Paragraph({ alignment: AlignmentType.CENTER, children: [new TextRun({ text: "⭐⭐⭐", size: 22 })] })] }),
                new TableCell({ borders, children: [new Paragraph({ alignment: AlignmentType.CENTER, children: [new TextRun({ text: "高", size: 22, bold: true, color: "0070C0" })] })] }),
              ]
            }),
            new TableRow({
              children: [
                new TableCell({ borders, children: [new Paragraph({ children: [new TextRun({ text: "便携式影像设备", size: 22 })] })] }),
                new TableCell({ borders, children: [new Paragraph({ children: [new TextRun({ text: "水上摄影飞行相机", size: 22 })] })] }),
                new TableCell({ borders, children: [new Paragraph({ children: [new TextRun({ text: "$150-400", size: 22 })] })] }),
                new TableCell({ borders, children: [new Paragraph({ alignment: AlignmentType.CENTER, children: [new TextRun({ text: "⭐⭐⭐⭐", size: 22 })] })] }),
                new TableCell({ borders, children: [new Paragraph({ alignment: AlignmentType.CENTER, children: [new TextRun({ text: "极高", size: 22, bold: true, color: "C00000" })] })] }),
              ]
            }),
          ]
        });
      })(),
      
      new Paragraph({ spacing: { before: 300, after: 300 }, children: [new PageBreak()] }),
      
      new Paragraph({ heading: HeadingLevel.HEADING_2, children: [new TextRun("1.2 国外没有/少见的小众产品")] }),
      
      new Paragraph({ heading: HeadingLevel.HEADING_3, children: [new TextRun("🎯 高潜力小众产品")] }),
      
      new Paragraph({ numbering: { reference: "numbers", level: 0 }, children: [new TextRun({ text: "AI 智能眼镜（实时翻译版）", size: 24, bold: true })] }),
      new Paragraph({ numbering: { reference: "bullets", level: 0 }, children: [new TextRun({ text: "特点：支持多语言实时互译、语音控制、拍照录像", size: 22 })] }),
      new Paragraph({ numbering: { reference: "bullets", level: 0 }, children: [new TextRun({ text: "国内价格：¥300-800 | 海外售价潜力：$80-150", size: 22 })] }),
      new Paragraph({ numbering: { reference: "bullets", level: 0 }, children: [new TextRun({ text: "优势：2025 年海外销量同比涨 270%，消除跨境交流障碍", size: 22 })] }),
      new Paragraph({ numbering: { reference: "bullets", level: 0 }, children: [new TextRun({ text: "TikTok 适配性：⭐⭐⭐⭐⭐（演示效果极佳）", size: 22 })] }),
      
      new Paragraph({ spacing: { before: 150 }, numbering: { reference: "numbers", level: 0 }, children: [new TextRun({ text: "智能吉他", size: 24, bold: true })] }),
      new Paragraph({ numbering: { reference: "bullets", level: 0 }, children: [new TextRun({ text: "特点：内置教学系统、自动和弦、蓝牙连接 APP", size: 22 })] }),
      new Paragraph({ numbering: { reference: "bullets", level: 0 }, children: [new TextRun({ text: "国内价格：¥2000-3000 | 海外售价潜力：$400-600", size: 22 })] }),
      new Paragraph({ numbering: { reference: "bullets", level: 0 }, children: [new TextRun({ text: "优势：音乐学习 + 科技结合，视觉冲击强", size: 22 })] }),
      new Paragraph({ numbering: { reference: "bullets", level: 0 }, children: [new TextRun({ text: "TikTok 适配性：⭐⭐⭐⭐⭐（音乐内容天然适合）", size: 22 })] }),
      
      new Paragraph({ spacing: { before: 150 }, numbering: { reference: "numbers", level: 0 }, children: [new TextRun({ text: "AI 图灵琴键", size: 24, bold: true })] }),
      new Paragraph({ numbering: { reference: "bullets", level: 0 }, children: [new TextRun({ text: "特点：便携式智能键盘、AI 作曲辅助", size: 22 })] }),
      new Paragraph({ numbering: { reference: "bullets", level: 0 }, children: [new TextRun({ text: "国内价格：¥500-1000 | 海外售价潜力：$100-200", size: 22 })] }),
      new Paragraph({ numbering: { reference: "bullets", level: 0 }, children: [new TextRun({ text: "优势：CES 2026 创新获奖产品", size: 22 })] }),
      
      new Paragraph({ spacing: { before: 150 }, numbering: { reference: "numbers", level: 0 }, children: [new TextRun({ text: "水上摄影飞行相机", size: 24, bold: true })] }),
      new Paragraph({ numbering: { reference: "bullets", level: 0 }, children: [new TextRun({ text: "特点：防水、可飞行、自动跟拍", size: 22 })] }),
      new Paragraph({ numbering: { reference: "bullets", level: 0 }, children: [new TextRun({ text: "国内价格：¥800-2000 | 海外售价潜力：$150-350", size: 22 })] }),
      new Paragraph({ numbering: { reference: "bullets", level: 0 }, children: [new TextRun({ text: "优势：CES 2026 创新获奖，视觉内容极佳", size: 22 })] }),
      new Paragraph({ numbering: { reference: "bullets", level: 0 }, children: [new TextRun({ text: "TikTok 适配性：⭐⭐⭐⭐⭐", size: 22 })] }),
      
      new Paragraph({ spacing: { before: 150 }, numbering: { reference: "numbers", level: 0 }, children: [new TextRun({ text: "桌面 AI 伙伴/沉浸式 AI 桌面宠物", size: 24, bold: true })] }),
      new Paragraph({ numbering: { reference: "bullets", level: 0 }, children: [new TextRun({ text: "特点：情感交互、语音对话、可爱外观", size: 22 })] }),
      new Paragraph({ numbering: { reference: "bullets", level: 0 }, children: [new TextRun({ text: "国内价格：¥300-800 | 海外售价潜力：$80-150", size: 22 })] }),
      new Paragraph({ numbering: { reference: "bullets", level: 0 }, children: [new TextRun({ text: "优势：情感陪伴需求，Z 世代喜爱", size: 22 })] }),
      new Paragraph({ numbering: { reference: "bullets", level: 0 }, children: [new TextRun({ text: "TikTok 适配性：⭐⭐⭐⭐⭐", size: 22 })] }),
      
      new Paragraph({ spacing: { before: 150 }, numbering: { reference: "numbers", level: 0 }, children: [new TextRun({ text: "AI 戒指", size: 24, bold: true })] }),
      new Paragraph({ numbering: { reference: "bullets", level: 0 }, children: [new TextRun({ text: "特点：健康监测、手势控制、极简设计", size: 22 })] }),
      new Paragraph({ numbering: { reference: "bullets", level: 0 }, children: [new TextRun({ text: "国内价格：¥200-500 | 海外售价潜力：$60-120", size: 22 })] }),
      new Paragraph({ numbering: { reference: "bullets", level: 0 }, children: [new TextRun({ text: "优势：比智能手表更隐蔽、时尚", size: 22 })] }),
      new Paragraph({ numbering: { reference: "bullets", level: 0 }, children: [new TextRun({ text: "TikTok 适配性：⭐⭐⭐⭐", size: 22 })] }),
      
      new Paragraph({ children: [new PageBreak()] }),

      // Chapter 2
      new Paragraph({ heading: HeadingLevel.HEADING_1, children: [new TextRun("🌍 二、海外市场销售潜力分析")] }),
      
      new Paragraph({ heading: HeadingLevel.HEADING_2, children: [new TextRun("2.1 目标市场优先级")] }),
      
      (() => {
        const border = { style: BorderStyle.SINGLE, size: 1, color: "CCCCCC" };
        const borders = { top: border, bottom: border, left: border, right: border };
        const headerBorder = { style: BorderStyle.SINGLE, size: 2, color: "1F4E78" };
        const headerBorders = { top: headerBorder, bottom: headerBorder, left: border, right: border };
        
        return new Table({
          width: { size: 9360, type: WidthType.DXA },
          columnWidths: [1800, 1400, 1600, 1600, 1500, 1460],
          rows: [
            new TableRow({
              children: [
                new TableCell({ borders: headerBorders, shading: { fill: "1F4E78", type: ShadingType.CLEAR },
                  children: [new Paragraph({ alignment: AlignmentType.CENTER, children: [new TextRun({ text: "市场", size: 22, bold: true, color: "FFFFFF" })] })] }),
                new TableCell({ borders: headerBorders, shading: { fill: "1F4E78", type: ShadingType.CLEAR },
                  children: [new Paragraph({ alignment: AlignmentType.CENTER, children: [new TextRun({ text: "优先级", size: 22, bold: true, color: "FFFFFF" })] })] }),
                new TableCell({ borders: headerBorders, shading: { fill: "1F4E78", type: ShadingType.CLEAR },
                  children: [new Paragraph({ alignment: AlignmentType.CENTER, children: [new TextRun({ text: "电商渗透率", size: 22, bold: true, color: "FFFFFF" })] })] }),
                new TableCell({ borders: headerBorders, shading: { fill: "1F4E78", type: ShadingType.CLEAR },
                  children: [new Paragraph({ alignment: AlignmentType.CENTER, children: [new TextRun({ text: "TikTok 用户", size: 22, bold: true, color: "FFFFFF" })] })] }),
                new TableCell({ borders: headerBorders, shading: { fill: "1F4E78", type: ShadingType.CLEAR },
                  children: [new Paragraph({ alignment: AlignmentType.CENTER, children: [new TextRun({ text: "物流时效", size: 22, bold: true, color: "FFFFFF" })] })] }),
                new TableCell({ borders: headerBorders, shading: { fill: "1F4E78", type: ShadingType.CLEAR },
                  children: [new Paragraph({ alignment: AlignmentType.CENTER, children: [new TextRun({ text: "竞争程度", size: 22, bold: true, color: "FFFFFF" })] })] }),
              ]
            }),
            new TableRow({
              children: [
                new TableCell({ borders, children: [new Paragraph({ children: [new TextRun({ text: "东南亚", size: 22 })] })] }),
                new TableCell({ borders, children: [new Paragraph({ alignment: AlignmentType.CENTER, children: [new TextRun({ text: "⭐⭐⭐⭐⭐", size: 22 })] })] }),
                new TableCell({ borders, children: [new Paragraph({ children: [new TextRun({ text: "<30%", size: 22 })] })] }),
                new TableCell({ borders, children: [new Paragraph({ children: [new TextRun({ text: "极高", size: 22 })] })] }),
                new TableCell({ borders, children: [new Paragraph({ children: [new TextRun({ text: "3-7 天", size: 22 })] })] }),
                new TableCell({ borders, children: [new Paragraph({ children: [new TextRun({ text: "中", size: 22 })] })] }),
              ]
            }),
            new TableRow({
              children: [
                new TableCell({ borders, children: [new Paragraph({ children: [new TextRun({ text: "拉美", size: 22 })] })] }),
                new TableCell({ borders, children: [new Paragraph({ alignment: AlignmentType.CENTER, children: [new TextRun({ text: "⭐⭐⭐⭐", size: 22 })] })] }),
                new TableCell({ borders, children: [new Paragraph({ children: [new TextRun({ text: "~35%", size: 22 })] })] }),
                new TableCell({ borders, children: [new Paragraph({ children: [new TextRun({ text: "高", size: 22 })] })] }),
                new TableCell({ borders, children: [new Paragraph({ children: [new TextRun({ text: "7-15 天", size: 22 })] })] }),
                new TableCell({ borders, children: [new Paragraph({ children: [new TextRun({ text: "低", size: 22 })] })] }),
              ]
            }),
            new TableRow({
              children: [
                new TableCell({ borders, children: [new Paragraph({ children: [new TextRun({ text: "中东", size: 22 })] })] }),
                new TableCell({ borders, children: [new Paragraph({ alignment: AlignmentType.CENTER, children: [new TextRun({ text: "⭐⭐⭐⭐", size: 22 })] })] }),
                new TableCell({ borders, children: [new Paragraph({ children: [new TextRun({ text: "~40%", size: 22 })] })] }),
                new TableCell({ borders, children: [new Paragraph({ children: [new TextRun({ text: "中高", size: 22 })] })] }),
                new TableCell({ borders, children: [new Paragraph({ children: [new TextRun({ text: "5-10 天", size: 22 })] })] }),
                new TableCell({ borders, children: [new Paragraph({ children: [new TextRun({ text: "低", size: 22 })] })] }),
              ]
            }),
            new TableRow({
              children: [
                new TableCell({ borders, children: [new Paragraph({ children: [new TextRun({ text: "美国", size: 22 })] })] }),
                new TableCell({ borders, children: [new Paragraph({ alignment: AlignmentType.CENTER, children: [new TextRun({ text: "⭐⭐⭐", size: 22 })] })] }),
                new TableCell({ borders, children: [new Paragraph({ children: [new TextRun({ text: "~80%", size: 22 })] })] }),
                new TableCell({ borders, children: [new Paragraph({ children: [new TextRun({ text: "高", size: 22 })] })] }),
                new TableCell({ borders, children: [new Paragraph({ children: [new TextRun({ text: "3-7 天", size: 22 })] })] }),
                new TableCell({ borders, children: [new Paragraph({ children: [new TextRun({ text: "高", size: 22 })] })] }),
              ]
            }),
          ]
        });
      })(),
      
      new Paragraph({ spacing: { before: 300 }, heading: HeadingLevel.HEADING_2, children: [new TextRun("2.2 产品 - 市场匹配分析")] }),
      
      new Paragraph({ heading: HeadingLevel.HEADING_3, children: [new TextRun("东南亚市场（首选）")] }),
      new Paragraph({ numbering: { reference: "bullets", level: 0 }, children: [new TextRun({ text: "推荐产品：AI 智能眼镜、智能手表、AI 翻译耳机", size: 22 })] }),
      new Paragraph({ numbering: { reference: "bullets", level: 0 }, children: [new TextRun({ text: "2025 年 TikTok Shop 东南亚 GMV 增速突破 120%", size: 22 })] }),
      new Paragraph({ numbering: { reference: "bullets", level: 0 }, children: [new TextRun({ text: "电脑办公设备增速近 5 倍", size: 22 })] }),
      new Paragraph({ numbering: { reference: "bullets", level: 0 }, children: [new TextRun({ text: "价格敏感，中国产品性价比高", size: 22 })] }),
      new Paragraph({ numbering: { reference: "bullets", level: 0 }, children: [new TextRun({ text: "RCEP 协议生效后物流时效缩短", size: 22 })] }),
      
      new Paragraph({ spacing: { before: 200 }, heading: HeadingLevel.HEADING_3, children: [new TextRun("拉美市场（次选）")] }),
      new Paragraph({ numbering: { reference: "bullets", level: 0 }, children: [new TextRun({ text: "推荐产品：智能穿戴、创意小 gadget、影像设备", size: 22 })] }),
      new Paragraph({ numbering: { reference: "bullets", level: 0 }, children: [new TextRun({ text: "电商渗透率低，增长空间大", size: 22 })] }),
      new Paragraph({ numbering: { reference: "bullets", level: 0 }, children: [new TextRun({ text: "对中国电子产品接受度高", size: 22 })] }),
      new Paragraph({ numbering: { reference: "bullets", level: 0 }, children: [new TextRun({ text: "竞争相对较小", size: 22 })] }),
      
      new Paragraph({ spacing: { before: 200 }, heading: HeadingLevel.HEADING_3, children: [new TextRun("中东市场")] }),
      new Paragraph({ numbering: { reference: "bullets", level: 0 }, children: [new TextRun({ text: "推荐产品：智能家居、穆斯林时尚科技产品、宠物用品", size: 22 })] }),
      new Paragraph({ numbering: { reference: "bullets", level: 0 }, children: [new TextRun({ text: "高消费能力", size: 22 })] }),
      new Paragraph({ numbering: { reference: "bullets", level: 0 }, children: [new TextRun({ text: "对新产品接受度高", size: 22 })] }),
      
      new Paragraph({ children: [new PageBreak()] }),

      // Chapter 3
      new Paragraph({ heading: HeadingLevel.HEADING_1, children: [new TextRun("📱 三、TikTok 推广策略")] }),
      
      new Paragraph({ heading: HeadingLevel.HEADING_2, children: [new TextRun("3.1 内容策略")] }),
      new Paragraph({ heading: HeadingLevel.HEADING_3, children: [new TextRun("高转化内容类型")] }),
      
      new Paragraph({ numbering: { reference: "numbers", level: 0 }, children: [new TextRun({ text: "产品演示视频（15-30 秒）", size: 24, bold: true })] }),
      new Paragraph({ numbering: { reference: "bullets", level: 0 }, children: [new TextRun({ text: "展示产品核心功能的\"wow moment\"", size: 22 })] }),
      new Paragraph({ numbering: { reference: "bullets", level: 0 }, children: [new TextRun({ text: "例如：AI 眼镜实时翻译不同语言", size: 22 })] }),
      
      new Paragraph({ spacing: { before: 150 }, numbering: { reference: "numbers", level: 0 }, children: [new TextRun({ text: "使用场景短视频", size: 24, bold: true })] }),
      new Paragraph({ numbering: { reference: "bullets", level: 0 }, children: [new TextRun({ text: "真实生活场景中的应用", size: 22 })] }),
      new Paragraph({ numbering: { reference: "bullets", level: 0 }, children: [new TextRun({ text: "例如：智能吉他在派对上的表现", size: 22 })] }),
      
      new Paragraph({ spacing: { before: 150 }, numbering: { reference: "numbers", level: 0 }, children: [new TextRun({ text: "对比视频", size: 24, bold: true })] }),
      new Paragraph({ numbering: { reference: "bullets", level: 0 }, children: [new TextRun({ text: "传统产品 vs 智能产品", size: 22 })] }),
      new Paragraph({ numbering: { reference: "bullets", level: 0 }, children: [new TextRun({ text: "价格对比（中国直邮 vs 本地售价）", size: 22 })] }),
      
      new Paragraph({ spacing: { before: 150 }, numbering: { reference: "numbers", level: 0 }, children: [new TextRun({ text: "用户生成内容（UGC）", size: 24, bold: true })] }),
      new Paragraph({ numbering: { reference: "bullets", level: 0 }, children: [new TextRun({ text: "鼓励买家分享使用体验", size: 22 })] }),
      new Paragraph({ numbering: { reference: "bullets", level: 0 }, children: [new TextRun({ text: "设置挑战赛/话题标签", size: 22 })] }),
      
      new Paragraph({ spacing: { before: 300 }, heading: HeadingLevel.HEADING_2, children: [new TextRun("3.2 运营策略")] }),
      
      new Paragraph({ heading: HeadingLevel.HEADING_3, children: [new TextRun("店铺搭建")] }),
      new Paragraph({ numbering: { reference: "bullets", level: 0 }, children: [new TextRun({ text: "TikTok Shop 美区/东南亚区：优先开通", size: 22 })] }),
      new Paragraph({ numbering: { reference: "bullets", level: 0 }, children: [new TextRun({ text: "全球库存 + 本地履约：采用易仓 ERP 管理", size: 22 })] }),
      new Paragraph({ numbering: { reference: "bullets", level: 0 }, children: [new TextRun({ text: "多平台利润对比：资源向 TikTok Shop 倾斜", size: 22 })] }),
      
      new Paragraph({ spacing: { before: 200 }, heading: HeadingLevel.HEADING_3, children: [new TextRun("流量获取")] }),
      new Paragraph({ numbering: { reference: "bullets", level: 0 }, children: [new TextRun({ text: "短视频带货：日更 3-5 条", size: 22 })] }),
      new Paragraph({ numbering: { reference: "bullets", level: 0 }, children: [new TextRun({ text: "直播带货：每周 3-5 场，每场 2-4 小时", size: 22 })] }),
      new Paragraph({ numbering: { reference: "bullets", level: 0 }, children: [new TextRun({ text: "达人合作：寻找垂直领域 KOL（科技、生活方式）", size: 22 })] }),
      new Paragraph({ numbering: { reference: "bullets", level: 0 }, children: [new TextRun({ text: "付费广告：初期测试，ROI>2 后加大投入", size: 22 })] }),
      
      new Paragraph({ spacing: { before: 200 }, heading: HeadingLevel.HEADING_3, children: [new TextRun("转化优化")] }),
      new Paragraph({ numbering: { reference: "bullets", level: 0 }, children: [new TextRun({ text: "橱窗优化：高质量主图 + 视频", size: 22 })] }),
      new Paragraph({ numbering: { reference: "bullets", level: 0 }, children: [new TextRun({ text: "价格策略：心理定价（$49.99 而非$50）", size: 22 })] }),
      new Paragraph({ numbering: { reference: "bullets", level: 0 }, children: [new TextRun({ text: "限时促销：制造紧迫感", size: 22 })] }),
      new Paragraph({ numbering: { reference: "bullets", level: 0 }, children: [new TextRun({ text: "评价管理：积极回复，处理差评", size: 22 })] }),
      
      new Paragraph({ spacing: { before: 300 }, heading: HeadingLevel.HEADING_2, children: [new TextRun("3.3 成功案例参考")] }),
      
      new Paragraph({ heading: HeadingLevel.HEADING_3, children: [new TextRun("案例 1：水晶灯在 TikTok 大火")] }),
      new Paragraph({ numbering: { reference: "bullets", level: 0 }, children: [new TextRun({ text: "产品：几块钱的水晶装饰灯", size: 22 })] }),
      new Paragraph({ numbering: { reference: "bullets", level: 0 }, children: [new TextRun({ text: "结果：卖家 7 天进账 60 万", size: 22 })] }),
      new Paragraph({ numbering: { reference: "bullets", level: 0 }, children: [new TextRun({ text: "成功因素：视觉效果强、价格低、易传播", size: 22 })] }),
      
      new Paragraph({ spacing: { before: 200 }, heading: HeadingLevel.HEADING_3, children: [new TextRun("案例 2：AI 智能眼镜")] }),
      new Paragraph({ numbering: { reference: "bullets", level: 0 }, children: [new TextRun({ text: "2025 年海外销量同比涨 270%", size: 22 })] }),
      new Paragraph({ numbering: { reference: "bullets", level: 0 }, children: [new TextRun({ text: "成功因素：功能实用、演示效果好、解决痛点", size: 22 })] }),
      
      new Paragraph({ children: [new PageBreak()] }),

      // Chapter 4
      new Paragraph({ heading: HeadingLevel.HEADING_1, children: [new TextRun("⚠️ 四、风险与挑战")] }),
      
      new Paragraph({ heading: HeadingLevel.HEADING_2, children: [new TextRun("4.1 主要风险")] }),
      
      (() => {
        const border = { style: BorderStyle.SINGLE, size: 1, color: "CCCCCC" };
        const borders = { top: border, bottom: border, left: border, right: border };
        const headerBorder = { style: BorderStyle.SINGLE, size: 2, color: "1F4E78" };
        const headerBorders = { top: headerBorder, bottom: headerBorder, left: border, right: border };
        
        return new Table({
          width: { size: 9360, type: WidthType.DXA },
          columnWidths: [2200, 4000, 3160],
          rows: [
            new TableRow({
              children: [
                new TableCell({ borders: headerBorders, shading: { fill: "1F4E78", type: ShadingType.CLEAR },
                  children: [new Paragraph({ alignment: AlignmentType.CENTER, children: [new TextRun({ text: "风险类型", size: 22, bold: true, color: "FFFFFF" })] })] }),
                new TableCell({ borders: headerBorders, shading: { fill: "1F4E78", type: ShadingType.CLEAR },
                  children: [new Paragraph({ alignment: AlignmentType.CENTER, children: [new TextRun({ text: "描述", size: 22, bold: true, color: "FFFFFF" })] })] }),
                new TableCell({ borders: headerBorders, shading: { fill: "1F4E78", type: ShadingType.CLEAR },
                  children: [new Paragraph({ alignment: AlignmentType.CENTER, children: [new TextRun({ text: "应对策略", size: 22, bold: true, color: "FFFFFF" })] })] }),
              ]
            }),
            new TableRow({
              children: [
                new TableCell({ borders, children: [new Paragraph({ children: [new TextRun({ text: "政策风险", size: 22, bold: true })] })] }),
                new TableCell({ borders, children: [new Paragraph({ children: [new TextRun({ text: "TikTok 美国业务不确定性", size: 22 })] })] }),
                new TableCell({ borders, children: [new Paragraph({ children: [new TextRun({ text: "多市场布局，不依赖单一市场", size: 22 })] })] }),
              ]
            }),
            new TableRow({
              children: [
                new TableCell({ borders, children: [new Paragraph({ children: [new TextRun({ text: "物流风险", size: 22, bold: true })] })] }),
                new TableCell({ borders, children: [new Paragraph({ children: [new TextRun({ text: "跨境物流时效不稳定", size: 22 })] })] }),
                new TableCell({ borders, children: [new Paragraph({ children: [new TextRun({ text: "海外仓备货，多物流商合作", size: 22 })] })] }),
              ]
            }),
            new TableRow({
              children: [
                new TableCell({ borders, children: [new Paragraph({ children: [new TextRun({ text: "合规风险", size: 22, bold: true })] })] }),
                new TableCell({ borders, children: [new Paragraph({ children: [new TextRun({ text: "产品认证（CE/FCC 等）", size: 22 })] })] }),
                new TableCell({ borders, children: [new Paragraph({ children: [new TextRun({ text: "提前办理目标市场认证", size: 22 })] })] }),
              ]
            }),
            new TableRow({
              children: [
                new TableCell({ borders, children: [new Paragraph({ children: [new TextRun({ text: "竞争风险", size: 22, bold: true })] })] }),
                new TableCell({ borders, children: [new Paragraph({ children: [new TextRun({ text: "跟卖、价格战", size: 22 })] })] }),
                new TableCell({ borders, children: [new Paragraph({ children: [new TextRun({ text: "品牌化、差异化、快速迭代", size: 22 })] })] }),
              ]
            }),
            new TableRow({
              children: [
                new TableCell({ borders, children: [new Paragraph({ children: [new TextRun({ text: "售后风险", size: 22, bold: true })] })] }),
                new TableCell({ borders, children: [new Paragraph({ children: [new TextRun({ text: "退换货成本高", size: 22 })] })] }),
                new TableCell({ borders, children: [new Paragraph({ children: [new TextRun({ text: "清晰的产品说明，视频指导", size: 22 })] })] }),
              ]
            }),
          ]
        });
      })(),
      
      new Paragraph({ spacing: { before: 300 }, heading: HeadingLevel.HEADING_2, children: [new TextRun("4.2 产品选择注意事项")] }),
      new Paragraph({ numbering: { reference: "numbers", level: 0 }, children: [new TextRun({ text: "避免侵权产品：不碰大牌仿品", size: 22 })] }),
      new Paragraph({ numbering: { reference: "numbers", level: 0 }, children: [new TextRun({ text: "认证要求：电子产品需 CE/FCC/RoHS 认证", size: 22 })] }),
      new Paragraph({ numbering: { reference: "numbers", level: 0 }, children: [new TextRun({ text: "电池限制：含锂电池产品物流受限", size: 22 })] }),
      new Paragraph({ numbering: { reference: "numbers", level: 0 }, children: [new TextRun({ text: "电压适配：确保符合目标市场电压标准", size: 22 })] }),
      
      new Paragraph({ children: [new PageBreak()] }),

      // Chapter 5
      new Paragraph({ heading: HeadingLevel.HEADING_1, children: [new TextRun("💡 五、行动建议")] }),
      
      new Paragraph({ heading: HeadingLevel.HEADING_2, children: [new TextRun("5.1 第一阶段（1-2 个月）：测试期")] }),
      new Paragraph({ heading: HeadingLevel.HEADING_3, children: [new TextRun("选品测试")] }),
      new Paragraph({ numbering: { reference: "bullets", level: 0 }, children: [new TextRun({ text: "选择 3-5 款产品进行小规模测试", size: 22 })] }),
      new Paragraph({ numbering: { reference: "bullets", level: 0 }, children: [new TextRun({ text: "推荐：AI 智能眼镜、智能手表、创意小 gadget", size: 22 })] }),
      new Paragraph({ numbering: { reference: "bullets", level: 0 }, children: [new TextRun({ text: "每款产品准备 50-100 件库存", size: 22 })] }),
      
      new Paragraph({ spacing: { before: 150 }, heading: HeadingLevel.HEADING_3, children: [new TextRun("内容测试")] }),
      new Paragraph({ numbering: { reference: "bullets", level: 0 }, children: [new TextRun({ text: "每日发布 3-5 条短视频", size: 22 })] }),
      new Paragraph({ numbering: { reference: "bullets", level: 0 }, children: [new TextRun({ text: "测试不同内容类型的转化率", size: 22 })] }),
      new Paragraph({ numbering: { reference: "bullets", level: 0 }, children: [new TextRun({ text: "找到最适合的内容形式", size: 22 })] }),
      
      new Paragraph({ spacing: { before: 150 }, heading: HeadingLevel.HEADING_3, children: [new TextRun("数据收集")] }),
      new Paragraph({ numbering: { reference: "bullets", level: 0 }, children: [new TextRun({ text: "追踪每个产品的点击率、转化率、ROI", size: 22 })] }),
      new Paragraph({ numbering: { reference: "bullets", level: 0 }, children: [new TextRun({ text: "记录用户反馈和常见问题", size: 22 })] }),
      
      new Paragraph({ spacing: { before: 300 }, heading: HeadingLevel.HEADING_2, children: [new TextRun("5.2 第二阶段（3-6 个月）：扩张期")] }),
      new Paragraph({ heading: HeadingLevel.HEADING_3, children: [new TextRun("爆品放大")] }),
      new Paragraph({ numbering: { reference: "bullets", level: 0 }, children: [new TextRun({ text: "加大表现最好的产品库存", size: 22 })] }),
      new Paragraph({ numbering: { reference: "bullets", level: 0 }, children: [new TextRun({ text: "增加广告投入", size: 22 })] }),
      new Paragraph({ numbering: { reference: "bullets", level: 0 }, children: [new TextRun({ text: "拓展更多达人合作", size: 22 })] }),
      
      new Paragraph({ spacing: { before: 150 }, heading: HeadingLevel.HEADING_3, children: [new TextRun("海外仓布局")] }),
      new Paragraph({ numbering: { reference: "bullets", level: 0 }, children: [new TextRun({ text: "在主要市场（东南亚、美国）设置海外仓", size: 22 })] }),
      new Paragraph({ numbering: { reference: "bullets", level: 0 }, children: [new TextRun({ text: "缩短物流时效至 3-5 天", size: 22 })] }),
      
      new Paragraph({ spacing: { before: 150 }, heading: HeadingLevel.HEADING_3, children: [new TextRun("品牌建设")] }),
      new Paragraph({ numbering: { reference: "bullets", level: 0 }, children: [new TextRun({ text: "注册品牌商标", size: 22 })] }),
      new Paragraph({ numbering: { reference: "bullets", level: 0 }, children: [new TextRun({ text: "设计统一的品牌视觉", size: 22 })] }),
      new Paragraph({ numbering: { reference: "bullets", level: 0 }, children: [new TextRun({ text: "建立品牌独立站", size: 22 })] }),
      
      new Paragraph({ spacing: { before: 300 }, heading: HeadingLevel.HEADING_2, children: [new TextRun("5.3 第三阶段（6-12 个月）：成熟期")] }),
      new Paragraph({ heading: HeadingLevel.HEADING_3, children: [new TextRun("产品线扩展")] }),
      new Paragraph({ numbering: { reference: "bullets", level: 0 }, children: [new TextRun({ text: "基于数据开发新品", size: 22 })] }),
      new Paragraph({ numbering: { reference: "bullets", level: 0 }, children: [new TextRun({ text: "与工厂合作定制独家产品", size: 22 })] }),
      new Paragraph({ numbering: { reference: "bullets", level: 0 }, children: [new TextRun({ text: "建立产品护城河", size: 22 })] }),
      
      new Paragraph({ spacing: { before: 150 }, heading: HeadingLevel.HEADING_3, children: [new TextRun("多渠道布局")] }),
      new Paragraph({ numbering: { reference: "bullets", level: 0 }, children: [new TextRun({ text: "拓展亚马逊、独立站等渠道", size: 22 })] }),
      new Paragraph({ numbering: { reference: "bullets", level: 0 }, children: [new TextRun({ text: "不依赖单一平台", size: 22 })] }),
      
      new Paragraph({ spacing: { before: 150 }, heading: HeadingLevel.HEADING_3, children: [new TextRun("团队搭建")] }),
      new Paragraph({ numbering: { reference: "bullets", level: 0 }, children: [new TextRun({ text: "组建专业运营团队", size: 22 })] }),
      new Paragraph({ numbering: { reference: "bullets", level: 0 }, children: [new TextRun({ text: "建立标准化 SOP", size: 22 })] }),
      
      new Paragraph({ children: [new PageBreak()] }),

      // Chapter 6
      new Paragraph({ heading: HeadingLevel.HEADING_1, children: [new TextRun("📊 六、财务预估")] }),
      
      new Paragraph({ heading: HeadingLevel.HEADING_2, children: [new TextRun("6.1 启动成本（首月）")] }),
      
      (() => {
        const border = { style: BorderStyle.SINGLE, size: 1, color: "CCCCCC" };
        const borders = { top: border, bottom: border, left: border, right: border };
        const headerBorder = { style: BorderStyle.SINGLE, size: 2, color: "1F4E78" };
        const headerBorders = { top: headerBorder, bottom: headerBorder, left: border, right: border };
        
        return new Table({
          width: { size: 9360, type: WidthType.DXA },
          columnWidths: [5000, 4360],
          rows: [
            new TableRow({
              children: [
                new TableCell({ borders: headerBorders, shading: { fill: "1F4E78", type: ShadingType.CLEAR },
                  children: [new Paragraph({ children: [new TextRun({ text: "项目", size: 22, bold: true, color: "FFFFFF" })] })] }),
                new TableCell({ borders: headerBorders, shading: { fill: "1F4E78", type: ShadingType.CLEAR },
                  children: [new Paragraph({ alignment: AlignmentType.CENTER, children: [new TextRun({ text: "预算", size: 22, bold: true, color: "FFFFFF" })] })] }),
              ]
            }),
            new TableRow({
              children: [
                new TableCell({ borders, children: [new Paragraph({ children: [new TextRun({ text: "产品采购（5 款×50 件）", size: 22 })] })] }),
                new TableCell({ borders, children: [new Paragraph({ alignment: AlignmentType.RIGHT, children: [new TextRun({ text: "$2,000-5,000", size: 22 })] })] }),
              ]
            }),
            new TableRow({
              children: [
                new TableCell({ borders, children: [new Paragraph({ children: [new TextRun({ text: "TikTok Shop 保证金", size: 22 })] })] }),
                new TableCell({ borders, children: [new Paragraph({ alignment: AlignmentType.RIGHT, children: [new TextRun({ text: "$500-2,000", size: 22 })] })] }),
              ]
            }),
            new TableRow({
              children: [
                new TableCell({ borders, children: [new Paragraph({ children: [new TextRun({ text: "内容制作（设备 + 人力）", size: 22 })] })] }),
                new TableCell({ borders, children: [new Paragraph({ alignment: AlignmentType.RIGHT, children: [new TextRun({ text: "$500-1,000", size: 22 })] })] }),
              ]
            }),
            new TableRow({
              children: [
                new TableCell({ borders, children: [new Paragraph({ children: [new TextRun({ text: "广告测试预算", size: 22 })] })] }),
                new TableCell({ borders, children: [new Paragraph({ alignment: AlignmentType.RIGHT, children: [new TextRun({ text: "$1,000-3,000", size: 22 })] })] }),
              ]
            }),
            new TableRow({
              children: [
                new TableCell({ borders, children: [new Paragraph({ children: [new TextRun({ text: "物流费用", size: 22 })] })] }),
                new TableCell({ borders, children: [new Paragraph({ alignment: AlignmentType.RIGHT, children: [new TextRun({ text: "$500-1,000", size: 22 })] })] }),
              ]
            }),
            new TableRow({
              children: [
                new TableCell({ borders: { top: { style: BorderStyle.SINGLE, size: 3, color: "1F4E78" }, bottom: border, left: border, right: border },
                  shading: { fill: "D5E8F0", type: ShadingType.CLEAR },
                  children: [new Paragraph({ children: [new TextRun({ text: "总计", size: 24, bold: true })] })] }),
                new TableCell({ borders: { top: { style: BorderStyle.SINGLE, size: 3, color: "1F4E78" }, bottom: border, left: border, right: border },
                  shading: { fill: "D5E8F0", type: ShadingType.CLEAR },
                  children: [new Paragraph({ alignment: AlignmentType.RIGHT, children: [new TextRun({ text: "$4,500-12,000", size: 24, bold: true, color: "1F4E78" })] })] }),
              ]
            }),
          ]
        });
      })(),
      
      new Paragraph({ spacing: { before: 300 }, heading: HeadingLevel.HEADING_2, children: [new TextRun("6.2 收益预估（保守）")] }),
      
      (() => {
        const border = { style: BorderStyle.SINGLE, size: 1, color: "CCCCCC" };
        const borders = { top: border, bottom: border, left: border, right: border };
        const headerBorder = { style: BorderStyle.SINGLE, size: 2, color: "1F4E78" };
        const headerBorders = { top: headerBorder, bottom: headerBorder, left: border, right: border };
        
        return new Table({
          width: { size: 9360, type: WidthType.DXA },
          columnWidths: [2000, 2500, 2400, 2460],
          rows: [
            new TableRow({
              children: [
                new TableCell({ borders: headerBorders, shading: { fill: "1F4E78", type: ShadingType.CLEAR },
                  children: [new Paragraph({ alignment: AlignmentType.CENTER, children: [new TextRun({ text: "月份", size: 22, bold: true, color: "FFFFFF" })] })] }),
                new TableCell({ borders: headerBorders, shading: { fill: "1F4E78", type: ShadingType.CLEAR },
                  children: [new Paragraph({ alignment: AlignmentType.CENTER, children: [new TextRun({ text: "销售额", size: 22, bold: true, color: "FFFFFF" })] })] }),
                new TableCell({ borders: headerBorders, shading: { fill: "1F4E78", type: ShadingType.CLEAR },
                  children: [new Paragraph({ alignment: AlignmentType.CENTER, children: [new TextRun({ text: "利润率", size: 22, bold: true, color: "FFFFFF" })] })] }),
                new TableCell({ borders: headerBorders, shading: { fill: "1F4E78", type: ShadingType.CLEAR },
                  children: [new Paragraph({ alignment: AlignmentType.CENTER, children: [new TextRun({ text: "净利润", size: 22, bold: true, color: "FFFFFF" })] })] }),
              ]
            }),
            new TableRow({
              children: [
                new TableCell({ borders, children: [new Paragraph({ children: [new TextRun({ text: "第 1 月", size: 22 })] })] }),
                new TableCell({ borders, children: [new Paragraph({ children: [new TextRun({ text: "$3,000-5,000", size: 22 })] })] }),
                new TableCell({ borders, children: [new Paragraph({ children: [new TextRun({ text: "20-30%", size: 22 })] })] }),
                new TableCell({ borders, children: [new Paragraph({ children: [new TextRun({ text: "$600-1,500", size: 22 })] })] }),
              ]
            }),
            new TableRow({
              children: [
                new TableCell({ borders, children: [new Paragraph({ children: [new TextRun({ text: "第 3 月", size: 22 })] })] }),
                new TableCell({ borders, children: [new Paragraph({ children: [new TextRun({ text: "$10,000-20,000", size: 22 })] })] }),
                new TableCell({ borders, children: [new Paragraph({ children: [new TextRun({ text: "25-35%", size: 22 })] })] }),
                new TableCell({ borders, children: [new Paragraph({ children: [new TextRun({ text: "$2,500-7,000", size: 22 })] })] }),
              ]
            }),
            new TableRow({
              children: [
                new TableCell({ borders, children: [new Paragraph({ children: [new TextRun({ text: "第 6 月", size: 22 })] })] }),
                new TableCell({ borders, children: [new Paragraph({ children: [new TextRun({ text: "$30,000-50,000", size: 22 })] })] }),
                new TableCell({ borders, children: [new Paragraph({ children: [new TextRun({ text: "30-40%", size: 22 })] })] }),
                new TableCell({ borders, children: [new Paragraph({ children: [new TextRun({ text: "$9,000-20,000", size: 22 })] })] }),
              ]
            }),
            new TableRow({
              children: [
                new TableCell({ borders, children: [new Paragraph({ children: [new TextRun({ text: "第 12 月", size: 22 })] })] }),
                new TableCell({ borders, children: [new Paragraph({ children: [new TextRun({ text: "$100,000+", size: 22 })] })] }),
                new TableCell({ borders, children: [new Paragraph({ children: [new TextRun({ text: "30-40%", size: 22 })] })] }),
                new TableCell({ borders, children: [new Paragraph({ children: [new TextRun({ text: "$30,000+", size: 22 })] })] }),
              ]
            }),
          ]
        });
      })(),
      
      new Paragraph({ children: [new PageBreak()] }),

      // Chapter 7
      new Paragraph({ heading: HeadingLevel.HEADING_1, children: [new TextRun("🎯 七、结论")] }),
      
      new Paragraph({ heading: HeadingLevel.HEADING_2, children: [new TextRun("核心建议")] }),
      new Paragraph({ numbering: { reference: "numbers", level: 0 }, children: [new TextRun({ text: "首选产品：AI 智能眼镜、智能穿戴、创意小 gadget", size: 22 })] }),
      new Paragraph({ numbering: { reference: "numbers", level: 0 }, children: [new TextRun({ text: "首选市场：东南亚 > 拉美 > 中东 > 美国", size: 22 })] }),
      new Paragraph({ numbering: { reference: "numbers", level: 0 }, children: [new TextRun({ text: "核心策略：TikTok 短视频 + 直播 + 达人合作", size: 22 })] }),
      new Paragraph({ numbering: { reference: "numbers", level: 0 }, children: [new TextRun({ text: "关键成功因素：", size: 22, bold: true })] }),
      new Paragraph({ numbering: { reference: "bullets", level: 0 }, children: [new TextRun({ text: "选品准确（视觉冲击强、功能新颖）", size: 22 })] }),
      new Paragraph({ numbering: { reference: "bullets", level: 0 }, children: [new TextRun({ text: "内容质量高（真实、有趣、有共鸣）", size: 22 })] }),
      new Paragraph({ numbering: { reference: "bullets", level: 0 }, children: [new TextRun({ text: "供应链稳定（快速补货、质量可控）", size: 22 })] }),
      new Paragraph({ numbering: { reference: "bullets", level: 0 }, children: [new TextRun({ text: "合规经营（认证齐全、不侵权）", size: 22 })] }),
      
      new Paragraph({ spacing: { before: 300 }, heading: HeadingLevel.HEADING_2, children: [new TextRun("最后提醒")] }),
      new Paragraph({ numbering: { reference: "numbers", level: 0 }, children: [new TextRun({ text: "2026 年跨境电商已从流量红利期转向深度运营阶段", size: 22 })] }),
      new Paragraph({ numbering: { reference: "numbers", level: 0 }, children: [new TextRun({ text: "TikTok Shop 仍是核心增长引擎，但需要精细化运营", size: 22 })] }),
      new Paragraph({ numbering: { reference: "numbers", level: 0 }, children: [new TextRun({ text: "不要期待一夜暴富，做好 3-6 个月的测试和积累", size: 22 })] }),
      new Paragraph({ numbering: { reference: "numbers", level: 0 }, children: [new TextRun({ text: "保持学习，紧跟平台政策和市场趋势", size: 22 })] }),
      
      new Paragraph({ spacing: { before: 600 }, children: [new PageBreak()] }),
      
      // End page
      new Paragraph({
        alignment: AlignmentType.CENTER,
        spacing: { before: 400 },
        children: [new TextRun({ text: "感谢阅读", size: 32, bold: true, color: "1F4E78" })]
      }),
      new Paragraph({
        alignment: AlignmentType.CENTER,
        children: [new TextRun({ text: "如有任何问题，欢迎随时联系", size: 24, color: "666666" })]
      }),
    ]
  }]
});

Packer.toBuffer(doc).then(buffer => {
  fs.writeFileSync('/home/22607104_wy/openclaw/workspace/2026 中国创新电子产品海外销售分析报告.docx', buffer);
  console.log('Word document created successfully!');
}).catch(err => {
  console.error('Error creating document:', err);
  process.exit(1);
});
