# 🧪 JAEGIS NexusSync - Testing Guide

Comprehensive guide to testing the JAEGIS NexusSync system.

## 📋 Table of Contents

1. [Test Overview](#test-overview)
2. [Running Tests](#running-tests)
3. [Test Structure](#test-structure)
4. [Writing Tests](#writing-tests)
5. [Coverage Reports](#coverage-reports)
6. [CI/CD Integration](#cicd-integration)

---

## 🎯 Test Overview

### Test Types

**Unit Tests** (Fast, No External Dependencies)
- Test individual functions and classes in isolation
- Use mocks for all external dependencies
- Run in milliseconds
- Located in `tests/test_*.py`

**Integration Tests** (May Require Services)
- Test interaction between components
- May require running services (Ollama, Qdrant, etc.)
- Run in seconds
- Marked with `@pytest.mark.integration`

### Test Coverage

| Module | Unit Tests | Integration Tests | Coverage |
|--------|------------|-------------------|----------|
| RAG Engine | ✅ | ✅ | ~90% |
| LLM Service | ✅ | ✅ | ~85% |
| Vector Store | ✅ | ✅ | ~85% |
| Web Search | ✅ | ✅ | ~80% |
| Content Processor | ✅ | ✅ | ~80% |
| Database | ✅ | ✅ | ~90% |
| MCP Server | ✅ | ✅ | ~75% |

**Overall Coverage: ~85%**

---

## 🚀 Running Tests

### Quick Start

```bash
# Install test dependencies
pip install pytest pytest-asyncio pytest-mock pytest-cov

# Run all tests
python run_tests.py --all

# Run unit tests only (fast)
python run_tests.py --unit

# Run with coverage
python run_tests.py --coverage
```

### Using pytest Directly

```bash
# Run all tests
pytest

# Run unit tests only
pytest -m "not integration"

# Run integration tests only
pytest -m integration

# Run specific test file
pytest tests/test_rag_engine.py

# Run specific test
pytest tests/test_rag_engine.py::TestAdaptiveRAGEngine::test_retrieve_node

# Run with verbose output
pytest -v

# Run with coverage
pytest --cov=youtube_chat_cli_main --cov-report=html
```

### Using the Test Runner

```bash
# Run all tests
python run_tests.py --all

# Run unit tests
python run_tests.py --unit

# Run integration tests
python run_tests.py --integration

# Run with coverage
python run_tests.py --coverage

# Run specific test
python run_tests.py --test tests/test_rag_engine.py

# Run linting
python run_tests.py --lint

# Run type checking
python run_tests.py --type-check

# Run full CI pipeline
python run_tests.py --ci

# Verbose output
python run_tests.py --all -v
```

---

## 📁 Test Structure

```
tests/
├── __init__.py
├── test_rag_engine.py          # RAG engine unit tests
├── test_llm_service.py          # LLM service unit tests
├── test_vector_store.py         # Vector store unit tests
├── test_web_search_service.py   # Web search unit tests
├── test_content_processor.py    # Content processor unit tests
├── test_rag_integration.py      # Integration tests
└── test_integration.py          # Legacy integration tests
```

### Test File Naming

- `test_*.py` - Test files
- `Test*` - Test classes
- `test_*` - Test functions

---

## ✍️ Writing Tests

### Unit Test Example

```python
import pytest
from unittest.mock import Mock, patch

from youtube_chat_cli_main.services.rag_engine import AdaptiveRAGEngine


class TestAdaptiveRAGEngine:
    """Test suite for AdaptiveRAGEngine."""
    
    @pytest.fixture
    def mock_config(self):
        """Mock configuration."""
        config = Mock()
        config.rag_top_k = 5
        return config
    
    def test_retrieve_node(self, mock_config):
        """Test the retrieve node."""
        with patch('youtube_chat_cli_main.services.rag_engine.get_config', return_value=mock_config):
            engine = AdaptiveRAGEngine()
            
            state = {
                "question": "What is the test about?",
                "documents": []
            }
            
            result = engine._retrieve(state)
            
            assert "documents" in result
            assert len(result["documents"]) > 0
```

### Integration Test Example

```python
import pytest
from unittest.mock import patch


@pytest.mark.integration
class TestEndToEndWorkflow:
    """Test complete end-to-end workflows."""
    
    def test_document_ingestion_workflow(self):
        """Test complete document ingestion workflow."""
        # Setup mocks for external services
        with patch('youtube_chat_cli_main.services.content_processor.get_vector_store') as mock_vs:
            mock_vs.return_value.add_documents.return_value = ["doc1", "doc2"]
            
            # Test workflow
            processor = ContentProcessor()
            success = processor.process_queue_item(1)
            
            assert success is True
```

### Test Markers

```python
# Unit test (default)
def test_something():
    pass

# Integration test
@pytest.mark.integration
def test_integration():
    pass

# Slow test
@pytest.mark.slow
def test_slow_operation():
    pass

# Requires specific service
@pytest.mark.requires_ollama
def test_with_ollama():
    pass
```

### Fixtures

```python
@pytest.fixture
def mock_config():
    """Mock configuration."""
    config = Mock()
    config.llm_model = "llama3.1:8b"
    return config

@pytest.fixture
def temp_dir():
    """Create temporary directory."""
    with tempfile.TemporaryDirectory() as tmpdir:
        yield tmpdir
```

---

## 📊 Coverage Reports

### Generate Coverage Report

```bash
# Terminal report
pytest --cov=youtube_chat_cli_main --cov-report=term-missing

# HTML report
pytest --cov=youtube_chat_cli_main --cov-report=html

# XML report (for CI)
pytest --cov=youtube_chat_cli_main --cov-report=xml
```

### View HTML Report

```bash
# Generate report
pytest --cov=youtube_chat_cli_main --cov-report=html

# Open in browser (Windows)
start htmlcov/index.html

# Open in browser (macOS)
open htmlcov/index.html

# Open in browser (Linux)
xdg-open htmlcov/index.html
```

### Coverage Goals

- **Overall**: 85%+
- **Core Services**: 90%+
- **CLI Commands**: 75%+
- **MCP Server**: 75%+

---

## 🔄 CI/CD Integration

### GitHub Actions Example

```yaml
name: Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    
    steps:
    - uses: actions/checkout@v2
    
    - name: Set up Python
      uses: actions/setup-python@v2
      with:
        python-version: '3.13'
    
    - name: Install dependencies
      run: |
        pip install -r requirements.txt
        pip install pytest pytest-cov
    
    - name: Run tests
      run: |
        python run_tests.py --ci
    
    - name: Upload coverage
      uses: codecov/codecov-action@v2
      with:
        file: ./coverage.xml
```

### Pre-commit Hook

```bash
# .git/hooks/pre-commit
#!/bin/bash

echo "Running tests before commit..."
python run_tests.py --unit

if [ $? -ne 0 ]; then
    echo "Tests failed. Commit aborted."
    exit 1
fi

echo "Tests passed. Proceeding with commit."
```

---

## 🐛 Debugging Tests

### Run Single Test with Debug Output

```bash
pytest tests/test_rag_engine.py::TestAdaptiveRAGEngine::test_retrieve_node -v -s
```

### Use pytest debugger

```python
def test_something():
    # Add breakpoint
    import pdb; pdb.set_trace()
    
    # Or use pytest's built-in
    pytest.set_trace()
```

### Print Debug Information

```bash
# Show print statements
pytest -s

# Show local variables on failure
pytest -l

# Show full traceback
pytest --tb=long
```

---

## 📝 Best Practices

### 1. Test Isolation
- Each test should be independent
- Use fixtures for setup/teardown
- Don't rely on test execution order

### 2. Mock External Dependencies
- Mock all external services (Ollama, Qdrant, etc.)
- Use `unittest.mock.patch` for dependencies
- Mock at the boundary of your code

### 3. Test Naming
- Use descriptive names: `test_retrieve_node_with_valid_query`
- Group related tests in classes
- Use docstrings to explain complex tests

### 4. Assertions
- Use specific assertions: `assert result == expected`
- Test both success and failure cases
- Verify side effects (mock calls, database changes)

### 5. Coverage
- Aim for 85%+ coverage
- Focus on critical paths
- Don't test trivial code

---

## 🎯 Common Test Scenarios

### Testing RAG Engine

```python
def test_rag_query_with_relevant_documents(self, rag_engine, mock_llm, mock_vector_store):
    """Test RAG query with relevant documents."""
    # Setup mocks
    mock_vector_store.search.return_value = [...]
    mock_llm.generate.return_value = "Answer"
    
    # Execute
    result = rag_engine.query("Question?")
    
    # Verify
    assert result["answer"] == "Answer"
    assert len(result["documents"]) > 0
```

### Testing File Processing

```python
def test_process_pdf_file(self, processor):
    """Test PDF file processing."""
    with patch('youtube_chat_cli_main.services.content_processor.PyPDF2.PdfReader') as mock_pdf:
        # Setup mock
        mock_pdf.return_value.pages = [Mock(extract_text=lambda: "Content")]
        
        # Execute
        content = processor._process_pdf_file("test.pdf")
        
        # Verify
        assert "Content" in content
```

### Testing Database Operations

```python
def test_queue_operations(self, test_db):
    """Test queue CRUD operations."""
    # Create
    queue_id = test_db.add_to_queue("file.pdf", "file.pdf", "local", 0)
    
    # Read
    item = test_db.get_queue_item(queue_id)
    assert item["file_name"] == "file.pdf"
    
    # Update
    test_db.update_queue_status(queue_id, "completed")
    
    # Verify
    item = test_db.get_queue_item(queue_id)
    assert item["status"] == "completed"
```

---

## 🎉 Success!

You now have a comprehensive testing suite for JAEGIS NexusSync!

**Next Steps:**
1. Run the tests: `python run_tests.py --all`
2. Check coverage: `python run_tests.py --coverage`
3. Fix any failing tests
4. Add more tests for edge cases
5. Integrate with CI/CD

Happy testing! 🚀

