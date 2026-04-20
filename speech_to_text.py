import speech_recognition as sr
import tempfile
from pydub import AudioSegment
import os

def listen(audio_bytes):
    """Convert audio bytes to WAV and recognize speech using Google API"""
    if not audio_bytes:
        return None

    try:
        # Create temp files
        with tempfile.NamedTemporaryFile(delete=False, suffix=".webm") as webm_file:
            webm_file.write(audio_bytes)
            webm_path = webm_file.name

        wav_path = webm_path.replace(".webm", ".wav")

        # Convert webm to wav using pydub
        try:
            audio = AudioSegment.from_file(webm_path, format="webm")
            audio.export(wav_path, format="wav")
        except Exception as e:
            print(f"Conversion error: {e}")
            # Fallback: try treating as raw audio
            with open(wav_path, 'wb') as f:
                f.write(audio_bytes)

        # Recognize speech
        recognizer = sr.Recognizer()
        
        try:
            with sr.AudioFile(wav_path) as source:
                audio_data = recognizer.record(source)
                text = recognizer.recognize_google(audio_data)
                return text
        except sr.UnknownValueError:
            return "Could not understand audio"
        except sr.RequestError as e:
            return f"Error: {e}"
        finally:
            # Clean up temp files
            try:
                os.remove(webm_path)
                os.remove(wav_path)
            except:
                pass

    except Exception as e:
        print(f"Listen error: {e}")
        return "Error"
