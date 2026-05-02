import os
from contextlib import asynccontextmanager

from dotenv import load_dotenv
from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from fastapi_clerk_auth import ClerkConfig, ClerkHTTPBearer, HTTPAuthorizationCredentials  # type: ignore

from groq import Groq


load_dotenv()

GROQ_API_KEY = os.getenv("GROQ_API_KEY")

clerk_config = ClerkConfig(jwks_url=os.getenv("CLERK_JWKS_URL"))
clerk_guard = ClerkHTTPBearer(clerk_config)


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



# ── SSE helper ─────────────────────────────────────────────────────────
SSE_HEADERS = {
    "Cache-Control": "no-cache, no-transform",
    "X-Accel-Buffering": "no",
}

async def quote_stream():
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

@app.get("/api")
async def quote(ucreds: HTTPAuthorizationCredentials = Depends(clerk_guard)):
    return StreamingResponse(
        quote_stream(),
        media_type="text/event-stream",
        headers=SSE_HEADERS,
    )