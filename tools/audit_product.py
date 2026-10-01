from pathlib import Path
from bs4 import BeautifulSoup
from urllib.parse import unquote
import json
import re

root = Path(__file__).resolve().parents[1]
site = root / 'site'
issues, missing = [], set()
files = [p for p in site.rglob('*.html') if '_assets' not in str(p)]
pattern = re.compile(r'cominvi|Guanajuato|Edificio|1[.,]000[.,]000|837[.,]650|360 machines|1[.,]700', re.I)
for p in files:
    soup = BeautifulSoup(p.read_text('utf-8'), 'html.parser')
    for node in soup.select('script,style'):
        node.decompose()
    if pattern.search(soup.get_text(' ',strip=True)):
        issues.append(str(p.relative_to(site)))
    for node in soup.select('[src],a[href]'):
        url = node.get('src',node.get('href','')).split('#')[0].split('?')[0]
        if url.startswith('/') and not url.startswith('//'):
            if not (site / unquote(url.lstrip('/'))).exists():
                missing.add(url)
report = {'pages':len(files),'stale_claims':issues,'missing_targets':sorted(missing)}
(root/'verification/product-audit.json').write_text(json.dumps(report,indent=2),'utf-8')
print(json.dumps(report,indent=2))
