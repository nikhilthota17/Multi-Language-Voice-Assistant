from deep_translator import GoogleTranslator
from langdetect import detect

def detect_language(text):
    try:
        return detect(text)
    except:
        return "en"

def translate_text(text, dest):
    try:
        return GoogleTranslator(source='auto', target=dest).translate(text)
    except:
        return text