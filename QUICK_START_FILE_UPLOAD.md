# Quick Start: File Upload Feature

## 🚀 Start the System

### Step 1: Start the API Server

Open a terminal and run:

```batch
.\restart_api_server.bat
```

Or use the existing startup script:

```batch
cd youtube_chat_cli_main
.\start_api_server.bat
```

Or manually:

```batch
# Activate virtual environment
venv\Scripts\activate.bat

# Start API server
python run_api_server.py
```

**Expected Output:**
```
INFO:     Started server process
INFO:     Waiting for application startup.
INFO:     Application startup complete.
INFO:     Uvicorn running on http://0.0.0.0:8555
```

### Step 2: Start the Dashboard

Open a **new terminal** and run:

```batch
cd youtube_chat_cli_main\workspace-ae4a103b-351b-4c44-8352-ad192e1dfc24
npm run dev
```

**Expected Output:**
```
  ▲ Next.js 14.x.x
  - Local:        http://localhost:3000
  - Ready in 2.5s
```

### Step 3: Open the Dashboard

Open your browser and navigate to:
```
http://localhost:3000
```

## 📤 Using the File Upload Feature

### Upload a Local File

1. **Click the paperclip icon** (📎) next to the chat input field
2. The **File Upload Dialog** will open
3. Make sure you're on the **"Local Files"** tab
4. **Click the upload area** or drag and drop a file
5. **Select a file** from your computer (PDF, TXT, DOC, DOCX, MD, CSV, JSON)
6. Click the **"Upload File"** button
7. Watch the **progress bar** as the file uploads
8. A **success message** will appear in the chat
9. The dialog will close automatically

### Upload from Google Drive

1. **Click the paperclip icon** (📎) next to the chat input field
2. The **File Upload Dialog** will open
3. Click the **"Google Drive"** tab
4. Files from your authenticated Google Drive account will load
5. **Click on a file** to select it
6. Watch the **progress bar** as the file downloads
7. A **success message** will appear in the chat
8. The dialog will close automatically

### Query Your Uploaded Files

After uploading a file, you can immediately ask questions about it:

**Example Questions:**
- "What is this document about?"
- "Summarize the main points"
- "What does it say about [topic]?"
- "Find information about [keyword]"

## 🧪 Testing the Feature

### Test 1: Local File Upload

1. Create a test file:
   ```batch
   echo "This is a test document about artificial intelligence." > test_doc.txt
   ```

2. Upload it using the paperclip button

3. Ask: "What is this document about?"

4. Expected response: Information about artificial intelligence

### Test 2: Google Drive File

1. Make sure you have files in your Google Drive folder

2. Click paperclip → Google Drive tab

3. Select a file from the list

4. Ask questions about the file content

### Test 3: Multiple Files

1. Upload multiple files (local and/or Google Drive)

2. Ask: "How many sources are currently indexed in the RAG?"

3. Ask questions that span multiple documents

## 🔍 Troubleshooting

### Issue: Paperclip button not visible

**Solution:**
1. Make sure the dashboard is running on port 3000
2. Hard refresh the browser (Ctrl + Shift + R)
3. Check browser console for errors (F12)

### Issue: File upload fails

**Solution:**
1. Check file size (should be reasonable, < 10MB)
2. Verify file type is supported
3. Check API server logs for errors
4. Ensure API server is running on port 8555

### Issue: Google Drive files not loading

**Solution:**
1. Verify Google Drive OAuth is configured
2. Check if `client_secret.json` exists
3. Check if `token.pickle` exists
4. Re-authenticate if needed:
   ```batch
   python youtube_chat_cli_main\cli.py gdrive-sync
   ```

### Issue: Uploaded files not queryable

**Solution:**
1. Wait a few seconds for processing to complete
2. Check the processing queue:
   ```batch
   python youtube_chat_cli_main\cli.py queue-status
   ```
3. Process the queue manually if needed:
   ```batch
   python youtube_chat_cli_main\cli.py process-queue
   ```

### Issue: API server not responding

**Solution:**
1. Check if server is running:
   ```batch
   netstat -ano | findstr :8555
   ```
2. Restart the server:
   ```batch
   restart_api_server.bat
   ```
3. Check for port conflicts

### Issue: Dashboard not connecting to API

**Solution:**
1. Verify `.env.local` has correct API URL:
   ```env
   NEXT_PUBLIC_API_URL=http://localhost:8555
   ```
2. Restart the dashboard:
   ```batch
   cd youtube_chat_cli_main\workspace-ae4a103b-351b-4c44-8352-ad192e1dfc24
   npm run dev
   ```
3. Clear browser cache

## 📊 Monitoring

### Check API Server Health

```batch
curl http://localhost:8555/api/v1/health
```

