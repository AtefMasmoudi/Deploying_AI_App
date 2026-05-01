import os
from fastapi import FastAPI, Request, Depends
from fastapi.responses import StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi_clerk_auth import ClerkConfig, ClerkHTTPBearer, HTTPAuthorizationCredentials
from groq import Groq
from dotenv import load_dotenv

load_dotenv()

app = FastAPI()

# CORS is required for SSE to work correctly across origins
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configure Clerk authentication
clerk_config = ClerkConfig(jwks_url=os.getenv("CLERK_JWKS_URL"))
clerk_guard = ClerkHTTPBearer(clerk_config)

# SSE headers to prevent proxy buffering
SSE_HEADERS = {
    "Cache-Control": "no-cache, no-transform",
    "X-Accel-Buffering": "no",
    "Connection": "keep-alive",
}

@app.get("/api")
def quote(request: Request):
    # Extract Authorization header manually to handle errors gracefully
    auth_header = request.headers.get("Authorization", "")

    # Validate auth header format
    if not auth_header.startswith("Bearer "):
        def auth_error_stream():
            yield "data: Error: Missing or invalid Authorization header\\n\\n"
        return StreamingResponse(
            auth_error_stream(),
            media_type="text/event-stream",
            headers=SSE_HEADERS
        )

    # Verify JWT token
    try:
        creds = clerk_guard(request)
        user_id = creds.decoded.get("sub", "unknown")
    except Exception as e:
        def auth_error_stream():
            yield f"data: Error: Authentication failed -- {str(e)}\\n\\n"
        return StreamingResponse(
            auth_error_stream(),
            media_type="text/event-stream",
            headers=SSE_HEADERS
        )

    # Check Groq API key
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        def config_error_stream():
            yield "data: Error: GROQ_API_KEY not configured\\n\\n"
        return StreamingResponse(
            config_error_stream(),
            media_type="text/event-stream",
            headers=SSE_HEADERS
        )

    # Generate motivational quote with streaming
    try:
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
    except Exception as e:
        def groq_error_stream():
            yield f"data: Error: Failed to initialize Groq stream -- {str(e)}\\n\\n"
        return StreamingResponse(
            groq_error_stream(),
            media_type="text/event-stream",
            headers=SSE_HEADERS
        )

    def event_stream():
        try:
            for chunk in stream:
                text = chunk.choices[0].delta.content
                if text:
                    lines = text.split("\\n")
                    for line in lines:
                        if line:
                            yield f"data: {line}\\n"
                        else:
                            yield "data:  \\n"
                    yield "\\n"
            # Send completion marker
            yield "data: [DONE]\\n\\n"
        except Exception as e:
            yield f"data: Error: Stream interrupted -- {str(e)}\\n\\n"

    return StreamingResponse(
        event_stream(),
        media_type="text/event-stream",
        headers=SSE_HEADERS
    )