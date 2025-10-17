# 🆓 JAEGIS NexusSync - 100% Free Tier Setup Guide

This guide will help you set up JAEGIS NexusSync using **completely free services** with **zero costs**.

## 📋 Overview of Free Services

All services used in this setup are **100% free**:

| Service | Cost | Setup Time | Notes |
|---------|------|------------|-------|
| **OpenRouter** | FREE | 2 min | Free tier with generous limits |
| **Ollama** | FREE | 5 min | Local LLM, runs on your machine |
| **ChromaDB** | FREE | 0 min | Included in dependencies, local storage |
| **Tesseract OCR** | FREE | 3 min | Open-source, local processing |
| **Google Drive API** | FREE | 5 min | Free within generous quotas |
| **Tavily Search** | FREE | 2 min | 1,000 searches/month free |
| **DuckDuckGo** | FREE | 0 min | Fallback search, unlimited |

**Total Setup Time: ~20 minutes**

---

## 🚀 Step-by-Step Setup

### Step 1: Install Ollama (Local LLM & Embeddings)

**Why Ollama?**
- 100% free, runs locally on your machine
- No API costs, unlimited usage
- Privacy-focused (data never leaves your computer)
- Works offline

**Installation:**

#### Windows:
1. Download from: https://ollama.ai/download
2. Run the installer
3. Open PowerShell and verify: `ollama --version`

#### macOS:
```bash
brew install ollama
```

#### Linux:
```bash
curl -fsSL https://ollama.ai/install.sh | sh
```

**Pull Required Models:**
```bash
# LLM model (choose one based on your RAM)
ollama pull llama3.1:8b        # 8GB model (recommended for 16GB RAM)
# OR
ollama pull phi3:mini          # 2GB model (for 8GB RAM systems)

# Embedding model (required for RAG)
ollama pull nomic-embed-text   # 274MB (lightweight, fast)
```

**Verify Ollama is running:**
```bash
ollama list
# Should show the models you pulled
```

---

### Step 2: Install Tesseract OCR (PDF/Image Processing)

**Why Tesseract?**
- 100% free, open-source
- No API costs, unlimited usage
- Supports 100+ languages
- Industry-standard OCR quality

**Installation:**

#### Windows:
1. Download installer: https://github.com/UB-Mannheim/tesseract/wiki
2. Download: `tesseract-ocr-w64-setup-5.3.3.exe`
3. Run installer (default location: `C:\Program Files\Tesseract-OCR`)
4. Add to PATH or note the installation path

#### macOS:
```bash
brew install tesseract
```

#### Linux:
```bash
sudo apt-get update
sudo apt-get install tesseract-ocr
```

**Verify Installation:**
```bash
tesseract --version
# Should show: tesseract 5.x.x
```

---

### Step 3: Get OpenRouter API Key (Free Tier)

**Why OpenRouter?**
- Free tier with generous limits
- Access to multiple free models
- No credit card required
- Easy to use

**Setup:**
1. Go to: https://openrouter.ai/
2. Click "Sign In" (use Google/GitHub)
3. Go to "Keys" section
4. Click "Create Key"
5. Copy your API key (starts with `sk-or-...`)

**Free Models Available:**
- `meta-llama/llama-3.1-8b-instruct` (FREE)
- `google/gemini-flash-1.5` (FREE)
- `mistral/mistral-7b-instruct` (FREE)

**Free Tier Limits:**
- Generous daily limits (sufficient for personal use)
- No credit card required
- No expiration

---

### Step 4: Get Tavily API Key (Free Tier)

**Why Tavily?**
- 1,000 searches/month free
- No credit card required
- High-quality search results
- DuckDuckGo fallback if limit reached

**Setup:**
1. Go to: https://tavily.com/
2. Click "Get API Key"
3. Sign up (email only, no credit card)
4. Copy your API key

**Free Tier:**
- 1,000 searches/month
- No expiration
- No credit card required

---

### Step 5: Set Up Google Drive API (Free)

