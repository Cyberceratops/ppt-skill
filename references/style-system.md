# 风格系统

## 风格数据模型

每套风格由以下字段定义：

```json
{
  "style_name": "风格名称",
  "style_id": "corp_tech | mwc_expo | flat_report | flat_training | sci_tech_blue | event_blue",
  "background": {
    "primary": "#色值",
    "gradient_to": "#色值"
  },
  "card": {
    "gradient_from": "#色值",
    "gradient_to": "#色值",
    "border": "rgba(...)",
    "border_radius": 12
  },
  "text": {
    "primary": "#色值",
    "secondary": "rgba(...)",
    "title_size": 28,
    "body_size": 14,
    "card_title_size": 20
  },
  "accent": {
    "primary": ["#渐变起", "#渐变止"],
    "secondary": ["#渐变起", "#渐变止"]
  },
  "font_family": "字体族",
  "grid_pattern": {
    "enabled": true,
    "size": 40,
    "dot_radius": 1,
    "dot_color": "#色值",
    "dot_opacity": 0.05
  },
  "decorations": {
    "corner_lines": false,
    "glow_effects": false,
    "description": "装饰元素描述"
  }
}
```

---

## 预置风格库

> 以下风格基于公司常用 PPT 模板提炼，结合通用设计原则调优。
> 原始模板文件保存在 `doc/template/`，备份风格保存在 `references/style-system.backup.md`。

### 1. 科技年终汇报 (corp_tech)

适用场景：年终总结、科技主题汇报、技术成果展示、产品发布会

提炼来源：`12年终[科技]系列汇报PPT` -- 深色背景 + 科技蓝橙配色

```json
{
  "style_name": "科技年终汇报 (Corporate Tech)",
  "style_id": "corp_tech",
  "background": { "primary": "#0A0E1A", "gradient_to": "#111827" },
  "card": { "gradient_from": "#1E293B", "gradient_to": "#0F172A", "border": "rgba(255,255,255,0.06)", "border_radius": 12 },
  "text": { "primary": "#FFFFFF", "secondary": "rgba(255,255,255,0.7)", "title_size": 28, "body_size": 14, "card_title_size": 20 },
  "accent": { "primary": ["#4472C4", "#5B9BD5"], "secondary": ["#ED7D31", "#FFC000"] },
  "font_family": "'Alibaba PuHuiTi', 'Noto Sans SC', 'Microsoft YaHei', system-ui, sans-serif",
  "grid_pattern": { "enabled": true, "size": 40, "dot_radius": 1, "dot_color": "#FFFFFF", "dot_opacity": 0.04 },
  "decorations": { "corner_lines": true, "glow_effects": true, "description": "蓝色光晕 + 橙色数据点缀，角落装饰线条，深邃科技感" }
}
```

```css
:root {
  --bg-primary: #0A0E1A;
  --bg-secondary: #111827;
  --card-bg-from: #1E293B;
  --card-bg-to: #0F172A;
  --card-border: rgba(255,255,255,0.06);
  --card-radius: 12px;
  --text-primary: #FFFFFF;
  --text-secondary: rgba(255,255,255,0.7);
  --accent-1: #4472C4;
  --accent-2: #5B9BD5;
  --accent-3: #ED7D31;
  --accent-4: #FFC000;
}
```

---

### 2. 展会展览 (mwc_expo)

适用场景：巴塞罗那 MWC 展会、CES、产品展览、国际会议、品牌展示

提炼来源：`MWC模板-1920X1080` -- 纯黑背景 + 蓝色天空渐变 + 展会大气感

```json
{
  "style_name": "展会展览 (MWC Expo)",
  "style_id": "mwc_expo",
  "background": { "primary": "#000000", "gradient_to": "#0C1929" },
  "card": { "gradient_from": "#151E2D", "gradient_to": "#0A1018", "border": "rgba(91,155,213,0.12)", "border_radius": 14 },
  "text": { "primary": "#FFFFFF", "secondary": "rgba(255,255,255,0.65)", "title_size": 28, "body_size": 14, "card_title_size": 20 },
  "accent": { "primary": ["#5B9BD5", "#4472C4"], "secondary": ["#ED7D31", "#FFC000"] },
  "font_family": "'Myriad Pro', '方正标雅宋简体', 'Microsoft YaHei', system-ui, sans-serif",
  "grid_pattern": { "enabled": false },
  "decorations": { "corner_lines": false, "glow_effects": true, "description": "纯黑到深蓝渐变，大面积图片氛围底图，科技光晕点缀，展会级大气视觉" }
}
```

