# 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

import os
from openai import OpenAI

# Set Groq API key
os.environ["OPENAI_API_KEY"] = "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"

client = OpenAI(
    base_url="https://api.groq.com/openai/v1",
    api_key=os.environ["OPENAI_API_KEY"]
)

# Make a chat completion request using a supported model
response = client.chat.completions.create(
    model="llama3-70b-8192",  # or llama3-70b-8192, mixtral-8x7b-32768, gemma-7b-it
messages = [
    {
        "role": "system",
        "content": (
            "You are a helpful food recommendation assistant. "
            "Based on the user's current mood, weather, time of day, and location, suggest 5 food or drink options. "
            "Make sure the options are appropriate for the time (e.g., light food at night, beverages during tea time) "
            "and culturally relevant to the location mentioned. Include both comfort food and healthy choices if possible."
        )
    },
    {
        "role": "user",
        "content": (
            "I feel tired, it's summer, I'm in Kochi, and it's lunch time. "
            "What food or drinks do you suggest?"
        )
    }
],


    temperature=0.7,
    max_tokens=300
)

print(response.choices[0].message.content)
