from sqlalchemy import Column, Integer, String, Text, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from database.db import Base
import datetime

class Condition(Base):
    __tablename__ = "conditions"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    description = Column(Text)
    severity_level = Column(String)
    remedies = relationship("Remedy", back_populates="condition")

class Symptom(Base):
    __tablename__ = "symptoms"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    body_part = Column(String)
    severity_indicators = Column(Text)

class Remedy(Base):
    __tablename__ = "remedies"
    id = Column(Integer, primary_key=True, index=True)
    condition_id = Column(Integer, ForeignKey("conditions.id"))
    remedy_text = Column(Text, nullable=False)
    safety_notes = Column(Text)
    condition = relationship("Condition", back_populates="remedies")

class Conversation(Base):
    __tablename__ = "conversations"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String)
    messages = Column(Text)
    timestamp = Column(DateTime, default=datetime.datetime.utcnow)

class UserSession(Base):
    __tablename__ = "user_sessions"
    id = Column(String, primary_key=True, index=True)
    symptoms = Column(Text)
    conditions_suggested = Column(Text)
    canonicals = Column(Text)
    answers = Column(Text)
    followups = Column(Text)
    timestamp = Column(DateTime, default=datetime.datetime.utcnow) 