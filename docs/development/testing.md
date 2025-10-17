# Testing Guide

Comprehensive testing guide for YouTube Free Deep Research CLI.

## Test Structure

```
tests/
├── __init__.py
├── unit/                    # Unit tests
│   ├── test_llm.py
│   ├── test_tts.py
│   ├── test_rag.py
│   └── test_services.py
├── integration/             # Integration tests
│   ├── test_api.py
│   ├── test_workflows.py
│   └── test_end_to_end.py
├── fixtures/                # Test fixtures
│   ├── conftest.py
│   ├── mock_data.py
│   └── factories.py
└── __main__.py
```

## Running Tests

### Run All Tests

```bash
pytest -q
```

### Run Specific Test File

```bash
pytest tests/unit/test_llm.py -v
```

### Run Specific Test

```bash
pytest tests/unit/test_llm.py::test_llm_generate -v
```

### Run with Coverage

```bash
pytest --cov=youtube_chat_cli_main --cov-report=html
```

### Run with Markers

```bash
# Run only fast tests
pytest -m "not slow"

# Run only unit tests
pytest -m "unit"

# Run only integration tests
pytest -m "integration"
```

## Writing Tests

### Unit Test Example

```python
# tests/unit/test_llm.py
import pytest
from youtube_chat_cli_main.services.llm import OpenRouterLLM

class TestOpenRouterLLM:
    """Test OpenRouter LLM service."""
    
    @pytest.fixture
    def llm(self):
        """Create LLM instance."""
        return OpenRouterLLM()
    
    def test_generate(self, llm):
        """Test text generation."""
        response = llm.generate("test")
        assert isinstance(response, str)
        assert len(response) > 0
    
    def test_generate_with_model(self, llm):
        """Test generation with specific model."""
        response = llm.generate(
            "test",
            model="openrouter/gpt-3.5-turbo"
        )
        assert isinstance(response, str)
    
    def test_invalid_model(self, llm):
        """Test with invalid model."""
        with pytest.raises(ValueError):
            llm.generate("test", model="invalid-model")
```

### Async Test Example

```python
# tests/unit/test_async.py
import pytest

@pytest.mark.asyncio
async def test_async_operation():
    """Test async operation."""
    result = await some_async_function()
    assert result is not None

@pytest.mark.asyncio
async def test_async_with_fixture(async_client):
    """Test async with fixture."""
    response = await async_client.get("/health/live")
    assert response.status_code == 200
```

### Mocking Example

```python
# tests/unit/test_with_mocks.py
from unittest.mock import Mock, patch
import pytest

def test_with_mock():
    """Test with mocked dependency."""
    with patch('youtube_chat_cli_main.services.llm.requests.post') as mock_post:
        mock_post.return_value.json.return_value = {"response": "test"}
        
        llm = OpenRouterLLM()
        response = llm.generate("test")
        
        assert response == "test"
        mock_post.assert_called_once()

@pytest.fixture
def mock_llm():
    """Mock LLM service."""
    with patch('youtube_chat_cli_main.services.llm.OpenRouterLLM') as mock:
        mock.return_value.generate.return_value = "mocked response"
        yield mock
```

## Test Fixtures

### Conftest Example

```python
# tests/fixtures/conftest.py
import pytest
from youtube_chat_cli_main.api.server import create_app

@pytest.fixture
def app():
    """Create test app."""
    app = create_app()
    app.config['TESTING'] = True
    return app

@pytest.fixture
def client(app):
    """Create test client."""
    return app.test_client()

@pytest.fixture
async def async_client(app):
    """Create async test client."""
    async with app.test_client() as client:
        yield client

@pytest.fixture
def mock_data():
    """Provide mock data."""
    return {
        "query": "test query",
        "response": "test response",
        "tokens": 100
    }
```

## Test Markers

### Define Markers

```python
# pytest.ini
[pytest]
markers =
    unit: Unit tests
    integration: Integration tests
    slow: Slow tests
    api: API tests
    rag: RAG tests
```

