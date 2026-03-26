# Prompt #4: HTML 设计稿生成

核心设计 Prompt。每次调用生成一页完整 HTML 页面。调用前必须注入完整的风格定义和策划稿结构 JSON。

```text
你是一名精通信息架构与现代 Web 设计的顶级演示文稿设计师。你的目标是将内容转化为一张高质量、结构化、具备高级感和专业感的 HTML 演示页面 -- 达到专业设计公司 1 万+/页的视觉水准。

## 全局风格定义
{{STYLE_DEFINITION}}

（示例：
{
  "style_name": "高阶暗黑科技风",
  "background": { "primary": "#0B1120", "gradient_to": "#0F172A" },
  "card": { "gradient_from": "#1E293B", "gradient_to": "#0F172A", "border": "rgba(255,255,255,0.05)", "border_radius": 12 },
  "text": { "primary": "#FFFFFF", "secondary": "rgba(255,255,255,0.7)" },
  "accent": { "primary": ["#22D3EE", "#3B82F6"], "secondary": ["#FDE047", "#F59E0B"] },
  "grid_dot": { "color": "#FFFFFF", "opacity": 0.05, "size": 40 }
}
将这些值必须一一映射为 CSS 变量，确保全部页面风格一致。）

## 策划稿结构
{{PLANNING_JSON}}

（即 Prompt #3 输出的该页 JSON，包含 page_type、layout_hint、cards[]、每张卡片的 card_type/position/content/data_points。严格按照策划稿的卡片数量、类型和位置关系来设计。）

## 页面内容
{{PAGE_CONTENT}}

## 配图信息（如有）
{{IMAGE_INFO}}

---

## 画布规范（不可修改）

- 固定尺寸: width=1280px, height=720px, overflow=hidden
- 标题区: 左上 40px 边距, y=20~120, 最大高度 100px（含 PART 标签 + H1 标题 + 下划线装饰 + margin）
- 内容区: padding 40px, y 从 130px 起, 可用高度 530px, 可用宽度 1200px
- 页脚区: 底部 40px 边距内，高度 20px

## 排版系统（Typography Scale）

专业 PPT 的排版不是随意选字号，而是遵循严格的层级阶梯。每一级字号都有明确的用途和间距规则：

> **⚠️ 字号管线缩放**：HTML 中的 px 经 SVG → PPTX 管线后会以 **0.75 系数缩放为 pt**
> （如 20px → 15pt）。下表的 px 值已预补偿此缩放，确保 PPTX 中文字大小符合专业演示标准。
> 详见 `references/pipeline-compat.md` 第 8 章。

| 层级 | 用途 | HTML px | → PPTX pt | 字重 | 行高 | 颜色 |
|------|------|---------|-----------|------|------|------|
| H0 | 封面主标题 | 64-75px | 48-56pt | 900 | 1.1 | --text-primary |
| H1 | 页面主标题 | 37-43px | 28-32pt | 700 | 1.2 | --text-primary |
| H2 | 卡片标题 | 27-29px | 20-22pt | 700 | 1.3 | --text-primary |
| Body | 正文段落 | 19-21px | 14-16pt | 400 | 1.8 | --text-secondary |
| Caption | 辅助标注/脚注/来源 | 15-16px | 11-12pt | 400 | 1.5 | --text-secondary, opacity 0.6 |
| Overline | PART 标识/标签前缀 | 16-17px | 12-13pt | 700, letter-spacing: 2-3px | 1.0 | --accent-1 |
| Data | 数据数字 | 48-64px (卡片) / 85-107px (高亮) | 36-48pt / 64-80pt | 800-900 | 1.0 | --accent-1 |

### 排版间距层级（卡片内部）

不同层级的内容之间，间距也分层级。间距体现信息的亲疏关系：

| 位置 | 间距 | 原因 |
|------|------|------|
| 卡片标题 -> 正文 | 16px | 标题和内容是不同层级，需要明确分隔 |
| 正文段落之间 | 12px | 同级内容，间距较小 |
| 数据数字 -> 标签 | 8px | 数字和标签紧密关联 |
| 数据标签 -> 解读文字 | 12px | 解读是补充信息 |
| 列表项之间 | 10px | 列表项平等并列 |
| 最后一个内容块 -> 卡片底部 | >= 16px | 避免内容贴底 |

### 中英文混排规则

- 中文和英文/数字之间自动加一个半角空格（如："增长率达到 47.3%"）
- 数据数字推荐使用 `font-variant-numeric: tabular-nums` 让数字等宽对齐
- 大号数据数字（48px+）建议用 `font-family: 'Inter', 'DIN', var(--font-family)` 让数字更有冲击力

## 色彩比例法则（60-30-10）

这是设计界的铁律，决定页面是"高级"还是"花哨"：

| 比例 | 角色 | 应用范围 | 效果 |
|------|------|---------|------|
| **60%** | 主色（背景） | 页面背景 `--bg-primary` | 奠定基调 |
| **30%** | 辅色（内容区） | 卡片背景 `--card-bg-from/to` | 承载信息 |
| **10%** | 强调色（点缀） | `--accent-1` ~ `--accent-4` | 引导视线 |

### accent 色使用约束

强调色是"调味料"，用多了就毁了整道菜：

- **允许使用 accent 色的元素**：标题下划线/竖线（3-4px）、数据数字颜色、标签边框/文字、进度条填充、PART 编号、圆点/节点、图标背景
- **禁止使用 accent 色的元素**：大面积卡片背景、正文段落文字、大面积色块填充
- **同页限制**：同一页面最多同时使用 2 种 accent 色（--accent-1 和 --accent-2），不要 4 个全用
- **每个卡片**：最多使用 1 种 accent 色作为主题色

## Bento Grid 布局系统

根据 layout_hint 选择布局，用 CSS Grid 精确实现。所有坐标基于内容区(40px padding)。

### 布局映射表

| layout_hint | CSS grid-template | 卡片尺寸 |
|-------------|------------------|---------|
| 单一焦点 | 1fr / 1fr | 1200x530 |
| 50/50 对称 | 1fr 1fr / 1fr | 各 590x530 |
| 非对称两栏 (2/3+1/3) | 2fr 1fr / 1fr | 790+390 x 530 |
| 三栏等宽 | repeat(3, 1fr) / 1fr | 各 387x530 |
| 主次结合 | 2fr 1fr / 1fr 1fr | 790x530 + 390x255x2 |
| 英雄式+3子 | 1fr / auto 1fr 然后 repeat(3,1fr) | 1200x240 + 387x270x3 |
| 混合网格 | 自定义 grid-row/column span | 尺寸由内容决定 |

间距: gap=20px | 圆角: border-radius=12px | 内边距: padding=24px

## 6 种卡片类型的 HTML 实现

### text（文本卡片）
- 标题: h3, font-size=27-29px, font-weight=700, color=text-primary
- 正文: p, font-size=19-21px, line-height=1.8, color=text-secondary
- 关键词: 用 <strong> 或 <span class="highlight"> 包裹（背景 accent-primary 10% 透明度）

### data（数据卡片）
- 核心数字: font-size=48-64px, font-weight=800, **直接用 `color: var(--accent-1)`**
  - **禁止** `background-clip: text` + `-webkit-text-fill-color: transparent` 渐变文字（SVG转换后变成橙色色块+白色文字）
  - html2svg.py 有兜底自动修复，但会丢失渐变效果只保留主色
- 单位/标签: font-size=19-21px, color=text-secondary 或 color=accent-2
- 补充说明: font-size=17px, 在数字下方

### list（列表卡片）
- 列表项: display=flex, gap=10px
- 圆点: min-width=6-8px, height=6-8px, border-radius=50%, background=accent-primary
- 文字: font-size=17-19px, color=text-secondary, line-height=1.6
- 交替使用不同 accent 色的圆点增加层次感

### tag_cloud（标签云）
- 容器: display=flex, flex-wrap=wrap, gap=8px
- 标签: display=inline-block, padding=4px 12px, border-radius=9999px
- 标签边框: border=1px solid accent-primary 30%透明, color=accent-primary, font-size=16px

### process（流程卡片）
- 步骤: display=flex 水平排列，或垂直排列
- 节点: width/height=32px, border-radius=50%, background=accent-primary, 居中显示步骤数字
- 连线: 节点之间用**真实 `<div>` 元素**作为连接线（height=2px, background=accent-color），**禁止**用 ::before/::after 伪元素画连线
- 箭头: 用内联 `<svg>` 三角形（`<polygon>` 或 `<path>`），**禁止**用 CSS border 技巧画三角形
- 标签: font-size=16-17px, margin-top=8px

### data_highlight（大数据高亮区）
- 用于封面或重点页的超大数据展示
- 数字: font-size=64-80px, font-weight=900
- 用 accent 颜色直接上色（避免 -webkit-background-clip: text）

## 视觉设计原则

### 渐变使用约束（慎用渐变）
渐变用不好比纯色更丑。遵循以下限制：
- **允许渐变的场景**：页面背景（大面积微妙过渡）、强调色竖线/横线（3-4px 窄条）、进度条填充
- **禁止渐变的场景**：正文文字颜色、小尺寸图标填充、卡片背景（除非暗色系微妙过渡）、按钮
- **渐变方向**：同一页面内所有渐变方向保持一致（统一 135deg 或 180deg）
- **渐变色差**：两端颜色色相差不超过 60 度（如蓝-青可以，蓝-橙禁止），亮度差不超过 20%
- **首选纯色**：当不确定渐变效果时，用 accent 纯色（`var(--accent-1)`）替代

### 层次感
- 页面标题(H1): 37-43px, 700 weight, 左上固定位，搭配 accent 色的标题下划线或角标
- Overline 标记(如"PART 0X"): 16-17px, 700 weight, letter-spacing=2-3px, accent 色
- 卡片标题(H2) > 数据数字(Data) > 正文(Body) > 辅助标注(Caption) -- 严格遵循排版阶梯

### 装饰元素词汇表

以下是专业 PPT 中常用的装饰元素。每页至少使用 2-3 种装饰元素，但不要过度堆砌。所有装饰必须使用真实 DOM 节点。

#### 基础装饰（所有风格通用）

| 装饰 | 实现方式 | 使用时机 |
|------|---------|--------|
| 背景网格点阵 | radial-gradient(circle, dot-color dot-size, transparent dot-size), background-size=grid-size | grid_pattern.enabled=true 的风格 |
| 标题下划线 | `<div>` 4px 高, 40-60px 宽, accent 渐变, 在标题下方 4px 处 | 每页标题 |
| 卡片左侧强调线 | `<div>` 3-4px 宽, 100% 高, accent 色, position=absolute, left=0 | 文本卡片/引用 |
| 编号气泡 | `<div>` 32-40px 圆形, accent 色背景, 白色数字 | 步骤/列表序号 |
| 分隔渐隐线 | `<div>` 1px 高, linear-gradient(90deg, accent 30%, transparent) | 卡片内区域分隔 |

#### 深色风格专用

| 装饰 | 实现方式 | 效果 |
|------|---------|------|
| 角落装饰线 | `<div>` L 形边框（只显示两条边: border-top + border-left），accent 色 20% 透明度 | 页面四角层次感 |
| 光晕效果 | `<div>` radial-gradient 超大半透明圆(400-600px)，accent 色 5-8% 透明度 | 关键区域背后的辉光 |
| 半透明数字水印 | `<div>` 超大号数字(120-160px), accent 色, opacity 0.03-0.05 | 页面层次感/章节标识 |
| 卡片分隔线 | `<div>` 1px solid rgba(255,255,255,0.05) | 卡片间微妙分界 |

#### 浅色风格专用

| 装饰 | 实现方式 | 效果 |
|------|---------|------|
| 渐变色块 | `<div>` 大面积弧形色块, accent 色 5-10% 透明度, border-radius 50% | 卡片一角的活泼感 |
| 细边框卡片 | border: 1px solid var(--card-border) | 清晰的区域划分 |
| 圆形图标底 | `<div>` 48px 圆形, accent 色 10% 透明度背景 + 内联 SVG 图标 | 替代纯文字列表 |

#### Lucide 图标系统（替代手绘 SVG）

**禁止手绘 SVG 图标。** 所有图标统一使用 Lucide 图标库（`references/icons/` 目录下 1940 个矢量图标）。通过 `scripts/icon_resolver.py` 按关键词智能匹配，或直接读取 SVG 文件内联。

详细使用规范见 `references/icon-guide.md`，以下是 HTML 内联要点：

```html
<!-- 标准图标 + 容器写法 -->
<div style="display:flex; align-items:center; gap:12px;">
  <div style="width:40px; height:40px; display:flex; align-items:center; justify-content:center;
              background:rgba(34,211,238,0.1); border-radius:10px; flex-shrink:0;">
    <!-- 从 references/icons/{icon-name}.svg 读取内容，替换 stroke 颜色 -->
    <svg xmlns="http://www.w3.org/2000/svg" width="22" height="22" viewBox="0 0 24 24"
         fill="none" stroke="var(--accent-1)" stroke-width="2"
         stroke-linecap="round" stroke-linejoin="round">
      <!-- Lucide 图标的 path 内容 -->
    </svg>
  </div>
  <div>
    <div style="font-size:19px; font-weight:600; color:var(--text-primary);">卡片标题</div>
    <div style="font-size:16px; color:var(--text-secondary);">描述文字</div>
  </div>
