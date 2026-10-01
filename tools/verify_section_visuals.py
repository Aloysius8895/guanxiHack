"""Browser smoke check and screenshots for the imagery/navigation refresh."""
import json
from pathlib import Path
from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'verification'
report = {}
with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    for device, width, height in [('desktop', 1440, 1000), ('mobile', 390, 844)]:
        page = browser.new_page(viewport={'width': width, 'height': height})
        for route, selector in [('/', '.section_services'), ('/our-services', '.metrix-solutions-grid'), ('/safety', '.section_ccrm'), ('/about-us', '.section_about-us')]:
            errors = []
            def on_error(error): errors.append(str(error))
            page.on('pageerror', on_error)
            response = page.goto('http://127.0.0.1:8002' + route, wait_until='domcontentloaded')
            page.wait_for_timeout(4500)
            name = route.strip('/') or 'home'
            if name in ('safety', 'about-us'):
                page.screenshot(path=str(OUT / f'imagery-{device}-{name}-hero.png'))
            page.locator(selector).first.scroll_into_view_if_needed()
            page.wait_for_timeout(1800)
            page.screenshot(path=str(OUT / f'imagery-{device}-{name}.png'))
            images = page.locator('main img[src*="/_assets/metrix/"]').evaluate_all('els => els.map(e => ({src:e.getAttribute("src"),loaded:e.complete && e.naturalWidth>0}))')
            # Fetch all lazy images explicitly to verify references even below the fold.
            bad_images = page.evaluate('''async sources => {
              const checks=await Promise.all(sources.map(async s=>({src:s,ok:(await fetch(s)).ok})));
              return checks.filter(x=>!x.ok);
            }''', list({i['src'] for i in images}))
            sections = page.locator('main > div[class*="section_"]').evaluate_all('els => els.map(e=>({section:e.className,entries:e.querySelectorAll("a").length}))')
            result = {'status': response.status, 'errors': errors, 'missing_images': bad_images, 'horizontal_overflow': page.evaluate('document.documentElement.scrollWidth>innerWidth'), 'sections': sections}
            if name in ('home', 'our-services'):
                result['cards'] = page.locator('.section_services .metrix-solution-card').count()
                result['card_buttons'] = page.locator('.section_services .metrix-solutions-grid button').count()
                assert result['cards'] == 5
                assert result['card_buttons'] == 0
            if name == 'home':
                assert page.locator('.section_technology a.button').get_attribute('href') == '/technology'
                assert page.locator('.section_services a').count() == 1
                assert page.locator('.section_services a').get_attribute('href') == '/our-services'
            if name == 'our-services':
                assert page.locator('.section_next').count() == 0
                assert page.locator('.metrix-mine-story').count() == 1
                page.locator('.metrix-section-entry').click()
                page.wait_for_url('**/contact', timeout=15000)
                result['pilot_navigation'] = True
            report[device + '-' + name] = result
            assert not bad_images and not result['horizontal_overflow'] and not errors, result
            assert all(s['entries'] <= 1 for s in sections), sections
            page.remove_listener('pageerror', on_error)
        page.close()
    browser.close()
(OUT / 'imagery-navigation-report.json').write_text(json.dumps(report, indent=2), 'utf-8')
print(json.dumps(report, indent=2))
