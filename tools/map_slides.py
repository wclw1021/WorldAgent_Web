import zipfile,xml.etree.ElementTree as ET
from pathlib import Path
from PIL import Image
ns={'a':'http://schemas.openxmlformats.org/drawingml/2006/main','p':'http://schemas.openxmlformats.org/presentationml/2006/main','r':'http://schemas.openxmlformats.org/officeDocument/2006/relationships'}
with zipfile.ZipFile(r'C:\Users\Admin\Downloads\ToDesk\WorldAgent.pptx') as z:
 for i in [12,19,21]:
  root=ET.fromstring(z.read(f'ppt/slides/slide{i}.xml'))
  rm={r.attrib['Id']:r.attrib['Target'] for r in ET.fromstring(z.read(f'ppt/slides/_rels/slide{i}.xml.rels'))}
  for shape in root.findall('.//p:sp',ns)+root.findall('.//p:pic',ns):
   texts=''.join(x.text or '' for x in shape.findall('.//a:t',ns))
   off=shape.find('.//a:xfrm/a:off',ns)
   vids=shape.findall('.//a:videoFile',ns)
   if texts or vids:print(i,off.attrib if off is not None else '',texts,[(v.attrib,rm[v.attrib['{'+ns['r']+'}link']]) for v in vids])
  if i==12:
   Path('.review/ppt-method.png').write_bytes(z.read('ppt/media/image28.png'))
