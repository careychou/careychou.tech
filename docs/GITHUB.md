# Connecting careychou.tech to GitHub

The site lives in this local git repo. This runbook connects it to a **dedicated
GitHub repo** — `github.com/careychou/careychou.tech` — for version history and
(optionally) Git-based auto-deploy.

State as of setup: local repo on branch `main`, committed, **no remote yet**,
`.env`/secrets ignored, no cached GitHub credential on this machine.

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
- The confidentiality gate (`carey-cloudflare-publish` skill) still applies
  before any deploy, Git-based or manual.
