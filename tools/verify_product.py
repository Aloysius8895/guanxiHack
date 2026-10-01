from pathlib import Path
import json
from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'verification'
BASE = 'http://127.0.0.1:8002'

def main():
    report = {}
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        for name, width, height in [('desktop',1440,1000),('mobile',390,844)]:
            page = browser.new_page(viewport={'width':width,'height':height}, accept_downloads=True)
            errors = []
            page.on('pageerror', lambda e: errors.append(str(e)))
            page.goto(BASE, wait_until='networkidle')
            page.wait_for_timeout(5500)
            page.screenshot(path=str(OUT/f'product-{name}-home.png'))
            assert 'Mine Smarter.' in page.locator('h1').inner_text()
            assert page.locator('.is-h1-span').first.evaluate('(e)=>parseFloat(getComputedStyle(e).fontSize)') > 24
            page.locator('button.is-menu').click()
            page.wait_for_timeout(1200)
            page.screenshot(path=str(OUT/f'product-{name}-menu.png'))
            link = page.locator('.nav-inner a[href="/our-services"]').first
            if not link.count(): link = page.locator('a[href="/our-services"]').filter(visible=True).first
            link.click()
            page.wait_for_url('**/our-services')
            page.wait_for_timeout(2500)
            assert 'MineFit AI' in page.locator('body').inner_text()
            page.screenshot(path=str(OUT/f'product-{name}-solutions.png'))
            page.goto(BASE+'/rover/', wait_until='networkidle')
            page.wait_for_timeout(1000)
            assert page.locator('canvas').count() == 1
            for button in ['drive','sample','orbit']:
                page.locator('#'+button).click()
            page.locator('#explode').click()
            assert page.locator('#parts').is_visible()
            assert page.locator('#explode').inner_text() == 'Assemble'
            page.screenshot(path=str(OUT/f'product-{name}-rover-exploded.png'))
            page.locator('#explode').click()
            page.locator('#reset').click()
            page.wait_for_timeout(1100)
            page.screenshot(path=str(OUT/f'product-{name}-rover.png'))
            report[name] = {'menu_navigation':True,'rover_controls':True,'page_errors':errors}
            page.close()
        page = browser.new_page(viewport={'width':1440,'height':1000}, accept_downloads=True)
        page.goto(BASE+'/contact',wait_until='networkidle')
        page.wait_for_timeout(4500)
        form = page.locator('[data-metrix-brief]')
        form.locator('[name="name"]').fill('Preview Test')
        form.locator('[name="email"]').fill('preview@example.com')
        form.locator('#Message').fill('Equipment matching pilot verification.')
        with page.expect_download() as info:
            form.evaluate('(form)=>form.requestSubmit()')
        download = info.value
        text = Path(download.path()).read_text('utf-8-sig')
        assert 'Preview Test' in text and 'Equipment matching' in text
        report['brief_download'] = True
        browser.close()
    (OUT/'product-report.json').write_text(json.dumps(report,indent=2),'utf-8')
    print(json.dumps(report,indent=2))

if __name__ == '__main__': main()
