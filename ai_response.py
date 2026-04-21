import os
from groq import Groq # Or openai

# Initialize the client HERE
client = Groq(
    api_key=os.environ.get("GROQ_API_KEY"),
)

def get_ai_response(prompt):
    # Now 'client' is defined and can be used
    completion = client.chat.completions.create(
        model="mixtral-8x7b-32768",
        messages=[{"role": "user", "content": prompt}]
    )
    return completion.choices[0].message.content