from pathlib import Path
from playwright.sync_api import sync_playwright

root = Path(__file__).resolve().parents[1]
with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    page = browser.new_page(viewport={'width':1100,'height':800})
    page.goto('http://127.0.0.1:8002/rover/',wait_until='networkidle')
    page.wait_for_timeout(1200)
    page.screenshot(path=str(root/'verification/product-rover-final.png'),timeout=15000)
    assert page.locator('canvas').count() == 1
    page.goto('http://127.0.0.1:8002/technology',wait_until='domcontentloaded')
    page.wait_for_timeout(4000)
    page.locator('iframe').evaluate('(e)=>e.loading="eager"')
    page.frame_locator('iframe').locator('canvas').wait_for(timeout=15000)
    print('Final rover and embedded canvas verified.')
    browser.close()
