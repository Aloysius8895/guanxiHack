"""Build a local mirror from the existing crawler's network capture.

Run from any directory: python guanxiHack/tools/mirror.py
Only public GET resources are downloaded. Original responses are kept in raw/.
"""
from __future__ import annotations

import concurrent.futures
import hashlib
import html
import json
import re
import time
import urllib.error
import urllib.request
from collections import deque
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urldefrag, urljoin, urlsplit, unquote

ROOT = Path(__file__).resolve().parents[1]
ORIGIN = 'https://www.cominvi.com.mx'
OWN = {'www.cominvi.com.mx', 'cominvi.com.mx'}
ASSET_HOSTS = {'cdn.prod.website-files.com', 'assets.website-files.com',
               'd3e54v103j8qbb.cloudfront.net', 'cominvi.pages.dev',
               'cominvi.netlify.app', 'precious-hotteok-8da21f.netlify.app',
               'cdn.jsdelivr.net', 'tiles.openfreemap.org',
               'fonts.googleapis.com', 'fonts.gstatic.com'}
EXT = re.compile(r'\.(?:css|js|mjs|json|png|jpe?g|webp|avif|gif|svg|ico|woff2?|ttf|otf|eot|mp4|webm|mp3|wav|af|glb|gltf|bin|pdf|wasm|pbf)(?:[?#]|$)', re.I)
ABS = re.compile(r'https?://[^\s\"\x27`<>\\)]+')
manifest = json.loads((ROOT/'manifest.json').read_text('utf-8')) if (ROOT/'manifest.json').exists() else {}


def normalize(url):
    url = urldefrag(html.unescape(url))[0]
    parts = urlsplit(url)
    if parts.scheme not in ('https', 'http') or not parts.hostname:
        return None
    return url


def relative_path(url):
    p = urlsplit(url)
    parts = [re.sub(r'[<>:"|?*]', '_', unquote(x)) for x in p.path.split('/') if x and x not in ('.', '..')]
    if p.hostname in OWN:
        rel = Path(*parts) if parts else Path('index.html')
        if not rel.suffix:
            rel = rel/'index.html'
    else:
        rel = Path('_assets', p.hostname, *(parts or ['index']))
        if p.hostname == 'tiles.openfreemap.org' and p.path == '/planet':
            rel = rel/'index.json'
    if p.query:
        rel = rel.with_name(rel.stem+'__'+hashlib.sha256(p.query.encode()).hexdigest()[:10]+rel.suffix)
    return rel.as_posix()


class References(HTMLParser):
    def __init__(self, base):
        super().__init__()
        self.base, self.urls = base, set()

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        for key in ('src', 'poster', 'data-src', 'data-poster-url', 'data-video-urls'):
            if attrs.get(key):
                for value in attrs[key].split(','):
                    self.urls.add(urljoin(self.base, value.strip()))
        if attrs.get('srcset'):
            for value in attrs['srcset'].split(','):
                if value.strip(): self.urls.add(urljoin(self.base, value.strip().split()[0]))
        if attrs.get('href'):
            value = urljoin(self.base, attrs['href'])
            host = urlsplit(value).hostname
            if (tag == 'a' and host in OWN) or (tag == 'link' and attrs.get('rel') not in ('preconnect', 'dns-prefetch', 'canonical', 'alternate')):
                self.urls.add(value)
        for key, value in attrs.items():
            if value and ',' not in value and key.startswith('data-') and EXT.search(value) and value.startswith(('https://', 'http://', '/')):
                self.urls.add(urljoin(self.base, value))


def references(url, data, content_type):
    found = set()
    if not any(x in content_type for x in ('text/', 'javascript', 'json', 'xml', 'svg')):
        return found
    s = data.decode('utf-8', errors='replace')
    if 'html' in content_type:
        parser = References(url)
        parser.feed(s)
        found.update(parser.urls)
    for candidate in ABS.findall(s):
        for match in candidate.split(','):
            if EXT.search(match) and '{' not in match and urlsplit(match).hostname in ASSET_HOSTS | OWN:
                found.add(match.rstrip(';'))
    if 'css' in content_type:
        for match in re.findall(r'url\(\s*[\"\x27]?([^\s)\"\x27]+)', s):
            found.add(urljoin(url, match))
    if 'javascript' in content_type or urlsplit(url).path.endswith(('.js', '.mjs')):
        for match in re.findall(r'[\"\x27]((?:\./|\.\./)[^\"\x27\s]+\.(?:js|mjs|css|wasm))[\"\x27]', s):
            found.add(urljoin(url, match))
        # Vite modulepreload lists are relative to the bundle root.
        for match in re.findall(r'[\"\x27](assets/[^\"\x27\s]+\.(?:js|css))[\"\x27]', s):
            found.add(urljoin('https://cominvi.pages.dev/', match))
    if url.endswith('/cave-scene/scroll/manifest.json'):
        doc = json.loads(s)
        base = 'https://cominvi.pages.dev'
        for variant in doc['variants'].values():
            for value in variant['intro'].values(): found.add(base+value)
            seq = variant['scroll']
            for batch in seq['batches']:
                for index in range(batch['startIndex'], batch['startIndex']+batch['count']):
                    found.add(f"{base}{seq['basePath']}/{batch['id']}/frame_{index:05d}.webp")
        found.add(base+doc['poster']['webp'])
    return {v for x in found if (v := normalize(x)) and urlsplit(v).hostname in ASSET_HOSTS | OWN}


