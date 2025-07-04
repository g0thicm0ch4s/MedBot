from database.db import engine, Base, SessionLocal
from database.models import Condition, Remedy

def init_db():
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    # Check if already initialized
    if db.query(Condition).first():
        print("Database already initialized.")
        db.close()
        return
    # Sample conditions
    cold = Condition(name="Common Cold", description="A viral infection causing sneezing, sore throat, and runny nose.", severity_level="mild")
    migraine = Condition(name="Migraine", description="A severe headache often accompanied by nausea and sensitivity to light.", severity_level="moderate")
    db.add_all([cold, migraine])
    db.commit()
    # Sample remedies
    remedy1 = Remedy(condition_id=cold.id, remedy_text="Rest, drink plenty of fluids, and use saline nasal drops.", safety_notes="Consult a doctor if symptoms persist.")
    remedy2 = Remedy(condition_id=migraine.id, remedy_text="Rest in a dark, quiet room and use a cold compress on your forehead.", safety_notes="Seek medical attention for sudden, severe headaches.")
    db.add_all([remedy1, remedy2])
    db.commit()
    db.close()
    print("Database initialized with sample data.")

if __name__ == "__main__":
    init_db() 