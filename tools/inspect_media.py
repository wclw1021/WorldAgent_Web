from pathlib import Path
import zipfile,xml.etree.ElementTree as ET,json
from PIL import Image,ImageOps,ImageDraw
import fitz,subprocess
ns={'a':'http://schemas.openxmlformats.org/drawingml/2006/main','p':'http://schemas.openxmlformats.org/presentationml/2006/main','r':'http://schemas.openxmlformats.org/officeDocument/2006/relationships'}
with zipfile.ZipFile(r'C:\Users\Admin\Downloads\ToDesk\WorldAgent.pptx') as z:
 for i in [12,13,14,15,16,17,18,19,20,21,22]:
  root=ET.fromstring(z.read(f'ppt/slides/slide{i}.xml'))
  rels=ET.fromstring(z.read(f'ppt/slides/_rels/slide{i}.xml.rels'))
  rm={r.attrib['Id']:r.attrib['Target'] for r in rels}
  print('SLIDE',i)
  for pic in root.findall('.//p:pic',ns):
   print(ET.tostring(pic,encoding='unicode')[:250],[(k,v) for k,v in rm.items() if k in ET.tostring(pic,encoding='unicode')])
  for k,v in rm.items():
   if 'media/' in v:
    name='ppt/'+v.replace('../',''); info=z.getinfo(name)
    print(k,v,round(info.file_size/1024/1024,2),'MB')
    if i in [20,22] and name.lower().endswith(('.png','.jpg','.jpeg')):
     target=Path('.review')/f'slide{i}-{Path(name).name}';target.write_bytes(z.read(name))
for name in ['Pipeline','MethodVerification','Main','More_main','Comparison','More_comparison_model']:
 doc=fitz.open(str(Path(r'D:\Agentic-Simulation-iclr-2027\figures') / (name+'.pdf')));page=doc[0]
 page.get_pixmap(matrix=fitz.Matrix(1.5,1.5)).save('.review/'+name+'.png')
 Path('.review/'+name+'.txt').write_text(page.get_text(),encoding='utf-8')
files=list(Path(r'D:\Dropbox\Agent-simulation\supp_video\source').rglob('*.mp4'))
thumbs=[]
for i,f in enumerate(files):
 data=json.loads(subprocess.check_output(['ffprobe','-v','quiet','-show_format','-show_streams','-of','json',str(f)]))
 st=next(s for s in data['streams'] if s['codec_type']=='video')
 print(str(f.relative_to(Path(r'D:\Dropbox\Agent-simulation\supp_video\source'))),st['width'],st['height'],data['format']['duration'],round(f.stat().st_size/1e6))
 out=Path('.review')/f'video{i}.jpg'
 subprocess.run(['ffmpeg','-v','error','-ss','3','-i',str(f),'-frames:v','1','-vf','scale=384:-1','-y',str(out)],check=True)
 im=Image.open(out).convert('RGB');tile=Image.new('RGB',(400,256),'white');tile.paste(ImageOps.contain(im,(400,222)),(0,0));ImageDraw.Draw(tile).text((8,228),f.stem,fill='black');thumbs.append(tile)
contact=Image.new('RGB',(1200,256*((len(thumbs)+2)//3)), '#eee')
for i,t in enumerate(thumbs):contact.paste(t,((i%3)*400,(i//3)*256))
contact.save('.review/video-contact.jpg')
