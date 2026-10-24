import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import re
from services.markdown_parser import parse_markdown_questions

sample = """# Gujarat DDCET Maths Questions

---
## Question: MATH-DET-001
**Subject**: Mathematics
**Topic**: Matrices and Determinants
**Subtopic**: Determinants
**Difficulty**: medium
**Verified**: true

If $\\begin{vmatrix} x & 2 \\\\ 8 & x \\end{vmatrix} = 0$, what is the value of $x$?

- (A) $\\pm 4$
- (B) $\\pm 2$
- (C) $4$
- (D) $16$

**Correct Answer**: A
**Explanation**:
The determinant of a $2 \\times 2$ matrix is given by $ad - bc$:
$$\\begin{vmatrix} x & 2 \\\\ 8 & x \\end{vmatrix} = x \\cdot x - 2 \\cdot 8 = x^2 - 16 = 0$$
$$x^2 = 16 \\implies x = \\pm 4$$
"""

records = parse_markdown_questions(sample)
print("Records count:", len(records))
if records:
    q = records[0]
    print("Question ID:", q["id"])
    print("Question text:", repr(q["question"]))
    print("Options:", q["options"])
    print("Correct Answer:", q["correct_answer"])
    print("Explanation:", repr(q["explanation"][:80]))
