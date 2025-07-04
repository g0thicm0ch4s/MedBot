from database.db import SessionLocal
from database.models import Condition

def add_or_update_vertigo():
    db = SessionLocal()
    vertigo = db.query(Condition).filter(Condition.name == "Vertigo").first()
    description = "A sensation of spinning or dizziness, often caused by inner ear problems. Symptoms include dizziness, loss of balance, and nausea."
    if vertigo:
        vertigo.description = description
        vertigo.severity_level = "mild"
        print("Updated existing Vertigo condition.")
    else:
        vertigo = Condition(name="Vertigo", description=description, severity_level="mild")
        db.add(vertigo)
        print("Added new Vertigo condition.")
    db.commit()
    db.close()
    print("Done.")

if __name__ == "__main__":
    add_or_update_vertigo() 