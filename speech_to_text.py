import speech_recognition as sr
import os

def listen():
    try:
        # 🚨 Detect cloud environment
        if os.environ.get("STREAMLIT_SERVER_RUNNING"):
            return "VOICE_NOT_SUPPORTED"

        recognizer = sr.Recognizer()

        with sr.Microphone() as source:
            print("Listening...")
            audio = recognizer.listen(source)

        return recognizer.recognize_google(audio)

    except Exception as e:
        print("Error:", e)
        return "Error"