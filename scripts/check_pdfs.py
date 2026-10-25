#!/usr/bin/env python3
"""Render every generated page and record structural and layout checks."""
from pathlib import Path
import concurrent.futures,hashlib,json,re,subprocess,sys,xml.etree.ElementTree as ET
from PIL import Image,ImageDraw
from pypdf import PdfReader

ROOT=Path(__file__).resolve().parents[1]
WORK=ROOT/'output/pdf/production'
BIN=Path.home()/'.cache/codex-runtimes/codex-primary-runtime/dependencies/native/poppler/poppler/bin'
MANIFEST=json.loads((WORK/'manifest.json').read_text())
QA=WORK/'qa';QA.mkdir(exist_ok=True)
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def check(m):
    pdf=ROOT/m['output'];folder=QA/'pages'/m['id'];folder.mkdir(parents=True,exist_ok=True)
    reader=PdfReader(pdf);pages=len(reader.pages)
    assert pages==m['pages'] and sha(ROOT/m['source'])==m['sha256'],m['source']
    assert all(sha(ROOT/p)==v for p,v in m['dependencies'].items()),m['source']
    assert all(p.get('/AmitaiLogoSHA256')==m['logo_sha256'] for p in reader.pages),m['source']
    normalized=(WORK/'documents'/m['id']/'normalized.md').read_text()
    assert re.findall(r'\d+(?:\.\d+)?',(ROOT/m['source']).read_text())==re.findall(r'\d+(?:\.\d+)?',normalized),m['source']
    fonts=subprocess.run([str(BIN/'pdffonts'),str(pdf)],capture_output=True,text=True,check=True).stdout
    (folder/'fonts.txt').write_text(fonts)
    # All rows have type columns of variable length, but the trailing flags are fixed.
    unembedded=[line for line in fonts.splitlines()[2:] if len(line.split())>=8 and line.split()[-5]!='yes']
    bbox=subprocess.run([str(BIN/'pdftotext'),'-bbox-layout',str(pdf),'-'],capture_output=True,text=True,check=True).stdout
    xml=ET.fromstring(bbox);ns={'p':'http://www.w3.org/1999/xhtml'};bounds=[];wordcounts=[]
    for n,p in enumerate(xml.findall('.//p:page',ns),1):
        words=p.findall('.//p:word',ns);wordcounts.append(len(words))
        for w in words:
            in_body=70<float(w.attrib['yMin']) and float(w.attrib['yMax'])<805
            if (in_body and (float(w.attrib['xMin'])<42 or float(w.attrib['xMax'])>554)) or float(w.attrib['yMin'])<5 or float(w.attrib['yMax'])>837:
                bounds.append({'page':n,'text':w.text,'bbox':w.attrib})
    for old in folder.glob('page-*.png'):old.unlink()
    subprocess.run([str(BIN/'pdftoppm'),'-scale-to','1100','-png',str(pdf),str(folder/'page')],capture_output=True,check=True)
    images=sorted(folder.glob('page-*.png'),key=lambda p:int(p.stem.split('-')[-1]));assert len(images)==pages
    logo_pixels=[];body_pixels=[]
    for p in images:
        im=Image.open(p).convert('RGB');w,h=im.size
        crop=im.crop((round(w*167/210),round(h*6/297),round(w*193/210),round(h*25/297)))
        count=sum(1 for r,g,b in crop.getdata() if min(r,g,b)<180 and max(r,g,b)-min(r,g,b)>25)
        logo_pixels.append(count)
        crop=im.crop((round(w*17/210),round(h*29/297),round(w*193/210),round(h*280/297))).convert('L')
        body_pixels.append(sum(c<180 for c in crop.getdata()))
    assert min(logo_pixels)>100,(m['source'],logo_pixels)
    return {'source':m['source'],'id':m['id'],'chapter':m['chapter'],'pages':pages,'source_unchanged':True,'assets_unchanged':True,'numbers_preserved':True,'logo_every_page':True,'logo_pixels':logo_pixels,'body_pixels':body_pixels,'wordcounts':wordcounts,'unembedded_fonts':unembedded,'bounds':bounds,'images':[str(p.relative_to(ROOT)) for p in images]}

selected=MANIFEST
results=[]
if '--changed' in sys.argv:
    ids={m['id'] for m in json.loads((WORK/'pending.json').read_text())}
    selected=[m for m in MANIFEST if m['id'] in ids]
    results=[r for r in json.loads((QA/'verification.json').read_text()) if r['id'] not in ids]
with concurrent.futures.ThreadPoolExecutor(max_workers=4) as pool:
    jobs={pool.submit(check,m):m for m in selected}
    for f in concurrent.futures.as_completed(jobs):
        m=jobs[f]
        try:r=f.result();results.append(r);print(f'{len(results)}/{len(MANIFEST)} {m["id"]}: {r["pages"]} pages',flush=True)
        except Exception as e:print(m['source'],str(e),flush=True);raise
order={m['id']:i for i,m in enumerate(MANIFEST)};results.sort(key=lambda r:order[r['id']])
(QA/'verification.json').write_text(json.dumps(results,ensure_ascii=False,indent=2))
# A contact-sheet inventory contains each final page exactly once.
allpages=[{'source':r['source'],'id':r['id'],'page':n,'image':p,'chapter':r['chapter']} for r in results for n,p in enumerate(r['images'],1)]
sheetdir=QA/'contact-sheets';sheetdir.mkdir(exist_ok=True);sheets=[]
for old in sheetdir.glob('review-*.jpg'):old.unlink()
for start in range(0,len(allpages),20):
    group=allpages[start:start+20];sheet=Image.new('RGB',(1500,1816),'#dce5e7');draw=ImageDraw.Draw(sheet)
    for i,p in enumerate(group):
        im=Image.open(ROOT/p['image']).convert('RGB');im.thumbnail((292,414));x=(i%5)*300+4;y=(i//5)*454+30
        sheet.paste(im,(x,y));draw.text((x,y-22),f'{order[p["id"]]+1:03d} ch{p["chapter"]} p{p["page"]}',fill='black')
    target=sheetdir/f'review-{start//20+1:03d}.jpg';sheet.save(target,quality=86)
    sheets.append({'sheet':str(target.relative_to(ROOT)),'pages':group})
(QA/'visual-inventory.json').write_text(json.dumps(sheets,ensure_ascii=False,indent=2))
print(json.dumps({'pdfs':len(results),'pages':len(allpages),'sheets':len(sheets),'bounds':sum(len(r['bounds']) for r in results),'unembedded':sum(len(r['unembedded_fonts']) for r in results)}))
