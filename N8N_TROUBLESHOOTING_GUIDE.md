# n8n Integration Troubleshooting Guide

**Date:** September 30, 2025  
**Purpose:** Diagnose and fix common issues with the n8n RAG integration

---

## 🔍 QUICK DIAGNOSTICS

### **Test 1: Check if n8n is Running**

```bash
# Check if n8n is accessible
curl http://localhost:5678/healthz

# Expected: HTTP 200 OK
```

**If this fails:**
- n8n is not running
- Run: `docker start n8n` or `npx n8n`

---

### **Test 2: Check if Qdrant is Running**

```bash
# Check Qdrant health
curl http://localhost:6333/

# Expected: JSON response with version info
```

**If this fails:**
- Qdrant is not running
- Run: `docker start qdrant`

---

### **Test 3: Check if Workflow is Active**

```bash
# Test the webhook
curl -X POST http://localhost:5678/webhook/invoke_n8n_agent \
  -H "Content-Type: application/json" \
  -d '{"chatInput": "test", "sessionId": "test-123"}'

# Expected: JSON response with agent reply
```

**If this fails:**
- Workflow is not active in n8n
- Open n8n UI and activate the workflow

---

### **Test 4: Check Python CLI Connection**

```bash
# Test from Python CLI
python -m youtube_chat_cli_main.cli invoke-n8n "Hello"

# Expected: Response from n8n agent
```

**If this fails:**
- Check `.env` file has `N8N_WEBHOOK_URL` configured
- Verify webhook URL is correct

---

## ❌ COMMON ERRORS AND SOLUTIONS

### **Error 1: "N8N_WEBHOOK_URL environment variable not set"**

**Cause:** `.env` file is missing or doesn't have the webhook URL

**Solution:**
```bash
# Add to .env file
echo "N8N_WEBHOOK_URL=http://localhost:5678/webhook/invoke_n8n_agent" >> .env
```

---

### **Error 2: "Connection refused" or "Failed to connect to n8n"**

**Cause:** n8n server is not running

**Solution:**
```bash
# Option A: Start with Docker
docker start n8n

# Option B: Start with npx
npx n8n

# Option C: Check if running
docker ps | grep n8n
```

---

### **Error 3: "Workflow not found" or "404 Not Found"**

**Cause:** Workflow is not imported or webhook URL is wrong

**Solution:**
1. Open n8n at `http://localhost:5678`
2. Go to **Workflows** → **Import from File**
3. Select `youtube_chat_cli_main/Local RAG AI Agent.json`
4. Click **Activate** toggle in top-right
5. Verify webhook URL in workflow matches `.env`

---

### **Error 4: "Qdrant connection failed"**

**Cause:** Qdrant is not running or collection doesn't exist

**Solution:**
```bash
# Start Qdrant
docker start qdrant

# Create collection
curl -X PUT 'http://localhost:6333/collections/documents' \
  -H 'Content-Type: application/json' \
  -d '{
    "vectors": {
      "size": 768,
      "distance": "Cosine"
    }
  }'
```

---

### **Error 5: "PostgreSQL connection failed"**

**Cause:** PostgreSQL is not running or database doesn't exist

**Solution:**
```bash
# Start PostgreSQL
docker start postgres-n8n

# Create database and table
docker exec -i postgres-n8n psql -U postgres <<EOF
CREATE DATABASE n8n_chat;
\c n8n_chat
CREATE TABLE IF NOT EXISTS chat_memory (
  id SERIAL PRIMARY KEY,
  session_id VARCHAR(255) NOT NULL,
  message TEXT NOT NULL,
  role VARCHAR(50) NOT NULL,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
EOF
```

---

### **Error 6: "Ollama model not found"**

**Cause:** Ollama models are not installed

**Solution:**
```bash
# Pull required models
ollama pull llama3.1:latest
ollama pull nomic-embed-text:latest

# Verify models
ollama list
```

**Alternative:** Use OpenRouter instead of Ollama
- Add `OPENROUTER_API_KEY` to `.env`
- Configure OpenRouter in n8n workflow

---

### **Error 7: "Google Drive authentication failed"**

**Cause:** Google Drive OAuth2 credentials not configured

**Solution:**
1. In n8n, go to **Credentials** → **Add Credential**
2. Select **Google Drive OAuth2**
3. Follow the setup wizard
4. Update the workflow to use your credentials

**Note:** Google Drive is optional - you can use the workflow without it

---

### **Error 8: "File type not supported"**

**Cause:** File type is not in the supported list

**Solution:**
```bash
# Check supported file types
python -m youtube_chat_cli_main.cli list-supported-files

# If your file type is not listed, you may need to:
# 1. Convert it to a supported format
# 2. Extract text manually and save as .txt
```

---

### **Error 9: "Mock response returned" instead of real n8n response**

**Cause:** n8n client is falling back to mock mode

**Solution:**
1. Check if n8n is running: `curl http://localhost:5678/healthz`
2. Check if workflow is active in n8n UI
3. Verify webhook URL in `.env` matches workflow
4. Check n8n logs for errors: `docker logs n8n`

