# Automated Security Auditor – Phase 1 Research (Integration Prompt #8)

Date of Execution: 2025-10-03 (established via live web sources)

Project: youtube-chat-cli-main (Python 3.13 / FastAPI, LangChain/LangGraph, SQLAlchemy, Playwright; Next.js 15 / React 19)

## Executive Summary

A multi-language, open-source, CI-native SAST program can be achieved with a Semgrep-first approach augmented by Bandit (Python-specific hardening), ESLint security plugins (JS/TS hygiene), Gitleaks (secrets), and CodeQL (deep dataflow for critical paths, optional). This mix provides broad coverage across OWASP Top 10, CWE Top 25, and modern AI/LLM-specific risks (prompt injection, SSRF via tool calls, unsafe subprocess usage), with SARIF output for GitHub Security integration and automated issue creation. To keep runtime under ~10 minutes on GitHub Actions, scope CodeQL to a weekly job (optional) while Semgrep runs on PRs and the weekly schedule.

Recommended stack:
- Primary SAST: Semgrep OSS (multi-language, tunable rules, good perf)
- Python depth: Bandit (fast, low-noise Python security checks)
- JS/TS hygiene: ESLint + security rules (eslint-plugin-security, eslint-plugin-react, Next.js guidelines)
- Secrets: Gitleaks
- Optional (weekly): CodeQL (deeper inter-procedural taint tracking)

## Current Threat Landscape (highlights)
- OWASP Top 10 (latest cycle) emphasizes access control, cryptographic failures, injection (SQL/NoSQL/command), SSRF, and software/ data integrity issues.
- CWE Top 25 continues to feature injection, buffer/array issues, and authorization problems.
- FastAPI/ASGI ecosystems: risks include trust of request bodies, file upload handling, path traversal from user file paths, insecure CORS, SSRF via requests, command/subprocess misuse, JWT misconfiguration.
- Next.js: XSS from dangerouslySetInnerHTML, prototype pollution via third-party libs, CORS/CSRF misconfiguration, SSRF in server actions, open redirects.
- LLM apps: prompt injection, over-trusting tool outputs and unvalidated external content (web scraping/search), data exfiltration via system prompt leaks.
- Supply chain: dependency confusion, typosquatting in PyPI/npm, malicious postinstall scripts.

## Tooling Comparison (concise)

| Tool | Languages | Strengths | Limits/Notes | GH Actions | Perf |
|---|---|---|---|---|---|
| Semgrep OSS | Python, JS/TS, many | Fast, tunable rules, wide rulesets (community + custom), SARIF | Deep inter-procedural analysis limited vs CodeQL | First-class | Fast (<5–7m typical) |
| Bandit | Python | Python-specific vulns; simple config | Limited multi-file dataflow | Easy | Very fast (<1m) |
| ESLint (+security plugins) | JS/TS | Lint + security smells for React/Next.js | Not a full SAST | Easy | Fast (<2–4m) |
| Gitleaks | Any | Secrets detection, CI friendly | False positives need tuning | Easy | Fast (<1–2m) |
| CodeQL | Many | Deep dataflow/taint; SARIF | Heavier, rule authoring learning curve | Native | Moderate–heavy (recommended weekly) |
| SonarQube CE | Many | Dashboarding, quality gates | GitHub setup heavier; limited rules vs paid | Possible | Variable |

Conclusion: Use Semgrep+Bandit+ESLint+Gitleaks on PRs and weekly. Add CodeQL as optional weekly deep scan if runtime budget allows.

## Coverage Mapping (examples)
- SQL Injection (SQLAlchemy/ORM): Semgrep (Python rules), CodeQL (optional), Bandit (limited). Guidance: parameterized queries, ORM query builders, avoid f-strings/format on SQL.
- Command Injection (subprocess/os.system): Bandit + Semgrep. Guidance: avoid shell=True; pass argv list; validate inputs.
- XSS (Next.js/React): ESLint rules, Semgrep JS rules. Guidance: avoid dangerouslySetInnerHTML; encode/escape untrusted content; use Next.js security headers.
- Insecure Deserialization: Semgrep Python rules; CodeQL optional. Guidance: avoid pickle/unsafe yaml.load; prefer safe loaders.
- Secrets exposure: Gitleaks (+ detect-secrets optional). Guidance: .env in .gitignore; key rotation.
- Prompt Injection (LLM): Semgrep custom rules + heuristic checks in app code (validate sources, tool outputs). Guidance: sanitize untrusted content; restrict tool capabilities; content filters.
- SSRF: Semgrep Python/JS rules + custom; CodeQL optional. Guidance: allowlist hosts; block localhost/metadata IPs; restricted schemes.
- Path Traversal: Semgrep Python rules; Bandit. Guidance: Pathlib resolve; join + sandbox; validate filenames.
- AuthN/Z flaws: Semgrep custom rules for FastAPI dependencies/guards; CodeQL optional. Guidance: explicit dependency injection of auth; test negative paths.

