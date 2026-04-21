import streamlit as st
import streamlit.components.v1 as components
import base64
import os

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
if "messages"          not in st.session_state: st.session_state.messages          = []
if "status"            not in st.session_state: st.session_state.status            = "ready"
if "_last_mic_seen"    not in st.session_state: st.session_state._last_mic_seen    = ""

# ---------------------------------------------------
# CSS
# ---------------------------------------------------
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;500;600;700&family=Syne:wght@700;800&display=swap');

html, body, [class*="css"] {
    font-family: 'Plus Jakarta Sans', sans-serif;
    color: #1a1a2e;
}
.stApp { background: #f4f6fb; }
#MainMenu, footer, header { visibility: hidden; }
.block-container { max-width: 760px; padding-top: 2rem; padding-bottom: 3rem; }

.va-header { text-align: center; margin-bottom: 1.6rem; }
.va-header h1 {
    font-family: 'Syne', sans-serif; font-size: 2.1rem; font-weight: 800;
    color: #1a1a2e; letter-spacing: -0.5px; margin: 0 0 4px;
}
.va-header p { font-size: 0.9rem; color: #6b7280; margin: 0; }

.va-status-wrap { display: flex; justify-content: center; margin-bottom: 1.2rem; }
.va-status {
    display: inline-flex; align-items: center; gap: 7px;
    padding: 5px 16px; border-radius: 99px; font-size: 0.78rem; font-weight: 600;
}
.va-status.ready     { background:#ecfdf5; color:#065f46; border:1px solid #a7f3d0; }
.va-status.working   { background:#eff6ff; color:#1d4ed8; border:1px solid #bfdbfe; }
.va-status.speaking  { background:#f5f3ff; color:#5b21b6; border:1px solid #ddd6fe; }
.va-status.listening { background:#fefce8; color:#854d0e; border:1px solid #fde68a; }
.va-status.error     { background:#fef2f2; color:#991b1b; border:1px solid #fecaca; }
.va-dot {
    width:7px; height:7px; border-radius:50%; background:currentColor;
    animation: blink 1.6s infinite;
}
@keyframes blink { 0%,100%{opacity:1} 50%{opacity:0.3} }

.va-chat {
    background:#fff; border:1px solid #e5e7eb; border-radius:20px;
    padding:18px 16px; min-height:360px; max-height:430px;
    overflow-y:auto; margin-bottom:1rem; display:flex; flex-direction:column;
    gap:12px; box-shadow:0 1px 6px rgba(0,0,0,0.05);
    scrollbar-width:thin; scrollbar-color:#e5e7eb transparent;
}
.va-chat::-webkit-scrollbar{width:4px}
.va-chat::-webkit-scrollbar-thumb{background:#e5e7eb;border-radius:4px}
.va-chat.empty { align-items:center; justify-content:center; }
.va-empty-state { text-align:center; }
.va-empty-icon  { font-size:2.4rem; display:block; margin-bottom:8px; }
.va-empty-state p { font-size:0.88rem; color:#9ca3af; margin:0; }

.msg-row { display:flex; gap:9px; align-items:flex-start; }
.msg-row.user { flex-direction:row-reverse; }
.msg-avatar {
    width:30px; height:30px; border-radius:50%; font-size:0.66rem; font-weight:700;
    display:flex; align-items:center; justify-content:center; flex-shrink:0; margin-top:2px;
}
.user-avatar { background:#ede9fe; color:#5b21b6; }
.bot-avatar  { background:#ecfdf5; color:#065f46; }
.bubble {
    max-width:72%; padding:11px 15px; font-size:0.9rem;
    line-height:1.6; word-break:break-word;
}
.user-bubble { background:#4f46e5; color:#fff; border-radius:18px 18px 4px 18px; }
.bot-bubble  { background:#f3f4f6; color:#111827; border-radius:18px 18px 18px 4px; border:1px solid #e5e7eb; }

.va-divider { border:none; border-top:1px solid #e9ecf0; margin:0.8rem 0; }
.input-label { font-size:0.74rem; font-weight:600; color:#9ca3af; text-transform:uppercase; letter-spacing:0.6px; margin-bottom:5px; }

/* hide the mic hidden input completely */
div[data-testid="stTextInput"]:has(input[placeholder="__mic_receiver__"]) {
    display: none !important;
    height: 0 !important;
    overflow: hidden !important;
}

.stSelectbox [data-baseweb="select"]>div { background:#f9fafb !important; border:1px solid #d1d5db !important; border-radius:10px !important; }
.stSelectbox [data-baseweb="select"] span { color:#111827 !important; font-weight:500 !important; }

textarea {
    background:#f9fafb !important; border:1px solid #d1d5db !important;
    border-radius:14px !important; color:#111827 !important;
    font-family:'Plus Jakarta Sans',sans-serif !important; font-size:0.9rem !important;
    resize:none !important; height:108px !important; min-height:108px !important;
    max-height:108px !important; padding:12px 14px !important;
}
textarea::placeholder { color:#9ca3af !important; }
textarea:focus { border-color:#818cf8 !important; box-shadow:0 0 0 3px rgba(99,102,241,0.12) !important; outline:none !important; }

.send-btn-wrap { margin-top:6px !important; }
.send-btn-wrap .stButton>button {
    background:#4f46e5 !important; color:#fff !important; border:none !important;
    border-radius:12px !important; font-weight:600 !important; height:44px !important; width:100% !important;
}
.send-btn-wrap .stButton>button:hover { background:#4338ca !important; }

.clear-btn-wrap .stButton>button {
    background:#fff1f2 !important; color:#be123c !important; border:1px solid #fda4af !important;
    border-radius:10px !important; font-size:0.82rem !important; font-weight:600 !important; height:38px !important;
}
.clear-btn-wrap .stButton>button:hover { background:#ffe4e6 !important; }

[data-testid="column"] { padding:0 5px !important; }
</style>
""", unsafe_allow_html=True)


# ---------------------------------------------------
# PROCESS MESSAGE
# ---------------------------------------------------
def process_message(user_text, lang):
    try:
        st.session_state.status = "working"
        st.session_state.messages.append(("user", user_text, None))

        query       = translate_text(user_text, "en") if lang != "en" else user_text
        command     = handle_commands(query)
        reply       = command if command else get_ai_response(query)
        final_reply = translate_text(reply, lang) if lang != "en" else reply

        st.session_state.status = "speaking"

        audio_bytes = None
        audio_file  = speak(final_reply, lang)
        if audio_file and os.path.exists(audio_file):
            try:
                with open(audio_file, "rb") as f:
                    audio_bytes = f.read()
                os.remove(audio_file)
            except Exception as e:
                print(f"[Audio] {e}")

        st.session_state.messages.append(("bot", final_reply, audio_bytes))
        st.session_state.status = "ready"

    except Exception as e:
        st.session_state.status = "error"
        st.error(f"Error: {e}")


# ---------------------------------------------------
# MIC COMPONENT
# Uses Web Speech API. Transcript is injected into a
# hidden Streamlit text_input via the React native setter —
# this is the only reliable way to push data from an iframe
# back to Streamlit without a full component declaration.
# ---------------------------------------------------
def mic_component(lang_code: str):
    lang_bcp = {"en": "en-US", "hi": "hi-IN", "te": "te-IN"}.get(lang_code, "en-US")

    html = f"""
    <div style="width:100%;height:108px;display:flex;align-items:center;">
      <button id="mic-btn" onclick="toggleMic()" style="
          width:100%; height:108px;
          background:#f0fdf4; color:#065f46;
          border:1.5px solid #6ee7b7; border-radius:14px;
          font-family:'Plus Jakarta Sans',sans-serif;
          font-size:0.92rem; font-weight:700; cursor:pointer;
          display:flex; flex-direction:column; align-items:center;
          justify-content:center; gap:8px; transition:all 0.15s;
      ">
        <span id="mic-icon" style="font-size:1.7rem;">🎤</span>
        <span id="mic-label">Speak</span>
      </button>
    </div>

    <script>
    var recognition = null;
    var isListening  = false;

    function toggleMic() {{
        isListening ? stopMic() : startMic();
    }}

    function startMic() {{
        var SR = window.SpeechRecognition || window.webkitSpeechRecognition;
        if (!SR) {{
            setBtn('#fef2f2','#991b1b','#fecaca','❌','Not supported — use Chrome/Edge');
            return;
        }}

        recognition              = new SR();
        recognition.lang         = '{lang_bcp}';
        recognition.interimResults = true;
        recognition.continuous   = false;

        isListening = true;
        setBtn('#fefce8','#854d0e','#fde68a','🔴','Listening… tap to stop');

        recognition.onresult = function(e) {{
            var interim = '', final_t = '';
            for (var i = e.resultIndex; i < e.results.length; i++) {{
                var t = e.results[i][0].transcript;
                if (e.results[i].isFinal) final_t += t;
                else interim += t;
            }}
            if (interim)
                document.getElementById('mic-label').innerText = '"' + interim.substring(0,40) + '…"';
            if (final_t.trim()) {{
                setBtn('#ecfdf5','#065f46','#6ee7b7','✅','"' + final_t.trim().substring(0,40) + '"');
                pushToStreamlit(final_t.trim());
            }}
        }};

        recognition.onerror = function(e) {{
            isListening = false;
            var msg = {{
                'not-allowed' : 'Mic denied — allow mic in browser settings',
                'no-speech'   : 'No speech detected — try again',
                'network'     : 'Network error'
            }}[e.error] || ('Error: ' + e.error);
            setBtn('#fef2f2','#991b1b','#fecaca','❌', msg);
            setTimeout(resetBtn, 3000);
        }};

        recognition.onend = function() {{
            isListening = false;
            setTimeout(resetBtn, 1500);
        }};

        recognition.start();
    }}

    function stopMic() {{
        if (recognition) recognition.stop();
        isListening = false;
    }}

    function resetBtn() {{
        setBtn('#f0fdf4','#065f46','#6ee7b7','🎤','Speak');
    }}

    function setBtn(bg, color, border, icon, lbl) {{
        var b = document.getElementById('mic-btn');
        b.style.background  = bg;
        b.style.color       = color;
        b.style.borderColor = border;
        document.getElementById('mic-icon').innerText  = icon;
        document.getElementById('mic-label').innerText = lbl;
    }}

    // ── KEY FIX ──────────────────────────────────────────────
    // components.html runs in a same-origin srcdoc iframe.
    // We reach into window.parent.document, find the hidden
    // Streamlit text input by its unique placeholder, set its
    // value via React's native setter, then dispatch an 'input'
    // event so React / Streamlit picks up the change and reruns.
    // ─────────────────────────────────────────────────────────
    function pushToStreamlit(text) {{
        try {{
            var parentDoc = window.parent.document;
            var input = parentDoc.querySelector('input[placeholder="__mic_receiver__"]');

            if (!input) {{
                console.warn('[Mic] Hidden input not found in parent page.');
                return;
            }}

            // Use React's internal setter — plain .value= won't fire onChange
            var nativeSetter = Object.getOwnPropertyDescriptor(
                window.parent.HTMLInputElement.prototype, 'value'
            ).set;
            nativeSetter.call(input, text);

            // Dispatch both 'input' and 'change' so React sees it
            input.dispatchEvent(new Event('input',  {{ bubbles: true }}));
            input.dispatchEvent(new Event('change', {{ bubbles: true }}));

            console.log('[Mic] Pushed to Streamlit:', text);
        }} catch(err) {{
            console.error('[Mic] pushToStreamlit error:', err);
        }}
    }}
    </script>
    """

    components.html(html, height=120, scrolling=False)


# ---------------------------------------------------
# UI
# ---------------------------------------------------

st.markdown("""
<div class="va-header">
    <h1>🤖 AI Voice Assistant</h1>
    <p>Multi-language &nbsp;·&nbsp; Voice &amp; Text &nbsp;·&nbsp; Smart Commands</p>
</div>
""", unsafe_allow_html=True)

# Status
status = st.session_state.status
labels = {
    "ready":     ("ready",    "Ready"),
    "working":   ("working",  "Processing…"),
    "speaking":  ("speaking", "Speaking…"),
    "listening": ("listening","Listening…"),
    "error":     ("error",    "Error"),
}
cls, lbl = labels.get(status, ("ready","Ready"))
st.markdown(f"""
<div class="va-status-wrap">
    <div class="va-status {cls}"><span class="va-dot"></span>{lbl}</div>
</div>
""", unsafe_allow_html=True)

# Language + Clear
lc, gc, cc = st.columns([3.5, 0.2, 1.3])
with lc:
    lang_map  = {"English":"en","Hindi":"hi","Telugu":"te"}
    lang_name = st.selectbox("Language", list(lang_map.keys()), label_visibility="collapsed")
    lang      = lang_map[lang_name]
with cc:
    st.markdown('<div class="clear-btn-wrap">', unsafe_allow_html=True)
    if st.button("🗑 Clear Chat", use_container_width=True):
        st.session_state.messages       = []
        st.session_state._last_mic_seen = ""
        st.rerun()
    st.markdown("</div>", unsafe_allow_html=True)

# Chat window
msgs = st.session_state.messages
if msgs:
    rows        = ""
    latest_audio = None
    for role, msg, audio_bytes in msgs:
        if role == "user":
            rows += f'<div class="msg-row user"><div class="msg-avatar user-avatar">You</div><div class="bubble user-bubble">{msg}</div></div>'
        else:
            rows += f'<div class="msg-row bot"><div class="msg-avatar bot-avatar">AI</div><div class="bubble bot-bubble">{msg}</div></div>'
            if audio_bytes:
                latest_audio = audio_bytes

    st.markdown(f'<div class="va-chat">{rows}</div>', unsafe_allow_html=True)

    # Invisible autoplay for the latest bot response only
    if latest_audio:
        b64 = base64.b64encode(latest_audio).decode()
        st.markdown(
            f'<audio autoplay style="display:none"><source src="data:audio/mp3;base64,{b64}" type="audio/mp3"></audio>',
            unsafe_allow_html=True
        )
else:
    st.markdown("""
    <div class="va-chat empty">
        <div class="va-empty-state">
            <span class="va-empty-icon">💬</span>
            <p>Speak or type something to begin</p>
        </div>
    </div>""", unsafe_allow_html=True)

st.markdown('<hr class="va-divider">', unsafe_allow_html=True)

# ── Hidden input — receives transcript from mic JS
# The placeholder "__mic_receiver__" is what the JS searches for
mic_val = st.text_input(
    "mic_receiver",
    value="",
    placeholder="__mic_receiver__",
    key="_mic_receiver",
    label_visibility="collapsed"
)

# Input row
mic_col, right_col = st.columns([1, 3], gap="small")

with mic_col:
    st.markdown('<div class="input-label">🎤 Voice</div>', unsafe_allow_html=True)
    mic_component(lang)

with right_col:
    st.markdown('<div class="input-label">✏️ Text</div>', unsafe_allow_html=True)
    typed = st.text_area(
        "Message", value="",
        placeholder="Type your message here…",
        height=108, label_visibility="collapsed", key="text_input"
    )
    st.markdown('<div class="send-btn-wrap">', unsafe_allow_html=True)
    send = st.button("Send  ➤", use_container_width=True)
    st.markdown("</div>", unsafe_allow_html=True)

# ---------------------------------------------------
# HANDLERS
# ---------------------------------------------------

# Mic — fires when the hidden input gets a new value from JS
if mic_val and mic_val.strip() and mic_val.strip() != st.session_state._last_mic_seen:
    user_query = mic_val.strip()
    st.session_state._last_mic_seen = user_query
    
    # Optional: Update the visible text area so the user sees their speech
    st.session_state["text_input"] = user_query
    
    # Process the message immediately
    process_message(user_query, lang)
    st.rerun()

# 2. Catch Typed Input
if send and typed.strip():
    process_message(typed.strip(), lang)
    # Clear the text area after sending
    st.session_state["text_input"] = "" 
    st.rerun()