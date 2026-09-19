#!/usr/bin/env python3
"""Validate the curated Blueprint map; optionally resolve declarations in Lean.

Prose correspondence and dependency edges are editorial, not certified here.
"""
from pathlib import Path
import argparse, hashlib, json, re, subprocess
ROOT=Path(__file__).resolve().parents[1]

def source_root(value=None):
    source=Path(value).resolve() if value else ROOT
    if not (source/'formal/lean-toolchain').is_file() and not value:
        source=(ROOT/'../canonical-roots-lean').resolve()
    if not (source/'formal/lean-toolchain').is_file():
        raise ValueError('Pass --source /path/to/canonical-roots-lean')
    return source

def declarations(path):
    stack=[]; found={}
    for line_no,line in enumerate(path.read_text().splitlines(),1):
        m=re.match(r'^(?:noncomputable )?(namespace|section)\b(?:\s+([^\s]+))?',line)
        if m:
            stack.append((m[1],m[2] or ''));continue
        if re.match(r'^end(?:\s|$)',line):
            if stack:stack.pop()
            continue
        m=re.match(r'^(?:@\[[^]]+\]\s*)?(?:(?:noncomputable|protected|private)\s+)*(?:theorem|def|abbrev|structure|inductive)\s+([^\s:({]+)',line)
        if m:
            name='.'.join([s[1] for s in stack if s[0]=='namespace']+[m[1]])
            found[name]=line_no
    return found

def inspect(source):
    nodes=json.loads((ROOT/'blueprint/nodes.json').read_text())
    content=(ROOT/'blueprint/src/content.tex').read_text()
    labels=re.findall(r'\\label\{([^}]+)\}',content)
    expected=[n['label'] for n in nodes]
    if len(set(expected))!=len(expected) or labels!=expected:raise ValueError('Blueprint label mismatch')
    refs=[x.strip() for s in re.findall(r'\\lean\{([^}]+)\}',content) for x in s.split(',')]
    if refs!=[d for n in nodes for d in n['declarations']]:raise ValueError('Blueprint declaration order mismatch')
    locations={}; graph={n['label']:n['uses'] for n in nodes}
    for n in nodes:
        section=content.split('\\label{'+n['label']+'}',1)[1].split('\\label{',1)[0]
        # The next environment has no uses before its own label.
        used=[x.strip() for s in re.findall(r'\\uses\{([^}]+)\}',section) for x in s.split(',')]
        if used!=n['uses']:raise ValueError('Blueprint edge mismatch: '+n['label'])
        file=source/'formal/CanonicalRoots'/(n['module']+'.lean')
        decls=declarations(file)
        for name in n['declarations']:
            if name not in decls:raise ValueError('No exact source declaration: '+name)
            locations[name]={'path':str(file.relative_to(source)),'line':decls[name]}
    visiting=set(); visited=set()
    def visit(label):
        if label in visiting:raise ValueError('Dependency cycle: '+label)
        if label not in graph:raise ValueError('Unknown dependency: '+label)
        if label in visited:return
        visiting.add(label)
        for used in graph[label]:visit(used)
        visiting.remove(label);visited.add(label)
    for label in graph:visit(label)
    if source!=ROOT:
        if (ROOT/'blueprint/nodes.json').read_bytes()!=(source/'blueprint/nodes.json').read_bytes():raise ValueError('Japanese graph differs from canonical graph')
        lock=json.loads((ROOT/'upstream.lock.json').read_text())
        head=subprocess.check_output(['git','-C',str(source),'rev-parse','HEAD'],text=True).strip()
        if lock['commit']!=head:raise ValueError('Wrong canonical commit; check upstream.lock.json')
        manifest=source/'evidence/source-manifest.json'
        if hashlib.sha256(manifest.read_bytes()).hexdigest()!=lock['source_manifest_sha256']:
            raise ValueError('Canonical manifest does not match the companion pin')
        dirty=subprocess.check_output(['git','-C',str(source),'status','--porcelain','--untracked-files=no','--','formal','blueprint/nodes.json','evidence/source-manifest.json'],text=True)
        if dirty:raise ValueError('Canonical source has uncommitted changes')
        hashes=json.loads(manifest.read_text())
        for path,digest in hashes.items():
            if hashlib.sha256((source/path).read_bytes()).hexdigest()!=digest:raise ValueError('Canonical source changed: '+path)
    return nodes,locations

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--source');ap.add_argument('--lean',action='store_true');args=ap.parse_args()
    source=source_root(args.source);nodes,locations=inspect(source)
    out=ROOT/'validation/publication';out.mkdir(parents=True,exist_ok=True)
    (out/'declaration-map.json').write_text(json.dumps(locations,indent=2)+'\n')
    if args.lean:
        path=source/'formal/.publication/BlueprintCheck.lean';path.parent.mkdir(exist_ok=True)
        path.write_text('import CanonicalRoots\nimport OutputCertificates\n'+''.join('#check '+n+'\n#print axioms '+n+'\n' for n in locations))
        run=subprocess.run(['lake','env','lean',str(path)],cwd=source/'formal',capture_output=True,text=True)
        (out/'blueprint-declarations.log').write_text(run.stdout+run.stderr)
        if run.returncode:raise SystemExit(run.returncode)
        reports={m[1]:[x.strip() for x in (m[2] or '').split(',') if x.strip()] for m in re.finditer(r"'([^']+)'\s+(?:depends on axioms:\s*\[([^\]]*)\]|does not depend on any axioms)",run.stdout,re.S)}
        if set(reports)!=set(locations):raise ValueError('Missing Lean axiom reports')
        for name,axioms in reports.items():
            if set(axioms)-{'propext','Classical.choice','Quot.sound'}:raise ValueError('Disallowed axioms: '+name)
    print(f'PASS: {len(nodes)} nodes, {len(locations)} declarations, acyclic curated graph'+('; Lean resolution and axiom allowlist passed' if args.lean else '; static checks only'))
if __name__=='__main__':main()
