# JAEGIS NexusSync - Quick Start Guide

## 🚀 Start in 3 Steps

### 1️⃣ Start API Server
```bash
python run_api_server.py
```
✅ Server running on `http://localhost:8555`

### 2️⃣ Start Dashboard
```bash
cd youtube_chat_cli_main\workspace-ae4a103b-351b-4c44-8352-ad192e1dfc24
npm run dev
```
✅ Dashboard running on `http://localhost:3000`

### 3️⃣ Open Browser
Navigate to: **`http://localhost:3000`**

---

## ✨ What's Working

### 💬 Chat Interface
- Ask questions to RAG-powered AI
- Get answers from your knowledge base
- See sources and metadata

**Try it:**
- "Can you tell me about the indexed sources?"
- "What documents are in the knowledge base?"

### 🖥️ Natural Language Terminal
- Type commands in plain English
- Auto-converts to CLI commands
- Executes automatically

**Try it:**
- "sync my Google Drive folder"
- "show system status"
- "search for AI papers"

---

## 📚 Documentation

- **FINAL_STATUS_REPORT.md** - Complete status and features
- **DASHBOARD_INTEGRATION_FIXES.md** - Technical details
- **COMPLETE_TESTING_GUIDE.md** - How to test everything
- **GOOGLE_DRIVE_OAUTH_FIX.md** - OAuth setup guide

---

## 🔧 Troubleshooting

**Dashboard won't start?**
```bash
npm install
npm run dev
```

**Chat not working?**
- Check `.env.local` exists in dashboard directory
- Should contain: `NEXT_PUBLIC_API_URL=http://localhost:8555`

**Need help?**
- Check API server logs
- Open browser console (F12)
- See COMPLETE_TESTING_GUIDE.md

---

## ✅ System Status

- ✅ Chat Interface → RAG Backend: **WORKING**
- ✅ Natural Language Terminal: **WORKING**
- ✅ API Server (port 8555): **READY**
- ✅ Dashboard (port 3000): **READY**

**Everything is fully functional!** 🎉

