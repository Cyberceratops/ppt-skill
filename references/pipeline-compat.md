# HTML -> SVG -> PPTX 管线兼容性规则

本文档汇总所有管线兼容性教训。**HTML 设计稿生成时必须遵守，在源头规避偏移问题。**

核心原则：**html2svg + svg2pptx 不是浏览器**，很多 CSS 特性和 SVG 属性在转换过程中会丢失或产生偏移。HTML 写法必须考虑到下游转换器的能力边界。

---

## 1. CSS 禁止清单

| 禁止特性 | 转换后现象 | 正确替代写法 |
|---------|---------|-----------|
| `background` + `background-image` 分写 | `background-image` 覆盖 `background` 中的渐变，深色底变白底 | 合并为多层 `background` 简写（见下方示例） |
| `background-clip: text` | 渐变变色块 + 白色文字 | `color: var(--accent-1)` 直接上色 |
| `-webkit-text-fill-color` | 文字颜色丢失 | 标准 `color` 属性 |
| `mask-image` / `-webkit-mask-image` | 图片完全消失 | `<div>` 遮罩层（linear-gradient 背景） |
| `::before` / `::after`（视觉装饰用） | 内容消失 | 真实 `<div>` / `<span>` |
| `conic-gradient` | 不渲染 | 内联 SVG `<circle>` + stroke-dasharray |
| CSS border 三角形 (width:0 trick) | 形状丢失 | 内联 SVG `<polygon>` |
| `mix-blend-mode` | 不支持 | `opacity` 叠加 |
| `filter: blur()` | 光栅化变位图 | `opacity` 或 `box-shadow` |
| `content: '文字'` | 文字消失 | 真实 `<span>` |
| CSS `background-image: url(...)` | dom-to-svg 忽略 | `<img>` 标签 |

html2svg.py 兜底覆盖：前3项 + 伪元素 + conic-gradient + border三角形（共6种），但兜底效果远不如正确写法。

### 1.1 多层背景合并写法（最常见错误）

body 同时需要点阵纹理和渐变底色时，**禁止分写**，必须合并为单条 `background` 简写：

```css
/* 错误 — background-image 会覆盖 background 简写中的渐变，深色底消失变白底 */
background: linear-gradient(135deg, var(--bg-primary), var(--bg-secondary));
background-image: radial-gradient(circle, rgba(255,255,255,0.05) 1px, transparent 1px);
background-size: 40px 40px;

/* 正确 — 多层 background，点阵在上，渐变在下 */
background: radial-gradient(circle, rgba(255,255,255,0.05) 1px, transparent 1px),
            linear-gradient(135deg, var(--bg-primary), var(--bg-secondary));
background-size: 40px 40px, 100% 100%;
```

**原理**：CSS 规范中 `background-image` 属于 longhand，会覆盖 `background` shorthand 中设置的 image 层。多层 background 简写将所有层合并到一条声明中，不存在覆盖问题。

---

## 2. 防偏移写法（关键章节）

svg2pptx 的文本定位基于 SVG text 元素的坐标，但 PPTX textbox 的坐标系与 SVG 不同（SVG text y = baseline，PPTX y = textbox 顶部）。以下写法可从 HTML 源头避免偏移：

### 2.1 内联 SVG 中的文本标注 -- 用 HTML 叠加替代 SVG text

**问题**：内联 SVG 中的 `<text>` 元素经过 dom-to-svg 转换后坐标是 viewBox 坐标系，svg2pptx 在处理 baseline 偏移和 text-anchor 居中时有精度损失（约 +/- 3-5px），导致标注位置偏移。

**HTML 防偏移写法**：把文字标注从 SVG `<text>` 移出来，用 HTML `<div>` 绝对定位叠加在 SVG 上方。HTML div 由 dom-to-svg 精确定位，不经过 viewBox 坐标转换，偏移风险为零。

```html
<!-- 正确：HTML div 叠加标注，零偏移 -->
<div class="chart-container" style="position: relative;">
  <svg viewBox="0 0 660 340" style="width:100%; height:100%;">
    <!-- 只画柱子、线条等图形元素，不写 <text> -->
    <rect x="80" y="100" width="60" height="200" fill="#FF6900"/>
  </svg>
  <!-- 标注用 HTML 绝对定位叠加 -->
  <span style="position:absolute; left:12.5%; top:25%; font-size:14px; color:#fff;">720</span>
  <span style="position:absolute; left:12.5%; bottom:5%; font-size:12px; color:rgba(255,255,255,0.6);">标准版</span>
</div>
```

```html
<!-- 禁止：SVG text 在 PPTX 中会偏移 -->
<svg viewBox="0 0 660 340">
  <rect x="80" y="100" width="60" height="200" fill="#FF6900"/>
  <text x="110" y="90" text-anchor="middle" fill="#fff">720</text>
</svg>
```

### 2.2 不同字号混排 -- 必须用 flex 独立元素

**问题**：大小字号内嵌（`<div class="big">3.08<span class="small">s</span></div>`）经 dom-to-svg 转为独立 tspan 后，svg2pptx 给每个 tspan 按各自字号做 baseline 偏移，小字会上移。

