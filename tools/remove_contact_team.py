"""Remove the Contact and Pilot Partners (join-the-team) pages and every link to them."""
import re
import shutil
from pathlib import Path
from bs4 import BeautifulSoup

ROOT = Path(__file__).resolve().parents[1] / 'site'
TARGET = re.compile(r'^(/es)?/(contact|join-the-team)/?$')

for prefix in ['', 'es/']:
    for page in ['contact', 'join-the-team']:
        shutil.rmtree(ROOT / prefix / page, ignore_errors=True)

for path in ROOT.rglob('index.html'):
    soup = BeautifulSoup(path.read_text('utf-8'), 'html.parser')
    links = soup.find_all('a', href=TARGET)
    if not links:
        continue
    for a in links:
        if a.decomposed:
            continue
        # Remove the smallest wrapper that only exists for this link.
        wrapper = (a.find_parent(class_='section_next') or a.find_parent(class_='button-wrap-lg')
                   or a.find_parent('li') or a.find_parent(class_='footer_socials') or a)
        wrapper.decompose()
    path.write_text(str(soup), 'utf-8')
    print('updated', path.relative_to(ROOT))
