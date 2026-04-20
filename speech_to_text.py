import speech_recognition as sr
import tempfile
import os
import subprocess
import struct
import io


# ──────────────────────────────────────────────────────────────
# UTILITY: write a proper WAV file from raw PCM bytes
# ──────────────────────────────────────────────────────────────
def _write_wav(pcm_bytes: bytes, path: str, sample_rate=16000, channels=1, bit_depth=16):
    byte_rate    = sample_rate * channels * bit_depth // 8
    block_align  = channels * bit_depth // 8
    data_size    = len(pcm_bytes)
    with open(path, "wb") as f:
        f.write(b"RIFF")
        f.write(struct.pack("<I", 36 + data_size))
        f.write(b"WAVE")
        f.write(b"fmt ")
        f.write(struct.pack("<IHHIIHH", 16, 1, channels, sample_rate,
                            byte_rate, block_align, bit_depth))
        f.write(b"data")
        f.write(struct.pack("<I", data_size))
        f.write(pcm_bytes)


# ──────────────────────────────────────────────────────────────
# STRATEGY 1 — ffmpeg (best, handles webm/ogg/opus/mp4)
# ──────────────────────────────────────────────────────────────
def _try_ffmpeg(raw_path: str, wav_path: str) -> bool:
    try:
        result = subprocess.run(
            ["ffmpeg", "-y", "-i", raw_path,
             "-ar", "16000", "-ac", "1", "-f", "wav", wav_path],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            timeout=15
        )
        if result.returncode == 0 and os.path.exists(wav_path) and os.path.getsize(wav_path) > 1000:
            print("[STT] ✅ ffmpeg conversion succeeded")
            return True
        print("[STT] ffmpeg error:", result.stderr.decode(errors="ignore")[-200:])
    except FileNotFoundError:
        print("[STT] ffmpeg not found on this system")
    except Exception as e:
        print(f"[STT] ffmpeg exception: {e}")
    return False


# ──────────────────────────────────────────────────────────────
# STRATEGY 2 — pydub (needs ffmpeg internally, but tries anyway)
# ──────────────────────────────────────────────────────────────
def _try_pydub(raw_path: str, wav_path: str) -> bool:
    try:
        from pydub import AudioSegment
        for fmt in ("webm", "ogg", "mp4", "wav", "raw"):
            try:
                if fmt == "raw":
                    sound = AudioSegment.from_raw(
                        raw_path, sample_width=2, frame_rate=44100, channels=1
                    )
                else:
                    sound = AudioSegment.from_file(raw_path, format=fmt)

                sound = sound.set_channels(1).set_frame_rate(16000).set_sample_width(2)
                sound.export(wav_path, format="wav")

                if os.path.exists(wav_path) and os.path.getsize(wav_path) > 1000:
                    print(f"[STT] ✅ pydub succeeded with format='{fmt}'")
                    return True
            except Exception as e:
                print(f"[STT] pydub format '{fmt}' failed: {e}")
    except ImportError:
        print("[STT] pydub not installed")
    return False


# ──────────────────────────────────────────────────────────────
# STRATEGY 3 — Raw WAV passthrough (browser sends actual WAV)
# ──────────────────────────────────────────────────────────────
def _try_raw_wav(audio_bytes: bytes, wav_path: str) -> bool:
    if audio_bytes[:4] == b"RIFF" and b"WAVE" in audio_bytes[:12]:
        with open(wav_path, "wb") as f:
            f.write(audio_bytes)
        print("[STT] ✅ Bytes are already a valid WAV file")
        return True
    return False


# ──────────────────────────────────────────────────────────────
# STRATEGY 4 — soundfile / scipy (pure Python, no ffmpeg)
# Works only for WAV/FLAC/OGG formats
# ──────────────────────────────────────────────────────────────
def _try_soundfile(audio_bytes: bytes, wav_path: str) -> bool:
    try:
        import soundfile as sf
        import numpy as np

        buf = io.BytesIO(audio_bytes)
        data, samplerate = sf.read(buf, dtype="int16")

        # Resample to 16kHz if needed
        if samplerate != 16000:
            try:
                import scipy.signal as sig
                samples = round(len(data) * 16000 / samplerate)
                data = sig.resample(data, samples).astype("int16")
            except ImportError:
                pass  # skip resample, still try

        # Convert stereo → mono
        if data.ndim == 2:
            data = data.mean(axis=1).astype("int16")

        _write_wav(data.tobytes(), wav_path, sample_rate=16000)
        print("[STT] ✅ soundfile conversion succeeded")
        return True
    except Exception as e:
        print(f"[STT] soundfile failed: {e}")
    return False


# ──────────────────────────────────────────────────────────────
# MAIN ENTRY POINT
# ──────────────────────────────────────────────────────────────
def listen(audio_bytes: bytes) -> str:
    """
    Convert mic audio bytes → transcribed text.
    Returns "Error" on any failure.
    """

    if not audio_bytes or len(audio_bytes) < 500:
        print(f"[STT] Audio too small: {len(audio_bytes) if audio_bytes else 0} bytes")
        return "Error"

    print(f"[STT] Received {len(audio_bytes)} bytes | magic: {audio_bytes[:8].hex()}")

    with tempfile.TemporaryDirectory() as tmp:
        raw_path = os.path.join(tmp, "input.audio")
        wav_path = os.path.join(tmp, "output.wav")

        # Save raw bytes
        with open(raw_path, "wb") as f:
            f.write(audio_bytes)

        # Try each conversion strategy in order
        converted = (
            _try_raw_wav(audio_bytes, wav_path)   or
            _try_ffmpeg(raw_path, wav_path)        or
            _try_pydub(raw_path, wav_path)         or
            _try_soundfile(audio_bytes, wav_path)
        )

        if not converted:
            print("[STT] ❌ All conversion strategies failed")
            return "Error"

        wav_size = os.path.getsize(wav_path)
        print(f"[STT] WAV ready: {wav_size} bytes")

        if wav_size < 1000:
            print("[STT] WAV too small — silent or corrupt")
            return "Error"

        # ── Speech recognition
        recognizer = sr.Recognizer()
        recognizer.energy_threshold       = 150   # lower = picks up quieter speech
        recognizer.dynamic_energy_threshold = True
        recognizer.pause_threshold        = 0.8

        try:
            with sr.AudioFile(wav_path) as source:
                recognizer.adjust_for_ambient_noise(source, duration=0.2)
                audio_data = recognizer.record(source)

            text = recognizer.recognize_google(audio_data)
            print(f"[STT] ✅ Recognized: '{text}'")
            return text

        except sr.UnknownValueError:
            print("[STT] ❌ Google could not understand speech")
            return "Error"

        except sr.RequestError as e:
            print(f"[STT] ❌ Google API error: {e}")
            return "NetworkError"

        except Exception as e:
            print(f"[STT] ❌ Unexpected error: {e}")
            return "Error"