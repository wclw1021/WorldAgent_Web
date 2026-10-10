"""Build the standalone page from editable content.json. No dependencies required."""
from pathlib import Path
import json
from html import escape

ROOT = Path(__file__).resolve().parent.parent
data = json.loads((ROOT / 'content.json').read_text(encoding='utf-8'))
paper_url = data.get('paperUrl', '')
paper_icon = '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8Z"/><path d="M14 2v6h6M8 13h8M8 17h6"/></svg>'
code_icon = '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M9 19c-4.3 1.3-4.3-2.2-6-2.7m12 6v-3.9a3.4 3.4 0 0 0-.9-2.7c3-.3 6.2-1.5 6.2-6.9a5.4 5.4 0 0 0-1.5-3.8A5 5 0 0 0 18.7 1S17.5.6 14.8 2.5a13.3 13.3 0 0 0-7 0C5.1.6 3.9 1 3.9 1a5 5 0 0 0-.1 4A5.4 5.4 0 0 0 2.3 8.8c0 5.4 3.2 6.6 6.2 6.9a3.4 3.4 0 0 0-.9 2.7v3.9"/></svg>'

def paper_link(classes):
    label = paper_icon + '<span>Paper</span>'
    if paper_url:
        return f'<a class="{classes}" href="{escape(paper_url, quote=True)}" target="_blank" rel="noopener noreferrer">{label}</a>'
    return f'<button class="{classes}" type="button" disabled aria-label="Paper — link coming soon">{label}</button>'

def video(slug, title):
    return f'''<div class="video-frame"><video class="auto-video" controls muted loop playsinline preload="none" poster="assets/images/{slug}.webp" aria-label="{escape(title)}"><source src="assets/videos/{slug}.mp4" type="video/mp4"></video><p class="video-error" hidden>Video could not be loaded. <a href="assets/videos/{slug}.mp4">Open video</a></p></div>'''

def prompt(text):
    return f'<p class="prompt"><span>Prompt</span> {escape(text)}</p>'

def result(item):
    wide = ' result-wide' if item['id'] == 'shining' else ''
    return f'''<figure class="result{wide}">{video(item['id'],item['title'])}<figcaption>{prompt(item['prompt'])}</figcaption></figure>'''

# Author order, affiliations, and contribution markers follow main_arxiv.tex.
authors = [
    ('Caoliwen Wang', '1,*'), ('Mengdi Wang', '1,*,†'), ('Yige Chen', '2,*,§'),
    ('Zejia Wu', '3'), ('Bowen Huang', '3'), ('Siyuan Chen', '1'),
    ('Guanxiong Chen', '1'), ('Lifu Wei', '1'), ('Heng Zhang', '1'),
    ('Qinghai Zhang', '3'), ('Yin Yang', '4'), ('Guandao Yang', '5'),
    ('Shiying Xiong', '3'), ('Peng Wang', '2'), ('Chenfanfu Jiang', '6'),
    ('Peter Yichen Chen', '1,†'),
]
affiliations = ['University of British Columbia', 'VAST', 'Zhejiang University',
                'University of Utah', 'The University of Texas at Austin',
                'University of California, Los Angeles']
author_html = ''.join(f'<span>{name}<sup>{marks}</sup></span>' for name, marks in authors)
affiliation_html = ''.join(f'<span><sup>{i}</sup> {name}</span>' for i, name in enumerate(affiliations, 1))
results = sorted(data['results'], key=lambda item: item['id'] == 'shining')

