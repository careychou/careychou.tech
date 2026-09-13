# Connecting careychou.tech to GitHub

The site lives in this local git repo. This runbook connects it to a **dedicated
GitHub repo** — `github.com/careychou/careychou.tech` — for version history and
(optionally) Git-based auto-deploy.

State: **connected** — `origin` → `github.com/careychou/careychou.tech` (public),
branch `main` pushed. `.env`/secrets ignored; no token stored in `.git/config`.

Future pushes: the stored remote is the clean HTTPS URL, so `git push` will ask
for credentials (this machine has no cached GitHub credential). Use your PAT —
either let macOS keychain store it on first prompt, or push non-interactively:
```bash
TOKEN="$(tr -d ' \t\r\n' < ~/Documents/personal/github.cred)"
git push "https://x-access-token:${TOKEN}@github.com/careychou/careychou.tech.git" main
```
(Installing `gh` + `gh auth login` also works and makes plain `git push` seamless.)

---

## 1. Create the repo + push (one time)

Everything is scripted in `./connect-github.sh` (idempotent). Pick an auth path:

**Option A — gh CLI (recommended):**
```bash
brew install gh          # if missing
gh auth login            # choose GitHub.com → HTTPS → browser; complete in browser
./connect-github.sh      # creates careychou/careychou.tech (public) and pushes main
```

**Option B — Personal Access Token:**
1. Create a token at https://github.com/settings/tokens with **`repo`** scope.
2. Run (token is used only for this command, never stored in the repo):
   ```bash
   GITHUB_TOKEN=ghp_xxx ./connect-github.sh
   ```

Make it private instead of public: prefix either command with `VISIBILITY=private`.

After this, normal git flow works: `git add -A && git commit && git push`.

---

## 2. (Optional) Git-based auto-deploy — Cloudflare Pages ↔ GitHub

Today deploys are manual (`./deploy.sh` → `wrangler pages deploy`). To make
**`git push` auto-deploy** instead:

1. Cloudflare dashboard → **Workers & Pages** → the `careychou` project →
   **Settings → Builds & deployments → Connect to Git**.
2. Authorize GitHub, pick `careychou/careychou.tech`, branch `main`.
3. Build settings for this static site:
   - **Framework preset:** None
   - **Build command:** *(leave empty)*
   - **Build output directory:** `site`
4. Save. Every push to `main` now builds a deployment; the custom domain
   `careychou.tech` stays attached.

You can keep using `./deploy.sh` for direct pushes even after connecting Git —
they coexist. If you want ONLY Git deploys, just stop running `deploy.sh`.

---

## 3. Notes
- `.gitignore` already excludes `node_modules/`, `.wrangler/`, `.env*`, `venv/`,
  `*.log`, `devserver.out`, `.DS_Store` — no secrets are committed.
- The `site/writing/img/` images (~14 MB) are committed intentionally; they're
  real site assets and are needed for a Git-based build/deploy.
- The confidentiality gate (`careychou-tech-site-ops` skill) still applies
  before any deploy, Git-based or manual.
