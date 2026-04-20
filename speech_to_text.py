import speech_recognition as sr
import tempfile
import os
import wave

def listen(audio_bytes):
    """Convert webrtc audio bytes to WAV and recognize speech"""
    if not audio_bytes:
        return None

    wav_path = None
    try:
        # Create temporary WAV file
        with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as wav_file:
            wav_path = wav_file.name
            
        # Write audio to WAV file with proper headers
        try:
            with wave.open(wav_path, 'wb') as wav:
                # Streamlit webrtc audio settings
                wav.setnchannels(1)  # Mono
                wav.setsampwidth(2)  # 16-bit (2 bytes)
                wav.setframerate(16000)  # 16kHz sample rate
                wav.writeframes(audio_bytes)
        except Exception as e:
            print(f"WAV writing error: {e}")
            # Fallback: write raw bytes directly
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
            print(f"Recognition service error: {e}")
            return "Service unavailable"
        except Exception as e:
            print(f"Recognition error: {e}")
            return "Error recognizing speech"
            
    except Exception as e:
        print(f"Listen error: {e}")
        return "Error"
    finally:
        # Clean up temporary file
        if wav_path and os.path.exists(wav_path):
            try:
                os.remove(wav_path)
            except:
                pass
