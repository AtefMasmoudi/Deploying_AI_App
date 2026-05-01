import os
import sys
import traceback

# Debug: print startup info to stderr (visible in Vercel logs)
print("[DEBUG] api/index.py starting...", file=sys.stderr)
print(f"[DEBUG] Python version: {sys.version}", file=sys.stderr)

# --- Safe environment loading ---
try:
    from dotenv import load_dotenv
    load_dotenv()
    print("[DEBUG] dotenv loaded", file=sys.stderr)
except Exception as e:
    print(f"[DEBUG] dotenv load failed (ok if env vars set in Vercel): {e}", 
          file=sys.stderr)

# --- Check critical env vars BEFORE importing heavy deps ---
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
CLERK_JWKS_URL = os.getenv("CLERK_JWKS_URL")

print(f"[DEBUG] GROQ_API_KEY present: {bool(GROQ_API_KEY)}", file=sys.stderr)
print(f"[DEBUG] CLERK_JWKS_URL present: {bool(CLERK_JWKS_URL)}", file=sys.stderr)

# --- Import FastAPI ---
from fastapi import FastAPI, Request
from fastapi.responses import StreamingResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

# Add CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- Health check (no auth required) ---
@app.get("/api/health")
@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "groq_key_present": bool(GROQ_API_KEY),
        "jwks_url_present": bool(CLERK_JWKS_URL),
    }

# --- Main SSE endpoint ---
@app.get("/api")
def quote(request: Request):
    # Extract Authorization header
    auth_header = request.headers.get("Authorization", "")

    if not auth_header.startswith("Bearer "):
        def auth_err():
            yield "data: Error: Missing Authorization header\\n\\n"
        return StreamingResponse(
            auth_err(),
            media_type="text/event-stream",
            headers={
                "Cache-Control": "no-cache",
                "X-Accel-Buffering": "no",
            }
        )

    token = auth_header[7:]  # Remove "Bearer "

    # Verify JWT (lazy import to avoid startup failures)
    try:
        from fastapi_clerk_auth import ClerkConfig, ClerkHTTPBearer
        clerk_config = ClerkConfig(jwks_url=CLERK_JWKS_URL)
        clerk_guard = ClerkHTTPBearer(clerk_config)
        # Manually verify
        creds = clerk_guard(request)
        user_id = creds.decoded.get("sub", "unknown")
        print(f"[DEBUG] Authenticated user: {user_id}", file=sys.stderr)
    except Exception as e:
        print(f"[ERROR] Auth failed: {e}", file=sys.stderr)
        traceback.print_exc(file=sys.stderr)
        def auth_err():
            yield f"data: Error: Authentication failed -- {str(e)}\\n\\n"
        return StreamingResponse(
            auth_err(),
            media_type="text/event-stream",
            headers={
                "Cache-Control": "no-cache",
                "X-Accel-Buffering": "no",
            }
        )

    # Check Groq key
    if not GROQ_API_KEY:
        def key_err():
            yield "data: Error: GROQ_API_KEY not configured\\n\\n"
        return StreamingResponse(
            key_err(),
            media_type="text/event-stream",
            headers={
                "Cache-Control": "no-cache",
                "X-Accel-Buffering": "no",
            }
        )

    # Generate quote
    try:
        from groq import Groq
        client = Groq(api_key=GROQ_API_KEY)
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
        print(f"[ERROR] Groq init failed: {e}", file=sys.stderr)
        traceback.print_exc(file=sys.stderr)
        def groq_err():
            yield f"data: Error: Failed to connect to AI service -- {str(e)}\\n\\n"
        return StreamingResponse(
            groq_err(),
            media_type="text/event-stream",
            headers={
                "Cache-Control": "no-cache",
                "X-Accel-Buffering": "no",
            }
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
            yield "data: [DONE]\\n\\n"
        except Exception as e:
            print(f"[ERROR] Stream error: {e}", file=sys.stderr)
            traceback.print_exc(file=sys.stderr)
            yield f"data: Error: Stream interrupted -- {str(e)}\\n\\n"

    return StreamingResponse(
        event_stream(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "X-Accel-Buffering": "no",
        }
    )

# --- Global exception handler ---
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    print(f"[FATAL] Unhandled exception: {exc}", file=sys.stderr)
    traceback.print_exc(file=sys.stderr)
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error", "error": str(exc)}
    )

print("[DEBUG] api/index.py loaded successfully", file=sys.stderr)