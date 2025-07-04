from fastapi import FastAPI, Request, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from sqlalchemy.orm import Session
from database.db import get_db
from database.models import Condition, Remedy, Conversation, UserSession
import datetime
from models.symptom_analyzer import SymptomAnalyzer
from utils.safety_checker import check_emergency_symptoms
from config.medical_config import DISCLAIMER
import json

app = FastAPI()

# CORS setup
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class ChatRequest(BaseModel):
    message: str
    user_id: str = None

analyzer = SymptomAnalyzer()

@app.get("/health")
def health_check():
    return {"status": "ok"}

# Helper: get or create user session
def get_or_create_session(db, user_id):
    session = db.query(UserSession).filter(UserSession.id == user_id).first()
    if not session:
        session = UserSession(
            id=user_id,
            symptoms="[]",
            conditions_suggested="[]",
            canonicals="[]",
            answers="{}",
            followups="[]"
        )
        db.add(session)
        db.commit()
    return session

# Helper: get follow-up questions for a symptom
FOLLOWUP_TEMPLATES = {
    "sore throat": [
        "How long have you had your sore throat?",
        "On a scale of 1-10, how severe is your sore throat?",
        "Are you also experiencing any cough or fever?"
    ],
    "headache": [
        "How long have you had your headache?",
        "On a scale of 1-10, how severe is your headache?",
        "Are you also experiencing any nausea or vision changes?"
    ],
    "eyes": [
        "How long have you had your eye symptoms?",
        "Are your eyes red, itchy, or sensitive to light?",
        "Do you have any vision changes?"
    ],
    "chest pain": [
        "How long have you had your chest pain?",
        "On a scale of 1-10, how severe is your chest pain?",
        "Are you also experiencing shortness of breath or sweating?"
    ],
    "fatigue": [
        "How long have you been feeling fatigued?",
        "Is your fatigue constant or does it come and go?",
        "Are you also experiencing any fever or muscle aches?"
    ],
    # Add more as needed
}

