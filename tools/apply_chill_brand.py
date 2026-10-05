"""Apply the Chill team logo and replace leftover content from the original mirror.

Chill is the team; MetriX AI stays the product name. Safe to re-run.
"""
import re
from pathlib import Path

SITE = Path(__file__).resolve().parents[1] / 'site'
CDN = r'/_assets/cdn\.prod\.website-files\.com/[0-9a-f]+/[0-9a-f]+_'

# Any inline SVG whose only content is the "MetriX AI" text logo.
TEXT_LOGO = re.compile(r'<svg(?P<attrs>[^>]*)>(?:(?!<svg|</svg>).)*?>MetriX AI</text></svg>', re.S)
LOADER_ICON = re.compile(r'<svg class="logo-icon"[^>]*>.*?</svg>', re.S)

def logo_svg(m):
    attrs = re.sub(r'\s(?:clip-path|aria-label|role)="[^"]*"', '', m.group('attrs'))
    attrs = re.sub(r'class="([^"]*)"', r'class="\1 chill-logo"', attrs)
    return f'<svg{attrs} role="img" aria-label="Chill"></svg>'

COMMON = [
    (re.compile(r'href="[^"]*_Favicon32\.svg" rel="shortcut icon" type="image/x-icon"'),
     'href="/_assets/metrix/chill-favicon-32.png" rel="shortcut icon" type="image/png"'),
    (re.compile(r'href="[^"]*_favicon256\.svg" rel="apple-touch-icon"'),
     'href="/_assets/metrix/chill-favicon-180.png" rel="apple-touch-icon"'),
    (re.compile(r'(<a\b[^>]*footer-link[^>]*>)Smart Rover</a>'), r'\1Technology</a>'),
    (re.compile(r'(<a\b[^>]*footer-link[^>]*>)Validation</a>'), r'\1Human Review</a>'),
    (re.compile(r'2026 MetriX AI · Prototype &amp; proof of concept'), '2026 Chill · MetriX AI prototype &amp; proof of concept'),
]

# Home "Who We Serve" cylinder listed the original site's real clients.
AUDIENCES = {
    'Trafigura': 'Fleet Planners', 'Aura Mineral Inc.': 'Mine Geologists', 'Capstone': 'Sampling Teams',
    'Coeur Mining': 'Testing Laboratories', 'Endeavour silver': 'Quality Control Teams', 'Penoles': 'Process Engineers',
    'Fresnillo': 'Tailings Managers', 'First Majestic': 'Recovery Specialists', 'Leagold Mining': 'Metallurgists',
    'Magna Gold': 'Research Institutes', 'Equinox gold': 'Industry Partners',
}

VALUES = [
    ('Honesty', 'Explainable', 'Every recommendation shows its source data, constraints and assumptions, so teams can see why it was made.'),
    ('Respect', 'Evidence', 'Results are compared with an agreed baseline, and the platform expands only when measured outcomes support it.'),
    ('Integrity', 'Human Review', 'Qualified people review important operational, sampling and recovery decisions before they are used.'),
    ('Loyalty', 'Traceable', 'Inputs, samples, model versions and review decisions stay linked, so every result can be checked and repeated.'),
    ('Reliability', 'Pilot First', 'We start with one clearly scoped scenario and commit only to what the evidence shows we can deliver.'),
]
OLD_TITLES = '|'.join(v[0] for v in VALUES)
NEW_VALUE = {old: (new, text) for old, new, text in VALUES}

def about(html):
    html = html.replace('>Values</', '>Principles</').replace('>Our Values<', '>Our Principles<')
    # Title followed by its own description.
    html = re.sub(rf'>({OLD_TITLES})(</span><p class="body-s[^"]*"[^>]*>)[^<]*</p>',
                  lambda m: f'>{NEW_VALUE[m[1]][0]}{m[2]}{NEW_VALUE[m[1]][1]}</p>', html)
    # Descriptions listed separately from their titles, in the same order.
    def desc_list(m):
        texts = iter(v[2] for v in VALUES)
        return re.sub(r'(<p class="body-s">)[^<]*</p>', lambda p: p[1] + next(texts) + '</p>', m[0])
    html = re.sub(r'<div class="scroll-desc">(?:<div class="scroll-item"><p class="body-s">[^<]*</p></div>){5}', desc_list, html)
    html = re.sub(rf'>({OLD_TITLES})</span>', lambda m: f'>{NEW_VALUE[m[1]][0]}</span>', html)
    html = html.replace(
        'We take it further, optimizing resources, minimizing waste, and building a strong environmental culture within our teams. '
        'Our commitment is clear: to protect the environment with the same seriousness with which we protect our people.',
        'Environmental results are reported with their data source, scenario boundary and assumptions, so every claim can be checked.')
    return html.replace('MetriX AI is at the prototype and proof-of-concept stage. We invite',
                        'MetriX AI is developed by Chill and is at the prototype and proof-of-concept stage. We invite')

