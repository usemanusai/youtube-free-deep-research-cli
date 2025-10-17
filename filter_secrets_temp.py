
import re
import sys

# Read the file content
with open(sys.argv[1], 'r', encoding='utf-8', errors='ignore') as f:
    content = f.read()

# Remove OpenRouter API keys (sk-or-v1-*)
content = re.sub(r'sk-or-v1-[a-zA-Z0-9]{64,}', 'REDACTED_OPENROUTER_KEY', content)

# Remove PyPI tokens (pypi-*)
content = re.sub(r'pypi-[a-zA-Z0-9_-]+', 'REDACTED_PYPI_TOKEN', content)

# Remove NPM tokens (npm_*)
content = re.sub(r'npm_[a-zA-Z0-9_-]+', 'REDACTED_NPM_TOKEN', content)

# Remove generic API keys
content = re.sub(r'["']?api[_-]?key["']?\s*[:=]\s*["']?[a-zA-Z0-9_-]+["']?', 'api_key=REDACTED', content, flags=re.IGNORECASE)

# Remove Bearer tokens
content = re.sub(r'Bearer\s+[a-zA-Z0-9_.-]+', 'Bearer REDACTED', content)

# Write back
with open(sys.argv[1], 'w', encoding='utf-8') as f:
    f.write(content)
