from config.medical_config import EMERGENCY_SYMPTOMS

def check_emergency_symptoms(text):
    """
    Check if user input contains any emergency symptoms.
    Returns True if emergency detected, else False.
    """
    text_lower = text.lower()
    for symptom in EMERGENCY_SYMPTOMS:
        if symptom in text_lower:
            return True
    return False 