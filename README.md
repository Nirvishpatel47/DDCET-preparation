# Gujarat DDCET Exam Preparation Application
### Offline-First Diploma-to-Degree Entrance Mastery Engine

A dedicated, offline-first learning system and question bank engine designed to help polytechnic diploma students prepare for Gujarat's **DDCET (Diploma to Degree Common Entrance Test)** in approximately two months, using a focused **~60-minute daily study routine**.

The primary objective is **mastery, revision, accuracy, and speed**—not merely answering high volumes of questions.

---

## 🗑️ Data Reset & Clean-Slate Guide (How to Remove Everything)

If you need to reset questions, wipe your study history, or start from a completely clean slate, choose one of the options below:

### 1. Complete Nuclear Reset (Wipe Everything)
This completely deletes your local SQLite database, attempt history, practice sessions, revision schedules, backups, and pending cloud sync queues. The next time you launch the app, it will initialize a fresh, clean database automatically.

**PowerShell (Windows):**
```powershell
Remove-Item -Recurse -Force "$env:USERPROFILE\.ddcet-preparation"
```

**Python (Cross-Platform):**
```bash
python -c "import shutil, os; p = os.path.expanduser('~/.ddcet-preparation'); shutil.rmtree(p, ignore_errors=True); print('All local user data, progress, and database completely removed.')"
```

---

### 2. Delete All Questions Only (Preserve Account & Settings)
If you want to clear the entire question bank from the database while keeping your user profile and application settings intact:

```bash
python -c "from database.db import get_db; conn = get_db().__enter__(); conn.execute('PRAGMA foreign_keys = ON;'); conn.execute('DELETE FROM questions;'); conn.commit(); print('All questions deleted successfully.')"
```

---

### 3. Prevent Master Questions from Auto-Reseeding
By default, the application seeds questions from `data/ddcet_1500_master.json` when the database is empty. If you want the question bank to **stay completely empty** (for example, to import your own custom question files from scratch without default questions):

**PowerShell (Windows):**
```powershell
Set-Content -Path "data\ddcet_1500_master.json" -Value "[]"
```

**Python (Cross-Platform):**
```bash
python -c "open('data/ddcet_1500_master.json', 'w', encoding='utf-8').write('[]'); print('Master bank cleared.')"
```

---

## 🎨 Dual Theme System (Light & Dark)

The application features two distraction-free, publication-grade themes designed for long, comfortable study sessions:

| Theme | Background | Surface / Cards | Primary Accent | Text Primary | Border |
|---|---|---|---|---|---|
| **Light (Warm Paper)** | `#F6F5F0` | `#FFFFFF` | `#789681` (Sage Green) | `#29372F` | `#E7E6DF` |
| **Dark (Deep Charcoal)** | `#171B19` | `#222925` | `#8EAB95` (Muted Sage) | `#E5EAE5` | `#343D37` |

- **Three Modes**: `Light`, `Dark`, and `Auto (System)` matching your operating system preference.
- **Zero FOUT**: Theme preference is loaded synchronously in the `<head>` to prevent flashes of unstyled content.
- **Smooth 180ms Transitions**: Subtle surface transitions that respect `prefers-reduced-motion`.

---

## ⚡ 4 Difficulty Levels

Questions are strictly categorized into four standardized difficulty tiers, each with dedicated high-contrast semantic badges:

| Level | Light Badge | Dark Badge | Description |
|---|---|---|---|
| **Easy** | Soft Green (`#E5F0E6`) | Dark Forest (`#263D2E`) | Direct recall, basic formulas, standard textbook definitions |
| **Moderate** | Soft Amber (`#F4EBD9`) | Muted Bronze (`#403725`) | Multi-step calculation, conceptual application, standard DDCET level |
| **Hard** | Soft Coral (`#F5E8E5`) | Deep Rose (`#442B2A`) | Complex integrations, tricky edge cases, trap options |
| **Stretch** | Soft Purple (`#F0EAF8`) | Deep Lavender (`#322543`) | Advanced competitive rank-decider questions |

*Note: Any legacy datasets referencing `medium` are automatically normalized to `moderate` on import and migration.*

---

## 🔒 User Data Protection & Architecture

