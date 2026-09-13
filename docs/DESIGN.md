# careychou.tech — Design System (living source of truth)

> This is the **authoritative** description of the site's look, feel, and
> structure. `site/assets/site.css` is the implementation; this doc is the
> intent. When they disagree, reconcile them — do not let them drift. The
> `careychou-tech-site-ops` skill *references* this file rather than copying it.

The site expresses one idea: **creativity × design × science × human-centered AI**,
rendered in a **liquid glass + flow** visual language on a deep near-black canvas.

---

## 1. Design tokens (`:root` in site.css)

```
/* surfaces */         --bg-0:#05070f  --bg-1:#0a0e1c
/* text */             --ink:#e9edf8   --ink-dim:#9aa6c2   --ink-faint:#6b7591
/* brand flow palette*/--iris:#7c5cff  --cyan:#22d3ee  --mint:#34e0b0  --magenta:#ff5ca8  --amber:#ffb26b
/* glass */            --glass-bg / --glass-bg-strong / --glass-brd / --glass-hi / --glass-shadow
/* shape */            --radius:22px   --radius-sm:14px   --maxw:1180px
/* motion */           --ease:cubic-bezier(.22,1,.36,1)
/* type */             --font:Inter…   --font-display:"Space Grotesk"…
```
Rules: **never hardcode a raw color** — use a token. New accents should be
composed from the flow palette (iris→cyan→mint→magenta→amber), not net-new hues.

## 2. Typography
- Display / headings: **Space Grotesk** (500–700). Body: **Inter** (400–600).
- Fluid sizing via `clamp()` everywhere (e.g. hero `h1` `clamp(2.5rem,7vw,4.8rem)`).
- Measure: prose columns cap around `46–72ch`; article body `max-width:720px`.

## 3. Layout & spacing
- `.wrap` centers content at `--maxw` with fluid gutters `clamp(1.1rem,4vw,2.4rem)`.
- Vertical rhythm uses `clamp()` section gaps (`.sec-head`, `.about`, `footer.site`).
- Breakpoints: **860px** (zones → 1 col), **760px** (art-feature → 1 col),
  **640px** (`.hide-sm` nav links hide). Keep new grids collapsing at these.

## 4. The liquid-glass + flow language
- **Glass** (`.glass`): translucent fill (`--glass-bg`), hairline border
  (`--glass-brd`), soft depth shadow (`--glass-shadow`), rounded `--radius`.
- **Flow field** (`.flow-field` + `.blob b1..b4`): four blurred drifting color
  blobs behind content — the "flow." Present on most pages, `aria-hidden`.
- **Pointer sheen** (`[data-tilt]`): a specular highlight tracks the cursor on
  glass cards (added by `site.js`). Decorative; pointer-only.
- **Gradient text** (`.gradient-text`, `.grad`): flow-palette gradient on key words.

## 5. Components / utility classes (in site.css)
| Class | Role |
|---|---|
| `.nav` + `.brand` + `.nav-links` | top nav (brand mark + Writing/Art/Home) |
| `.hero` `.hero-cta` `.lede` | homepage hero |
| `.zones` `.zone` `.zone-icon` | the two-halves split (writing / art) |
| `.sec-head` | section header row (title + link) |
| `.posts` `.post` | writing card grid + card |
| `.gallery` `.art-feature` `.art-tile` | art gallery grid + tiles |
| `.article` `.article-body` | long-form reading shell |
| `.glass` `.btn`/`.btn-primary`/`.btn-ghost` `.tag` `.chip`/`.chips` `.eyebrow` `.kicker` `.note-box` `.formula` | primitives |
| `.reveal` | scroll-in animation hook (JS adds `.in`) |
| `.flow-field` `.blob` | background flow |
| `.wrap` `.skip` `.socials` `.about` | scaffolding |

`site.js` = two progressive enhancements only: **reveal-on-scroll**
(IntersectionObserver) and **pointer sheen** on `[data-tilt]`. The site is fully
functional with JS off.

## 6. Information architecture
```
/                 homepage: hero → two zones (Writing / Art) → post cards → art teaser → about
/writing/         hub of article cards         /writing/<slug>.html   article
/art/             gallery of tiles             /art/<slug>.html       art piece
/<route>/         standalone app / one-off (clean URL)
```
Every page: brand → Writing / Art / Home nav; footer = brand + LinkedIn only.

## 7. Voice & content principles
- Personal, editorial, precise — creativity meets rigor. No corporate filler.
- **Self-hosted, format-independent**: no "Read on Medium"/"original" links,
  no outbound Medium lock-in; images are local.
- **Public only**: never any H-E-B-confidential material (enforced by the skill's
  `check-content.sh` gate).

## 8. Accessibility (non-negotiable, WCAG 2.1 AA)
- Semantic landmarks (`nav`/`main`/`footer`), one `<h1>` per page, `.skip` link.
- Visible focus: `:focus-visible { outline: 2px solid var(--cyan) }`.
- `alt`/`aria-label` on all media; decorative layers `aria-hidden`.
- Honor `@media (prefers-reduced-motion: reduce)` — all reveal/tilt/flow motion
  must degrade to static. Any new animation MUST add a reduced-motion fallback.
- Maintain contrast: `--ink` on `--bg-0/1` passes AA; dim text only for
  secondary content.

## 9. How to evolve the design (checklist)
1. Change tokens/components in `site/assets/site.css` (and this doc together).
2. Preview locally, resize through the three breakpoints, tab through for focus.
3. Verify reduced-motion still renders everything.
4. Run the skill's gate, deploy, verify live. Commit both `site.css` and this doc.
