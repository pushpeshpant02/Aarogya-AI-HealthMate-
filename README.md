# 🩺 HealthMate – Aarogya AI Chatbot

HealthMate is a simple full-stack AI healthcare assistant.  
It combines a **FastAPI backend** with a **minimal dark frontend** (HTML, CSS, JS).  

The chatbot provides **general health guidance** and highlights possible **emergency symptoms** like chest pain or breathing difficulty.

⚠️ **Note:** This is *not* a replacement for a doctor. Always seek professional medical help in real emergencies.

---

## ✨ What’s Inside
- 🤖 **Chatbot API** powered by FastAPI + Uvicorn  
- 💬 **Conversational UI** with dark theme and larger input box  
- 🚨 **Emergency detection** for critical symptoms  
- 🎨 **Lightweight frontend** (HTML, CSS, JS only)  

---

## 🧭 Project Structure
healthmate/
├── backend/
│ └── main.py # FastAPI app (entry point)
├── frontend/
│ ├── index.html # Chat page
│ ├── login.html # Login page
│ ├── styles.css # Dark theme styles
│ └── config.js # API base URL config
├── requirements.txt # Python dependencies
└── README.md

## 🚀 Getting Started (Local)

### 1️⃣ Backend (FastAPI)
```bash
cd backend
python3 -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r ../requirements.txt
uvicorn main:app --host 127.0.0.1 --port 8000 --reload
Health Check → http://127.0.0.1:8000/health


Frontend (Static Server)
cd frontend
python3 -m http.server 5500

Frontend Config
const API_BASE = 'http://127.0.0.1:8000';
window.API_BASE = API_BASE;
