import speech_recognition as sr
import tempfile

def listen(audio_bytes):
    if not audio_bytes:
        return None

    with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as f:
        f.write(audio_bytes)
        filename = f.name

    recognizer = sr.Recognizer()

    with sr.AudioFile(filename) as source:
        audio_data = recognizer.record(source)

    try:
        text = recognizer.recognize_google(audio_data)
        return text
    except:
        return "Error"
