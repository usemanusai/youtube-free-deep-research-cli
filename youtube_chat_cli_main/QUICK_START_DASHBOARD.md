# JAEGIS NexusSync Dashboard - Quick Start Guide

Get the dashboard up and running in 5 minutes!

## ⚡ Quick Start

### Step 1: Install Backend Dependencies

```bash
cd youtube_chat_cli_main
pip install -r api_requirements.txt
```

### Step 2: Start the API Server

**Windows:**
```bash
start_api_server.bat
```

**Linux/Mac:**
```bash
chmod +x start_api_server.sh
./start_api_server.sh
```

The API server will start on `http://localhost:8000`

### Step 3: Install Dashboard Dependencies

```bash
cd workspace-ae4a103b-351b-4c44-8352-ad192e1dfc24
npm install
```

### Step 4: Configure Environment

```bash
cp .env.local.example .env.local
```

The default configuration should work out of the box:
```env
NEXT_PUBLIC_API_URL=http://localhost:8000
```

### Step 5: Start the Dashboard

```bash
npm run dev
```

The dashboard will start on `http://localhost:3000`

### Step 6: Access the Dashboard

Open your browser and navigate to:
```
http://localhost:3000
```

## 🎯 What You Can Do

### 1. Chat with Your Knowledge Base
- Go to the **Chat** tab
- Type a question
- Get AI-powered answers from your documents

### 2. Upload Documents
- Go to the **Upload** tab
- Drag and drop files or click to browse
- Supported: PDF, DOC, DOCX, TXT, MD, JSON, XML, CSV, Images

### 3. Monitor Processing Queue
- Go to the **Queue** tab
- See files being processed
- Track status (pending, processing, completed, failed)

### 4. Check System Status
- Go to the **Status** tab
- View service health
- Monitor system metrics

### 5. Execute CLI Commands
- Go to the **Terminal** tab
- Type commands like `jaegis status` or `jaegis config`
- See real-time output

## 🔧 Verify Everything Works

### Test 1: Health Check

Open in browser:
```
http://localhost:8000/api/v1/health
```

Should return:
```json
{
  "status": "healthy",
  "timestamp": 1234567890
}
```

### Test 2: System Status

Open in browser:
```
http://localhost:8000/api/v1/system/status
```

Should return service status information.

### Test 3: API Documentation

Open in browser:
```
http://localhost:8000/docs
```

You should see the interactive Swagger UI with all API endpoints.

### Test 4: Dashboard

Open in browser:
```
http://localhost:3000
```

You should see the JAEGIS NexusSync dashboard.

## 🐛 Common Issues

### Issue: API server won't start

**Solution:**
```bash
# Check if port 8000 is in use
netstat -ano | findstr :8000  # Windows
lsof -i :8000                 # Linux/Mac

# Kill the process if needed
taskkill /PID <PID> /F        # Windows
kill -9 <PID>                 # Linux/Mac
```

### Issue: Dashboard can't connect to backend

**Solution:**
1. Verify API server is running: `http://localhost:8000/api/v1/health`
2. Check `.env.local` has `NEXT_PUBLIC_API_URL=http://localhost:8000`
3. Restart the dashboard: `npm run dev`

### Issue: npm install fails

**Solution:**
```bash
# Clear npm cache
npm cache clean --force

# Delete node_modules and package-lock.json
rm -rf node_modules package-lock.json

# Reinstall
npm install
```

### Issue: Python dependencies fail to install

**Solution:**
```bash
# Upgrade pip
python -m pip install --upgrade pip

# Install dependencies one by one
pip install fastapi
pip install uvicorn[standard]
pip install python-multipart
pip install aiofiles
```

## 📚 Next Steps

1. **Configure your services** - Edit `.env` file with your API keys
2. **Add documents** - Upload files through the dashboard
3. **Start chatting** - Ask questions about your documents
4. **Set up Google Drive** - Configure Google Drive sync
5. **Enable background service** - Automate document processing

## 🎓 Learn More

- **Full Documentation**: See `DASHBOARD_INTEGRATION.md`
- **API Reference**: `http://localhost:8000/docs`
- **CLI Commands**: Type `help` in the Terminal tab

## 💡 Tips

- Use the **Chat** tab for quick questions
- Use the **Upload** tab to add new documents
- Use the **Queue** tab to monitor processing
- Use the **Status** tab to check system health
- Use the **Terminal** tab for advanced commands

## 🚀 Production Deployment

When you're ready to deploy:

1. **Build the dashboard:**
   ```bash
   npm run build
   ```

2. **Run in production mode:**
   ```bash
   npm run start
   ```

3. **Use a production ASGI server:**
   ```bash
   gunicorn api_server:app -w 4 -k uvicorn.workers.UvicornWorker
   ```

## 📞 Support

If you encounter issues:

1. Check the browser console (F12) for errors
2. Check the API server logs
3. Verify all services are configured correctly
4. Review the full documentation in `DASHBOARD_INTEGRATION.md`

---

**Enjoy using JAEGIS NexusSync Dashboard! 🎉**

