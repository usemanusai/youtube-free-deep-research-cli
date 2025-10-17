# RAG Engine Guide

Complete guide to the Adaptive RAG (Retrieval-Augmented Generation) engine.

## Overview

The RAG engine combines document retrieval with LLM generation to provide accurate, context-aware responses.

## Architecture

```
User Query
    ↓
Query Embedding
    ↓
Vector Search (Retrieve)
    ↓
Context Grading
    ↓
LLM Generation
    ↓
Response
```

## Components

### 1. Retriever

Retrieves relevant documents from the vector store.

```python
from youtube_chat_cli_main.services.rag import RAGEngine

engine = RAGEngine()
documents = engine.retrieve("search query", top_k=5)
```

### 2. Grader

Grades retrieved documents for relevance.

```python
graded_docs = engine.grade_documents(documents, query)
```

### 3. Transformer

Transforms context for LLM input.

```python
context = engine.transform_context(graded_docs)
```

### 4. Generator

Generates response using LLM.

```python
response = engine.generate(query, context)
```

## Setup

### 1. Configure Vector Store

```bash
# Using Qdrant
export VECTOR_STORE_TYPE=qdrant
export QDRANT_URL=http://localhost:6333

# Or using Chroma
export VECTOR_STORE_TYPE=chroma
export CHROMA_PERSIST_DIR=./chroma_data
```

### 2. Start Vector Store

```bash
# Qdrant with Docker
docker run -p 6333:6333 qdrant/qdrant

# Or use Chroma (embedded)
# No setup needed, uses local directory
```

### 3. Index Documents

```bash
# CLI
youtube-chat rag index /path/to/documents

# Python
from youtube_chat_cli_main.services.rag import RAGEngine

engine = RAGEngine()
engine.index_documents("/path/to/documents")
```

## Usage

### Basic Query

```python
from youtube_chat_cli_main.services.rag import RAGEngine

engine = RAGEngine()
response = engine.query("What is machine learning?")
print(response)
```

### Query with Options

```python
response = engine.query(
    query="What is machine learning?",
    top_k=10,
    threshold=0.7,
    stream=True
)
```

### Streaming Response

```python
for chunk in engine.query_stream("Your question"):
    print(chunk, end="", flush=True)
```

## Configuration

### RAG Settings

```bash
# Retrieval
RAG_TOP_K=5
RAG_THRESHOLD=0.7

# Grading
RAG_GRADE_THRESHOLD=0.5
RAG_GRADE_MODEL=openrouter/auto

# Generation
RAG_GENERATION_MODEL=openrouter/auto
RAG_GENERATION_TEMPERATURE=0.7
RAG_GENERATION_MAX_TOKENS=2048
```

### Embeddings

```bash
# Embeddings Model
EMBEDDINGS_MODEL=sentence-transformers/all-MiniLM-L6-v2

# Embeddings Dimension
EMBEDDINGS_DIMENSION=384
```

## Advanced Usage

### Custom Retrieval

```python
from youtube_chat_cli_main.services.rag import RAGEngine

engine = RAGEngine()

# Custom retrieval with filters
documents = engine.retrieve(
    query="machine learning",
    top_k=10,
    filters={"source": "research_papers"}
)
```

### Custom Grading

```python
# Grade documents with custom threshold
graded = engine.grade_documents(
    documents=documents,
    query="machine learning",
    threshold=0.8
)
```

### Custom Generation

```python
# Generate with custom system prompt
response = engine.generate(
    query="What is machine learning?",
    context=context,
    system_prompt="You are an expert in AI and machine learning"
)
```

## Document Indexing

### Supported Formats

- PDF (.pdf)
- Word (.docx)
- Text (.txt)
- Markdown (.md)
- HTML (.html)
- JSON (.json)

### Index Documents

```bash
# Index single file
youtube-chat rag index document.pdf

# Index directory
youtube-chat rag index /path/to/documents

# Index with metadata
youtube-chat rag index /path/to/documents --metadata source=research
```

### Update Index

```python
# Add new documents
engine.add_documents("/path/to/new/documents")

# Remove documents
engine.remove_documents(document_ids)

# Clear index
engine.clear_index()
```

## Search

### Vector Search

```bash
youtube-chat search vector "search query"
```

### Hybrid Search

```bash
youtube-chat search combined "search query" --web --vector
```

### Search with Filters

```python
results = engine.search(
    query="machine learning",
    filters={"source": "research_papers"},
    top_k=10
)
```

## Performance Optimization

### Batch Indexing

```python
# Index documents in batches
engine.index_documents(
    path="/path/to/documents",
    batch_size=100
)
```

### Caching

```python
# Enable caching
engine.enable_cache()

# Clear cache
engine.clear_cache()
```

### Parallel Processing

```python
# Process documents in parallel
engine.index_documents(
    path="/path/to/documents",
    num_workers=4
)
```

## Monitoring

### Index Statistics

```bash
youtube-chat rag stats
```

### Query Metrics

```python
metrics = engine.get_metrics()
print(f"Total queries: {metrics['total_queries']}")
print(f"Avg latency: {metrics['avg_latency']}ms")
```

## Troubleshooting

### Vector Store Connection Error

```bash
# Check if vector store is running
curl http://localhost:6333/health

# Restart vector store
docker restart qdrant
```

### No Results Found

```bash
# Check if documents are indexed
youtube-chat rag stats

# Re-index documents
youtube-chat rag clear
youtube-chat rag index /path/to/documents
```

### Low Quality Results

```bash
# Adjust threshold
youtube-chat config set rag.threshold 0.5

# Increase top_k
youtube-chat config set rag.top_k 10

# Use different embeddings model
youtube-chat config set embeddings.model sentence-transformers/all-mpnet-base-v2
```

## Best Practices

1. **Index Quality** - Ensure documents are well-formatted
2. **Metadata** - Add metadata for better filtering
3. **Threshold Tuning** - Adjust threshold based on use case
4. **Regular Updates** - Keep index up-to-date
5. **Monitor Performance** - Track query metrics

---

See [System Overview](../architecture/overview.md) for architecture details.

