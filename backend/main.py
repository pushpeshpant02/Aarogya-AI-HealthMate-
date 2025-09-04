"""
AI Healthcare Chatbot - FastAPI Backend (Gemini + optional FAISS)
— Full, detailed answers; no disclaimers —

Run locally:
  pip install -r requirements.txt
  uvicorn main:app --host 127.0.0.1 --port 8000 --reload

Environment (set in backend/.env or platform env vars):
  - GEMINI_API_KEY   (required for LLM replies)
  - GEMINI_MODEL     (optional, default: gemini-1.5-flash)
  - ALLOW_ORIGINS    (optional, comma-separated list for CORS in prod)
  - FULL_GEMINI      (optional, "1"=always use Gemini; default "1")
  - USE_CONTEXT      (optional, "1"=include retrieved context in prompt; default "0")
  - FAISS_FALLBACK   (optional, "1"=fallback to FAISS sections if LLM empty; default "0")
  - MAX_TOKENS       (optional, default "2048")
  - TEMPERATURE      (optional, default "0.9")
  - TOP_P            (optional, default "0.95")
"""

from typing import List, Optional
import os
from pathlib import Path
from datetime import datetime

from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, ConfigDict

# ---------------- Env & Gemini Setup ----------------
load_dotenv(dotenv_path=Path(__file__).parent / ".env", override=False)

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "").strip()
GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-1.5-flash").strip()

# Behavior flags (override via env without changing code)
FULL_GEMINI = os.getenv("FULL_GEMINI", "1") == "1"          # if true, always use Gemini
USE_CONTEXT = os.getenv("USE_CONTEXT", "0") == "1"           # if true, include retrieved context in prompt
FAISS_FALLBACK = os.getenv("FAISS_FALLBACK", "0") == "1"     # if true, shape answers from FAISS if LLM is empty

MAX_TOKENS = int(os.getenv("MAX_TOKENS", "2048"))
TEMPERATURE = float(os.getenv("TEMPERATURE", "0.9"))
TOP_P = float(os.getenv("TOP_P", "0.95"))

# Gemini SDK is optional at runtime (we fallback if key missing)
_genai_available = False
try:
    import google.generativeai as genai
    if GEMINI_API_KEY:
        genai.configure(api_key=GEMINI_API_KEY)
        _GEN_MODEL = genai.GenerativeModel(
            GEMINI_MODEL,
            generation_config={
                "temperature": TEMPERATURE,
                "top_p": TOP_P,
                "max_output_tokens": MAX_TOKENS,
            },
        )
        _genai_available = True
    else:
        print("⚠️ GEMINI_API_KEY not set — LLM disabled.")
except Exception as _e:
    print(f"⚠️ google-generativeai unavailable ({_e}) — LLM disabled.")

# ---------------- Safeguards ----------------
EMERGENCY_KEYWORDS = [
    "chest pain",
    "difficulty breathing",
    "trouble breathing",
    "shortness of breath",
    "suicidal",
    "suicide",
    "fainting",
    "severe bleeding",
]

# Toggle this if you also want to hide emergency messages completely
SHOW_EMERGENCY_NOTICE = True

# System prompt: allow detailed, full responses (no disclaimers, no forced brevity)
SYSTEM_PROMPT = (
    "You are an AI healthcare assistant. Answer the user's question fully and clearly, "
    "providing step-by-step, well-structured explanations when helpful. "
    "Use everyday language and add practical tips. Avoid adding disclaimers unless asked."
)

# ---------------- Schemas ----------------
class ChatRequest(BaseModel):
    model_config = ConfigDict(extra="ignore")
    message: str

class ChatResponse(BaseModel):
    reply: str
    emergency_recommended: bool = False

class SOSRequest(BaseModel):
    model_config = ConfigDict(extra="ignore")
    emergency: bool = True
    timestamp: Optional[str] = None

class SOSResponse(BaseModel):
    status: str

# ---------------- Utilities ----------------
def contains_emergency_keywords(text: str) -> bool:
    lowered = text.lower()
    return any(keyword in lowered for keyword in EMERGENCY_KEYWORDS)

def _import_llm_client():
    try:
        from .services.llm import LLMClient  # type: ignore
    except Exception:
        from services.llm import LLMClient  # type: ignore
    return LLMClient

def _import_retriever():
    try:
        from .services.retrieval import Retriever  # type: ignore
    except Exception:
        from services.retrieval import Retriever  # type: ignore
    return Retriever

def retrieve_context(query: str) -> List[str]:
    Retriever = _import_retriever()
    try:
        return Retriever().search(query, k=4)
    except Exception as e:
        print("⚠️ Retrieval failed:", e)
        return []

def generate_via_llm(prompt: str, context_blocks: Optional[List[str]] = None) -> str:
    """
    Priority:
    1) Gemini SDK if configured
    2) Your custom LLMClient() if present
    """
    # 1) Gemini
    if _genai_available and FULL_GEMINI:
        try:
            ctx = "\n\n".join(context_blocks or []) if (context_blocks and USE_CONTEXT) else ""
            final_prompt = (
                f"{SYSTEM_PROMPT}\n\n"
                f"{'Context:\\n' + ctx + '\\n\\n' if ctx else ''}"
                f"User: {prompt}\nAssistant:"
            )
            resp = _GEN_MODEL.generate_content(final_prompt)
            text = (resp.text or "").strip() if resp else ""
            if text:
                return text
        except Exception as e:
            print("⚠️ Gemini call failed:", e)

    # 2) Custom LLMClient (optional if you have it wired)
    try:
        LLMClient = _import_llm_client()
        return LLMClient().generate(prompt, context_blocks if USE_CONTEXT else None)
    except Exception as e:
        print("ℹ️ Custom LLMClient unavailable:", e)
        return ""

