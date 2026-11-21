"""Páginas del generador de discos de Tiger Road (Saturn y Dreamcast). El motor (engine.js, tr-music.wasm) y los datos de las
plantillas están en build/tiger-road/ y salen de los repositorios de los ports (make builder-template); aquí solo el HTML,
con la cabecera de la web. Se llama desde tools/build.py."""
import hashlib
import html
import pathlib

CSS = """
<style>
.bld { display:flex; flex-direction:column; gap:32px; }
.bld-hero { display:grid; grid-template-columns:1fr; gap:20px; }
.bld-hero img { width:100%; height:auto; border:1px solid var(--line); }
.bld h1 { font-size:28px; line-height:1.2; margin:0; color:var(--ink); font-weight:600; }
.bld .kicker { font-family:var(--mono); font-size:13px; color:var(--muted); margin:0 0 6px; }
.bld p { margin:0; color:var(--text); }
.bld .lead { font-size:17px; }
.step { background:var(--surface); border:1px solid var(--line); padding:20px; display:flex; flex-direction:column; gap:14px; }
.step h2 { font-size:15px; margin:0; font-family:var(--mono); font-weight:500; color:var(--ink); display:flex; gap:10px; align-items:baseline; }
.step h2 .n { color:var(--accent); }
.step.off { opacity:.5; }
.drop { border:1.5px dashed var(--chip); padding:22px; text-align:center; font-size:15px; color:var(--soft); display:block; cursor:pointer; }
.drop.over { border-color:var(--accent); background:#EEF2FD; }
.drop b { color:var(--accent); font-weight:500; }
.drop .names { display:block; font-family:var(--mono); font-size:12px; color:var(--muted); margin-top:6px; word-break:break-all; }
.drop input { position:absolute; width:1px; height:1px; opacity:0; }
.files { list-style:none; margin:0; padding:0; font-family:var(--mono); font-size:13px; display:flex; flex-direction:column; gap:6px; }
.files li { display:flex; justify-content:space-between; gap:12px; flex-wrap:wrap; padding:8px 10px; background:var(--bg); }
.ok { color:#1F7A3A; } .opt { color:var(--muted); } .bad { color:#B3261E; }
.btn { align-self:flex-start; font:500 15px var(--sans); background:var(--accent); color:#fff; border:0; padding:10px 18px; cursor:pointer; }
.btn[disabled] { background:var(--chip); color:var(--muted); cursor:default; }
.note { font-size:14px; color:var(--soft); background:var(--code-bg); padding:10px 12px; }
.msg { color:#B3261E; font-size:14px; }
.msg:empty { display:none; }
.bar { height:8px; background:var(--code-bg); }
.bar span { display:block; height:100%; width:0; background:var(--accent); transition:width .3s; }
.stages { list-style:none; margin:0; padding:0; font-family:var(--mono); font-size:13px; display:flex; flex-direction:column; gap:4px; color:var(--muted); }
.stages li::before { content:'· '; }
.stages .done { color:var(--text); } .stages .done::before { content:'✓ '; }
.stages .now { color:var(--accent); } .stages .now::before { content:'› '; }
.dl a { display:inline-block; font:500 15px var(--sans); background:#1F7A3A; color:#fff; padding:10px 18px; text-decoration:none; }
.run, .dl { display:flex; flex-direction:column; gap:12px; }
.run[hidden], .dl[hidden] { display:none; }
.faq { display:flex; flex-direction:column; gap:14px; font-size:15px; }
.faq h3 { font-size:15px; margin:0 0 4px; color:var(--ink); }
@media (min-width:720px) { .bld-hero { grid-template-columns:1fr 1fr; align-items:center; } }
</style>
"""

CFG = {
    'ss': dict(console='Saturn', img='/img/2026/tiger-road-ss-bezel2.png', w=320, h=224,
               alt='Tiger Road on the Saturn with an illustrated bezel on the side bands.',
               fmt='<b>BIN/CUE</b>: for Saroo, Fenrir and other optical drive emulators, or to burn to a CD-R.',
               stages=['Checking your ROM files', 'Building the program, graphics and voices', 'Generating music tracks', 'Writing the disc image'],
               after='A .zip with the .cue, the data track and the 34 audio tracks.',
               play='A Saturn with a Saroo, a Fenrir or another drive emulator, or a modded console that runs CD-Rs. It also works in Mednafen.',
               credits='The bezel artwork is by Capcom, taken from the Capcom wiki.'),
    'dc': dict(console='Dreamcast', img='/img/2026/tiger-road-dc-fullscreen.png', w=598, h=448,
               alt='Tiger Road on the Dreamcast in full screen.',
               fmt='<b>GDI</b>: comes as a folder ready to copy to your GDEMU SD card, and also plays in Flycast.',
               stages=['Checking your ROM files', 'Building the program and the texts', 'Generating music tracks', 'Writing the disc image'],
               after='A .zip with the folder for your GDEMU SD card: disc.gdi and its tracks.',
               play='A Dreamcast with a GDEMU or another drive emulator that loads GDI images, or Flycast. It can\'t be burned to a CD-R.',
               credits='The cover shown in the GDEMU menu uses artwork by Capcom, taken from the Capcom wiki.'),
}


