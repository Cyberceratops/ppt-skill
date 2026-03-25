#!/usr/bin/env python3
"""Lucide 图标智能匹配器

根据关键词/场景描述，从 Lucide 图标库中匹配最合适的图标，
返回可直接内联到 HTML 的 SVG 代码。

用法：
    # 单个关键词匹配（返回最佳匹配）
    python icon_resolver.py "growth"

    # 多关键词匹配（返回每个关键词的最佳匹配）
    python icon_resolver.py "growth" "network" "security" "database"

    # 批量模式：从 JSON 文件读取
    python icon_resolver.py --batch queries.json --output-dir OUTPUT_DIR

    # 自定义颜色和尺寸
    python icon_resolver.py "growth" --color "#22D3EE" --size 32

    # 列出所有分类
    python icon_resolver.py --categories

    # 按分类浏览
    python icon_resolver.py --category "chart"

    # 输出为 JSON（含 SVG 内容和元数据）
    python icon_resolver.py "growth" --json

queries.json 格式:
    [
        {"id": "card1", "keywords": ["growth", "revenue"]},
        {"id": "card2", "keywords": ["security", "shield"]}
    ]
"""

import argparse
import json
import os
import re
import sys
from pathlib import Path
from collections import defaultdict

# 脚本所在目录
SCRIPT_DIR = Path(__file__).resolve().parent
# 图标目录和标签文件
ICONS_DIR = SCRIPT_DIR.parent / "references" / "icons"
TAGS_FILE = ICONS_DIR / "tags.json"

