import webbrowser
import os
import yt_dlp

from speech_to_text import listen
from translator import translate_text
from text_to_speech import speak
from ai_response import get_ai_response


# 🔹 Language Selection
def choose_language():
    while True:
        speak("Please say your language. English, Telugu, or Hindi.", "en")

        text = listen()

        if not text or text == "Error":
            continue

        text = text.lower()

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
            speak("Sorry, try again.", "en")


# 🔹 Command Handling
def handle_commands(text):
    text = text.lower()

    if "play" in text:
        query = text.replace("play", "").strip()

        if query:
            try:
                ydl_opts = {
                    'quiet': True,
                    'skip_download': True,
                    'default_search': 'ytsearch',
                    'js_runtimes': {'node': {}},
                }

                with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                    info = ydl.extract_info(query, download=False)
                    video = info['entries'][0]
                    video_id = video['id']

                    url = f"https://www.youtube.com/watch?v={video_id}"
                    webbrowser.open(url)

                return f"Playing {query}"

            except Exception as e:
                print("Error:", e)
                return "Sorry, couldn't play"

    elif "search" in text:
        import urllib.parse
        query = text.replace("search", "").strip()

        if query:
            url = f"https://www.google.com/search?q={urllib.parse.quote(query)}"
            webbrowser.open(url)
            return f"Searching {query}"

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

    elif any(word in text for word in ["bye", "goodbye", "stop", "exit"]):
        return "EXIT"

    return None


# 🔹 Main Assistant
def assistant():
    lang = choose_language()

    speak(translate_text("Assistant started", lang), lang)

    while True:
        text = listen()

        if not text or text == "Error":
            continue

        english_text = translate_text(text, "en")

        if any(word in english_text.lower() for word in ["exit", "bye", "goodbye", "stop"]):
            speak(translate_text("Ok Bye", lang), lang)
            break

        command = handle_commands(english_text)

        if command:
            speak(translate_text(command, lang), lang)
            continue

        ai_reply = get_ai_response(english_text)
        final_output = translate_text(ai_reply, lang)

        speak(final_output, lang)


if __name__ == "__main__":
    assistant()