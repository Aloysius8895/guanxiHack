"""Refresh MetriX imagery in place, preserving the existing page animation shell."""
from pathlib import Path
from bs4 import BeautifulSoup

ROOT = Path(__file__).resolve().parents[1]
ASSET = '/_assets/metrix/'
MEDIA = {
    'MineFit AI': ('visuals/minefit.webp', 'Concept illustration of haul trucks and route planning'),
    'QualityGuard AI': ('components/sample-records.webp', 'MetriX sample collection and traceability concept'),
    'CircularMine AI': ('visuals/circular.webp', 'Mineral samples for secondary resource recovery assessment'),
    'Smart Sampling Rover': ('components/sampling-arm.webp', 'MetriX articulated sampling arm concept'),
    'Enterprise Integration': ('components/platform-link.webp', 'MetriX connected rover and decision platform concept'),
    'Human Review': ('visuals/review.webp', 'Illustration of engineers reviewing sample evidence'),
    'Field Sampling': ('components/sample-handling.webp', 'MetriX field sampling concept'),
}


def set_image(img, path, alt):
    img['src'] = ASSET + path
    img['alt'] = alt
    for attr in ('srcset', 'sizes'):
        img.attrs.pop(attr, None)


def set_headline(soup, hero, lines):
    if not hero:
        return
    hero.clear()
    for text in lines:
        wrapper = soup.new_tag('div', attrs={'class': 'is-h1-span-wrap'})
        span = soup.new_tag('span', attrs={'class': 'is-h1-span'})
        span.string = text
        wrapper.append(span)
        hero.append(wrapper)


def refresh(path):
    soup = BeautifulSoup(path.read_text('utf-8'), 'html.parser')
    rel = path.relative_to(ROOT / 'site').as_posix()
    page = rel.removeprefix('es/')
    lang = '/es' if rel.startswith('es/') else ''
    main = soup.select_one('main')
    if not main:
        return
    # One set of entry points in the content, without duplicate hero preview links.
    for previews in main.select('.hero-bottom_cards'):
        previews.decompose()
    for grid in main.select('.is-grid-3'):
        cards = grid.select('.service-card, .team-card')
        if not cards:
            continue
        grid['class'] = ['metrix-solutions-grid']
        for card in cards:
            heading = card.select_one('h3')
            if not heading or heading.get_text(strip=True) not in MEDIA:
                continue
            name = heading.get_text(strip=True)
            card.name = 'article'
            card.attrs = {'class': ['metrix-solution-card']}
            for icon in card.select('.service-icon'):
                icon.decompose()
            img = soup.new_tag('img', loading='lazy', decoding='async')
            set_image(img, *MEDIA[name])
            img['class'] = ['metrix-solution-image']
            card.insert(0, img)
            inner = card.select_one('.card-inner')
            if inner:
                inner['class'] = ['metrix-solution-copy']
            desc = card.select_one('.desc')
            if desc:
                desc['class'] = ['metrix-solution-description']
        for viewer in grid.select('.services-viewer'):
            viewer.decompose()
    # Fix the actual homepage destination and remove the repeat Services Rover promo.
    if page == 'index.html':
        for selector, destination, label in [('.section_services', '/our-services', 'EXPLORE AI SOLUTIONS'), ('.section_teams', '/join-the-team', 'EXPLORE PILOT OPPORTUNITIES')]:
            section = main.select_one(selector)
            if section and not section.select_one('a'):
                a = soup.new_tag('a', href=lang + destination, attrs={'class': 'metrix-section-entry'})
                a.string = label + '  →'
                section.append(a)
        for a in main.select('.section_technology a.button'):
            a['href'] = lang + '/technology'
        for preload in main.select('.section_technology link[rel="prefetch"]'):
            preload['href'] = lang + '/technology'
        for sec in main.select('.section_next'):
            sec.decompose()
        for img in main.select('.section_about .image-wrapper img'):
            set_image(img, 'visuals/research.webp', 'MetriX robotics research concept illustration')
        for img in main.select('.section_safety .image-wrapper img'):
            set_image(img, 'visuals/review.webp', 'Engineers reviewing sampling evidence, concept illustration')
    if page == 'our-services/index.html':
        for sec in main.select('.section_next, .metrix-rover-title'):
            sec.decompose()
        for p in list(main.select('p')):
            if 'Explore the six-wheel rover' in p.get_text():
                p.parent.decompose()
        hero = main.select_one('h1')
        set_headline(soup, hero, ['Intelligence for', 'every mining decision.'])
        for img in main.select('.background_image'):
            set_image(img, 'visuals/minefit.webp', 'Mine planning and equipment routing concept illustration')
        section = main.select_one('.section_services')
        if section and not section.select_one('a'):
            a = soup.new_tag('a', href=lang + '/contact', attrs={'class': 'metrix-section-entry'})
            a.string = 'DISCUSS A PILOT  →'
            section.append(a)
    if page == 'safety/index.html':
        hero = main.select_one('h1')
        set_headline(soup, hero, ['Evidence first.', 'People in control.'])
        mapping = {
            '.background_image': ('visuals/review.webp', 'Human review at a sample laboratory, concept illustration'),
            '.section_ccrm img': MEDIA['QualityGuard AI'],
            '.section_commitment img': ('components/remote-operation.webp', 'Human oversight of the MetriX rover concept'),
            '.section_img img': ('visuals/review.webp', 'Engineers comparing samples and evidence, concept illustration'),
            '.section_improvement img': ('components/coverage-review.webp', 'Sampling coverage review concept'),
            '.section_next img': ('visuals/research.webp', 'Robotics research workshop concept illustration'),
        }
        for selector, media in mapping.items():
            for img in main.select(selector):
                set_image(img, *media)
    if page == 'about-us/index.html':
        mapping = {
            '.background_image': ('visuals/research.webp', 'MetriX robotics research concept illustration'),
            '.section_about-us .image-wrapper img': ('components/task-planning.webp', 'Connected mining task planning concept'),
            '.section_improvement img': MEDIA['CircularMine AI'],
            '.section_next img': ('visuals/review.webp', 'Industry collaboration concept illustration'),
        }
        for selector, media in mapping.items():
            for img in main.select(selector):
                set_image(img, *media)
        for selector in ('.workshops_img-view img', '.workshops_img-view_sm img'):
            for img, media in zip(main.select(selector), [MEDIA['Enterprise Integration'], ('visuals/research.webp', 'Collaborative robotics research concept'), MEDIA['Human Review']]):
                set_image(img, *media)
        for i, wrapper in enumerate(main.select('.story_video')):
            wrapper.clear()
            wrapper.attrs = {'class': ['story_video', 'metrix-story-still']}
            img = soup.new_tag('img', loading='lazy')
            set_image(img, *[MEDIA['MineFit AI'], MEDIA['QualityGuard AI'], MEDIA['Human Review'], MEDIA['Enterprise Integration']][i % 4])
            wrapper.append(img)
    if page in ('safety/index.html', 'about-us/index.html'):
        main['class'] = list(dict.fromkeys(list(main.get('class', [])) + ['metrix-editorial']))
    # Shared stylesheet is loaded on every entry route for client-side transitions.
    if not soup.select_one('link[href="' + ASSET + 'sections.css"]'):
        soup.head.append(soup.new_tag('link', rel='stylesheet', href=ASSET + 'sections.css'))
    path.write_text(str(soup), 'utf-8')


if __name__ == '__main__':
    for path in (ROOT / 'site').rglob('*.html'):
        if '_assets' not in path.parts and 'rover' not in path.parts:
            refresh(path)
