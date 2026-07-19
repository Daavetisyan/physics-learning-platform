#!/usr/bin/env bash
set -euo pipefail

REPO_URL="https://github.com/Daavetisyan/physics-learning-platform.git"
BRANCH="main"
PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$PROJECT_DIR"

if ! command -v git >/dev/null 2>&1; then
  echo "Git is not installed. Install it with: sudo apt install git"
  exit 1
fi

if ! git config --global user.name >/dev/null 2>&1; then
  read -r -p "Git name: " GIT_NAME
  git config --global user.name "$GIT_NAME"
fi

if ! git config --global user.email >/dev/null 2>&1; then
  read -r -p "Git email: " GIT_EMAIL
  git config --global user.email "$GIT_EMAIL"
fi

# GitHub no longer accepts account passwords for Git pushes. GitHub CLI gives
# the most reliable browser-based login on Linux when it is installed.
if command -v gh >/dev/null 2>&1; then
  if ! gh auth status >/dev/null 2>&1; then
    echo "Opening GitHub browser authentication..."
    gh auth login --hostname github.com --git-protocol https --web
  fi
  gh auth setup-git
else
  echo "GitHub CLI (gh) is not installed."
  echo "The script will still try git push using any existing Git credential or SSH setup."
  echo "For browser login, install gh first: https://cli.github.com/"
fi

if [[ ! -d .git ]]; then
  git init
fi

git branch -M "$BRANCH"
if git remote get-url origin >/dev/null 2>&1; then
  git remote set-url origin "$REPO_URL"
else
  git remote add origin "$REPO_URL"
fi

git add --all
if ! git diff --cached --quiet; then
  git commit -m "Upload section-based physics learning platform"
fi

# Preserve the existing GitHub README commit while preferring this project's
# complete files if README content conflicts.
git fetch origin "$BRANCH" || true
if git show-ref --verify --quiet "refs/remotes/origin/$BRANCH"; then
  if ! git merge-base "$BRANCH" "origin/$BRANCH" >/dev/null 2>&1; then
    git merge "origin/$BRANCH" --allow-unrelated-histories -X ours \
      -m "Merge existing GitHub repository history"
  else
    git merge "origin/$BRANCH" --no-edit || true
  fi
fi

git push -u origin "$BRANCH"

echo
echo "Uploaded successfully: https://github.com/Daavetisyan/physics-learning-platform"
echo "Run locally with: ./run_local.sh"
