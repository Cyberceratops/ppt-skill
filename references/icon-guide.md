# Lucide 图标系统使用指南

## 概览

PPT 设计稿中的图标统一使用 [Lucide](https://lucide.dev) 图标库（1940 个矢量 SVG 图标）。
所有图标位于 `references/icons/` 目录，标签索引位于 `references/icons/tags.json`。

**核心原则：不再手绘 SVG 图标，而是从图标库匹配。**

---

## 使用方式

### 方式 1: 脚本智能匹配（推荐）

通过 `scripts/icon_resolver.py` 按关键词（中/英文）匹配图标：

```bash
# 获取最匹配的图标 SVG 代码
python SKILL_DIR/scripts/icon_resolver.py "增长" --svg --color "var(--accent-1)" --size 32

# 多关键词匹配，返回 top 5
python SKILL_DIR/scripts/icon_resolver.py "数据" "分析" "图表"

# 批量匹配（为每个卡片分配图标）
cat > OUTPUT_DIR/icon_queries.json << 'EOF'
[
  {"id": "card1_icon", "keywords": ["数据", "增长"]},
  {"id": "card2_icon", "keywords": ["安全", "防护"]},
  {"id": "card3_icon", "keywords": ["团队", "协作"]}
]
EOF
python SKILL_DIR/scripts/icon_resolver.py --batch OUTPUT_DIR/icon_queries.json --output-dir OUTPUT_DIR/icons_resolved --color "var(--accent-1)" --size 32
```

### 方式 2: 直接读取 SVG 文件

如果已知图标名，直接读取文件内容内联到 HTML：

```bash
# 图标路径格式
SKILL_DIR/references/icons/{icon-name}.svg

# 示例
cat SKILL_DIR/references/icons/trending-up.svg
cat SKILL_DIR/references/icons/shield-check.svg
```

---

## PPT 场景图标分类速查

| 分类 | 分类ID | 高频图标示例 |
|------|--------|-------------|
| 📊 图表/数据 | `chart` | `chart-bar`, `chart-line`, `chart-pie`, `trending-up`, `trending-down` |
| 💼 商务/办公 | `business` | `briefcase`, `building`, `target`, `award`, `trophy`, `presentation` |
| 💻 技术/开发 | `tech` | `cpu`, `server`, `database`, `code`, `terminal`, `cloud`, `brain` |
| 💰 金融/财务 | `finance` | `dollar-sign`, `wallet`, `credit-card`, `coins`, `banknote` |
| 💬 通讯/协作 | `communication` | `message-circle`, `mail`, `phone`, `video`, `share-2`, `megaphone` |
| 👤 用户/团队 | `user` | `user`, `users`, `user-check`, `user-plus`, `contact` |
| 🧭 导航/方向 | `navigation` | `arrow-right`, `chevron-right`, `map-pin`, `compass`, `navigation` |
| 🔒 安全/权限 | `security` | `shield`, `lock`, `key`, `fingerprint`, `scan`, `shield-check` |
| 📁 文件/文档 | `file` | `file-text`, `folder`, `book`, `notebook`, `save`, `download` |
| 🎨 媒体/设计 | `media` | `image`, `camera`, `palette`, `pen-tool`, `layers`, `figma` |
| 📱 设备/硬件 | `device` | `smartphone`, `monitor`, `laptop`, `printer`, `headphones` |
| ⚡ 操作/动作 | `action` | `check`, `plus`, `edit`, `trash`, `search`, `settings`, `filter` |
| ⏰ 时间/日程 | `time` | `clock`, `timer`, `calendar`, `hourglass`, `history` |
| 🌿 自然/环保 | `nature` | `leaf`, `tree`, `sun`, `cloud`, `sprout`, `recycle` |

> 可用 `python SKILL_DIR/scripts/icon_resolver.py --categories` 查看完整列表
> 可用 `python SKILL_DIR/scripts/icon_resolver.py --category chart` 浏览某分类所有图标

---

## 在 HTML 设计稿中使用图标

### 内联 SVG（标准做法）

图标以内联 SVG 形式嵌入 HTML，像素级可控：

```html
<!-- 列表项前的图标 -->
<div style="display:flex; align-items:center; gap:12px; margin-bottom:10px;">
  <div style="width:32px; height:32px; display:flex; align-items:center; justify-content:center;
              background:rgba(34,211,238,0.1); border-radius:8px;">
    <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24"
         fill="none" stroke="var(--accent-1)" stroke-width="2"
         stroke-linecap="round" stroke-linejoin="round">
      <path d="M22 12h-2.48a2 2 0 0 0-1.93 1.46l-2.35 8.36..."/>
    </svg>
  </div>
  <span style="font-size:17px; color:var(--text-secondary);">列表项文字</span>
</div>
```

### 图标样式规范

| 属性 | 值 | 说明 |
|------|-----|------|
| `width` / `height` | 16-32px | 列表项 16-20px，卡片标题旁 24px，大图标 32px |
| `stroke` | `var(--accent-1)` | 使用 CSS 变量，与风格主题一致 |
| `stroke-width` | `2` (默认) 或 `1.5` | 小尺寸可用 1.5 减少笨重感 |
| `fill` | `none` | Lucide 是线条风格图标，保持 fill=none |

### 图标容器规范

为保证图标在视觉上与文字对齐且有"呼吸感"，推荐使用图标容器：

```html
<!-- 标准图标容器（浅色风格） -->
<div style="width:40px; height:40px; display:flex; align-items:center; justify-content:center;
            background:rgba(var(--accent-1-rgb), 0.1); border-radius:10px;">
  <!-- SVG 图标放这里 -->
</div>

<!-- 标准图标容器（深色风格） -->
<div style="width:40px; height:40px; display:flex; align-items:center; justify-content:center;
            background:rgba(255,255,255,0.05); border-radius:10px;">
  <!-- SVG 图标放这里 -->
</div>
```

---

## 使用场景决策表

| 卡片类型 | 是否使用图标 | 图标位置 | 推荐尺寸 |
|---------|-------------|---------|---------|
| text（列表式） | ✅ 每个列表项配一个 | 列表项左侧 | 16-20px |
| text（段落式） | ✅ 标题旁 | 标题左侧或上方 | 24-32px |
| data | ✅ KPI 标签旁 | 数字/标签左侧 | 20-24px |
| list | ✅ 每项一个 | 替代圆点标记 | 16-20px |
| process | ✅ 每步一个 | 步骤节点内或上方 | 24-32px |
| tag_cloud | ❌ 不需要 | - | - |
| data_highlight | ⚡ 可选 | 大数字上方或旁边 | 32-40px |

---

## 管线兼容性

Lucide SVG 图标在 PPT 生成管线中完全兼容：

| 阶段 | 兼容性 | 说明 |
|------|--------|------|
| HTML 内联 | ✅ | 标准 SVG 元素 |
| dom-to-svg (html2svg.py) | ✅ | SVG 嵌套 SVG 被保留 |
| svg2pptx.py | ✅ | `<path>` → OOXML `custGeom`  |
| PPTX 显示 | ✅ | 原生矢量形状，可放大不失真 |

> **注意**: Lucide 图标使用 `stroke`（线条）而非 `fill`（填充），
> `svg2pptx.py` 的 `_path()` 方法已支持 `stroke` 属性。
