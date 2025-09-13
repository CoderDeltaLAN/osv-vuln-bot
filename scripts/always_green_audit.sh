#!/usr/bin/env zsh
setopt pipefail
REPO="${1:-CoderDeltaLAN/osv-vuln-bot}"
OUT_DIR="_intel/audit-$(date +%Y%m%d%H%M%S)"
mkdir -p "$OUT_DIR"

echo "# Audit for $REPO" | tee "$OUT_DIR/summary.txt"

# Default branch
DEF=$(gh repo view "$REPO" --json defaultBranchRef --jq .defaultBranchRef.name)
echo "default_branch=$DEF" | tee -a "$OUT_DIR/summary.txt"

# Protection
gh api "repos/$REPO/branches/$DEF/protection" | tee "$OUT_DIR/protection.json" >/dev/null
jq '{strict:.required_status_checks.strict,contexts:.required_status_checks.contexts,admins:.enforce_admins,approvals:.required_pull_request_reviews.required_approving_review_count}' "$OUT_DIR/protection.json" | tee -a "$OUT_DIR/summary.txt"

# Last 10 runs
gh run list --repo "$REPO" --limit 10 \
  --json databaseId,workflowName,headBranch,status,conclusion,createdAt,url \
  --jq '.[]|[.databaseId,.workflowName,.headBranch,.status,.conclusion,.createdAt,.url]|@tsv' \
  | tee "$OUT_DIR/runs.tsv" >/dev/null

# Branches
gh api "repos/$REPO/branches?per_page=100" --paginate --jq '.[].name' | sort -u | tee "$OUT_DIR/branches.txt" >/dev/null

echo "Audit written to $OUT_DIR"
