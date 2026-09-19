#!/usr/bin/env python3
"""Configure public URLs locally; never creates a remote or pushes."""
from pathlib import Path
import argparse,json,re
root=Path(__file__).resolve().parents[1]
ap=argparse.ArgumentParser();ap.add_argument('--owner',required=True);args=ap.parse_args()
if not re.fullmatch(r'[A-Za-z0-9](?:[A-Za-z0-9-]{0,37}[A-Za-z0-9])?',args.owner):raise SystemExit('Invalid GitHub owner')
meta=json.loads((root/'publication.json').read_text())
other='canonical-roots-lean-ja' if meta['role']=='canonical' else 'canonical-roots-lean'
meta['repository_url']=f'https://github.com/{args.owner}/{meta["repository_name"]}'
meta['companion_url']=f'https://github.com/{args.owner}/{other}'
(root/'publication.json').write_text(json.dumps(meta,ensure_ascii=False,indent=2)+'\n')
lock=root/'upstream.lock.json'
if lock.exists():
    value=json.loads(lock.read_text());value['repository']=f'https://github.com/{args.owner}/canonical-roots-lean';lock.write_text(json.dumps(value,indent=2)+'\n')
readme=root/'README.md';text=readme.read_text().split('\n<!-- EDITION_LINKS -->')[0].rstrip()
readme.write_text(text+'\n\n<!-- EDITION_LINKS -->\n[English source](https://github.com/'+args.owner+'/canonical-roots-lean) · [日本語解説](https://github.com/'+args.owner+'/canonical-roots-lean-ja)\n')
cff=root/'CITATION.cff';lines=[x for x in cff.read_text().splitlines() if not x.startswith('repository-code:')]
cff.write_text('\n'.join(lines)+'\nrepository-code: "'+meta['repository_url']+'"\n')
print('Configured local metadata for',meta['repository_url'])