# ---- PPT 场景专用的语义扩展映射 ----
# 将中文/业务关键词映射到 Lucide 标签空间
SEMANTIC_ALIASES = {
    # 数据/图表
    "数据": ["chart", "data", "analytics", "statistics", "graph"],
    "图表": ["chart", "bar chart", "graph", "pie", "analytics"],
    "增长": ["growth", "trending up", "arrow up", "increase", "rise"],
    "下降": ["trending down", "arrow down", "decrease", "decline"],
    "趋势": ["trending", "chart", "line chart", "sparkline"],
    "分析": ["analytics", "chart", "search", "magnify", "scan"],
    "统计": ["statistics", "chart", "bar", "pie"],
    "KPI": ["gauge", "target", "goal", "metric", "chart"],
    "指标": ["gauge", "meter", "target", "dashboard"],
    "仪表盘": ["dashboard", "gauge", "layout", "grid"],

    # 商务/组织
    "公司": ["building", "office", "company", "corporate"],
    "团队": ["users", "group", "people", "team", "organization"],
    "用户": ["user", "person", "profile", "account", "avatar"],
    "会议": ["video", "presentation", "meeting", "calendar"],
    "合作": ["handshake", "partnership", "link", "connect"],
    "管理": ["settings", "sliders", "admin", "control"],
    "领导": ["crown", "star", "award", "trophy"],
    "战略": ["target", "crosshair", "compass", "map"],
    "项目": ["folder", "kanban", "clipboard", "task"],
    "流程": ["workflow", "git branch", "route", "path"],
    "效率": ["zap", "rocket", "timer", "gauge", "speed"],
    "成本": ["dollar", "coins", "wallet", "receipt", "calculator"],
    "收入": ["dollar", "trending up", "wallet", "banknote"],
    "利润": ["coins", "piggy bank", "trending up", "dollar"],

    # 技术
    "AI": ["brain", "cpu", "bot", "sparkles", "wand"],
    "人工智能": ["brain", "cpu", "bot", "sparkles", "wand"],
    "机器学习": ["brain", "cpu", "graduation cap", "network"],
    "云计算": ["cloud", "server", "database", "upload"],
    "云": ["cloud", "server", "upload", "download"],
    "服务器": ["server", "hard drive", "database", "rack"],
    "数据库": ["database", "server", "hard drive", "cylinder"],
    "API": ["plug", "webhook", "code", "terminal", "link"],
    "代码": ["code", "terminal", "command", "braces"],
    "网络": ["network", "wifi", "globe", "ethernet", "router"],
    "安全": ["shield", "lock", "key", "fingerprint", "scan"],
    "加密": ["lock", "key", "shield", "hash"],
    "物联网": ["cpu", "radio", "bluetooth", "wifi", "signal"],
    "IoT": ["cpu", "radio", "bluetooth", "wifi", "signal"],
    "芯片": ["cpu", "chip", "circuit", "microchip"],
    "5G": ["signal", "antenna", "radio", "wifi"],
    "区块链": ["link", "blocks", "chain", "hash"],

    # 产品/设计
    "产品": ["box", "package", "shopping bag", "gift"],
    "设计": ["pen tool", "palette", "brush", "figma", "vector"],
    "创新": ["lightbulb", "sparkles", "wand", "star", "rocket"],
    "功能": ["puzzle", "layers", "component", "blocks"],
    "性能": ["gauge", "zap", "rocket", "timer", "speedometer"],
    "质量": ["badge", "check", "award", "star", "shield"],
    "品牌": ["tag", "bookmark", "flag", "stamp"],

    # 营销/销售
    "营销": ["megaphone", "target", "mail", "share", "campaign"],
    "推广": ["megaphone", "speaker", "broadcast", "share"],
    "客户": ["user", "users", "heart", "smile", "handshake"],
    "转化": ["arrow right", "funnel", "filter", "target"],
    "漏斗": ["funnel", "filter", "chevron down"],
    "社交": ["share", "message", "users", "heart", "thumbs up"],
    "影响力": ["megaphone", "trending up", "star", "award"],

    # 通用概念
    "时间": ["clock", "timer", "calendar", "hourglass", "watch"],
    "位置": ["map pin", "map", "navigation", "compass", "globe"],
    "全球": ["globe", "earth", "world", "map"],
    "国际": ["globe", "languages", "flag", "plane"],
    "环保": ["leaf", "tree", "recycle", "sprout", "earth"],
    "绿色": ["leaf", "tree", "sprout", "recycle"],
    "健康": ["heart", "activity", "stethoscope", "pill"],
    "教育": ["graduation cap", "book", "school", "pencil"],
    "研究": ["microscope", "flask", "search", "book", "scroll"],
    "创意": ["lightbulb", "sparkles", "palette", "wand"],
    "速度": ["zap", "rocket", "gauge", "timer", "fast forward"],
    "连接": ["link", "plug", "network", "wifi", "cable"],
    "整合": ["puzzle", "merge", "combine", "layers", "blocks"],
    "自动化": ["bot", "repeat", "cog", "workflow", "wand"],
    "可靠": ["shield", "check", "lock", "award"],
    "可扩展": ["maximize", "expand", "layers", "plus"],
    "灵活": ["move", "shuffle", "sliders", "toggle"],

    # 文档/内容
    "文档": ["file", "document", "text", "scroll", "book"],
    "报告": ["file text", "clipboard", "chart", "presentation"],
    "演示": ["presentation", "monitor", "projector"],
    "通知": ["bell", "alert", "info", "notification"],
    "消息": ["message", "mail", "chat", "inbox"],
    "搜索": ["search", "magnifying glass", "scan", "eye"],
    "设置": ["settings", "cog", "sliders", "wrench", "tool"],
    "帮助": ["help circle", "info", "question", "life buoy"],
    "警告": ["alert", "warning", "triangle alert", "shield alert"],
    "成功": ["check", "circle check", "badge check", "trophy"],
    "错误": ["x", "circle x", "alert", "bug"],

    # English common terms (also useful)
    "growth": ["trending up", "chart", "arrow up", "sprout", "rocket"],
    "revenue": ["dollar", "coins", "wallet", "trending up", "banknote"],
    "security": ["shield", "lock", "key", "fingerprint"],
    "performance": ["gauge", "zap", "rocket", "timer", "speedometer"],
    "innovation": ["lightbulb", "sparkles", "wand", "star", "rocket"],
    "network": ["network", "wifi", "globe", "ethernet", "share"],
    "database": ["database", "server", "hard drive", "cylinder"],
    "cloud": ["cloud", "server", "upload", "download"],
    "mobile": ["smartphone", "phone", "tablet", "device"],
    "desktop": ["monitor", "laptop", "computer", "display"],
    "email": ["mail", "inbox", "send", "envelope"],
    "settings": ["settings", "cog", "sliders", "wrench"],
    "download": ["download", "arrow down", "save", "import"],
    "upload": ["upload", "arrow up", "cloud upload", "export"],
    "share": ["share", "external link", "forward", "send"],
    "filter": ["filter", "funnel", "sliders", "sort"],
    "search": ["search", "magnifying glass", "scan", "find"],
    "notification": ["bell", "alert", "inbox", "message"],
    "payment": ["credit card", "wallet", "dollar", "banknote", "coins"],
    "cart": ["shopping cart", "bag", "basket"],
    "home": ["home", "house", "building"],
    "menu": ["menu", "hamburger", "list", "grid"],
    "profile": ["user", "avatar", "circle user"],
    "logout": ["log out", "door", "exit"],
    "refresh": ["refresh", "rotate", "sync", "reload"],
    "edit": ["pen", "edit", "pencil", "type"],
    "delete": ["trash", "x", "eraser", "minus"],
    "save": ["save", "bookmark", "heart", "download"],
    "print": ["printer", "print"],
    "copy": ["copy", "clipboard", "duplicate"],
    "lock": ["lock", "shield", "key"],
    "unlock": ["unlock", "key", "open"],
    "check": ["check", "circle check", "badge check"],
    "close": ["x", "circle x", "minus"],
    "expand": ["maximize", "expand", "arrows", "full screen"],
    "compress": ["minimize", "shrink", "compress"],
}