def format_as_markdown(section_title: str, text_block: str) -> str:
    """Format bullet lists from plain text into markdown."""
    lines = [line.strip("- ").strip() for line in text_block.split("\n") if line.strip()]
    bullets = "\n".join([f"- {line}" for line in lines])
    return f"**{section_title}:**\n{bullets}" if bullets else f"**{section_title}:**\n{text_block}"

# ---------------- Reply Builder ----------------
def build_reply(message: str) -> ChatResponse:
    recommend_emergency = contains_emergency_keywords(message)

    # Get context only if we might use it
    context = retrieve_context(message) if (USE_CONTEXT or FAISS_FALLBACK) else []

    # Try Gemini (or your LLMClient)
    llm_answer = generate_via_llm(message, context if USE_CONTEXT else None)

    # Optional FAISS fallback (disabled by default)
    if (not llm_answer) and FAISS_FALLBACK and context:
        answer = None
        lower_msg = message.lower()

        for block in context:
            if "symptom" in lower_msg and "Common Symptoms:" in block:
                section = block.split("Common Symptoms:")[1].split("General Advice")[0].strip()
                answer = format_as_markdown("Common Symptoms", section)
                break
            elif ("advice" in lower_msg or "self-care" in lower_msg) and "General Advice" in block:
                section = block.split("General Advice")[1].split("Prevention")[0].strip()
                answer = format_as_markdown("General Advice / Self-care", section)
                break
            elif "prevention" in lower_msg and "Prevention Tips:" in block:
                section = block.split("Prevention Tips:")[1].split("When to Seek")[0].strip()
                answer = format_as_markdown("Prevention Tips", section)
                break
            elif ("when to seek" in lower_msg or "medical help" in lower_msg) and "When to Seek" in block:
                section = block.split("When to Seek")[1].split("Disclaimer")[0].strip()
                answer = format_as_markdown("When to Seek Medical Help", section)
                break
            elif "overview" in lower_msg and "Overview:" in block:
                section = block.split("Overview:")[1].split("Common Symptoms")[0].strip()
                answer = f"**Overview:**\n{section}"
                break

        if answer is None and any(x in lower_msg for x in ["tell me", "about", "what is", "details"]) and context:
            block = context[0]
            overview = block.split("Overview:")[1].split("Common Symptoms")[0].strip() if "Overview:" in block else ""
            symptoms = block.split("Common Symptoms:")[1].split("General Advice")[0].strip() if "Common Symptoms:" in block else ""
            advice = block.split("General Advice")[1].split("Prevention")[0].strip() if "General Advice" in block else ""
            parts = []
            if overview:  parts.append(f"**Overview:**\n{overview}")
            if symptoms:  parts.append(format_as_markdown("Common Symptoms", symptoms))
            if advice:    parts.append(format_as_markdown("General Advice / Self-care", advice))
            if parts:     answer = "\n\n".join(parts)

        if not answer and context:
            answer = "Here’s what I found:\n\n" + context[0]

        llm_answer = answer or llm_answer or "Sorry, I could not generate a response."

    # If still empty, return a friendly message
    if not llm_answer:
        llm_answer = "Sorry, I could not generate a response at this moment. Please try again."

    # No disclaimers; optional emergency notice
    reply = llm_answer
    if recommend_emergency and SHOW_EMERGENCY_NOTICE:
        reply += "\n\n⚠️ **Emergency Notice:** If symptoms are severe or worsening, please seek immediate medical help."

    return ChatResponse(reply=reply, emergency_recommended=recommend_emergency)

# ---------------- FastAPI Setup ----------------
app = FastAPI(title="AI Healthcare Chatbot Backend", version="0.4.0")

allow_origins_env = os.getenv("ALLOW_ORIGINS", "")
allow_origins = [o.strip() for o in allow_origins_env.split(",") if o.strip()] or [
    "http://localhost:3000",
    "http://127.0.0.1:3000",
    "http://localhost:5173",
    "http://127.0.0.1:5173",
    "http://localhost:5500",
    "http://127.0.0.1:5500",
    "http://localhost:5501",
    "http://127.0.0.1:5501",
]
app.add_middleware(
    CORSMiddleware,
    allow_origins=allow_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ---------------- Routes ----------------
@app.get("/health")
def health() -> dict:
    return {"status": "ok", "service": "ai-healthcare-chatbot", "version": "0.4.0"}

@app.post("/chat", response_model=ChatResponse)
def chat(request: ChatRequest) -> ChatResponse:
    return build_reply(request.message)

@app.post("/sos", response_model=SOSResponse)
def sos(req: SOSRequest) -> SOSResponse:
    ts = req.timestamp or datetime.utcnow().isoformat()
    return SOSResponse(status=f"SOS request received at {ts}")
