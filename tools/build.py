#!/usr/bin/env python3
"""Build hombreimaginario.com from content/.

Sources (edit these):
  content/posts.json          one entry per post (metadata)
  content/posts/<slug>.html   the body of each post (plain HTML fragment)

Generated (do not edit by hand, they are rewritten on every build):
  index.html, archive/index.html, posts/<slug>/index.html, feed.xml, 404.html

Run from the repository root:  python3 tools/build.py
Standard library only.
"""
import html
import json
import re
import shutil
import sys
from datetime import date, datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from icons import ICONS  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
SITE_URL = "https://hombreimaginario.com"
SITE_NAME = "hombreimaginario"
SITE_SUB = "retro works"
SITE_DESC = "Retro game ports and other retro works by hombreimaginario."
HOME_LIMIT = 10
SOCIAL_CARD = "/img/social-card.png"  # preview image for pages without a cover; made by tools/make_card.py

# Order here is the order of the filter buttons.
PLATFORMS = {
    "mega-drive": "Mega Drive",
    "saturn": "Saturn",
    "dreamcast": "Dreamcast",
    "neo-geo": "Neo Geo",
}

SOCIAL = [
    ("x", "X", "https://x.com/hombreimagina"),
    ("itch", "itch.io", "https://hombreimaginario.itch.io"),
    ("github", "GitHub", "https://github.com/hombreimaginario"),
]

MONTHS = ["January", "February", "March", "April", "May", "June", "July",
          "August", "September", "October", "November", "December"]

e = html.escape


def load_posts():
    data = json.loads((ROOT / "content" / "posts.json").read_text(encoding="utf-8"))
    posts = []
    for p in data:
        for key in ("slug", "date", "title", "summary"):
            if not p.get(key):
                sys.exit(f"posts.json: entry missing '{key}': {p}")
        if not re.fullmatch(r"[a-z0-9]+(?:-[a-z0-9]+)*", p["slug"]):
            sys.exit(f"posts.json: bad slug '{p['slug']}' (use lowercase-words-with-dashes)")
        p["date_obj"] = date.fromisoformat(p["date"])
        p.setdefault("platforms", [])
        for plat in p["platforms"]:
            if plat not in PLATFORMS:
                sys.exit(f"posts.json: unknown platform '{plat}' in '{p['slug']}'")
        body_file = ROOT / "content" / "posts" / f"{p['slug']}.html"
        if not body_file.exists():
            sys.exit(f"missing body file: {body_file.relative_to(ROOT)}")
        p["body"] = body_file.read_text(encoding="utf-8").strip()
        posts.append(p)
    slugs = [p["slug"] for p in posts]
    if len(slugs) != len(set(slugs)):
        sys.exit("posts.json: duplicate slug")
    posts.sort(key=lambda p: (p["date_obj"], p["slug"]), reverse=True)
    return posts


def url(p):
    return f"/posts/{p['slug']}/"


def tags_links(p):
    """Tags for a post page: each platform links to the archive filtered by it."""
    parts = [f'<a href="/archive/#{e(x)}">{e(x)}</a>' for x in p["platforms"]]
    if p.get("project"):
        parts.append("#" + e(p["project"]))
    return " · ".join(parts)


def tags_line(p):
    parts = list(p["platforms"])
    if p.get("project"):
        parts.append("#" + p["project"])
    return " · ".join(e(x) for x in parts)


def read_minutes(p):
    words = len(re.sub(r"<[^>]+>", " ", p["body"]).split())
    return max(1, round(words / 200))


def icon_svg(key):
    return (f'<svg viewBox="0 0 24 24" aria-hidden="true" focusable="false">'
            f'<path d="{ICONS[key]}"/></svg>')


def header(current="", small=False):
    nav = []
    archive_attr = ' aria-current="page"' if current == "archive" else ""
    nav.append(f'<a href="/archive/"{archive_attr}>archive</a>')
    nav.append('<a href="/feed.xml">rss</a>')
    nav.append('<span class="sep" aria-hidden="true"></span>')
    for key, label, href in SOCIAL:
        nav.append(f'<a class="icon {key}" href="{href}" aria-label="{label}" rel="me">{icon_svg(key)}</a>')
    cls = "site-header small" if small else "site-header"
    return f"""<header class="{cls}">
<a class="brand" href="/">
<span class="brand-name">{SITE_NAME}</span>
<span class="brand-sub">{SITE_SUB}<span class="cursor">_</span></span>
</a>
<nav class="site-nav" aria-label="Site">
{chr(10).join(nav)}
</nav>
</header>"""


def footer():
    year = date.today().year
    return f"""<footer class="site-footer">
<span>© {year} hombreimaginario.com</span>
<a href="/feed.xml">rss</a>
</footer>"""


