from gtts import gTTS
import tempfile

def speak(text, lang="en"):
    try:
        tts = gTTS(text=text, lang=lang)

        with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as fp:
            tts.save(fp.name)
            return fp.name   # ✅ RETURN FILE (important)

    except Exception as e:
        print("TTS Error:", e)
        return None