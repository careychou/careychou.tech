#!/usr/bin/env bash
# connect-github.sh — one-time: create the dedicated GitHub repo and push this site.
#
# Creates  github.com/careychou/careychou.tech  (if it doesn't exist), wires it as
# 'origin', and pushes the current branch. Idempotent — safe to re-run.
#
# AUTH (pick one):
#   • gh CLI logged in:     ./connect-github.sh
#   • Personal Access Token: GITHUB_TOKEN=ghp_xxx ./connect-github.sh   (needs 'repo' scope)
#
# Options (env):
#   VISIBILITY=public|private   (default: public)
#   OWNER=careychou             REPO=careychou.tech
set -euo pipefail

OWNER="${OWNER:-careychou}"
REPO="${REPO:-careychou.tech}"
VISIBILITY="${VISIBILITY:-public}"
SLUG="$OWNER/$REPO"

cd "$(dirname "${BASH_SOURCE[0]}")"
git rev-parse --is-inside-work-tree >/dev/null 2>&1 || { echo "Not a git repo"; exit 1; }
BRANCH="$(git branch --show-current)"

create_with_gh() {
  gh repo view "$SLUG" >/dev/null 2>&1 && { echo "✓ repo $SLUG already exists"; return; }
  echo "→ creating $SLUG ($VISIBILITY) via gh"
  gh repo create "$SLUG" "--$VISIBILITY" --disable-wiki --description "careychou.tech — creativity × science × AI × tech" >/dev/null
}

create_with_token() {
  local priv="false"; [ "$VISIBILITY" = "private" ] && priv="true"
  local code
  code=$(curl -s -o /dev/null -w "%{http_code}" -H "Authorization: token $GITHUB_TOKEN" \
          "https://api.github.com/repos/$SLUG")
  if [ "$code" = "200" ]; then echo "✓ repo $SLUG already exists"; return; fi
  echo "→ creating $SLUG ($VISIBILITY) via API"
  curl -s -o /dev/null -w "  create HTTP %{http_code}\n" -X POST \
    -H "Authorization: token $GITHUB_TOKEN" \
    -H "Accept: application/vnd.github+json" \
    https://api.github.com/user/repos \
    -d "{\"name\":\"$REPO\",\"private\":$priv,\"description\":\"careychou.tech — creativity × science × AI × tech\",\"has_wiki\":false}"
  # push over HTTPS using the token as the credential for this invocation only
  git remote get-url origin >/dev/null 2>&1 || \
    git remote add origin "https://x-access-token:${GITHUB_TOKEN}@github.com/$SLUG.git"
}

if command -v gh >/dev/null 2>&1 && gh auth status >/dev/null 2>&1; then
  create_with_gh
  git remote get-url origin >/dev/null 2>&1 || git remote add origin "https://github.com/$SLUG.git"
elif [ -n "${GITHUB_TOKEN:-}" ]; then
  create_with_token
else
  cat <<'EOF'
✗ No auth found. Do ONE of:
   1) Install + login gh:   brew install gh && gh auth login    then re-run ./connect-github.sh
   2) Use a token:          GITHUB_TOKEN=ghp_xxx ./connect-github.sh   (token needs 'repo' scope)
EOF
  exit 2
fi

echo "→ pushing $BRANCH to origin"
git push -u origin "$BRANCH"
echo "✓ Done: https://github.com/$SLUG  (branch $BRANCH)"
echo "  Next (optional) — Git-based auto-deploy: see docs/GITHUB.md § Cloudflare Pages Git integration."
