#!/usr/bin/env python3
"""Port all Medium posts -> self-contained styled HTML under site/writing/.
Rebuilds each article from the RSS content, downloads images locally, and
emits article pages + a writing hub. No Medium lock-in, no external image deps.
"""
import re, os, html, json, urllib.request, hashlib, sys
from datetime import datetime

ROOT = os.path.dirname(os.path.abspath(__file__))
SITE = os.path.join(ROOT, "site")
WRITING = os.path.join(SITE, "writing")
IMG_ROOT = os.path.join(WRITING, "img")
FEED = "/tmp/feed.xml"

# Posts we do NOT text-generate (a richer interactive version already exists).
INTERACTIVE = {
    "the-ai-cognitive-quadrant": {
        "href": "/writing/ai-cognitive-quadrant.html",
        "badge": "Interactive",
    }
}

HEAD = """<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>{title} · Carey Chou</title>
  <meta name="description" content="{desc}" />
  <meta name="theme-color" content="#05070f" />
  <link rel="preconnect" href="https://fonts.googleapis.com" />
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin />
  <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600&family=Space+Grotesk:wght@500;600;700&display=swap" rel="stylesheet" />
  <link rel="stylesheet" href="/assets/site.css" />
</head>
<body>
  <a class="skip" href="#main">Skip to content</a>
  <div class="flow-field" aria-hidden="true">
    <span class="blob b1"></span><span class="blob b2"></span><span class="blob b3"></span><span class="blob b4"></span>
  </div>
  <nav class="nav" aria-label="Primary">
    <div class="wrap">
      <a class="brand" href="/"><span class="mark" aria-hidden="true"></span> Carey&nbsp;Chou</a>
      <div class="nav-links">
        <a href="/writing/" class="hide-sm">Writing</a>
        <a href="/art/" class="hide-sm">Art</a>
        <a href="/">← Home</a>
      </div>
    </div>
  </nav>
  <main id="main">
    <article class="article wrap">
      <header>
        <p class="eyebrow">{kicker}</p>
        <h1>{title}</h1>
        <p class="byline"><span>Carey Chou</span> · <span>{date}</span> · <span>{mins} min read</span></p>
      </header>
      <div class="article-body">
{body}
      </div>
      <hr style="border:none;border-top:1px solid rgba(255,255,255,0.12);margin:3rem 0 1.5rem" />
      <p style="margin-bottom:2rem"><a class="btn btn-ghost" href="/writing/">← All writing</a></p>
    </article>
  </main>
  <footer class="site">
    <div class="wrap">
      <a class="brand" href="/"><span class="mark" aria-hidden="true"></span> Carey Chou</a>
      <nav class="socials" aria-label="Elsewhere">
        <a href="https://www.linkedin.com/in/careychou/" target="_blank" rel="noopener">LinkedIn ↗</a>
      </nav>
    </div>
  </footer>
  <script src="/assets/site.js" defer></script>
</body>
</html>
"""


def slug_from_link(link, title):
    m = re.search(r'/([a-z0-9-]+)-[0-9a-f]{8,}(?:\?|$)', link)
    if m:
        return m.group(1)
    s = re.sub(r'[^a-z0-9]+', '-', title.lower()).strip('-')
    return s[:60]


def fetch_img(url, dest):
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
        data = urllib.request.urlopen(req, timeout=30).read()
        with open(dest, "wb") as f:
            f.write(data)
        return True
    except Exception as e:
        print(f"    ! image failed {url}: {e}")
        return False


