import asyncio
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT.parent))
from crawler.browser import BrowserSession, BrowserConfig


async def main():
    port = sys.argv[1] if len(sys.argv)>1 else '8002'
    results = []
    for label,width,height in [('desktop',1440,1000),('mobile',390,844)]:
        async with BrowserSession(BrowserConfig(headless=True,viewport_width=width,viewport_height=height)) as page:
            await page.goto(f'http://127.0.0.1:{port}/',wait_until='networkidle')
            await page.wait_for_timeout(6000)
            menu = page.locator('button.is-menu')
            await menu.click()
            await page.wait_for_timeout(1500)
            expanded = await menu.get_attribute('aria-expanded')
            nav_link = page.locator('.nav-inner a[href="/our-services"]')
            if not await nav_link.count():
                nav_link = page.locator('a[href="/our-services"]').first
            menu_visible = await nav_link.is_visible()
            await page.screenshot(path=str(ROOT/'verification'/f'{label}-menu.png'))
            links = page.locator('a[href="/our-services"]')
            clicked = False
            for i in range(await links.count()):
                link = links.nth(i)
                if await link.is_visible():
                    await link.click()
                    clicked = True
                    break
            await page.wait_for_url('**/our-services')
            await page.wait_for_timeout(3500)
            await page.screenshot(path=str(ROOT/'verification'/f'{label}-services-navigation.png'))
            result = {'viewport':label,'menu_aria_expanded':expanded,'menu_visible':menu_visible,'clicked_services':clicked,'destination':page.url,'title':await page.title()}
            assert menu_visible and clicked and page.url.endswith('/our-services'), result
            results.append(result)
            print(result,flush=True)
    (ROOT/'verification/interactions.json').write_text(json.dumps(results,ensure_ascii=False,indent=2),'utf-8')


if __name__ == '__main__': asyncio.run(main())