```html
<!-- 正确：flex baseline 对齐 -->
<div style="display:flex; align-items:baseline; gap:4px;">
  <span style="font-size:48px;">3.08</span>
  <span style="font-size:18px;">s</span>
</div>
```

```html
<!-- 禁止：内嵌不同字号 span -->
<div class="big">3.08<span class="small">s</span></div>
```

### 2.3 环形图（圆弧进度条）-- SVG 画弧 + HTML 叠加文字

```html
<!-- 正确：环形图最佳实践 -->
<div class="ring-container" style="position: relative; width:120px; height:120px;">
  <!-- SVG 只画圆环弧线 -->
  <svg viewBox="0 0 120 120" style="width:100%; height:100%;">
    <!-- 底圈 -->
    <circle cx="60" cy="60" r="50" fill="none" stroke="rgba(255,255,255,0.1)" stroke-width="8"/>
    <!-- 弧线：用 dasharray 两值格式，禁止 dashoffset -->
    <circle cx="60" cy="60" r="50" fill="none" stroke="#FF6900" stroke-width="8"
            stroke-dasharray="235 314" stroke-linecap="round"
            transform="rotate(-90 60 60)"/>
  </svg>
  <!-- 中心文字用 HTML 叠加，不用 SVG text -->
  <div style="position:absolute; top:50%; left:50%; transform:translate(-50%,-50%); text-align:center;">
    <div style="font-size:22px; font-weight:700; color:#fff;">15</div>
    <div style="font-size:10px; color:rgba(255,255,255,0.6);">分钟</div>
  </div>
</div>
```

### 2.4 图例标签 -- 用 HTML flex 布局

```html
<!-- 正确：HTML flex 图例，不用 SVG text -->
<div style="display:flex; gap:16px; font-size:12px;">
  <div style="display:flex; align-items:center; gap:4px;">
    <span style="display:inline-block; width:12px; height:12px; background:#999; border-radius:2px;"></span>
    <span style="color:rgba(255,255,255,0.6);">初代SU7</span>
  </div>
  <div style="display:flex; align-items:center; gap:4px;">
    <span style="display:inline-block; width:12px; height:12px; background:#FF6900; border-radius:2px;"></span>
    <span style="color:rgba(255,255,255,0.6);">新一代SU7</span>
  </div>
</div>
```

### 2.5 x 轴标签（标准版/Pro/Max）-- 用 HTML 容器

```html
<!-- 正确: x 轴标签用 HTML -->
<div style="display:flex; justify-content:space-around; padding:0 10%;">
  <span style="font-size:13px; color:rgba(255,255,255,0.6);">标准版</span>
  <span style="font-size:13px; color:rgba(255,255,255,0.6);">Pro</span>
  <span style="font-size:13px; color:rgba(255,255,255,0.6);">Max</span>
</div>
```

---

## 3. 图片路径

| 场景 | 错误写法 | 正确写法 |
|------|---------|---------|
| img src 引用 | 依赖浏览器 resolve | html2svg 以 HTML 文件所在目录为基准 resolve 相对路径 |
| CSS background-image | 会被 dom-to-svg 忽略 | 用 `<img>` 标签 |

---

## 4. SVG circle 环形图属性

| 属性 | svg2pptx 支持 | 说明 |
|------|-------------|------|
| `stroke-dasharray="arc gap"` | 支持 | 用两个值：弧线长度 + 间隔长度 |
| `stroke-dashoffset` | **不支持** | 禁止使用，改用 dasharray 的两值格式 |
| `stroke-linecap="round"` | 支持 | 圆角弧端 |
| `transform="rotate(-90 cx cy)"` | 支持 | 从12点钟方向开始 |

正确弧线写法：`stroke-dasharray="235 314"` （弧长=235, 圆周=2*pi*50=314）

---

## 5. 底层氛围图

| 项目 | 规则 |
|------|------|
| opacity | 0.05 - 0.10（卡片内）/ 0.25 - 0.40（封面页） |
| 尺寸 | 限制在容器 40-60%，不要全覆盖 |
| z-index | 必须为 0 或 -1 |
| 实现方式 | 极低 opacity：直接 `<img>` + opacity |
| | 封面级渐隐：`<div>` 容器内 img + 遮罩 div |
| **禁止** | div 遮罩在 PPTX 中层叠不可靠时，回退到纯 opacity |

---

## 6. 配图技法管线安全等级

| 技法 | 管线安全 | 原因 |
|------|---------|------|
| 渐隐融合（div遮罩） | 安全 | 真实 div + linear-gradient |
| 色调蒙版 | 安全 | 真实 div + 半透明背景 |
| 氛围底图 | 最安全 | 纯 opacity |
| 裁切视窗 | 安全 | overflow:hidden + div 渐变 |
| 圆形裁切 | 安全 | border-radius |
| ~~CSS mask-image~~ | **禁止** | dom-to-svg 不支持 |

---

## 7. 总结：HTML 设计稿防偏移 checklist

生成每页 HTML 时，对照以下清单：

