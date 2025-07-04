-- Table: conditions
CREATE TABLE IF NOT EXISTS conditions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    description TEXT,
    severity_level TEXT
);

-- Table: symptoms
CREATE TABLE IF NOT EXISTS symptoms (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    body_part TEXT,
    severity_indicators TEXT
);

-- Table: remedies
CREATE TABLE IF NOT EXISTS remedies (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    condition_id INTEGER,
    remedy_text TEXT NOT NULL,
    safety_notes TEXT,
    FOREIGN KEY (condition_id) REFERENCES conditions(id)
);

-- Table: conversations
CREATE TABLE IF NOT EXISTS conversations (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id TEXT,
    messages TEXT,
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- Table: user_sessions
CREATE TABLE IF NOT EXISTS user_sessions (
    id TEXT PRIMARY KEY,
    symptoms TEXT,
    conditions_suggested TEXT,
    canonicals TEXT,
    answers TEXT,
    followups TEXT,
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
); 