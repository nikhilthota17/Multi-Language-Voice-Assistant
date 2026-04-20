import streamlit as st
import base64
from speech_to_text import listen
from translator import translate_text
from ai_response import get_ai_response
from text_to_speech import speak
from main import handle_commands
from streamlit_mic_recorder import mic_recorder

# =========================
# PAGE CONFIG
# =========================
st.set_page_config(page_title="AI Multi-language Voice Assistant", page_icon="✨", layout="wide")

# =========================
# PREMIUM CSS STYLING
# =========================
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');

.stApp {
    background-color: #f8fafc;
    font-family: 'Inter', sans-serif;
    color: #1e293b;
}

#MainMenu {visibility: hidden;}
footer {display: none !important;}
header {visibility: hidden;}

[data-testid="stBottomBlockContainer"], [data-testid="stBottom"] {
    background-color: transparent !important;
    background: transparent !important;
}

/* Container resizing for better chat layout */
.block-container {
    max-width: 900px !important;
    padding-top: 2rem !important;
}

.app-header {
    background: #ffffff;
    border: 1px solid #e2e8f0;
    padding: 2rem 1.5rem;
    border-radius: 16px;
    text-align: center;
    margin-bottom: 2rem;
    box-shadow: 0 4px 6px -1px rgba(0,0,0,0.05), 0 2px 4px -2px rgba(0,0,0,0.05);
}

.app-header h1 {
    font-weight: 800;
    font-size: 2.8rem;
    margin: 0;
    color: #1e293b;
    letter-spacing: -1px;
}

.app-header h1 span {
    color: #4f46e5;
}

.app-header p {
    color: #475569;
    font-size: 1.15rem;
    margin-top: 8px;
    font-weight: 500;
}

/* Chat Input Styling */
div[data-testid="stChatInputContainer"] {
    padding-bottom: 2rem !important;
}
div[data-testid="stChatInput"] {
    background-color: #ffffff !important;
    border: 1px solid #cbd5e1 !important;
    border-radius: 12px !important;
    box-shadow: 0 4px 6px -1px rgba(0,0,0,0.05) !important;
}
div[data-testid="stChatInput"] textarea {
    color: #f9fafc !important;
    background-color: transparent !important;
    font-weight: 500 !important;
}
div[data-testid="stChatInput"] button {
    color: #4f46e5 !important; 
}

/* Buttons Styling */
.stButton > button {
    background-color: #4f46e5 !important;
    color: white !important;
    border: none !important;
    border-radius: 12px !important;
    padding: 0.6rem 1.5rem !important;
    font-weight: 600 !important;
    font-size: 1.1rem !important;
    transition: all 0.2s ease !important;
    box-shadow: 0 4px 6px -1px rgba(79, 70, 229, 0.2) !important;
    width: 100%;
}
.stButton > button:hover {
    background-color: #4338ca !important;
    transform: translateY(-1px) !important;
    box-shadow: 0 6px 8px -1px rgba(79, 70, 229, 0.3) !important;
}

/* Selectbox Styling */
.stSelectbox > div > div {
    background: #ffffff !important;
    color: #1e293b !important;
    border: 1px solid #cbd5e1 !important;
    border-radius: 10px;
}
.stSelectbox label {
    color: #040507 !important;
    font-weight: 600 !important;
}

/* =========================================
   CHAT BUBBLE OVERRIDES FOR SEPARATION 
   ========================================= */

/* Assistant Chat Bubble (Left) */
div[data-testid="stChatMessage"]:has(.assistant-msg-marker) {
    background: #ffffff;
    border: 1px solid #e2e8f0;
    border-radius: 16px 16px 16px 4px;
    padding: 15px 20px;
    margin-bottom: 20px;
    width: fit-content;
    max-width: 80%;
    margin-right: auto;
    box-shadow: 0 2px 4px rgba(0,0,0,0.02);
}
div[data-testid="stChatMessage"]:has(.assistant-msg-marker) .stMarkdown p {
    color: #040507;
    font-weight: 500;
}