def _top(root):
    src = (root / 'projects/tiger-road/index.html').read_text()
    return src[:src.index('</header>') + len('</header>')].replace('aria-current="page"', '')


def page(top, k, c, ver):
    stages = ''.join(f'<li><span class="t">{html.escape(s)}</span></li>' for s in c['stages'])
    body = f'''
<main id="main" class="bld" data-builder="{k}" data-base="/build/tiger-road/">
<a class="back" href="/projects/tiger-road/">← Tiger Road</a>
<div class="bld-hero">
<div>
<p class="kicker">disc builder · V1.2</p>
<h1>Build your own Tiger Road disc for the {c["console"]}</h1>
</div>
<img src="{c["img"]}" alt="{c["alt"]}" width="{c["w"]}" height="{c["h"]}">
</div>
<p class="lead">I can't share Capcom's ROMs, so there's no disc to download. This page builds the {c["console"]} disc image from the arcade ROM sets you own. Everything happens in your browser: your files are never uploaded anywhere.</p>
<section class="step">
<h2><span class="n">1</span> Add your arcade ROMs</h2>
<p>Both MAME ROM sets are needed, as .zip files: split (two files) or merged (toramich inside tigeroad.zip). Every file is checked against its expected checksum.</p>
<label class="drop">Drop your ROM files here or <b>choose files</b><input id="roms" type="file" accept=".zip" multiple><span class="names"></span></label>
<ul class="files">
<li data-set="us"><span>tigeroad.zip <span class="opt">· Tiger Road, World/US</span></span><span class="st opt">required</span></li>
<li data-set="jp"><span>toramich.zip <span class="opt">· Tora-he no Michi, Japan: Japanese text, logo and voices</span></span><span class="st opt">required</span></li>
</ul>
<p class="msg"></p>
</section>
<section class="step later off">
<h2><span class="n">2</span> Format</h2>
<p>{c["fmt"]}</p>
</section>
<section class="step later off">
<h2><span class="n">3</span> Build</h2>
<p class="note">The music on the disc is played from CD audio tracks. They can't be shared either, so your browser recreates them by emulating the arcade's two YM2203 sound chips, channel by channel, and mixing them in stereo. This takes two or three minutes on a recent computer: keep this tab open.</p>
<button class="btn" id="build" disabled>Build disc image</button>
<div class="run" hidden><div class="bar"><span></span></div><ul class="stages">{stages}</ul></div>
<div class="dl" hidden><a href="#">Download</a><p class="note">{c["after"]}</p></div>
</section>
<section class="faq">
<h3 style="font-size:17px">Questions</h3>
<div><h3>Where do I get the ROMs?</h3><p>From your own arcade board or a set you legally own. I can't help with that.</p></div>
<div><h3>What do I need to play it?</h3><p>{c["play"]}</p></div>
<div><h3>Which browsers work?</h3><p>Recent versions of Chrome, Edge, Firefox and Safari on a computer. The disc takes a few hundred MB of memory while it's being built.</p></div>
<div><h3>Credits</h3><p>{c["credits"]}</p></div>
<div><h3>Something went wrong</h3><p>If a file isn't found, it's probably from another version of the game or a different MAME set. Tell me on <a href="https://x.com/hombreimagina">X</a> which one you have.</p></div>
</section>
</main>
<script type="module" src="/build/tiger-road/page.js?v={ver}"></script>
</div>
</body>
</html>
'''
    t = top.replace('<title>Tiger Road · hombreimaginario</title>', f'<title>Disc builder · Tiger Road {c["console"]} · hombreimaginario</title>')
    t = t.replace('https://hombreimaginario.com/projects/tiger-road/', f'https://hombreimaginario.com/build/tiger-road-{k}/')
    return t.replace('</head>', CSS + '</head>') + body


def main(root):
    top = _top(root)
    ver = hashlib.sha1((root / 'build/tiger-road/page.js').read_bytes() + (root / 'build/tiger-road/engine.js').read_bytes()).hexdigest()[:8]
    for k, c in CFG.items():
        d = root / 'build' / f'tiger-road-{k}'
        d.mkdir(parents=True, exist_ok=True)
        (d / 'index.html').write_text(page(top, k, c, ver))