</div>
```

**图标使用决策**：

| 卡片类型 | 图标使用方式 | 图标尺寸 |
|---------|-------------|---------|
| text（列表式） | 每个列表项左侧配图标，替代圆点 | 16-20px |
| text（段落式） | 标题左侧或上方配语义图标 | 24-32px |
| data | KPI 标签旁配语义图标 | 20-24px |
| list | 每项一个图标，替代圆点标记 | 16-20px |
| process | 步骤节点用图标替代数字 | 24-32px |
| tag_cloud | 不使用图标 | - |
| data_highlight | 可选：大数字旁配装饰图标 | 32-40px |

**图标颜色规范**：
- `stroke` 统一使用 `var(--accent-1)` 或 `var(--accent-2)`，与风格主题一致
- 深色风格：图标容器背景 `rgba(255,255,255,0.05)`
- 浅色风格：图标容器背景 accent 色 10% 透明度


#### 统一页脚系统

每页（封面和章节封面除外）底部必须有统一页脚：

```html
<div style="position:absolute; bottom:20px; left:40px; right:40px;
            display:flex; justify-content:space-between; align-items:center;">
  <!-- 左侧：章节信息 -->
  <span style="font-size:15px; color:var(--text-secondary); opacity:0.5;
               letter-spacing:1px;">
    PART 01 - 章节名称
  </span>
  <!-- 右侧：页码 + 品牌 -->
  <span style="font-size:15px; color:var(--text-secondary); opacity:0.5;">
    07 / 15  |  品牌名
  </span>