**Why Google Drive API?**
- Completely free for personal use
- 1 billion requests/day quota (you'll never hit this)
- No credit card required
- Automated document ingestion

**Setup:**

1. **Go to Google Cloud Console:**
   - Visit: https://console.cloud.google.com/

2. **Create a New Project:**
   - Click "Select a project" → "New Project"
   - Name: "JAEGIS NexusSync"
   - Click "Create"

3. **Enable Google Drive API:**
   - Go to: https://console.cloud.google.com/apis/library
   - Search for "Google Drive API"
   - Click "Enable"

4. **Create OAuth 2.0 Credentials:**
   - Go to: https://console.cloud.google.com/apis/credentials
   - Click "Create Credentials" → "OAuth client ID"
   - If prompted, configure OAuth consent screen:
     - User Type: "External"
     - App name: "JAEGIS NexusSync"
     - User support email: your email
     - Developer contact: your email
     - Click "Save and Continue" (skip scopes)
     - Add yourself as test user
   - Application type: "Desktop app"
   - Name: "JAEGIS NexusSync Desktop"
   - Click "Create"

5. **Download Credentials:**
   - Click "Download JSON"
   - Save as `client_secret.json` in your project directory

6. **Get Folder ID (Optional):**
   - Create a folder in Google Drive for monitoring
   - Open the folder in browser
   - Copy the ID from URL: `https://drive.google.com/drive/folders/YOUR_FOLDER_ID`

**Free Tier Quotas:**
- 10,000 requests per 100 seconds per user
- 1 billion requests per day
- Completely free, no credit card needed

---

### Step 6: Create Your .env File

Copy the template and fill in your values:

```bash
cp .env.template .env
```

**Edit `.env` with your values:**

```bash
# LLM Configuration (FREE)
OPENROUTER_API_KEY=sk-or-v1-your-actual-key-here
LLM_MODEL=meta-llama/llama-3.1-8b-instruct

# Google Drive (FREE)
GOOGLE_CLIENT_SECRETS_FILE=client_secret.json
GOOGLE_DRIVE_FOLDER_ID=your-folder-id-here

# Vector Store (FREE - Local)
VECTOR_STORE_TYPE=chroma
CHROMA_PERSIST_DIRECTORY=./chroma_db

# Embeddings (FREE - Local)
EMBEDDING_PROVIDER=ollama
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_EMBEDDING_MODEL=nomic-embed-text

# Web Search (FREE)
TAVILY_API_KEY=tvly-your-actual-key-here
USE_DUCKDUCKGO_FALLBACK=true

# OCR (FREE - Local)
OCR_PROVIDER=tesseract
TESSERACT_PATH=C:\Program Files\Tesseract-OCR\tesseract.exe

# Database (FREE - Local SQLite)
DATABASE_PATH=./jaegis_nexus_sync.db

# Background Service
BACKGROUND_SERVICE_ENABLED=true
BACKGROUND_SERVICE_INTERVAL=300

# Logging
LOG_LEVEL=INFO
LOG_FILE=./logs/jaegis_nexus_sync.log
```

---

### Step 7: Install Python Dependencies

```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
# Windows:
venv\Scripts\activate
# macOS/Linux:
# source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

---

## ✅ Verification Checklist

Before running JAEGIS NexusSync, verify:

- [ ] Ollama is installed and running (`ollama list` shows models)
- [ ] Tesseract is installed (`tesseract --version` works)
- [ ] OpenRouter API key is in `.env` file
- [ ] Tavily API key is in `.env` file
- [ ] Google Drive `client_secret.json` is in project directory
- [ ] `.env` file is created and configured
- [ ] Python dependencies are installed

---

## 💰 Cost Breakdown

| Service | Monthly Cost | Annual Cost |
|---------|--------------|-------------|
| Ollama | $0 | $0 |
| ChromaDB | $0 | $0 |
| Tesseract | $0 | $0 |
| OpenRouter (free tier) | $0 | $0 |
| Tavily (free tier) | $0 | $0 |
| Google Drive API | $0 | $0 |
| **TOTAL** | **$0** | **$0** |

---

## 🔧 Troubleshooting

### Ollama Issues
**Problem:** `ollama: command not found`
**Solution:** Restart terminal after installation, or add to PATH

**Problem:** Model download fails
**Solution:** Check internet connection, try smaller model (phi3:mini)

### Tesseract Issues
**Problem:** `tesseract: command not found`
**Solution:** Add Tesseract to PATH or specify full path in `.env`

**Problem:** OCR quality is poor
**Solution:** Install language packs: `tesseract-ocr-eng` for English

### OpenRouter Issues
**Problem:** API key invalid
**Solution:** Regenerate key at https://openrouter.ai/keys

**Problem:** Rate limit exceeded
**Solution:** Wait a few minutes, or switch to local Ollama

### Google Drive Issues
**Problem:** OAuth consent screen error
**Solution:** Add yourself as test user in OAuth consent screen

**Problem:** Folder not found
**Solution:** Verify folder ID is correct, check folder permissions

---

## 🎯 Next Steps

Once setup is complete:

1. **Test the installation:**
   ```bash
   python -m youtube_chat_cli_main verify-connections
   ```

2. **Run your first RAG query:**
   ```bash
   python -m youtube_chat_cli_main chat
   ```

3. **Process your first document:**
   ```bash
   python -m youtube_chat_cli_main process-file document.pdf
   ```

4. **Start background service:**
   ```bash
   python -m youtube_chat_cli_main start-background-service
   ```

---

## 📚 Additional Resources

- **Ollama Documentation:** https://ollama.ai/docs
- **Tesseract Documentation:** https://tesseract-ocr.github.io/
- **OpenRouter Models:** https://openrouter.ai/models
- **Google Drive API:** https://developers.google.com/drive/api/guides/about-sdk
- **ChromaDB Documentation:** https://docs.trychroma.com/

---

**You're all set! Enjoy your completely free, powerful RAG system! 🎉**

