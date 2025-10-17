# Helios Module — Phase 1 Research (Automated Dependency Updates)

Date of Execution: 2025-10-03
Scope: Scheduled, zero-cost, GitHub-native (preferred) dependency scanning for Python (pip/requirements.txt) and Node.js (npm/package.json) with actionable GitHub Issues.

## Executive Summary
- Recommended approach: GitHub Actions workflow that runs weekly to:
  - Python: `pip-audit` (vulnerabilities) + `pip list --outdated` (updates)
  - Node: `npm audit --json` (vulnerabilities) + `npm outdated --json` (updates)
  - Aggregate JSON results ➜ generate a Markdown report ➜ create/update a GitHub Issue with labels `dependencies` and `security` (if vulns found).
- Rationale: 100% free, no external SaaS, supports Python & Node, easy setup, runs in <5 minutes on ubuntu-latest, outputs actionable Issue without auto-changing code.
- Alternatives: Dependabot and Renovate are excellent for PR automation; we can optionally enable Dependabot with `.github/dependabot.yml` for ongoing PRs, but the weekly CI Issue provides unified visibility and avoids PR noise.

## Tooling Landscape (2025)
- Dependabot (GitHub-native)
  - Features: Security alerts, security updates, version updates, PRs; supports Python, npm. Weekly scheduling supported; recent changelog adds cron expressions for schedules.
  - Costs: Included in GitHub Free. No runner minutes for native Dependabot; but separate from Actions workflow.
  - Pros: Native PRs, precise ecosystem support. Cons: Focused on PRs; not a single consolidated weekly Issue.
- Renovate (Mend Renovate)
  - Options: Hosted GitHub App (free for public) or self-hosted (via GH Actions). Generates PRs across ecosystems, very configurable.
  - Pros: Powerful monorepo handling. Cons: More config complexity; PR-centric, not Issue-centric.
- Dependency Review Action (GitHub)
  - Purpose: Scans dependency changes in pull requests; prevents introducing new vulns. Not designed for scheduled repo-wide audits.
- pip-audit (PyPA / Trail of Bits)
  - Scans Python dependencies; outputs JSON/SARIF/Markdown; has a maintained GitHub Action. Free, fast. Good for scheduled audits.
- Safety CLI
  - Alternative Python scanner; commercial offering with free CLI. Good, but pip-audit is PyPA-backed and sufficient.
- npm audit
  - Built-in npm security scan; `--json` output for programmatic parsing. Works well in CI. Noise can be filtered by severity.
- Trivy
  - Comprehensive scanner (images, fs, repos) with JSON/SARIF; can scan Node & Python manifests. Great for security, but does not report "outdated" versions. Heavier footprint than needed for this repo.

## Evaluation (against requirements)
- Cost: All selected tools are free and run on GitHub-hosted runners.
- Language coverage: Yes (Python + Node).
- Ease of setup: Single workflow file; minimal scripting with `jq` (available on ubuntu-latest).
- Actionability: Creates/updates a GitHub Issue with a Markdown table of findings; labels applied.
- Performance: Each scan completes quickly on typical repos; expected < 5 minutes total with caching of npm.
- Maintenance: Tools are actively maintained in 2025 (pip-audit, npm). No external SaaS accounts required.

## Proposed Workflow Design (weekly)
- Trigger: `cron: '0 2 * * 1'` (Mondays 02:00 UTC)
- Jobs:
  1) Python scan
     - Set up Python 3.13
     - Install `pip-audit`
     - Run `pip-audit --requirement requirements.txt --format json > python-vulns.json`
     - Run `python -m pip list --outdated --format=json > python-outdated.json`
  2) Node scan
     - Discover dashboard path: `workspace-*` subdir with package.json
     - `npm ci` then `npm audit --json > node-vulns.json` and `npm outdated --json > node-outdated.json`
  3) Aggregate & issue
     - Use a small script/jq to build a Markdown report summarizing found vulnerabilities and outdated packages
     - Idempotency: search for an existing open Issue with title prefix `Weekly Dependency Scan - [DATE]`; update if exists else create new
     - Apply labels: `dependencies`; add `security` if vulnerabilities detected

## Issue Body (example fields)
- Title: `Weekly Dependency Scan - 2025-10-03 - 3 vulnerabilities found`
- Body sections:
  - Summary (counts by severity for Python/Node)
  - Python Vulnerabilities (table: package, version, advisory/CVE, fix)
  - Node Vulnerabilities (table)
  - Outdated Packages (Python & Node tables: name, current, latest, type)
  - Next steps: review and update via PRs; optional Dependabot enablement

## Idempotency Strategy
- Use `actions/github-script` to search for an existing open Issue with the same date-based title; update that Issue if found, otherwise create a new one.
- Labels applied consistently. Avoids duplicate weekly Issues on retries.

## Alternatives Considered
- Dependabot alone: creates multiple PRs, good for automation; does not produce a consolidated weekly Issue report across ecosystems.
- Renovate: powerful PR engine and dashboard; requires app or more config; still PR-centric.
- Trivy-only: excellent for CVEs, but doesn't handle "outdated" version reporting; we'd still need extra steps.

## Example Snippets (to be used in Phase 2)
- Python:
  - `pip-audit --requirement requirements.txt --format json`
  - `python -m pip list --outdated --format=json`
- Node:
  - `npm ci && npm audit --json`
  - `npm outdated --json`
- Create Issue (github-script): search & create/update with labels.

## Performance Expectations
- `pip-audit` on medium requirements.txt: typically < 1 minute
- `npm audit` + `npm outdated` after `npm ci`: typically < 2 minutes
- Aggregation + issue creation: seconds
- Total: < 5 minutes expected on ubuntu-latest

## Limitations & Edge Cases
- If package managers cannot resolve/install, scans may fail; workflow should continue and note failure in the report.
- npm audit noise: can be high; we summarize by severity and top advisories.
- If no Node workspace directory exists or no package.json found, Node job skips gracefully.
- Private registries requiring auth are out of scope for this zero-config setup.

## Sources (representative)
- GitHub Docs: Dependabot options & security updates; Dependency Review Action; Workflow syntax; permissions
- Renovate GitHub & docs (hosted vs self-hosted)
- pip-audit GitHub Action & PyPI
- npm audit & npm outdated docs/examples
- Trivy action & docs (formats)

---
This document completes Phase 1 research for Helios Module. On approval, Phase 2 will generate `.github/workflows/dependency-check.yml`, optional `.github/dependabot.yml`, and documentation updates, following the proposed design.