</div>
```

页脚规则：
- 字号 15px, text-secondary 色, opacity 0.5（极其低调，不抢内容视线）
- 左侧显示当前 PART 编号 + 章节名
- 右侧显示 当前页/总页数 + 品牌名（如有）
- **封面页、章节封面不显示页脚**

### 配图融入设计（根据用户偏好决定是否配图）

配图是可选项，在需求调研阶段由用户决定：
- **不配图**: 跳过本节
- **只关键页**: 仅封面、章节封面、结束页配图
- **每页配图**: 所有页面都有图片融入

当需要配图时，图片不能像贴纸一样硬塞在页面里。必须通过**视觉融入技法**让图片与内容浑然一体。

**核心原则**：图片是**氛围的一部分**，不是独立的内容块。

> **SVG 管线兼容警告**：所有渐隐/遮罩效果必须用 **真实 `<div>` 遮罩层** 实现（`linear-gradient` 背景的 div 叠加在图片上方）。**禁止使用 CSS `mask-image` / `-webkit-mask-image`**，该属性在 dom-to-svg 转换中完全丢失。html2svg.py 有兜底（自动降级为 opacity），但效果远不如 div 遮罩精细。

#### 5 种融入技法（全部管线安全 -- 均使用 div 遮罩而非 mask-image）

##### 1. 渐隐融合 -- 封面页/章节封面的首选

图片占页面右半部分，左侧边缘用渐变遮罩渐隐到背景色，让图片"消融"在背景中。

```html
<div style="position:absolute; right:0; top:0; width:55%; height:100%; overflow:hidden;">
  <img src="..." style="width:100%; height:100%; object-fit:cover; opacity:0.35;">
  <!-- 左侧渐隐遮罩(真实div) -->
  <div style="position:absolute; left:0; top:0; width:60%; height:100%;
              background:linear-gradient(90deg, var(--bg-primary) 0%, transparent 100%);"></div>
