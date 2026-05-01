import os
from fastapi import FastAPI, Depends, HTTPException
from fastapi.responses import StreamingResponse
from groq import Groq
from dotenv import load_dotenv
from fastapi_clerk_auth import ClerkConfig, ClerkHTTPBearer, HTTPAuthorizationCredentials  # type: ignore

load_dotenv()

app = FastAPI()

clerk_config = ClerkConfig(jwks_url=os.getenv("CLERK_JWKS_URL"))
clerk_guard = ClerkHTTPBearer(clerk_config)


@app.get("/api")
def quote(creds: HTTPAuthorizationCredentials = Depends(clerk_guard)):
    user_id = creds.decoded["sub"]

    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        def error_stream():
            yield "data: GROQ_API_KEY not configured\n\n"
        return StreamingResponse(error_stream(), media_type="text/event-stream")

    client = Groq(api_key=api_key)

    prompt = [{
        "role": "user",
        "content": (
            "Generate an inspiring, motivational quote for someone starting their day. "
            "Make it uplifting, empowering, and memorable. "
            "Format with quote in italics and author below using Markdown."
        )
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
                # ✅ CORRECT SSE FORMAT
                yield f"data: {text}\n\n"

        # optional end event
        yield "data: [DONE]\n\n"

    return StreamingResponse(
        event_stream(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive"
        }
    )