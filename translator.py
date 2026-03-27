<<<<<<< HEAD
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
=======
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
>>>>>>> 3fd4ff1b9efcd09783e97e4d36e9d336665ac9fe
        return text