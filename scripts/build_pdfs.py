#!/usr/bin/env python3
"""Reproducible, incremental Markdown -> HTML/KaTeX -> branded PDF."""
from pathlib import Path
import argparse, difflib, hashlib, html, json, os, re, subprocess, sys

ROOT = Path(__file__).resolve().parents[1]
WORK = ROOT / 'output/pdf/production'
PILOT = ROOT / 'output/pdf/pilot-html-vs-latex-2026-10-22'
RUNTIME = Path.home() / '.cache/codex-runtimes/codex-primary-runtime/dependencies'
PANDOC = PILOT / 'tools/pandoc-3.12.1-arm64/bin/pandoc'
KATEX = PILOT / 'tools/katex/dist'
LOGO = ROOT / 'logo - amitay/amitai-logo.pdf'

def digest(path): return hashlib.sha256(Path(path).read_bytes()).hexdigest()
def write_json(path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2)+'\n')

def normalize(raw, path):
    text=raw
    if path.name.startswith('5.2_הזזות_'):
        for a,b in [
            ('(x-3)(x-6)=$0$','@@EQ14@@'),
            (';$A$(3,4)$,$B$(6,1)$','; $A(3,4), B(6,1)$'),
            ('$A$(3,4)$','$A(3,4)$'),
            ('(x-2)(x-5)=0$','$(x-2)(x-5)=0$'),
            ('y=(x-3)^2+$4$;','$y=(x-3)^2+4$;'),
            ('$y$:$','$y$:'),
            ('(x-3)^2=-4$','$(x-3)^2=-4$'),
            ('-(x-4)^2+$5$;','$-(x-4)^2+5$;'),
            ('(x-3)(x-6)=0$','$(x-3)(x-6)=0$'),
        ]:text=text.replace(a,b)
        text=text.replace('@@EQ14@@','$(x-3)(x-6)=0$')
    if path.name.startswith('5.3_שטחים_והיקפים_'):
        # Repair malformed delimiters in the production copy; preserve numbers.
        text=re.sub(r'\$([ABCDE])\$\(([^)\n]+)\)\$',r'$\1(\2)$',text)
        text=re.sub(r'(?<![A-Za-z$])([A-Z])\$\(([^)\n]+)\)\$',r'$\1(\2)$',text)
        text=text.replace('(x-5)(x+2)=$0$','$(x-5)(x+2)=0$')
        text=text.replace('(x-4)(x+1)=$0$','$(x-4)(x+1)=0$')
        text=text.replace('$C\\left$\n$(\\frac{5}{2},-\\frac{29}{4}\\right)$', '$C\\left(\\frac{5}{2},-\\frac{29}{4}\\right)$')
    # Equivalent TeX notation for units, split delimiters and coordinates.
    text=re.sub(r'\$([ABCDE])\$\(([^)\n]+)\)\$',r'$\1(\2)$',text)
    text=re.sub(r'(?<![A-Za-z$])([A-Z])\$\(([^)\n]+)\)\$',r'$\1(\2)$',text)
    text=re.sub(r'\\left\$\s*\$\(',r'\\left(',text)
    text=re.sub(r'\\text\{([^{}]*?)\^(\d+)\}',lambda m:r'\text{'+m[1]+'}^{'+m[2]+'}',text)
    if path.parent.name.startswith('8 - ') and path.name.startswith('6.2_'):
        text=text.replace('$x>$2$','$x>2$').replace('$x>$4$','$x>4$').replace('$-4<x<$3$','$-4<x<3$')
        text=text.replace('$1:$\nx=3\\pm\\sqrt{5}$','1:\n$x=3\\pm\\sqrt{5}$')
        text=text.replace('פרבולה 2:$','פרבולה 2:').replace('$x=4$\n;$','$x=4$\n;')
        text=text.replace('$1:$\n$(4,5)$','1:\n$(4,5)$')
        text=text.replace('$B$\n(\\frac{3}{2},\\frac{25}{4});','$B(\\frac{3}{2},\\frac{25}{4})$;')
    text=re.sub(r'(\$\$.*?\$\$|\$[^$]+\$)',lambda m:m[0].replace('°',r'^{\circ}') if m[0].startswith('$$') else '$'+m[0][1:-1].strip().replace('°',r'^{\circ}')+'$',text,flags=re.S)
    text=re.sub(r'(?m)^(\s*[א-ת]\.)\s*$',r'\n\1 ',text)
    text=re.sub(r'\$\$(.*?)\$\$\s*\n\s*([.,;:])(?=\s*(?:\n|$))',lambda m:'$$'+m[1]+r'\text{'+m[2]+'}$$',text,flags=re.S)
    lines=text.splitlines(); out=[]
    for j,line in enumerate(lines):
        table=line.lstrip().startswith('|'); prev=j>0 and lines[j-1].lstrip().startswith('|')
        if table and not prev and out and out[-1].strip():out.append('')
        if not table and prev and line.strip():out.append('')
        out.append(line)
    return '\n'.join(out)+'\n'

