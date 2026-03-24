# Bento Grid 布局系统

## 画布参数

```
固定画布: width=1280px, height=720px
标题区: x=40, y=20, w=1200, h=100
内容区: x=40, y=130, w=1200, h=530
卡片间距: gap=20px
卡片圆角: border-radius=12px
卡片内边距: padding=24px
```

> **标题区高度说明**：内容页标题区包含 PART 标签(~17px) + H1 标题(~48px) + 下划线装饰(~12px) + margin，
> 合计约 100px。标题区底部 y=120，内容区 y=130 留出 10px 视觉呼吸间距，确保标题与卡片不粘连。

## CSS Grid 实现

所有布局通过 CSS Grid 精确实现。内容区容器统一定义：

```css
.content-area {
  position: absolute;
  left: 40px; top: 130px;
  width: 1200px; height: 530px;
  display: grid;
  gap: 20px;
}
```

## 页面类型布局

### 封面页 (cover)
- 大标题居中或左对齐, font-size=64-75px, accent-primary 色
- 副标题 font-size=32px
- 演讲人/日期/公司 底部小号文字 font-size=21px
- 装饰: 品牌色块、几何线条、配图（渐隐融合技法）
- **不使用 Bento Grid**，自由排版

### 目录页 (toc)
- 2-5 个等大卡片网格

| 卡片数 | grid-template-columns | 单卡尺寸 |
|-------|----------------------|---------|
| 2 | 1fr 1fr | 590x530 |
| 3 | repeat(3, 1fr) | 387x530 |
| 4 | 1fr 1fr / 1fr 1fr (2x2) | 590x255 |
| 5 | repeat(3, 1fr) / repeat(2, 1fr) (3+2) | 混合 |

### 章节封面 (section)
- "PART 0X" font-size=27px, accent-primary, letter-spacing=2px
- 标题 font-size=59px, font-weight=700
- 导语 font-size=24px, color=text-secondary
- 大量留白，营造呼吸感
- **不使用 Bento Grid**，居中排版

### 结束页 (end)
- 标题 font-size=59px 居中
- 核心要点 3-5 个, font-size=24px
- 联系方式/CTA 底部

---

## 7 种内容页布局

所有基于内容区 (1200x530px, 起始坐标 40,130)。

### 1. 单一焦点

适用: 1个核心论点/大数据全屏展示

```css
.content-area { grid-template: 1fr / 1fr; }
/* 卡片: 1200x530 */
```

### 2. 50/50 对称

适用: 对比、并列概念

```css
.content-area { grid-template: 1fr / 1fr 1fr; }
/* 左: 590x530 | 右: 590x530 */
```

### 3. 非对称两栏 (2/3 + 1/3)

适用: 主次关系。**最常用的布局。**

```css
.content-area { grid-template: 1fr / 2fr 1fr; }
/* 主: 790x530 | 辅: 390x530 */
```

### 4. 三栏等宽

适用: 3个并列比较

```css
.content-area { grid-template: 1fr / repeat(3, 1fr); }
/* 卡1: 387x530 | 卡2: 387x530 | 卡3: 386x530 */
```

### 5. 主次结合 (大 + 两小)

适用: 层级关系。**推荐：信息层次丰富时优先选择。**

```css
.content-area { grid-template: 1fr 1fr / 2fr 1fr; }
/* 主: 790x530 (span 2 rows) | 辅1: 390x255 | 辅2: 390x255 */
```

主卡片需设置 `grid-row: 1 / -1;` 跨两行。

### 6. 顶部英雄式

适用: 总分关系。**推荐：总分结构清晰时优先选择。**

**3子项版（最常用）**：
```css
.content-area { grid-template: auto 1fr / repeat(3, 1fr); }
/* 英雄: 1200x240 (span 3 cols) | 子1-3: 387x270 */
```

**4子项版**：
```css
.content-area { grid-template: auto 1fr / repeat(4, 1fr); }
/* 英雄: 1200x240 (span 4 cols) | 子1-4: 285x270 */
```

**2子项版**：
```css
.content-area { grid-template: auto 1fr / 1fr 1fr; }
/* 英雄: 1200x260 (span 2 cols) | 子1-2: 590x250 */
```

英雄卡片需设置 `grid-column: 1 / -1;` 跨所有列。

### 7. 混合网格

适用: 高信息密度, 4-6个异构块。**推荐：信息密度最高时优先选择。**

**2x3 网格**：
```css
.content-area { grid-template: repeat(3, 1fr) / 1fr 1fr; }
/* 6个卡片: 各 590x163 */
```

