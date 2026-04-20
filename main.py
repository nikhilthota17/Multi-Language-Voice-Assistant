import webbrowser
import os
import platform
import subprocess
import urllib.parse
import yt_dlp


def open_app(app_name: str):
    system = platform.system().lower()

    try:
        if "windows" in system:
            if app_name == "notepad":
                os.system("notepad")
            elif app_name == "calculator":
                os.system("calc")
            else:
                os.system(app_name)

        elif "linux" in system:
            subprocess.Popen([app_name])

        elif "darwin" in system:
            subprocess.Popen(["open", "-a", app_name])

    except Exception:
        pass


def play_youtube(query):
    try:
        ydl_opts = {
            "quiet": True,
            "skip_download": True,
            "default_search": "ytsearch1"
        }

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(query, download=False)

            if "entries" in info:
                video = info["entries"][0]
            else:
                video = info

            url = f"https://www.youtube.com/watch?v={video['id']}"
            webbrowser.open(url)
            return f"Playing {query}"

    except Exception:
        return "Unable to play video."


def handle_commands(text):
    if not text:
        return None

    text = text.lower().strip()

    # Exit
    if any(word in text for word in ["bye", "goodbye", "stop", "exit"]):
        return "Goodbye!"

    # Play song/video
    if text.startswith("play "):
        query = text.replace("play", "", 1).strip()
        if query:
            return play_youtube(query)

    # Search google
    if text.startswith("search "):
        query = text.replace("search", "", 1).strip()
        if query:
            url = f"https://www.google.com/search?q={urllib.parse.quote(query)}"
            webbrowser.open(url)
            return f"Searching {query}"

    # Open websites
    if "youtube" in text:
        webbrowser.open("https://www.youtube.com")
        return "Opening YouTube"

    if "whatsapp" in text:
        webbrowser.open("https://web.whatsapp.com")
        return "Opening WhatsApp"

    if "gmail" in text:
        webbrowser.open("https://mail.google.com")
        return "Opening Gmail"

    if "google" in text:
        webbrowser.open("https://www.google.com")
        return "Opening Google"

    # Open system apps
    if "notepad" in text:
        open_app("notepad")
        return "Opening Notepad"

    if "calculator" in text:
        open_app("calculator")
        return "Opening Calculator"

    return None


if __name__ == "__main__":
    while True:
        cmd = input("Enter Command: ")

        result = handle_commands(cmd)

        if result:
            print(result)

        if result == "Goodbye!":
            break   