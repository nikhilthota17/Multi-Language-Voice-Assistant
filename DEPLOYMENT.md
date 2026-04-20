# 🚀 Deployment Guide - Multi-Language Voice Assistant

## Prerequisites for Streamlit Cloud

1. **GitHub Repository** - Push your code to GitHub
2. **GROQ API Key** - Get from [console.groq.com](https://console.groq.com)
3. **Streamlit Account** - Sign up at [streamlit.io](https://streamlit.io)

## Steps to Deploy on Streamlit Cloud

### 1. Add Secrets to Streamlit Cloud
Go to **"Manage app"** → **"Settings"** → **"Secrets"** → Add this:

```toml
GROQ_API_KEY = "your_groq_api_key_here"
```

### 2. Deploy via GitHub
1. Go to [share.streamlit.io](https://share.streamlit.io)
2. Click **"New app"**
3. Select your GitHub repo and `app.py`
4. Click **Deploy**

## Fixed Issues

✅ **Audio Format Handling** - Now converts webm to wav properly  
✅ **ffmpeg Support** - Added ffmpeg-python for audio conversion  
✅ **Dependencies** - Removed duplicates and pinned versions  
✅ **Streamlit Config** - Added media server settings  
✅ **Error Handling** - Better error messages for debugging  

## Testing Locally

```bash
pip install -r requirements.txt
streamlit run app.py
```

Set the `GROQ_API_KEY` environment variable:

**Windows (PowerShell):**
```powershell
$env:GROQ_API_KEY = "your_key_here"
streamlit run app.py
```

**Linux/Mac:**
```bash
export GROQ_API_KEY="your_key_here"
streamlit run app.py
```

## Troubleshooting

| Issue | Solution |
|-------|----------|
| "installer returned a non-zero exit code" | ✅ Fixed - removed broken ffmpeg-python, using standard library instead |
| "Error during processing dependencies" | Make sure `requirements.txt` has no broken packages - should install cleanly now |
| "Audio file could not be read" | ✅ Fixed - speech_to_text.py now handles audio bytes properly |
| "GROQ_API_KEY missing" | Add it to Streamlit Secrets in "Manage app" → Settings → Secrets |
| Audio not recording | Check browser permissions for microphone |
| Slow response time | Use shorter `max_tokens` in ai_response.py (currently 60) |
| ModuleNotFoundError with dependencies | Wait 5 mins after deployment for all packages to install, then refresh browser |

## Performance Tips

- Keep responses short (60 tokens max recommended)
- Use Groq's fastest models for real-time conversations
- Test locally before deploying

## Support

If deployment still fails:
1. Check Streamlit Cloud logs (Manage app → Logs)
2. Verify all environment variables are set
3. Ensure requirements.txt is in the root directory