```css
:root {
  --bg-primary: #000000;
  --bg-secondary: #0C1929;
  --card-bg-from: #151E2D;
  --card-bg-to: #0A1018;
  --card-border: rgba(91,155,213,0.12);
  --card-radius: 14px;
  --text-primary: #FFFFFF;
  --text-secondary: rgba(255,255,255,0.65);
  --accent-1: #5B9BD5;
  --accent-2: #4472C4;
  --accent-3: #ED7D31;
  --accent-4: #FFC000;
}
```

---

### 3. 扁平插画汇报 (flat_report)

适用场景：月度/季度工作汇报、日常总结、部门汇报

提炼来源：`月度工作汇报扁平插画风PPT模板` -- 白色背景 + 蓝色主题 + 扁平插画风

```json
{
  "style_name": "扁平插画汇报 (Flat Report)",
  "style_id": "flat_report",
  "background": { "primary": "#FFFFFF", "gradient_to": "#F0F5FF" },
  "card": { "gradient_from": "#F5F8FF", "gradient_to": "#EBF0FA", "border": "rgba(7,113,252,0.12)", "border_radius": 16 },
  "text": { "primary": "#282828", "secondary": "#666666", "title_size": 28, "body_size": 14, "card_title_size": 20 },
  "accent": { "primary": ["#0771FC", "#0563EB"], "secondary": ["#FF8C3A", "#FF6D1F"] },
  "font_family": "'GEETYPE-XinGothicGB', 'OPPOSans', 'Microsoft YaHei', system-ui, sans-serif",
  "grid_pattern": { "enabled": false },
  "decorations": { "corner_lines": false, "glow_effects": false, "description": "清爽白底 + 蓝色标题装饰条，大圆角卡片，扁平化视觉，插画元素留白区" }
}
```

```css
:root {
  --bg-primary: #FFFFFF;
  --bg-secondary: #F0F5FF;
  --card-bg-from: #F5F8FF;
  --card-bg-to: #EBF0FA;
  --card-border: rgba(7,113,252,0.12);
  --card-radius: 16px;
  --text-primary: #282828;
  --text-secondary: #666666;
  --accent-1: #0771FC;
  --accent-2: #0563EB;
  --accent-3: #FF8C3A;
  --accent-4: #FF6D1F;
}
```

---

### 4. 扁平插画培训 (flat_training)

适用场景：新员工培训、入职引导、内部培训课件、企业文化宣贯

提炼来源：`蓝色扁平插画风新员工入职培训PPT` -- 白底蓝色 + 培训风格 + 活泼配色

```json
{
  "style_name": "扁平插画培训 (Flat Training)",
  "style_id": "flat_training",
  "background": { "primary": "#FFFFFF", "gradient_to": "#F8FAFF" },
  "card": { "gradient_from": "#FFFFFF", "gradient_to": "#F0F4FF", "border": "rgba(71,134,251,0.15)", "border_radius": 20 },
  "text": { "primary": "#282828", "secondary": "#666666", "title_size": 28, "body_size": 14, "card_title_size": 20 },
  "accent": { "primary": ["#4786FB", "#3B6FE0"], "secondary": ["#FF7043", "#FF5722"] },
  "font_family": "'Noto Sans SC', 'Microsoft YaHei', system-ui, sans-serif",
  "grid_pattern": { "enabled": false },
  "decorations": { "corner_lines": false, "glow_effects": false, "description": "清新白底 + 天蓝强调色，大圆角卡片(20px)，活泼扁平插画风，适合轻松的培训氛围" }
}
```

```css
:root {
  --bg-primary: #FFFFFF;
  --bg-secondary: #F8FAFF;
  --card-bg-from: #FFFFFF;
  --card-bg-to: #F0F4FF;
  --card-border: rgba(71,134,251,0.15);
  --card-radius: 20px;
  --text-primary: #282828;
  --text-secondary: #666666;
  --accent-1: #4786FB;
  --accent-2: #3B6FE0;
  --accent-3: #FF7043;
  --accent-4: #FF5722;
}
```

---

### 5. 蓝色科技互联网 (sci_tech_blue)

适用场景：互联网行业项目计划、技术方案、产品架构、开发者大会

提炼来源：`蓝色科技风互联网行业项目计划PPT模板` -- 深蓝科技背景 + 青蓝渐变 + 数据驱动