# ---- PPT 场景分类 (面向 PPT 设计的高频分类) ----
PPT_CATEGORIES = {
    "chart": {
        "display": "📊 图表/数据",
        "keywords": ["chart", "graph", "analytics", "statistics", "bar", "pie", "line", "trending",
                     "gauge", "meter"],
    },
    "business": {
        "display": "💼 商务/办公",
        "keywords": ["building", "briefcase", "presentation", "handshake", "badge", "id card",
                     "clipboard", "target", "award", "trophy", "crown", "stamp"],
    },
    "tech": {
        "display": "💻 技术/开发",
        "keywords": ["code", "terminal", "server", "database", "cpu", "cloud", "wifi", "globe",
                     "network", "plug", "cable", "bot", "brain", "circuit"],
    },
    "finance": {
        "display": "💰 金融/财务",
        "keywords": ["dollar", "coins", "wallet", "credit card", "banknote", "receipt",
                     "calculator", "piggy bank", "landmark"],
    },
    "communication": {
        "display": "💬 通讯/协作",
        "keywords": ["message", "mail", "phone", "video", "share", "send", "inbox",
                     "megaphone", "bell", "rss"],
    },
    "user": {
        "display": "👤 用户/团队",
        "keywords": ["user", "users", "person", "group", "contact", "profile", "avatar"],
    },
    "navigation": {
        "display": "🧭 导航/方向",
        "keywords": ["arrow", "chevron", "move", "navigation", "compass", "map", "route",
                     "direction", "corner"],
    },
    "security": {
        "display": "🔒 安全/权限",
        "keywords": ["shield", "lock", "key", "fingerprint", "scan", "eye", "alert",
                     "bug", "siren"],
    },
    "file": {
        "display": "📁 文件/文档",
        "keywords": ["file", "folder", "document", "book", "notebook", "scroll", "archive",
                     "save", "download", "upload"],
    },
    "media": {
        "display": "🎨 媒体/设计",
        "keywords": ["image", "camera", "video", "palette", "pen", "brush", "figma",
                     "layers", "frame", "crop"],
    },
    "device": {
        "display": "📱 设备/硬件",
        "keywords": ["smartphone", "monitor", "laptop", "tablet", "printer", "keyboard",
                     "mouse", "headphones", "speaker", "usb"],
    },
    "action": {
        "display": "⚡ 操作/动作",
        "keywords": ["check", "plus", "minus", "x", "edit", "trash", "copy", "refresh",
                     "settings", "search", "filter", "sort", "toggle"],
    },
    "time": {
        "display": "⏰ 时间/日程",
        "keywords": ["clock", "timer", "calendar", "hourglass", "watch", "alarm", "history"],
    },
    "nature": {
        "display": "🌿 自然/环保",
        "keywords": ["leaf", "tree", "flower", "sun", "moon", "cloud", "rain", "snow",
                     "mountain", "sprout", "recycle"],
    },
    "transport": {
        "display": "🚗 交通/物流",
        "keywords": ["car", "truck", "plane", "ship", "train", "bike", "bus",
                     "package", "box", "container"],
    },
    "health": {
        "display": "🏥 健康/医疗",
        "keywords": ["heart", "activity", "stethoscope", "pill", "syringe", "thermometer",
                     "hospital", "ambulance"],
    },
    "education": {
        "display": "🎓 教育/学习",
        "keywords": ["graduation cap", "book", "school", "pencil", "library", "backpack",
                     "apple", "ruler"],
    },
    "food": {
        "display": "🍽️ 餐饮/食品",
        "keywords": ["coffee", "pizza", "cake", "apple", "wine", "beer", "utensils",
                     "chef hat", "cooking"],
    },
    "shape": {
        "display": "🔷 形状/装饰",
        "keywords": ["circle", "square", "triangle", "hexagon", "star", "heart",
                     "diamond", "octagon", "sparkles"],
    },
}