def annotate(text):
    """Keep every source line; add print grouping without rebuilding its prose."""
    out=[]; current=False; answers=False; active=False; qs=[]; ans=[];current_number=None
    illustrations={}
    def collect_image(m):
        illustrations.setdefault(int(m[1]),[]).append(m[0]);return ''
    # Some source illustrations appear after the next level heading. Bind them
    # to their explicit exercise number, rather than their incidental position.
    text=re.sub(r'(?m)^!\[(?:גרף )?תרגיל (\d+)\]\([^\n]+\)\s*$',collect_image,text)
    def close():
        nonlocal current
        if current:
            if not answers:out.extend(['',*illustrations.pop(current_number,[]),''])
            out.extend(['',':::','']);current=False
    for line in text.splitlines():
        if line.startswith('<details'):
            close();answers=True;active=True;out.extend(['','## תשובות סופיות {.answer-start}','']);continue
        if line.startswith('<summary') or line.startswith('</details'):continue
        if re.match(r'^#{1,2} ',line):
            close()
            if line.startswith('## ') and 'רמה' in line:active=True
            out.append(line);continue
        m=re.match(r'^(?:\*\*)?(\d+)\.(?:\*\*)?\s*(.*)$',line) if active else None
        bold=re.match(r'^\*\*תרגיל\s+(\d+)(?::)?\*\*\s*(.*)$',line) if active else None
        if m or bold:
            close();n=int((m or bold)[1]);rest=(m or bold)[2]
            current_number=n
            (ans if answers else qs).append(n)
            out.extend(['',f'::: {{.{"answer" if answers else "exercise"} data-{"answer" if answers else "q"}="{n}"}}',''])
            # Preserve original bold exercise labels and their provenance wording.
            out.extend([line if bold else f'### {"תשובה" if answers else "תרגיל"} {n}', '' if bold else rest, ''])
            current=True;continue
        if line.strip()=='---' and current:continue
        out.append(line)
    close()
    if illustrations:raise ValueError(f'Illustration without matching exercise: {list(illustrations)}')
    if qs!=list(range(1,len(qs)+1)) or ans!=qs:
        raise ValueError(f'Question/answer sequence mismatch: {qs}, {ans}')
    return '\n'.join(out),qs,ans

RUN = re.compile(r'[-+−]?[A-Za-z0-9]+(?:[.:/_–—-][A-Za-z0-9]+)*(?:°C|°)?|°C')
def walk(obj, stats):
    if isinstance(obj,list):
        out=[]
        for item in obj:
            if isinstance(item,dict) and item.get('t')=='Str':
                txt=item['c'];pos=0
                for m in RUN.finditer(txt):
                    if m.start()>pos:out.append({'t':'Str','c':txt[pos:m.start()]})
                    out.append({'t':'Span','c':[['',[],[['dir','ltr']]],[{'t':'Str','c':m[0]}]]});pos=m.end()
                if pos<len(txt):out.append({'t':'Str','c':txt[pos:]})
            else:out.append(walk(item,stats))
        return out
    if isinstance(obj,dict):
        if obj.get('t')=='Math':stats['math']+=1
        if obj.get('t')=='Image':
            stats['images']+=1
            target=obj['c'][2][0]
            obj['c'][2][0]=(stats['source'].parent/target).resolve().as_uri()
        return {k:walk(v,stats) for k,v in obj.items()}
    return obj

