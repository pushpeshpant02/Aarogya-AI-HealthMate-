"""
AI Healthcare Chatbot - FastAPI Backend (Gemini-powered)

Run instructions:
1) Install dependencies:
   pip install -r requirements.txt

2) Create backend/.env with your key:
   GEMINI_API_KEY=your_real_key_here

3) Start the development server:
   uvicorn main:app --reload
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from datetime import datetime
import os

# --- NEW: Gemini + .env ---
from dotenv import load_dotenv
import google.generativeai as genai

# Load environment variables (backend/.env in dev; plain env vars in prod)
load_dotenv()
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
if not GEMINI_API_KEY:
    raise RuntimeError(
        "GEMINI_API_KEY missing. Add it to backend/.env for local "
        "or set as an environment variable on your host (Railway, etc.)."
    )

genai.configure(api_key=GEMINI_API_KEY)
MODEL = genai.GenerativeModel("gemini-1.5-flash")  # use 'gemini-1.5-pro' for deeper answers

# -------- Schemas --------
class ChatRequest(BaseModel):
    message: str

class ChatResponse(BaseModel):
    reply: str

class SOSRequest(BaseModel):
    emergency: bool = True
    timestamp: str | None = None

class SOSResponse(BaseModel):
    status: str
    message: str

# -------- App --------
app = FastAPI(title="AI Healthcare Chatbot Backend", version="0.1.0")

# CORS settings
PRODUCTION_ORIGINS = [
    # "https://your-frontend.com",
    # add more domains here for production
]
app.add_middleware(
    CORSMiddleware,
    allow_origins=PRODUCTION_ORIGINS or [
        "http://127.0.0.1:5500",
        "http://localhost:5500",
        "http://127.0.0.1:3000",
        "http://localhost:3000",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# -------- Logic --------
EMERGENCY_TRIGGERS = ("chest pain", "trouble breathing", "severe bleeding")

SAFETY_SYSTEM_PROMPT = (
    "You are HealthMate, an informational health assistant. "
    "Provide concise, general guidance only. Always include a short disclaimer "
    "that this is not medical advice. If symptoms may be life-threatening, "
    "advise seeking emergency care immediately."
)

def looks_emergency(text: str) -> bool:
    t = text.lower()
    return any(k in t for k in EMERGENCY_TRIGGERS)

def generate_chat_reply(user_message: str) -> str:
    """
    Gemini-backed response generation with a safety system prompt.
    """
    if looks_emergency(user_message):
        return ("⚠️ This may be an emergency. Please seek immediate medical help "
                "or call your local emergency number. (Information only, not medical advice.)")

    prompt = f"{SAFETY_SYSTEM_PROMPT}\n\nUser: {user_message}\nAssistant:"
    try:
        resp = MODEL.generate_content(prompt)
        text = (resp.text or "").strip() if resp else ""
        if not text:
            text = ("Sorry, I couldn’t generate a response right now. "
                    "(Information only, not medical advice.)")
        return text
    except Exception as e:
        return (f"Temporary error reaching the AI service. Please try again. "
                f"(Information only, not medical advice.) Details: {e}")

# -------- Routes --------
@app.post("/chat", response_model=ChatResponse)
def chat(request: ChatRequest) -> ChatResponse:
    """Accept a user's message and return an AI response."""
    reply_text = generate_chat_reply(request.message)
    return ChatResponse(reply=reply_text)

@app.post("/sos", response_model=SOSResponse)
def sos(_: SOSRequest) -> SOSResponse:
    """Handle SOS alerts from the frontend (placeholder)."""
    ts = datetime.utcnow().isoformat()
    return SOSResponse(status="ok", message=f"Emergency services have been notified at {ts}.")

@app.get("/health")
def health() -> dict:
    """Basic health check endpoint for monitoring and deployment checks."""
    return {"status": "ok", "service": "ai-healthcare-chatbot", "version": "0.1.0"}
