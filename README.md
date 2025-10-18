# 🧠 Hiya Voice AI Agent

This project is a **voice-enabled AI assistant** built for the **Hiya AI Engineer assignment**.  
It allows real-time, conversational interaction through **Twilio Voice** and **Groq’s Llama 3 model**,  
letting callers speak naturally while the AI responds contextually — just like a human support agent.

---

## 🌟 Features

✅ **Voice-based Conversational AI** using Twilio + Groq  
✅ **Speech-to-Text + LLM Response** via Groq API  
✅ **FastAPI Webhook Backend** with `/voice` endpoint  
✅ **Real-time Conversation Memory** per call  
✅ **SQLite Logging** of every interaction (for evaluation)  
✅ **Ngrok Tunnel** for public webhook testing  
✅ **Modular Code Structure** (clean, scalable, and easy to demo)

---

## 🧩 Project Structure

hiya-assignment/
│
├── app/
│ ├── main.py # FastAPI app & Twilio webhook
│ ├── store.py # SQLite logging (call history)
│ ├── init.py # package marker
│ ├── tools.py # placeholder (future tools)
│ ├── prompts.py # placeholder for prompt templates
│ ├── twilio_xml.py # placeholder for TwiML helpers
│ └── agent.py # placeholder for orchestration
│
├── .env.example # environment template (no real keys)
├── requirements.txt # dependencies
├── call_logs.db # SQLite log (optional)
└── README.md # this file


---

## ⚙️ Setup Instructions

### 1️⃣ Clone the repository

```bash
git clone https://github.com/AayushA10/hive-assignment.git
cd hive-assignment

2️⃣ Create and activate virtual environment
python3 -m venv venv
source venv/bin/activate   # Mac/Linux
venv\Scripts\activate      # Windows

3️⃣ Install dependencies
pip install -r requirements.txt

4️⃣ Create your .env file (do NOT commit this)
cp .env.example .env

Fill in your actual credentials:
GROQ_API_KEY=your_groq_api_key
TWILIO_ACCOUNT_SID=your_twilio_sid
TWILIO_AUTH_TOKEN=your_twilio_token
TWILIO_PHONE_NUMBER=+18888058261
PUBLIC_BASE_URL=https://<your-ngrok-url>.ngrok-free.app

🧠 Running the Project

1️⃣ Start the FastAPI server
uvicorn app.main:app --reload

2️⃣ Expose your server publicly with Ngrok
ngrok http 8000

Copy your public Ngrok URL and update your Twilio phone number’s Voice webhook:
https://<your-ngrok-url>.ngrok-free.app/voice

3️⃣ Make a test call (trigger via Twilio API)
curl -X POST https://api.twilio.com/2010-04-01/Accounts/<ACCOUNT_SID>/Calls.json \
--data-urlencode "From=<your_twilio_number>" \
--data-urlencode "To=<your_personal_number>" \
--data-urlencode "Url=https://<your-ngrok-url>.ngrok-free.app/voice" \
-u <ACCOUNT_SID>:<AUTH_TOKEN>

💾 Database Logging

All calls are logged automatically in a lightweight SQLite DB:
call_logs.db

You can inspect logs with:
from app.store import fetch_all
print(fetch_all())

Each record contains:

call_sid
from_number
to_number
user_message
ai_reply
timestamp

🧱 Architecture Overview
[Caller]
   ↓ (Voice)
[Twilio Phone Number]
   ↓ (Webhook)
[FastAPI App - /voice]
   ↓
[Groq API - Llama 3 Model]
   ↓
[AI Reply -> Twilio <Say>]
   ↓
[Spoken Response to Caller]
   ↳ Logged to SQLite (call_logs.db)

🧩 Example Flow

You call your Twilio number
Twilio hits your /voice endpoint
AI greets: “Hi, this is Hiya’s voice assistant. How may I help you?”
You speak — Twilio sends speech transcript to your FastAPI app
Groq generates a response using llama3-70b-8192
The AI replies over the call in natural speech
The conversation is logged to SQLite
