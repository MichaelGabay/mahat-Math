#!/usr/bin/env python3
"""Create the PDF collection's navigation index and distributable archive."""
from pathlib import Path
from urllib.parse import quote
import hashlib,json,re,zipfile
ROOT=Path(__file__).resolve().parents[1];WORK=ROOT/'output/pdf/production'
m=json.loads((WORK/'manifest.json').read_text())
verify=json.loads((WORK/'qa/verification.json').read_text())
assert len(m)==len(verify)==173
def natural(x):return [int(t) if t.isdigit() else t for t in re.split(r'(\d+)',x)]
lines=['# מאגר PDF — אמיתי','',f'{len(m)} קבצים · {sum(x["pages"] for x in m):,} עמודים · לוגו בכל עמוד','',
       'המקורות נשמרו ללא שינוי. לעדכונים ולממצאי מקור ידועים: [הוראות ועדכון](<PDF - הוראות ועדכון.md>).','']
for chapter in range(1,11):
    docs=sorted([x for x in m if x['chapter']==chapter],key=lambda x:natural(Path(x['output']).name))
    folder=Path(docs[0]['output']).parts[0]
    lines.extend([f'## {folder}','',f'{len(docs)} קבצים · {sum(x["pages"] for x in docs)} עמודים',''])
    for x in docs:lines.append(f'- [{Path(x["output"]).stem.replace("_"," ")}](<{x["output"]}>) — {x["pages"]} עמודים')
    lines.append('')
index=ROOT/'PDF - תוכן העניינים.md';index.write_text('\n'.join(lines))
report={'pdfs':len(m),'pages':sum(x['pages'] for x in m),'questions':sum(x['questions'] for x in m),'answers':sum(x['answers'] for x in m),'image_references':sum(x['images'] for x in m),'math_spans':sum(x['math'] for x in m),'all_sources_unchanged':all(x['source_unchanged'] for x in verify),'all_assets_unchanged':all(x['assets_unchanged'] for x in verify),'logo_on_every_page':all(x['logo_every_page'] for x in verify),'numbers_preserved':all(x['numbers_preserved'] for x in verify),'unembedded_fonts':sum(len(x['unembedded_fonts']) for x in verify),'body_boundary_violations':sum(len(x['bounds']) for x in verify),'full_mathematical_revalidation':False}
(WORK/'qa/summary.json').write_text(json.dumps(report,ensure_ascii=False,indent=2))
archive=ROOT/'output/pdf/כל קובצי ה-PDF - אמיתי.zip'
with zipfile.ZipFile(archive,'w',compression=zipfile.ZIP_DEFLATED,compresslevel=6) as z:
    for x in m:
        p=ROOT/x['output'];assert hashlib.sha256(p.read_bytes()).hexdigest()==x['pdf_sha256'];z.write(p,x['output'])
    for p in [index,ROOT/'PDF - הוראות ועדכון.md']:z.write(p,p.name)
    for p in [WORK/'qa/summary.json',WORK/'qa/incremental-checks.json',WORK/'qa/visual-review.json']:
        if p.exists():z.write(p,'בדיקות/'+p.name)
with zipfile.ZipFile(archive) as z:
    assert sum(n.endswith('.pdf') for n in z.namelist())==173
    assert z.testzip() is None
print(json.dumps({**report,'zip_bytes':archive.stat().st_size,'archive':str(archive)},ensure_ascii=False))
