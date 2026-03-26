# PPT Agent Skill

**[English](README_EN.md)**

> 模拟万元/页级 PPT 设计公司的完整工作流，从一句话需求到专业级演示文稿。

> **期望管理**：AI 生成的 PPT 能达到 80-90% 的完成度（结构合理、风格统一、数据可视化到位），
> 但局部细节（文字溢出、间距微调、个别页面排版）仍需人工审查和微调。
> 定位是**高质量初稿生成器**，将 8-16 小时的手工制作压缩到 25 分钟 AI 生成 + 10 分钟人工润色。

## 效果展示

> 以「PPT Agent Skill 降本增效」为主题的示例输出（蓝白商务风格，10 页，全流程约 25 分钟）：

| 封面页 | 传统 vs AI 对比页 |
|:---:|:---:|
| ![封面页](doc/showcase/slide_01.png) | ![对比页](doc/showcase/slide_04.png) |

| 6 步 Pipeline | 降本增效数据 |
|:---:|:---:|
| ![Pipeline](doc/showcase/slide_06.png) | ![数据总览](doc/showcase/slide_08.png) |

| ROI 测算 | 结束页 |
|:---:|:---:|
| ![ROI](doc/showcase/slide_09.png) | ![结束页](doc/showcase/slide_10.png) |

## 工作流概览

```
一句话需求 → 需求调研 → 资料搜集 → 大纲策划 → 策划稿 → 风格+配图+HTML → 后处理(SVG+PPTX)
```

| 步骤 | 说明 | 工具 |
|------|------|------|
| Step 1 | 需求调研（7 题三层递进） | Agent 对话 |
| Step 2 | 资料搜集 | `web_search.py`（Brave + Tavily 双引擎） |
| Step 3 | 大纲策划（金字塔原理） | Prompt #2 |
| Step 4 | 内容分配 + 策划稿 | Prompt #3 + Bento Grid 布局选择 |
| Step 5 | 风格 + 配图 + HTML 设计稿 | `generate_image.py`（Gemini 生图）+ Prompt #4 |
| Step 6 | 后处理 | `html2svg.py` → `svg2pptx.py` |

## 核心特性

| 特性 | 说明 |
|------|------|
| **6 步 Pipeline** | 模拟专业 PPT 公司完整工作流，端到端自动化 |
| **智能搜索** | Brave + Tavily 双引擎，零依赖 Python 脚本，自动降级容错 |
| **AI 配图** | Gemini 原生生图，16:9 宽屏，智能判断配图范围（封面/章节/结束页） |
| **6 种预置风格** | 科技年终汇报 / 展会展览 / 扁平插画汇报 / 扁平插画培训 / 蓝色科技互联网 / 蓝色立体活动策划（基于公司常用模板提炼） |
| **Lucide 图标系统** | 1940 个矢量 SVG 图标，19 个 PPT 场景分类，智能中英文关键词匹配（`icon_resolver.py`） |
| **7 种 Bento Grid 布局** | 卡片式灵活布局，内容驱动版式自动选择 |
| **排版系统** | 7 级字号阶梯 + 中英文混排 + 60-30-10 色彩法则 |
| **8 种数据可视化** | 进度条 / 环形图 / 迷你折线 / 对比柱 / 点阵图 / KPI 卡等（纯 CSS/SVG） |
| **管线兼容规范** | `pipeline-compat.md` 记录所有 CSS → SVG → PPTX 转换陷阱和正确写法 |
| **PPTX 全链路可编辑** | HTML → SVG → PPTX，PPT 365 中右键"转换为形状"即可编辑 |
| **跨平台可移植** | 所有外部能力（搜索/生图/转换）均为独立 Python 脚本 + `.env` 配置，不绑定任何 Agent 框架 |

## 环境依赖

**必须：**
- **Python** >= 3.8
- **Node.js** >= 18（Puppeteer + dom-to-svg 要求，`node --version` 确认当前 shell 实际使用的版本）

**安装：**
```bash
pip install python-pptx lxml Pillow
```

> **重要**：Puppeteer 首次安装需要下载 Chromium（~170MB），dom-to-svg 也需要编译，
> 建议在使用前提前安装，避免工作流执行到 Step 6 时长时间等待：
> ```bash
> cd ppt-output 
  npm init -y 
  npm install puppeteer dom-to-svg
> ```
> `html2svg.py` 首次运行时如未检测到依赖也会自动安装，但耗时可能导致超时。

**降级路径（dom-to-svg 不可用时）：**