class IconResolver:
    def __init__(self, icons_dir=None, tags_file=None):
        self.icons_dir = Path(icons_dir) if icons_dir else ICONS_DIR
        self.tags_file = Path(tags_file) if tags_file else TAGS_FILE
        self._tags = None
        self._reverse_index = None  # tag -> [icon_names]

    @property
    def tags(self):
        if self._tags is None:
            with open(self.tags_file, "r", encoding="utf-8") as f:
                self._tags = json.load(f)
        return self._tags

    @property
    def reverse_index(self):
        """反向索引：tag -> [icon_names]"""
        if self._reverse_index is None:
            self._reverse_index = defaultdict(list)
            for icon_name, icon_tags in self.tags.items():
                for tag in icon_tags:
                    self._reverse_index[tag.lower()].append(icon_name)
                # 图标名本身也作为索引 (e.g., "chart-bar" -> ["chart", "bar"])
                for part in icon_name.split("-"):
                    self._reverse_index[part.lower()].append(icon_name)
        return self._reverse_index

    def resolve(self, keywords, top_n=5):
        """根据关键词列表匹配图标，返回评分排序的结果。

        Args:
            keywords: 关键词列表，如 ["growth", "revenue"]
            top_n: 返回前 N 个结果

        Returns:
            [(icon_name, score, matched_tags), ...]
        """
        if isinstance(keywords, str):
            keywords = [keywords]

        # 扩展关键词：中文 -> 英文标签
        expanded = set()
        for kw in keywords:
            kw_lower = kw.lower().strip()
            if kw_lower in SEMANTIC_ALIASES:
                expanded.update(SEMANTIC_ALIASES[kw_lower])
            else:
                expanded.add(kw_lower)
                # 也尝试拆分英文短语
                for part in kw_lower.replace("-", " ").split():
                    expanded.add(part)

        # 评分每个图标
        scores = defaultdict(lambda: {"score": 0, "matched": []})

        for search_term in expanded:
            # 1. 精确匹配图标名
            if search_term.replace(" ", "-") in self.tags:
                icon_name = search_term.replace(" ", "-")
                scores[icon_name]["score"] += 10
                scores[icon_name]["matched"].append(f"name:{search_term}")

            # 2. 标签匹配
            for icon_name in self.reverse_index.get(search_term, []):
                scores[icon_name]["score"] += 3
                scores[icon_name]["matched"].append(f"tag:{search_term}")

            # 3. 部分匹配标签（如 "chart" 匹配 "chart-bar", "chart-pie"）
            for tag, icon_names in self.reverse_index.items():
                if search_term in tag or tag in search_term:
                    for icon_name in icon_names:
                        if icon_name not in [s for s in scores if scores[s]["score"] > 0]:
                            scores[icon_name]["score"] += 1
                            scores[icon_name]["matched"].append(f"partial:{tag}")

        # 排序并去重 matched 标签
        results = []
        for icon_name, data in scores.items():
            if data["score"] > 0:
                svg_path = self.icons_dir / f"{icon_name}.svg"
                if svg_path.exists():
                    seen = set()
                    unique_matched = []
                    for m in data["matched"]:
                        if m not in seen:
                            seen.add(m)
                            unique_matched.append(m)
                    results.append((icon_name, data["score"], unique_matched))

        results.sort(key=lambda x: x[1], reverse=True)
        return results[:top_n]

    def get_svg(self, icon_name, color=None, size=None, stroke_width=None):
        """获取图标的 SVG 代码，可自定义颜色和尺寸。

        Args:
            icon_name: 图标名（如 "chart-bar"）
            color: 颜色值（如 "#22D3EE" 或 "var(--accent-1)"），默认 currentColor
            size: 尺寸 px，默认 24
            stroke_width: 线宽，默认 2

        Returns:
            SVG 字符串，可直接内联到 HTML
        """
        svg_path = self.icons_dir / f"{icon_name}.svg"
        if not svg_path.exists():
            return None

        svg = svg_path.read_text(encoding="utf-8")
        # 移除注释行
        svg = re.sub(r"<!--.*?-->", "", svg, flags=re.DOTALL).strip()

        if color:
            svg = svg.replace('stroke="currentColor"', f'stroke="{color}"')
        if size:
            svg = re.sub(r'width="24"', f'width="{size}"', svg)
            svg = re.sub(r'height="24"', f'height="{size}"', svg)
        if stroke_width:
            svg = re.sub(r'stroke-width="2"', f'stroke-width="{stroke_width}"', svg)

        # 移除 class 属性（在 PPT HTML 中不需要）
        svg = re.sub(r'\s*class="[^"]*"', '', svg)

        return svg

    def list_categories(self):
        """列出所有 PPT 场景分类及其图标数量。"""
        result = {}
        for cat_id, cat_info in PPT_CATEGORIES.items():
            matched_icons = set()
            for kw in cat_info["keywords"]:
                for icon_name in self.reverse_index.get(kw, []):
                    matched_icons.add(icon_name)
            result[cat_id] = {
                "display": cat_info["display"],
                "count": len(matched_icons),
                "sample": sorted(matched_icons)[:8],
            }
        return result

    def browse_category(self, category):
        """浏览某个分类下的所有图标。"""
        if category not in PPT_CATEGORIES:
            return None
        cat_info = PPT_CATEGORIES[category]
        matched_icons = set()
        for kw in cat_info["keywords"]:
            for icon_name in self.reverse_index.get(kw, []):
                matched_icons.add(icon_name)
        return sorted(matched_icons)