def filters():
    btns = ['<button type="button" data-filter="all" aria-pressed="true">all</button>']
    for key in PLATFORMS:
        btns.append(f'<button type="button" data-filter="{key}" aria-pressed="false">{key}</button>')
    return '<div class="filters" role="group" aria-label="Filter by platform">\n' + "\n".join(btns) + "\n</div>"


def page(title, body, description=SITE_DESC, canonical="/", og_image=None, scripts=False, extra_head=""):
    full_title = f"{title} · {SITE_NAME}" if title else f"{SITE_NAME} · {SITE_SUB}"
    og_image = og_image or SOCIAL_CARD
    og_img = f'\n<meta property="og:image" content="{SITE_URL}{e(og_image)}">'
    og_img += '\n<meta property="og:image:width" content="1200">\n<meta property="og:image:height" content="630">' if og_image == SOCIAL_CARD else ""
    script = '\n<script src="/assets/js/filter.js" defer></script>' if scripts else ""
    return f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{e(full_title)}</title>
<meta name="description" content="{e(description)}">
<link rel="canonical" href="{SITE_URL}{canonical}">
<meta property="og:site_name" content="{SITE_NAME}">
<meta property="og:title" content="{e(title or SITE_NAME + " · " + SITE_SUB)}">
<meta property="og:description" content="{e(description)}">
<meta property="og:url" content="{SITE_URL}{canonical}">{og_img}
<meta name="twitter:card" content="{'summary_large_image' if og_image else 'summary'}">
<meta name="twitter:site" content="@hombreimagina">
<meta name="twitter:creator" content="@hombreimagina">
<link rel="icon" href="/favicon.ico" sizes="any">
<link rel="icon" href="/favicon-32.png" type="image/png" sizes="32x32">
<link rel="apple-touch-icon" href="/apple-touch-icon.png">
<link rel="alternate" type="application/atom+xml" title="{SITE_NAME}" href="/feed.xml">
<link rel="preload" href="/assets/fonts/ibm-plex-sans-latin-400-normal.woff2" as="font" type="font/woff2" crossorigin>
<link rel="stylesheet" href="/assets/css/style.css">
<script>document.documentElement.className += ' js';</script>{script}{extra_head}
</head>
<body>
<a class="skip" href="#main">Skip to content</a>
<div class="wrap">
{body}
</div>
</body>
</html>
"""


def build_home(posts):
    items = []
    for p in posts[:HOME_LIMIT]:
        cover = ""
        if p.get("cover"):
            pixel = ' pixel' if p.get("cover_pixel") else ''
            cover = (f'\n<a href="{url(p)}" tabindex="-1" aria-hidden="true">'
                     f'<img class="post-cover{pixel}" src="{e(p["cover"])}" alt="" loading="lazy"></a>')
        items.append(f"""<article class="post-item" data-platforms="{' '.join(p['platforms'])}">
<div class="post-date"><time datetime="{p['date']}">{p['date']}</time></div>
<div class="post-main">
<div class="tags">{tags_line(p)}</div>
<h2 class="post-title"><a href="{url(p)}">{e(p['title'])}</a></h2>
<p class="post-summary">{e(p['summary'])}</p>{cover}
<a class="read-more" href="{url(p)}" aria-label="Read more: {e(p['title'])}">[+] read more</a>
</div>
</article>""")
    body = f"""{header()}
<main id="main" class="wrap-main" style="display:flex;flex-direction:column;gap:48px">
{filters()}
<div class="post-list">
{chr(10).join(items)}
</div>
<p class="empty" hidden>No posts for this platform yet. <a href="/archive/">Check the archive.</a></p>
<a class="more" href="/archive/">ls ./archive — all posts →</a>
</main>
{footer()}"""
    return page("", body, scripts=True)


def build_archive(posts):
    groups = []
    for p in posts:
        key = (p["date_obj"].year, p["date_obj"].month)
        if not groups or groups[-1][0] != key:
            groups.append((key, []))
        groups[-1][1].append(p)
    sections = []
    for (y, m), items in groups:
        rows = "\n".join(
            f'<li data-platforms="{" ".join(p["platforms"])}"><a href="{url(p)}">'
            f'<span class="d">{p["date"]}</span>'
            f'<span class="t">{e(p["title"])}</span>'
            f'<span class="g">{tags_line(p)}</span></a></li>'
            for p in items)
        n = len(items)
        sections.append(f"""<section class="month">
<h2><span>{y}-{m:02d}</span><span class="count">{n} {'post' if n == 1 else 'posts'}</span></h2>
<ul>
{rows}
</ul>
</section>""")
    n = len(posts)
    body = f"""{header(current="archive")}