/* User Chat Bubble (Right) */
div[data-testid="stChatMessage"]:has(.user-msg-marker) {
    background: #4f46e5;
    border: none;
    border-radius: 16px 16px 4px 16px;
    padding: 15px 20px;
    margin-bottom: 20px;
    width: fit-content;
    max-width: 80%;
    margin-left: auto;
    box-shadow: 0 2px 4px rgba(79, 70, 229, 0.2);
    flex-direction: row-reverse;
}
div[data-testid="stChatMessage"]:has(.user-msg-marker) .stMarkdown {
    text-align: right;
}
div[data-testid="stChatMessage"]:has(.user-msg-marker) .stMarkdown p {
    color: #040507;
    font-weight: 500;
}
</style>
""", unsafe_allow_html=True)


st.markdown("""
<div class="app-header">
    <h1>✨ <span>AI</span> Multi-Language Voice Assistant</h1>
    <p>Seamless intelligent conversations across languages.</p>
</div>
""", unsafe_allow_html=True)

# =========================
# STATE INITIALIZATION
# =========================
if "messages" not in st.session_state:
    st.session_state.messages = []

if "system_status" not in st.session_state:
    st.session_state.system_status = "idle"

# =========================
# CONTROLS
# =========================
col1, col2, col3 = st.columns([1, 2, 1])

with col2:
    lang_map = {"English": "en", "Telugu": "te", "Hindi": "hi"}
    lang_name = st.selectbox("🌐 Select Translation Language", list(lang_map.keys()), index=0)
    lang = lang_map[lang_name]

# Start Listening Button
st.markdown("<br>", unsafe_allow_html=True)

btn_col1, btn_col2, btn_col3 = st.columns([1, 2, 1])

with btn_col2:
    audio = mic_recorder(
        start_prompt="🎤 Tap to Speak",
        stop_prompt="⏹ Stop Recording",
        just_once=True,
        key="main_mic"
    )

if audio:
    text = listen(audio["bytes"])

    if text and text.lower() != "error":
        st.session_state.messages.append({
            "role": "user",
            "content": text
        })
        st.session_state.system_status = "thinking"
        st.rerun()

    else:
        st.session_state.messages.append({
            "role": "assistant",
            "content": "Sorry, I missed that. Could you please try again?"
        })
        st.rerun()
st.markdown("<br>", unsafe_allow_html=True)


for msg in st.session_state.messages:
    with st.chat_message(msg["role"], avatar="🙎‍♂️" if msg["role"] == "user" else "🤖"):
        st.markdown(f'<div class="{msg["role"]}-msg-marker"></div>', unsafe_allow_html=True)
        st.write(msg["content"])


if user_input := st.chat_input("Or type your message here..."):
    st.session_state.messages.append({"role": "user", "content": user_input})
    st.session_state.system_status = "thinking"
    st.rerun()


if st.session_state.system_status == "listening":
    with st.spinner("🎙️ Listening carefully..."):
        text = listen()

    if text is None:
        st.session_state.system_status = "idle"

    elif text and text.lower() != "error":
        st.session_state.messages.append({
            "role": "user",
            "content": text
        })
        st.session_state.system_status = "thinking"

    else:
        st.session_state.messages.append({
            "role": "assistant",
            "content": "Sorry, I missed that. Could you please try again?"
        })
        st.session_state.system_status = "idle"

    st.rerun()

elif st.session_state.system_status == "thinking":
    user_msg = st.session_state.messages[-1]["content"]

    with st.spinner("✨ Processing..."):
        try:
            # 1. Translate User Input to English (if needed)
            if lang != "en":
                english_query = translate_text(user_msg, "en")
            else:
                english_query = user_msg

            # 1.5. Check for local commands (play, search, open apps)
            command_response = handle_commands(english_query)

            if command_response:
                if command_response == "EXIT":
                    ai_reply = "Goodbye! You can close the tab now."
                else:
                    ai_reply = command_response
            else:
                # 2. Get AI Response
                ai_reply = get_ai_response(english_query)

            # 3. Translate AI Response back to target Language
            if lang != "en":
                final_reply = translate_text(ai_reply, lang)
            else:
                final_reply = ai_reply

        except Exception as e:
            final_reply = "I apologize, but I encountered an error while processing your request."

    st.session_state.messages.append({"role": "assistant", "content": final_reply})
    st.session_state.system_status = "speaking"
    st.rerun()

elif st.session_state.system_status == "speaking":
    reply_to_speak = st.session_state.messages[-1]["content"]

    # Needs to be reset safely before speaking
    st.session_state.system_status = "idle"

    # Speak out the text synchronously
    with st.spinner("🔊 Speaking..."):


        audio_file = speak(reply_to_speak, lang)
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
