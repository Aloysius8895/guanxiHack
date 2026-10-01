"""Apply supplied rover media and scoped title layout without rebuilding other content."""
from pathlib import Path
from bs4 import BeautifulSoup

ASSET = '/_assets/metrix/'
LABELS = [
    'Six-Wheel Chassis', 'Emergency Stop', 'Sampling Arm', 'Sample Carousel',
    'Vision Sensors', 'Sensor Mast', 'Sample Handling', 'Task Planning',
    'Sample Records', 'Platform Link', 'Remote Operation', 'Image Capture',
    'Coverage Review', 'Scanning Concept',
]


def update_media(soup):
    for card in soup.select('.machines-grid_button, .machine-card'):
        heading = card.select_one('h3, .machines_label .body-m')
        if not heading or heading.get_text(strip=True) not in LABELS:
            continue
        label = heading.get_text(strip=True)
        for image in card.select('img'):
            image['src'] = ASSET + 'components/' + label.lower().replace(' ', '-') + '.png'
            image['alt'] = 'MetriX AI — ' + label
            image['data-metrix-image'] = 'component' if LABELS.index(label) < 6 else 'scenario'
            for attr in ('srcset', 'sizes'):
                image.attrs.pop(attr, None)
    for title in soup.select('.display-text'):
        if any(node.get_text(strip=True) == 'Smart sampling rover' for node in title.select('.body-xxl')):
            title['class'] = list(dict.fromkeys(title.get('class', []) + ['metrix-rover-title']))
    if not soup.select_one('link[href="' + ASSET + 'product.css"]'):
        soup.head.append(soup.new_tag('link', rel='stylesheet', href=ASSET + 'product.css'))


if __name__ == '__main__':
    site = Path(__file__).resolve().parents[1] / 'site'
    for path in site.rglob('*.html'):
        if '_assets' in path.parts:
            continue
        soup = BeautifulSoup(path.read_text('utf-8'), 'html.parser')
        if not soup.select_one('.machines-grid_button, .display-text'):
            continue
        update_media(soup)
        path.write_text(str(soup), 'utf-8')
        print(path.relative_to(site))
