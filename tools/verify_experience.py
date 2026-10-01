from playwright.sync_api import sync_playwright
from pathlib import Path
import json
out=Path('verification');report={}
with sync_playwright() as p:
 b=p.chromium.launch(headless=True)
 for name,w,h in [('desktop',1440,1000),('mobile',390,844)]:
  page=b.new_page(viewport={'width':w,'height':h});errors=[]
  page.on('pageerror',lambda e: errors.append(str(e)))
  page.goto('http://127.0.0.1:8002/technology');page.wait_for_timeout(6500)
  cards=page.locator('.metrix-component');cards.first.scroll_into_view_if_needed();page.wait_for_timeout(800)
  if name=='desktop':cards.first.hover();page.wait_for_timeout(650)
  page.screenshot(path=str(out/f'ux-{name}-cards.png'))
  report[name]={'cards':cards.count(),'visible':cards.first.is_visible(),'descriptionOpacity':cards.first.locator('p').evaluate('(e)=>getComputedStyle(e).opacity'),'overflow':page.evaluate('document.documentElement.scrollWidth>innerWidth'),'errors':errors}
  page.goto('http://127.0.0.1:8002/our-services');page.wait_for_timeout(6000)
  page.locator('.metrix-route-search').scroll_into_view_if_needed();page.wait_for_timeout(9000)
  page.screenshot(path=str(out/f'ux-{name}-routes.png'))
  report[name]['routePhase']=page.locator('[data-route-search]').get_attribute('data-route-phase')
  report[name]['routeBox']=page.locator('[data-route-search]').bounding_box()
  page.locator('[data-route-pause]').click();report[name]['paused']=page.locator('[data-route-pause]').get_attribute('aria-pressed')
  page.locator('.metrix-section-entry').scroll_into_view_if_needed();page.wait_for_timeout(1000)
  before=page.evaluate('window.__lenisWrapper.scrollTop');page.locator('.metrix-section-entry').click();page.wait_for_timeout(5000)
  report[name]['destination']=page.url
  page.go_back();page.wait_for_timeout(7000)
  report[name]['back']={'before':before,'after':page.evaluate('window.__lenisWrapper.scrollTop'),'url':page.url}
  page.close()
 print(json.dumps(report,indent=2));(out/'ux-report.json').write_text(json.dumps(report,indent=2))
 b.close()
