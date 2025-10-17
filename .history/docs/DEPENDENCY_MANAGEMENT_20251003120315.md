# Helios Module — Automated Dependency Updates and Security Scans

This document explains how the Helios automation keeps Python and Node.js dependencies healthy using a weekly GitHub Actions workflow and optional Dependabot PRs.

## What Helios does

- Runs every Monday at 02:00 UTC (and can be triggered manually)
- Scans for:
  - Python vulnerabilities (pip-audit) and outdated packages (pip list --outdated)
  - Node.js vulnerabilities (npm audit) and outdated packages (npm outdated) in workspace-* subprojects and/or the repository root
- Aggregates findings into a Markdown report
- Creates or updates a single GitHub Issue titled "Helios: Weekly Dependency Audit Report" with labels `dependencies` and `security`
- Uploads JSON artifacts for deeper inspection

## Files added

- .github/workflows/dependency-check.yml — Weekly CI job with manual trigger
- .github/dependabot.yml — Optional PR-based updates for npm and pip ecosystems

## Manual trigger

1. Navigate to GitHub → Actions → Helios Dependency Checks
2. Click "Run workflow"
3. Wait for the job to finish; it will create/update the Helios issue and attach artifacts

## Interpreting the results

- The issue body shows, per ecosystem and per requirements/package.json file:
  - Total vulnerabilities detected
  - List of packages that are outdated, with current → latest version
- Download the `helios-artifacts` archive from the job run to inspect JSON files:
  - Python: artifacts/python/<requirements>.pip_audit.json and <requirements>.outdated.json
  - Node: artifacts/node/<path_to_package.json>.audit.json and .outdated.json

## Suppressing noise / triage tips

- pip-audit and npm audit are intentionally surfaced; not all findings are immediately actionable.
- For packages pinned to older versions for compatibility, note the reason in a CODEOWNERS comment or in the issue thread.
- Consider enabling Dependabot PRs (already configured) to automatically raise PRs for patch/minor updates. Major updates can be grouped and scheduled.

## Troubleshooting

- The workflow expects at least one requirements.txt/in file or one package.json. If none are found, corresponding sections will report "No artifacts found".
- If `npm ci` fails due to a missing lockfile, the workflow falls back to `npm install`.
- If audit commands fail, the steps continue and still produce a report with best-effort data.
- If no issue appears, check Action logs for permissions: the workflow needs `issues: write`.

## Local reproduction (optional)

- Python
  - pip install pip-audit
  - pip-audit -r requirements.txt -f json > local.pip_audit.json
  - pip list --outdated --format=json > local.outdated.json
- Node
  - npm audit --json > local.audit.json
  - npm outdated --json > local.outdated.json

## Maintenance

- Adjust the cron schedule in .github/workflows/dependency-check.yml as needed
- Add additional requirements files or workspaces; the workflow auto-discovers them via git ls-files
- Labels and issue title can be customized in the workflow script block

