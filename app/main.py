import os
import xml.etree.ElementTree as ET
from fastapi import FastAPI, Request
from fastapi.responses import PlainTextResponse, JSONResponse
from dotenv import load_dotenv
from groq import Groq
from app.store import init_db, log_interaction, fetch_all

# =====================================
#  Load environment variables
# =====================================
load_dotenv()

GROQ_API_KEY = os.getenv("GROQ_API_KEY")
TWILIO_PHONE_NUMBER = os.getenv("TWILIO_PHONE_NUMBER")

# Initialize Groq client
groq_client = Groq(api_key=GROQ_API_KEY)

# Initialize FastAPI app
app = FastAPI(title="Hiya Voice AI Agent")

# Initialize DB once on startup
init_db()

# Simple in-memory conversation history
conversation_state = {}


# =====================================
#  Helper: build TwiML <Say> + <Gather> response
# =====================================
def make_twiml_response(prompt_text: str, action: str = "/voice") -> str:
    """Build a TwiML response for Twilio (Speak + Listen)."""
    twiml = f"""
    <?xml version="1.0" encoding="UTF-8"?>
    <Response>
        <Gather input="speech" timeout="5" speechTimeout="auto" action="{action}" method="POST">
            <Say>{prompt_text}</Say>
        </Gather>
        <Redirect>/fallback</Redirect>
    </Response>
    """
    return twiml.strip()


# =====================================
#  Helper: call Groq LLM (Llama3)
# =====================================
def get_ai_reply(prompt: str, call_sid: str) -> str:
    """Send caller message to Groq Llama3 model and get text reply."""
    try:
        history = conversation_state.get(call_sid, [])
        messages = [
            {
                "role": "system",
                "content": (
                    "You are Hiya's friendly voice assistant. "
                    "Speak naturally, answer briefly, and confirm caller details if relevant. "
                    "Avoid long paragraphs—keep replies under 3 short sentences."
                ),
            }
        ]
        messages += history
        messages.append({"role": "user", "content": prompt})

        chat_completion = groq_client.chat.completions.create(
            messages=messages,
            model=os.getenv("GROQ_MODEL", "llama3-70b-8192"),
            temperature=0.7,
            max_tokens=150,
        )

        reply = chat_completion.choices[0].message["content"].strip()

        # update memory
        history.append({"role": "user", "content": prompt})
        history.append({"role": "assistant", "content": reply})
        conversation_state[call_sid] = history

        return reply

    except Exception as e:
        print(f"[Groq Error]: {e}")
        return "Sorry, there was a technical issue. Please try again later."


# =====================================
#  Webhook: handle Twilio Voice POST
# =====================================
@app.post("/voice")
async def handle_voice(request: Request):
    """Twilio sends POST requests here during calls."""
    form = await request.form()
    call_sid = form.get("CallSid")
    speech_result = form.get("SpeechResult") or ""
    from_number = form.get("From")
    to_number = form.get("To")

    print(f"[Call] From: {from_number} → To: {to_number}")
    print(f"[Speech]: {speech_result}")

    # initial greeting (first time caller)
    if not speech_result:
        greet = (
            "Hello! This is Hiya's AI voice assistant. "
            "You can simply speak to me — please tell me your name and reason for calling."
        )
        twiml = make_twiml_response(greet)
        return PlainTextResponse(twiml, media_type="text/xml")

    # got user speech — call Groq for AI response
    reply_text = get_ai_reply(speech_result, call_sid)
    print(f"[AI Reply]: {reply_text}")

    # log interaction into SQLite
    try:
        log_interaction(call_sid, from_number, to_number, speech_result, reply_text)
    except Exception as e:
        print(f"[DB Log Error]: {e}")

    twiml = make_twiml_response(reply_text)
    return PlainTextResponse(twiml, media_type="text/xml")


# =====================================
#  Fallback route (for silence or timeouts)
# =====================================
@app.post("/fallback")
async def fallback():
    print("[Fallback triggered] No input or timeout.")
    twiml = make_twiml_response(
        "I'm sorry, I didn't catch that. Could you please repeat?", action="/voice"
    )
    return PlainTextResponse(twiml, media_type="text/xml")


# =====================================
#  View stored call logs (for demo)
# =====================================
@app.get("/logs")
async def get_logs():
    """View all logged calls + conversations."""
    data = fetch_all()
    formatted = [
        {
            "id": row[0],
            "call_sid": row[1],
            "from": row[2],
            "to": row[3],
            "user_message": row[4],
            "ai_reply": row[5],
            "timestamp": row[6],
        }
        for row in data
    ]
    return JSONResponse(formatted)


# =====================================
#  Root health check
# =====================================
@app.get("/")
async def root():
    return {"message": "Hiya Voice AI Agent is running!"}
