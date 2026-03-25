#!/usr/bin/env python3
"""从 PPTX 模板中提取风格信息

提取每个 PPTX 模板的：
- 颜色主题（背景色、文字色、强调色）
- 字体设置
- 装饰特征描述

输出为 style-system.md 兼容的 JSON 格式。

用法：
    python extract_style.py <pptx_file_or_dir> [-o output.json]
"""

import argparse
import json
import os
import re
import sys
import zipfile
from collections import Counter, defaultdict
from pathlib import Path
from xml.etree import ElementTree as ET

# OOXML 命名空间
NS = {
    'a': 'http://schemas.openxmlformats.org/drawingml/2006/main',
    'r': 'http://schemas.openxmlformats.org/officeDocument/2006/relationships',
    'p': 'http://schemas.openxmlformats.org/presentationml/2006/main',
}


def hex_from_rgb(r, g, b):
    return f"#{r:02X}{g:02X}{b:02X}"


def parse_clr_element(el):
    """解析颜色元素（srgbClr, sysClr 等），返回 #RRGGBB 或 None。"""
    if el is None:
        return None
    for child in el:
        tag = child.tag.split('}')[-1] if '}' in child.tag else child.tag
        if tag == 'srgbClr':
            val = child.get('val', '')
            if len(val) == 6:
                return f"#{val.upper()}"
        elif tag == 'sysClr':
            val = child.get('lastClr', '')
            if len(val) == 6:
                return f"#{val.upper()}"
    return None


def luminance(hex_color):
    """计算颜色的相对亮度 (0-1)。"""
    if not hex_color or len(hex_color) != 7:
        return 0.5
    r = int(hex_color[1:3], 16) / 255
    g = int(hex_color[3:5], 16) / 255
    b = int(hex_color[5:7], 16) / 255
    return 0.2126 * r + 0.7152 * g + 0.0722 * b


def extract_theme_colors(zip_file):
    """从 theme/theme1.xml 提取颜色方案。"""
    theme_path = None
    for name in zip_file.namelist():
        if 'theme/theme1.xml' in name.lower() or 'theme1.xml' in name.lower():
            theme_path = name
            break

    if not theme_path:
        return {}

    tree = ET.parse(zip_file.open(theme_path))
    root = tree.getroot()

    colors = {}
    # 查找 a:clrScheme
    for scheme in root.iter(f'{{{NS["a"]}}}clrScheme'):
        for child in scheme:
            tag = child.tag.split('}')[-1] if '}' in child.tag else child.tag
            color = parse_clr_element(child)
            if color:
                colors[tag] = color

    return colors


def extract_fonts_from_theme(zip_file):
    """从 theme 提取字体方案。"""
    theme_path = None
    for name in zip_file.namelist():
        if 'theme/theme1.xml' in name.lower() or 'theme1.xml' in name.lower():
            theme_path = name
            break

    if not theme_path:
        return {}

    tree = ET.parse(zip_file.open(theme_path))
    root = tree.getroot()

    fonts = {}
    for font_scheme in root.iter(f'{{{NS["a"]}}}fontScheme'):
        for major in font_scheme.iter(f'{{{NS["a"]}}}majorFont'):
            for latin in major.iter(f'{{{NS["a"]}}}latin'):
                fonts['major_latin'] = latin.get('typeface', '')
            for ea in major.iter(f'{{{NS["a"]}}}ea'):
                fonts['major_ea'] = ea.get('typeface', '')
        for minor in font_scheme.iter(f'{{{NS["a"]}}}minorFont'):
            for latin in minor.iter(f'{{{NS["a"]}}}latin'):
                fonts['minor_latin'] = latin.get('typeface', '')
            for ea in minor.iter(f'{{{NS["a"]}}}ea'):
                fonts['minor_ea'] = ea.get('typeface', '')

    return fonts