```
User Computer
├── F:\Prep\                          # Public Codebase (tracked in Git)
│   ├── app.py                       # FastAPI application entry point
│   ├── data\
│   │   └── ddcet_1500_master.json   # Public seed questions
│   ├── database\
│   │   ├── db.py                    # Connection manager, transactions & migrations
│   │   └── schema.sql               # SQLite schema with WAL mode & indexes
│   ├── models\schemas.py            # Pydantic models & validation rules
│   ├── routes\                      # Modular API routers
│   ├── services\                    # Business logic (practice, revision, analytics)
│   ├── static\                      # CSS, Vanilla JS, and KaTeX vendor assets
│   └── templates\index.html         # Responsive SPA interface
│
└── C:\Users\<Username>\.ddcet-preparation\  # Isolated User Data (Never in Git)
    ├── data\
    │   ├── ddcet_user.db            # Persistent private SQLite database
    │   └── sync_queue.json          # Offline queue for Supabase cloud sync
    └── backups\                     # Point-in-time database backups
```

- **Git-Immune Progress**: User attempts, personal scores, and progress records reside strictly in `~/.ddcet-preparation/`. Pulling new updates from GitHub will **never** overwrite or delete your study history.
- **Zero-Loss Auto-Migration**: Database schema updates are managed through version-controlled migrations (`Migration 1` through `Migration 4`) preserving existing attempts.

---

## 🎯 Practice Workflow & DDCET Rules

1. **Strict 4-Step Sequence**:
   $$\text{Select Option} \longrightarrow \text{Check Answer} \longrightarrow \text{View Feedback \& Explanation} \longrightarrow \text{Next Question}$$
   - Selecting an option never reveals correctness before clicking **Check Answer**.
   - Answers and options are locked immediately upon checking.
   - Detailed mathematical explanation and mistake reason taggers appear instantly.
2. **Anti-Memorization Randomization**:
   - Question ordering is randomized across sessions.
   - Option choices (A, B, C, D) are shuffled dynamically with correct answer keys automatically remapped so students cannot memorize by letter position.
3. **Official Marking Scheme**:
   - **+1.0 mark** for correct answers.
   - **-0.25 marks** negative penalty for incorrect answers (configurable in Settings).
   - In **Full Mock Exams** (100 questions, 90 minutes), all feedback and explanations remain hidden until the entire exam is submitted.

---

## ⚔️ Battle Arena & Supabase Cloud Sync

Compete head-to-head with friends while preserving an uncompromising offline-first model:

1. **100% Offline-First**:
   - All questions, attempts, and sessions operate locally from SQLite.
   - If there is no internet connection, stats are queued in `sync_queue.json`.
   - Once online, stats push automatically to Supabase.
2. **Head-to-Head Duels**:
   - Enter a friend's email address to inspect a side-by-side metric comparison: Total Score, Accuracy %, MCQs Solved, Speed (s/q), and Streak.
3. **Topic-Wise MCQs Done Matrix**:
   - Chapter-by-chapter matrix showing which syllabus topics each student has completed and mastered.
4. **Supabase Cloud Setup**:
   - Add your connection URL in `.env`:
     ```env
     DATABASE_API_KEY=your_supabase_postgres_url
     ```
   - Run the script in `database/supabase_schema.sql` inside your Supabase SQL Editor.

---

## 📐 Mathematical Typesetting & Markdown Format (.md)

The application bundles offline **KaTeX** math rendering and **GFM Markdown** parsing.

### Example Markdown Question Format:

```markdown
# Gujarat DDCET Mathematics Questions

---
## Question: MATH-CALC-001
**Subject**: Mathematics
**Topic**: Calculus
**Subtopic**: Definite Integrals
**Difficulty**: moderate
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
- **Offline fonts**: KaTeX fonts are locally served; no CDN connection is required.

---

## 🚀 Quick Start Guide

### 1. Requirements
- Python 3.10+ installed.

### 2. Launch Application
On **Windows**, double-click:
```cmd
run.bat
```
Or start via terminal / PowerShell:
```powershell
python -m uvicorn app:app --host 127.0.0.1 --port 8000 --reload
```

### 3. Open in Browser
Visit in your web browser:
```
http://127.0.0.1:8000
```

---

## ⌨️ Practice Keyboard Shortcuts

- `A`, `B`, `C`, `D` or `1`, `2`, `3`, `4`: Select option.
- `Enter`: Check answer / Proceed to next question.
- `N` or `→`: Next question.
- `P` or `←`: Previous question.
- `M`: Toggle "Mark for Review".

---

## 🧪 Automated Testing

Run the full pytest suite (44 tests covering answer integrity, workflow, battle sync, persistence, and duplicate checks):

```powershell
python -m pytest
```

---

## 📄 License & Privacy
- **100% Private**: Your study habits, mistakes, and attempts never leave your local computer unless you explicitly enable cloud sync with Supabase.
- Point-in-time database backups can be generated and restored at any time from the Settings tab or `backups/` directory.