baseline = [
    ['SWE-Agent', '.3005', '.2862', '.5436', '.9423', '16.2615', '.5635', '.7715'],
    ['Blender MCP', '.9007', '.3223', '.5487', '.9038', '15.6957', '.6730', '.7103'],
    ['VIGA', '.1338', '.3152', '.4859', '.7500', '16.0059', '.6739', '.7713'],
    ['Code2Worlds', '.1148', '.0656', '.5051', '.5577', '15.1408', '.5546', '.6587'],
    ['Ours (GPT-5.6 Sol)', '.0613', '.4081', '.5962', '1.0000', '16.1757', '.6707', '.7866'],
    ['Wan 2.2', '—', '.4692', '.5795', '.9615', '15.2647', '.7070', '.9310'],
    ['MiniMax H3', '—', '.5408', '.5256', '.9615', '16.6525', '.7011', '.9220'],
    ['Ours (GPT-6 Astra)', '.0415', '.6825', '.6042', '1.0000', '16.1225', '.7129', '.8319'],
]
backbone = [
    ['GPT-5.6 Sol', '.6747', '.3004', '.5038', '.7692', '15.6923', '.5836', '.6419'],
    ['GPT-6 Astra', '.2248', '.6031', '.5308', '.9615', '16.2150', '.7296', '.8465'],
    ['Opus 5', '.8316', '.4255', '.5300', '.9500', '17.4162', '.6368', '.8226'],
    baseline[4], baseline[7],
    ['Ours (Opus 5)', '.2038', '.6638', '.6000', '1.0000', '17.6531', '.6505', '.8489'],
]
study = [
    ['GPT-5.6 Sol', '2.226', '2.811', '2.578', '2.293'],
    ['SWE-Agent', '2.503', '3.005', '2.946', '2.692'],
    ['Blender MCP', '2.103', '2.763', '2.724', '2.247'],
    ['VIGA', '2.196', '2.255', '2.560', '2.636'],
    ['Code2Worlds', '2.491', '2.241', '2.203', '2.369'],
    ['Ours (GPT-5.6 Sol)', '3.647', '3.484', '3.469', '3.615'],
]

def table(rows, caption, groups, split=None, user_study=False):
    best = set()
    for start, end in groups:
        for col in range(1, len(rows[0])):
            values = [(float(rows[r][col]), r) for r in range(start, end) if rows[r][col] != '—']
            target = (min if col == 1 and not user_study else max)(v for v, _ in values)
            best.update((r, col) for v, r in values if v == target)
    body = ''
    for r, row in enumerate(rows):
        cls = ('ours ' if row[0].startswith('Ours') else '') + ('group-start' if r == split else '')
        body += f'<tr class="{cls}"><th scope="row">{row[0]}</th>'
        for col, value in enumerate(row[1:], 1):
            value = '0' + value if value.startswith('.') else value
            body += '<td>' + (f'<strong class="best">{value}</strong>' if (r, col) in best else value) + '</td>'
        body += '</tr>'
    if user_study:
        head = '<tr><th scope="col">Method</th>' + ''.join(f'<th scope="col">{x} ↑</th>' for x in ['Physical plausibility', 'Shot planning', 'Content alignment', 'Aesthetics']) + '</tr>'
    else:
        head = '''<tr><th rowspan="2" scope="col">Method / Metric</th><th colspan="2" scope="colgroup">Physical plausibility</th><th scope="col">Shot planning</th><th colspan="2" scope="colgroup">Content alignment</th><th colspan="2" scope="colgroup">Aesthetics</th></tr><tr>'''
        metrics = [('Pen. ↓', 'Normalized maximum penetration'), ('Caus. ↑', 'Causal beat completion'), ('Qual. ↑', 'Shot planning quality'), ('Comp. ↑', 'Scene composition completeness'), ('Align. ↑', 'Semantic alignment'), ('Imag. ↑', 'Imaging quality'), ('Prod. ↑', 'Production quality')]
        head += ''.join(f'<th scope="col"><abbr title="{full}">{short}</abbr></th>' for short, full in metrics) + '</tr>'
    return f'<div class="table-scroll" tabindex="0" role="region" aria-label="{caption}"><table><caption class="sr-only">{caption}</caption><thead>{head}</thead><tbody>{body}</tbody></table></div>'

baseline_videos = ''.join(f'<figure class="comparison-video{ " ours-video" if slug == "baseline-ours" else ""}">{video(slug,title)}<figcaption>{title}</figcaption></figure>' for slug, title in [('baseline-swe','SWE-Agent'),('baseline-blender','Blender MCP'),('baseline-viga','VIGA'),('baseline-code2worlds','Code2Worlds'),('baseline-gpt','GPT-5.6 Sol'),('baseline-ours','Ours (GPT-5.6 Sol)')])
backbone_videos = ''.join(f'''<div class="backbone-column"><h4>{item['title']}</h4><figure class="comparison-video">{video(item['baseline'],item['title']+' — direct prompting')}<figcaption>Direct prompting</figcaption></figure><figure class="comparison-video ours-video">{video(item['ours'],'WorldAgent with '+item['title'])}<figcaption>WorldAgent (Ours)</figcaption></figure></div>''' for item in data['backbones'])

