# Gujarat DDCET Exam Preparation Application
### Offline-First Diploma-to-Degree Entrance Mastery Engine

A dedicated, offline-first learning system and question bank engine designed to help polytechnic diploma students prepare for Gujarat's **DDCET (Diploma to Degree Common Entrance Test)** in approximately two months, using a focused **~60-minute daily study routine**.

The primary objective is **mastery, revision, accuracy, and speed**—not merely answering high volumes of questions.

---

## Key Features & Architecture

- **100% Offline & Private**: Zero external cloud databases, zero paid APIs, zero telemetry, and zero LLM dependencies. Everything runs locally on your computer.
- **60-Minute Daily Mastery Structure**:
  - **5 Mins**: Review due spaced-repetition revisions.
  - **35 Mins**: Adaptive focused practice prioritizing high-impact syllabus areas.
  - **15 Mins**: Error and concept analysis with mistake reason categorization.
  - **5 Mins**: Progress and accuracy review to plan tomorrow's session.
- **Adaptive Priority Algorithm (Configurable & Explainable)**:
  $$\text{Priority} = 0.35 \times \text{Weakness} + 0.25 \times \text{Revision Urgency} + 0.20 \times \text{Syllabus Importance} + 0.10 \times \text{Neglect} + 0.10 \times \text{Speed Difficulty}$$
  - **Bayesian/Laplace Smoothing**: Prevents a single wrong answer from wildly swinging topic priority.
  - **Diagnostic Mode**: Unseen topics receive initial diagnostic questions rather than automatically being marked as weak.
  - **Anti-Monopoly Topic Cap**: Prevents a single topic from consuming the entire session.
  - **Transparent Explanations**: Tells the student *why* a topic was prioritized.
- **Spaced Repetition Revision System**:
  - Incorrect answers: scheduled for review tomorrow (1 day).
  - Correct low-confidence: 2 days.
  - Correct medium-confidence: 4 days.
  - Correct high-confidence: 7 days.
  - Consecutive correct answers: exponentially expand interval (capped to prevent premature retirement).
  - Mistake categories tracked: *Didn't understand concept*, *Forgot formula*, *Calculation error*, *Misread question*, *Guessed correctly*, *Ran out of time*, *Other*.
- **Full DDCET Mock Exam Simulation**:
  - Official Gujarat DDCET pattern: 100 questions, 90 minutes.
  - Standard marking scheme: **+1.0 mark** for correct, **-0.25 marks** negative penalty for incorrect (configurable in Settings).
  - Answers and explanations are **hidden** during mock exams and revealed only after submission.
  - Question palette navigation, auto-saving, and review flagging.
- **Import / Export System**:
  - Bulk import from **Excel (.xlsx)**, **CSV (.csv)**, and **JSON (.json)**.
  - 2-Stage workflow: Preview with exact duplicate hash detection, probable duplicate flagging (offline token similarity), and validation quarantine.
  - Pre-built downloadable templates with sample demonstration questions clearly labeled as sample data.
  - Export question bank, attempts history, and quarantined records.
- **Data Safety & Integrity**:
  - SQLite database stored securely in `data/ddcet.db` (outside static folder).
  - Safe live point-in-time database backups (`backups/`) and one-click restore.

---

## Technology Stack

- **Frontend**: HTML5, Responsive CSS3, Vanilla JavaScript (Fast, accessible, mobile-friendly, keyboard navigation: `A`/`B`/`C`/`D`, `1`-`4`, `Enter`/`N` for Next, `M` for Review).
- **Backend**: Python 3.10+, FastAPI, Uvicorn.
- **Database**: SQLite with WAL mode, foreign keys, and indexes.
- **Data Interchange**: OpenPyXL (Excel), CSV, JSON.

---

## Directory Structure

