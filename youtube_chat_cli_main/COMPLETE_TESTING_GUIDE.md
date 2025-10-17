# JAEGIS NexusSync - Complete Testing Guide

## Quick Start

### 1. Start API Server
```bash
python run_api_server.py
```
Expected: Server running on `http://localhost:8555`

### 2. Start Dashboard
```bash
cd youtube_chat_cli_main\workspace-ae4a103b-351b-4c44-8352-ad192e1dfc24
npm run dev
```
Expected: Dashboard running on `http://localhost:3000`

### 3. Open Browser
Navigate to: `http://localhost:3000`

---

## Test Scenarios

### ✅ Test 1: Chat Interface with RAG

**Steps:**
1. Go to Chat tab
2. Type: "Can you tell me how many sources are indexed?"
3. Press Enter

**Expected:**
- Message sent successfully
- AI response received
- Metadata badges show (Web Search, Sources, etc.)
- No errors in console

---

### ✅ Test 2: Natural Language Terminal

**Steps:**
1. Go to Terminal tab
2. Type: "sync my Google Drive folder"
3. Press Enter

**Expected:**
- Converts to: `jaegis gdrive-sync`
- Confidence: 90%
- Command executes
- Results displayed

**More examples to try:**
- "upload a PDF file" → `jaegis add-file`
- "show system status" → `jaegis status`
- "search for AI papers" → `jaegis search AI papers`

---

### ✅ Test 3: Direct CLI Commands

**Steps:**
1. In Terminal tab, type: `help`
2. Type: `jaegis status`
3. Type: `clear`

**Expected:**
- All commands execute immediately
- No conversion step
- Results displayed correctly

---

## Troubleshooting

### Chat not working?
1. Check `.env.local` exists in dashboard directory
2. Verify it contains: `NEXT_PUBLIC_API_URL=http://localhost:8555`
3. Restart dashboard

### Terminal not converting?
1. Check API server logs
2. Test endpoint:
   ```bash
   curl -X POST http://localhost:8555/api/v1/terminal/convert \
     -H "Content-Type: application/json" \
     -d "{\"input\": \"sync drive\"}"
   ```

### Dashboard won't start?
1. Check node_modules exists
2. Run: `npm install`
3. Try: `npm run dev` again

---

## Success Checklist

- [ ] API server running (port 8555)
- [ ] Dashboard running (port 3000)
- [ ] Chat sends/receives messages
- [ ] Natural language converts to commands
- [ ] Commands execute successfully
- [ ] No console errors

**All checked? System is fully functional!** ✅

