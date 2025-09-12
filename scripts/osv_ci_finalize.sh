#!/usr/bin/env zsh
setopt pipefail
REPO="CoderDeltaLAN/osv-vuln-bot"
LOG_DIR="_ci_logs"; mkdir -p "$LOG_DIR"

echo "# Protecciones" | tee "$LOG_DIR/protection.summary.txt"
gh api "repos/$REPO/branches/main/protection" \
  --jq '{strict:.required_status_checks.strict,contexts:.required_status_checks.contexts,approvals:.required_pull_request_reviews.required_approving_review_count}' \
  | tee -a "$LOG_DIR/protection.summary.txt"

# 1) Eliminar runs fallidos de workflows NO requeridos
for WF in "Release Drafter" "dependabot metadata and labels"; do
  gh api "repos/$REPO/actions/runs?per_page=100" --paginate \
    --jq ".workflow_runs[] | select(.name==\"$WF\" and .conclusion==\"failure\") | [.id,.head_branch,.name] | @tsv" \
  | tee "$LOG_DIR/delete.$(echo "$WF" | tr ' ' '_').tsv" \
  | while IFS=$'\t' read -r ID BR NM; do
      gh api -X DELETE "repos/$REPO/actions/runs/$ID" >/dev/null 2>&1 || true
    done
done

# 2) Rerun sólo si falla un check REQUERIDO en ramas activas
ACTIVE="$(gh api "repos/$REPO/branches?per_page=200" --paginate --jq '.[].name' | sort -u)"
gh api "repos/$REPO/actions/runs?per_page=100" --paginate \
  --jq '.workflow_runs[] | select(.conclusion=="failure") | [.id,.head_branch,.name] | @tsv' \
| while IFS=$'\t' read -r ID BR NM; do
  if printf '%s\n' "$ACTIVE" | grep -qx "$BR"; then
    case "$NM" in
      "CI / build"|"CodeQL Analysis") gh run rerun "$ID" --repo "$REPO" --failed >/dev/null 2>&1 || true ;;
    esac
  fi
done

# 3) Aprobar y auto-merge PRs de Dependabot si existen
gh pr list -R "$REPO" --state open \
  --json number,headRefName,author \
  --jq '.[] | select(.author.login=="dependabot[bot]") | "\(.number)\t\(.headRefName)"' \
| while IFS=$'\t' read -r NUM BR; do
    gh pr review "$NUM" -R "$REPO" --approve >/dev/null 2>&1 || true
    gh pr merge  "$NUM" -R "$REPO" --squash --delete-branch --auto >/dev/null 2>&1 || true
  done

# 4) Resumen runs recientes
gh run list --repo "$REPO" --limit 25 \
  --json databaseId,workflowName,headBranch,status,conclusion,url \
  --jq '.[]|[.databaseId,.workflowName,.headBranch,.status,.conclusion,.url]|@tsv' \
  | tee "$LOG_DIR/actions.summary.final.tsv"

# 5) PRs abiertos con estado de merge y checks
gh pr list -R "$REPO" --state open \
  --json number,title,isDraft,mergeable,mergeStateStatus,statusCheckRollup \
  --jq '.[]|[.number,.title,.isDraft,.mergeable,.mergeStateStatus, ( .statusCheckRollup.state // "unknown")]|@tsv' \
  | tee "$LOG_DIR/prs.open.tsv"

echo "Done. Logs en $LOG_DIR/"
