-- DDCET Gujarat Exam Preparation Database Schema
-- Version 1.0

PRAGMA foreign_keys = ON;

CREATE TABLE IF NOT EXISTS schema_version (
    version INTEGER PRIMARY KEY,
    applied_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS settings (
    key TEXT PRIMARY KEY,
    value TEXT NOT NULL,
    description TEXT
);

CREATE TABLE IF NOT EXISTS subjects (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL UNIQUE COLLATE NOCASE,
    syllabus_weight REAL DEFAULT 1.0
);

CREATE TABLE IF NOT EXISTS topics (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    subject_id INTEGER NOT NULL REFERENCES subjects(id) ON DELETE CASCADE,
    name TEXT NOT NULL COLLATE NOCASE,
    syllabus_weight REAL DEFAULT 1.0,
    UNIQUE(subject_id, name)
);

CREATE TABLE IF NOT EXISTS subtopics (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    topic_id INTEGER NOT NULL REFERENCES topics(id) ON DELETE CASCADE,
    name TEXT NOT NULL COLLATE NOCASE,
    UNIQUE(topic_id, name)
);

CREATE TABLE IF NOT EXISTS questions (
    id TEXT PRIMARY KEY,
    question_text TEXT NOT NULL,
    option_a TEXT NOT NULL,
    option_b TEXT NOT NULL,
    option_c TEXT NOT NULL,
    option_d TEXT NOT NULL,
    correct_answer TEXT NOT NULL CHECK(correct_answer IN ('A', 'B', 'C', 'D')),
    explanation TEXT,
    subject_id INTEGER NOT NULL REFERENCES subjects(id),
    topic_id INTEGER NOT NULL REFERENCES topics(id),
    subtopic_id INTEGER NOT NULL REFERENCES subtopics(id),
    difficulty TEXT NOT NULL CHECK(difficulty IN ('easy', 'medium', 'hard')),
    source_json TEXT DEFAULT '{}',
    tags_json TEXT DEFAULT '[]',
    verified INTEGER NOT NULL DEFAULT 0 CHECK(verified IN (0, 1)),
    text_hash TEXT NOT NULL,
    created_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS sessions (
    id TEXT PRIMARY KEY,
    session_type TEXT NOT NULL, -- 'daily_mixed', 'subject', 'topic', 'subtopic', 'weak_topic', 'revision_only', 'timed', 'full_mock'
    target_subject_id INTEGER REFERENCES subjects(id),
    target_topic_id INTEGER REFERENCES topics(id),
    target_subtopic_id INTEGER REFERENCES subtopics(id),
    total_questions INTEGER NOT NULL,
    answered_questions INTEGER DEFAULT 0,
    correct_count INTEGER DEFAULT 0,
    incorrect_count INTEGER DEFAULT 0,
    unanswered_count INTEGER DEFAULT 0,
    total_score REAL DEFAULT 0.0,
    accuracy_pct REAL DEFAULT 0.0,
    time_taken_seconds INTEGER DEFAULT 0,
    time_limit_seconds INTEGER DEFAULT 0,
    is_completed INTEGER DEFAULT 0 CHECK(is_completed IN (0, 1)),
    started_at TEXT NOT NULL,
    completed_at TEXT
);

CREATE TABLE IF NOT EXISTS session_questions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    session_id TEXT NOT NULL REFERENCES sessions(id) ON DELETE CASCADE,
    question_id TEXT NOT NULL REFERENCES questions(id) ON DELETE CASCADE,
    order_index INTEGER NOT NULL,
    selected_option TEXT CHECK(selected_option IS NULL OR selected_option IN ('A', 'B', 'C', 'D')),
    is_marked_for_review INTEGER DEFAULT 0 CHECK(is_marked_for_review IN (0, 1)),
    is_answered INTEGER DEFAULT 0 CHECK(is_answered IN (0, 1)),
    is_correct INTEGER CHECK(is_correct IS NULL OR is_correct IN (0, 1)),
    time_spent_seconds INTEGER DEFAULT 0,
    confidence TEXT CHECK(confidence IS NULL OR confidence IN ('low', 'medium', 'high')),
    mistake_category TEXT CHECK(mistake_category IS NULL OR mistake_category IN ('concept', 'formula', 'calculation', 'misread', 'guess', 'time', 'other')),
    UNIQUE(session_id, order_index)
);

CREATE TABLE IF NOT EXISTS attempts (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    question_id TEXT NOT NULL REFERENCES questions(id) ON DELETE CASCADE,
    session_id TEXT NOT NULL REFERENCES sessions(id) ON DELETE CASCADE,
    selected_option TEXT CHECK(selected_option IS NULL OR selected_option IN ('A', 'B', 'C', 'D')),
    is_correct INTEGER NOT NULL CHECK(is_correct IN (0, 1)),
    time_spent_seconds INTEGER NOT NULL DEFAULT 0,
    confidence TEXT CHECK(confidence IS NULL OR confidence IN ('low', 'medium', 'high')),
    mistake_category TEXT CHECK(mistake_category IS NULL OR mistake_category IN ('concept', 'formula', 'calculation', 'misread', 'guess', 'time', 'other')),
    attempted_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS revision_schedules (
    question_id TEXT PRIMARY KEY REFERENCES questions(id) ON DELETE CASCADE,
    last_attempt_at TEXT NOT NULL,
    next_due_date TEXT NOT NULL, -- ISO Date YYYY-MM-DD
    current_interval_days INTEGER NOT NULL DEFAULT 1,
    consecutive_correct INTEGER NOT NULL DEFAULT 0,
    consecutive_incorrect INTEGER NOT NULL DEFAULT 0,
    total_attempts INTEGER NOT NULL DEFAULT 1,
    difficulty_rating TEXT NOT NULL DEFAULT 'medium',
    last_confidence TEXT,
    last_mistake_category TEXT
);

CREATE TABLE IF NOT EXISTS quarantined_imports (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    batch_id TEXT NOT NULL,
    raw_data_json TEXT NOT NULL,
    reason TEXT NOT NULL,
    quarantined_at TEXT NOT NULL
);

-- Optimized Performance Indexes
CREATE INDEX IF NOT EXISTS idx_questions_subject_topic ON questions(subject_id, topic_id);
CREATE INDEX IF NOT EXISTS idx_questions_subtopic ON questions(subtopic_id);
CREATE INDEX IF NOT EXISTS idx_questions_difficulty ON questions(difficulty);
CREATE INDEX IF NOT EXISTS idx_questions_verified ON questions(verified);
CREATE INDEX IF NOT EXISTS idx_questions_text_hash ON questions(text_hash);
CREATE INDEX IF NOT EXISTS idx_attempts_question ON attempts(question_id, attempted_at);
CREATE INDEX IF NOT EXISTS idx_attempts_date ON attempts(attempted_at);
CREATE INDEX IF NOT EXISTS idx_revision_due ON revision_schedules(next_due_date);
CREATE INDEX IF NOT EXISTS idx_session_questions_lookup ON session_questions(session_id, order_index);
CREATE INDEX IF NOT EXISTS idx_sessions_completed ON sessions(is_completed, started_at);