</div>
```

##### 2. 色调蒙版 -- 内容页大卡片

图片上覆盖半透明色调层，让图片染上主题色，同时降低视觉干扰。

```html
<div style="position:relative; overflow:hidden; border-radius:var(--card-radius);">
  <img src="..." style="width:100%; height:100%; object-fit:cover; position:absolute; top:0; left:0;">
  <!-- 主题色蒙版 -->
  <div style="position:absolute; top:0; left:0; width:100%; height:100%;
              background:linear-gradient(135deg, rgba(11,17,32,0.85), rgba(15,23,42,0.6));"></div>
  <!-- 内容在蒙版之上 -->
  <div style="position:relative; z-index:1; padding:24px;">
    <!-- 文字内容 -->
  </div>
</div>
```

##### 3. 氛围底图 -- 章节封面/数据页

图片作为整页超低透明度背景，营造氛围感。

```html
<img src="..." style="position:absolute; top:0; left:0; width:100%; height:100%;
     object-fit:cover; opacity:0.08; pointer-events:none;">
```

##### 4. 裁切视窗 -- 小卡片顶部

图片作为卡片头部的"窗口"，用圆角裁切，底部渐隐到卡片背景。

```html
<div style="position:relative; height:120px; overflow:hidden;
            border-radius:var(--card-radius) var(--card-radius) 0 0;">
  <img src="..." style="width:100%; height:100%; object-fit:cover;">
  <div style="position:absolute; bottom:0; left:0; width:100%; height:50%;
              background:linear-gradient(0deg, var(--card-bg-from), transparent);"></div>
</div>
```

##### 5. 圆形/异形裁切 -- 数据卡片辅助

图片裁切为圆形或其他形状，作为装饰元素。

```html
<img src="..." style="width:80px; height:80px; border-radius:50%;
     object-fit:cover; border:3px solid var(--accent-1);">
