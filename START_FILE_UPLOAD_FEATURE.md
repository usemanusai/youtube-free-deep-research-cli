# 🚀 Start File Upload Feature - Quick Guide

## The Problem You Had

You saw this error when trying to start the API server:
```
ImportError: attempted relative import with no known parent package
```

**Why?** The script was trying to run `python youtube_chat_cli_main\api_server.py` directly, which doesn't work with Python's module system.

## ✅ The Solution

Use the proper launcher script that sets up the Python path correctly.

---

## 🎯 Quick Start (2 Commands)

### Terminal 1: Start API Server

```powershell
.\restart_api_server.bat
```

**OR** use the existing script:

```powershell
cd youtube_chat_cli_main
.\start_api_server.bat
```

### Terminal 2: Start Dashboard

```powershell
cd youtube_chat_cli_main\workspace-ae4a103b-351b-4c44-8352-ad192e1dfc24
npm run dev
```

### Open Browser

```
http://localhost:3000
```

---

## 📋 What You Should See

### API Server Output
```
============================================================
JAEGIS NexusSync - Restarting API Server
============================================================

Activating virtual environment...

Starting API server on port 8555...
Press Ctrl+C to stop the server

============================================================
JAEGIS NexusSync API Server
============================================================

Starting API server on http://localhost:8555
API documentation: http://localhost:8555/docs

Press Ctrl+C to stop the server

INFO:     Will watch for changes in these directories: ['C:\\Users\\...']
INFO:     Uvicorn running on http://0.0.0.0:8555 (Press CTRL+C to quit)
INFO:     Started reloader process [12345] using WatchFiles
INFO:     Started server process [67890]
INFO:     Waiting for application startup.
INFO:     Application startup complete.
```

### Dashboard Output
```
  ▲ Next.js 14.x.x
  - Local:        http://localhost:3000
  - Environments: .env.local

 ✓ Starting...
 ✓ Ready in 2.5s
```

---

## 🎨 What to Look For in the Browser

1. **Chat Interface** should load at `http://localhost:3000`
2. **Paperclip Icon** (📎) should appear next to the chat input field
3. **Click the paperclip** to open the file upload dialog
4. **Two tabs** should be visible:
   - "Local Files" - Upload from your computer
   - "Google Drive" - Browse files from Google Drive

---

## 🧪 Quick Test

### Test 1: Upload a Local File

1. Click the paperclip icon (📎)
2. Make sure you're on the "Local Files" tab
3. Click the upload area or drag a file
4. Select a text file (TXT, PDF, MD, etc.)
5. Click "Upload File"
6. Watch the progress bar
7. Success message should appear in chat

### Test 2: Browse Google Drive

1. Click the paperclip icon (📎)
2. Click the "Google Drive" tab
3. Files from your Google Drive should load
4. Click on a file to download it
5. Watch the progress bar
6. Success message should appear in chat

### Test 3: Query Uploaded Files

After uploading a file, type in the chat:
```
What is this document about?
```

You should get an AI-generated answer based on the file content.

---

## ❌ Troubleshooting

### Error: "ImportError: attempted relative import"

**Solution:** Don't run `python youtube_chat_cli_main\api_server.py` directly.
Use the launcher script instead:
```powershell
.\restart_api_server.bat
```

### Error: "restart_api_server.bat is not recognized"

**Solution:** Add `.\` before the command in PowerShell:
```powershell
.\restart_api_server.bat
```

### Error: "Port 8555 is already in use"

**Solution:** Kill the existing process:
```powershell
# Find the process
netstat -ano | findstr :8555

# Kill it (replace PID with the actual process ID)
taskkill /PID <PID> /F

# Then restart
.\restart_api_server.bat
```

### Dashboard shows "Failed to fetch" or "Network error"

**Solution:**
1. Make sure API server is running on port 8555
2. Check `.env.local` has correct API URL:
   ```env
   NEXT_PUBLIC_API_URL=http://localhost:8555
   ```
3. Restart the dashboard:
   ```powershell
   cd youtube_chat_cli_main\workspace-ae4a103b-351b-4c44-8352-ad192e1dfc24
   npm run dev
   ```

### Paperclip icon not visible

**Solution:**
1. Hard refresh the browser (Ctrl + Shift + R)
2. Clear browser cache
3. Check browser console for errors (F12)
4. Make sure dashboard restarted after code changes

---

## 📝 Summary

**The file upload feature is fully implemented!** You just need to:

1. ✅ Start API server with `.\restart_api_server.bat`
2. ✅ Start dashboard with `npm run dev` in the workspace directory
3. ✅ Open browser to `http://localhost:3000`
4. ✅ Click the paperclip icon to upload files
5. ✅ Ask questions about your uploaded files

**All the code is ready - just restart the servers and test it!**

---

## 🔗 More Information

- **Full Implementation Details**: `FILE_UPLOAD_FEATURE_IMPLEMENTATION.md`
- **Architecture Diagrams**: `FILE_UPLOAD_ARCHITECTURE.md`
- **Detailed Quick Start**: `QUICK_START_FILE_UPLOAD.md`
- **API Documentation**: `youtube_chat_cli_main/API_DOCUMENTATION.md`

---

## ✨ What's New

### Backend (API Server)
- ✅ New endpoint: `GET /api/v1/gdrive/list` - List Google Drive files
- ✅ New endpoint: `POST /api/v1/gdrive/download` - Download from Google Drive
- ✅ Existing endpoint: `POST /api/v1/files/upload` - Upload local files

### Frontend (Dashboard)
- ✅ New component: `file-upload-dialog.tsx` - File upload dialog
- ✅ Updated component: `chat-interface.tsx` - Added paperclip button
- ✅ Two-tab interface: Local Files + Google Drive
- ✅ Progress indicators for uploads and downloads
- ✅ Success notifications in chat

### Integration
- ✅ Files automatically indexed in ChromaDB
- ✅ Immediate querying after upload
- ✅ Session tracking for uploaded files
- ✅ Google Drive OAuth integration

**Everything is ready to go! 🎉**

