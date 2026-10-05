"""Add the rover scene imagery to Technology and AI Solutions (safe to run repeatedly).

On Technology the gallery replaces the Platform Modules section, which duplicated the
module cards on Home and AI Solutions.

Source screenshots were cropped to remove their mock navigation bar and saved as
WebP under site/_assets/metrix/scenes/.
"""
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1] / 'site'
SCENES = '/_assets/metrix/scenes/'

# (file, label, alt, width, height) - each row keeps equal heights via flex-grow = aspect ratio.
GALLERY_ROWS = [
    [
        ('autonomous-sampling', '01 / Exploration', 'MetriX rover scanning a sulfide zone on a tunnel wall with visual and thermal sensors', 677, 282),
        ('ore-detection', '02 / Ore detection', 'Thermal sensor view marking a high-grade zone, possible ore and an unsure area on the rock face', 683, 278),
    ],
    [
        ('realtime-monitoring', '03 / Real-time monitoring', 'Rover in a tunnel labelling rock wall, overhang, rock and a clear path in real time', 445, 278),
        ('sample-collection', '04 / Sample collection', 'Robotic arm gripping a rock sample at a marked point on the tunnel wall', 433, 286),
        ('cave-mapping', '05 / 3D mapping', 'Rover building a LiDAR point-cloud map of a tunnel with rock face, ore seam and sample point markers', 510, 281),
    ],
]


def figure(name, label, alt, width, height):
    return (
        f'<figure class="metrix-scene" style="flex-grow:{width / height:.3f}">'
        f'<img alt="{alt}" class="metrix-scene-image" height="{height}" loading="lazy" src="{SCENES}{name}.webp" width="{width}"/>'
        f'<figcaption class="eyebrow-s">{label}</figcaption></figure>'
    )


GALLERY = (
    '<div bg="black" class="section_scenes" data-metrix-scenes=""><div class="intro"><div class="eyebrows is-white">'
    '<div class="is-eyebrow"><span class="eyebrow-s">S.02</span></div>'
    '<div class="is-eyebrow"><h2 class="eyebrow-s">Rover in Action</h2></div></div>'
    '<p class="body-xl" tr="1">In the tunnel, the rover concept scans the rock face, flags likely ore, '
    'collects representative samples and maps the route it travelled.</p></div>'
    '<div class="metrix-scenes">'
    + ''.join('<div class="metrix-scenes-row">' + ''.join(figure(*item) for item in row) + '</div>' for row in GALLERY_ROWS)
    + '</div><p class="metrix-scenes-note">Concept visualisations. Detection, sampling and mapping remain subject to field validation.</p></div>'
)

FLEET = (
    '<section aria-label="Underground fleet route coordination concept" bg="black" class="metrix-fleet-scene" data-metrix-fleet="">'
    '<img alt="Several MetriX rovers linked across an underground tunnel network, with one optimal route to the target ore zone highlighted '
    'and a blocked route and rough terrain marked" class="metrix-fleet-image" height="879" loading="lazy" '
    f'src="{SCENES}fleet-route-sync.webp" width="1672"/>'
    '<div class="metrix-route-top"><span>MINEFIT AI / UNDERGROUND FLEET SYNC</span><span class="metrix-route-live">● CONCEPT VISUAL</span></div>'
    '</section>'
)


def remove_div(html, marker):
    """Remove the <div> that starts at `marker`, including all nested divs."""
    start = html.find(marker)
    if start < 0:
        return html
    depth, i = 0, start
    while True:
        open_at, close_at = html.find('<div', i), html.find('</div>', i)
        if open_at != -1 and open_at < close_at:
            depth, i = depth + 1, open_at + 4
        else:
            depth, i = depth - 1, close_at + 6
            if depth == 0:
                return html[:start] + html[i:]


def insert_before(html, marker, block, guard):
    if guard in html:
        return html
    i = html.index(marker)
    return html[:i] + block + html[i:]


for prefix in ['', 'es/']:
    path = ROOT / prefix / 'technology/index.html'
    html = path.read_bytes().decode('utf-8')
    # Platform Modules repeated the AI Solutions module cards; the rover gallery takes its S.02 slot.
    html = remove_div(html, '<div bg="black" class="section_brands"')
    html = html.replace('<span class="eyebrow-s">S.04</span>', '<span class="eyebrow-s">S.03</span>')
    html = insert_before(html, '<div bg="black" class="section_workshops"', GALLERY, 'data-metrix-scenes')
    path.write_bytes(html.encode('utf-8'))

    path = ROOT / prefix / 'our-services/index.html'
    html = path.read_bytes().decode('utf-8')
    html = insert_before(html, '<div bg="white" class="section_process"', FLEET, 'data-metrix-fleet')
    path.write_bytes(html.encode('utf-8'))
