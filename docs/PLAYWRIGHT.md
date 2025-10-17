# Playwright Integration

## When to use Playwright vs requests
- Use Playwright for JS-heavy, client-rendered sites (infinite scroll, dynamic content, SPA frameworks).
- Use requests fallback for static/SSR pages where HTML contains the desired content.
- The scraper automatically tries Playwright first (if installed); on failure or when content remains empty, it falls back to requests.

## Installation
```
pip install playwright
playwright install chromium
```
Optional: to reduce resource usage, only install Chromium.

## Configuration
Key environment variables (see .env.example):
- SCRAPER_PLAYWRIGHT_STEALTH=true|false
- SCRAPER_WAIT_SELECTORS={"host": [".selector", "#id"]}
- SCRAPER_PROXY_URL=socks5://127.0.0.1:1080 or http://user:pass@host:port
- SCRAPER_BLOCK_RESOURCES=analytics,ad,tracker,image,media
- SCRAPER_COOKIES_JSON=[{"name":"session","value":"...","domain":"example.com"}]
- SCRAPER_LOCAL_STORAGE_JSON={"token":"..."}
- SCRAPER_VIEWPORT=desktop|tablet|mobile|1200x900
- SCRAPER_CANVAS_SPOOF=true|false

## Features enabled in WebScraperService
- Stealth mode: anti-automation flags, small random mouse movement
- Per-site waits: wait for specific selectors after load
- Request interception: block trackers/ads/images when configured
- Identity injection: cookies + localStorage
- Proxy support: pass-through to browser launch
- Canvas fingerprint spoofing (lightweight)
- Viewport presets/emulation
- Retries with exponential backoff and error screenshots (./logs/scraper_errors)