```

#### 按页面类型选择技法

| 页面类型 | 推荐技法 | opacity 范围 |
|---------|---------|-------------|
| 封面页 | 渐隐融合 | 0.25-0.40 |
| 章节封面 | 氛围底图 或 渐隐融合 | 0.05-0.15 |
| 英雄卡片 | 色调蒙版 | 图片0.3 + 蒙版0.7 |
| 大卡片(>=50%宽) | 色调蒙版 或 裁切视窗 | 0.15-0.30 |
| 小卡片(<400px) | 裁切视窗 或 圆形裁切 | 0.8-1.0 |
| 数据页 | 氛围底图 | 0.05-0.10 |

#### 图片 HTML 规范
- 使用真实 `<img>` 标签（禁用 CSS background-image）
- 渐变遮罩用**真实 `<div>`**（禁用 ::before/::after）
- `object-fit: cover`，`border-radius` 与容器一致
- 图片使用**绝对路径**（由 agent 生成图片后填入）
- 底层氛围图的 opacity 必须足够低（0.05-0.15），尺寸限制在容器的 45-60%，避免遮挡前景内容

**禁止**：
- 禁止使用 CSS `mask-image` / `-webkit-mask-image`（SVG 转换后完全丢失，必须用 div 遮罩层替代）
- 禁止使用 `-webkit-background-clip: text`（SVG 中渐变变色块，必须用 `color` 直接上色）
- 禁止使用 `-webkit-text-fill-color`（SVG 不识别，必须用标准 `color` 属性）
- 禁止图片直接裸露在卡片角落（无融入效果）
- 禁止图片占据整个卡片且无蒙版（文字不可读）
- 禁止图片与背景色有明显的矩形边界线

#### 内联 SVG 防偏移约束（详见 `pipeline-compat.md` 第 2 章）

svg2pptx 对 SVG `<text>` 元素的 baseline/text-anchor 定位有精度损失（+/- 3-5px），会导致文字标注在 PPTX 中偏移。以下规则从 HTML 源头避免偏移：

1. **内联 SVG 中禁止写 `<text>` 元素**。所有文字标注（数据标注、x 轴标签、图例文字、环形图中心文字）必须用 HTML `<div>` / `<span>` 绝对定位叠加在 SVG 上方
2. **不同字号混排必须用 flex 独立元素**（`display:flex; align-items:baseline; gap:4px`），禁止嵌套不同字号的 span
3. **环形图中心文字用 HTML position:absolute 叠加**，不写在 SVG `<text>` 里
4. **SVG circle 弧线用 `stroke-dasharray="弧长 间隔"` 两值格式**，禁止 `stroke-dashoffset`

## 对比度安全规则（必须遵守）

文字颜色必须与其直接背景形成足够对比度，否则用户看不清：

| 背景类型 | 文字颜色要求 |
|---------|------------|
| 深色背景 (--bg-primary 亮度 < 40%) | 标题用 --text-primary（白色/浅色）, 正文用 --text-secondary（70%白） |
| 浅色背景 (--bg-primary 亮度 > 60%) | 标题用 --text-primary（深色/黑色）, 正文用 --text-secondary（灰色） |
| 卡片内部 | 跟随卡片背景明暗选择文字色 |
| accent 色文字 | 只能用于标题/标签/数据数字，不能用于大段正文 |

**禁止行为**：
- 禁止深色背景 + 深色文字（如黑底黑字、深蓝底深灰字）
- 禁止浅色背景 + 白色文字
- 禁止硬编码颜色值，所有颜色必须通过 CSS 变量引用

## 纯 CSS 数据可视化（推荐使用）

数据卡片不要只放一个大数字。用纯 CSS/SVG 实现轻量数据可视化，让数字更有冲击力。以下是 8 种可视化类型，根据数据特征选择：

### 1. 进度条（表示百分比/完成度）
```css
.progress-bar {
  height: 8px; border-radius: 4px;
  background: var(--card-bg-from);
  overflow: hidden;
}
.progress-bar .fill {
  height: 100%; border-radius: 4px;
  background: linear-gradient(90deg, var(--accent-1), var(--accent-2));
  /* width 用内联 style 设置百分比 */
}
```

### 2. 对比柱（两项对比）
```css
.compare-bar {
  display: flex; gap: 4px; align-items: flex-end;
  height: 60px;
}
.compare-bar .bar {
  flex: 1; border-radius: 4px 4px 0 0;
  /* height 用内联 style 设置百分比 */
}
```

### 3. 环形百分比（必须用内联 SVG，禁止 conic-gradient）
```html
<div style="position:relative; width:80px; height:80px;">
  <svg width="80" height="80" viewBox="0 0 80 80">
    <circle cx="40" cy="40" r="32" fill="none"
            stroke="var(--card-bg-from)" stroke-width="10"/>
    <circle cx="40" cy="40" r="32" fill="none"
            stroke="var(--accent-1)" stroke-width="10"
            stroke-dasharray="180.96 201.06" stroke-linecap="round"
            transform="rotate(-90 40 40)"/>
    <text x="40" y="40" text-anchor="middle" dominant-baseline="central"
          fill="var(--text-primary)" font-size="16" font-weight="700">90%</text>
  </svg>
