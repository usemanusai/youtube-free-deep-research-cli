# CLI Usage Guide

Complete guide to using the YouTube Free Deep Research CLI.

## Getting Started

### Display Help

```bash
youtube-chat --help
```

### Display Version

```bash
youtube-chat --version
```

## Chat Commands

### Start Interactive Chat

```bash
youtube-chat chat
```

Starts an interactive chat session where you can ask questions.

### Send Single Message

```bash
youtube-chat chat --message "Your question here"
```

### Chat with System Prompt

```bash
youtube-chat chat --system-prompt "You are a helpful assistant" --message "Your question"
```

### Stream Response

```bash
youtube-chat chat --message "Your question" --stream
```

### Save Chat History

```bash
youtube-chat chat --message "Your question" --save-history
```

## File Commands

### Upload File

```bash
youtube-chat files upload /path/to/file.pdf
```

### List Files

```bash
youtube-chat files list
```

### List with Pagination

```bash
youtube-chat files list --limit 20 --offset 0
```

### Download File

```bash
youtube-chat files download <file-id> --output /path/to/output.pdf
```

### Delete File

```bash
youtube-chat files delete <file-id>
```

### Process File

```bash
youtube-chat files process /path/to/file.pdf --extract-text
```

## Search Commands

### Web Search

```bash
youtube-chat search web "search query"
```

### Web Search with Limit

```bash
youtube-chat search web "search query" --limit 10
```

### Vector Search

```bash
youtube-chat search vector "search query"
```

### Vector Search with Threshold

```bash
youtube-chat search vector "search query" --threshold 0.7
```

### Combined Search

```bash
youtube-chat search combined "search query" --web --vector
```

## Configuration Commands

### Show Configuration

```bash
youtube-chat config show
```

### Show Specific Setting

```bash
youtube-chat config show --key llm.model
```

### Set Configuration

```bash
youtube-chat config set llm.model openrouter/auto
```

### Set TTS Engine

```bash
youtube-chat config set tts.engine melotts
```

### Set TTS Voice

```bash
youtube-chat config set tts.voice en-US-AriaNeural
```

### Reset Configuration

```bash
youtube-chat config reset
```

## Background Job Commands

### List Jobs

```bash
youtube-chat jobs list
```

### List Running Jobs

```bash
youtube-chat jobs list --status running
```

### Get Job Status

```bash
youtube-chat jobs status <job-id>
```

### Cancel Job

```bash
youtube-chat jobs cancel <job-id>
```

### Wait for Job

```bash
youtube-chat jobs wait <job-id>
```

## RAG Commands

### Index Documents

```bash
youtube-chat rag index /path/to/documents
```

### Search Documents

```bash
youtube-chat rag search "search query"
```

### Clear Index

```bash
youtube-chat rag clear
```

### Show Index Stats

```bash
youtube-chat rag stats
```

## Global Options

### Verbose Output

```bash
youtube-chat --verbose chat --message "Your question"
```

### Debug Mode

```bash
youtube-chat --debug chat --message "Your question"
```

### Quiet Mode

```bash
youtube-chat --quiet chat --message "Your question"
```

### Log Level

```bash
youtube-chat --log-level DEBUG chat --message "Your question"
```

### Configuration File

```bash
youtube-chat --config /path/to/config.yaml chat --message "Your question"
```

### Environment File

```bash
youtube-chat --env-file /path/to/.env chat --message "Your question"
```

## Examples

### Example 1: Ask a Question

```bash
youtube-chat chat --message "What is machine learning?"
```

### Example 2: Upload and Search

```bash
# Upload a PDF
youtube-chat files upload research_paper.pdf

# Search the uploaded file
youtube-chat search vector "key findings"
```

### Example 3: Interactive Session

```bash
# Start interactive chat
youtube-chat chat

# Type your questions:
# > What is Python?
# > How do I install it?
# > Show me an example
```

### Example 4: Batch Processing

```bash
# Process multiple files
for file in *.pdf; do
  youtube-chat files process "$file" --extract-text
done
```

### Example 5: Configure and Chat

```bash
# Set configuration
youtube-chat config set tts.engine melotts
youtube-chat config set llm.model openrouter/auto

# Start chat
youtube-chat chat --message "Hello, how are you?"
```

## Output Formatting

### JSON Output

```bash
youtube-chat chat --message "Your question" --format json
```

### Table Output

```bash
youtube-chat files list --format table
```

### CSV Output

```bash
youtube-chat search web "query" --format csv
```

## Error Handling

### Common Errors

```bash
# Error: Configuration not found
# Solution: Run 'youtube-chat config reset'

# Error: File not found
# Solution: Check file path and permissions

# Error: API connection failed
# Solution: Check internet connection and API keys
```

## Tips and Tricks

1. **Use Aliases** - Create shell aliases for common commands
   ```bash
   alias yc="youtube-chat"
   yc chat --message "Your question"
   ```

2. **Pipe Output** - Pipe output to other commands
   ```bash
   youtube-chat search web "query" | grep "result"
   ```

3. **Save Output** - Save output to file
   ```bash
   youtube-chat chat --message "Your question" > output.txt
   ```

4. **Batch Operations** - Use loops for batch operations
   ```bash
   for query in "query1" "query2" "query3"; do
     youtube-chat search web "$query"
   done
   ```

---

See [REST API](../api/rest-api.md) for API endpoints.

