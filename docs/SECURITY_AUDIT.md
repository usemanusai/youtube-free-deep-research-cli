# Automated Security Auditor

This repository includes a GitHub Actions workflow that runs security scans on every pull request to `main` and weekly on Sunday 03:00 UTC. Results are uploaded to the GitHub Security tab (SARIF) and summarized on PRs. High‑signal findings also open/update GitHub Issues automatically.

## What runs

- Semgrep (multi‑language SAST) with community rules + custom rules from `.semgrep.yml`
- Bandit (Python security linter) on `youtube_chat_cli_main/`
- ESLint (JS/TS) with security plugins for the Next.js dashboard
- Gitleaks (secrets scanning)
- (Optional, weekly) CodeQL deep scan for Python and JavaScript (commented block)

## Interpreting results

- Go to the repo **Security** tab → Code scanning alerts to filter by tool and severity
- Semgrep alerts include CWE/OWASP mappings; open the alert to see the exact file/line and remediation guidance
- Bandit surfaces common Python risks (e.g., `subprocess` with `shell=True`, weak crypto)
- ESLint findings cover JS/TS hygiene and React/Next.js XSS patterns
- Secrets detected by Gitleaks are redacted; rotate any exposed secrets immediately

## Suppressing false positives

- Prefer fixing root causes; if suppression is needed:
  - Semgrep: add a line comment `# nosemgrep: RULE_ID` or tune `.semgrep.yml`
  - Bandit: add `# nosec` on the line or use `-x` to exclude paths
  - ESLint: `// eslint-disable-next-line <rule>` with a brief justification in code review
  - Add ignores for generated/vendor folders as needed

## Running locally

```bash
# Semgrep (needs Python)
pip install semgrep
semgrep --config auto --config ./.semgrep.yml --error

# Bandit (Python)
pip install bandit
bandit -r youtube_chat_cli_main -ll

# ESLint (from dashboard workspace)
cd youtube_chat_cli_main/workspace-*/
npm i -D eslint eslint-plugin-security eslint-formatter-sarif
npx eslint .

# Gitleaks (binary)
# macOS: brew install gitleaks
# Linux: download release from https://github.com/gitleaks/gitleaks
# Windows: choco install gitleaks
```

## Severity & CWE mapping

- Critical/High: exploitable injection, secrets exposure, auth bypass, RCE, SSRF
- Medium: risky patterns with limited reach; defense‑in‑depth items
- Low/Note: hygiene issues and informational findings

Semgrep rules in `.semgrep.yml` include CWE annotations; review alert details for the CWE link and remediation patterns.