def download(url):
    rel = relative_path(url)
    target = ROOT/'raw'/rel
    old = manifest.get(url)
    if old and old.get('ok') and target.is_file():
        return url, old, references(url, target.read_bytes(), old['content_type'])
    error = 'Download failed'
    for attempt in range(3):
        try:
            req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0', 'Referer': ORIGIN+'/', 'Accept-Encoding': 'identity'})
            with urllib.request.urlopen(req, timeout=60) as r:
                data = r.read()
                ctype = r.headers.get('Content-Type', 'application/octet-stream')
                status = r.status
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes(data)
            entry = {'ok': True, 'path': rel, 'content_type': ctype, 'bytes': len(data), 'status': status}
            return url, entry, references(url, data, ctype)
        except Exception as exc:
            error = str(exc)
            if isinstance(exc, urllib.error.HTTPError) and exc.code in (404, 403): break
            if attempt < 2: time.sleep(attempt+1)
    return url, {'ok': False, 'path': rel, 'error': error}, set()


def rewrite():
    # Preserve folder structure so relative CSS URLs and ES module imports work.
    replacements = {}
    for url, entry in manifest.items():
        if not entry.get('ok'): continue
        p = urlsplit(url)
        localized = '/'+entry['path']
        if p.hostname not in OWN and not Path(p.path).suffix:
            localized = localized.removesuffix('/index.json')
        replacements[url] = localized if p.hostname not in OWN or Path(p.path).suffix else p.path or '/'
    # Root replacements also cover runtime-constructed animation URLs.
    for host in ASSET_HOSTS:
        replacements['https://'+host] = '/_assets/'+host
        replacements['http://'+host] = '/_assets/'+host
    for host in OWN:
        replacements['https://'+host] = ''
    pattern = re.compile('|'.join(re.escape(k) for k in sorted(replacements, key=len, reverse=True)))
    for entry in manifest.values():
        if not entry.get('ok'): continue
        data = (ROOT/'raw'/entry['path']).read_bytes()
        if any(t in entry['content_type'] for t in ('text/', 'javascript', 'json', 'xml', 'svg')):
            s = data.decode('utf-8', errors='replace')
            s = pattern.sub(lambda m: replacements[m[0]], s)
            if 'html' in entry['content_type']:
                # Original SRI hashes no longer match files with localized URLs.
                s = re.sub(r'\s+integrity="[^"]*"', '', s)
                # The source services page has a stray semicolon inside a poster URL.
                s = s.replace('.avif;\'','.avif\'')
            data = s.encode('utf-8')
        dest = ROOT/'site'/entry['path']
        dest.parent.mkdir(parents=True, exist_ok=True)
        dest.write_bytes(data)


def main():
    for url in list(manifest):
        if ',https://' in url: del manifest[url]
    seeds = {ORIGIN+'/'}
    for file in (ROOT/'capture').glob('*/network/requests.json'):
        for entry in json.loads(file.read_text('utf-8')):
            if entry.get('method') == 'GET': seeds.add(entry['url'])
    extra = ROOT/'extra-urls.json'
    if extra.exists(): seeds.update(json.loads(extra.read_text('utf-8')))
    pending = deque(seeds)
    seen = set()
    with concurrent.futures.ThreadPoolExecutor(max_workers=8) as pool:
        while pending:
            batch = []
            while pending and len(batch) < 40:
                url = normalize(pending.popleft())
                if not url or url in seen or urlsplit(url).hostname not in ASSET_HOSTS | OWN: continue
                seen.add(url)
                batch.append(url)
            for url, entry, refs in pool.map(download, batch):
                manifest[url] = entry
                pending.extend(refs-seen)
                if not entry['ok']: print('FAILED', url, entry.get('error'), flush=True)
            (ROOT/'manifest.json').write_text(json.dumps(manifest, ensure_ascii=False, indent=2), 'utf-8')
            print(f'Scanned {len(seen)}, saved {sum(bool(x.get("ok")) for x in manifest.values())}, queued {len(pending)}', flush=True)
    rewrite()
    print('Local mirror ready:', ROOT/'site', flush=True)


if __name__ == '__main__': main()
