# Quick Fix: Google Drive OAuth Error

## The Error You're Seeing

```
Fout 400: redirect_uri_mismatch
redirect_uri=http://localhost:61825/
```

---

## Quick Fix (5 Minutes)

### 1. Go to Google Cloud Console
👉 https://console.cloud.google.com/apis/credentials

### 2. Edit Your OAuth 2.0 Client ID
- Find client ID: `1079692665134-v2lqo45uenpgr42flfu5jh3nt6at9uvv`
- Click the pencil icon (✏️) to edit

### 3. Add These Redirect URIs
Click "+ ADD URI" and add:
```
http://localhost:8080/
http://127.0.0.1:8080/
```

### 4. Save and Wait
- Click "SAVE"
- Wait 5-10 minutes for Google to update

### 5. Restart API Server
```bash
# Press Ctrl+C to stop
python run_api_server.py
```

### 6. Try Again
```bash
python -m youtube_chat_cli_main.cli.main gdrive-auth
```

---

## What I Changed

✅ Updated code to use **fixed port 8080** instead of random port  
✅ File modified: `youtube_chat_cli_main/services/gdrive_service.py`

---

## Need More Help?

See detailed guide: `GOOGLE_DRIVE_OAUTH_FIX.md`

---

**That's it! After adding the redirect URI and waiting a few minutes, authentication should work.**

