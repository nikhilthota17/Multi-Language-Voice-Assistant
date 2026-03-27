<<<<<<< HEAD
from groq import Groq
import os
from dotenv import load_dotenv

load_dotenv()
api_key = os.getenv("GROQ_API_KEY")
client = Groq(api_key=api_key)

def get_ai_response(prompt):
    response = client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=[
            {
                "role": "system",
                "content": "You are a voice assistant. Answer in 1 or 2 short sentences only. Be clear and direct."
            },
            {"role": "user", "content": prompt}
        ],
        max_tokens=60   # 🔥 LIMIT LENGTH
    )
=======
from groq import Groq

client = Groq(api_key="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")

def get_ai_response(prompt):
    response = client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=[
            {
                "role": "system",
                "content": "You are a voice assistant. Answer in 1 or 2 short sentences only. Be clear and direct."
            },
            {"role": "user", "content": prompt}
        ],
        max_tokens=60   # 🔥 LIMIT LENGTH
    )
>>>>>>> 3fd4ff1b9efcd09783e97e4d36e9d336665ac9fe
    return response.choices[0].message.content