import os
from dotenv import load_dotenv
from groq import Groq

# Load env
load_dotenv()

api_key = os.getenv("GROQ_API_KEY")

client = Groq(api_key=api_key)


def get_ai_response(prompt):
    try:
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",  # latest working model
            messages=[
                {"role": "system", "content": "You are a voice assistant. Answer briefly."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=60
        )

        return response.choices[0].message.content.strip()

    except Exception as e:
        print("Error:", e)
        return "Sorry, I'm having trouble right now."