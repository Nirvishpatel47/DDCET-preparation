import json
import sqlite3

def audit():
    with open('data/data.json', 'r', encoding='utf-8') as f:
        data_questions = json.load(f)

    print(f"Total in data.json: {len(data_questions)}")
    a_count = 0
    b_count = 0
    c_count = 0
    d_count = 0
    for i, q in enumerate(data_questions):
        ans = q['correct_answer']
        if ans == 'A': a_count += 1
        elif ans == 'B': b_count += 1
        elif ans == 'C': c_count += 1
        elif ans == 'D': d_count += 1
    print(f"Keys: A={a_count}, B={b_count}, C={c_count}, D={d_count}")

    # Check for duplicate question text
    seen_texts = {}
    duplicates = []
    for q in data_questions:
        txt = q['question'].strip()
        if txt in seen_texts:
            duplicates.append((q['id'], seen_texts[txt], txt))
        else:
            seen_texts[txt] = q['id']
    print(f"Total duplicates found: {len(duplicates)}")
    for d in duplicates:
        print(f"  Duplicate: {d[0]} and {d[1]} -> '{d[2][:60]}...'")




if __name__ == '__main__':
    audit()
