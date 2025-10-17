# Google Drive OAuth 2.0 Configuration Fix

## Problem

When trying to authenticate with Google Drive, you get this error:

```
Fout 400: redirect_uri_mismatch

Je kunt niet inloggen bij de app omdat deze niet voldoet aan het OAuth 2.0-beleid van Google.

Details van verzoek: redirect_uri=http://localhost:61825/
```

**Root Cause:** The redirect URI is not registered in your Google Cloud Console OAuth 2.0 configuration.

---

## Solution Applied

I've updated the code to use a **fixed port (8080)** instead of a random port. This makes it easier to configure in Google Cloud Console.

**File Modified:** `youtube_chat_cli_main/services/gdrive_service.py`
- Changed `port=0` (random) to `port=8080` (fixed)

---

## Step-by-Step Fix

### Step 1: Add Redirect URI to Google Cloud Console

1. **Open Google Cloud Console:**
   - Visit: https://console.cloud.google.com/apis/credentials

2. **Sign in** with your Google account

3. **Select the correct project:**
   - Make sure you're in the project that contains your OAuth 2.0 credentials

4. **Find your OAuth 2.0 Client ID:**
   - Look for the client ID: `1079692665134-v2lqo45uenpgr42flfu5jh3nt6at9uvv`
   - Click on the pencil icon (✏️) to edit it

5. **Add Authorized Redirect URIs:**
   - Scroll down to the "Authorized redirect URIs" section
   - Click "+ ADD URI"
   - Add these URIs one by one:
     ```
     http://localhost:8080/
     http://127.0.0.1:8080/
     ```

6. **Save the changes:**
   - Click the "SAVE" button at the bottom

7. **Wait 5-10 minutes:**
   - Google needs time to propagate the changes across their servers

---

### Step 2: Verify Port 8080 is Available

Before authenticating, make sure port 8080 is not in use:

**Windows:**
```bash
netstat -ano | findstr :8080
```

**Linux/Mac:**
```bash
lsof -i :8080
```

**If port 8080 is in use:**
- Stop the service using that port, OR
- Choose a different port (see "Alternative Ports" section below)

---

### Step 3: Restart the API Server

Since we modified the code, restart the API server:

```bash
# Stop the current server (Ctrl+C)
python run_api_server.py
```

---

### Step 4: Authenticate with Google Drive

Now try authenticating again:

```bash
python -m youtube_chat_cli_main.cli.main gdrive-auth
```

**Expected flow:**

1. A browser window will open automatically
2. You'll be asked to sign in to your Google account
3. You'll be asked to grant permissions to the app
4. After granting permissions, you'll see: "Authorization successful! You can close this window."
5. The terminal will show: "Google Drive authentication successful!"

---

### Step 5: Verify Authentication

Check if the token was saved:

**Windows:**
```bash
dir youtube_chat_cli_main\token.json
```

**Linux/Mac:**
```bash
ls -l youtube_chat_cli_main/token.json
```

If the file exists, authentication was successful!

---

## Alternative Ports

If port 8080 is not available, you can use a different port:

### Option 1: Use Port 8090

1. **Edit the code:**
   - Open `youtube_chat_cli_main/services/gdrive_service.py`
   - Find line 110: `port=8080,`
   - Change to: `port=8090,`

2. **Add to Google Cloud Console:**
   - Add these redirect URIs:
     ```
     http://localhost:8090/
     http://127.0.0.1:8090/
     ```

### Option 2: Use Port 9090

1. **Edit the code:**
   - Change `port=8080,` to `port=9090,`

2. **Add to Google Cloud Console:**
   - Add these redirect URIs:
     ```
     http://localhost:9090/
     http://127.0.0.1:9090/
     ```

---

## Troubleshooting

### Issue: Still getting redirect_uri_mismatch

**Possible causes:**

1. **Changes not propagated yet:**
   - Wait 10-15 minutes after saving in Google Cloud Console
   - Try clearing your browser cache

2. **Wrong OAuth Client ID:**
   - Make sure you edited the correct OAuth 2.0 Client ID
   - The client ID should match the one in your `client_secret.json` file

3. **Typo in redirect URI:**
   - Make sure the URI is exactly: `http://localhost:8080/`
   - Include the trailing slash `/`
   - Use `http://` not `https://`

### Issue: Browser doesn't open automatically

**Manual authentication:**

1. Copy the URL from the terminal
2. Paste it into your browser manually
3. Complete the authentication flow
4. The callback should still work

### Issue: "Address already in use" error

**Port 8080 is occupied:**

1. Find what's using the port:
   ```bash
   # Windows
   netstat -ano | findstr :8080
   
   # Linux/Mac
   lsof -i :8080
   ```

2. Either:
   - Stop that service, OR
   - Use a different port (see "Alternative Ports" above)

### Issue: client_secret.json not found

**Make sure the file exists:**

```bash
# Check if file exists
ls youtube_chat_cli_main/client_secret.json
```

**If missing:**

1. Download it from Google Cloud Console:
   - Go to: https://console.cloud.google.com/apis/credentials
   - Click on your OAuth 2.0 Client ID
   - Click "DOWNLOAD JSON"
   - Save it as `client_secret.json` in the `youtube_chat_cli_main` directory

---

## Google Cloud Console - Detailed Steps

### Finding Your OAuth 2.0 Client ID

1. Go to: https://console.cloud.google.com/apis/credentials
2. Look for "OAuth 2.0 Client IDs" section
3. You should see an entry with:
   - **Name:** Something like "Desktop client 1" or custom name
   - **Client ID:** `1079692665134-v2lqo45uenpgr42flfu5jh3nt6at9uvv...`
   - **Type:** Desktop app or Web application

### Adding Redirect URIs (with Screenshots Guide)

1. **Click the pencil icon (✏️)** next to your OAuth 2.0 Client ID

2. **Scroll to "Authorized redirect URIs"**

3. **Click "+ ADD URI"**

4. **Enter the URI:** `http://localhost:8080/`
   - Make sure to include the trailing slash!
   - Use `http://` not `https://`

5. **Click "+ ADD URI" again** and add: `http://127.0.0.1:8080/`

6. **Click "SAVE"** at the bottom of the page

7. **Wait 5-10 minutes** for changes to propagate

---

## Testing the Fix

After completing all steps, test the authentication:

```bash
# Authenticate
python -m youtube_chat_cli_main.cli.main gdrive-auth

# If successful, test listing files
python -m youtube_chat_cli_main.cli.main gdrive-list
```

**Expected output:**
```
Google Drive authentication successful!
Token saved to: youtube_chat_cli_main/token.json

Files in Google Drive:
- Document1.pdf (1.2 MB)
- Spreadsheet.xlsx (500 KB)
...
```

---

## Summary

✅ **Code updated** to use fixed port 8080  
✅ **Instructions provided** for Google Cloud Console configuration  
✅ **Alternative ports** documented if 8080 is unavailable  
✅ **Troubleshooting guide** included  

**Next step:** Add `http://localhost:8080/` to your Google Cloud Console OAuth 2.0 configuration and try authenticating again!

