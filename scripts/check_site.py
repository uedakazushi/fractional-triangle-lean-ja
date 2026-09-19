#!/usr/bin/env python3
"""Check generated HTML targets, fragments, and the Blueprint Lean resolver links."""
from pathlib import Path
from html.parser import HTMLParser
from urllib.parse import urlsplit, unquote
import json
ROOT=Path(__file__).resolve().parents[1]; SITE=ROOT/'_site'
class Links(HTMLParser):
    def __init__(self):super().__init__();self.links=[];self.ids=set()
    def handle_starttag(self,tag,attrs):
        a=dict(attrs)
        if 'id' in a:self.ids.add(a['id'])
        if tag=='a' and 'name' in a:self.ids.add(a['name'])
        for key in ('href','src'):
            if a.get(key):self.links.append(a[key])
parsed={}
for f in SITE.rglob('*.html'):
    p=Links();p.feed(f.read_text());parsed[f.resolve()]=p
names=json.loads((SITE/'declaration-map.json').read_text()); errors=[]; checked=0; lean_links=0
for file,p in parsed.items():
    for raw in p.links:
        url=urlsplit(raw)
        if url.scheme or url.netloc:continue
        target=(file.parent/unquote(url.path)).resolve() if url.path else file
        if target.is_dir():target=target/'index.html'
        checked+=1
        if not target.is_file():errors.append(f'{file.relative_to(SITE)}: missing {raw}');continue
        fragment=unquote(url.fragment)
        if fragment.startswith('doc/'):
            lean_links+=1
            if fragment[4:] not in names:errors.append('Unknown Lean link: '+raw)
        elif fragment and target.suffix=='.html' and fragment not in parsed[target].ids:
            errors.append(f'{file.relative_to(SITE)}: missing fragment {raw}')
if not lean_links:errors.append('No Lean declaration links found')
if errors:raise SystemExit('\n'.join(errors))
print(f'PASS: {len(parsed)} HTML files; {checked} local links; {lean_links} Lean links')