---

### **Error 10: "Timeout waiting for n8n response"**

**Cause:** n8n workflow is taking too long (>30 seconds)

**Solution:**
1. Check n8n execution logs in UI
2. Verify Ollama/OpenRouter is responding
3. Check if vector search is slow (too many documents)
4. Increase timeout in `n8n_client.py` if needed

---

## 🔧 ADVANCED TROUBLESHOOTING

### **Check n8n Logs**

```bash
# Docker logs
docker logs n8n --tail 100 --follow

# Look for errors related to:
# - Webhook execution
# - Database connections
# - API calls
```

---

### **Check Qdrant Collections**

```bash
# List all collections
curl http://localhost:6333/collections

# Get collection info
curl http://localhost:6333/collections/documents

# Count vectors
curl http://localhost:6333/collections/documents/points/count
```

---

### **Check PostgreSQL Data**

```bash
# Connect to database
docker exec -it postgres-n8n psql -U postgres -d n8n_chat

# View chat history
SELECT * FROM chat_memory ORDER BY created_at DESC LIMIT 10;

# Count messages
SELECT COUNT(*) FROM chat_memory;

# Exit
\q
```

---

### **Test Ollama Directly**

```bash
# Test LLM
curl http://localhost:11434/api/generate -d '{
  "model": "llama3.1",
  "prompt": "Hello, how are you?",
  "stream": false
}'

# Test embeddings
curl http://localhost:11434/api/embeddings -d '{
  "model": "nomic-embed-text",
  "prompt": "test text"
}'
```

---

### **Reset Everything**

If all else fails, reset the entire setup:

```bash
# Stop all containers
docker stop n8n qdrant postgres-n8n

# Remove containers
docker rm n8n qdrant postgres-n8n

# Remove volumes (WARNING: This deletes all data!)
docker volume prune -f

# Re-run setup
./setup_n8n_integration.sh  # Linux/Mac
setup_n8n_integration.bat   # Windows
```

---

## 📊 PERFORMANCE OPTIMIZATION

### **Slow Vector Search**

**Symptoms:** Queries take >5 seconds

**Solutions:**
1. Reduce chunk size in text splitter (currently 100 chars)
2. Limit number of vectors returned (currently unlimited)
3. Use HNSW index in Qdrant for faster search
4. Increase Qdrant memory allocation

---

### **High Memory Usage**

**Symptoms:** Docker containers using >4GB RAM

**Solutions:**
1. Use smaller embedding models
2. Reduce Ollama context window
3. Limit PostgreSQL connections
4. Use OpenRouter instead of local Ollama

---

### **Slow Podcast Generation**

**Symptoms:** Podcast generation takes >10 minutes

**Solutions:**
1. Use faster TTS engine (Kokoro instead of MeloTTS)
2. Reduce podcast duration
3. Use OpenRouter instead of Ollama for faster LLM
4. Generate script and audio in parallel

---

## 🎯 VERIFICATION CHECKLIST

Use this checklist to verify everything is working:

- [ ] Docker is installed and running
- [ ] n8n is running on http://localhost:5678
- [ ] Qdrant is running on http://localhost:6333
- [ ] PostgreSQL is running on localhost:5432
- [ ] Ollama is installed (or OpenRouter API key configured)
- [ ] Workflow is imported in n8n
- [ ] Workflow is activated in n8n
- [ ] `.env` has `N8N_WEBHOOK_URL` configured
- [ ] Webhook test returns valid response
- [ ] CLI `invoke-n8n` command works
- [ ] File processing works
- [ ] Podcast generation from RAG works

---

## 📞 GETTING HELP

If you're still having issues:

1. **Check the logs:**
   - n8n: `docker logs n8n`
   - Qdrant: `docker logs qdrant`
   - PostgreSQL: `docker logs postgres-n8n`

2. **Review the documentation:**
   - `N8N_INTEGRATION_ANALYSIS_AND_FIX.md` - Setup guide
   - `N8N_TROUBLESHOOTING_GUIDE.md` - This file

3. **Test each component individually:**
   - Test n8n webhook directly with curl
   - Test Qdrant API directly
   - Test PostgreSQL connection
   - Test Ollama models

4. **Check the workflow in n8n UI:**
   - Open http://localhost:5678
   - View execution history
   - Check for error messages
   - Verify credentials are configured

---

## 🎉 SUCCESS INDICATORS

You'll know everything is working when:

✅ `curl http://localhost:5678/healthz` returns 200 OK  
✅ `curl http://localhost:6333/` returns Qdrant version  
✅ `python -m youtube_chat_cli_main.cli invoke-n8n "test"` returns a response  
✅ `python -m youtube_chat_cli_main.cli process-file test.txt` processes successfully  
✅ `python -m youtube_chat_cli_main.cli generate-podcast-from-rag --query "test"` generates audio  

---

**If you've completed the checklist and all tests pass, your n8n RAG integration is fully operational!** 🚀