当 Node.js < 18 或 dom-to-svg 安装失败时，html2svg.py 自动降级为 Puppeteer PDF + pdf2svg 方案（文字变 path，不可编辑）。此路径需要系统级 pdf2svg：
```bash
# Debian/Ubuntu
sudo apt install pdf2svg
# macOS
brew install pdf2svg
```

**可选（配置 `.env`）：**
```bash
cp .env.example .env
# 编辑 .env 填入 API Key：
# BRAVE_API_KEY=xxx       — 网页搜索（Brave Search，免费 2000 次/月）
# TAVILY_API_KEY=xxx      — 网页搜索 + 内容提取（Tavily）
# IMAGE_API_KEY=xxx       — AI 配图（Gemini 生图）
# IMAGE_API_BASE=xxx      — 生图 API 地址
# IMAGE_MODEL=xxx         — 生图模型名
```

## 目录结构

```
ppt-agent-skill/
  SKILL.md                        # Agent 主工作流指令（入口）
  .env.example                    # 环境变量模板
  references/
    prompts.md                    # 5 套 Prompt 模板
    style-system.md               # 6 种预置风格 + CSS 变量 + 明度自动判断
    bento-grid.md                 # 7 种布局规格 + 6 种卡片类型
    pipeline-compat.md            # HTML→SVG→PPTX 管线兼容性规则
    icon-guide.md                 # Lucide 图标系统使用指南（19 分类速查）
    icons/                        # 1940 个 Lucide SVG 图标
    icons/tags.json               # 图标标签索引
    method.md                     # 核心方法论
  scripts/
    web_search.py                 # 网页搜索（Brave + Tavily 双引擎）
    generate_image.py             # AI 配图（Gemini 原生生图）
    icon_resolver.py              # 图标智能匹配（中英文关键词 → Lucide SVG）
    html_packager.py              # 多页 HTML 合并为翻页预览
    html2svg.py                   # HTML → SVG（dom-to-svg，文字可编辑）
    svg2pptx.py                   # SVG → PPTX（OOXML 原生形状）
  doc/
    showcase/                     # README 展示图
```

## 输出产物

所有产物输出到 `ppt-output/{主题}_{日期}/` 目录（如 `ppt-output/AI安全培训_20260326/`）。
主题名从用户输入自动提取（≤10 字符，去除文件名非法字符），日期为 `YYYYMMDD` 格式。

### 最终交付物

| 文件 | 格式 | 说明 |
|------|------|------|
| `{主题}_{日期}.pptx` | PPTX | 最终演示文稿，PPT 365 中右键"转换为形状"可编辑文字和形状 |
| `{主题}_{日期}_preview.html` | HTML | 浏览器打开即可翻页预览，包含所有页面 |
| `svg/*.svg` | SVG | 逐页矢量文件，也可单独拖入 PPT 编辑 |

### 设计稿源文件

| 文件 | 格式 | 说明 |
|------|------|------|
| `slides/slide_XX.html` | HTML | 逐页 HTML 设计稿，1280x720px 固定画布，所有样式内联 |
| `images/slide_XX.png` | PNG | AI 生成配图，16:9 宽屏 |

### 流程中间产物

| 文件 | 说明 |
|------|------|
| `outline.json` | 大纲结构（parts → chapters → pages） |
| `planning.json` | 策划稿（每页的卡片类型、布局、内容定义） |
| `style.json` | 风格定义（颜色变量 + 字体 + 渐变 + 装饰元素） |
| `queries.json` | 搜索查询列表 |
| `search_results/*.json` | 搜索结果 |
| `images/batch.json` | 配图批次定义 |
| `notes.json` | 演讲者备注（可选，`--notes` 参数注入 PPTX） |

## 使用方式

在对话中描述需求即可触发，Agent 自动执行 6 步工作流：

```
你："帮我做一个关于 X 的 PPT"
  → Step 1: Agent 提问调研需求
  → Step 2: web_search.py 搜索资料
  → Step 3-4: 生成大纲 → 策划稿
  → Step 5: 风格决策 + generate_image.py 配图 + 逐页 HTML 设计稿
  → Step 6: html2svg.py + svg2pptx.py → 输出 PPTX
```

**触发示例：**

| 场景 | 说法 |
|------|------|
| 纯主题 | "帮我做个 PPT" / "做一个关于 X 的演示" |
| 带素材 | "把这篇文档做成 PPT" / "用这份报告做 slides" |
| 带要求 | "做 15 页暗黑风的 AI 安全汇报材料" |
| 隐式触发 | "我要给老板汇报 Y" / "做个培训课件" / "做路演 deck" |

## 许可证

[MIT](LICENSE)