def extract_slide_colors(zip_file):
    """遍历所有幻灯片，提取背景色和常用颜色。"""
    bg_colors = []
    text_colors = Counter()
    fill_colors = Counter()
    font_names = Counter()

    slide_files = [n for n in zip_file.namelist()
                   if re.match(r'ppt/slides/slide\d+\.xml', n)]

    for slide_file in slide_files:
        tree = ET.parse(zip_file.open(slide_file))
        root = tree.getroot()

        # 背景色
        for bg in root.iter(f'{{{NS["p"]}}}bg'):
            for solid in bg.iter(f'{{{NS["a"]}}}solidFill'):
                color = parse_clr_element(solid)
                if color:
                    bg_colors.append(color)
            for grad_stop in bg.iter(f'{{{NS["a"]}}}gs'):
                color = parse_clr_element(grad_stop)
                if color:
                    bg_colors.append(color)

        # 文字颜色和字体
        for rpr in root.iter(f'{{{NS["a"]}}}rPr'):
            for solid in rpr.iter(f'{{{NS["a"]}}}solidFill'):
                color = parse_clr_element(solid)
                if color:
                    text_colors[color] += 1
            # 字体
            for latin in rpr.iter(f'{{{NS["a"]}}}latin'):
                tf = latin.get('typeface', '')
                if tf and not tf.startswith('+'):
                    font_names[tf] += 1
            for ea in rpr.iter(f'{{{NS["a"]}}}ea'):
                tf = ea.get('typeface', '')
                if tf and not tf.startswith('+'):
                    font_names[tf] += 1

        # 形状填充色
        for sp_pr in root.iter(f'{{{NS["a"]}}}spPr'):
            for solid in sp_pr.findall(f'{{{NS["a"]}}}solidFill'):
                color = parse_clr_element(solid)
                if color:
                    fill_colors[color] += 1

    return {
        'bg_colors': bg_colors,
        'text_colors': text_colors,
        'fill_colors': fill_colors,
        'font_names': font_names,
        'slide_count': len(slide_files),
    }


