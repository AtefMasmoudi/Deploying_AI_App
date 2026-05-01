import os
import sys
import traceback

print("[DEBUG] api/index.py starting...", file=sys.stderr)

# Load environment
try:
    from dotenv import load_dotenv
    load_dotenv()
except Exception:
    pass

GROQ_API_KEY = os.getenv("GROQ_API_KEY")
CLERK_JWKS_URL = os.getenv("CLERK_JWKS_URL")
CLERK_SECRET_KEY = os.getenv("CLERK_SECRET_KEY")

print(f"[DEBUG] GROQ_API_KEY present: {bool(GROQ_API_KEY)}", file=sys.stderr)
print(f"[DEBUG] CLERK_JWKS_URL present: {bool(CLERK_JWKS_URL)}", file=sys.stderr)

from fastapi import FastAPI, Request
from fastapi.responses import StreamingResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
import jwt
import httpx

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Cache JWKS keys
_jwks_cache = None
_jwks_last_fetch = None

def get_jwks_keys():
    global _jwks_cache, _jwks_last_fetch
    if _jwks_cache is not None:
        return _jwks_cache
    if not CLERK_JWKS_URL:
        return None
    try:
        resp = httpx.get(CLERK_JWKS_URL, timeout=10.0)
        resp.raise_for_status()
        _jwks_cache = resp.json().get("keys", [])
        return _jwks_cache
    except Exception as e:
        print(f"[ERROR] Failed to fetch JWKS: {e}", file=sys.stderr)
        return None

def verify_clerk_token(token: str):
    """Verify a Clerk JWT using JWKS. Returns user_id or None."""
    keys = get_jwks_keys()
    if not keys:
        return None
    try:
        kid = jwt.get_unverified_header(token).get("kid")
        key = next((k for k in keys if k.get("kid") == kid), None)
        if not key:
            return None
        from jwt.algorithms import RSAAlgorithm
        public_key = RSAAlgorithm.from_jwk(key)
        payload = jwt.decode(token, public_key, algorithms=["RS256"])
        return payload.get("sub")
    except jwt.ExpiredSignatureError:
        print("[ERROR] Token expired", file=sys.stderr)
        return None
    except Exception as e:
        print(f"[ERROR] Token verification failed: {e}", file=sys.stderr)
        return None

SSE_HEADERS = {
    "Cache-Control": "no-cache",
    "X-Accel-Buffering": "no",
}

@app.get("/api/health")
async def health_check():
    return {
        "status": "healthy",
        "groq_key_present": bool(GROQ_API_KEY),
        "jwks_url_present": bool(CLERK_JWKS_URL),
    }

@app.get("/api")
def quote(request: Request):
    auth_header = request.headers.get("Authorization", "")
    if not auth_header.startswith("Bearer "):
        def auth_err():
            yield "data: Error: Missing Authorization header\n\n"
        return StreamingResponse(auth_err(), media_type="text/event-stream",
                                 headers=SSE_HEADERS)

    token = auth_header[7:]
    user_id = verify_clerk_token(token)
    if not user_id:
        def auth_err():
            yield "data: Error: Invalid or expired token. Please sign in again.\n\n"
        return StreamingResponse(auth_err(), media_type="text/event-stream",
                                 headers=SSE_HEADERS)

    print(f"[DEBUG] Authenticated user: {user_id}", file=sys.stderr)

    if not GROQ_API_KEY:
        def key_err():
            yield "data: Error: GROQ_API_KEY not configured\n\n"
        return StreamingResponse(key_err(), media_type="text/event-stream",
                                 headers=SSE_HEADERS)

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
        def groq_err():
            yield f"data: Error: AI service unavailable -- {str(e)}\n\n"
        return StreamingResponse(groq_err(), media_type="text/event-stream",
                                 headers=SSE_HEADERS)

    def event_stream():
        try:
            for chunk in stream:
                text = chunk.choices[0].delta.content
                if text:
                    lines = text.split("\n")
                    for line in lines:
                        if line:
                            yield f"data: {line}\n"
                        else:
                            yield "data:  \n"
                    yield "\n"
            #yield "data: [DONE]\n\n"
        except Exception as e:
            print(f"[ERROR] Stream error: {e}", file=sys.stderr)
            yield f"data: Error: Stream interrupted -- {str(e)}\n\n"

    return StreamingResponse(event_stream(), media_type="text/event-stream",
                             headers=SSE_HEADERS)

@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    print(f"[FATAL] {exc}", file=sys.stderr)
    traceback.print_exc(file=sys.stderr)
    return JSONResponse(status_code=500,
                        content={"detail": "Internal server error"})

print("[DEBUG] api/index.py loaded successfully", file=sys.stderr)
