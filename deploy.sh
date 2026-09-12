#!/usr/bin/env bash
# Deploy the static site in ./site to Cloudflare Pages.
# One-time prerequisites (see GUIDE.md):
#   1. A free Cloudflare account
#   2. `npx wrangler login`  (opens a browser to authorize this machine)
# After that, every publish is just: ./deploy.sh
set -euo pipefail

PROJECT_NAME="careychou"

echo "→ Deploying ./site to Cloudflare Pages project: $PROJECT_NAME"
npx wrangler pages deploy ./site --project-name "$PROJECT_NAME" --commit-dirty=true

echo "✓ Done. Your live URL is shown above (https://$PROJECT_NAME.pages.dev)."