### Use Markers

```python
@pytest.mark.unit
def test_unit():
    pass

@pytest.mark.integration
def test_integration():
    pass

@pytest.mark.slow
def test_slow():
    pass
```

## Coverage

### Generate Coverage Report

```bash
# Terminal report
pytest --cov=youtube_chat_cli_main

# HTML report
pytest --cov=youtube_chat_cli_main --cov-report=html

# Open report
open htmlcov/index.html
```

### Coverage Targets

- **Overall**: >80%
- **Critical paths**: >90%
- **Services**: >85%
- **API**: >85%

## Integration Tests

### API Integration Test

```python
# tests/integration/test_api.py
import pytest

@pytest.mark.integration
def test_chat_endpoint(client):
    """Test chat endpoint."""
    response = client.post('/api/chat/message', json={
        "session_id": "test-session",
        "message": "test message"
    })
    assert response.status_code == 200
    assert "response" in response.json

@pytest.mark.integration
def test_file_upload(client):
    """Test file upload."""
    with open('test.pdf', 'rb') as f:
        response = client.post('/api/files/upload', data={'file': f})
    assert response.status_code == 200
    assert "file_id" in response.json
```

### End-to-End Test

```python
# tests/integration/test_end_to_end.py
@pytest.mark.integration
def test_full_workflow(client):
    """Test complete workflow."""
    # 1. Upload file
    with open('test.pdf', 'rb') as f:
        upload_response = client.post('/api/files/upload', data={'file': f})
    file_id = upload_response.json['file_id']
    
    # 2. Search
    search_response = client.post('/api/search/vector', json={
        "query": "test"
    })
    assert search_response.status_code == 200
    
    # 3. Chat
    chat_response = client.post('/api/chat/message', json={
        "message": "test"
    })
    assert chat_response.status_code == 200
```

## Performance Testing

### Load Test

```python
# tests/performance/test_load.py
import pytest
import time

@pytest.mark.performance
def test_concurrent_requests(client):
    """Test concurrent requests."""
    import concurrent.futures
    
    def make_request():
        return client.get('/health/live')
    
    with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
        futures = [executor.submit(make_request) for _ in range(100)]
        results = [f.result() for f in concurrent.futures.as_completed(futures)]
    
    assert all(r.status_code == 200 for r in results)
```

## Debugging Tests

### Verbose Output

```bash
pytest -v
```

### Show Print Statements

```bash
pytest -s
```

### Drop into Debugger

```python
def test_with_debugger():
    import pdb; pdb.set_trace()
    # Code here
```

### Use pytest-pdb

```bash
pytest --pdb
```

## CI/CD Integration

### GitHub Actions

```yaml
# .github/workflows/tests.yml
name: Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    strategy:
      matrix:
        python-version: ['3.13']
    
    steps:
      - uses: actions/checkout@v2
      - uses: actions/setup-python@v2
        with:
          python-version: ${{ matrix.python-version }}
      - run: pip install -r requirements.txt
      - run: pytest --cov=youtube_chat_cli_main
```

## Best Practices

1. **Test Isolation** - Each test should be independent
2. **Clear Names** - Test names should describe what they test
3. **Arrange-Act-Assert** - Structure tests clearly
4. **Mock External** - Mock external API calls
5. **Test Edge Cases** - Test error conditions
6. **Keep Tests Fast** - Avoid slow operations
7. **Use Fixtures** - Reuse common setup
8. **Document Tests** - Add docstrings

## Troubleshooting

### Tests Fail Locally but Pass in CI

```bash
# Run in isolated environment
python -m venv test_env
source test_env/bin/activate
pip install -r requirements.txt
pytest
```

### Flaky Tests

```bash
# Run test multiple times
pytest --count=10 tests/unit/test_flaky.py

# Run with different random seed
pytest --randomly-seed=12345
```

### Slow Tests

```bash
# Find slowest tests
pytest --durations=10
```

---

See [Contributing](contributing.md) for contribution guidelines.

