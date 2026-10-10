from playwright.sync_api import sync_playwright
from pathlib import Path
import json, re, urllib.request
ROOT=Path(__file__).resolve().parent.parent
report={}
with sync_playwright() as p:
 browser=p.chromium.launch(channel='chrome',headless=True)
 context=browser.new_context(viewport={'width':1440,'height':1000},device_scale_factor=1)
 page=context.new_page(); errors=[]; bad=[]
 page.on('pageerror',lambda e:errors.append(str(e)))
 page.on('response',lambda r:bad.append([r.status,r.url]) if r.status>=400 else None)
 page.goto('http://localhost:4173',wait_until='networkidle')
 page.add_style_tag(content='html{scroll-behavior:auto!important}')
 page.screenshot(path=str(ROOT/'.review/desktop-top.png'))
 report['counts']={'videos':page.locator('video').count(),'tables':page.locator('table').count(),'result_prompts':page.locator('.result .prompt').count()}
 page.locator('#results').evaluate('(e)=>e.scrollIntoView({block:"start",behavior:"instant"})'); page.wait_for_timeout(1400)
 page.screenshot(path=str(ROOT/'.review/desktop-results.png'))
 first=page.locator('.result video').first
 page.wait_for_function('document.querySelector(".result video").currentTime > 0.2')
 report['playback']=first.evaluate('(v)=>({time:v.currentTime,paused:v.paused,width:v.videoWidth})')
 first.evaluate('(v)=>v.pause()');page.wait_for_timeout(100)
 page.locator('#method').evaluate('(e)=>e.scrollIntoView({block:"start",behavior:"instant"})');page.wait_for_timeout(100)
 page.locator('#results').evaluate('(e)=>e.scrollIntoView({block:"start",behavior:"instant"})');page.wait_for_timeout(700)
 report['resume_on_reentry']=first.evaluate('(v)=>!v.paused')
 for selector,label in [('#comparison','desktop-comparison'),('#backbones','desktop-backbones')]:
  page.locator(selector).evaluate('(e)=>e.scrollIntoView({block:"start",behavior:"instant"})');page.wait_for_timeout(1000);page.screenshot(path=str(ROOT/f'.review/{label}.png'))
 page.emulate_media(reduced_motion='reduce')
 report['media']=page.evaluate('''async()=>{const out=[];for(const v of document.querySelectorAll('video')){v.preload='auto';if(v.readyState<2){await new Promise(resolve=>{const timer=setTimeout(resolve,20000);v.addEventListener('loadeddata',()=>{clearTimeout(timer);resolve()},{once:true});v.load()})}out.push({label:v.getAttribute('aria-label'),width:v.videoWidth,error:v.error?.message||null});v.pause()}return out}''')
 report['images']=page.evaluate('''()=>[...document.images].map(i=>({src:i.getAttribute('src'),ok:i.complete&&i.naturalWidth>0}))''')
 report['desktop_overflow']=page.evaluate('document.documentElement.scrollWidth>innerWidth')
 mobile=browser.new_context(viewport={'width':390,'height':844},is_mobile=True,has_touch=True,reduced_motion='reduce')
 m=mobile.new_page();m.goto('http://localhost:4173',wait_until='networkidle');m.screenshot(path=str(ROOT/'.review/mobile-top.png'))
 for selector,label in [('#results','mobile-results'),('#comparison','mobile-comparison'),('#backbones','mobile-backbones')]:
  m.locator(selector).evaluate('(e)=>e.scrollIntoView({block:"start",behavior:"instant"})');m.wait_for_timeout(300);m.screenshot(path=str(ROOT/f'.review/{label}.png'))
 report['mobile_overflow']=m.evaluate('document.documentElement.scrollWidth>innerWidth')
 m.wait_for_function('[...document.querySelectorAll("video")].some(v=>!v.paused)')
 report['reference_autoplay']=m.locator('video').evaluate_all('(vs)=>vs.some(v=>!v.paused)')
 report['mobile_table_scroll']=m.locator('.table-scroll').first.evaluate('(e)=>e.scrollWidth>e.clientWidth')
 m.set_viewport_size({'width':320,'height':740});report['small_mobile_overflow']=m.evaluate('document.documentElement.scrollWidth>innerWidth')
 report['console_errors']=errors;report['http_errors']=bad
 browser.close()
req=urllib.request.Request('http://localhost:4173/assets/videos/autumn-valley.mp4',headers={'Range':'bytes=100-199'})
with urllib.request.urlopen(req) as r:report['range_request']={'status':r.status,'length':len(r.read()),'range':r.headers['Content-Range']}
(ROOT/'.review/browser-report.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
print(json.dumps(report,indent=2))
assert not report['console_errors'] and not report['http_errors']
assert all(v['width']>0 and not v['error'] for v in report['media'])
assert report['resume_on_reentry'] and report['reference_autoplay']
assert report['playback']['time'] > 0.2 and not report['playback']['paused']
assert not report['mobile_overflow'] and not report['small_mobile_overflow'] and not report['desktop_overflow']