def prepare(args):
    WORK.mkdir(parents=True,exist_ok=True)
    oldfile=WORK/'manifest.json'
    old={m['source']:m for m in json.loads(oldfile.read_text())} if oldfile.exists() else {}
    engine=hashlib.sha256(b''.join(p.read_bytes() for p in [Path(__file__),ROOT/'scripts/render_pdfs.cjs',ROOT/'scripts/pdf-print.css',LOGO,KATEX/'katex.min.js',KATEX/'katex.min.css',PANDOC])).hexdigest()
    docs=[];pending=[]
    dirs=sorted([p for p in ROOT.iterdir() if p.is_dir() and re.match(r'^(?:[1-9]|10) - ',p.name)],key=lambda p:int(p.name.split(' ')[0]))
    for chapter in dirs:
        number=int(chapter.name.split(' ')[0]);dest=ROOT/chapter.name.replace(' - ',' PDF - ',1)
        for src in sorted(chapter.rglob('*.md')):
            rel=str(src.relative_to(ROOT));raw=src.read_text()
            images=[(src.parent/x).resolve() for x in re.findall(r'!\[[^\]]*\]\(([^)]+)\)',raw)]
            deps={str(p.relative_to(ROOT)):digest(p) for p in sorted(set(images))}
            sourcehash=digest(src)
            fp=hashlib.sha256(json.dumps([engine,sourcehash,deps],sort_keys=True).encode()).hexdigest()
            output=dest/src.relative_to(chapter).with_suffix('.pdf');prev=old.get(rel,{})
            changed=args.force or prev.get('rendered_fingerprint')!=fp or not output.exists() or (output.exists() and prev.get('pdf_sha256')!=digest(output))
            m={**prev,'source':rel,'chapter':number,'sha256':sourcehash,'dependencies':deps,'fingerprint':fp,'output':str(output.relative_to(ROOT)),'id':hashlib.sha256(rel.encode()).hexdigest()[:12]}
            selected=(not args.chapter or number in args.chapter) and (not args.file or args.file in rel)
            if changed and selected and not args.check:
                normalized=normalize(raw,src)
                if normalized.count('$')%2:raise ValueError(f'Odd number of math delimiters after normalization: {src}')
                annotated,qs,ans=annotate(normalized)
                folder=WORK/'documents'/m['id'];folder.mkdir(parents=True,exist_ok=True)
                (folder/'normalized.md').write_text(normalized)
                (folder/'normalization.diff').write_text(''.join(difflib.unified_diff(raw.splitlines(True),normalized.splitlines(True),fromfile=rel,tofile='production-copy')))
                ast=json.loads(subprocess.run([str(PANDOC),'-f','markdown+tex_math_dollars-smart+fenced_divs','-t','json'],input=annotated,text=True,capture_output=True,check=True).stdout)
                stats={'math':0,'images':0,'source':src};ast=walk(ast,stats)
                if stats['images']!=len(images):raise ValueError(f'Lost image: {src}')
                body=subprocess.run([str(PANDOC),'-f','json','-t','html','--katex','--wrap=none'],input=json.dumps(ast),text=True,capture_output=True,check=True).stdout
                css=(ROOT/'scripts/pdf-print.css').read_text()
                title=re.search(r'^# (.+)',raw,re.M)[1]
                doc=f'<!doctype html><html dir="rtl" lang="he"><meta charset="utf-8"><title>{html.escape(title)}</title><link rel="stylesheet" href="{(KATEX/"katex.min.css").as_uri()}"><style>{css}</style><body class="chapter-{number}"><div class="chapter-name">{html.escape(chapter.name)}</div>{body}<script src="{(KATEX/"katex.min.js").as_uri()}"></script><script>'+'''window.mathErrors=[];for(const el of document.querySelectorAll('.math')){let src=el.textContent;try{katex.render(src,el,{displayMode:el.classList.contains('display'),throwOnError:true,strict:'ignore',trust:false});for(const t of el.querySelectorAll('.mord.text')){if(/[א-ת]/.test(t.textContent)){t.dir='rtl';t.style.unicodeBidi='isolate';}}}catch(e){window.mathErrors.push({source:src,error:String(e)});}}window.ready=true;</script></body></html>'''
                (folder/'document.html').write_text(doc)
                m.update(questions=len(qs),answers=len(ans),images=len(images),math=stats['math'],normalized=normalized!=raw,html=str(folder/'document.html'),raw_pdf=str(folder/'raw.pdf'))
                pending.append(m)
            elif changed and selected:pending.append(m)
            docs.append(m)
    if not args.check:
        write_json(WORK/'manifest.json',docs);write_json(WORK/'pending.json',pending)
    print(json.dumps({'documents':len(docs),'pending':len(pending),'unchanged':len(docs)-len(pending)},ensure_ascii=False))
    return pending

