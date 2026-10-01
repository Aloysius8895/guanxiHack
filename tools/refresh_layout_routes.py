"""Apply the approved page structure changes (safe to run repeatedly)."""
from pathlib import Path
from bs4 import BeautifulSoup

ROOT = Path(__file__).resolve().parents[1] / 'site'
for prefix in ['', 'es/']:
    path = ROOT / prefix / 'index.html'
    soup = BeautifulSoup(path.read_text('utf-8'), 'html.parser')
    for grid in soup.select('.section_technology .machines-grid'):
        content = grid.find_parent(class_='content')
        if content:
            content.decompose()
    path.write_text(str(soup), 'utf-8')

    path = ROOT / prefix / 'technology/index.html'
    soup = BeautifulSoup(path.read_text('utf-8'), 'html.parser')
    for i, card in enumerate(soup.select('.machines-grid_item')):
        if card.select_one('.metrix-component'):
            continue
        name = card.select_one('h3').get_text(strip=True)
        description = card.select_one('.machines-grid_desc').get_text(' ', strip=True)
        img = card.select_one('img').extract()
        img['class'] = ['metrix-component-image']
        card.clear()
        figure = soup.new_tag('figure', attrs={'class': 'metrix-component', 'tabindex': '0', 'aria-labelledby': f'component-title-{i}', 'aria-describedby': f'component-desc-{i}'})
        visual = soup.new_tag('div', attrs={'class': 'metrix-component-visual'})
        visual.append(img)
        desc = soup.new_tag('p', attrs={'class': 'metrix-component-description', 'id': f'component-desc-{i}'})
        desc.string = description
        visual.append(desc)
        figure.append(visual)
        title = soup.new_tag('figcaption', attrs={'id': f'component-title-{i}'})
        title.string = name
        figure.append(title)
        card.append(figure)
    # Use the complete card collection on mobile too, rather than the legacy
    # mobile collection which only contains perception cards.
    for old in soup.select('.machine-grid_mobile'):
        old.decompose()
    path.write_text(str(soup), 'utf-8')

    path = ROOT / prefix / 'our-services/index.html'
    soup = BeautifulSoup(path.read_text('utf-8'), 'html.parser')
    if not soup.select_one('[data-route-search]'):
        scene = BeautifulSoup('''<section class="metrix-route-search" data-route-search bg="black" aria-label="MineFit route planning concept">
          <div class="metrix-route-top"><span>MINEFIT AI / MINE HAUL ROUTE PLANNING</span><span class="metrix-route-live">● SIMULATION</span></div>
          <canvas aria-label="Animated dashed mine site map: compare candidate haul routes and highlight the lowest-cost route"></canvas>
          <div class="metrix-route-bottom"><div><span class="metrix-route-kicker">PIT 02 / HAUL NETWORK</span><h2>Find the best route.<br>Make every move count.</h2><p>Compare haul roads across benches, ramps and unstable ground.<br>Route around the pit along the lowest-cost path.</p></div>
          <div class="metrix-route-readout"><span data-route-status role="status">MAPPING THE NETWORK</span><span data-route-metric>SCANNING CONNECTED WAYPOINTS</span><small>CONCEPT DEMO / ILLUSTRATIVE ROUTE COSTS</small><button type="button" data-route-pause aria-pressed="false">Pause animation Ⅱ</button></div></div>
        </section>''', 'html.parser').section
        soup.select_one('.metrix-mine-story').insert_after(scene)
    path.write_text(str(soup), 'utf-8')