- [ ] CSS 禁止清单中的特性未使用
- [ ] body 背景用多层 `background` 简写（点阵+渐变合一），禁止分写 `background` + `background-image`，详见第 1.1 章
- [ ] 所有图片用 `<img>` 标签，不用 CSS background-image
- [ ] 内联 SVG 中**不含 `<text>` 元素**，所有文字标注用 HTML div 叠加
- [ ] 不同字号混排用 flex + 独立 span，不用嵌套 span
- [ ] 环形图用 stroke-dasharray 两值格式，不用 dashoffset
- [ ] 图例、x轴标签、数据标注全部用 HTML 元素，不用 SVG text
- [ ] 底层配图用低 opacity `<img>` 或 div 遮罩
- [ ] 伪元素 `::before`/`::after` 装饰已用真实元素替代
- [ ] 字号使用补偿后的 px 值（正文 ≥ 19px，标题 ≥ 37px），详见第 8 章
- [ ] 标题/副标题等单行文本加 `white-space: nowrap`，容器宽度 ≥ 文本宽度 + 余量，详见第 9.1 章
- [ ] 胶囊/标签/badge 用 `display: inline-flex` + `align-items: center` + `line-height: 1`，详见第 9.2 章
- [ ] 多卡片列用 `justify-content: space-between` 对齐，禁止 `flex: 1` 拉伸，禁止冗余 `grid-row: span`，详见 bento-grid.md

---

## 8. 字号管线缩放规则

### 转换公式

`svg2pptx.py` 的 `font_sz()` 函数将 SVG 中的 px 值转为 OOXML 字号单位：

```
PPTX_pt = HTML_px × 0.75
```

即 **HTML 中的 1px 在 PPTX 中变为 0.75pt**。这是 CSS 标准的 px-to-pt 换算（96dpi 屏幕下 1px = 0.75pt）。

### 设计约束

HTML 设计稿中必须使用**预补偿后的 px 值**，确保 PPTX 输出达到目标字号：

| 目标 PPTX pt | 所需 HTML px | 计算方式 |
|-------------|-------------|---------|
| 12pt | 16px | 12 ÷ 0.75 |
| 14pt | 19px | 14 ÷ 0.75 |
| 16pt | 21px | 16 ÷ 0.75 |
| 20pt | 27px | 20 ÷ 0.75 |
| 28pt | 37px | 28 ÷ 0.75 |
| 32pt | 43px | 32 ÷ 0.75 |
| 48pt | 64px | 48 ÷ 0.75 |

### 底线规则

- **正文 Body**：HTML 中不低于 19px（→ PPTX 14pt）
- **卡片标题 H2**：HTML 中不低于 27px（→ PPTX 20pt）
- **页面标题 H1**：HTML 中不低于 37px（→ PPTX 28pt）
- **页脚/脚注**：HTML 中不低于 13px（→ PPTX 10pt）

---

## 9. 文字溢出与容器尺寸规则

### 9.1 禁止单字换行

**问题**：容器 `max-width` 不足以容纳文本行宽，导致末尾 1-2 个字换行到下一行，视觉效果极差。

**根因**：中文每字约占 `font-size` 宽度，设计时未验证「字数 × 字号 ≤ 容器宽度」。

**强制规则**：
- 标题、副标题等单行文本：**必须加 `white-space: nowrap`**
- 容器 `max-width` 必须 ≥ 文本像素宽度 + 20px 余量
- 中文近似公式：`文本宽度 ≈ 字符数 × font-size`（标点/字母按 0.5 字宽计算）
- 如果内容可能超出容器，用 `overflow: hidden; text-overflow: ellipsis` 截断，绝不允许单字换行

### 9.2 胶囊/标签（pill/badge/tag）居中

**问题**：`display: inline-block` + `padding` 无法保证文字垂直居中，字体的 ascender/descender 差异会导致文字偏上或偏下。

**强制写法**：
```css
/* 正确：inline-flex 双轴居中 */
.pill {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  padding: 6px 16px;
  line-height: 1;
  white-space: nowrap;
}
```

```css
/* 禁止：inline-block 无法保证垂直居中 */
.pill {
  display: inline-block;
  padding: 4px 12px;
}
```

### 9.3 卡片边框与 accent bar 对齐

**问题**：卡片 `border: 1px solid` 导致内部 `position:absolute; left:0; top:0` 的 accent bar 被推到 border 内侧，SVG 转换后 bar 比卡片偏移 1px、短 2px，圆角也无法匹配。

**根因**：CSS `border` 占据布局空间，`left:0` 定位到 padding-box 而非 border-box。`overflow:hidden` 的裁切效果在 SVG 中丢失。

**强制写法**：
```css
/* 正确：box-shadow 不占布局空间，accent bar 与卡片外边缘完全对齐 */
.card {
  box-shadow: inset 0 0 0 1px var(--card-border);
  border-radius: var(--card-radius);
  overflow: hidden;
}
.card-accent-bar {
  position: absolute;
  left: 0; top: 0;
  width: 4px; height: 100%;
  /* 不加 border-radius — 由卡片 overflow:hidden 裁切 */
}
```

```css
/* 禁止：border 会把 accent bar 推到内侧 */
.card {
  border: 1px solid var(--card-border);
}
```