def process_images(body, slug):
    outdir = os.path.join(IMG_ROOT, slug)
    os.makedirs(outdir, exist_ok=True)
    srcs = re.findall(r'<img[^>]+src="([^"]+)"', body)
    seen = {}
    for i, src in enumerate(srcs, 1):
        if src in seen:
            body = body.replace(src, seen[src])
            continue
        # normalize to a larger render
        clean = re.sub(r'/max/\d+/', '/max/1400/', src)
        ext = ".png"
        m = re.search(r'\.(png|jpe?g|gif|webp|svg)', clean.split('/')[-1], re.I)
        if m:
            ext = "." + m.group(1).lower()
        name = f"{i:02d}{ext}"
        dest = os.path.join(outdir, name)
        rel = f"/writing/img/{slug}/{name}"
        if fetch_img(clean, dest) or fetch_img(src, dest):
            seen[src] = rel
            body = body.replace(src, rel)
    return body


def clean_body(body):
    # Drop Medium's trailing "originally published" / clap footers if present.
    body = re.sub(r'<hr[^>]*>\s*<p>\s*<em>.*?originally published.*?</p>', '', body, flags=re.I | re.S)
    # Remove empty figures / captions that are just image credits we can't keep.
    body = body.replace('<figure>', '<figure>').strip()
    return body


def excerpt(body):
    m = re.search(r'<p>(.*?)</p>', body, re.S)
    if not m:
        return ""
    txt = re.sub(r'<[^>]+>', '', m.group(1))
    txt = html.unescape(txt).strip()
    return (txt[:160] + "…") if len(txt) > 160 else txt


def reading_mins(body):
    words = len(re.sub(r'<[^>]+>', ' ', body).split())
    return max(1, round(words / 200))


def main():
    x = open(FEED, encoding="utf-8").read()
    items = re.findall(r'<item>.*?</item>', x, re.S)
    posts = []
    seen_slugs = set()
    for it in items:
        title = html.unescape(re.search(r'<title><!\[CDATA\[(.*?)\]\]></title>', it, re.S).group(1))
        link = re.search(r'<link>(.*?)</link>', it, re.S).group(1)
        date_raw = re.search(r'<pubDate>(.*?)</pubDate>', it, re.S).group(1)
        cats = re.findall(r'<category><!\[CDATA\[(.*?)\]\]></category>', it)
        cont = re.search(r'<content:encoded><!\[CDATA\[(.*?)\]\]></content:encoded>', it, re.S)
        body = cont.group(1) if cont else ""
        slug = slug_from_link(link, title)
        if slug in seen_slugs:
            print(f"  (skip duplicate) {title}")
            continue
        seen_slugs.add(slug)
        try:
            dt = datetime.strptime(date_raw[:25].strip(), "%a, %d %b %Y %H:%M:%S")
            date = dt.strftime("%b %-d, %Y")
        except Exception:
            dt = datetime(2025, 1, 1); date = date_raw[:16]

        rec = {"title": title, "slug": slug, "date": date, "dt": dt.isoformat(),
               "tags": cats[:4]}

        if slug in INTERACTIVE:
            rec.update(INTERACTIVE[slug])
            rec["excerpt"] = excerpt(body)
            posts.append(rec)
            print(f"  (interactive) {title} -> {rec['href']}")
            continue

        print(f"  porting: {title}")
        body = clean_body(body)
        body = process_images(body, slug)
        mins = reading_mins(body)
        kicker = " · ".join([date] + ([cats[0].replace('-', ' ')] if cats else []))
        page = HEAD.format(
            title=html.escape(title),
            desc=html.escape(excerpt(body)),
            kicker=html.escape(kicker),
            date=date, mins=mins,
            body="\n".join("        " + ln for ln in body.splitlines()),
        )
        with open(os.path.join(WRITING, slug + ".html"), "w", encoding="utf-8") as f:
            f.write(page)
        rec.update({"href": f"/writing/{slug}.html", "excerpt": excerpt(body), "mins": mins})
        posts.append(rec)

    posts.sort(key=lambda p: p["dt"], reverse=True)
    with open(os.path.join(ROOT, "posts.json"), "w") as f:
        json.dump(posts, f, indent=2)
    print(f"\n✓ {len(posts)} posts")
    for p in posts:
        print(f"  - {p['date']:>14} | {p['href']}")


if __name__ == "__main__":
    main()
