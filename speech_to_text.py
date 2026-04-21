import speech_recognition as sr
import streamlit as st

def listen(lang="en"):
    """
    Utility function for Speech-to-Text.
    Note: In browser environments (like Codespaces), the Web Speech API 
    in app.py handles the primary recording. This function serves as 
    a backend processor if needed.
    """
    recognizer = sr.Recognizer()
    
    # Language mapping for Google Speech Recognition
    lang_map = {
        "en": "en-IN",
        "hi": "hi-IN",
        "te": "te-IN"
    }
    recog_lang = lang_map.get(lang, "en-IN")

    try:
        with sr.Microphone() as source:
            # Adjust for ambient noise for better accuracy
            recognizer.adjust_for_ambient_noise(source, duration=0.5)
            
            # Listen for the user's voice
            audio = recognizer.listen(source, timeout=5, phrase_time_limit=10)

        # Convert Speech to Text using Google's API
        text = recognizer.recognize_google(audio, language=recog_lang)
        return text.strip()

    except sr.WaitTimeoutError:
        return ""
    except sr.UnknownValueError:
        # Speech was unintelligible
        return ""
    except sr.RequestError as e:
        print(f"Could not request results from Google Service; {e}")
        return ""
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        return ""

def process_transcript(text):
    """
    Cleans or formats the transcript before sending to AI
    """
    if not text:
        return ""
    return text.strip().capitalize()