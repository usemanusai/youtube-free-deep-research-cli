# JAEGIS NexusSync Dashboard - Testing Guide

Step-by-step testing guide for the web dashboard integration.

## 🧪 Pre-Testing Setup

### 1. Start the Backend
```bash
cd youtube_chat_cli_main
python api_server.py
```

Verify: `curl http://localhost:8000/api/v1/health`

### 2. Start the Dashboard
```bash
cd workspace-ae4a103b-351b-4c44-8352-ad192e1dfc24
npm run dev
```

Open: `http://localhost:3000`

## ✅ Quick Test Checklist

### Backend Tests
- [ ] API server starts without errors
- [ ] Health endpoint responds: `http://localhost:8000/api/v1/health`
- [ ] Swagger UI loads: `http://localhost:8000/docs`
- [ ] System status endpoint works
- [ ] Chat query endpoint works
- [ ] File upload endpoint works

### Frontend Tests
- [ ] Dashboard loads without console errors
- [ ] All 8 tabs are visible and clickable
- [ ] Chat interface sends and receives messages
- [ ] File upload accepts files
- [ ] Queue manager displays items
- [ ] System status shows real data
- [ ] Terminal executes commands
- [ ] Settings panel loads

### Integration Tests
- [ ] Dashboard connects to backend
- [ ] Chat queries return AI responses
- [ ] File uploads add to processing queue
- [ ] Queue processing updates status
- [ ] Real-time updates work (auto-refresh)
- [ ] Error handling shows toast notifications

### CLI Compatibility Tests
- [ ] `python cli/main.py chat` still works
- [ ] `python cli/main.py status` still works
- [ ] All other CLI commands work unchanged

## 📋 Detailed Test Scenarios

### Test 1: Chat Interface
1. Navigate to **Chat** tab
2. Type: "What is JAEGIS NexusSync?"
3. Press Enter
4. **Expected**: AI response appears with source documents

### Test 2: File Upload
1. Navigate to **Upload** tab
2. Create test file: `echo "Test" > test.txt`
3. Drag and drop `test.txt`
4. **Expected**: Progress bar → Success indicator → Appears in queue

### Test 3: Queue Management
1. Navigate to **Queue** tab
2. Click **Process Queue**
3. Watch status change: Pending → Processing → Completed
4. **Expected**: File processes successfully

### Test 4: Terminal Commands
1. Navigate to **Terminal** tab
2. Type: `help`
3. **Expected**: Help text appears
4. Type: `jaegis status`
5. **Expected**: System status appears

### Test 5: System Status
1. Navigate to **Status** tab
2. Click **Refresh**
3. **Expected**: Service statuses update

## 🐛 Common Issues

### CORS Error
**Fix**: Verify CORS middleware in `api_server.py` allows `http://localhost:3000`

### Connection Refused
**Fix**: 
1. Check backend is running
2. Verify `.env.local` has `NEXT_PUBLIC_API_URL=http://localhost:8000`

### File Upload Fails
**Fix**: Create `uploads/` directory

### Chat Timeout
**Fix**: Check LLM service is configured and running

## 📊 Test Results

```
Date: ___________
Tester: ___________

Backend Tests: ⬜ Pass ⬜ Fail
Frontend Tests: ⬜ Pass ⬜ Fail
Integration Tests: ⬜ Pass ⬜ Fail
CLI Compatibility: ⬜ Pass ⬜ Fail

Overall: ⬜ Ready ⬜ Needs Fixes

Notes:
_________________________________
_________________________________
```

## 🚀 Production Readiness

Before deploying to production:

- [ ] All tests pass
- [ ] No console errors
- [ ] No TypeScript errors
- [ ] Environment variables configured
- [ ] Build process tested (`npm run build`)
- [ ] Production server tested (`npm run start`)
- [ ] Error logging configured
- [ ] Monitoring configured

## 📚 Resources

- **Quick Start**: `QUICK_START_DASHBOARD.md`
- **Full Documentation**: `DASHBOARD_INTEGRATION.md`
- **API Docs**: `http://localhost:8000/docs`