```
f:\Prep\
├── app.py                      # FastAPI application entry point
├── requirements.txt            # Dependencies list
├── run.bat                     # Windows one-click startup script
├── run.sh                      # Unix/Linux/macOS startup script
├── data\                       # Non-static database storage
│   └── ddcet.db                # SQLite database (auto-created on startup)
├── backups\                    # Live point-in-time database backups
├── database\
│   ├── schema.sql              # Versioned schema with optimized indexes
│   └── db.py                   # Connection manager, transactions, backup/restore
├── models\
│   └── schemas.py              # Pydantic validation models
├── routes\
│   ├── api_questions.py        # Question bank & syllabus hierarchy APIs
│   ├── api_practice.py         # Practice sessions, auto-save & scoring APIs
│   ├── api_revision.py         # Due revisions & mistake tracking APIs
│   ├── api_import_export.py    # Import preview/commit, templates, backups
│   ├── api_analytics.py        # 60-min daily dashboard & priorities APIs
│   └── api_settings.py         # Configurable marking & weights APIs
├── services\
│   ├── validation_service.py   # Strict MCQ validation & hierarchy mapping
│   ├── duplicate_service.py    # Exact text hash & offline probable duplicate detection
│   ├── import_export_service.py# Excel/CSV/JSON parser, exporter & template generator
│   ├── adaptive_service.py     # Rule-based priority score & diagnostic engine
│   ├── revision_service.py     # Spaced repetition scheduling & error tracking
│   ├── practice_service.py     # Session generation, timer & scoring engine
│   └── analytics_service.py    # Dashboard metrics & 5-point honest summary
├── templates\
│   └── index.html              # Responsive single-page application UI
├── static\
│   ├── css\style.css           # Clean, accessible stylesheet
│   └── js\app.js               # Vanilla JS application controller & keyboard handler
├── import_templates\           # Downloadable Excel, CSV, and JSON templates
└── tests\
    ├── test_all.py             # Automated unit & integration tests
    └── benchmark_scale.py      # Synthetic scale & performance benchmark
```

---

## Quick Start Guide

### 1. Requirements
Ensure Python 3.10+ is installed on your computer.

### 2. Start Application
On **Windows**, double-click:
```cmd
run.bat
```
Or run directly from PowerShell / Terminal:
```bash
python -m uvicorn app:app --host 127.0.0.1 --port 8000 --reload
```

### 3. Open in Browser
Visit in your web browser:
```
http://127.0.0.1:8000
```

---

## Question Data Format

Every question conforms to this exact structure:

```json
{
  "id": "MATH-CALC-001",
  "question": "What is the derivative of sin(2x) with respect to x?",
  "options": {
    "A": "2 * cos(2x)",
    "B": "-2 * cos(2x)",
    "C": "cos(2x)",
    "D": "2 * sin(2x)"
  },
  "correct_answer": "A",
  "explanation": "Using chain rule: d/dx[sin(u)] = cos(u) * du/dx = 2*cos(2x).",
  "subject": "Mathematics",
  "topic": "Calculus",
  "subtopic": "Derivatives",
  "difficulty": "easy",
  "source": {
    "name": "DDCET Official Syllabus Guide",
    "page": 12
  },
  "tags": ["calculus", "chain_rule"],
  "verified": true,
  "created_at": "2026-10-24T10:00:00"
}
```

---

## Mathematics & Markdown Format Support (.md)

The application includes built-in, offline **KaTeX** mathematical rendering and **GFM Markdown** parsing.
You can directly import math question banks in `.md` format!

### Example Markdown Question Bank (`.md` format):

```markdown
# Gujarat DDCET Mathematics Questions

---
## Question: MATH-CALC-001
**Subject**: Mathematics
**Topic**: Calculus
**Subtopic**: Definite Integrals
**Difficulty**: medium
**Verified**: true

Evaluate the definite integral:
$$\int_0^{\frac{\pi}{2}} \sin^2(x) \, dx$$

- (A) $\frac{\pi}{4}$
- (B) $\frac{\pi}{2}$
- (C) $1$
- (D) $0$

**Correct Answer**: A
**Explanation**:
Using the half-angle identity $\sin^2(x) = \frac{1 - \cos(2x)}{2}$:
$$\int_0^{\frac{\pi}{2}} \frac{1 - \cos(2x)}{2} \, dx = \left[ \frac{x}{2} - \frac{\sin(2x)}{4} \right]_0^{\frac{\pi}{2}} = \frac{\pi}{4}$$
```

