from pathlib import Path
import zipfile, xml.etree.ElementTree as ET, json, re
ppt=Path(r'C:\Users\Admin\Downloads\ToDesk\WorldAgent.pptx')
ns={'a':'http://schemas.openxmlformats.org/drawingml/2006/main'}
with zipfile.ZipFile(ppt) as z:
    names=sorted([n for n in z.namelist() if re.match(r'ppt/slides/slide\d+\.xml$',n)],key=lambda s:int(re.search(r'(\d+)\.xml',s)[1]))
    rows=[]
    for n in names:
        root=ET.fromstring(z.read(n))
        texts=[t.text for t in root.findall('.//a:t',ns)]
        rows.append({'slide':n,'text':texts})
    Path('.review/slides.json').write_text(json.dumps(rows,indent=2,ensure_ascii=False),encoding='utf-8')
    for row in rows:
        print(row['slide'], '\n', '\n'.join(row['text']), '\n')
