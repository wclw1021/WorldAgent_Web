from pathlib import Path
import zipfile, json, shutil, subprocess, concurrent.futures, fitz
from PIL import Image
ROOT=Path(__file__).resolve().parent.parent
SOURCE=Path(r'D:\Dropbox\Agent-simulation\supp_video\source')
PAPER=Path(r'D:\Agentic-Simulation-iclr-2027')
PPT=Path(r'C:\Users\Admin\Downloads\ToDesk\WorldAgent.pptx')
slides=json.loads((ROOT/'.review/slides.json').read_text(encoding='utf-8'))
def prompt(n):
 return ' '.join(' '.join(slides[n-1]['text']).split()).split('Prompt:',1)[1].strip()
def pdf_prompts(name):
 with fitz.open(PAPER/'figures'/f'{name}.pdf') as doc: text=doc[0].get_text()
 return [' '.join(x.split()) for x in text.split('\nA ') if x.strip()]
more=pdf_prompts('More_main'); more=[s if s.startswith('A ') else 'A '+s for s in more]
coast=' '.join((ROOT/'.review/More_comparison_model.txt').read_text(encoding='utf-8').split('A cinematic',1)[1].split()); coast='A cinematic '+coast
forest=more[2]
results=[
 ('autumn-valley','Autumn valley', 'main_results/astra_7/astra_7.mp4',prompt(13)),
 ('mountain-river','Mountain river','main_results/case10_flow_bank_v05/case10_flow_bank_v05.mp4',prompt(14)),
 ('river-detail','River dynamics','main_results/case10_flow_v04/case10_flow_v04.mp4',prompt(15)),
 ('forest-stream','Forest stream','main_results/case07_forest_stream/case07_result.mp4',forest),
 ('earthquake','Earthquake in a public building','main_results/earthquake_teaching_building/earthquake_teaching_building.mp4',prompt(16)),
 ('castle','Castle bombardment','main_results/case08_castle_bombardment/case08_result.mp4',prompt(17)),
 ('shining','The Shining',None,prompt(18)),
 ('subway','Subway flooding','main_results/astra_9/astra_9.mp4',more[1]),
 ('waterfall','Canyon waterfall','main_results/astra_1/astra_1.mp4',more[0]),
 ('restaurant','Earthquake in a restaurant','main_results/dining_house/06_dining_house_final.mp4',more[3]),
 ('coast','Coastal waves','main_results/big_wave.mp4',coast),
]
jobs=[]
with zipfile.ZipFile(PPT) as z:
 for num,name in [(14,'shining'),(18,'baseline-swe'),(19,'baseline-blender'),(17,'baseline-viga'),(16,'baseline-code2worlds'),(15,'baseline-gpt'),(20,'baseline-ours')]:
  target=ROOT/'.review'/f'{name}-source.mp4'
  if not target.exists():
   with z.open(f'ppt/media/media{num}.mp4') as src,target.open('wb') as dst:shutil.copyfileobj(src,dst)
  if name!='shining':jobs.append((name,target,1280))
for slug,title,path,p in results:jobs.append((slug,SOURCE/path if path else ROOT/'.review/shining-source.mp4',1920))
backbones=[('gpt-sol','GPT-5.6 Sol','GPT-5.6_Sol.mp4','Ours_GPT-5.6_Sol.mp4'),('gpt-astra','GPT-6 Astra','GPT-6_Astra.mp4','Ours_GPT_6.mp4'),('opus','Opus 5','Opus_5.mp4','Ours_Opus_5.mp4')]
for slug,title,base,ours in backbones:
 jobs.append(('backbone-'+slug,SOURCE/'comparison/coastal'/base,1280))
 if slug!='gpt-astra':jobs.append(('ours-'+slug,SOURCE/'comparison/coastal'/ours,1280))
for font in ['linux-biolinum-regular.ttf','linux-biolinum-bold.ttf']:shutil.copy2(Path(r'D:\WorldParticle_Web\assets\fonts')/font,ROOT/'assets/fonts'/font)
with fitz.open(PAPER/'figures/MethodVerification.pdf') as doc:
 pix=doc[0].get_pixmap(matrix=fitz.Matrix(1,1));Image.frombytes('RGB',[pix.width,pix.height],pix.samples).save(ROOT/'assets/images/method.webp',quality=94)
content={'results':[dict(id=s,title=t,prompt=p) for s,t,_,p in results], 'forestPrompt':forest,'coastPrompt':coast,'backbones':[dict(id=s,title=t,baseline='backbone-'+s,ours='coast' if s=='gpt-astra' else 'ours-'+s) for s,t,_,_ in backbones]}
(ROOT/'content.json').write_text(json.dumps(content,ensure_ascii=False,indent=2),encoding='utf-8')
def encode(job):
 name,source,width=job;target=ROOT/'assets/videos'/f'{name}.mp4'
 if not target.exists():
  subprocess.run(['ffmpeg','-v','error','-i',str(source),'-map','0:v:0','-an','-vf',f'scale=min({width}\\,iw):-2','-c:v','libx264','-threads','3','-preset','fast','-crf','23','-pix_fmt','yuv420p','-movflags','+faststart','-y',str(target)],check=True)
 poster=ROOT/'assets/images'/f'{name}.webp'
 subprocess.run(['ffmpeg','-v','error','-ss','1','-i',str(target),'-frames:v','1','-vf','scale=960:-1','-y',str(poster)],check=True)
 print(name,round(target.stat().st_size/1e6,1),'MB',flush=True)
with concurrent.futures.ThreadPoolExecutor(max_workers=3) as pool:list(pool.map(encode,jobs))
