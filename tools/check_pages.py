"""Check each captured HTML page and discover remaining runtime assets."""
import asyncio
import json
import sys
from pathlib import Path
from urllib.parse import urlsplit

ROOT = Path(__file__).resolve().parents[1]
BASE = 'http://127.0.0.1:'+(sys.argv[1] if len(sys.argv)>1 else '8002')
sys.path.insert(0, str(ROOT.parent))
from crawler.browser import BrowserSession, BrowserConfig


async def main():
    manifest = json.loads((ROOT/'manifest.json').read_text('utf-8'))
    pages = [url for url, item in manifest.items() if item.get('ok') and 'text/html' in item['content_type']]
    results = []
    async with BrowserSession(BrowserConfig(headless=True)) as page:
        for url in pages:
            errors, missing, external = [], set(), set()
            error_handler = lambda msg: errors.append(msg.text) if msg.type == 'error' else None
            response_handler = lambda r: missing.add(r.url) if r.status >= 400 else None
            request_handler = lambda r: external.add(r.url) if r.url.startswith('http') and urlsplit(r.url).hostname != '127.0.0.1' else None
            page.on('console',error_handler)
            page.on('response',response_handler)
            page.on('request',request_handler)
            response = await page.goto(BASE+urlsplit(url).path,wait_until='networkidle')
            await page.wait_for_timeout(2500)
            result = {'url':url,'status':response.status,'errors':errors,'missing':sorted(missing),'external':sorted(external)}
            results.append(result)
            print(urlsplit(url).path, response.status,'errors',len(errors),'missing',len(missing),'external',len(external),flush=True)
            (ROOT/'verification/pages.json').write_text(json.dumps(results,ensure_ascii=False,indent=2),'utf-8')
            page.remove_listener('console',error_handler)
            page.remove_listener('response',response_handler)
            page.remove_listener('request',request_handler)


if __name__ == '__main__': asyncio.run(main())
