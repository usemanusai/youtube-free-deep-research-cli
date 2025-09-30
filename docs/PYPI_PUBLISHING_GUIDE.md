# 📦 PyPI Publishing Guide for YouTube Chat CLI

This guide provides step-by-step instructions for publishing the YouTube Chat CLI package to PyPI.

## 🔐 Prerequisites

### 1. PyPI Account Setup
1. Create an account at [PyPI.org](https://pypi.org/account/register/)
2. Verify your email address
3. Enable two-factor authentication (recommended)

### 2. API Token Generation
1. Go to [PyPI Account Settings](https://pypi.org/manage/account/)
2. Scroll to "API tokens" section
3. Click "Add API token"
4. Set scope to "Entire account" (or specific to this project after first upload)
5. Copy the generated token (starts with `pypi-`)

### 3. Environment Setup
```bash
# Set your PyPI token as an environment variable
export PYPI_TOKEN="pypi-your-token-here"

# For TestPyPI (optional, for testing)
export PYPI_TEST_TOKEN="pypi-your-test-token-here"
```

## 🚀 Publishing Process

### Method 1: Using the Automated Script (Recommended)

```bash
# Test on TestPyPI first (recommended)
python scripts/publish_to_pypi.py --test

# Publish to PyPI
python scripts/publish_to_pypi.py
```

### Method 2: Manual Publishing

#### Step 1: Install Build Tools
```bash
pip install --upgrade build twine
```

#### Step 2: Clean Previous Builds
```bash
rm -rf build/ dist/ *.egg-info/
```

#### Step 3: Build the Package
```bash
python -m build
```

#### Step 4: Validate the Package
```bash
python -m twine check dist/*
```

#### Step 5: Upload to PyPI
```bash
# Test upload (optional)
python -m twine upload --repository testpypi dist/*

# Production upload
python -m twine upload dist/*
```

## 🔒 Security Best Practices

### 1. Token Management
- **Never commit tokens to version control**
- Use environment variables or secure secret managers
- Rotate tokens regularly
- Use project-scoped tokens when possible

### 2. Secure Token Storage
```bash
# Option 1: Environment variables (temporary)
export PYPI_TOKEN="your-token"

# Option 2: .pypirc file (persistent, but secure the file)
cat > ~/.pypirc << EOF
[distutils]
index-servers = pypi testpypi

[pypi]
username = __token__
password = your-pypi-token-here

[testpypi]
repository = https://test.pypi.org/legacy/
username = __token__
password = your-test-pypi-token-here
EOF

chmod 600 ~/.pypirc  # Secure the file
```

### 3. CI/CD Integration
For automated publishing in GitHub Actions:

```yaml
# .github/workflows/publish.yml
name: Publish to PyPI

on:
  release:
    types: [published]

jobs:
  publish:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v3
    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.9'
    - name: Install dependencies
      run: |
        python -m pip install --upgrade pip
        pip install build twine
    - name: Build package
      run: python -m build
    - name: Publish to PyPI
      env:
        TWINE_USERNAME: __token__
        TWINE_PASSWORD: ${{ secrets.PYPI_TOKEN }}
      run: twine upload dist/*
```

## ✅ Pre-Publication Checklist

- [ ] Version number updated in all files (pyproject.toml, setup.py, __init__.py)
- [ ] README.md updated with installation instructions
- [ ] CHANGELOG.md updated with new version
- [ ] All tests passing
- [ ] Package builds without errors
- [ ] Package validates with twine check
- [ ] PyPI token configured securely
- [ ] Tested on TestPyPI (optional but recommended)

## 🧪 Testing Your Package

### After Publishing to TestPyPI
```bash
# Install from TestPyPI
pip install --index-url https://test.pypi.org/simple/ youtube-chat-cli

# Test basic functionality
youtube-chat --help
```

### After Publishing to PyPI
```bash
# Install from PyPI
pip install youtube-chat-cli

# Test installation
youtube-chat --version
youtube-chat --help
```

## 🐛 Troubleshooting

### Common Issues

1. **"File already exists" error**
   - You cannot overwrite existing versions on PyPI
   - Increment the version number and rebuild

2. **Authentication errors**
   - Check your token is correct and not expired
   - Ensure token has appropriate permissions

3. **Package validation errors**
   - Run `twine check dist/*` to see specific issues
   - Common issues: missing README, invalid metadata

4. **Import errors after installation**
   - Check package structure in `src/`
   - Verify entry points in pyproject.toml

### Getting Help
- [PyPI Help](https://pypi.org/help/)
- [Python Packaging Guide](https://packaging.python.org/)
- [Twine Documentation](https://twine.readthedocs.io/)

## 📈 Post-Publication

### 1. Verify Installation
```bash
pip install youtube-chat-cli
youtube-chat --version
```

### 2. Update Documentation
- Update README badges with PyPI links
- Create GitHub release
- Update project documentation

### 3. Monitor Package
- Check download statistics on PyPI
- Monitor for issues and user feedback
- Plan future releases

## 🔄 Version Management

### Semantic Versioning
- **MAJOR.MINOR.PATCH** (e.g., 2.1.0)
- **MAJOR**: Breaking changes
- **MINOR**: New features, backward compatible
- **PATCH**: Bug fixes, backward compatible

### Release Process
1. Update version in all files
2. Update CHANGELOG.md
3. Create git tag: `git tag v2.1.0`
4. Push tag: `git push origin v2.1.0`
5. Publish to PyPI
6. Create GitHub release
