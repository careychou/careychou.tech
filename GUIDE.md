# Cloudflare Pages + Domain — Setup Guide

Everything in `site/` is ready to deploy. This guide covers the parts only **you**
can do (account signup + domain purchase) and the one-command deploys I can do for you.

Project name: **careychou** → free URL will be **https://careychou.pages.dev**
Target custom domain: **careychou.com** (confirm availability at purchase — swap if taken)

---

## Step 1 — Create a free Cloudflare account  *(you, ~2 min)*
1. Go to https://dash.cloudflare.com/sign-up
2. Sign up with your email + password, verify the email.
3. That's it — no credit card needed for the free tier.

## Step 2 — Authorize this machine to deploy  *(you, ~1 min)*
In your terminal:
```bash
cd ~/projects/careychou-site
npx wrangler login
```
A browser opens → click **Allow**. This stores a token locally so deploys are hands-off afterward.

> Headless / no browser? Instead create an API token at
> https://dash.cloudflare.com/profile/api-tokens (template: **"Edit Cloudflare Workers"**,
> or a custom token with **Account → Cloudflare Pages → Edit**), then:
> `export CLOUDFLARE_API_TOKEN=xxxxx` before running `./deploy.sh`.

## Step 3 — First deploy  *(I can run this once you've done Steps 1–2)*
```bash
./deploy.sh
```
First run creates the Pages project and uploads `site/`. Live in ~10 seconds at
`https://careychou.pages.dev`. Every future publish is the same one command.

---

## Step 4 — Buy your domain  *(you, ~5 min, ~$10–12/yr)*

### Option A — Cloudflare Registrar (recommended: at-cost, one dashboard)
> Note: Cloudflare Registrar can only **register a brand-new domain** once you have
> an active zone, OR you can register directly from the dashboard if available in your
> account. The simplest reliable path:
1. In the Cloudflare dashboard, left sidebar → **Domain Registration → Register Domains**.
2. Search `careychou` → pick an available TLD (`.com`, `.dev`, etc.) → checkout.
3. Because it's registered inside Cloudflare, DNS is auto-managed — no nameserver step.

### Option B — Buy elsewhere (Porkbun / Namecheap), point DNS at Cloudflare
1. Buy `careychou.com` at https://porkbun.com or https://namecheap.com.
2. In Cloudflare dashboard → **Add a site** → enter `careychou.com` → choose **Free** plan.
3. Cloudflare gives you 2 nameservers → set them at your registrar (replace the defaults).
4. Wait for the zone to go "Active" (minutes to a few hours).

## Step 5 — Attach the domain to your Pages site  *(you in dashboard, ~2 min)*
1. Dashboard → **Workers & Pages → careychou → Custom domains**.
2. Click **Set up a custom domain** → enter `careychou.com` (and `www.careychou.com`).
3. Cloudflare adds the DNS records automatically (if the zone is on Cloudflare).
4. HTTPS cert is issued automatically — done. Your site is live at `https://careychou.com`.

---

## Daily workflow after setup
- Add/edit HTML files in `site/` (link new ones from `site/index.html`).
- Run `./deploy.sh` — or just tell me "publish this" and I'll drop the file in `site/` and deploy.
- Preview locally anytime:
  ```bash
  npx wrangler pages dev ./site
  ```

## When you outgrow static (backend logic)
Cloudflare Workers handle JS/edge APIs + D1 (SQLite), KV, R2. But your stated stack is
**Python (Google ADK) + PostgreSQL** — that does NOT run on Workers. For that backend, use a
Python-friendly host (Fly.io / Railway / Render / Hetzner) with managed Postgres, and keep the
React frontend + infographics here on Cloudflare Pages.
