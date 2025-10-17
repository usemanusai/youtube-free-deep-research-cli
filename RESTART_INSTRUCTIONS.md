# 🚀 Restart Instructions - Port 8555

## What Changed

The API server port has been changed from **8000** to **8555** because port 8000 was already in use.

---

## Step-by-Step Restart Process

### Step 1: Stop the Current Server

In the terminal where the API server is running:
```
Press Ctrl+C
```

Wait for the server to shut down completely.

---

### Step 2: Verify Port Change

Run the verification script to ensure all files were updated:

```bash
python youtube_chat_cli_main/verify_port_change.py
```

**Expected output:**
```
✅ All files have been updated correctly!
```

---

### Step 3: Restart the API Server

From the repository root directory:

```bash
python run_api_server.py
```

**Expected output:**
```
============================================================
JAEGIS NexusSync API Server
============================================================

Starting API server on http://localhost:8555
API documentation: http://localhost:8555/docs

Press Ctrl+C to stop the server

INFO:     Will watch for changes in these directories: [...]
INFO:     Uvicorn running on http://0.0.0.0:8555 (Press CTRL+C to quit)
INFO:     Started reloader process [...]
INFO:     Started server process [...]
INFO:     Waiting for application startup.
INFO:     Application startup complete.
```

**Look for:**
- ✅ Port 8555 (not 8000)
- ✅ No error messages
- ✅ "Application startup complete"

---

### Step 4: Verify the Server is Running

**Open in your browser:**

1. **Landing Page:** `http://localhost:8555/`
   - Should show purple gradient page with "JAEGIS NexusSync API"

2. **API Documentation:** `http://localhost:8555/docs`
   - Should show Swagger UI with all endpoints

3. **Health Check:** `http://localhost:8555/api/v1/health`
   - Should return: `{"status": "healthy", "timestamp": ...}`

---

### Step 5: Run Automated Tests

Open a **NEW terminal** (keep the server running):

```bash
cd youtube_chat_cli_main
python test_api_endpoints.py
```

**Expected output:**
```
============================================================
JAEGIS NexusSync API - Endpoint Testing
============================================================
Testing API at: http://localhost:8555
============================================================

TEST: Root Endpoint (/)
✅ PASS: Status Code: 200
✓ HTML page returned successfully

TEST: Health Check (/api/v1/health)
✅ PASS: Status Code: 200

TEST: System Status (/api/v1/system/status)
✅ PASS: Status Code: 200

Service Status:
  ✓ database: {'status': 'ok'}
  ✓ vector_store: {'status': 'ok', 'type': 'chroma'}
  ✓ llm: {'status': 'ok'}
  ...
```

---

### Step 6: Update Dashboard Configuration (if needed)

If you plan to use the dashboard, create the environment file:

```bash
cd workspace-ae4a103b-351b-4c44-8352-ad192e1dfc24
cp .env.local.example .env.local
```

The `.env.local` file should contain:
```env
NEXT_PUBLIC_API_URL=http://localhost:8555
```

---

### Step 7: Start the Dashboard (Optional)

```bash
cd workspace-ae4a103b-351b-4c44-8352-ad192e1dfc24
npm install  # First time only
npm run dev
```

Then open: `http://localhost:3000`

---

## Quick Reference

| Service | URL |
|---------|-----|
| **API Server** | `http://localhost:8555` |
| **API Docs** | `http://localhost:8555/docs` |
| **Health Check** | `http://localhost:8555/api/v1/health` |
| **System Status** | `http://localhost:8555/api/v1/system/status` |
| **Dashboard** | `http://localhost:3000` |

---

## Troubleshooting

### Issue: Server won't start on port 8555

**Check if port is in use:**

**Windows:**
```bash
netstat -ano | findstr :8555
```

**Linux/Mac:**
```bash
lsof -i :8555
```

**If port is in use, kill the process or choose a different port.**

---

### Issue: "Address already in use" error

This means port 8555 is occupied. You have two options:

**Option 1: Kill the process using port 8555**

**Windows:**
```bash
netstat -ano | findstr :8555
taskkill /PID <PID> /F
```

**Linux/Mac:**
```bash
lsof -i :8555
kill -9 <PID>
```

**Option 2: Use a different port**

Edit `run_api_server.py` and change:
```python
port=8555,  # Change to another port like 8556
```

Then update `.env.local` in the dashboard directory to match.

---

### Issue: Dashboard can't connect to API

**Check browser console for errors:**
- Open browser DevTools (F12)
- Look for CORS or network errors

**Verify environment file:**
```bash
cd workspace-ae4a103b-351b-4c44-8352-ad192e1dfc24
cat .env.local
```

Should show: `NEXT_PUBLIC_API_URL=http://localhost:8555`

**Restart the dashboard:**
```bash
npm run dev
```

---

### Issue: Tests fail with connection errors

**Make sure the API server is running:**
```bash
# Check if server is responding
curl http://localhost:8555/api/v1/health
```

**If no response, restart the server:**
```bash
python run_api_server.py
```

---

## Success Checklist

- [ ] API server starts without errors
- [ ] Server shows "Uvicorn running on http://0.0.0.0:8555"
- [ ] Can access `http://localhost:8555/` in browser
- [ ] Landing page displays correctly
- [ ] API docs accessible at `/docs`
- [ ] Health check returns healthy status
- [ ] Automated tests pass
- [ ] Dashboard connects successfully (if using)

---

## Files Updated

All references to port 8000 have been updated to 8555 in:

✅ Server configuration files  
✅ Testing scripts  
✅ Documentation files  
✅ Frontend configuration  
✅ Startup scripts  

See `PORT_CHANGE_SUMMARY.md` for complete list.

---

**You're all set! The API server is now configured to run on port 8555.**

