import os
from fastapi import FastAPI, Depends
from fastapi.responses import StreamingResponse
from fastapi_clerk_auth import ClerkConfig, ClerkHTTPBearer, HTTPAuthorizationCredentials
from groq import Groq
from dotenv import load_dotenv

load_dotenv()

app = FastAPI()

clerk_config = ClerkConfig(jwks_url=os.getenv("CLERK_JWKS_URL"))
clerk_guard = ClerkHTTPBearer(clerk_config)

@app.get("/api")
def quote(creds: HTTPAuthorizationCredentials = Depends(clerk_guard)):
    user_id = creds.decoded["sub"]  # User ID from JWT
    # We now know which user is making the request!
    # You could use user_id to:
    # - Track usage per user
    # - Store favorite quotes in a database
    # - Apply user-specific limits or customization

    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        def error_stream():
            yield "data: Error: GROQ_API_KEY not configured\\n\\n"
        return StreamingResponse(error_stream(), 
                                 media_type="text/event-stream")

    client = Groq(api_key=api_key)
    prompt = [{
        "role": "user",
        "content": "Reply with an inspiring motivational quote, formatted "
                   "with the quote in italics and the author name below it. "
                   "Use Markdown formatting."
    }]
    stream = client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=prompt,
        stream=True
    )

    def event_stream():
        for chunk in stream:
            text = chunk.choices[0].delta.content
            print(text)
            if text:
                #lines = text.split("\n\n")
                #for line in lines:
                yield f"data: {text}\n\n"
                #yield "\n\n"

    return StreamingResponse(event_stream(), media_type="text/event-stream")