def finalize():
    from pypdf import PdfReader,PdfWriter,Transformation
    from pypdf.generic import NameObject,TextStringObject
    docs=json.loads((WORK/'manifest.json').read_text());lookup={m['source']:m for m in docs}
    logo=PdfReader(LOGO).pages[0];scale=26*72/25.4/float(logo.mediabox.width)
    for m in json.loads((WORK/'pending.json').read_text()):
        raw=Path(m['raw_pdf']);reader=PdfReader(raw);writer=PdfWriter()
        for page in reader.pages:
            x=float(page.mediabox.width)-17*72/25.4-26*72/25.4
            y=float(page.mediabox.height)-6*72/25.4-float(logo.mediabox.height)*scale
            page.merge_transformed_page(logo,Transformation().scale(scale).translate(x,y))
            page[NameObject('/AmitaiLogoSHA256')]=TextStringObject(digest(LOGO))
            writer.add_page(page)
        writer.add_metadata({'/Title':Path(m['source']).stem,'/Author':'אמיתי — מתמטיקה ותכנות על אמת','/Subject':m['source'],'/Producer':'Markdown / Pandoc / KaTeX / Chromium; vector logo'})
        out=ROOT/m['output'];out.parent.mkdir(parents=True,exist_ok=True)
        temporary=out.with_suffix('.pdf.tmp')
        with temporary.open('wb') as f:writer.write(f)
        temporary.replace(out)
        m.update(pages=len(reader.pages),pdf_sha256=digest(out),logo_sha256=digest(LOGO),rendered_fingerprint=m['fingerprint'])
        lookup[m['source']]=m
    write_json(WORK/'manifest.json',[lookup[m['source']] for m in docs])
    print('Finalized',len(json.loads((WORK/'pending.json').read_text())),'PDFs')

def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--chapter',type=int,nargs='+');ap.add_argument('--file');ap.add_argument('--force',action='store_true');ap.add_argument('--check',action='store_true');ap.add_argument('--prepare',action='store_true');ap.add_argument('--finalize',action='store_true')
    args=ap.parse_args()
    if args.finalize:finalize();return
    pending=prepare(args)
    if args.check or args.prepare or not pending:return
    subprocess.run([str(RUNTIME/'node/bin/node'),str(ROOT/'scripts/render_pdfs.cjs')],check=True)
    finalize()

if __name__=='__main__':
    try:import pypdf
    except ImportError:
        py=RUNTIME/'python/bin/python3'
        if Path(sys.executable).resolve()!=py.resolve():os.execv(str(py),[str(py),__file__,*sys.argv[1:]])
        raise
    main()
