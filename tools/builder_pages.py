"""Páginas del generador de discos de Tiger Road (Saturn y Dreamcast): de momento, vista previa sin funcionar y sin enlaces.
Se generan desde tools/build.py con la cabecera de la web (misma versión del CSS)."""
import pathlib


def _top(root):
    src = (root / 'projects/tiger-road/index.html').read_text()
    head_end = src.index('</header>') + len('</header>')
    return src[:head_end].replace('aria-current="page"', '')

CSS = """
<style>
.bld { display:flex; flex-direction:column; gap:32px; }
.bld-hero { display:grid; grid-template-columns: 1fr; gap:20px; }
.bld-hero img { width:100%; height:auto; image-rendering:auto; border:1px solid var(--line); }
.bld h1 { font-size:28px; line-height:1.2; margin:0; color:var(--ink); font-weight:600; }
.bld .kicker { font-family:var(--mono); font-size:13px; color:var(--muted); margin:0 0 6px; }
.bld p { margin:0; color:var(--text); }
.bld .lead { font-size:17px; }
.step { background:var(--surface); border:1px solid var(--line); padding:20px; display:flex; flex-direction:column; gap:14px; }
.step h2 { font-size:15px; margin:0; font-family:var(--mono); font-weight:500; color:var(--ink); display:flex; gap:10px; align-items:baseline; }
.step h2 .n { color:var(--accent); }
.step.off { opacity:.5; }
.drop { border:1.5px dashed var(--chip); padding:22px; text-align:center; font-size:15px; color:var(--soft); }
.drop b { color:var(--accent); font-weight:500; }
.files { list-style:none; margin:0; padding:0; font-family:var(--mono); font-size:13px; display:flex; flex-direction:column; gap:6px; }
.files li { display:flex; justify-content:space-between; gap:12px; flex-wrap:wrap; padding:8px 10px; background:var(--bg); }
.ok { color:#1F7A3A; } .opt { color:var(--muted); } .bad { color:#B3261E; }
.opts { display:flex; flex-direction:column; gap:8px; font-size:15px; }
.opts label { display:flex; gap:10px; align-items:flex-start; }
.opts small { display:block; color:var(--muted); font-size:13px; }
.btn { align-self:flex-start; font:500 15px var(--sans); background:var(--accent); color:#fff; border:0; padding:10px 18px; cursor:pointer; }
.btn[disabled] { background:var(--chip); color:var(--muted); cursor:default; }
.note { font-size:14px; color:var(--soft); background:var(--code-bg); padding:10px 12px; }
.bar { height:8px; background:var(--code-bg); }
.bar span { display:block; height:100%; background:var(--accent); }
.stages { list-style:none; margin:0; padding:0; font-family:var(--mono); font-size:13px; display:flex; flex-direction:column; gap:4px; color:var(--muted); }
.stages .done { color:var(--text); } .stages .now { color:var(--accent); }
.faq { display:flex; flex-direction:column; gap:14px; font-size:15px; }
.faq h3 { font-size:15px; margin:0 0 4px; color:var(--ink); }
.mock { font-family:var(--mono); font-size:12px; color:#8A5A00; background:#FFF3D6; padding:6px 10px; align-self:flex-start; }
@media (min-width: 720px) { .bld-hero { grid-template-columns: 1fr 1fr; align-items:center; } }
</style>
"""

