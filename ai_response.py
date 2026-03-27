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
    return response.choices[0].message.content