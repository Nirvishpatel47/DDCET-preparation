import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import json
from database.db import get_db, init_db
from services.validation_service import get_or_create_hierarchy
from services.duplicate_service import compute_question_hash, compute_question_text_hash, check_duplicate_fast

init_db()

with open("data/data.json", "r", encoding="utf-8") as f:
    questions = json.load(f)

print(f"Loaded {len(questions)} questions from data/data.json")

with get_db() as conn:
    existing_ids = {r[0] for r in conn.execute("SELECT id FROM questions").fetchall()}
    added = 0
    updated = 0
    skipped_duplicates = 0

    for q in questions:
        sub_id, top_id, subtop_id = get_or_create_hierarchy(
            conn, q["subject"], q["topic"], q["subtopic"]
        )
        text_hash = compute_question_hash(q["question"], q["options"])
        q_text_hash = compute_question_text_hash(q["question"])
        source_json = json.dumps(q.get("source", {}))
        tags_json = json.dumps(q.get("tags", []))
        verified_int = 1 if q.get("verified") else 0

        if q["id"] in existing_ids:
            # Update options, question, explanation in case any field was cleaned
            conn.execute(
                """
                UPDATE questions
                SET question_text = ?, option_a = ?, option_b = ?, option_c = ?, option_d = ?,
                    correct_answer = ?, explanation = ?, subject_id = ?, topic_id = ?, subtopic_id = ?,
                    difficulty = ?, source_json = ?, tags_json = ?, verified = ?, text_hash = ?, question_text_hash = ?
                WHERE id = ?
                """,
                (
                    q["question"], q["options"]["A"], q["options"]["B"], q["options"]["C"], q["options"]["D"],
                    q["correct_answer"], q["explanation"], sub_id, top_id, subtop_id,
                    q["difficulty"], source_json, tags_json, verified_int, text_hash, q_text_hash, q["id"]
                )
            )
            updated += 1
        else:
            # Check if this new question is a duplicate before adding
            dup = check_duplicate_fast(conn, q["id"], q["question"], q["options"])
            if dup:
                print(f"Skipping duplicate question: {q['id']} - {dup['reason']}")
                skipped_duplicates += 1
                continue

            conn.execute(
                """
                INSERT INTO questions (
                    id, question_text, option_a, option_b, option_c, option_d,
                    correct_answer, explanation, subject_id, topic_id, subtopic_id,
                    difficulty, source_json, tags_json, verified, text_hash, question_text_hash, created_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    q["id"], q["question"], q["options"]["A"], q["options"]["B"], q["options"]["C"], q["options"]["D"],
                    q["correct_answer"], q["explanation"], sub_id, top_id, subtop_id,
                    q["difficulty"], source_json, tags_json, verified_int, text_hash, q_text_hash, q.get("created_at")
                )
            )
            added += 1

    total = conn.execute("SELECT COUNT(*) FROM questions").fetchone()[0]
    print(f"Database sync complete: {added} new, {updated} updated, {skipped_duplicates} duplicates skipped. Total questions in database: {total}")
