from database.db import SessionLocal
from database.models import Symptom

def populate_symptoms():
    common_symptoms = [
        ("headache", "head", "severe, throbbing, persistent"),
        ("tiredness", "general", "fatigue, exhaustion"),
        ("fatigue", "general", "weakness, low energy"),
        ("fever", "general", "high temperature, chills"),
        ("cough", "chest", "dry, productive, persistent"),
        ("sore throat", "throat", "pain, scratchy, irritation"),
        ("runny nose", "nose", "congestion, discharge"),
        ("nausea", "stomach", "queasy, urge to vomit"),
        ("vomiting", "stomach", "throwing up"),
        ("diarrhea", "stomach", "loose stools"),
        ("abdominal pain", "stomach", "cramps, discomfort"),
        ("chest pain", "chest", "pressure, tightness"),
        ("shortness of breath", "chest", "difficulty breathing"),
        ("dizziness", "head", "lightheaded, fainting"),
        ("muscle aches", "muscles", "soreness, pain"),
        ("joint pain", "joints", "stiffness, swelling"),
        ("rash", "skin", "redness, bumps, irritation"),
        ("sensitivity to light", "head", "photophobia"),
        ("loss of appetite", "general", "not hungry"),
        ("chills", "general", "shivering, cold"),
        ("congestion", "nose", "blocked nose"),
        ("sneezing", "nose", "frequent sneezing"),
        ("itchy eyes", "eyes", "irritation, redness"),
        ("blood in stool", "stomach", "rectal bleeding"),
        ("blood in urine", "urinary", "hematuria"),
        ("loss of consciousness", "head", "fainting, blackout"),
        ("severe allergic reaction", "general", "anaphylaxis, swelling, hives"),
    ]
    db = SessionLocal()
    for name, body_part, severity in common_symptoms:
        exists = db.query(Symptom).filter(Symptom.name == name).first()
        if not exists:
            db.add(Symptom(name=name, body_part=body_part, severity_indicators=severity))
    db.commit()
    db.close()
    print("Symptoms table populated with common symptoms.")

if __name__ == "__main__":
    populate_symptoms() 