## Configuration Recommendations
- Semgrep: Start with default community rulesets for python, javascript, security; add targeted rules for FastAPI, SQLAlchemy, subprocess, requests, Next.js SSR. Configure severity mapping and ignore patterns for generated/third-party files.
- Bandit: Enable high + medium severity; exclude tests if noisy; target app directories.
- ESLint: Enable security plugins; ensure Next.js recommended configs; disallow dangerouslySetInnerHTML without justification.
- Gitleaks: Use maintained default rules; add allowlist for false positives; scan entire repo excluding node_modules, .venv, etc.
- CodeQL (optional weekly): Enable python + javascript queries; cache databases between runs to save time.

## CI/CD Integration Patterns
- Triggers: PR to main; weekly schedule (Sunday 03:00 UTC); workflow_dispatch.
- Jobs: setup-python 3.13; setup-node 20.x; install Semgrep/Bandit/Gitleaks/ESLint; run scans in parallel; collect SARIF; upload to GitHub Security tab.
- Performance: run Semgrep with –config auto + project rules; limit CodeQL to weekly; parallelize matrix for languages if needed.
- Deduplication: maintain a small JSON state of previously filed issues by rule+location; update/skip duplicates.

## Issue Creation Automation
- Parse SARIF/JSON outputs; classify severity (Critical/High/Medium/Low); map to CWE when provided.
- Auto-create GitHub Issues with labels security, automated, and severity. Include remediation guidance and code examples.
- On PRs, post a summarized comment with top issues and links to detailed artifacts.

## FastAPI and Next.js – Common Vulnerabilities and Fixes (examples)

Python (command injection risk):
```python
# Vulnerable
subprocess.run(f"ffmpeg -i {user_path} out.mp3", shell=True)

# Safer
subprocess.run(["ffmpeg", "-i", user_path, "out.mp3"], check=True)
```

Python (SSRF via requests):
```python
# Vulnerable
requests.get(user_url, timeout=5)

# Safer: allowlist + parsed scheme/host check before requesting
```

Next.js (XSS):
```tsx
// Vulnerable
div dangerouslySetInnerHTML={{ __html: userHtml }} />

// Safer: render sanitized output or avoid raw HTML
```

FastAPI (auth dependency):
```python
# Ensure protected routes include dependency(verify_jwt)
@router.get("/items", dependencies=[Depends(verify_jwt)])
```

## Selected Tooling Justification
- Semgrep provides the best OSS balance of coverage, speed, tunability, and SARIF output for both Python and JS/TS.
- Bandit adds targeted Python checks with extremely low overhead.
- ESLint security plugins enforce React/Next.js hygiene that static analyzers may miss.
- Gitleaks is a proven OSS secrets scanner for CI.
- CodeQL can be added for deeper weekly analysis with manageable runtime when tuned.

## Links (representative official resources)
- Semgrep: https://semgrep.dev/; GitHub Action: returntocorp/semgrep-action
- Bandit: https://bandit.readthedocs.io/
- ESLint security: https://eslint.org/; plugins: eslint-plugin-security, eslint-plugin-react
- Gitleaks: https://gitleaks.io/
- CodeQL: https://codeql.github.com/; github/codeql-action
- OWASP: https://owasp.org/
- CWE Top 25: https://cwe.mitre.org/top25/archive/2025

---

Recommendation: Proceed with Semgrep+Bandit+ESLint+Gitleaks on PRs and weekly schedule, with SARIF uploads and automated issue creation. Add optional weekly CodeQL job if CI time budget allows.

