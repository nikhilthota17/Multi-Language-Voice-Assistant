
from gtts import gTTS
import playsound
import os

def speak(text, lang="en"):
    try:
        if not text:
            return

        print("Speaking:", text)

        tts = gTTS(text=text, lang=lang)
        filename = "voice.mp3"
        tts.save(filename)

        playsound.playsound(filename)
        os.remove(filename)

    except Exception as e:
        print("TTS Error:", e)