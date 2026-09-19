#!/usr/bin/env python3
"""Build genuine Lean Blueprint HTML/PDF plus a local exact-source browser.

The wrapper accommodates the preserved formal/ layout without adding Lean dependencies.
"""
from pathlib import Path
import argparse, html, json, os, shutil, subprocess
from check_blueprint import ROOT, source_root, inspect

def run(argv,cwd,log,env=None):
    with log.open('w') as f:
        p=subprocess.run(argv,cwd=cwd,stdout=f,stderr=subprocess.STDOUT,env=env)
    if p.returncode:
        print(log.read_text()[-7000:]);raise SystemExit(p.returncode)

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--source');ap.add_argument('--pdf',action='store_true');args=ap.parse_args()
    source=source_root(args.source);nodes,locations=inspect(source)
    logs=ROOT/'validation/publication';logs.mkdir(parents=True,exist_ok=True)
    run(['plastex','--config=plastex.cfg','web.tex'],ROOT/'blueprint/src',logs/'blueprint-web.log')
    site=ROOT/'_site';site.mkdir(exist_ok=True)
    # A fresh output directory prevents stale pages from surviving source edits.
    for name in ('blueprint','lean'):
        if (site/name).exists():shutil.rmtree(site/name)
    shutil.copytree(ROOT/'blueprint/web',site/'blueprint')
    src_out=site/'lean/source';src_out.mkdir(parents=True)
    css='body{max-width:1100px;margin:2rem auto;padding:0 1rem;font:16px system-ui;line-height:1.6;color:#172b3a}a{color:#176096}pre{overflow:auto;background:#f4f6f8;padding:1rem}pre span{display:block;scroll-margin:3rem}pre span:target{background:#ffefb0}.no{display:inline-block;width:4em;color:#718096;text-decoration:none;user-select:none}li{margin:.4rem 0}nav{margin-bottom:2rem}'
    def page(title,body,lang='en'):
        return '<!doctype html><html lang="'+lang+'"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>'+html.escape(title)+'</title><style>'+css+'</style><body>'+body+'</body></html>'
    for path in sorted({v['path'] for v in locations.values()}):
        outname=path.removeprefix('formal/').replace('/','.')+'.html'
        lines=(source/path).read_text().splitlines()
        body='<nav><a href="../../index.html">Home</a> · <a href="../../blueprint/index.html">Blueprint</a></nav><h1>'+html.escape(path)+'</h1><p>Exact source, with line anchors. This is not generated API documentation.</p><pre><code>'
        body+='\n'.join('<span id="L'+str(i)+'"><a class="no" href="#L'+str(i)+'">'+str(i)+'</a>'+html.escape(line)+'</span>' for i,line in enumerate(lines,1))+'</code></pre>'
        (src_out/outname).write_text(page(path,body))
    mapping={name:'../source/'+v['path'].removeprefix('formal/').replace('/','.')+'.html#L'+str(v['line']) for name,v in locations.items()}
    finder=site/'lean/find';finder.mkdir()
    body='<h1>Lean declaration source index</h1><p id="message">Choose a declaration below.</p><ul>'
    body+=''.join('<li><a href="'+html.escape(url,quote=True)+'">'+html.escape(name)+'</a></li>' for name,url in mapping.items())+'</ul>'
    body+='<script>const decls='+json.dumps(mapping).replace('<','\\u003c')+';const name=decodeURIComponent(location.hash.replace(/^#doc\\//,""));if(name){if(Object.hasOwn(decls,name)){location.replace(decls[name]);}else{document.getElementById("message").textContent="Unknown declaration: "+name;}}</script>'
    (finder/'index.html').write_text(page('Lean declaration source index',body))
    ja=not (ROOT/'formal').exists()
    language='ja' if ja else 'en'
    title='孤立 canonical-root 超曲面 — 日本語解説' if ja else 'Canonical-root hypersurfaces — Lean formalization'
    body='<h1>'+title+'</h1><p>Kenji Hashimoto · Hwayoung Lee · Kazushi Ueda</p>'
    body+='<p>'+('英語版の固定コミットに対応する日本語解説。' if ja else 'The canonical source edition and its curated mathematical blueprint.')+'</p>'
    body+='<ul><li><a href="blueprint/index.html">Lean Blueprint</a></li><li><a href="blueprint/dep_graph_document.html">Dependency graph / 依存グラフ</a></li><li><a href="lean/find/index.html">Lean source declarations / 宣言一覧</a></li>'
    if args.pdf:
        env=os.environ.copy();cache=ROOT/'.cache/tex';cache.mkdir(parents=True,exist_ok=True)
        env['TEXMFVAR']=str(cache);env['TEXMFCACHE']=str(cache)
        pdf_dir=ROOT/'blueprint/print';pdf_dir.mkdir(exist_ok=True)
        run(['latexmk','-lualatex','-interaction=nonstopmode','-halt-on-error','-outdir=../print','print.tex'],ROOT/'blueprint/src',logs/'blueprint-pdf.log',env)
        shutil.copy2(pdf_dir/'print.pdf',site/'blueprint.pdf')
        body+='<li><a href="blueprint.pdf">PDF</a></li>'
    body+='</ul><p>'+('Lean のビルド・公理監査と、数学的な意味の人手レビューは別々に確認してください。' if ja else 'Lean compilation and axiom audits are distinct from human review of the mathematical meaning.')+'</p>'
    meta=json.loads((ROOT/'publication.json').read_text())
    for label in ('repository_url','companion_url'):
        if meta.get(label):body+='<p><a href="'+html.escape(meta[label],quote=True)+'">'+label.replace('_',' ')+'</a></p>'
    if ja:
        lock=json.loads((ROOT/'upstream.lock.json').read_text());body+='<p>Canonical commit: <code>'+lock['commit']+'</code></p>'
    (site/'index.html').write_text(page(title,body,language));(site/'.nojekyll').touch()
    (site/'declaration-map.json').write_text(json.dumps(locations,indent=2)+'\n')
    print('Built',site)
if __name__=='__main__':main()