def main():
    parser = argparse.ArgumentParser(
        description="Lucide 图标智能匹配器",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  python icon_resolver.py "growth"
  python icon_resolver.py "数据" "增长" --color "var(--accent-1)" --size 32
  python icon_resolver.py --categories
  python icon_resolver.py --category chart
  python icon_resolver.py --batch queries.json --output-dir ./icons_output
        """,
    )
    parser.add_argument("keywords", nargs="*", help="搜索关键词（中/英文均可）")
    parser.add_argument("--color", default=None, help="SVG stroke 颜色 (默认 currentColor)")
    parser.add_argument("--size", type=int, default=None, help="SVG 尺寸 px (默认 24)")
    parser.add_argument("--stroke-width", type=float, default=None, help="SVG 线宽 (默认 2)")
    parser.add_argument("--top", type=int, default=5, help="返回前 N 个匹配 (默认 5)")
    parser.add_argument("--json", action="store_true", help="输出 JSON 格式")
    parser.add_argument("--svg", action="store_true", help="输出第一个匹配的 SVG 代码")
    parser.add_argument("--categories", action="store_true", help="列出所有分类")
    parser.add_argument("--category", default=None, help="浏览某个分类的图标")
    parser.add_argument("--batch", default=None, help="批量模式：JSON 文件路径")
    parser.add_argument("--output-dir", default=None, help="批量模式输出目录")
    parser.add_argument("--icons-dir", default=None, help="图标目录路径")
    parser.add_argument("--tags-file", default=None, help="标签文件路径")

    args = parser.parse_args()
    resolver = IconResolver(icons_dir=args.icons_dir, tags_file=args.tags_file)

    # 列出分类
    if args.categories:
        cats = resolver.list_categories()
        print("PPT 场景图标分类：\n")
        for cat_id, info in cats.items():
            print(f"  {info['display']}  ({info['count']} 个)")
            print(f"    分类ID: {cat_id}")
            print(f"    示例: {', '.join(info['sample'])}")
            print()
        return

    # 浏览分类
    if args.category:
        icons = resolver.browse_category(args.category)
        if icons is None:
            print(f"未知分类: {args.category}", file=sys.stderr)
            print(f"可用分类: {', '.join(PPT_CATEGORIES.keys())}", file=sys.stderr)
            sys.exit(1)
        cat_info = PPT_CATEGORIES[args.category]
        print(f"{cat_info['display']} ({len(icons)} 个图标):\n")
        for icon in icons:
            tags = resolver.tags.get(icon, [])
            print(f"  {icon:30s}  tags: {', '.join(tags[:5])}")
        return

    # 批量模式
    if args.batch:
        batch_path = Path(args.batch)
        if not batch_path.exists():
            print(f"文件不存在: {batch_path}", file=sys.stderr)
            sys.exit(1)
        with open(batch_path, "r", encoding="utf-8") as f:
            queries = json.load(f)

        output_dir = Path(args.output_dir) if args.output_dir else batch_path.parent / "icons_resolved"
        output_dir.mkdir(parents=True, exist_ok=True)

        results = {}
        for q in queries:
            qid = q["id"]
            kws = q["keywords"]
            matches = resolver.resolve(kws, top_n=1)
            if matches:
                icon_name = matches[0][0]
                svg = resolver.get_svg(icon_name, color=args.color, size=args.size,
                                       stroke_width=args.stroke_width)
                if svg:
                    svg_path = output_dir / f"{qid}.svg"
                    svg_path.write_text(svg, encoding="utf-8")
                    results[qid] = {"icon": icon_name, "svg_file": str(svg_path)}
                    print(f"  [{qid}] -> {icon_name}")

        # 保存映射结果
        result_path = output_dir / "mapping.json"
        with open(result_path, "w", encoding="utf-8") as f:
            json.dump(results, f, ensure_ascii=False, indent=2)
        print(f"\n已保存到: {output_dir}")
        return

    # 单词/多词匹配
    if not args.keywords:
        parser.print_help()
        sys.exit(0)

    matches = resolver.resolve(args.keywords, top_n=args.top)

    if args.json:
        output = []
        for icon_name, score, matched in matches:
            svg = resolver.get_svg(icon_name, color=args.color, size=args.size,
                                   stroke_width=args.stroke_width)
            output.append({
                "icon": icon_name,
                "score": score,
                "matched_by": matched,
                "tags": resolver.tags.get(icon_name, []),
                "svg": svg,
            })
        print(json.dumps(output, ensure_ascii=False, indent=2))
        return

    if args.svg:
        if matches:
            svg = resolver.get_svg(matches[0][0], color=args.color, size=args.size,
                                   stroke_width=args.stroke_width)
            if svg:
                print(svg)
        return

    # 默认：打印匹配结果表
    print(f"关键词: {', '.join(args.keywords)}")
    print(f"{'排名':>4}  {'图标名':30s}  {'分数':>4}  匹配来源")
    print("-" * 80)
    for i, (icon_name, score, matched) in enumerate(matches):
        print(f"  {i+1:>2}.  {icon_name:30s}  {score:>4}  {', '.join(matched[:4])}")

    if not matches:
        print("  未找到匹配的图标")


if __name__ == "__main__":
    main()