html = f'''<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <meta name="description" content="WorldAgent: verification-guided physical world construction from a single natural-language prompt. Method, simulation results, and comparisons.">
  <meta name="theme-color" content="#ffffff">
  <title>WorldAgent | Physical World Construction</title>
  <link rel="icon" href="assets/favicon.svg" type="image/svg+xml">
  <link rel="preload" href="assets/fonts/linux-biolinum-regular.ttf" as="font" type="font/ttf" crossorigin>
  <link rel="stylesheet" href="styles.css">
  <script src="script.js" defer></script>
</head>
<body>
  <a class="skip-link" href="#method">Skip to content</a>
  <nav class="site-nav" aria-label="Primary navigation"><a class="wordmark" href="#top">WorldAgent</a><div class="nav-links"><a href="#method">Method</a><a href="#results">Results</a><a href="#comparison">Comparison</a></div><div class="nav-actions">{paper_link('nav-resource')}</div></nav>
  <main id="top">
    <header class="hero content-width">
      <h1>WorldAgent</h1>
      <p class="hero-subtitle">Verification-Guided Agentic<br>Physical World Construction</p>
      <div class="authors">{author_html}</div>
      <div class="affiliations">{affiliation_html}</div>
      <div class="contributions"><span><sup>*</sup> Equal contribution</span><span><sup>†</sup> Corresponding authors</span><span><sup>§</sup> Work done during internship at VAST</span></div>
      <div class="hero-actions" aria-label="Project links">{paper_link('button button-primary')}<button class="button button-secondary" type="button" disabled>{code_icon}<span>Code (coming soon)</span></button></div>
    </header>
    <section class="section method-section" id="method"><div class="content-width">
      <div class="section-heading"><h2>Method</h2></div>
      <div class="method-layout">
        <figure class="method-figure"><a href="assets/images/method.webp" target="_blank" rel="noopener" aria-label="Open the WorldAgent method figure at full resolution"><img src="assets/images/method.webp" width="1560" height="1554" alt="WorldAgent framework: a world construction layer uses structured specifications and skill-guided execution, while a verification layer checks static scenes and simulations in a feedback loop."></a></figure>
        <p class="method-caption">WorldAgent builds and simulates physical worlds from a single prompt, using geometric, visual, and simulation checks to guide automatic refinement.</p>
      </div>
    </div></section>
    <section class="section results-section" id="results"><div class="content-width">
      <div class="section-heading"><h2>Results</h2></div>
      <div class="results-grid">{''.join(result(item) for item in results)}</div>
    </div></section>
    <section class="section comparison-section" id="comparison"><div class="content-width">
      <div class="section-heading"><h2>Comparison</h2></div>
      <div class="comparison-block" id="baselines">
        <h3 class="subsection-title">Baseline comparisons</h3>
        <div class="comparison-grid">{baseline_videos}</div>
        {prompt(data['forestPrompt'])}
        <div class="table-heading"><h4>AgenticSimBench</h4><p>13 prompts · Green indicates best.</p></div>
        {table(baseline, 'Baseline comparison scores on AgenticSimBench', [(0,5),(5,8)],split=5)}
        <p class="table-note">Top: GPT-5.6 Sol agents. Bottom: video models vs. WorldAgent (GPT-6 Astra).</p>
        <div class="table-heading"><h4>User study</h4><p>26 participants · Ratings from 1 to 5.</p></div>
        {table(study,'User study mean ratings',[(0,6)],user_study=True)}
      </div>
      <div class="comparison-block backbone-block" id="backbones">
        <h3 class="subsection-title">Language model backbone</h3>
        <div class="backbone-grid">{backbone_videos}</div>
        {prompt(data['coastPrompt'])}
        <div class="table-heading"><h4>Backbone comparison</h4></div>
        {table(backbone,'Language model backbone comparison scores',[(0,6)],split=3)}
      </div>
    </div></section>
  </main>
  <footer class="content-width"><span>WorldAgent</span><a href="#top">Back to top ↑</a></footer>
</body>
</html>
'''
(ROOT / 'index.html').write_text(html, encoding='utf-8')
print('Built index.html: 11 results, 12 comparison videos, 3 tables.')
