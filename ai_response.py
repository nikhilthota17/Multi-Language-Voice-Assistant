import os
import streamlit as st
from dotenv import load_dotenv
from groq import Groq

# Load env (for local usage)
load_dotenv()

# Fallback mechanism: check OS/Env first, then Streamlit Secrets
api_key = os.getenv("GROQ_API_KEY")
if not api_key:
    try:
        api_key = st.secrets["GROQ_API_KEY"]
    except Exception:
        api_key = None

try:
    client = Groq(api_key=api_key)
except Exception:
    client = None


def get_ai_response(prompt):
    if not client:
        return "⚠️ GROQ API KEY is missing. If you are on Streamlit Cloud, add `GROQ_API_KEY` to your App Settings (Manage App > Settings > Secrets)."

    try:
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",  # latest working model
            messages=[
                {"role": "system", "content": "You are a voice assistant. Answer briefly."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=60
        )

        return response.choices[0].message.content.strip()

    except Exception as e:
        print("Error:", e)
        return "Sorry, I'm having trouble right now."