@app.post("/chat")
async def chat_endpoint(request: ChatRequest, db: Session = Depends(get_db)):
    user_message = request.message
    user_id = request.user_id or "anonymous"
    print('DEBUG: user_id:', user_id)
    session = get_or_create_session(db, user_id)
    print('DEBUG: loaded session:', session.__dict__)
    # Load session state
    session_symptoms = json.loads(session.symptoms) if session.symptoms else []
    canonicals_raw = session.canonicals if session.canonicals else '[]'
    session_canonicals = json.loads(canonicals_raw)
    answers_raw = session.answers if session.answers else '{}'
    followups_raw = session.followups if session.followups else '[]'
    print('DEBUG: DB session.answers:', session.answers)
    print('DEBUG: DB session.followups:', session.followups)
    session_answers = json.loads(answers_raw)
    session_followups = json.loads(followups_raw)

    # Reset session if user requests
    if user_message.strip().lower() in ["reset", "start over", "clear"]:
        session.symptoms = "[]"
        session.canonicals = "[]"
        session.answers = "{}"
        session.followups = "[]"
        db.commit()
        return {
            "response": "Hello! I'm MedBot, your preliminary health assistant. How are you feeling today? Please describe your symptoms.",
            "disclaimer": DISCLAIMER
        }

    # If there are pending follow-ups, treat this message as an answer
    if 'current_followup' in session_answers:
        last_q = session_answers['current_followup']
        session_answers[last_q] = user_message
        del session_answers['current_followup']
        session.answers = json.dumps(session_answers)
        db.commit()
        if session_followups:
            # Ask the next follow-up
            next_q = session_followups.pop(0)
            session_answers['current_followup'] = next_q
            session.followups = json.dumps(session_followups)
            session.answers = json.dumps(session_answers)
            db.commit()
            response_text = next_q + "\n\n" + DISCLAIMER
            conv = Conversation(user_id=user_id, messages=f"USER: {user_message}\nBOT: {response_text}")
            db.add(conv)
            db.commit()
            return {
                "response": response_text,
                "disclaimer": DISCLAIMER
            }
        # If no follow-ups left, fall through to diagnosis below

    # Track if new symptoms were added
    symptoms, intent = analyzer.extract_and_classify(user_message)
    canonicals = [analyzer.synonym_map.get(s, s) for s in symptoms]
    is_emergency = check_emergency_symptoms(user_message)
    new_symptom_added = False
    if canonicals:
        for s in canonicals:
            if s not in session_canonicals:
                session_canonicals.append(s)
                new_symptom_added = True
        session.canonicals = json.dumps(session_canonicals)
        db.commit()

    # Only generate follow-ups if a new symptom was added
    if new_symptom_added:
        # Use the most recently added canonical symptom for follow-ups
        main_canonical = canonicals[-1] if canonicals else session_canonicals[-1]
        if main_canonical in FOLLOWUP_TEMPLATES:
            session_followups = FOLLOWUP_TEMPLATES[main_canonical][:]
        else:
            session_followups = [
                f"How long have you had your {main_canonical}?",
                f"On a scale of 1-10, how severe is your {main_canonical}?"
            ]
        session.followups = json.dumps(session_followups)
        db.commit()
        # Ask the first follow-up
        next_q = session_followups.pop(0)
        session_answers['current_followup'] = next_q
        session.followups = json.dumps(session_followups)
        session.answers = json.dumps(session_answers)
        db.commit()
        response_text = next_q + "\n\n" + DISCLAIMER
        conv = Conversation(user_id=user_id, messages=f"USER: {user_message}\nBOT: {response_text}")
        db.add(conv)
        db.commit()
        return {
            "response": response_text,
            "disclaimer": DISCLAIMER
        }

    # If no follow-ups and no new symptoms, proceed to diagnosis and summary
    print('DEBUG: session_canonicals:', session_canonicals)
    print('DEBUG: session_answers:', session_answers)
    analysis = analyzer.analyze(session_canonicals) if session_canonicals else []
    print('DEBUG: analysis:', analysis)
    # Remedy suggestion (for top condition)
    remedy_text = None
    safety_notes = None
    if analysis:
        top_condition = db.query(Condition).filter(Condition.name == analysis[0]["condition"]).first()
        if top_condition:
            remedy = db.query(Remedy).filter(Remedy.condition_id == top_condition.id).first()
            if remedy:
                remedy_text = remedy.remedy_text
                safety_notes = remedy.safety_notes
    # Compose personalized summary
    summary_lines = []
    if session_canonicals:
        summary_lines.append(f"You reported: {', '.join(session_canonicals)}.")
    # Add follow-up answers to summary
    duration = None
    severity = None
    for q, a in session_answers.items():
        if "how long" in q.lower():
            duration = a
            summary_lines.append(f"Duration: {a}.")
        if "severe" in q.lower():
            severity = a
            summary_lines.append(f"Severity: {a}/10.")
    # Add warnings if needed
    warning = ""
    try:
        if severity and int(severity) >= 8:
            warning = "Your symptoms are quite severe. Please consider seeking medical attention promptly."
        if duration and any(word in duration.lower() for word in ["week", "10 days", "long", "persistent"]):
            warning = "Your symptoms have lasted a long time. Please consult a healthcare provider."
    except Exception:
        pass
    if warning:
        summary_lines.append(f"⚠️ {warning}")
    # Add condition/remedy
    if is_emergency:
        summary_lines.append("⚠️ EMERGENCY: Your symptoms may indicate a serious condition. Please seek immediate medical attention or call your local emergency number.")
    elif intent == "remedy_request" and remedy_text:
        summary_lines.append(f"Possible condition: {analysis[0]['condition']}")
        summary_lines.append(f"Home remedy: {remedy_text}")
        summary_lines.append(f"Safety notes: {safety_notes}")
    elif analysis:
        summary_lines.append(f"Possible condition: {analysis[0]['condition']}")
        if remedy_text:
            summary_lines.append(f"Home remedy: {remedy_text}")
            summary_lines.append(f"Safety notes: {safety_notes}")
    else:
        summary_lines.append("I'm sorry, I couldn't identify your symptoms. Please provide more details.")
    summary_lines.append("")
    summary_lines.append(DISCLAIMER)
    response_text = "\n".join(summary_lines)
    # Log conversation
    conv = Conversation(user_id=user_id, messages=f"USER: {user_message}\nBOT: {response_text}")
    db.add(conv)
    db.commit()
    return {
        "response": response_text,
        "disclaimer": DISCLAIMER
    }

@app.get("/conditions")
def get_conditions(db: Session = Depends(get_db)):
    conditions = db.query(Condition).all()
    return [{"id": c.id, "name": c.name, "description": c.description, "severity_level": c.severity_level} for c in conditions]

@app.get("/remedies/{condition_id}")
def get_remedies(condition_id: int, db: Session = Depends(get_db)):
    remedies = db.query(Remedy).filter(Remedy.condition_id == condition_id).all()
    return [{"id": r.id, "remedy_text": r.remedy_text, "safety_notes": r.safety_notes} for r in remedies]

class FeedbackRequest(BaseModel):
    message: str
    user_id: str = None

@app.post("/feedback")
def submit_feedback(request: FeedbackRequest, db: Session = Depends(get_db)):
    conv = Conversation(user_id=request.user_id or "feedback", messages=f"FEEDBACK: {request.message}")
    db.add(conv)
    db.commit()
    return {"status": "success"} 