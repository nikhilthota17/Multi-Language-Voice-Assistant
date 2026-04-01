import speech_recognition as sr
import os

def listen():
    try:
        # Cloud check
        if os.environ.get("STREAMLIT_SERVER_RUNNING"):
            return "VOICE_NOT_SUPPORTED"

        recognizer = sr.Recognizer()

        with sr.Microphone() as source:
            print("🎤 Adjusting noise...")
            recognizer.adjust_for_ambient_noise(source, duration=1)

            print("🎤 Listening...")
            audio = recognizer.listen(source, timeout=5)

        print("🔄 Recognizing...")
        text = recognizer.recognize_google(audio)

        print("✅ You said:", text)
        return text

    except sr.WaitTimeoutError:
        print("⏱ Timeout - no speech")
        return "Error"

    except sr.UnknownValueError:
        print("❌ Could not understand audio")
        return "Error"

    except sr.RequestError:
        print("🌐 API error")
        return "Error"

    except Exception as e:
        print("🔥 Error:", e)
        return "Error"