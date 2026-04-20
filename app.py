import streamlit as st
import base64
import os
from streamlit_mic_recorder import mic_recorder

from speech_to_text import listen
from translator import translate_text
from ai_response import get_ai_response
from text_to_speech import speak
from main import handle_commands

# ---------------------------------------------------
# PAGE CONFIG
# ---------------------------------------------------
st.set_page_config(
    page_title="AI Voice Assistant",
    page_icon="🤖",
    layout="centered"
)

# ---------------------------------------------------
# SESSION STATE
# ---------------------------------------------------
if "messages" not in st.session_state:
    st.session_state.messages = []

if "status" not in st.session_state:
    st.session_state.status = "ready"

# Tracks last processed audio so same recording isn't processed twice on rerun
if "last_audio_id" not in st.session_state:
    st.session_state.last_audio_id = None

# Holds the transcribed text from mic so user can see/edit before sending
if "mic_transcript" not in st.session_state:
    st.session_state.mic_transcript = ""

# Holds any mic error message
if "mic_error" not in st.session_state:
    st.session_state.mic_error = ""

# ---------------------------------------------------
# CSS — Light Theme
# ---------------------------------------------------
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;500;600;700&family=Syne:wght@700;800&display=swap');

html, body, [class*="css"] {
    font-family: 'Plus Jakarta Sans', sans-serif;
    color: #1a1a2e;
}

.stApp {
    background: #f4f6fb;
    min-height: 100vh;
}

#MainMenu, footer, header { visibility: hidden; }

.block-container {
    max-width: 760px;
    padding-top: 2.2rem;
    padding-bottom: 3rem;
}

/* ── HEADER ── */
.va-header {
    text-align: center;
    margin-bottom: 1.8rem;
}
.va-header h1 {
    font-family: 'Syne', sans-serif;
    font-size: 2.2rem;
    font-weight: 800;
    color: #1a1a2e;
    letter-spacing: -0.5px;
    margin: 0 0 5px;
}
.va-header p {
    font-size: 0.92rem;
    color: #6b7280;
    font-weight: 400;
    margin: 0;
}

