# n8n RAG Integration - Quick Reference Card

**Last Updated:** September 30, 2025

---

## 🚀 QUICK START (3 COMMANDS)

```bash
# 1. Setup (run once)
setup_n8n_integration.bat

# 2. Import workflow in n8n UI
# Open http://localhost:5678 → Import → Local RAG AI Agent.json

# 3. Test
python -m youtube_chat_cli_main.cli invoke-n8n "Hello!"
```

---

## 📋 COMMON COMMANDS

### **Chat with n8n Agent**
```bash
python -m youtube_chat_cli_main.cli invoke-n8n "Your question here"
```

### **Process a File**
```bash
python -m youtube_chat_cli_main.cli process-file document.pdf
```

### **Generate Podcast from RAG**
```bash
python -m youtube_chat_cli_main.cli generate-podcast-from-rag \
    --query "Summarize the documents" \
    --output podcast.wav
```

### **List Supported File Types**
```bash
python -m youtube_chat_cli_main.cli list-supported-files
```

---

## 🔧 SERVICE MANAGEMENT

### **Start All Services**
```bash
docker start qdrant postgres-n8n n8n
```

### **Stop All Services**
```bash
docker stop qdrant postgres-n8n n8n
```

### **Check Status**
```bash
docker ps | grep -E "qdrant|postgres-n8n|n8n"
```

### **View Logs**
```bash
docker logs n8n --tail 50 --follow
```

---

## 🌐 SERVICE URLS

| Service | URL | Purpose |
|---------|-----|---------|
| **n8n UI** | http://localhost:5678 | Workflow management |
| **Qdrant** | http://localhost:6333 | Vector database |
| **PostgreSQL** | localhost:5432 | Chat memory |
| **Ollama** | http://localhost:11434 | Local LLM (optional) |

---

## 🧪 QUICK TESTS

### **Test 1: n8n Running**
```bash
curl http://localhost:5678/healthz
# Expected: HTTP 200 OK
```

### **Test 2: Qdrant Running**
```bash
curl http://localhost:6333/
# Expected: JSON with version
```

### **Test 3: Webhook Working**
```bash
curl -X POST http://localhost:5678/webhook/invoke_n8n_agent \
  -H "Content-Type: application/json" \
  -d '{"chatInput": "test", "sessionId": "test-123"}'
# Expected: JSON response
```

### **Test 4: CLI Working**
```bash
python -m youtube_chat_cli_main.cli invoke-n8n "test"
# Expected: Response from agent
```

---

## 📁 SUPPORTED FILE TYPES (600+)

### **Most Common**
- **Documents:** PDF, DOCX, DOC, TXT, MD
- **Spreadsheets:** XLSX, XLS, CSV
- **Presentations:** PPTX, PPT
- **Images:** PNG, JPG, JPEG (with OCR)
- **Code:** PY, JS, TS, JAVA, C, CPP, GO, RS
- **Data:** JSON, XML, YAML, CSV

### **Full List**
```bash
python -m youtube_chat_cli_main.cli list-supported-files
```

---

## ⚙️ CONFIGURATION

### **.env File**
```bash
# Required
N8N_WEBHOOK_URL=http://localhost:5678/webhook/invoke_n8n_agent

# Optional (if not using Ollama)
OPENROUTER_API_KEY=your_key_here
```

### **n8n Credentials**
- **Qdrant:** http://localhost:6333 (no API key)
- **PostgreSQL:** localhost:5432, db=n8n_chat, user=postgres, password=n8n_password
- **Ollama:** http://localhost:11434 (if installed)
- **OpenRouter:** API key from .env

---

## 🐛 TROUBLESHOOTING

### **Problem: "N8N_WEBHOOK_URL not set"**
```bash
echo "N8N_WEBHOOK_URL=http://localhost:5678/webhook/invoke_n8n_agent" >> .env
```

### **Problem: "Connection refused"**
```bash
docker start n8n
```

### **Problem: "Workflow not found"**
1. Open http://localhost:5678
2. Import `Local RAG AI Agent.json`
3. Click **Activate**

### **Problem: "Qdrant connection failed"**
```bash
docker start qdrant
```

### **More Help**
See `N8N_TROUBLESHOOTING_GUIDE.md`

---

## 📚 DOCUMENTATION

| File | Purpose |
|------|---------|
| `N8N_INTEGRATION_COMPLETE_SUMMARY.md` | Complete overview |
| `N8N_INTEGRATION_ANALYSIS_AND_FIX.md` | Setup guide |
| `N8N_TROUBLESHOOTING_GUIDE.md` | Troubleshooting |
| `N8N_QUICK_REFERENCE.md` | This file |

---

## 🎯 WORKFLOW EXAMPLES