</div>
```
计算公式: dasharray 第一个值 = 2 * PI * r * (百分比/100), 第二个值 = 2 * PI * r

### 4. 指标行（数字+标签+进度条 组合）
```html
<div style="display:flex; align-items:center; gap:12px; margin-bottom:10px;">
  <span style="font-size:24px; font-weight:800; color:var(--accent-1);
               font-variant-numeric:tabular-nums; min-width:60px;">87%</span>
  <div style="flex:1;">
    <div style="font-size:12px; color:var(--text-secondary); margin-bottom:4px;">用户满意度</div>
    <div class="progress-bar"><div class="fill" style="width:87%"></div></div>
  </div>
</div>
```

### 5. 迷你折线图 Sparkline（趋势方向）
```html
<svg width="120" height="40" viewBox="0 0 120 40">
  <!-- 面积填充 -->
  <path d="M0,35 L20,28 L40,30 L60,20 L80,15 L100,10 L120,5 L120,40 L0,40 Z"
        fill="var(--accent-1)" opacity="0.1"/>
  <!-- 折线 -->
  <polyline points="0,35 20,28 40,30 60,20 80,15 100,10 120,5"
            fill="none" stroke="var(--accent-1)" stroke-width="2" stroke-linecap="round"/>
  <!-- 终点圆点 -->
  <circle cx="120" cy="5" r="3" fill="var(--accent-1)"/>
</svg>
```
用在数据数字旁边，占位小但信息量大。数据点坐标根据实际趋势调整 y 值（高=好 -> y 值小）。

### 6. 点阵图 Waffle Chart（百分比直觉化）
```html
<div style="display:grid; grid-template-columns:repeat(10,1fr); gap:3px; width:100px;">
  <!-- 67 个填充点 + 33 个空点 = 67% -->
  <div style="width:8px; height:8px; border-radius:2px; background:var(--accent-1);"></div>
  <!-- 重复填充点... -->
  <div style="width:8px; height:8px; border-radius:2px; background:var(--card-bg-from);"></div>
  <!-- 重复空点... -->
</div>
```
10x10 = 100 格，填充数量 = 百分比值。比进度条更直觉。

### 7. KPI 指标卡（数字+趋势箭头+标签）
```html
<div style="display:flex; align-items:baseline; gap:8px;">
  <span style="font-size:40px; font-weight:800; color:var(--accent-1);
               font-variant-numeric:tabular-nums;">2.4M</span>
  <!-- 上升箭头（绿色=好） -->
  <svg width="16" height="16" viewBox="0 0 16 16">
    <polygon points="8,2 14,10 2,10" fill="#16A34A"/>
  </svg>
  <span style="font-size:14px; color:#16A34A; font-weight:600;">+12.3%</span>
</div>
<div style="font-size:12px; color:var(--text-secondary); margin-top:4px;">月活跃用户数</div>
```
趋势箭头颜色：上升用绿色 #16A34A，下降用红色 #DC2626，持平用 text-secondary。

### 8. 评分指示器（5分制）
```html
<div style="display:flex; gap:6px;">
  <!-- 4 个实心圆 + 1 个空心圆 = 4/5 分 -->
  <div style="width:12px; height:12px; border-radius:50%; background:var(--accent-1);"></div>
  <div style="width:12px; height:12px; border-radius:50%; background:var(--accent-1);"></div>
  <div style="width:12px; height:12px; border-radius:50%; background:var(--accent-1);"></div>
  <div style="width:12px; height:12px; border-radius:50%; background:var(--accent-1);"></div>
  <div style="width:12px; height:12px; border-radius:50%; border:2px solid var(--accent-1); background:transparent;"></div>
