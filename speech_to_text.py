import speech_recognition as sr
from streamlit_mic_recorder import mic_recorder
import tempfile

def listen():
    audio = mic_recorder(
        start_prompt="🎤 Start Recording",
        stop_prompt="⏹ Stop Recording",
        just_once=True,
        key="recorder"
    )

    if audio:
        with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as f:
            f.write(audio["bytes"])
            filename = f.name

        recognizer = sr.Recognizer()

        with sr.AudioFile(filename) as source:
            audio_data = recognizer.record(source)

        try:
            text = recognizer.recognize_google(audio_data)
            return text
        except:
            return "Error"

    return None
