from database.db import SessionLocal
from database.models import Condition
import difflib

class SymptomAnalyzer:
    """
    Analyzes symptoms, maps to conditions, and assigns confidence scores.
    """
    def __init__(self):
        # Expanded synonym/phrase mapping for better symptom extraction
        self.synonym_map = {
            # Headache
            "my head is hurting": "headache",
            "head is hurting": "headache",
            "pain in my head": "headache",
            "head hurts": "headache",
            "head is aching": "headache",
            "my head aches": "headache",
            "pounding head": "headache",
            "throbbing head": "headache",
            "pressure in head": "headache",
            # Fatigue/Tiredness
            "body feels weak": "fatigue",
            "i feel weak": "fatigue",
            "feeling weak": "fatigue",
            "tired": "tiredness",
            "i am tired": "tiredness",
            "i feel tired": "tiredness",
            "no energy": "fatigue",
            "exhausted": "fatigue",
            "worn out": "fatigue",
            "drained": "fatigue",
            "lethargic": "fatigue",
            "my body is heavy": "fatigue",
            "my eyes feel heavy": "fatigue",
            # Fever
            "i have a fever": "fever",
            "running a temperature": "fever",
            "high temperature": "fever",
            "feeling hot": "fever",
            "chills and fever": "fever",
            # Sore Throat
            "my throat hurts": "sore throat",
            "throat is sore": "sore throat",
            "scratchy throat": "sore throat",
            "throat pain": "sore throat",
            "throat is dry": "sore throat",
            "throat is itchy": "sore throat",
            "my throat is dry and itchy": "sore throat",
            # Cough
            "i am coughing": "cough",
            "i have a cough": "cough",
            "persistent cough": "cough",
            "dry cough": "cough",
            "wet cough": "cough",
            # Runny Nose
            "my nose is runny": "runny nose",
            "runny nose": "runny nose",
            "stuffy nose": "congestion",
            "blocked nose": "congestion",
            "nasal congestion": "congestion",
            # Nausea
            "i feel nauseous": "nausea",
            "nauseous": "nausea",
            "i feel sick": "nausea",
            "queasy": "nausea",
            # Dizziness
            "i feel dizzy": "dizziness",
            "i am dizzy": "dizziness",
            "feeling dizzy": "dizziness",
            "dizzy": "dizziness",
            "lightheaded": "dizziness",
            "i am lightheaded": "dizziness",
            "my head is spinning": "dizziness",
            # Sweating
            "i am sweating": "sweating",
            "sweating profusely": "sweating",
            "i am sweating a lot": "sweating",
            "excessive sweating": "sweating",
            # Chest pain/heaviness
            "my chest hurts": "chest pain",
            "pain in chest": "chest pain",
            "tightness in chest": "chest pain",
            "my chest feels heavy": "chest pain",
            "pressure in chest": "chest pain",
            "chest discomfort": "chest pain",
            # Shortness of breath
            "hard to breathe": "shortness of breath",
            "breathless": "shortness of breath",
            "difficulty breathing": "shortness of breath",
            "i can't catch my breath": "shortness of breath",
            # Muscle aches
            "my muscles ache": "muscle aches",
            "muscles are sore": "muscle aches",
            "body aches": "muscle aches",
            # Joint pain
            "my joints hurt": "joint pain",
            "joints are stiff": "joint pain",
            "joint pain": "joint pain",
            # Chills
            "i have chills": "chills",
            "i am shivering": "chills",
            # Abdominal pain
            "my stomach hurts": "abdominal pain",
            "stomach is hurting": "abdominal pain",
            "stomach ache": "abdominal pain",
            "belly pain": "abdominal pain",
            # Rash
            "skin rash": "rash",
            "itchy skin": "rash",
            "red spots": "rash",
            # Loss of appetite
            "not hungry": "loss of appetite",
            "no appetite": "loss of appetite",
        }
        # List of canonical symptoms for fuzzy matching
        db = SessionLocal()
        self.known_symptoms = [s for s in set(self.synonym_map.values())]
        db.close()

    def extract_and_classify(self, text):
        """
        Extract symptoms and classify intent from user input.
        Returns (symptoms, intent)
        """
        text_lower = text.lower()
        found = set()
        # Synonym/phrase matching
        for phrase, canonical in self.synonym_map.items():
            if phrase in text_lower:
                found.add(canonical)
        # Fuzzy matching for single words (lower cutoff for more matches)
        words = text_lower.replace('.', '').replace(',', '').split()
        for word in words:
            close = difflib.get_close_matches(word, self.known_symptoms, n=1, cutoff=0.7)
            if close:
                found.add(close[0])
        # Fuzzy matching for 2- and 3-word phrases (lower cutoff)
        for n in [2, 3]:
            for i in range(len(words) - n + 1):
                phrase = ' '.join(words[i:i+n])
                close = difflib.get_close_matches(phrase, self.known_symptoms, n=1, cutoff=0.65)
                if close:
                    found.add(close[0])
        # Intent classification
        if any(word in text_lower for word in ["remedy", "home remedy", "treatment", "what can i do"]):
            intent = "remedy_request"
        elif any(word in text_lower for word in ["feedback", "suggestion", "complaint"]):
            intent = "feedback"
        else:
            intent = "symptom_report"
        return list(found), intent

    def analyze(self, symptoms):
        """
        Map symptoms to potential conditions and assign confidence scores.
        Args:
            symptoms (list): List of extracted symptoms
        Returns:
            list of dict: [{"condition": str, "confidence": float}]
        """
        db = SessionLocal()
        results = []
        for cond in db.query(Condition).all():
            score = 0
            cond_desc = (cond.description or '').lower()
            for symptom in symptoms:
                canonical = self.synonym_map.get(symptom, symptom)
                if canonical in cond_desc:
                    score += 1
            if score > 0:
                confidence = score / len(symptoms)
                results.append({"condition": cond.name, "confidence": round(confidence, 2)})
        db.close()
        # Sort by confidence descending
        results.sort(key=lambda x: x["confidence"], reverse=True)
        return results 