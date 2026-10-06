"""Build the Chinese site under site/zh/ from the English pages, and point the
English pages' language switch at their Chinese counterparts.

Translations live in tools/i18n/zh.json (exact English string -> Chinese). Re-run after
editing an English page or the dictionary:

    python tools/build_zh.py

Strings with letters that have no translation are listed at the end so they can be added.
"""
import json
import re
from pathlib import Path

from bs4 import BeautifulSoup, Comment, NavigableString

ROOT = Path(__file__).resolve().parents[1]
SITE = ROOT / 'site'
ZH = json.loads((ROOT / 'tools/i18n/zh.json').read_text(encoding='utf-8'))

ROUTES = ['', 'about-us', 'technology', 'our-services', 'safety', 'notice-of-privacy', 'rover', 'blog',
          'blog/ccrm-bootcamp', 'blog/open-pit-vs-underground-mining',
          'blog/safety-first-how-cominvi-builds-a-culture-of-protection-underground']
# Names, codes and units that read the same in both languages (not reported as missing).
KEEP = re.compile(r'(MetriX AI|MineFit AI|QualityGuard AI|CircularMine AI|Chill|AI|En|html|S\.\d\d|[A-Z]{2}|MX-\d+'
                  r'|[\d.]+ ?(m|cm|km/h|°C)|[\d.°]+C – [\d.°]+C|[\d.]+°N / [\d.]+°W)')
TEXT_ATTRS = ('alt', 'aria-label', 'title', 'placeholder', 'content')
URL_ATTRS = ('href', 'src', 'data-defer-src', 'action')
# Literals inside inline scripts (the rover embed builds part of its UI in JS).
JS_ZH = {
    'Assemble': '组装',
    'Exploded View': '爆炸视图',
    'Chassis · Six wheels · Articulated suspension · Carousel · Sensors · Sampling arm':
        '底盘 · 六个车轮 · 铰接式悬架 · 转盘 · 传感器 · 采样臂',
    'Hardware concept · Engineering and field validation pending.': '硬件概念 · 工程与现场验证待完成。',
    'Six articulated wheel assemblies, a sampling arm and a sensor mast. Drag to rotate. Click the model, then scroll to zoom.':
        '六组铰接式车轮、一条采样臂和一根传感器桅杆。拖动旋转，点击模型后滚动缩放。',
    'Scroll to zoom · Esc to exit': '滚动缩放 · 按 Esc 退出',
    'Click the model to zoom': '点击模型以缩放',
}
HEAD_ASSETS = ('<link href="/_assets/metrix/zh.css" rel="stylesheet"/>'
               '<script src="/_assets/metrix/zh.js"></script>')
# The language switch keeps its orange "current" styling and shows the language being read;
# clicking it opens the same page in the other language (a full load, which main.js already
# exempts from animated navigation for .navlink-locale links).
LOCALE_A = re.compile(r'<a [^>]*class="navlink-locale w-inline-block w--current"[^>]*>'
                      r'<span class="navlink_label">(?:En|CN)</span></a>')


def en_url(route):
    return '/' + route if route else '/'


def zh_url(route):
    return '/zh/' + route


def localise_url(value):
    """Map a link to an English page onto its Chinese copy; assets and other links are unchanged."""
    m = re.fullmatch(r'/([^?#]*?)/?([?#].*)?', value or '')
    if not m or value.startswith('//') or m.group(1) not in ROUTES:
        return value
    return zh_url(m.group(1)) + (m.group(2) or '')


def translate(text, missing):
    core = text.strip()
    if not core or not re.search('[A-Za-z]', core):
        return text
    if core in ZH:
        return text.replace(core, ZH[core], 1)
    if not KEEP.fullmatch(core):
        missing.add(core)
    return text


def build_page(route, missing):
    source = (SITE / route / 'index.html').read_text(encoding='utf-8')
    soup = BeautifulSoup(source, 'html.parser')
    soup.html['lang'] = 'zh-CN'

    for node in list(soup.find_all(string=True)):
        if isinstance(node, Comment):
            continue
        if node.parent.name in ('script', 'style'):
            if node.parent.name == 'script' and node.parent.get('type') == 'module':
                text = str(node)
                for en, zh in JS_ZH.items():
                    text = text.replace(f"'{en}'", f"'{zh}'")
                node.replace_with(NavigableString(text))
            continue
        new = translate(str(node), missing)
        if new != str(node):
            node.replace_with(NavigableString(new))

    for el in soup.find_all(True):
        for attr in TEXT_ATTRS:
            value = el.get(attr)
            if not value:
                continue
            # Only page titles and descriptions among <meta content> values are prose.
            if attr == 'content' and not (el.name == 'meta' and (el.get('name') or el.get('property') or '').endswith(('title', 'description'))):
                continue
            el[attr] = translate(value, missing)
        for attr in URL_ATTRS:
            if el.get(attr):
                el[attr] = localise_url(el[attr])

    toggle = soup.select_one('.locale-switch_toggle .navlink_label div')
    if toggle:
        toggle.string = 'CN'
    html = str(soup)
    html = LOCALE_A.sub(f'<a aria-label="Switch to English" class="navlink-locale w-inline-block w--current" '
                        f'href="{en_url(route)}" hreflang="en"><span class="navlink_label">CN</span></a>', html)
    html = html.replace('</head>', HEAD_ASSETS + '</head>', 1)
    out = SITE / 'zh' / route / 'index.html'
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(html, encoding='utf-8', newline='')


def link_english_page(route):
    path = SITE / route / 'index.html'
    html = path.read_text(encoding='utf-8')
    new = LOCALE_A.sub(f'<a aria-label="切换到中文" class="navlink-locale w-inline-block w--current" '
                       f'href="{zh_url(route)}" hreflang="zh-CN"><span class="navlink_label">En</span></a>', html)
    if new != html:
        path.write_text(new, encoding='utf-8', newline='')


def main():
    missing = set()
    for route in ROUTES:
        build_page(route, missing)
        link_english_page(route)
    print(f'Built {len(ROUTES)} Chinese pages under site/zh/.')
    if missing:
        print('Untranslated strings:')
        for text in sorted(missing):
            print('  ', text)


if __name__ == '__main__':
    main()
