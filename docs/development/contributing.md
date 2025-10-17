# Contributing Guide

Guidelines for contributing to YouTube Free Deep Research CLI.

## Getting Started

### 1. Fork Repository

```bash
# Fork on GitHub, then clone
git clone https://github.com/YOUR_USERNAME/youtube-free-deep-research-cli.git
cd youtube-free-deep-research-cli
```

### 2. Create Development Environment

```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
pip install -r youtube_chat_cli_main/api_requirements.txt

# Install development dependencies
pip install pytest pytest-cov black flake8 mypy
```

### 3. Create Feature Branch

```bash
git checkout -b feature/your-feature-name
```

## Development Workflow

### Code Style

We follow PEP 8 with Black formatting:

```bash
# Format code
black youtube_chat_cli_main

# Check style
flake8 youtube_chat_cli_main

# Type check
mypy youtube_chat_cli_main
```

### Type Hints

All functions must have type hints:

```python
def process_text(text: str, max_length: int = 100) -> str:
    """Process text with maximum length.
    
    Args:
        text: Input text to process
        max_length: Maximum length of output
        
    Returns:
        Processed text
    """
    return text[:max_length]
```

### Docstrings

Use Google-style docstrings:

```python
def calculate_score(data: list[dict]) -> float:
    """Calculate score from data.
    
    Args:
        data: List of data dictionaries
        
    Returns:
        Calculated score
        
    Raises:
        ValueError: If data is empty
        
    Example:
        >>> calculate_score([{"value": 10}])
        10.0
    """
    if not data:
        raise ValueError("Data cannot be empty")
    return sum(d["value"] for d in data) / len(data)
```

## Testing

### Write Tests

```python
# tests/unit/test_example.py
import pytest
from youtube_chat_cli_main.services.llm import OpenRouterLLM

def test_llm_generate():
    """Test LLM generation."""
    llm = OpenRouterLLM()
    response = llm.generate("test")
    assert isinstance(response, str)
    assert len(response) > 0

@pytest.mark.asyncio
async def test_async_operation():
    """Test async operation."""
    result = await some_async_function()
    assert result is not None
```

### Run Tests

```bash
# Run all tests
pytest -q

# Run with coverage
pytest --cov=youtube_chat_cli_main

# Run specific test
pytest tests/unit/test_llm.py -v

# Run with markers
pytest -m "not slow"
```

### Test Coverage

Aim for >80% coverage:

```bash
pytest --cov=youtube_chat_cli_main --cov-report=html
```

## Commit Guidelines

### Commit Message Format

```
<type>: <subject>

<body>

<footer>
```

### Types

- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation
- `style`: Code style
- `refactor`: Code refactoring
- `perf`: Performance improvement
- `test`: Test addition/modification
- `chore`: Build/dependency changes

### Examples

```bash
git commit -m "feat: Add OpenRouter key rotation

- Implement round-robin key rotation
- Add least-used strategy
- Add monitoring and statistics"

git commit -m "fix: Resolve TTS bridge connection issue

Fixes #123"

git commit -m "docs: Update RAG engine guide"
```

## Pull Request Process

### 1. Push to Fork

```bash
git push origin feature/your-feature-name
```

### 2. Create Pull Request

- Title: Clear, descriptive title
- Description: Explain changes and motivation
- Link related issues: "Fixes #123"

### 3. PR Checklist

- [ ] Code follows style guide
- [ ] Tests added/updated
- [ ] Documentation updated
- [ ] No breaking changes
- [ ] All tests pass

### 4. Code Review

- Address reviewer comments
- Push updates to same branch
- Request re-review

### 5. Merge

Once approved, maintainer will merge.

## Adding New Features

### 1. Create Issue

Discuss feature before implementing.

### 2. Design

- Plan architecture
- Consider backward compatibility
- Document design decisions

### 3. Implement

- Follow code style
- Add type hints
- Write tests
- Update documentation

### 4. Test

```bash
# Run all tests
pytest -q

# Test specific feature
pytest tests/unit/test_new_feature.py -v

# Check coverage
pytest --cov=youtube_chat_cli_main
```

### 5. Document

- Update README if needed
- Add docstrings
- Update relevant guides
- Add examples

## Reporting Issues

### Bug Report

```markdown
## Description
Brief description of the bug

## Steps to Reproduce
1. Step 1
2. Step 2
3. Step 3

## Expected Behavior
What should happen

## Actual Behavior
What actually happens

## Environment
- Python version: 3.13
- OS: Windows/Linux/macOS
- Package version: 2.0.1
```

### Feature Request

```markdown
## Description
Brief description of feature

## Motivation
Why this feature is needed

## Proposed Solution
How to implement it

## Alternatives
Other approaches considered
```

## Code Review Checklist

- [ ] Code follows style guide
- [ ] Type hints present
- [ ] Docstrings complete
- [ ] Tests added
- [ ] Tests pass
- [ ] No breaking changes
- [ ] Documentation updated
- [ ] Performance acceptable

## Release Process

1. Update version in `pyproject.toml`
2. Update `CHANGELOG.md`
3. Create release branch
4. Create pull request
5. Merge to main
6. Create GitHub release
7. Publish to PyPI

## Development Tips

1. **Use IDE** - Use PyCharm or VS Code with Python extension
2. **Enable Linting** - Configure flake8 in IDE
3. **Format on Save** - Configure Black in IDE
4. **Run Tests Often** - Run tests before committing
5. **Keep Commits Small** - Easier to review and revert

## Getting Help

- Check [Troubleshooting](troubleshooting.md)
- Review [Architecture](../architecture/overview.md)
- Ask in GitHub Discussions
- Open an issue

## Code of Conduct

- Be respectful
- Be inclusive
- Be constructive
- Report issues appropriately

---

Thank you for contributing!

