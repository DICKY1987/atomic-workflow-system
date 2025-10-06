```bash
# === One-paste, all-in-one Git workflow (repo: CLI_RESTART) ===
# Default protocol: HTTPS. Use SSH by prefixing: PROTO=ssh bash -lc '<paste>'
# Optional: set a feature branch to merge main into with BRANCH=<your-branch>
# Example: BRANCH=feature/simplified-25ops-convo-updates PROTO=ssh bash -lc '<paste>'

bash -lc '
set -euo pipefail

# --- Config (you can override these via env) ---
RAW_URL="${RAW_URL:-https://github.com/DICKY1987/CLI_RESTART.gitb}"
BRANCH="${BRANCH:-}"   # e.g., feature/simplified-25ops-convo-updates

# Normalize URL (fix accidental ".gitb")
SANITIZED_URL="${RAW_URL%b}"
case "$SANITIZED_URL" in
  *.git) : ;;                  # ok
  *) SANITIZED_URL="${SANITIZED_URL}.git" ;;
esac

# Derive HTTPS/SSH remotes from sanitized URL
OWNER_REPO="$(printf "%s\n" "$SANITIZED_URL" | sed -E "s#^https?://github.com/([^/]+/[^.]+)(\.git)?#\1#")"
HTTPS_URL="https://github.com/${OWNER_REPO}.git"
SSH_URL="git@github.com:${OWNER_REPO}.git"

PROTO="${PROTO:-https}"
REPO_URL="$HTTPS_URL"
[ "$PROTO" = "ssh" ] && REPO_URL="$SSH_URL"

REPO_NAME="$(basename "${OWNER_REPO}")"

echo "→ Using $PROTO remote: $REPO_URL"
echo "→ Repo name: $REPO_NAME"
[ -n "${BRANCH:-}" ] && echo "→ Target feature branch: $BRANCH" || echo "→ No feature branch supplied (BRANCH unset). Main will be updated."

# --- Clone if needed ---
if [[ ! -d "$REPO_NAME/.git" ]]; then
  echo "→ Cloning $REPO_URL ..."
  git clone "$REPO_URL" "$REPO_NAME"
fi

cd "$REPO_NAME"

# Ensure remote uses chosen protocol
git remote set-url origin "$REPO_URL"

# Fetch everything (with prune)
git fetch origin "+refs/heads/*:refs/remotes/origin/*" --prune

# Ensure local main exists & is current
if git show-ref --verify --quiet refs/heads/main; then
  git checkout main
else
  git branch --track main origin/main 2>/dev/null || true
  git checkout main
fi
git pull --ff-only origin main

# If no BRANCH provided, stop after updating main
if [[ -z "${BRANCH:-}" ]]; then
  echo ""
  echo "✅ Main is up to date. If you want to merge main into a feature branch, re-run with:"
  echo "   BRANCH=<your-branch-name> bash -lc '\''<this script paste>'\''"
  exit 0
fi

# Checkout/create feature branch
if git rev-parse --verify "$BRANCH" >/dev/null 2>&1; then
  git checkout "$BRANCH"
elif git ls-remote --exit-code --heads origin "$BRANCH" >/dev/null 2>&1; then
  git checkout -t "origin/$BRANCH"
else
  echo "→ Remote branch not found; creating from main: $BRANCH"
  git checkout -b "$BRANCH" main
fi

# Merge main into feature branch
set +e
git merge --no-ff --no-edit main
merge_status=$?
set -e

if [[ $merge_status -ne 0 ]]; then
  cat <<EOF

⚠️  Merge conflicts detected.
Resolve them, then run:
  git add -A
  git commit --no-edit
  git push -u origin "$BRANCH"

Tip: See GitHub docs on resolving conflicts:
https://docs.github.com/en/get-started/using-git/resolving-merge-conflicts
EOF
  exit 1
fi

# Push updated branch
git push -u origin "$BRANCH"

echo ""
echo "✅ Done:"
echo "   - Repo: $REPO_URL"
echo "   - Branch: $BRANCH is merged with main and pushed."
'
```