```json
{
  "style_name": "蓝色科技互联网 (Sci-Tech Blue)",
  "style_id": "sci_tech_blue",
  "background": { "primary": "#020838", "gradient_to": "#0A1252" },
  "card": { "gradient_from": "#0F1A4A", "gradient_to": "#080E35", "border": "rgba(20,229,252,0.1)", "border_radius": 12 },
  "text": { "primary": "#FFFFFF", "secondary": "rgba(255,255,255,0.7)", "title_size": 28, "body_size": 14, "card_title_size": 20 },
  "accent": { "primary": ["#14E5FC", "#4472C4"], "secondary": ["#043BB9", "#0563C1"] },
  "font_family": "'Reeji-CloudHeiDa-GB', 'GEETYPE-XinGothicGB', 'Maven Pro', 'Microsoft YaHei', system-ui, sans-serif",
  "grid_pattern": { "enabled": true, "size": 48, "dot_radius": 1, "dot_color": "#14E5FC", "dot_opacity": 0.03 },
  "decorations": { "corner_lines": true, "glow_effects": true, "description": "深蓝星空背景，青色/蓝色霓虹光效，科技粒子感，数据可视化主导" }
}
```

```css
:root {
  --bg-primary: #020838;
  --bg-secondary: #0A1252;
  --card-bg-from: #0F1A4A;
  --card-bg-to: #080E35;
  --card-border: rgba(20,229,252,0.1);
  --card-radius: 12px;
  --text-primary: #FFFFFF;
  --text-secondary: rgba(255,255,255,0.7);
  --accent-1: #14E5FC;
  --accent-2: #4472C4;
  --accent-3: #043BB9;
  --accent-4: #0563C1;
}
```

---

### 6. 蓝色立体活动策划 (event_blue)

适用场景：品牌活动策划、营销推广方案、互联网活动、产品推广

提炼来源：`蓝色立体风互联网活动策划方案PPT` -- 浅色背景 + 立体渐变 + 蓝色系 + 详尽数据

```json
{
  "style_name": "蓝色立体活动策划 (Event Blue)",
  "style_id": "event_blue",
  "background": { "primary": "#F4F6FA", "gradient_to": "#EAEFF6" },
  "card": { "gradient_from": "#FFFFFF", "gradient_to": "#F5F7FC", "border": "rgba(68,114,196,0.1)", "border_radius": 12 },
  "text": { "primary": "#343434", "secondary": "#666666", "title_size": 28, "body_size": 14, "card_title_size": 20 },
  "accent": { "primary": ["#4472C4", "#3B63B0"], "secondary": ["#ED7D31", "#D96A1F"] },
  "font_family": "'GEETYPE-XinGothicGB', 'Reeji-CloudZhongDeng-GB', 'Microsoft YaHei', system-ui, sans-serif",
  "grid_pattern": { "enabled": false },
  "decorations": { "corner_lines": false, "glow_effects": false, "description": "浅灰蓝底，立体卡片阴影，蓝色渐变装饰条，橙色数据强调，信息密度高" }
}
```

```css
:root {
  --bg-primary: #F4F6FA;
  --bg-secondary: #EAEFF6;
  --card-bg-from: #FFFFFF;
  --card-bg-to: #F5F7FC;
  --card-border: rgba(68,114,196,0.1);
  --card-radius: 12px;
  --text-primary: #343434;
  --text-secondary: #666666;
  --accent-1: #4472C4;
  --accent-2: #3B63B0;
  --accent-3: #ED7D31;
  --accent-4: #D96A1F;
}
```

---

## 风格自动推断

当用户未指定风格时，根据主题关键词自动推断：

| 关键词匹配 | 推荐风格 |
|-----------|---------|
| 年终总结、年度汇报、成果展示、KPI、OKR | corp_tech |
| 展会、MWC、CES、展览、博览会、品牌展示、国际会议 | mwc_expo |
| 月度汇报、季度总结、工作汇报、部门总结、日常 | flat_report |
| 培训、入职、新人、课件、企业文化、内训、工作坊 | flat_training |
| AI、互联网、科技项目、开发、SaaS、云、平台、API、大模型、LLM、数据、算法、架构 | sci_tech_blue |
| 活动策划、营销、推广、品牌活动、市场方案、用户增长 | event_blue |
| 其他未匹配 | flat_report（最通用的默认风格） |

## 自定义风格

用户可以在 Step 1 的"补充需求"中指定品牌色：

> "品牌主色 #1DA1F2，背景用深色"

此时基于最接近的预置风格，替换对应的色值字段：
1. 将 accent.primary 替换为用户品牌色
2. 根据品牌色明度自动选择 background 深/浅
3. 其他字段保持预置风格的值
