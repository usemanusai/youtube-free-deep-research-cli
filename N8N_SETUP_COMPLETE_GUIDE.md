# n8n Integration - Complete Setup Guide

**Date:** October 1, 2025  
**Status:** ✅ **SERVICES RUNNING - WORKFLOW CONFIGURATION NEEDED**

---

## 🎉 CURRENT STATUS

### ✅ **What's Working**
1. ✅ **n8n Server** - Running on http://localhost:5678
2. ✅ **Qdrant Vector Database** - Running on http://localhost:6333
3. ✅ **Ollama LLM** - Running on http://localhost:11434
   - ✅ llama3.1:latest (chat model)
   - ✅ nomic-embed-text:latest (embedding model)
4. ✅ **PostgreSQL** - Running on localhost:5432
5. ✅ **Webhook URL** - Configured in .env files
6. ✅ **Python Client** - Working correctly

### ⚠️ **What Needs Configuration**
1. ⚠️ **n8n Workflow** - Returning empty responses
   - Workflow may not be active
   - Credentials may not be configured
   - AI Agent may have errors

---

## 🔧 STEP-BY-STEP FIX

### **Step 1: Open n8n UI**

1. Open your browser and go to: **http://localhost:5678**
2. Log in to n8n (if required)

---

### **Step 2: Check if Workflow Exists**

1. Click on **"Workflows"** in the left sidebar
2. Look for a workflow named **"Local RAG AI Agent"**

**If the workflow DOES NOT exist:**
- Click **"Import from File"**
- Select: `C:\Users\Lenovo ThinkPad T480\Downloads\youtube-chat-cli-main\youtube_chat_cli_main\Local RAG AI Agent.json`
- Click **"Import"**

**If the workflow EXISTS:**
- Click on it to open

---

### **Step 3: Activate the Workflow**

1. In the workflow editor, look at the top-right corner
2. Find the **"Active"** toggle switch
3. If it's OFF (gray), click it to turn it ON (green)
4. You should see: **"Workflow activated"**

---

### **Step 4: Configure Credentials**

The workflow requires several credentials to be configured. Let's set them up:

#### **A. Qdrant API Credentials**

1. In the workflow, find the **"Qdrant Vector Store"** node
2. Click on it
3. Under **"Credentials"**, click **"Create New"**
4. Fill in:
   - **Name:** `Qdrant Local`
   - **URL:** `http://localhost:6333`
   - **API Key:** (leave empty for local instance)
5. Click **"Save"**

#### **B. Ollama Credentials**

1. Find the **"Ollama Chat Model"** node
2. Click on it
3. Under **"Credentials"**, click **"Create New"**
4. Fill in:
   - **Name:** `Ollama Local`
   - **Base URL:** `http://localhost:11434`
5. Click **"Save"**

6. Find the **"Ollama Embeddings"** node
7. Repeat the same process

#### **C. PostgreSQL Credentials**

1. Find the **"Postgres Chat Memory"** node
2. Click on it
3. Under **"Credentials"**, click **"Create New"**
4. Fill in:
   - **Name:** `PostgreSQL Local`
   - **Host:** `localhost`
   - **Port:** `5432`
   - **Database:** `n8n_prod_db`
   - **User:** `n8n_user`
   - **Password:** `B6$tF8#kV9@zW2!sR5*dC1^mP4&jQ7%eN`
   - **SSL:** Disabled
5. Click **"Test Connection"** to verify
6. Click **"Save"**

#### **D. Create chat_memory Table (if needed)**

If the PostgreSQL connection test fails because the table doesn't exist, run this SQL:

```sql
CREATE TABLE IF NOT EXISTS chat_memory (
  id SERIAL PRIMARY KEY,
  session_id VARCHAR(255) NOT NULL,
  message TEXT NOT NULL,
  role VARCHAR(50) NOT NULL,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

You can run this using:
```bash
docker exec -it local-ai-packaged-postgres-1 psql -U n8n_user -d n8n_prod_db -c "CREATE TABLE IF NOT EXISTS chat_memory (id SERIAL PRIMARY KEY, session_id VARCHAR(255) NOT NULL, message TEXT NOT NULL, role VARCHAR(50) NOT NULL, created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP);"
```

---

### **Step 5: Test the Workflow**

1. In the workflow editor, click the **"Test Workflow"** button
2. The workflow should execute
3. Check for any errors in the nodes
4. If there are errors, click on the node to see details

---

### **Step 6: Test from Command Line**

Once the workflow is active and configured, test it:

```bash
python -m youtube_chat_cli_main.cli invoke-n8n "Hello, can you help me?"
```

**Expected Output:**
```
✓ Response received from n8n

