import os
from fastapi import FastAPI
from fastapi.responses import StreamingResponse
from groq import Groq
from dotenv import load_dotenv

load_dotenv()

app = FastAPI()

@app.get("/api")
def quote():
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        def error_stream():
            yield "data: Error: GROQ_API_KEY not configured\n\n"
        return StreamingResponse(error_stream(), media_type="text/event-stream")

    client = Groq(api_key=api_key)
    prompt = [{
        "role": "user",
        "content": "Generate an inspiring, motivational quote for someone starting their day. Make it uplifting, empowering, and memorable."
    }]
    stream = client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=prompt,
        stream=True
    )

    def event_stream():
        for chunk in stream:
            text = chunk.choices[0].delta.content
            if text:
                lines = text.split("\n")
                for line in lines:
                    yield f"data: {line}\n"
                yield "\n"

    return StreamingResponse(event_stream(), media_type="text/event-stream")