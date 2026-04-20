import streamlit as st
import base64
from streamlit_mic_recorder import mic_recorder

from speech_to_text import listen
from translator import translate_text
from ai_response import get_ai_response
from text_to_speech import speak
from main import handle_commands

# =========================
# PAGE CONFIG
# =========================
st.set_page_config(
    page_title="AI Multi-language Voice Assistant",
    page_icon="✨",
    layout="wide"
)

# =========================
# PREMIUM CSS
# =========================
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');

.stApp {
    background-color:#f8fafc;
    font-family:'Inter',sans-serif;
}

#MainMenu {visibility:hidden;}
footer {visibility:hidden;}
header {visibility:hidden;}

.block-container{
    max-width:900px;
    padding-top:2rem;
}

.app-header{
    background:white;
    padding:2rem;
    border-radius:18px;
    text-align:center;
    border:1px solid #e2e8f0;
    margin-bottom:2rem;
}

.app-header h1{
    font-size:2.7rem;
    margin:0;
}

.app-header span{
    color:#4f46e5;
}

.app-header p{
    color:#64748b;
    margin-top:8px;
}

.stButton button{
    width:100%;
    border-radius:12px;
}

div[data-testid="stChatMessage"]{
    border-radius:16px;
}
</style>
""", unsafe_allow_html=True)

# =========================
# HEADER
# =========================
st.markdown("""
<div class="app-header">
<h1>✨ <span>AI</span> Multi-Language Voice Assistant</h1>
<p>Seamless intelligent conversations across languages.</p>
</div>
""", unsafe_allow_html=True)

# =========================
# SESSION STATE
# =========================
if "messages" not in st.session_state:
    st.session_state.messages = []

# =========================
# LANGUAGE
# =========================
lang_map = {
    "English": "en",
    "Hindi": "hi",
    "Telugu": "te"
}

col1, col2, col3 = st.columns([1,2,1])

with col2:
    selected = st.selectbox(
        "🌐 Select Language",
        list(lang_map.keys()),
        index=0
    )

lang = lang_map[selected]

# =========================
# SHOW CHAT HISTORY
# =========================
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.write(msg["content"])

# =========================
# MICROPHONE
# =========================
st.markdown("### 🎤 Speak")

audio = mic_recorder(
    start_prompt="🎙 Tap to Speak",
    stop_prompt="⏹ Stop Recording",
    just_once=True,
    key="main_mic"
)

# =========================
# HANDLE MIC INPUT
# =========================
if audio:

    with st.spinner("🎙 Listening..."):
        text = listen(audio["bytes"])

    if text and text.lower() != "error":

        st.session_state.messages.append({
            "role":"user",
            "content":text
        })

        with st.chat_message("user"):
            st.write(text)

        with st.spinner("✨ Processing..."):

            try:
                # translate to english
                if lang != "en":
                    query = translate_text(text, "en")
                else:
                    query = text

                # commands
                command = handle_commands(query)

                if command:
                    reply = command
                else:
                    reply = get_ai_response(query)

                # translate back
                if lang != "en":
                    final_reply = translate_text(reply, lang)
                else:
                    final_reply = reply

            except Exception:
                final_reply = "Sorry, I encountered an error."

        st.session_state.messages.append({
            "role":"assistant",
            "content":final_reply
        })

        with st.chat_message("assistant"):
            st.write(final_reply)

        # voice reply
        with st.spinner("🔊 Speaking..."):
            audio_file = speak(final_reply, lang)

            if audio_file:
                with open(audio_file, "rb") as f:
                    audio_bytes = f.read()

                b64 = base64.b64encode(audio_bytes).decode()

                st.markdown(
                    f"""
                    <audio autoplay>
                    <source src="data:audio/mp3;base64,{b64}" type="audio/mp3">
                    </audio>
                    """,
                    unsafe_allow_html=True
                )

    else:
        st.warning("Sorry, I couldn't hear you clearly.")

# =========================
# TEXT INPUT
# =========================
user_input = st.chat_input("Or type your message here...")

if user_input:

    st.session_state.messages.append({
        "role":"user",
        "content":user_input
    })

    st.rerun()