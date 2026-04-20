import speech_recognition as sr
import tempfile
import os
from pydub import AudioSegment

def listen(audio_bytes):
    if not audio_bytes:
        return "Error"

    input_path = None
    output_path = None

    try:
        # save browser audio
        with tempfile.NamedTemporaryFile(delete=False, suffix=".webm") as f:
            f.write(audio_bytes)
            input_path = f.name

        output_path = input_path.replace(".webm", ".wav")

        # convert to wav
        sound = AudioSegment.from_file(input_path, format="webm")
        sound = sound.set_channels(1)
        sound = sound.set_frame_rate(16000)
        sound.export(output_path, format="wav")

        recognizer = sr.Recognizer()

        with sr.AudioFile(output_path) as source:
            audio = recognizer.record(source)

        text = recognizer.recognize_google(audio)
        return text

    except Exception as e:
        print("Speech error:", e)
        return "Error"

    finally:
        for file in [input_path, output_path]:
            if file and os.path.exists(file):
                os.remove(file)