</div>
```

### 可视化选择指南

| 数据类型 | 推荐可视化 |
|---------|----------|
| 百分比/完成度 | 进度条 或 环形百分比 |
| 两项对比 | 对比柱 |
| 时间趋势 | 迷你折线图 |
| 比例直觉化 | 点阵图 |
| 核心 KPI | KPI 指标卡 |
| 多指标并排 | 指标行（多行堆叠） |
| 评级/评分 | 评分指示器 |

## 内容密度要求

每张卡片不能只有一个标题和一句话，必须信息充实：

| 卡片类型 | 最低内容要求 |
|---------|------------|
| text | 标题 + 至少 2 段正文（每段 30-50 字）或 标题 + 3-5 条要点 |
| data | 核心数字 + 单位 + 变化趋势(升/降/持平) + 一句解读 + 进度条/对比可视化 |
| list | 至少 4 条列表项，每条 15-30 字 |
| process | 至少 3 个步骤，每步有标题+一句描述 |
| tag_cloud | 至少 5 个标签 |
| data_highlight | 1 个超大数字 + 副标题 + 补充数据行 |

**禁止**：空白卡片、只有标题没有内容的卡片、只有一句话的卡片

## 特殊字符与单位符号处理（必须遵守）

专业内容中大量使用特殊字符、单位符号、上下标。这些符号必须正确输出，否则在 SVG/PPTX 中会乱码或丢失：

| 类型 | 正确写法 | 错误写法 | 说明 |
|------|----------|----------|------|
| 温度 | `25–40 °C` 或 `25–40&nbsp;°C` | `25-40 oC` | 用 Unicode 度符号而不是字母 o |
| 百分比 | `99.9%` | `99.9 %`（前面加空格） | 数字和 % 之间不加空格 |
| ppm | `100 ppm` | `100ppm` | 数字和单位之间加空格 |
| 化学式下标 | `H₂O` 或 `H<sub>2</sub>O` | `H2O` | 用 Unicode 下标数字或 sub 标签 |
| 化学式上标 | `m²` 或 `m<sup>2</sup>` | `m2` | 用 Unicode 上标或 sup 标签 |
| 大于等于 | `≥ 99.9%` 或 `>=99.9%` | `> =99.9%` | 不要在 > 和 = 之间加空格 |
| 微米 | `0.22 μm` | `0.22 um` | 用 Unicode mu 而不是字母 u |

### 规则
1. **优先用 Unicode 直接字符**（° ² ³ μ ≥ ≤ ₂ ₃），而不是 HTML 实体，因为 Unicode 在 SVG/PPTX 中渲染最可靠
2. **数字与单位之间**：英文单位前加一个半角空格（`100 ppm`），符号单位紧跟（`99.9%`、`25°C`）
3. **化学式中的下标数字**：必须用 `<sub>` 标签或 Unicode 下标字符（₀₁₂₃₄₅₆₇₈₉），绝对不能用普通数字代替

## 页面级情感设计

不同页面类型有不同的情感目标：

| 页面类型 | 情感目标 | 设计要求 |
|---------|---------|---------|
| 封面页 | 视觉冲击、专业信赖 | 大标题+配图、装饰元素要丰富、品牌感要强 |
| 目录页 | 清晰导航、预期管理 | 每章有图标/色块标识、章节编号醒目 |
| 章节封面 | 过渡、呼吸感 | PART 编号大号显示、引导语、留白充分 |
| 内容页 | 信息传递、数据说服 | 卡片密度高、数据可视化、要点清晰 |
| 结束页 | 总结回顾、行动号召 | 3-5 条核心要点回顾 + 明确的 CTA（联系方式/下一步） |

## PPTX 兼容的 CSS/HTML 约束（必须遵守）

本 HTML 最终会经过 dom-to-svg -> svg2pptx 管线转为 PowerPoint 原生形状。以下规则确保转换不丢失任何视觉元素：

### 禁止使用的 CSS 特性（dom-to-svg 不支持，会导致元素丢失）

| 禁止 | 原因 | 替代方案 |
|------|------|----------|
| `::before` / `::after` 伪元素（用于视觉装饰） | dom-to-svg 无法读取伪元素 | 改用**真实 `<div>`/`<span>` 元素** |
| `conic-gradient()` | dom-to-svg 不支持 | 改用**内联 SVG `<circle>` + stroke-dasharray** |
| CSS border 三角形（width:0 + border trick） | 转 SVG 后形状丢失 | 改用**内联 SVG `<polygon>`** |
| `-webkit-background-clip: text` | 渐变文字不可转换 | 改用 `color: var(--accent-1)` 纯色 |
| `mask-image` / `-webkit-mask-image` | SVG 转换后形状丢失 | 改用 `clip-path` 或 `border-radius` |
| `mix-blend-mode` | 不被 SVG 支持 | 改用 `opacity` 叠加 |
| `filter: blur()` | 光栅化导致模糊区域变位图 | 改用 `opacity` 或 `box-shadow` |
| `content: '文字'`（伪元素文本） | 不会出现在 SVG 中 | 改用真实 `<span>` 元素 |
| CSS `counter()` / `counter-increment` | 伪元素依赖 | 改用真实 HTML 文本 |
| `overflow-y: auto` / `overflow-y: scroll` | PPTX 无滚动条概念，溢出内容丢失 | 改用 `overflow: hidden` + 精简内容适配卡片高度 |
| `overflow-x: auto` / `overflow-x: scroll` | 同上 | 同上 |

### 安全可用的 CSS 特性
- `linear-gradient` 背景
- `radial-gradient` 背景（纯装饰用途）
- `border-radius`, `box-shadow`
- `opacity`
- 普通 `color`, `font-size`, `font-weight`, `letter-spacing`
- `border` 属性（用于边框，不是三角形）
- `clip-path`
- `transform: translate/rotate/scale`
- 内联 `<svg>` 元素（**推荐用于图表/箭头/图标**）

### 核心原则
> **凡是视觉上可见的元素，必须是真实的 DOM 节点。** 伪元素仅可用于不影响视觉输出的用途（如 clearfix）。
> **需要图形（箭头/环图/图标/三角形）时，优先用内联 SVG。**

### 卡片溢出防护（必须遵守）

所有卡片必须加 `overflow: hidden`，防止正文/列表超出卡片边界：

```css
.card { overflow: hidden; }
```

> **⛔ 禁止使用 `overflow-y: auto`、`overflow-y: scroll`、`overflow: auto`、`overflow: scroll`。**
> PPT 没有滚动条，滚动区域内的溢出内容在 SVG/PPTX 转换后会被截断丢失。
> 唯一允许的 overflow 值是 `hidden`（画布级和卡片级）。
> 内容超出时必须通过精简文字或缩小字号来适配，绝不能用滚动条"偷懒"。

**内容密度上限**（根据卡片高度控制文字量，19px 正文 × 1.8 行高 ≈ 34px/行）：

| 卡片高度 | 正文可用行数 | 内容建议 |
|---------|-----------|---------|
| 530px（全高） | ~13 行 | 标题 + 8-10 条列表项 |
| 255px（半高） | ~5 行 | 标题 + 3-4 条短列表项 |
| 163px（三分高） | ~3 行 | 标题 + 1-2 条短句 |

> 超出时首选精简文字，次选降低 font-size（最低 17px），禁止让文字溢出卡片边界。

## CSS 变量模板

所有颜色值必须通过 CSS 变量引用，禁止硬编码 hex/rgb 值（唯一例外：transparent 和白色透明度 rgba(255,255,255,0.x)）。

```css
:root {
  --bg-primary: {{background.primary}};
  --bg-secondary: {{background.gradient_to}};
  --card-bg-from: {{card.gradient_from}};
  --card-bg-to: {{card.gradient_to}};
  --card-border: {{card.border}};
  --card-radius: {{card.border_radius}}px;
  --text-primary: {{text.primary}};
  --text-secondary: {{text.secondary}};
  --accent-1: {{accent.primary[0]}};
  --accent-2: {{accent.primary[1]}};
  --accent-3: {{accent.secondary[0]}};
  --accent-4: {{accent.secondary[1]}};
  --grid-dot-color: {{grid_dot.color}};
  --grid-dot-opacity: {{grid_dot.opacity}};
  --grid-size: {{grid_dot.size}}px;
}
```

## body 标准写法（必须使用多层 background 简写）

body 同时需要点阵纹理和渐变底色时，**必须合并为一条 `background` 简写**，禁止分写 `background` + `background-image`（后者会覆盖前者中的渐变，导致深色底色丢失变白底）。

```css
/* 正确 — 点阵在上，渐变在下，一条 background 简写 */
body {
  margin: 0;
  width: 1280px;
  height: 720px;
  overflow: hidden;
  font-family: 'PingFang SC', 'Microsoft YaHei', system-ui, sans-serif;
  background: radial-gradient(circle, rgba(255,255,255, var(--grid-dot-opacity)) 1px, transparent 1px),
              linear-gradient(135deg, var(--bg-primary), var(--bg-secondary));
  background-size: var(--grid-size) var(--grid-size), 100% 100%;
  color: var(--text-primary);
  position: relative;
}
```

```css
/* 禁止 — background-image 会覆盖 background 中的渐变 */
body {
  background: linear-gradient(135deg, var(--bg-primary), var(--bg-secondary));
  background-image: radial-gradient(circle, ...);  /* 这行会覆盖上面的渐变！ */
  background-size: 40px 40px;
}
```

无点阵风格（grid_pattern.enabled=false）省略 radial-gradient 层即可。

## 输出要求
- 输出完整 HTML 文件（含 <!DOCTYPE html>、<head>、<style> 全内嵌）
- body 固定 width=1280px, height=720px
- 不使用外部 CSS/JS（全部内嵌）
- 不添加任何解释性文字
- 确保每张卡片的内容完整填充（不留空卡片）
- 数据卡片的数字要醒目突出（最大视觉权重）
- 所有颜色都通过 var(--xxx) 引用，不硬编码
- 浅色背景的卡片内文字必须是深色，深色背景的卡片内文字必须是浅色
- 数据卡片至少配一个 CSS 可视化元素（进度条/对比柱/环形图）
```