### **Example 1: Process Meeting Notes**
```bash
# 1. Process the file
python -m youtube_chat_cli_main.cli process-file meeting_notes.docx

# 2. Query the content
python -m youtube_chat_cli_main.cli invoke-n8n "What were the action items?"

# 3. Generate podcast
python -m youtube_chat_cli_main.cli generate-podcast-from-rag \
    --query "Summarize the meeting" \
    --output meeting_summary.wav
```

### **Example 2: Research Paper Summary**
```bash
# 1. Process multiple papers
python -m youtube_chat_cli_main.cli process-file paper1.pdf
python -m youtube_chat_cli_main.cli process-file paper2.pdf
python -m youtube_chat_cli_main.cli process-file paper3.pdf

# 2. Generate comprehensive podcast
python -m youtube_chat_cli_main.cli generate-podcast-from-rag \
    --query "Compare and contrast the key findings from all papers" \
    --max-duration 45 \
    --output research_summary.wav
```

### **Example 3: Code Documentation**
```bash
# 1. Process code files
python -m youtube_chat_cli_main.cli process-file main.py
python -m youtube_chat_cli_main.cli process-file utils.py

# 2. Query the code
python -m youtube_chat_cli_main.cli invoke-n8n "Explain how the main function works"

# 3. Generate explanation podcast
python -m youtube_chat_cli_main.cli generate-podcast-from-rag \
    --query "Explain the codebase architecture" \
    --output code_explanation.wav
```

---

## 🎵 AUDIO QUALITY

| TTS Engine | Quality | Speed | Use Case |
|------------|---------|-------|----------|
| **MeloTTS** | 4/5 | Medium | Default (best quality) |
| **Kokoro** | 3.5/5 | Fast | Quick generation |
| **Chatterbox** | 4.5/5 | Slow | Premium quality (if installed) |

**Current Default:** MeloTTS (4/5 quality)

---

## 🔄 COMMON WORKFLOWS

### **Daily Workflow**
```bash
# Morning: Start services
docker start qdrant postgres-n8n n8n

# During day: Process files as needed
python -m youtube_chat_cli_main.cli process-file document.pdf

# Evening: Generate summary podcast
python -m youtube_chat_cli_main.cli generate-podcast-from-rag \
    --query "Summarize today's documents" \
    --output daily_summary.wav

# Night: Stop services (optional)
docker stop qdrant postgres-n8n n8n
```

### **Research Workflow**
```bash
# 1. Collect documents
# 2. Process all documents
for file in *.pdf; do
    python -m youtube_chat_cli_main.cli process-file "$file"
done

# 3. Query and explore
python -m youtube_chat_cli_main.cli invoke-n8n "What are the main themes?"

# 4. Generate final podcast
python -m youtube_chat_cli_main.cli generate-podcast-from-rag \
    --query "Create a comprehensive overview" \
    --max-duration 60 \
    --output research_overview.wav
```

---

## 💡 TIPS & TRICKS

### **Tip 1: Use Session IDs**
```bash
# Keep conversation context
python -m youtube_chat_cli_main.cli invoke-n8n "Tell me about AI" --session-id research-session
python -m youtube_chat_cli_main.cli invoke-n8n "What else?" --session-id research-session
```

### **Tip 2: Batch Process Files**
```bash
# Windows
for %f in (*.pdf) do python -m youtube_chat_cli_main.cli process-file "%f"

# Linux/Mac
for file in *.pdf; do python -m youtube_chat_cli_main.cli process-file "$file"; done
```

### **Tip 3: Custom Podcast Duration**
```bash
# Short (10 min)
--max-duration 10

# Medium (30 min)
--max-duration 30

# Long (60 min)
--max-duration 60
```

### **Tip 4: Check Vector Database**
```bash
# Count stored vectors
curl http://localhost:6333/collections/documents/points/count

# View collection info
curl http://localhost:6333/collections/documents
```

---

## 🎯 QUICK CHECKLIST

Before using the integration, verify:

- [ ] Docker is running
- [ ] Services are started: `docker ps | grep -E "qdrant|postgres|n8n"`
- [ ] n8n UI is accessible: http://localhost:5678
- [ ] Workflow is imported and active
- [ ] `.env` has `N8N_WEBHOOK_URL` configured
- [ ] Test command works: `python -m youtube_chat_cli_main.cli invoke-n8n "test"`

---

## 📞 HELP

**Quick Diagnostics:**
```bash
# Check all services
docker ps

# Test webhook
curl -X POST http://localhost:5678/webhook/invoke_n8n_agent \
  -H "Content-Type: application/json" \
  -d '{"chatInput": "test", "sessionId": "test"}'

# View n8n logs
docker logs n8n --tail 50
```

**Documentation:**
- Setup: `N8N_INTEGRATION_ANALYSIS_AND_FIX.md`
- Troubleshooting: `N8N_TROUBLESHOOTING_GUIDE.md`
- Summary: `N8N_INTEGRATION_COMPLETE_SUMMARY.md`

---

**Keep this file handy for quick reference!** 📌

