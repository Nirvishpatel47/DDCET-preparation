import re
import json
from typing import List, Dict, Any, Optional


def parse_markdown_questions(md_text: str) -> List[Dict[str, Any]]:
    """
    Parses questions from a Markdown (.md) document.
    Supports:
    1. Embedded ```json ... ``` blocks
    2. Markdown tables (| id | question | option_a | ...)
    3. Header / Section-delimited Markdown question blocks (e.g. ## Question, ### Q1)
    """
    if not md_text or not md_text.strip():
        return []

    # 1. Check for embedded JSON code blocks first
    json_block_match = re.search(r"```(?:json)?\s*(\[\s*\{.*?\}\s*\])\s*```", md_text, re.DOTALL)
    if json_block_match:
        try:
            parsed = json.loads(json_block_match.group(1))
            if isinstance(parsed, list):
                return parsed
        except Exception:
            pass

    # 2. Check for Markdown Table format
    lines = [line.strip() for line in md_text.splitlines() if line.strip()]
    table_rows = [line for line in lines if line.startswith("|") and line.endswith("|")]
    if len(table_rows) >= 3 and "question" in table_rows[0].lower():
        return parse_markdown_table(table_rows)

    # 3. Section / Header-delimited question blocks
    return parse_markdown_sections(md_text)


def parse_markdown_table(table_rows: List[str]) -> List[Dict[str, Any]]:
    """Parses a GFM Markdown table into question dictionaries."""
    headers = [c.strip().lower() for c in table_rows[0].strip("|").split("|")]
    records = []

    # Skip header and separator (row 1 is separator |---|---|)
    for row_str in table_rows[2:]:
        cols = [c.strip() for c in row_str.strip("|").split("|")]
        if len(cols) != len(headers):
            continue
        row_dict = dict(zip(headers, cols))
        records.append(row_dict)

    return records


def parse_markdown_sections(md_text: str) -> List[Dict[str, Any]]:
    """
    Parses section/block-based Markdown questions.
    Splits by delimiters like '---' or headers '## Question', '### Q1', etc.
    """
    # Clean separators
    raw_blocks = re.split(r"(?:\n|^)(?:---+\s*\n|(?=#{1,4}\s*(?:Question|Q\d+|\d+[\.\:])))", md_text)
    questions = []

    for idx, block in enumerate(raw_blocks):
        block = block.strip()
        if not block or len(block) < 20:
            continue

        q_item = parse_single_markdown_block(block, default_index=len(questions) + 1)
        # Must have valid question text and exactly 4 options to be a valid MCQ
        if q_item and q_item.get("question") and len(q_item.get("options", {})) == 4:
            questions.append(q_item)

    return questions


def parse_single_markdown_block(block: str, default_index: int) -> Optional[Dict[str, Any]]:
    """Extracts id, question, options, answer, explanation, subject, topic from a markdown block."""
    data = {
        "id": f"MD-MATH-{default_index:03d}",
        "subject": "Mathematics",
        "topic": "General Mathematics",
        "subtopic": "Core",
        "difficulty": "medium",
        "verified": True,
        "source": {"name": "Markdown Question Bank"},
        "tags": ["math", "markdown"]
    }

    # Extract ID (e.g. ## Question: MD-TEST-001 or ID: MATH-01)
    id_match = re.search(r"(?:question\s*:\s*|question\s*id\s*:\s*|\bid\s*[:=]\s*)([A-Za-z0-9_\-]+)", block, re.IGNORECASE)
    if not id_match:
        id_match = re.search(r"\[([A-Za-z0-9_\-]+)\]", block)
    if id_match:
        data["id"] = id_match.group(1).strip()

    # Extract Subject, Topic, Subtopic, Difficulty if explicitly tagged
    for field in ["subject", "topic", "subtopic", "difficulty"]:
        field_match = re.search(rf"\*\*{field}\*\*[\s:=]+([^\n]+)", block, re.IGNORECASE)
        if not field_match:
            field_match = re.search(rf"^{field}[\s:=]+([^\n]+)", block, re.IGNORECASE | re.MULTILINE)
        if field_match:
            data[field] = field_match.group(1).strip()

    # Extract Correct Answer
    ans_match = re.search(r"(?:\*\*correct\s*answer\*\*|\*\*answer\*\*|correct\s*answer|answer)[\s:=]+([A-Da-d])\b", block, re.IGNORECASE)
    if ans_match:
        data["correct_answer"] = ans_match.group(1).upper()

    # Extract Explanation
    exp_match = re.search(r"(?:\*\*explanation\*\*|explanation)[\s:=]+([\s\S]*?)(?=(?:\n#{1,4}|\n\*\*|$))", block, re.IGNORECASE)
    if exp_match:
        data["explanation"] = exp_match.group(1).strip()

    # Extract Options A, B, C, D
    options = {}
    opt_matches = re.finditer(
        r"(?:^|\n)\s*(?:[-*]\s*)?(?:\(?([A-Da-d])\)?[\.\:\)]|\*\*([A-Da-d])\*\*[\.\:\)])\s*([^\n]+(?:\n(?!\s*(?:[-*]\s*)?(?:\(?[A-Da-d]\)?|\*\*answer|\*\*explanation|\*\*correct|answer:|explanation:))[^\n]+)*)",
        block,
        re.IGNORECASE
    )

    for m in opt_matches:
        opt_key = (m.group(1) or m.group(2)).upper()
        opt_val = m.group(3).strip()
        opt_val = re.sub(r"^[-*]\s*", "", opt_val)
        options[opt_key] = opt_val

    if len(options) == 4:
        data["options"] = options
    else:
        # Not a complete MCQ block
        return None

    # Extract Question Text
    q_text = block
    q_text = re.sub(r"^#{1,4}[^\n]*\n", "", q_text)
    q_text = re.sub(r"\*\*(?:subject|topic|subtopic|difficulty|id|verified)\*\*[\s:=]+[^\n]*\n?", "", q_text, flags=re.IGNORECASE)
    q_text = re.sub(r"^(?:subject|topic|subtopic|difficulty|id|verified)[\s:=]+[^\n]*\n?", "", q_text, flags=re.IGNORECASE | re.MULTILINE)
    q_text = re.sub(r"(?:\*\*correct\s*answer\*\*|\*\*answer\*\*|correct\s*answer|answer)[\s:=]+[^\n]*\n?", "", q_text, flags=re.IGNORECASE)
    q_text = re.sub(r"(?:\*\*explanation\*\*|explanation)[\s:=]+[\s\S]*$", "", q_text, flags=re.IGNORECASE)

    for opt_k in ["A", "B", "C", "D"]:
        if opt_k in options:
            opt_esc = re.escape(options[opt_k])
            q_text = re.sub(rf"(?:^|\n)\s*(?:[-*]\s*)?\(?{opt_k}\)?[\.\:\)]\s*{opt_esc}", "", q_text, flags=re.IGNORECASE)

    q_text = re.sub(r"^###?\s*(?:question|q)\s*(?:\d+|:|\-)?\s*", "", q_text.strip(), flags=re.IGNORECASE)
    q_text = re.sub(r"^\*\*(?:question|problem)\*\*[\s:=]*", "", q_text.strip(), flags=re.IGNORECASE)
    q_text = q_text.strip()

    if q_text:
        data["question"] = q_text

    return data