def classify_colors(theme_colors, slide_data):
    """根据提取的颜色信息，分类为背景/文字/强调色。"""
    result = {
        'background': {},
        'card': {},
        'text': {},
        'accent': {},
    }

    # 背景色
    bg_colors = slide_data.get('bg_colors', [])
    if bg_colors:
        # 去重后取最常见的
        bg_counter = Counter(bg_colors)
        primary_bg = bg_counter.most_common(1)[0][0]
        result['background']['primary'] = primary_bg
        if len(bg_counter) > 1:
            result['background']['gradient_to'] = bg_counter.most_common(2)[1][0]
        else:
            result['background']['gradient_to'] = primary_bg
    elif 'dk1' in theme_colors:
        # 用主题的暗色/亮色
        dk1_lum = luminance(theme_colors.get('dk1', '#000000'))
        lt1_lum = luminance(theme_colors.get('lt1', '#FFFFFF'))
        if dk1_lum < 0.3:
            # 暗色主题
            result['background']['primary'] = theme_colors.get('dk1', '#0B1120')
            result['background']['gradient_to'] = theme_colors.get('dk2', '#0F172A')
        else:
            result['background']['primary'] = theme_colors.get('lt1', '#FFFFFF')
            result['background']['gradient_to'] = theme_colors.get('lt2', '#F8FAFC')

    # 判断是深色还是浅色背景
    bg_primary = result['background'].get('primary', '#FFFFFF')
    is_dark = luminance(bg_primary) < 0.4

    # 文字色
    text_colors = slide_data.get('text_colors', Counter())
    if text_colors:
        sorted_text = text_colors.most_common(10)
        # 主文字色 = 与背景对比度最大的常用颜色
        if is_dark:
            light_texts = [(c, n) for c, n in sorted_text if luminance(c) > 0.6]
            if light_texts:
                result['text']['primary'] = light_texts[0][0]
            else:
                result['text']['primary'] = '#FFFFFF'
            result['text']['secondary'] = 'rgba(255,255,255,0.7)'
        else:
            dark_texts = [(c, n) for c, n in sorted_text if luminance(c) < 0.4]
            if dark_texts:
                result['text']['primary'] = dark_texts[0][0]
            else:
                result['text']['primary'] = '#1E293B'
            result['text']['secondary'] = '#64748B'
    elif theme_colors:
        if is_dark:
            result['text']['primary'] = theme_colors.get('lt1', '#FFFFFF')
            result['text']['secondary'] = 'rgba(255,255,255,0.7)'
        else:
            result['text']['primary'] = theme_colors.get('dk1', '#1E293B')
            result['text']['secondary'] = '#64748B'

    # 强调色 — 从主题颜色中提取
    accent_colors = []
    for key in ['accent1', 'accent2', 'accent3', 'accent4', 'accent5', 'accent6']:
        if key in theme_colors:
            accent_colors.append(theme_colors[key])

    # 也从填充色中发现高频色（排除背景色和文字色）
    fill_colors = slide_data.get('fill_colors', Counter())
    known_colors = set([bg_primary, result['background'].get('gradient_to', ''),
                       result['text'].get('primary', ''),
                       '#FFFFFF', '#000000'])
    for c, n in fill_colors.most_common(20):
        if c not in known_colors and n >= 3:
            mid_lum = 0.15 < luminance(c) < 0.85
            if mid_lum and c not in accent_colors:
                accent_colors.append(c)

    if len(accent_colors) >= 2:
        result['accent']['primary'] = accent_colors[:2]
    elif len(accent_colors) == 1:
        result['accent']['primary'] = [accent_colors[0], accent_colors[0]]
    else:
        result['accent']['primary'] = ['#2563EB', '#1D4ED8']

    if len(accent_colors) >= 4:
        result['accent']['secondary'] = accent_colors[2:4]
    elif len(accent_colors) >= 3:
        result['accent']['secondary'] = [accent_colors[2], accent_colors[2]]
    else:
        result['accent']['secondary'] = result['accent']['primary']

    # 卡片色 — 根据背景色推算
    if is_dark:
        # 深色系：卡片比背景略亮
        r, g, b = int(bg_primary[1:3], 16), int(bg_primary[3:5], 16), int(bg_primary[5:7], 16)
        card_from = hex_from_rgb(min(255, r + 20), min(255, g + 20), min(255, b + 20))
        result['card'] = {
            'gradient_from': card_from,
            'gradient_to': bg_primary,
            'border': 'rgba(255,255,255,0.05)',
            'border_radius': 12,
        }
    else:
        # 浅色系：卡片用白色或比背景略深
        result['card'] = {
            'gradient_from': '#FFFFFF',
            'gradient_to': bg_primary,
            'border': f'rgba({int(accent_colors[0][1:3], 16) if accent_colors else 37},'
                      f'{int(accent_colors[0][3:5], 16) if accent_colors else 99},'
                      f'{int(accent_colors[0][5:7], 16) if accent_colors else 235},0.12)',
            'border_radius': 12,
        }

    return result