### Check Google Drive Status

```batch
curl http://localhost:8555/api/v1/gdrive/status
```

### List Google Drive Files

```batch
curl http://localhost:8555/api/v1/gdrive/list?page_size=10
```

### Check Processing Queue

```batch
python youtube_chat_cli_main\cli.py queue-status
```

## 🎯 Feature Checklist

Use this checklist to verify everything is working:

- [ ] API server starts without errors
- [ ] Dashboard starts without errors
- [ ] Dashboard loads at http://localhost:3000
- [ ] Chat interface is visible
- [ ] Paperclip button is visible next to input field
- [ ] Clicking paperclip opens file upload dialog
- [ ] File upload dialog has two tabs: "Local Files" and "Google Drive"
- [ ] Local Files tab allows file selection
- [ ] Local Files tab shows upload progress
- [ ] Local Files tab uploads file successfully
- [ ] Success message appears in chat after upload
- [ ] Google Drive tab loads files from account
- [ ] Google Drive tab allows file selection
- [ ] Google Drive tab shows download progress
- [ ] Google Drive tab downloads file successfully
- [ ] Uploaded files can be queried in chat
- [ ] Chat returns relevant answers from uploaded files

## 📝 Example Workflow

Here's a complete example workflow:

1. **Start the system**
   ```batch
   # Terminal 1
   restart_api_server.bat
   
   # Terminal 2
   cd youtube_chat_cli_main\workspace-ae4a103b-351b-4c44-8352-ad192e1dfc24
   npm run dev
   ```

2. **Open browser to http://localhost:3000**

3. **Upload a document**
   - Click paperclip icon
   - Select "Local Files" tab
   - Choose a PDF document
   - Click "Upload File"
   - Wait for success message

4. **Ask questions**
   - "What is this document about?"
   - "Summarize the key points"
   - "What does it say about [specific topic]?"

5. **Upload more documents**
   - Click paperclip icon
   - Select "Google Drive" tab
   - Choose a document from Google Drive
   - Click on it to download
   - Wait for success message

6. **Ask cross-document questions**
   - "Compare the information in both documents"
   - "What are the common themes?"
   - "Find all mentions of [keyword] across all documents"

## 🎨 UI Preview

### Chat Interface with Paperclip Button
```
┌─────────────────────────────────────────────────────┐
│  JAEGIS NexusSync RAG Chat                          │
├─────────────────────────────────────────────────────┤
│                                                     │
│  🤖 Hello! I'm your JAEGIS NexusSync RAG assistant. │
│     Ask me anything about your knowledge base!      │
│                                                     │
│  👤 [Your messages will appear here]                │
│                                                     │
├─────────────────────────────────────────────────────┤
│  [📎] [Ask a question...              ] [Send ➤]   │
└─────────────────────────────────────────────────────┘
```

### File Upload Dialog
```
┌─────────────────────────────────────────────────────┐
│  Upload File to Knowledge Base                      │
│  Choose a file from your computer or Google Drive   │
├─────────────────────────────────────────────────────┤
│  [ Local Files ]  [ Google Drive ]                  │
├─────────────────────────────────────────────────────┤
│                                                     │
│         ┌─────────────────────────────┐            │
│         │         📤                   │            │
│         │  Click to select a file     │            │
│         │  or drag and drop           │            │
│         │                             │            │
│         │  Supported: PDF, TXT, DOC,  │            │
│         │  DOCX, MD, CSV, JSON        │            │
│         └─────────────────────────────┘            │
│                                                     │
│  Selected: document.pdf (1.2 MB)                    │
│                                                     │
│  [Cancel]                    [Upload File ➤]        │
└─────────────────────────────────────────────────────┘
```

## 🔗 Related Documentation

- `FILE_UPLOAD_FEATURE_IMPLEMENTATION.md` - Complete implementation details
- `FILE_UPLOAD_ARCHITECTURE.md` - System architecture and data flow
- `API_DOCUMENTATION.md` - Full API reference
- `DASHBOARD_INTEGRATION.md` - Dashboard setup guide

## ✨ Tips & Best Practices

1. **File Size**: Keep files under 10MB for best performance
2. **File Types**: Use text-based formats (PDF, TXT, MD) for best results
3. **Processing Time**: Large files may take a few seconds to process
4. **Multiple Files**: Upload related documents together for better context
5. **Queries**: Be specific in your questions for better answers
6. **Session Management**: Start a new session for different topics

## 🎉 Success!

If you can see the paperclip button and successfully upload files, congratulations! The file upload feature is working correctly.

Now you can:
- Upload documents from your computer
- Import files from Google Drive
- Ask questions about your uploaded content
- Build a comprehensive knowledge base
- Get AI-powered answers from your documents

Happy chatting! 🚀

