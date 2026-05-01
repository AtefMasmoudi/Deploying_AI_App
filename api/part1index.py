import os
from fastapi import FastAPI
from fastapi.responses import PlainTextResponse
from groq import Groq
from dotenv import load_dotenv

load_dotenv()

app = FastAPI()

@app.get("/api", response_class=PlainTextResponse)
def quote():
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        return "Error: GROQ_API_KEY not configured"

    client = Groq(api_key=api_key)
    prompt = [{
        "role": "user",
        "content": "Generate an inspiring, motivational quote for someone starting their day. Make it uplifting, empowering, and memorable."
    }]
    response = client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=prompt
    )
    return response.choices[0].message.content