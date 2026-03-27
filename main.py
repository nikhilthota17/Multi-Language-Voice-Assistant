import urllib
import webbrowser
import os
from re import search

from speech_to_text import listen
from translator import translate_text
from text_to_speech import speak
from ai_response import get_ai_response
import webbrowser
import os
import yt_dlp


# 🔹 Language Selection
def choose_language():
    while True:
        # Ask user via voice
        speak("Please say your language. English, Telugu, or Hindi.", "en")

        text = listen()

        if not text or text == "Error":
            continue

        text = text.lower()
        print("Language input:", text)

        # Detect language
        if "english" in text:
            speak("English selected", "en")
            return "en"

        elif "telugu" in text:
            speak("తెలుగు ఎంపిక చేయబడింది", "te")
            return "te"

        elif "hindi" in text:
            speak("हिंदी चुनी गई है", "hi")
            return "hi"

        else:
            speak("Sorry, I did not understand. Please say again.", "en")


# 🔹 Command Handling

def handle_commands(text):
    text = text.lower()

    # 🔥 PLAY → YouTube (AUTO PLAY WITHOUT CLICK)
    if "play" in text:
        query = text.replace("play", "").strip()

        if query:
            try:
                ydl_opts = {
                    'quiet': True,
                    'skip_download': True,
                    'default_search': 'ytsearch',
                    'js_runtimes': {'node':{}},  # ✅ IMPORTANT FIX
                }

                with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                    info = ydl.extract_info(query, download=False)
                    video = info['entries'][0]
                    video_id = video['id']

                    url = f"https://www.youtube.com/embed/{video_id}"
                    webbrowser.open(url)

                return f"Playing {query}"

            except Exception as e:
                print("Error:", e)
                return "Sorry, I couldn't play the video"

        else:
            webbrowser.open("https://www.youtube.com")
            return "Opening YouTube"

    # 🔹 SEARCH → Google
    elif "search" in text:
        import urllib.parse
        query = text.replace("search", "").strip()

        if query:
            search_query = urllib.parse.quote(query)
            webbrowser.open(f"https://www.google.com/search?q={search_query}")
            return f"Searching {query}"
        else:
            webbrowser.open("https://www.google.com")
            return "Opening Google"

    # 🔹 OPEN APPS
    elif "whatsapp" in text:
        webbrowser.open("https://web.whatsapp.com")
        return "Opening WhatsApp"

    elif "youtube" in text:
        webbrowser.open("https://www.youtube.com")
        return "Opening YouTube"

    elif "notepad" in text:
        os.system("notepad")
        return "Opening Notepad"

    elif "calculator" in text:
        os.system("calc")
        return "Opening Calculator"

    # 🔴 EXIT
    elif any(word in text for word in ["bye", "goodbye", "stop", "exit"]):
        return "EXIT"

    return None


# 🔹 Main Assistant
def assistant():
    lang = choose_language()

    # Speak start message
    start_msg = translate_text("Assistant started", lang)
    speak(start_msg, lang)

    while True:
        text = listen()

        # Safety check
        if not text or text == "Error":
            continue

        print("User:", text)

        # 🔹 Step 1: Translate to English
        english_text = translate_text(text, "en")
        print("Translated:", english_text)

        # 🔴 EXIT CONDITION (multilingual)
        if any(word in english_text.lower() for word in ["exit", "bye", "goodbye", "stop"]):
            bye_msg = translate_text("Ok Bye", lang)
            print("Assistant:", bye_msg)
            speak(bye_msg, lang)
            break

        # 🔹 Step 2: Check commands
        command_response = handle_commands(english_text)

        if command_response:
            final_output = translate_text(command_response, lang)
            print("Assistant:", final_output)
            speak(final_output, lang)
            continue

        # 🔹 Step 3: AI response
        ai_reply = get_ai_response(english_text)

        # 🔹 Step 4: Translate back to selected language
        final_output = translate_text(ai_reply, lang)

        print("Assistant:", final_output)

        # 🔹 Step 5: Speak
        speak(final_output, lang)


# 🔹 Run Assistant
if __name__ == "__main__":
    assistant()

