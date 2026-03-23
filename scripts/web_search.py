#!/usr/bin/env python3
"""
网页搜索脚本 — 零额外依赖（仅 urllib + json）

支持 Brave Search 和 Tavily 双引擎，自动降级。

用法：
    # 单次搜索
    python web_search.py --query "AI PPT generation"

    # 批量搜索（自动串行 + 速率控制）
    python web_search.py --batch queries.json --output-dir path/to/results/

    queries.json 格式：
    [
      {"id": "q1", "query": "AI PPT generation trends 2026"},
      {"id": "q2", "query": "python-pptx best practices"}
    ]

    # 指定引擎
    python web_search.py --query "..." --engine brave
    python web_search.py --query "..." --engine tavily

    # 内容提取（仅 Tavily）
    python web_search.py --extract "https://example.com/article"

可选参数：
    --engine        搜索引擎（brave/tavily/auto，默认 auto）
    --count N       返回结果数（默认 5）
    --interval S    批量请求间隔秒数（默认 2）

环境变量（从 .env 读取）：
    BRAVE_API_KEY   — Brave Search API Key
    TAVILY_API_KEY  — Tavily API Key
    （至少配置一个，两个都有时 auto 模式优先用 Brave）
"""

import argparse
import json
import os
import sys
import time
import urllib.request
import urllib.error


def load_dotenv(path=None):
    """从 .env 文件加载环境变量。"""
    candidates = []
    if path:
        candidates.append(path)
    script_dir = os.path.dirname(os.path.abspath(__file__))
    candidates.append(os.path.join(script_dir, '.env'))
    candidates.append(os.path.join(os.path.dirname(script_dir), '.env'))

    for p in candidates:
        if os.path.isfile(p):
            with open(p, encoding='utf-8') as f:
                for line in f:
                    line = line.strip()
                    if not line or line.startswith('#') or '=' not in line:
                        continue
                    k, v = line.split('=', 1)
                    k, v = k.strip(), v.strip().strip('"').strip("'")
                    if k and k not in os.environ:
                        os.environ[k] = v
            break


# -------------------------------------------------------------------
# Brave Search
# -------------------------------------------------------------------
def _brave_search(query, api_key, count=5, timeout=30):
    """Brave Web Search API。返回结构化结果列表。"""
    url = 'https://api.search.brave.com/res/v1/web/search'
    params = urllib.parse.urlencode({'q': query, 'count': count})
    full_url = f'{url}?{params}'

    req = urllib.request.Request(full_url, headers={
        'Accept': 'application/json',
        'Accept-Encoding': 'gzip',
        'X-Subscription-Token': api_key,
    })

    resp = urllib.request.urlopen(req, timeout=timeout)
    data = resp.read()
    # handle gzip
    if resp.headers.get('Content-Encoding') == 'gzip':
        import gzip
        data = gzip.decompress(data)

    result = json.loads(data.decode('utf-8'))
    web_results = result.get('web', {}).get('results', [])

    return [{
        'title': r.get('title', ''),
        'url': r.get('url', ''),
        'snippet': r.get('description', ''),
        'source': 'brave',
    } for r in web_results[:count]]


# -------------------------------------------------------------------
# Tavily Search
# -------------------------------------------------------------------
def _tavily_search(query, api_key, count=5, timeout=30):
    """Tavily Search API。返回结构化结果列表。"""
    url = 'https://api.tavily.com/search'
    payload = json.dumps({
        'api_key': api_key,
        'query': query,
        'max_results': count,
        'include_answer': True,
    }).encode('utf-8')

    req = urllib.request.Request(url, data=payload, headers={
        'Content-Type': 'application/json',
    })

    resp = urllib.request.urlopen(req, timeout=timeout)
    result = json.loads(resp.read().decode('utf-8'))

    items = []
    # Tavily 的 AI 摘要
    answer = result.get('answer', '')
    if answer:
        items.append({
            'title': '[Tavily AI Summary]',
            'url': '',
            'snippet': answer,
            'source': 'tavily',
        })

    for r in result.get('results', [])[:count]:
        items.append({
            'title': r.get('title', ''),
            'url': r.get('url', ''),
            'snippet': r.get('content', ''),
            'source': 'tavily',
        })
    return items


def _tavily_extract(urls, api_key, timeout=30):
    """Tavily Extract API — 提取网页正文内容。"""
    url = 'https://api.tavily.com/extract'
    if isinstance(urls, str):
        urls = [urls]
    payload = json.dumps({
        'api_key': api_key,
        'urls': urls,
    }).encode('utf-8')

    req = urllib.request.Request(url, data=payload, headers={
        'Content-Type': 'application/json',
    })

    resp = urllib.request.urlopen(req, timeout=timeout)
    result = json.loads(resp.read().decode('utf-8'))

    return [{
        'url': r.get('url', ''),
        'content': r.get('raw_content', r.get('content', '')),
        'source': 'tavily_extract',
    } for r in result.get('results', [])]


