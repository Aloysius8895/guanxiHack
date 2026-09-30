"""Verify the mirror with the project's existing BrowserSession."""
import asyncio
import json
import sys
from pathlib import Path
from urllib.parse import urlsplit

ROOT = Path(__file__).resolve().parents[1]
BASE = 'http://127.0.0.1:'+(sys.argv[1] if len(sys.argv)>1 else '8002')
sys.path.insert(0, str(ROOT.parent))
from crawler.browser import BrowserSession, BrowserConfig


async def check(name, url, width, height, scroll=False):
    errors, failed, external, missing = [], [], set(), set()
    async with BrowserSession(BrowserConfig(headless=True, viewport_width=width, viewport_height=height)) as page:
        page.on('pageerror', lambda error: errors.append(str(error)))
        page.on('console', lambda msg: errors.append(msg.text) if msg.type == 'error' else None)
        page.on('requestfailed', lambda req: failed.append({'url': req.url, 'error': req.failure}))
        page.on('request', lambda req: external.add(req.url) if req.url.startswith('http') and urlsplit(req.url).hostname not in ('127.0.0.1', 'localhost') else None)
        page.on('response', lambda r: missing.add(r.url) if r.status >= 400 else None)
        response = await page.goto(url, wait_until='networkidle', timeout=60000)
        await page.wait_for_timeout(7000)
        await page.screenshot(path=str(ROOT/'verification'/f'{name}-top.png'))
        top = await page.evaluate('''() => ({title:document.title, text:document.body.innerText.length, images:document.images.length, broken:[...document.images].filter(x=>x.complete && !x.naturalWidth).map(x=>x.src), scrollables:[...document.querySelectorAll('*')].filter(x=>x.clientHeight>300 && x.scrollHeight>x.clientHeight+500).map(x=>({tag:x.tagName, cls:x.className,height:x.scrollHeight,client:x.clientHeight}))})''')
        if scroll:
            await page.mouse.move(width//2, height//2)
            for step in range(32):
                await page.mouse.wheel(0, 700)
                await page.wait_for_timeout(350)
                if step in (3, 11, 23, 31):
                    await page.screenshot(path=str(ROOT/'verification'/f'{name}-scroll-{step}.png'))
            top['after_scroll'] = await page.evaluate('''() => [...document.querySelectorAll('*')].filter(x=>x.scrollTop>100).map(x=>({cls:x.className,top:x.scrollTop,height:x.scrollHeight}))''')
        result = {'name':name, 'url':url, 'status':response.status, 'page':top,'errors':errors,'failed':failed,'external':sorted(external),'missing':sorted(missing)}
        print(name, 'status',result['status'], 'errors',len(errors),'missing',len(missing),'external',len(external),flush=True)
        return result


async def main():
    (ROOT/'verification').mkdir(exist_ok=True)
    results = []
    for params in [('desktop',BASE+'/',1440,1000,True),('mobile',BASE+'/',390,844,True),('services',BASE+'/our-services',1440,1000,True),('spanish',BASE+'/es',1440,1000,False)]:
        results.append(await check(*params))
        (ROOT/'verification/results.json').write_text(json.dumps(results,ensure_ascii=False,indent=2),'utf-8')


if __name__ == '__main__': asyncio.run(main())