<main id="main" style="display:flex;flex-direction:column;gap:48px">
<div class="page-head">
<div class="prompt" aria-hidden="true">$ ls -t ./archive</div>
<h1 class="page-title">Archive</h1>
<p class="page-lede" data-count>{n} {'post' if n == 1 else 'posts'}, newest first.</p>
{filters()}
</div>
<div class="months">
{chr(10).join(sections)}
</div>
<p class="empty" hidden>No posts for this platform yet.</p>
</main>
{footer()}"""
    return page("Archive", body, description="Every post on hombreimaginario, newest first.",
                canonical="/archive/", scripts=True)


def build_post(p, newer, older):
    nav = []
    if older:
        nav.append(f'<a class="prev" href="{url(older)}">← {e(older["title"])}</a>')
    if newer:
        nav.append(f'<a class="next" href="{url(newer)}">{e(newer["title"])} →</a>')
    nav_html = f'<nav class="post-nav" aria-label="More posts">\n{chr(10).join(nav)}\n</nav>' if nav else ""
    cover_html = ""
    if p.get("cover"):
        pixel = ' class="pixel"' if p.get("cover_pixel") else ''
        alt = e(p.get("cover_alt", p["title"]))
        cover_html = f'<figure class="cover">\n  <img{pixel} src="{e(p["cover"])}" alt="{alt}">\n</figure>\n'
    tags = tags_links(p)
    tags_html = f'<span class="tags">{tags}</span>' if tags else ""
    body = f"""{header(small=True)}
<main id="main" style="display:flex;flex-direction:column;gap:44px">
<article style="display:flex;flex-direction:column;gap:44px">
<header class="post-head">
<div class="meta">
<time datetime="{p['date']}">{p['date']}</time>
{tags_html}
<span>{read_minutes(p)} min read</span>
</div>
<h1>{e(p['title'])}</h1>
</header>
<div class="prose">
{cover_html}{p['body']}
</div>
</article>
{nav_html}
</main>
{footer()}"""
    return page(p["title"], body, description=p["summary"], canonical=url(p), og_image=p.get("cover"))


def build_feed(posts):
    now = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    entries = []
    for p in posts[:20]:
        stamp = f"{p['date']}T12:00:00Z"
        content = p["body"].replace('src="/', f'src="{SITE_URL}/').replace('href="/', f'href="{SITE_URL}/')
        cats = "".join(f'<category term="{c}"/>' for c in p["platforms"])
        entries.append(f"""<entry>
<title>{e(p['title'])}</title>
<link href="{SITE_URL}{url(p)}"/>
<id>{SITE_URL}{url(p)}</id>
<published>{stamp}</published>
<updated>{p.get('updated', p['date'])}T12:00:00Z</updated>
<summary>{e(p['summary'])}</summary>{cats}
<content type="html">{e(content)}</content>
</entry>""")
    return f"""<?xml version="1.0" encoding="utf-8"?>
<feed xmlns="http://www.w3.org/2005/Atom">
<title>{SITE_NAME} · {SITE_SUB}</title>
<subtitle>{e(SITE_DESC)}</subtitle>
<link href="{SITE_URL}/feed.xml" rel="self"/>
<link href="{SITE_URL}/"/>
<id>{SITE_URL}/</id>
<updated>{now}</updated>
<author><name>{SITE_NAME}</name></author>
{chr(10).join(entries)}
</feed>
"""


def build_404():
    body = f"""{header(small=True)}
<main id="main" class="page-head">
<div class="prompt" aria-hidden="true">$ cd ./this-page</div>
<h1 class="page-title">Not found</h1>
<p class="page-lede">That page doesn't exist. Try the <a href="/" style="color:var(--accent)">home page</a> or the <a href="/archive/" style="color:var(--accent)">archive</a>.</p>
</main>
{footer()}"""
    return page("Not found", body, canonical="/404.html")


def write(rel, text):
    path = ROOT / rel
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def main():
    posts = load_posts()
    # Rebuild posts/ from scratch so removed posts disappear.
    out_posts = ROOT / "posts"
    if out_posts.exists():
        shutil.rmtree(out_posts)
    for i, p in enumerate(posts):
        newer = posts[i - 1] if i > 0 else None
        older = posts[i + 1] if i + 1 < len(posts) else None
        write(f"posts/{p['slug']}/index.html", build_post(p, newer, older))
    write("index.html", build_home(posts))
    write("archive/index.html", build_archive(posts))
    write("feed.xml", build_feed(posts))
    write("404.html", build_404())
    print(f"Built {len(posts)} post(s).")


if __name__ == "__main__":
    main()
