# MedBot

MedBot is an AI-powered medical chatbot designed to provide preliminary health assistance, symptom analysis, and home remedy suggestions. Built with a FastAPI backend and a React frontend, MedBot leverages rule-based NLP and a medical knowledge base to deliver safe, user-friendly, and informative conversations.

## Features
- **Conversational Symptom Checker**: Users can describe their symptoms in natural language and receive preliminary analysis.
- **Follow-up Questions**: MedBot asks context-aware follow-up questions to refine its understanding.
- **Home Remedies & Safety Notes**: Suggests home remedies and provides important safety disclaimers.
- **Red Flag Detection**: Warns users if symptoms may indicate a medical emergency.
- **Session Management**: Remembers symptoms and answers during a session; supports session reset.
- **Age-Appropriate & Personalized**: Adapts follow-ups and advice based on user input.
- **Conversation Logging**: Stores chat history for feedback and improvement.

## Tech Stack
- **Backend**: FastAPI, SQLAlchemy, SQLite (or PostgreSQL)
- **Frontend**: React
- **NLP**: Rule-based symptom extraction, synonym/fuzzy matching
- **Database**: Medical conditions, symptoms, remedies, and user sessions

## Setup Instructions

### 1. Clone the Repository
```sh
git clone https://github.com/g0thicm0ch4s/MedBot.git
cd MedBot
```

### 2. Backend Setup
```sh
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
PYTHONPATH=. python3 database/init_db.py
uvicorn app:app --reload
```

### 3. Frontend Setup
```sh
cd frontend
npm install
npm start
```

### 4. Usage
- Open the frontend in your browser (usually at http://localhost:3000)
- Start chatting with MedBot!
- Type `reset` to clear your session and start over.

## Contributing
Pull requests are welcome! For major changes, please open an issue first to discuss what you would like to change.

## Disclaimer
MedBot provides general information only and cannot replace professional medical advice. For emergencies, call your local emergency number immediately.

---

## Project Description (for GitHub)

> **MedBot is an AI-powered medical chatbot that provides preliminary health guidance, symptom analysis, and home remedy suggestions. Built with FastAPI and React, MedBot offers a safe, conversational, and user-friendly experience for anyone seeking quick health information.** 