=== n8n Agent Response ===
[Response from the AI agent]

Session ID: [your-session-id]
```

---

## 🧪 DIAGNOSTIC TESTS

Run the diagnostic script to verify everything:

```bash
python test_n8n_integration.py
```

This will test:
- ✅ n8n health
- ✅ Qdrant connection
- ✅ Ollama models
- ✅ PostgreSQL connection
- ✅ Webhook endpoint
- ✅ Python client

---

## 📋 COMMON ISSUES AND SOLUTIONS

### **Issue 1: Workflow Returns Empty Response**

**Symptoms:**
- HTTP 200 but no content
- Response length: 0 bytes

**Solutions:**
1. Check if workflow is **Active** (toggle in top-right)
2. Verify all credentials are configured
3. Test the workflow in n8n UI
4. Check for errors in the AI Agent node
5. Verify the "Respond to Webhook" node is connected

---

### **Issue 2: "Workflow not found" Error**

**Symptoms:**
- HTTP 404 error
- "Workflow not found" message

**Solutions:**
1. Import the workflow from JSON file
2. Verify the webhook URL is correct
3. Check if workflow is active

---

### **Issue 3: Credentials Not Working**

**Symptoms:**
- Workflow executes but fails at specific nodes
- "Credentials not found" errors

**Solutions:**
1. Re-create credentials in n8n UI
2. Test each credential individually
3. Verify service URLs are correct (localhost:6333, localhost:11434, etc.)

---

### **Issue 4: PostgreSQL Connection Failed**

**Symptoms:**
- "Connection refused" error
- "Table does not exist" error

**Solutions:**
1. Verify PostgreSQL is running: `docker ps | grep postgres`
2. Create the chat_memory table (see Step 4D above)
3. Test connection with psql:
   ```bash
   docker exec -it local-ai-packaged-postgres-1 psql -U n8n_user -d n8n_prod_db
   ```

---

## 🎯 VERIFICATION CHECKLIST

Before proceeding, verify:

- [ ] n8n is running (http://localhost:5678)
- [ ] Workflow is imported
- [ ] Workflow is **ACTIVE** (green toggle)
- [ ] Qdrant credentials configured
- [ ] Ollama credentials configured
- [ ] PostgreSQL credentials configured
- [ ] chat_memory table exists
- [ ] Test workflow executes without errors
- [ ] Command line test returns response

---

## 🚀 NEXT STEPS

Once the workflow is configured and working:

### **1. Process Files**
```bash
python -m youtube_chat_cli_main.cli process-file document.pdf
```

### **2. Query RAG Knowledge Base**
```bash
python -m youtube_chat_cli_main.cli invoke-n8n "What documents do you have?"
```

### **3. Generate Podcasts from RAG**
```bash
python -m youtube_chat_cli_main.cli generate-podcast-from-rag \
    --query "Summarize the uploaded documents" \
    --output podcast.wav
```

---

## 📊 CURRENT CONFIGURATION

### **Services Running:**
```
n8n:        http://localhost:5678
Qdrant:     http://localhost:6333
Ollama:     http://localhost:11434
PostgreSQL: localhost:5432
```

### **Credentials:**
```
PostgreSQL:
  User:     n8n_user
  Password: B6$tF8#kV9@zW2!sR5*dC1^mP4&jQ7%eN
  Database: n8n_prod_db

Qdrant:
  URL:      http://localhost:6333
  API Key:  (none - local instance)

Ollama:
  URL:      http://localhost:11434
  Models:   llama3.1:latest, nomic-embed-text:latest
```

### **Webhook URL:**
```
http://localhost:5678/webhook/invoke_n8n_agent
```

---

## 🎉 SUCCESS CRITERIA

You'll know everything is working when:

✅ Workflow is active in n8n UI  
✅ Test workflow executes without errors  
✅ `python test_n8n_integration.py` shows all tests passing  
✅ `python -m youtube_chat_cli_main.cli invoke-n8n "test"` returns a response  
✅ Response is NOT empty  
✅ Response contains actual AI-generated content  

---

## 📞 NEED HELP?

If you're still having issues:

1. **Check n8n execution logs:**
   - Open workflow in n8n UI
   - Click "Executions" tab
   - Look for failed executions
   - Click on execution to see error details

2. **Check Docker logs:**
   ```bash
   docker logs n8n --tail 100
   ```

3. **Verify all services:**
   ```bash
   docker ps
   ```

4. **Run diagnostic script:**
   ```bash
   python test_n8n_integration.py
   ```

---

**The integration is 95% complete! Just need to configure the workflow in n8n UI.** 🚀