# -------------------------------------------------------------------
# 统一搜索接口
# -------------------------------------------------------------------
def search(query, engine='auto', count=5, timeout=30):
    """
    统一搜索入口。

    engine: 'brave' / 'tavily' / 'auto'
    auto 模式：优先 Brave（免费额度高），失败降级 Tavily。
    返回: list[dict] with keys: title, url, snippet, source
    """
    brave_key = os.environ.get('BRAVE_API_KEY', '')
    tavily_key = os.environ.get('TAVILY_API_KEY', '')

    if engine == 'brave':
        if not brave_key:
            print('Error: BRAVE_API_KEY not configured', file=sys.stderr)
            return []
        return _brave_search(query, brave_key, count, timeout)

    if engine == 'tavily':
        if not tavily_key:
            print('Error: TAVILY_API_KEY not configured', file=sys.stderr)
            return []
        return _tavily_search(query, tavily_key, count, timeout)

    # auto 模式
    errors = []
    if brave_key:
        try:
            return _brave_search(query, brave_key, count, timeout)
        except Exception as e:
            errors.append(f'Brave failed: {e}')
            print(f'Brave search failed, falling back to Tavily: {e}', file=sys.stderr)

    if tavily_key:
        try:
            return _tavily_search(query, tavily_key, count, timeout)
        except Exception as e:
            errors.append(f'Tavily failed: {e}')

    if not brave_key and not tavily_key:
        print('Error: No search API key configured. Set BRAVE_API_KEY or TAVILY_API_KEY in .env',
              file=sys.stderr)
    else:
        print(f'All search engines failed: {"; ".join(errors)}', file=sys.stderr)
    return []


def extract(urls, timeout=30):
    """内容提取（Tavily Extract）。"""
    tavily_key = os.environ.get('TAVILY_API_KEY', '')
    if not tavily_key:
        print('Error: TAVILY_API_KEY required for extract', file=sys.stderr)
        return []
    return _tavily_extract(urls, tavily_key, timeout)


# -------------------------------------------------------------------
# 批量搜索
# -------------------------------------------------------------------
def batch_search(batch_file, output_dir, engine='auto', count=5, interval=2.0):
    """批量搜索，结果按 id 保存为 JSON 文件。"""
    with open(batch_file, encoding='utf-8') as f:
        queries = json.load(f)

    os.makedirs(output_dir, exist_ok=True)
    results = {'ok': [], 'failed': []}

    for i, item in enumerate(queries):
        qid = item.get('id', f'q{i+1}')
        query = item.get('query', '')
        if not query:
            continue

        if i > 0:
            time.sleep(interval)

        print(f'[{i+1}/{len(queries)}] Searching: {query[:60]}...', file=sys.stderr)
        try:
            res = search(query, engine=engine, count=count)
            out_path = os.path.join(output_dir, f'{qid}.json')
            with open(out_path, 'w', encoding='utf-8') as f:
                json.dump({'query': query, 'results': res}, f, ensure_ascii=False, indent=2)
            results['ok'].append(qid)
        except Exception as e:
            print(f'  Failed: {e}', file=sys.stderr)
            results['failed'].append(qid)

    return results


# -------------------------------------------------------------------
# CLI
# -------------------------------------------------------------------
def main():
    load_dotenv()

    parser = argparse.ArgumentParser(description='Web search (Brave + Tavily)')
    parser.add_argument('--query', '-q', help='Search query')
    parser.add_argument('--batch', help='Batch queries JSON file')
    parser.add_argument('--output-dir', help='Output directory for batch results')
    parser.add_argument('--extract', help='URL(s) to extract content from (comma-separated)')
    parser.add_argument('--engine', default='auto', choices=['brave', 'tavily', 'auto'],
                        help='Search engine (default: auto)')
    parser.add_argument('--count', type=int, default=5, help='Number of results (default: 5)')
    parser.add_argument('--interval', type=float, default=2.0,
                        help='Batch request interval in seconds (default: 2)')
    args = parser.parse_args()

    if args.extract:
        urls = [u.strip() for u in args.extract.split(',')]
        results = extract(urls)
        print(json.dumps(results, ensure_ascii=False, indent=2))
        return

    if args.batch:
        out_dir = args.output_dir or 'search_results'
        results = batch_search(args.batch, out_dir,
                               engine=args.engine, count=args.count, interval=args.interval)
        print(json.dumps(results, ensure_ascii=False, indent=2))
        return

    if args.query:
        results = search(args.query, engine=args.engine, count=args.count)
        print(json.dumps(results, ensure_ascii=False, indent=2))
        return

    parser.print_help()
    sys.exit(1)


if __name__ == '__main__':
    main()
