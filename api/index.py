import os
from contextlib import asynccontextmanager

from dotenv import load_dotenv
from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from groq import Groq
import httpx
import jwt
from jwt.algorithms import RSAAlgorithm

load_dotenv()

GROQ_API_KEY = os.getenv("GROQ_API_KEY")
CLERK_JWKS_URL = os.getenv("CLERK_JWKS_URL")

# ── Lifespan: initialize heavy resources once ──────────────────────────
@asynccontextmanager
async def lifespan(app: FastAPI):
    app.state.groq = Groq(api_key=GROQ_API_KEY) if GROQ_API_KEY else None
    app.state.jwks = {}
    yield
    # cleanup (if needed)

app = FastAPI(lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=os.getenv("CORS_ORIGINS", "*").split(","),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

security = HTTPBearer(auto_error=False)

# ── Auth dependency ────────────────────────────────────────────────────
async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)) -> str:
    if not credentials or not credentials.scheme == "Bearer":
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Missing bearer token")
    
    token = credentials.credentials
    if not CLERK_JWKS_URL:
        raise HTTPException(status.HTTP_503_SERVICE_UNAVAILABLE, "Auth not configured")

    # Lazy-load & cache JWKS
    if not app.state.jwks:
        async with httpx.AsyncClient() as client:
            r = await client.get(CLERK_JWKS_URL, timeout=10)
            r.raise_for_status()
            app.state.jwks = {k["kid"]: k for k in r.json().get("keys", [])}

    try:
        kid = jwt.get_unverified_header(token).get("kid")
        key = RSAAlgorithm.from_jwk(app.state.jwks[kid])
        payload = jwt.decode(token, key, algorithms=["RS256"])
        return payload.get("sub")
    except Exception as exc:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Invalid or expired token") from exc

# ── SSE helper ─────────────────────────────────────────────────────────
SSE_HEADERS = {
    "Cache-Control": "no-cache, no-transform",
    "X-Accel-Buffering": "no",
}

async def quote_stream(user_id: str):
    client: Groq = app.state.groq
    if not client:
        yield "data: Error: AI service not configured\n\n"
        return

    try:
        stream = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[{
                "role": "user",
                "content": "Generate a short inspiring and motivational text for someone wants to learn AI production engineering with Atef MASMOUDI. Make it uplifting, empowering, and memorable. Generate the text formatted with headings, sub-headings and bullet points."
            }],
            stream=True
        )
        for chunk in stream:
            text = chunk.choices[0].delta.content
            if text:
                lines = text.split("\n")
                for line in lines[:-1]:
                    yield f"data: {line}\n\n"
                    yield "data: \n"
                yield f"data: {lines[-1]}\n\n"
        
    except Exception as exc:
        yield f"data: Error: {exc}\n\n"

# ── Endpoints ──────────────────────────────────────────────────────────
@app.get("/api/health")
async def health():
    return {
        "status": "healthy",
        "groq_key_present": bool(GROQ_API_KEY),
        "jwks_url_present": bool(CLERK_JWKS_URL),
    }

@app.get("/api")
async def quote(user_id: str = Depends(get_current_user)):
    return StreamingResponse(
        quote_stream(user_id),
        media_type="text/event-stream",
        headers=SSE_HEADERS,
    )