def page(top, cfg, state):
    files_ok = state != 'start'
    building = state == 'building'
    done = state == 'done'
    rom_rows = []
    for name, need, desc in cfg['roms']:
        if files_ok:
            st = '<span class="ok">✓ verified</span>' if need or state!='start' else ''
            if not need and cfg.get('opt_missing') and state=='ready':
                st = '<span class="opt">not added · optional</span>'
        else:
            st = '<span class="opt">required</span>' if need else '<span class="opt">optional</span>'
        rom_rows.append(f'<li><span>{name} <span class="opt">· {desc}</span></span>{st}</li>')
    opts = ''.join(f'<label><input type="radio" name="fmt" {"checked" if i==0 else ""}><span>{a}<small>{b}</small></span></label>' for i,(a,b) in enumerate(cfg['formats']))
    stage_list = cfg['stages']
    if building:
        k = 2
        st_html = ''.join(f'<li class="{"done" if i<k else "now" if i==k else ""}">{"✓" if i<k else "›" if i==k else "·"} {s}</li>' for i,s in enumerate(stage_list))
        prog = f'<div class="bar"><span style="width:46%"></span></div><ul class="stages">{st_html}</ul><p class="note">Keep this tab open. Generating the music takes two or three minutes.</p>'
        btn = '<button class="btn" disabled>Building…</button>'
    elif done:
        st_html = ''.join(f'<li class="done">✓ {s}</li>' for s in stage_list)
        prog = f'<div class="bar"><span style="width:100%"></span></div><ul class="stages">{st_html}</ul>'
        btn = f'<button class="btn">Download {cfg["outname"]}</button><p class="note">{cfg["after"]}</p>'
    else:
        prog = ''
        btn = f'<button class="btn" {"" if files_ok else "disabled"}>Build disc image</button>'
    drop = ('<div class="drop">Drop your ROM files here or <b>choose files</b></div>' if not files_ok else
            '<div class="drop">Files added · <b>choose again</b></div>')
    body = f'''
<main id="main" class="bld">
<a class="back" href="/projects/tiger-road/">← Tiger Road</a>
<span class="mock">PREVIEW · not working yet</span>
<div class="bld-hero">
<div>
<p class="kicker">disc builder · {cfg["ver"]}</p>
<h1>Build your own Tiger Road disc for the {cfg["console"]}</h1>
</div>
<img src="{cfg["img"]}" alt="{cfg["alt"]}" width="{cfg["w"]}" height="{cfg["h"]}">
</div>
<p class="lead">I can't share Capcom's ROMs, so there's no disc to download. This page builds the {cfg["console"]} disc image from the arcade ROM set you own. Everything happens in your browser: your files are never uploaded anywhere.</p>
<section class="step">
<h2><span class="n">1</span> Add your arcade ROMs</h2>
<p>Both MAME ROM sets are needed, as .zip files: split (two files) or merged (toramich inside tigeroad.zip). Every file is checked against its expected size and checksum.</p>
{drop}
<ul class="files">{"".join(rom_rows)}</ul>
</section>
<section class="step{"" if files_ok else " off"}">
<h2><span class="n">2</span> Format</h2>
<div class="opts">{opts}</div>
</section>
<section class="step{"" if files_ok else " off"}">
<h2><span class="n">3</span> Build</h2>
<p class="note">The music on the disc is played from CD audio tracks. They can't be shared either, so your browser recreates them by emulating the arcade's two YM2203 sound chips, channel by channel, and mixing them in stereo. This takes two or three minutes on a recent computer.</p>
{btn}
{prog}
</section>
<section class="faq">
<h3 style="font-size:17px">Questions</h3>
<div><h3>Where do I get the ROMs?</h3><p>From your own arcade board or a set you legally own. I can't help with that.</p></div>
<div><h3>What do I need to play it?</h3><p>{cfg["play"]}</p></div>
<div><h3>Credits</h3><p>{cfg["credits"]}</p></div>
<div><h3>Something went wrong</h3><p>If a file doesn't verify, it's probably from another version of the game or a different MAME set. Tell me on <a href="https://x.com/hombreimagina">X</a> which one you have.</p></div>
</section>
</main>
</div>
</body>
</html>
'''
    top = top.replace('<link rel="canonical"', '<meta name="robots" content="noindex">\n<link rel="canonical"')
    return top.replace('<title>Tiger Road · hombreimaginario</title>', f'<title>Disc builder · Tiger Road {cfg["console"]} · hombreimaginario</title>').replace('</head>', CSS + '</head>') + body

ROMS = [('tigeroad.zip', True, 'Tiger Road, World/US'), ('toramich.zip', True, 'Tora-he no Michi, Japan: Japanese text, logo and voices')]
CFG = {
 'ss': dict(console='Saturn', ver='V1.2', img='/img/2026/tiger-road-ss-bezel2.png', alt='Tiger Road on the Saturn with an illustrated bezel on the side bands.', w=320, h=224, roms=ROMS, opt_missing=False,
   formats=[('BIN/CUE','For Saroo, Fenrir and other optical drive emulators, or to burn to a CD-R.')],
   stages=['Checking ROMs','Converting graphics and program','Generating music tracks (23)','Writing disc image'],
   credits='The bezel artwork is by Capcom, taken from the <a href="FUENTE">Capcom wiki</a>.', outname='Tiger Road SS v1-2.zip', after='A .zip with the .cue, the data track and the 23 audio tracks.',
   play='A Saturn with a Saroo, a Fenrir or another drive emulator, or a modded console that runs CD-Rs. It also works in Mednafen.'),
 'dc': dict(console='Dreamcast', ver='V1.2', img='/img/2026/tiger-road-dc-fullscreen.png', alt='Tiger Road on the Dreamcast in full screen.', w=598, h=448, roms=ROMS, opt_missing=False,
   formats=[('GDI','Comes as a folder ready to copy to your GDEMU SD card, and also plays in Flycast.')],
   stages=['Checking ROMs','Building the arcade board image','Generating music tracks (23)','Writing disc image'],
   credits='The cover shown in the GDEMU menu uses artwork by Capcom, taken from the <a href="FUENTE">Capcom wiki</a>.', outname='Tiger Road DC v1-2.zip', after='A .zip with the folder for your GDEMU SD card: disc.gdi and its tracks.',
   play='A Dreamcast with a GDEMU or another drive emulator that loads GDI images, or Flycast. It can\'t be burned to a CD-R.'),
}
def main(root):
    top = _top(root)
    for k, c in CFG.items():
        d = root / 'build' / f'tiger-road-{k}'
        d.mkdir(parents=True, exist_ok=True)
        html = page(top, c, 'start').replace('https://hombreimaginario.com/projects/tiger-road/', f'https://hombreimaginario.com/build/tiger-road-{k}/')
        (d / 'index.html').write_text(html)
