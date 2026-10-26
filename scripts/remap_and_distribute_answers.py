import sys
import os
import json
from collections import Counter

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from models.schemas import QuestionModel
from database.db import get_db
from services.validation_service import get_or_create_hierarchy
from services.duplicate_service import compute_question_hash

def main():
    json_path = "data/data.json"
    with open(json_path, "r", encoding="utf-8") as f:
        questions = json.load(f)

    print(f"Loaded {len(questions)} questions.")

    # Fix the duplicate DDCET-MATH-DET-001 so it's a unique question
    for q in questions:
        if q["id"] == "DDCET-MATH-DET-001":
            q["question"] = r"If $\begin{vmatrix} x & 3 \\ 12 & x \end{vmatrix} = 0$, what is the value of $x$?"
            q["options"] = {
                "A": r"$\pm 6$",
                "B": r"$\pm 3$",
                "C": r"$6$",
                "D": r"$36$"
            }
            q["correct_answer"] = "A"
            q["explanation"] = r"Expanding determinant: $x^2 - (3)(12) = 0 \implies x^2 = 36 \implies x = \pm 6$."

    target_letters = ["A", "B", "C", "D"]
    remap_log = Counter()

    for idx, q in enumerate(questions):
        old_opts = q["options"]
        old_corr = q["correct_answer"]
        corr_val = old_opts[old_corr]

        target_letter = target_letters[idx % 4]

        # Gather distractors in original relative order
        distractor_vals = [val for k, val in old_opts.items() if k != old_corr]

        new_opts = {}
        d_idx = 0
        for letter in ["A", "B", "C", "D"]:
            if letter == target_letter:
                new_opts[letter] = corr_val
            else:
                new_opts[letter] = distractor_vals[d_idx]
                d_idx += 1

        # Verification asserts
        assert new_opts[target_letter] == corr_val, f"Mismatch in correct value for {q['id']}"
        assert set(new_opts.values()) == set(old_opts.values()), f"Options set altered in {q['id']}"
        assert len(new_opts) == 4, f"Options length not 4 in {q['id']}"

        q["options"] = new_opts
        q["correct_answer"] = target_letter

        # Validate with pydantic schema
        validated_q = QuestionModel(**q)
        remap_log[target_letter] += 1

    print("Distribution after deterministic remapping:", remap_log)

    # Save to data/data.json
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(questions, f, indent=2, ensure_ascii=False)
    print("Saved remapped questions to data/data.json")

    # Sync to SQLite database
    print("Syncing to SQLite database...")
    with get_db() as conn:
        for q in questions:
            sub_id, top_id, subtop_id = get_or_create_hierarchy(
                conn, q["subject"], q["topic"], q["subtopic"]
            )
            text_hash = compute_question_hash(q["question"], q["options"])
            source_json = json.dumps(q.get("source", {}))
            tags_json = json.dumps(q.get("tags", []))
            verified_int = 1 if q.get("verified") else 0

            conn.execute(
                """
                UPDATE questions
                SET question_text = ?, option_a = ?, option_b = ?, option_c = ?, option_d = ?,
                    correct_answer = ?, explanation = ?, subject_id = ?, topic_id = ?, subtopic_id = ?,
                    difficulty = ?, source_json = ?, tags_json = ?, verified = ?, text_hash = ?
                WHERE id = ?
                """,
                (
                    q["question"], q["options"]["A"], q["options"]["B"], q["options"]["C"], q["options"]["D"],
                    q["correct_answer"], q["explanation"], sub_id, top_id, subtop_id,
                    q["difficulty"], source_json, tags_json, verified_int, text_hash, q["id"]
                )
            )

        # Audit SQLite database distribution
        db_dist = conn.execute("SELECT correct_answer, COUNT(*) as cnt FROM questions GROUP BY correct_answer").fetchall()
        print("SQLite Database Distribution:")
        for row in db_dist:
            print(f"  {row['correct_answer']}: {row['cnt']}")

    print("Remapping and distribution complete and verified!")

if __name__ == "__main__":
    main()
