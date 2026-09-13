#!/usr/bin/env python3
"""Generate site/writing/index.html (the writing hub) from the ported article
files. Reads each article's real <h1> and first paragraph so the hub always
reflects the cleaned, self-hosted content. No Medium links, no 'original' copy.
"""
import re, os, json, html

ROOT = os.path.dirname(os.path.abspath(__file__))
SITE = os.path.join(ROOT, "site")
WRITING = os.path.join(SITE, "writing")


def read(p):
    return open(os.path.join(SITE, p.lstrip("/")), encoding="utf-8").read()


def title_of(s):
    m = re.search(r"<h1>(.*?)</h1>", s, re.S)
    t = html.unescape(re.sub(r"<[^>]+>", "", m.group(1))).strip() if m else "Untitled"
    return t.rstrip("… ").rstrip()


def excerpt_of(s):
    body = re.search(r'<div class="article-body">(.*?)</div>', s, re.S)
    scope = body.group(1) if body else s
    for m in re.finditer(r"<p>(.*?)</p>", scope, re.S):
        txt = html.unescape(re.sub(r"<[^>]+>", "", m.group(1))).strip()
        if len(txt) > 40:
            return (txt[:150] + "…") if len(txt) > 150 else txt
    return ""


CARD = """        <a class="post glass reveal" data-tilt href="{href}">
          <span class="kicker">{kicker}</span>
          <h3>{title}</h3>
          <p>{excerpt}</p>
          <div class="tags">{tags}</div>
          <span class="more">Read →</span>
        </a>"""

PAGE = """<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>Writing · Carey Chou</title>
  <meta name="description" content="Essays on creativity, design, science and human-centered AI by Carey Chou — self-hosted, in full fidelity." />
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
        <a href="/art/" class="hide-sm">Creative works</a>
        <a href="/">← Home</a>
      </div>
    </div>
  </nav>
  <main id="main">
    <header class="hero wrap" style="padding-bottom:1rem">
      <p class="eyebrow">The Science half</p>
      <h1 style="max-width:20ch">Writing at the edge of <span class="gradient-text">design &amp; AI</span>.</h1>
      <p class="lede">Essays on creativity, design, science and human-centered AI — written to be read the way they were designed, not flattened to fit someone else's template.</p>
    </header>
    <section class="wrap">
      <div class="posts">
{cards}
      </div>
    </section>
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


def main():
    posts = json.load(open(os.path.join(ROOT, "posts.json")))
    cards = []
    for p in posts:
        s = read(p["href"])
        title = title_of(s)
        exc = excerpt_of(s)
        badge = p.get("badge")
        kicker = p["date"] + (f" · {badge}" if badge else "")
        tags = "".join(f'<span class="tag">{html.escape(t)}</span>' for t in p.get("tags", [])[:3])
        cards.append(CARD.format(href=p["href"], kicker=html.escape(kicker),
                                 title=html.escape(title), excerpt=html.escape(exc), tags=tags))
    out = PAGE.format(cards="\n".join(cards))
    open(os.path.join(WRITING, "index.html"), "w", encoding="utf-8").write(out)
    print(f"✓ wrote writing hub with {len(posts)} posts")


if __name__ == "__main__":
    main()