def swap_image(html, name, src, alt):
    """Point every <img> of an original-site photo at a MetriX concept image."""
    def repl(m):
        tag = re.sub(r'\s(?:srcset|sizes)="[^"]*"', '', m[0])
        tag = re.sub(r'src="[^"]*"', f'src="{src}"', tag)
        return re.sub(r'alt="[^"]*"', f'alt="{alt}"', tag)
    return re.sub(rf'<img\b[^>]*src="{CDN}{re.escape(name)}"[^>]*>', repl, html)

TECH_IMAGES = [
    ('workshops-1.avif', '/_assets/metrix/visuals/research.webp', 'Engineers testing the rover concept on a workbench, concept illustration'),
    ('workshops-2.avif', '/_assets/metrix/components/remote-operation.webp', 'Remote operation of the rover concept'),
    ('safety-sm.avif', '/_assets/metrix/components/platform-link.webp', 'Rover concept linked to the MetriX AI platform'),
    ('safety-hero.avif', '/_assets/metrix/visuals/review.webp', 'Engineers reviewing sample evidence, concept illustration'),
]
BLOG_IMAGES = [
    ('blog-safety-first.avif', '/_assets/metrix/visuals/review.webp', 'QualityGuard AI sampling review, concept illustration'),
    ('blog-open-pit.avif', '/_assets/metrix/visuals/minefit.webp', 'MineFit AI haul route planning, concept illustration'),
    ('blog-ccrm-bootcamp.avif', '/_assets/metrix/visuals/circular.webp', 'CircularMine AI mineral samples, concept illustration'),
]

# The slider script drops duplicate logos (by aria-label) and leaves every tile empty when fewer
# unique logos than its six tiles remain; twelve distinct labels let it rotate, at one text size.
PLATFORM_LOGOS = ['MineFit AI', 'Route Planning', 'QualityGuard AI', 'Sampling Coverage', 'CircularMine AI', 'Recovery Value',
                  'Smart Rover', 'Sample Records', 'MetriX AI', 'Human Review', 'Data Provenance', 'Model Review']

def platform_logos(html):
    def logo(label, hidden):
        cls = 'logos-slider_logo is-b-2' + (' is-2' if hidden else '')
        return (f'<svg aria-label="{label}" class="{cls}" fill="none" role="img" viewbox="0 0 960 130" width="100%" '
                f'xmlns="http://www.w3.org/2000/svg"><text fill="currentColor" font-family="Arial, sans-serif" '
                f'font-size="100" font-weight="600" text-anchor="middle" x="480" y="100">{label}</text></svg>')
    tiles = ''.join(f'<div class="logos-slider_logo-wrap">{logo(a, False)}{logo(b, True)}</div>'
                    for a, b in zip(PLATFORM_LOGOS[::2], PLATFORM_LOGOS[1::2]))
    html = re.sub(r'(<div class="logos-slider_grid" role="list">)(?:<div class="logos-slider_logo-wrap">.*?</div>){6}',
                  lambda m: m[1] + tiles, html, flags=re.S)
    return html.replace('aria-label="Who We Serve" class="logos-slider_inner"', 'aria-label="Platform modules" class="logos-slider_inner"')

for path in sorted(SITE.rglob('index.html')):
    if '_assets' in path.parts:
        continue
    parts = path.parent.relative_to(SITE).parts
    route = '/'.join(parts[1:] if parts[:1] == ('es',) else parts)
    old = html = path.read_text('utf-8')
    html = LOADER_ICON.sub('<svg class="logo-icon chill-mark" fill="none" viewbox="0 0 32 33" width="100%" '
                           'xmlns="http://www.w3.org/2000/svg" role="img" aria-label="Chill"></svg>', html)
    html = TEXT_LOGO.sub(logo_svg, html)
    for pattern, new in COMMON:
        html = pattern.sub(new, html)
    if route == '':
        for name, audience in AUDIENCES.items():
            html = html.replace(f'>{name}<', f'>{audience}<')
    if route == 'about-us':
        html = about(html)
    if route == 'technology':
        html = re.sub(r'(class="button_label-small[^"]*">)Validation<', r'\1Human Review<', html)
        html = html.replace('>Explore validation<', '>Explore human review<')
        html = platform_logos(html)
        for image in TECH_IMAGES:
            html = swap_image(html, *image)
    if route.startswith('blog'):
        for image in BLOG_IMAGES:
            html = swap_image(html, *image)
    if html != old:
        path.write_text(html, 'utf-8')
        print('updated', path.relative_to(SITE))