/* ── STATUS PILL ── */
.va-status-wrap {
    display: flex;
    justify-content: center;
    margin-bottom: 1.4rem;
}
.va-status {
    display: inline-flex;
    align-items: center;
    gap: 7px;
    padding: 5px 16px;
    border-radius: 99px;
    font-size: 0.78rem;
    font-weight: 600;
    letter-spacing: 0.2px;
}
.va-status.ready      { background: #ecfdf5; color: #065f46; border: 1px solid #a7f3d0; }
.va-status.working    { background: #eff6ff; color: #1d4ed8; border: 1px solid #bfdbfe; }
.va-status.speaking   { background: #f5f3ff; color: #5b21b6; border: 1px solid #ddd6fe; }
.va-status.listening  { background: #fefce8; color: #854d0e; border: 1px solid #fde68a; }
.va-status.error      { background: #fef2f2; color: #991b1b; border: 1px solid #fecaca; }
.va-dot {
    width: 7px; height: 7px;
    border-radius: 50%;
    background: currentColor;
    animation: blink 1.6s infinite;
}
@keyframes blink {
    0%, 100% { opacity: 1; }
    50%       { opacity: 0.3; }
}

/* ── CHAT WINDOW ── */
.va-chat {
    background: #ffffff;
    border: 1px solid #e5e7eb;
    border-radius: 20px;
    padding: 18px 16px;
    min-height: 360px;
    max-height: 430px;
    overflow-y: auto;
    margin-bottom: 1rem;
    display: flex;
    flex-direction: column;
    gap: 12px;
    box-shadow: 0 1px 6px rgba(0,0,0,0.05);
    scrollbar-width: thin;
    scrollbar-color: #e5e7eb transparent;
}
.va-chat::-webkit-scrollbar { width: 4px; }
.va-chat::-webkit-scrollbar-thumb { background: #e5e7eb; border-radius: 4px; }

.va-chat.empty {
    align-items: center;
    justify-content: center;
}
.va-empty-state { text-align: center; }
.va-empty-icon  { font-size: 2.6rem; display: block; margin-bottom: 10px; }
.va-empty-state p {
    font-size: 0.88rem;
    color: #9ca3af;
    margin: 0;
}

/* ── MESSAGE ROWS ── */
.msg-row {
    display: flex;
    gap: 9px;
    align-items: flex-end;
}
.msg-row.user { flex-direction: row-reverse; }

.msg-avatar {
    width: 30px; height: 30px;
    border-radius: 50%;
    font-size: 0.68rem;
    font-weight: 700;
    display: flex; align-items: center; justify-content: center;
    flex-shrink: 0;
    letter-spacing: 0.3px;
}
.user-avatar { background: #ede9fe; color: #5b21b6; }
.bot-avatar  { background: #ecfdf5; color: #065f46; }

.bubble {
    max-width: 70%;
    padding: 11px 15px;
    font-size: 0.9rem;
    line-height: 1.6;
    font-weight: 400;
    word-break: break-word;
    font-family: 'Plus Jakarta Sans', sans-serif;
}
.user-bubble {
    background: #4f46e5;
    color: #ffffff;
    border-radius: 18px 18px 4px 18px;
}
.bot-bubble {
    background: #f3f4f6;
    color: #111827;
    border-radius: 18px 18px 18px 4px;
    border: 1px solid #e5e7eb;
}

/* ── TRANSCRIPT PREVIEW BANNER ── */
.transcript-box {
    background: #fefce8;
    border: 1px solid #fde68a;
    border-radius: 12px;
    padding: 10px 14px;
    margin-bottom: 10px;
    font-size: 0.85rem;
    color: #713f12;
    display: flex;
    align-items: flex-start;
    gap: 8px;
}
.transcript-box strong {
    color: #854d0e;
    white-space: nowrap;
}

/* ── MIC ERROR BANNER ── */
.mic-error-box {
    background: #fef2f2;
    border: 1px solid #fecaca;
    border-radius: 12px;
    padding: 9px 14px;
    margin-bottom: 10px;
    font-size: 0.83rem;
    color: #991b1b;
}

/* ── DIVIDER ── */
.va-divider {
    border: none;
    border-top: 1px solid #e9ecf0;
    margin: 0.8rem 0;
}

/* ── INPUT SECTION LABEL ── */
.input-label {
    font-size: 0.78rem;
    font-weight: 600;
    color: #9ca3af;
    text-transform: uppercase;
    letter-spacing: 0.6px;
    margin-bottom: 6px;
}

/* ── STREAMLIT OVERRIDES ── */

/* Selectbox */
.stSelectbox label { color: #374151 !important; font-size: 0.85rem !important; font-weight: 500 !important; }
.stSelectbox [data-baseweb="select"] > div {
    background: #f9fafb !important;
    border: 1px solid #d1d5db !important;
    border-radius: 10px !important;
}
.stSelectbox [data-baseweb="select"] span { color: #111827 !important; font-weight: 500 !important; }
.stSelectbox svg { color: #6b7280 !important; }

/* Textarea */
textarea {
    background: #f9fafb !important;
    border: 1px solid #d1d5db !important;
    border-radius: 14px !important;
    color: #111827 !important;
    font-family: 'Plus Jakarta Sans', sans-serif !important;
    font-size: 0.9rem !important;
    font-weight: 400 !important;
    resize: none !important;
    height: 108px !important;
    min-height: 108px !important;
    max-height: 108px !important;
    padding: 12px 14px !important;
    line-height: 1.6 !important;
}
textarea::placeholder { color: #9ca3af !important; }
textarea:focus {
    border-color: #818cf8 !important;
    box-shadow: 0 0 0 3px rgba(99,102,241,0.12) !important;
    outline: none !important;
}

/* Send button */
.send-btn-wrap { margin-top: 6px !important; }
.send-btn-wrap .stButton > button {
    background: #4f46e5 !important;
    color: #ffffff !important;
    border: none !important;
    border-radius: 12px !important;
    font-weight: 600 !important;
    font-size: 0.92rem !important;
    height: 44px !important;
    width: 100% !important;
    letter-spacing: 0.2px;
}
.send-btn-wrap .stButton > button:hover { background: #4338ca !important; }

/* Clear button */
.clear-btn-wrap .stButton > button {
    background: #fff1f2 !important;
    color: #be123c !important;
    border: 1px solid #fda4af !important;
    border-radius: 10px !important;
    font-size: 0.82rem !important;
    font-weight: 600 !important;
    height: 38px !important;
}
.clear-btn-wrap .stButton > button:hover { background: #ffe4e6 !important; }

/* Mic recorder — full height block matching textarea */
div[data-testid="stMicRecorder"] {
    display: flex !important;
    flex-direction: column !important;
    height: 100% !important;
}
div[data-testid="stMicRecorder"] button {
    background: #f0fdf4 !important;
    color: #065f46 !important;
    border: 1.5px solid #6ee7b7 !important;
    border-radius: 14px !important;
    font-weight: 700 !important;
    font-size: 0.88rem !important;
    width: 100% !important;
    height: 108px !important;
    display: flex !important;
    flex-direction: column !important;
    align-items: center !important;
    justify-content: center !important;
    gap: 8px !important;
    line-height: 1.5 !important;
    padding: 10px !important;
    transition: all 0.15s ease !important;
}
div[data-testid="stMicRecorder"] button:hover {
    background: #dcfce7 !important;
    border-color: #34d399 !important;
}

/* Column gaps */
[data-testid="column"] { padding: 0 5px !important; }

/* Error/alert */
.stAlert p { color: #991b1b !important; }
</style>
""", unsafe_allow_html=True)


# ---------------------------------------------------
# PROCESS MESSAGE
# ---------------------------------------------------
def process_message(user_text, lang):
    try:
        st.session_state.status = "working"
        st.session_state.messages.append(("user", user_text))

        query = translate_text(user_text, "en") if lang != "en" else user_text

        command = handle_commands(query)
        reply = command if command else get_ai_response(query)

        final_reply = translate_text(reply, lang) if lang != "en" else reply
        st.session_state.messages.append(("bot", final_reply))

        st.session_state.status = "speaking"

        audio_file = speak(final_reply, lang)
        if audio_file and os.path.exists(audio_file):
            with open(audio_file, "rb") as f:
                b64 = base64.b64encode(f.read()).decode()
            st.markdown(
                f'<audio autoplay><source src="data:audio/mp3;base64,{b64}" type="audio/mp3"></audio>',
                unsafe_allow_html=True
            )
            try:
                os.remove(audio_file)
            except Exception:
                pass

        st.session_state.status = "ready"

    except Exception as e:
        st.session_state.status = "error"
        st.error(f"Something went wrong: {e}")


# ---------------------------------------------------
# UI RENDERING
# ---------------------------------------------------

# ── Header
st.markdown("""
<div class="va-header">
    <h1>🤖 AI Voice Assistant</h1>
    <p>Multi-language &nbsp;·&nbsp; Voice &amp; Text &nbsp;·&nbsp; Smart Commands</p>
</div>
""", unsafe_allow_html=True)

# ── Status pill
status = st.session_state.status
status_labels = {
    "ready":     ("ready",     "Ready"),
    "working":   ("working",   "Processing…"),
    "speaking":  ("speaking",  "Speaking…"),
    "listening": ("listening", "Listening…"),
    "error":     ("error",     "Error"),
}
cls, label = status_labels.get(status, ("ready", "Ready"))
st.markdown(f"""
<div class="va-status-wrap">
    <div class="va-status {cls}">
        <span class="va-dot"></span>{label}
    </div>
</div>
""", unsafe_allow_html=True)

# ── Language selector + Clear
lang_col, gap_col, clear_col = st.columns([3.5, 0.2, 1.3])
with lang_col:
    lang_map = {"English": "en", "Hindi": "hi", "Telugu": "te"}
    lang_name = st.selectbox("Language", list(lang_map.keys()), label_visibility="collapsed")
    lang = lang_map[lang_name]
with clear_col:
    st.markdown('<div class="clear-btn-wrap">', unsafe_allow_html=True)
    if st.button("🗑 Clear Chat", use_container_width=True):
        st.session_state.messages = []
        st.session_state.mic_transcript = ""
        st.session_state.mic_error = ""
        st.rerun()
    st.markdown("</div>", unsafe_allow_html=True)

# ── Chat window
msgs = st.session_state.messages
if msgs:
    rows = ""
    for role, msg in msgs:
        if role == "user":
            rows += f"""
            <div class="msg-row user">
                <div class="msg-avatar user-avatar">You</div>
                <div class="bubble user-bubble">{msg}</div>
            </div>"""
        else:
            rows += f"""
            <div class="msg-row bot">
                <div class="msg-avatar bot-avatar">AI</div>
                <div class="bubble bot-bubble">{msg}</div>
            </div>"""
    st.markdown(f'<div class="va-chat">{rows}</div>', unsafe_allow_html=True)
else:
    st.markdown("""
    <div class="va-chat empty">
        <div class="va-empty-state">
            <span class="va-empty-icon">💬</span>
            <p>Speak or type something to begin your conversation</p>
        </div>
    </div>
    """, unsafe_allow_html=True)

# ── Divider
st.markdown('<hr class="va-divider">', unsafe_allow_html=True)

# ── Transcript preview (shown after mic recording is transcribed)
if st.session_state.mic_transcript:
    st.markdown(f"""
    <div class="transcript-box">
        <strong>🎤 Heard:</strong>
        <span>{st.session_state.mic_transcript}</span>
    </div>
    """, unsafe_allow_html=True)

# ── Mic error banner
if st.session_state.mic_error:
    st.markdown(f"""
    <div class="mic-error-box">
        ⚠️ {st.session_state.mic_error}
    </div>
    """, unsafe_allow_html=True)

# ── Input row: [Mic button] [Textarea + Send]
mic_col, right_col = st.columns([1, 3], gap="small")

with mic_col:
    st.markdown('<div class="input-label">🎤 Voice</div>', unsafe_allow_html=True)
    audio = mic_recorder(
        start_prompt="🎤  Speak",
        stop_prompt="⏹  Stop",
        just_once=True,        # fires once per recording — no double triggers
        use_container_width=True,
        key="mic"
    )

with right_col:
    st.markdown('<div class="input-label">✏️ Text</div>', unsafe_allow_html=True)
    typed = st.text_area(
        "Message",
        placeholder="Type your message here…",
        height=108,
        label_visibility="collapsed",
        key="text_input"
    )
    st.markdown('<div class="send-btn-wrap">', unsafe_allow_html=True)
    send = st.button("Send  ➤", use_container_width=True)
    st.markdown("</div>", unsafe_allow_html=True)


# ---------------------------------------------------
# HANDLERS
# ---------------------------------------------------

# ── Mic handler: deduplicate by audio id, transcribe, show preview, then send
if audio and "bytes" in audio and len(audio["bytes"]) > 0:
    # mic_recorder gives an incremental id each new recording
    audio_id = audio.get("id", None)

    if audio_id != st.session_state.last_audio_id:
        st.session_state.last_audio_id = audio_id
        st.session_state.mic_error = ""
        st.session_state.status = "listening"

        transcribed = listen(audio["bytes"])

        if transcribed and transcribed.strip().lower() != "error":
            st.session_state.mic_transcript = transcribed.strip()
            # Immediately process the transcribed voice input
            process_message(transcribed.strip(), lang)
            st.session_state.mic_transcript = ""   # clear preview after sending
        else:
            st.session_state.mic_error = (
                "Could not understand audio. Please speak clearly and try again."
            )
            st.session_state.status = "error"

        st.rerun()

# ── Text handler
if send and typed.strip():
    st.session_state.mic_transcript = ""
    st.session_state.mic_error = ""
    process_message(typed.strip(), lang)
    st.rerun()