def extract_style(pptx_path):
    """从单个 PPTX 文件提取完整风格信息。"""
    pptx_path = Path(pptx_path)
    if not pptx_path.exists():
        print(f"文件不存在: {pptx_path}", file=sys.stderr)
        return None

    try:
        with zipfile.ZipFile(str(pptx_path), 'r') as zf:
            theme_colors = extract_theme_colors(zf)
            theme_fonts = extract_fonts_from_theme(zf)
            slide_data = extract_slide_colors(zf)
    except (zipfile.BadZipFile, Exception) as e:
        print(f"无法解析: {pptx_path} ({e})", file=sys.stderr)
        return None

    colors = classify_colors(theme_colors, slide_data)

    # 字体
    font_names = slide_data.get('font_names', Counter())
    if font_names:
        top_fonts = [f for f, _ in font_names.most_common(3)]
        font_family = ', '.join(f"'{f}'" for f in top_fonts) + ', system-ui, sans-serif'
    elif theme_fonts:
        parts = []
        if theme_fonts.get('major_ea'):
            parts.append(f"'{theme_fonts['major_ea']}'")
        if theme_fonts.get('major_latin'):
            parts.append(f"'{theme_fonts['major_latin']}'")
        if theme_fonts.get('minor_ea') and theme_fonts['minor_ea'] != theme_fonts.get('major_ea'):
            parts.append(f"'{theme_fonts['minor_ea']}'")
        font_family = ', '.join(parts) + ', system-ui, sans-serif' if parts else "system-ui, sans-serif"
    else:
        font_family = "PingFang SC, Microsoft YaHei, system-ui, sans-serif"

    # 判断装饰风格
    is_dark = luminance(colors['background'].get('primary', '#FFF')) < 0.4

    # 构建风格 JSON
    style = {
        'style_name': pptx_path.stem,
        'style_id': re.sub(r'[^a-z0-9]+', '_', pptx_path.stem.lower()).strip('_'),
        'background': colors['background'],
        'card': colors['card'],
        'text': {
            **colors['text'],
            'title_size': 28,
            'body_size': 14,
            'card_title_size': 20,
        },
        'accent': colors['accent'],
        'font_family': font_family,
        'grid_pattern': {'enabled': is_dark, 'size': 40, 'dot_radius': 1,
                         'dot_color': colors['text'].get('primary', '#FFF'),
                         'dot_opacity': 0.03 if is_dark else 0},
        'decorations': {
            'corner_lines': is_dark,
            'glow_effects': is_dark,
            'description': '',
        },
        '_meta': {
            'source_file': pptx_path.name,
            'slide_count': slide_data['slide_count'],
            'theme_colors': theme_colors,
            'theme_fonts': theme_fonts,
            'top_text_colors': dict(slide_data['text_colors'].most_common(5)),
            'top_fill_colors': dict(slide_data['fill_colors'].most_common(5)),
            'top_fonts': dict(slide_data['font_names'].most_common(5)),
        },
    }

    # 生成 CSS 变量
    accent_primary = colors['accent'].get('primary', ['#2563EB', '#1D4ED8'])
    accent_secondary = colors['accent'].get('secondary', ['#059669', '#047857'])
    style['_css_vars'] = f""":root {{
  --bg-primary: {colors['background'].get('primary', '#FFFFFF')};
  --bg-secondary: {colors['background'].get('gradient_to', '#F8FAFC')};
  --card-bg-from: {colors['card'].get('gradient_from', '#F1F5F9')};
  --card-bg-to: {colors['card'].get('gradient_to', '#E2E8F0')};
  --card-border: {colors['card'].get('border', 'rgba(0,0,0,0.08)')};
  --card-radius: {colors['card'].get('border_radius', 12)}px;
  --text-primary: {colors['text'].get('primary', '#1E293B')};
  --text-secondary: {colors['text'].get('secondary', '#64748B')};
  --accent-1: {accent_primary[0] if accent_primary else '#2563EB'};
  --accent-2: {accent_primary[1] if len(accent_primary) > 1 else '#1D4ED8'};
  --accent-3: {accent_secondary[0] if accent_secondary else '#059669'};
  --accent-4: {accent_secondary[1] if len(accent_secondary) > 1 else '#047857'};
}}"""

    return style


def main():
    parser = argparse.ArgumentParser(description="从 PPTX 模板提取风格信息")
    parser.add_argument('input', help='PPTX 文件或包含 PPTX 的目录')
    parser.add_argument('-o', '--output', default=None, help='输出 JSON 文件路径')
    parser.add_argument('--pretty', action='store_true', help='格式化 JSON 输出')
    args = parser.parse_args()

    input_path = Path(args.input)
    if input_path.is_file():
        pptx_files = [input_path]
    elif input_path.is_dir():
        pptx_files = sorted(input_path.glob('*.pptx'))
    else:
        print(f"路径不存在: {input_path}", file=sys.stderr)
        sys.exit(1)

    if not pptx_files:
        print("未找到 PPTX 文件", file=sys.stderr)
        sys.exit(1)

    results = []
    for pptx_file in pptx_files:
        print(f"提取: {pptx_file.name} ...", file=sys.stderr)
        style = extract_style(pptx_file)
        if style:
            results.append(style)
            print(f"  背景: {style['background']}", file=sys.stderr)
            print(f"  强调: {style['accent']}", file=sys.stderr)
            print(f"  字体: {style['font_family']}", file=sys.stderr)

    indent = 2 if args.pretty else None
    output = json.dumps(results, ensure_ascii=False, indent=indent)

    if args.output:
        Path(args.output).write_text(output, encoding='utf-8')
        print(f"\n已保存到: {args.output}", file=sys.stderr)
    else:
        print(output)


if __name__ == '__main__':
    main()
