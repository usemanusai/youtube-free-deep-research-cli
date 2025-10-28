
import re
import sys

# Patterns to redact
patterns = [
    (r'sk-or-v1-[a-zA-Z0-9]{64,}', 'REDACTED_OPENROUTER_KEY'),
    (r'tvly-[a-zA-Z0-9_-]{20,}', 'REDACTED_TAVILY_KEY'),
    (r'AIza[0-9A-Za-z\-_]{35}', 'REDACTED_GOOGLE_API_KEY'),
    (r'GOCSPX-[a-zA-Z0-9_-]{20,}', 'REDACTED_GOOGLE_SECRET'),
    (r'1079692665134-[a-zA-Z0-9_-]{20,}', 'REDACTED_GOOGLE_CLIENT_ID'),
    (r'ya29\.[a-zA-Z0-9_-]{100,}', 'REDACTED_GOOGLE_OAUTH_TOKEN'),
    (r'[a-zA-Z0-9_-]{20,}@[a-zA-Z0-9_-]{20,}\.iam\.gserviceaccount\.com', 'REDACTED_SERVICE_ACCOUNT'),
    (r'Bearer [a-zA-Z0-9_.-]{50,}', 'Bearer REDACTED_TOKEN'),
    (r'api[_-]?key["\'\s]*[:=]["\'\s]*[a-zA-Z0-9_-]{20,}', 'api_key=REDACTED'),
    (r'secret["\'\s]*[:=]["\'\s]*[a-zA-Z0-9_-]{20,}', 'secret=REDACTED'),
    (r'password["\'\s]*[:=]["\'\s]*[a-zA-Z0-9_-]{20,}', 'password=REDACTED'),
    (r'token["\'\s]*[:=]["\'\s]*[a-zA-Z0-9_.-]{20,}', 'token=REDACTED'),
]

try:
    with open(sys.argv[1], 'r', encoding='utf-8', errors='ignore') as f:
        content = f.read()
    
    modified = False
    for pattern, replacement in patterns:
        new_content = re.sub(pattern, replacement, content, flags=re.IGNORECASE)
        if new_content != content:
            modified = True
            content = new_content
    
    if modified:
        with open(sys.argv[1], 'w', encoding='utf-8') as f:
            f.write(content)
except Exception as e:
    pass