### Supported Math Notation:
- **Inline math**: `$x^2 + y^2 = r^2$` or `\( \lim_{x \to 0} \frac{\sin x}{x} = 1 \)`
- **Display equations**: `$$\int_a^b f(x) dx$$` or `\[ A = \begin{pmatrix} a & b \\ c & d \end{pmatrix} \]`
- **Markdown syntax**: `**bold**`, `*italic*`, ```code blocks```, blockquotes, bullet lists, tables.
- **Offline rendering**: All KaTeX math fonts (`.woff2`) and scripts are bundled locally inside `static/libs/`. No internet connection is needed.

---

### Strict Validation Rules:
1. Exactly four options (`A`, `B`, `C`, `D`).
2. Correct answer must match one option key (`A`, `B`, `C`, or `D`).
3. Question text cannot be empty or whitespace only.
4. Subject, topic, and subtopic must be identifiable.
5. Difficulty must be one of `easy`, `medium`, or `hard`.
6. Verified questions **must** have a non-empty explanation.
7. Unverified questions are **never** silently marked as verified.
8. Invalid rows are quarantined into `quarantined_imports` with clear error diagnostics and can be exported for correction.

---

## Testing & Benchmarking

### Run Automated Test Suite
To run all 18 unit and integration tests:
```bash
pytest tests/test_all.py -v
```

### Run Synthetic Scale Benchmark
To test database indexing, deep pagination, and session selection speed on tens of thousands of synthetic questions:
```bash
python tests/benchmark_scale.py
```
*(All synthetic benchmark records are isolated in temporary storage and never mixed with real question banks).*

---

## Keyboard Shortcuts During Practice / Exam

- `A`, `B`, `C`, `D`: Select option A, B, C, or D.
- `1`, `2`, `3`, `4`: Alternative option selection.
- `Enter` or `N`: Move to next question.
- `P` or `←`: Move to previous question.
- `M`: Toggle "Mark for Review".

---

## License & Data Safety
- All user data and attempt histories remain strictly on your local machine.
- Backups are stored in `f:\Prep\backups\`. It is recommended to periodically copy backup files to external storage.
#   D D C E T - p r e p a r a t i o n  
 #   D D C E T - p r e p a r a t i o n  
 

---

## ⚔️ Battle Arena & Supabase Cloud Sync (Friends Competition)

Compete head-to-head with friends while maintaining a strict 100% offline-first architecture:

1. **Offline-First Architecture**:
   - All questions, attempts, and sessions remain stored in your local SQLite database (data/ddcet.db).
   - If there is no internet connection, your stats updates are stored safely in a local JSON queue (data/sync_queue.json).
   - When an internet connection is detected, pending stats are automatically pushed to your Supabase PostgreSQL cloud database.

2. **Head-to-Head Battle Duel**:
   - Enter any friend's email address to compare stats side-by-side.
   - **Core Metric Duels**: Total Score (+1.0 / -0.25), Accuracy %, MCQs Solved, Speed (s/q), Topics Mastered, Streak.
   - **Granular Topic-Wise MCQs Done / Not Done Battle Matrix**: Chapter-by-chapter table showing which MCQs each student has completed, accuracy, mastery level, and who leads each topic in the Gujarat DDCET syllabus.
   - **Competitors Leaderboard**: Live ranking of you and your friends sorted by total score.

3. **Supabase PostgreSQL Setup**:
   - Configure .env with:
     `env
     DATABASE_API_KEY=your_supabase_postgres_url_or_api_key
     `
   - Run the SQL script in database/supabase_schema.sql in your Supabase SQL Editor to create the required tables (ddcet_profiles, ddcet_user_stats, ddcet_friends) with RLS policies enabled.
