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
    return response.choices[0].message.content