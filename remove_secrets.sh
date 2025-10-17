#!/bin/bash
# Remove all API keys and secrets from git history

echo "Starting secret removal process..."

# Create a filter script
cat > /tmp/filter-secrets.sh << 'EOF'
#!/bin/bash
# Remove OpenRouter API keys
sed -i 's/sk-or-v1-[a-zA-Z0-9]*/REDACTED_OPENROUTER_KEY/g' "$1"

# Remove PyPI tokens
sed -i 's/pypi-[a-zA-Z0-9]*/REDACTED_PYPI_TOKEN/g' "$1"

# Remove NPM tokens
sed -i 's/npm_[a-zA-Z0-9]*/REDACTED_NPM_TOKEN/g' "$1"

# Remove generic API keys
sed -i 's/api[_-]key["\s]*[:=]["\s]*[a-zA-Z0-9_-]*/api_key=REDACTED/gi' "$1"

# Remove Bearer tokens
sed -i 's/Bearer [a-zA-Z0-9_-]*/Bearer REDACTED/g' "$1"
EOF

chmod +x /tmp/filter-secrets.sh

# Run git filter-branch
echo "Filtering git history..."
git filter-branch -f --tree-filter '/tmp/filter-secrets.sh "$GIT_COMMIT"' -- --all

# Clean up
rm /tmp/filter-secrets.sh

echo "Secret removal complete!"
echo "Now run: git push origin --force --all"