可通过 `grid-row`/`grid-column` 的 span 让个别卡片跨行/跨列，形成大小混搭效果。

**关键约束**: 所有卡片不得超出内容区边界（x+w<=1240, y+h<=660），间距>=20px，禁止重叠。

**填充约束**: 每列/每行的卡片必须填满可用空间，不允许出现大面积留白。当某列只有 1-2 张小卡片且列高 > 400px 时，必须补充卡片直到视觉均衡（推荐每列 ≥ 3 张）。

**子列对齐约束**: 当一列包含多张子卡片时，子卡片的顶底边缘必须与相邻列的大卡片对齐。使用 `justify-content: space-between` 均匀分布，**禁止** `flex: 1` 拉伸（拉伸会使卡片过高、内容稀疏）。

---

## 布局决策矩阵

| 内容特征 | 推荐布局 | 卡片数 |
|---------|---------|-------|
| 1 个核心论点/数据 | 单一焦点 | 1 |
| 2 个对比/并列 | 50/50 对称 | 2 |
| 主概念 + 补充 | 非对称两栏 | 3-4（辅助列 ≥ 2 张） |
| 3 个并列要素 | 三栏等宽 | 3 |
| 1 核心 + 2 辅助 | 主次结合 | 3 |
| 综述 + 3-4 子项 | 顶部英雄式 | 4-5 |
| 4-6 异构块 | 混合网格 | 4-6 |

**选择优先级**：避免"单一焦点"（除非确实只有一个全屏内容）。内容>=3块时，优先选择主次结合/英雄式/混合网格。

---

## Grid 跨行/跨列使用规则

### 禁止冗余 span

当 content-area 的每列只有 **1 个直接子元素** 时，**禁止使用 `grid-row: span`**。CSS Grid 的隐式行只有一行，子元素自然撑满整列高度，span 无效且可能破坏隐式行高计算。

```css
/* 正确：两列各一个元素，不需要 span */
.content-area { display: grid; grid-template-columns: 1fr 1fr; gap: 20px; }
.left-card { /* 自然撑满 */ }
.right-col { /* 自然撑满 */ }

/* 禁止：只有 1 行时写 span 2 */
.left-card { grid-row: span 2; }  /* 无意义，可能触发意外的隐式行 */
```

### 何时必须用 span

仅当**同一列有 2+ 个直接网格子元素、且某个元素需要跨越多行**时才使用 span。例如「主次结合」布局中，主卡片跨 2 行而同列无其他元素、对侧 2 张卡片各占 1 行：

```css
.content-area { grid-template: 1fr 1fr / 2fr 1fr; }
.main-card { grid-row: 1 / -1; }  /* 正确：对侧有 2 张卡片分别占一行 */
```

---

## 6 种卡片内容类型

### text（文本卡片）
- 标题: h3, 27-29px, 700 weight
- 正文: p, 19-21px, line-height 1.8
- 关键词用 `<strong>` 或 `<span class="highlight">` 高亮
- **最低要求**: 标题 + 至少 2 段正文（每段 30-50 字）

### data（数据卡片）
- 核心数字: 48-64px, 800 weight, accent 色
- 单位/标签: 19-21px, text-secondary
- 补充解读: 17px
- 推荐搭配一个 CSS 可视化（进度条/对比柱/环形图）
- **最低要求**: 核心数字 + 单位 + 趋势 + 解读 + 可视化

### list（列表卡片）
- 圆点: 6-8px 圆点, accent 色
- 文字: 17-19px, line-height 1.6
- 交替使用不同 accent 色圆点增加层次感
- **最低要求**: 至少 4 条列表项，每条 15-30 字

### tag_cloud（标签云）
- 容器: flex-wrap, gap=8px
- 标签: 圆角胶囊形, 16px, accent 色边框
- **最低要求**: 至少 5 个标签

### process（流程卡片）
- 节点: 32px 圆形, accent 色, 居中步骤数字
- 连线: **真实 `<div>` 元素**（禁止 ::before/::after）
- 箭头: **内联 SVG `<polygon>`**（禁止 CSS border 三角形）
- **最低要求**: 至少 3 个步骤，每步标题 + 一句描述

### data_highlight（大数据高亮区）
- 用于封面或重点页的超大数据展示
- 数字: 85-107px, 900 weight, accent 色
- 副标题 + 补充数据行
- **最低要求**: 1 个超大数字 + 副标题 + 补充数据行
