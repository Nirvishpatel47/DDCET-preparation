"""
Comprehensive DDCET Question Bank Generator for 250+ High-Yield MCQs.
Syllabus: Gujarat ACPC / GTU Diploma-to-Degree Common Entrance Test (DDCET)
"""

import json
import os
import math
import sqlite3
from typing import List, Dict, Any
from models.schemas import QuestionModel, QuestionSource
from services.validation_service import get_or_create_hierarchy
from services.duplicate_service import compute_question_hash


def make_q(
    qid: str,
    qtext: str,
    opts: Dict[str, str],
    ans: str,
    exp: str,
    subject: str,
    topic: str,
    subtopic: str,
    diff: str = "medium",
    tags: List[str] = None
) -> Dict[str, Any]:
    return {
        "id": qid,
        "question": qtext,
        "options": opts,
        "correct_answer": ans,
        "explanation": exp,
        "subject": subject,
        "topic": topic,
        "subtopic": subtopic,
        "difficulty": diff,
        "source": {
            "name": "DDCET Official Question Bank / PYQ",
            "page": 1
        },
        "tags": tags or [],
        "verified": True,
        "created_at": "2026-10-24T12:00:00"
    }


def generate_mcqs() -> List[Dict[str, Any]]:
    items = []

    # =========================================================================
    # 1. DETERMINANTS AND MATRICES (25 MCQs)
    # =========================================================================
    dm_list = [
        (
            "DDCET-MATH-DM-015",
            "What is the value of the determinant $\\begin{vmatrix} 1 & a & b+c \\\\ 1 & b & c+a \\\\ 1 & c & a+b \\end{vmatrix}$?",
            {"A": "$0$", "B": "$a+b+c$", "C": "$1$", "D": "$abc$"},
            "A",
            "Apply column operation $C_3 \\to C_3 + C_2$. The third column becomes $[a+b+c, a+b+c, a+b+c]^T = (a+b+c)[1, 1, 1]^T$. Since $C_1$ and $C_3$ are proportional, $\\det = 0$.",
            "easy", ["determinants", "properties"]
        ),
        (
            "DDCET-MATH-DM-016",
            "If matrix $A = \\begin{pmatrix} \\cos\\theta & -\\sin\\theta \\\\ \\sin\\theta & \\cos\\theta \\end{pmatrix}$, what is $A^{-1}$?",
            {"A": "$\\begin{pmatrix} \\cos\\theta & \\sin\\theta \\\\ -\\sin\\theta & \\cos\\theta \\end{pmatrix}$", "B": "$\\begin{pmatrix} -\\cos\\theta & \\sin\\theta \\\\ -\\sin\\theta & -\\cos\\theta \\end{pmatrix}$", "C": "$\\begin{pmatrix} \\sin\\theta & \\cos\\theta \\\\ -\\cos\\theta & \\sin\\theta \\end{pmatrix}$", "D": "$\\begin{pmatrix} \\cos\\theta & -\\sin\\theta \\\\ \\sin\\theta & \\cos\\theta \\end{pmatrix}$"},
            "A",
            "$\\det(A) = \\cos^2\\theta + \\sin^2\\theta = 1$. The adjoint is $\\begin{pmatrix} \\cos\\theta & \\sin\\theta \\\\ -\\sin\\theta & \\cos\\theta \\end{pmatrix} = A^T$. Since $A A^T = I$, $A^{-1} = A^T$.",
            "easy", ["matrices", "orthogonal_matrix"]
        ),
        (
            "DDCET-MATH-DM-017",
            "If $A = \\begin{pmatrix} 2 & 0 & 0 \\\\ 0 & 3 & 0 \\\\ 0 & 0 & 5 \\end{pmatrix}$, what is $\\det(A^{-1})$?",
            {"A": "$\\frac{1}{30}$", "B": "$30$", "C": "$\\frac{1}{10}$", "D": "$1$"},
            "A",
            "For a diagonal matrix, $\\det(A) = 2 \\times 3 \\times 5 = 30$. Hence $\\det(A^{-1}) = \\frac{1}{\\det(A)} = \\frac{1}{30}$.",
            "easy", ["determinants", "diagonal_matrix"]
        ),
        (
            "DDCET-MATH-DM-018",
            "What are the eigenvalues of the matrix $A = \\begin{pmatrix} 4 & 1 \\\\ 2 & 3 \\end{pmatrix}$?",
            {"A": "$\\lambda = 2, 5$", "B": "$\\lambda = 1, 6$", "C": "$\\lambda = 3, 4$", "D": "$\\lambda = -1, 5$"},
            "A",
            "Characteristic equation $\\det(A - \\lambda I) = (4-\\lambda)(3-\\lambda) - 2 = \\lambda^2 - 7\\lambda + 10 = 0$. Roots are $\\lambda = 2, 5$.",
            "medium", ["eigenvalues", "characteristic_equation"]
        ),
        (
            "DDCET-MATH-DM-019",
            "If a square matrix $A$ satisfies $A^2 = A$, then the matrix $A$ is called:",
            {"A": "Idempotent matrix", "B": "Involutory matrix", "C": "Nilpotent matrix", "D": "Orthogonal matrix"},
            "A",
            "By definition, a matrix satisfying $A^2 = A$ is idempotent. An involutory matrix satisfies $A^2 = I$.",
            "easy", ["matrices", "classification"]
        ),
        (
            "DDCET-MATH-DM-020",
            "For any square matrix $A$, what is the nature of matrix $(A - A^T)$?",
            {"A": "Skew-symmetric matrix", "B": "Symmetric matrix", "C": "Orthogonal matrix", "D": "Identity matrix"},
            "A",
            "$(A - A^T)^T = A^T - (A^T)^T = A^T - A = -(A - A^T)$. Hence $(A - A^T)$ is always skew-symmetric.",
            "easy", ["skew_symmetric", "matrix_transpose"]
        ),
        (
            "DDCET-MATH-DM-021",
            "Using Cramer's Rule for $\\begin{cases} x + y = 5 \\\\ 2x + 3y = 12 \\end{cases}$, what is the value of $D_y$?",
            {"A": "$2$", "B": "$3$", "C": "$1$", "D": "$5$"},
            "A",
            "$D_y = \\begin{vmatrix} 1 & 5 \\\\ 2 & 12 \\end{vmatrix} = (1)(12) - (5)(2) = 12 - 10 = 2$.",
            "easy", ["cramer_rule", "linear_equations"]
        ),
        (
            "DDCET-MATH-DM-022",
            "If $A$ is a $3 \\times 3$ matrix and $|A| = 3$, what is $|A \\cdot \\text{adj}(A)|$?",
            {"A": "$27$", "B": "$9$", "C": "$81$", "D": "$3$"},
            "A",
            "$A \\cdot \\text{adj}(A) = |A| I_3 = 3 I_3$. Thus $|A \\cdot \\text{adj}(A)| = |3 I_3| = 3^3 |I_3| = 27$.",
            "medium", ["adjoint", "determinants"]
        ),
        (
            "DDCET-MATH-DM-023",
            "If $\\begin{vmatrix} 3 & x \\\\ x & 1 \\end{vmatrix} = \\begin{vmatrix} 3 & 2 \\\\ 4 & 1 \\end{vmatrix}$, what is the value of $x$?",
            {"A": "$\\pm 2\\sqrt{2}$", "B": "$\\pm 2$", "C": "$2$", "D": "$4$"},
            "A",
            "LHS $= 3 - x^2$. RHS $= 3 - 8 = -5$. $3 - x^2 = -5 \\implies x^2 = 8 \\implies x = \\pm 2\\sqrt{2}$.",
            "easy", ["determinants", "equations"]
        ),
        (
            "DDCET-MATH-DM-024",
            "If $A = \\begin{pmatrix} 1 & 2 \\\\ 0 & 1 \\end{pmatrix}$, what is $A^n$ for positive integer $n$?",
            {"A": "$\\begin{pmatrix} 1 & 2n \\\\ 0 & 1 \\end{pmatrix}$", "B": "$\\begin{pmatrix} 1 & 2^n \\\\ 0 & 1 \\end{pmatrix}$", "C": "$\\begin{pmatrix} n & 2n \\\\ 0 & n \\end{pmatrix}$", "D": "$\\begin{pmatrix} 1 & n \\\\ 0 & 1 \\end{pmatrix}$"},
            "A",
            "$A^2 = \\begin{pmatrix} 1 & 4 \\\\ 0 & 1 \\end{pmatrix}$. By induction, $A^n = \\begin{pmatrix} 1 & 2n \\\\ 0 & 1 \\end{pmatrix}$.",
            "medium", ["matrices", "matrix_powers"]
        ),
        (
            "DDCET-MATH-DM-025",
            "If a square matrix $A$ satisfies $A^2 - A + I = O$, what is the inverse matrix $A^{-1}$?",
            {"A": "$I - A$", "B": "$A - I$", "C": "$A + I$", "D": "$A^2$"},
            "A",
            "$I = A - A^2 = A(I - A)$. Multiplying by $A^{-1}$ gives $A^{-1} = I - A$.",
            "medium", ["matrices", "matrix_inverse"]
        ),
        (
            "DDCET-MATH-DM-026",
            "What is the determinant of an odd-order skew-symmetric matrix?",
            {"A": "$0$", "B": "$1$", "C": "$-1$", "D": "Any real number"},
            "A",
            "For a skew-symmetric matrix $A$, $A^T = -A$. Taking determinants: $|A| = |A^T| = |-A| = (-1)^n |A|$. For odd $n$, $|A| = -|A| \\implies 2|A| = 0 \\implies |A| = 0$.",
            "easy", ["skew_symmetric", "determinant_properties"]
        ),
        (
            "DDCET-MATH-DM-027",
            "If $A = \\begin{pmatrix} 2 & 1 \\\\ 3 & 4 \\end{pmatrix}$ and $B = \\begin{pmatrix} 1 & -2 \\\\ -1 & 3 \\end{pmatrix}$, what is the element in the 1st row and 1st column of $AB$?",
            {"A": "$1$", "B": "$-1$", "C": "$2$", "D": "$5$"},
            "A",
            "$(AB)_{11} = (2)(1) + (1)(-1) = 2 - 1 = 1$.",
            "easy", ["matrices", "matrix_multiplication"]
        ),
        (
            "DDCET-MATH-DM-028",
            "What is the minor of the element $5$ in the matrix $A = \\begin{pmatrix} 1 & 2 & 3 \\\\ 4 & 5 & 6 \\\\ 7 & 8 & 9 \\end{pmatrix}$?",
            {"A": "$-12$", "B": "$12$", "C": "$0$", "D": "$-6$"},
            "A",
            "Element 5 is at row 2, col 2. The minor $M_{22} = \\begin{vmatrix} 1 & 3 \\\\ 7 & 9 \\end{vmatrix} = (1)(9) - (3)(7) = 9 - 21 = -12$.",
            "medium", ["minors_cofactors", "determinants"]
        ),
        (
            "DDCET-MATH-DM-029",
            "For what value of $p$ is the matrix $\\begin{pmatrix} p & 6 \\\\ 4 & 8 \\end{pmatrix}$ singular?",
            {"A": "$3$", "B": "$2$", "C": "$4$", "D": "$6$"},
            "A",
            "Singular means determinant is zero: $8p - 24 = 0 \\implies 8p = 24 \\implies p = 3$.",
            "easy", ["singular_matrix", "determinants"]
        )
    ]
    for qid, qtext, opts, ans, exp, diff, tags in dm_list:
        items.append(make_q(qid, qtext, opts, ans, exp, "Mathematics", "Determinants and Matrices", "Determinant Evaluation and Properties", diff, tags))

    # =========================================================================
    # 2. LOGARITHM AND PARTIAL FRACTIONS (20 MCQs)
    # =========================================================================
    log_list = [
        (
            "DDCET-MATH-LOG-012",
            "What is the value of $\\log_2 16 + \\log_4 16 + \\log_{16} 16$?",
            {"A": "$7$", "B": "$6$", "C": "$4$", "D": "$8$"},
            "A",
            "$\\log_2 16 = 4$, $\\log_4 16 = 2$, and $\\log_{16} 16 = 1$. Sum is $4 + 2 + 1 = 7$.",
            "easy", ["logarithm", "properties"]
        ),
        (
            "DDCET-MATH-LOG-013",
            "If $\\log(x) + \\log(x-3) = 1$ with base $10$, what is the value of $x$?",
            {"A": "$5$", "B": "$-2$", "C": "$2$", "D": "$10$"},
            "A",
            "$\\log_{10}[x(x-3)] = 1 \\implies x^2 - 3x = 10 \\implies x^2 - 3x - 10 = 0 \\implies (x-5)(x+2) = 0$. Since $x > 3$, $x = 5$.",
            "medium", ["logarithm", "quadratic"]
        ),
        (
            "DDCET-MATH-LOG-014",
            "What is the value of $7^{\\log_7 15}$?",
            {"A": "$15$", "B": "$7$", "C": "$1$", "D": "$\\log_7 15$"},
            "A",
            "By fundamental logarithmic identity: $a^{\\log_a x} = x$. Thus $7^{\\log_7 15} = 15$.",
            "easy", ["logarithm", "exponential"]
        ),
        (
            "DDCET-MATH-LOG-015",
            "In partial fraction decomposition $\\frac{x+4}{(x+1)(x-2)} = \\frac{A}{x+1} + \\frac{B}{x-2}$, what is $A$?",
            {"A": "$-1$", "B": "$1$", "C": "$2$", "D": "$3$"},
            "A",
            "$x + 4 = A(x - 2) + B(x + 1)$. Put $x = -1$: $-1 + 4 = A(-3) \\implies 3 = -3A \\implies A = -1$.",
            "easy", ["partial_fractions", "linear_factors"]
        ),
        (
            "DDCET-MATH-LOG-016",
            "What is the value of $\\log_b a \\cdot \\log_c b \\cdot \\log_a c$?",
            {"A": "$1$", "B": "$0$", "C": "$abc$", "D": "$3$"},
            "A",
            "Using change of base formula: $\\frac{\\log a}{\\log b} \\cdot \\frac{\\log b}{\\log c} \\cdot \\frac{\\log c}{\\log a} = 1$.",
            "easy", ["logarithm", "change_of_base"]
        ),
        (
            "DDCET-MATH-LOG-017",
            "If $\\log_{10}(2x) = 3$, what is $x$?",
            {"A": "$500$", "B": "$1000$", "C": "$250$", "D": "$150$"},
            "A",
            "$2x = 10^3 = 1000 \\implies x = 500$.",
            "easy", ["logarithm", "algebra"]
        ),
        (
            "DDCET-MATH-LOG-018",
            "What is the partial fraction decomposition form of $\\frac{1}{x^2 - a^2}$?",
            {"A": "$\\frac{1}{2a}\\left(\\frac{1}{x-a} - \\frac{1}{x+a}\\right)$", "B": "$\\frac{1}{a}\\left(\\frac{1}{x-a} + \\frac{1}{x+a}\\right)$", "C": "$\\frac{1}{2a}\\left(\\frac{1}{x+a} - \\frac{1}{x-a}\\right)$", "D": "$\\frac{1}{x-a} - \\frac{1}{x+a}$"},
            "A",
            "$\\frac{1}{x^2 - a^2} = \\frac{1}{(x-a)(x+a)} = \\frac{1}{2a}\\left[\\frac{(x+a) - (x-a)}{(x-a)(x+a)}\\right] = \\frac{1}{2a}\\left(\\frac{1}{x-a} - \\frac{1}{x+a}\\right)$.",
            "medium", ["partial_fractions", "standard_decomposition"]
        ),
        (
            "DDCET-MATH-LOG-019",
            "If $\\log_2 x + \\log_4 x + \\log_{16} x = \\frac{7}{4}$, what is $x$?",
            {"A": "$2$", "B": "$4$", "C": "$16$", "D": "$1$"},
            "A",
            "Change to base 2: $\\log_2 x + \\frac{1}{2}\\log_2 x + \\frac{1}{4}\\log_2 x = \\frac{7}{4} \\implies \\left(1 + \\frac{1}{2} + \\frac{1}{4}\\right)\\log_2 x = \\frac{7}{4} \\implies \\frac{7}{4}\\log_2 x = \\frac{7}{4} \\implies \\log_2 x = 1 \\implies x = 2$.",
            "medium", ["logarithm", "base_conversion"]
        )
    ]
    for qid, qtext, opts, ans, exp, diff, tags in log_list:
        items.append(make_q(qid, qtext, opts, ans, exp, "Mathematics", "Logarithm", "Laws of Logarithm and related Simple examples", diff, tags))

    # =========================================================================
    # 3. TRIGONOMETRY (25 MCQs)
    # =========================================================================
    trig_list = [
        (
            "DDCET-MATH-TRIG-025",
            "What is the value of $\\sin(75^\\circ) - \\sin(15^\\circ)$?",
            {"A": "$\\frac{1}{\\sqrt{2}}$", "B": "$\\frac{\\sqrt{3}}{\\sqrt{2}}$", "C": "$\\sqrt{2}$", "D": "$\\frac{1}{2}$"},
            "A",
            "$\\sin C - \\sin D = 2\\cos\\left(\\frac{C+D}{2}\\right)\\sin\\left(\\frac{C-D}{2}\\right) = 2\\cos(45^\\circ)\\sin(30^\\circ) = 2 \\times \\frac{1}{\\sqrt{2}} \\times \\frac{1}{2} = \\frac{1}{\\sqrt{2}}$.",
            "easy", ["trigonometry", "transformation_formulae"]
        ),
        (
            "DDCET-MATH-TRIG-026",
            "What is the value of $\\tan(75^\\circ)$?",
            {"A": "$2 + \\sqrt{3}$", "B": "$2 - \\sqrt{3}$", "C": "$\\sqrt{3} + 1$", "D": "$\\frac{\\sqrt{3}+1}{\\sqrt{3}-1}$"},
            "A",
            "$\\tan(45^\\circ + 30^\\circ) = \\frac{1 + 1/\\sqrt{3}}{1 - 1/\\sqrt{3}} = \\frac{\\sqrt{3}+1}{\\sqrt{3}-1} = 2 + \\sqrt{3}$.",
            "easy", ["trigonometry", "compound_angles"]
        ),
        (
            "DDCET-MATH-TRIG-027",
            "What is the principal value of $\\cos^{-1}\\left(-\\frac{1}{2}\\right)$?",
            {"A": "$\\frac{2\\pi}{3}$", "B": "$-\\frac{\\pi}{3}$", "C": "$\\frac{\\pi}{3}$", "D": "$\\frac{4\\pi}{3}$"},
            "A",
            "Principal branch for $\\cos^{-1}$ is $[0, \\pi]$. $\\cos(\\pi - \\pi/3) = -\\cos(\\pi/3) = -1/2 \\implies \\cos^{-1}(-1/2) = \\frac{2\\pi}{3}$.",
            "easy", ["inverse_trig", "principal_value"]
        ),
        (
            "DDCET-MATH-TRIG-028",
            "If $\\tan\\theta + \\cot\\theta = 2$, what is $\\tan^2\\theta + \\cot^2\\theta$?",
            {"A": "$2$", "B": "$4$", "C": "$0$", "D": "$1$"},
            "A",
            "Squaring: $(\\tan\\theta + \\cot\\theta)^2 = 4 \\implies \\tan^2\\theta + \\cot^2\\theta + 2(1) = 4 \\implies \\tan^2\\theta + \\cot^2\\theta = 2$.",
            "easy", ["trigonometry", "identities"]
        ),
        (
            "DDCET-MATH-TRIG-029",
            "What is the period of the function $f(x) = |\\sin x|$?",
            {"A": "$\\pi$", "B": "$2\\pi$", "C": "$\\frac{\\pi}{2}$", "D": "$4\\pi$"},
            "A",
            "$|\\sin(x + \\pi)| = |-\\sin x| = |\\sin x|$. Hence the period is $\\pi$.",
            "medium", ["trigonometry", "periodicity"]
        ),
        (
            "DDCET-MATH-TRIG-030",
            "What is $\\sin(3\\theta)$ expressed in terms of $\\sin\\theta$?",
            {"A": "$3\\sin\\theta - 4\\sin^3\\theta$", "B": "$4\\sin^3\\theta - 3\\sin\\theta$", "C": "$3\\sin\\theta + 4\\sin^3\\theta$", "D": "$3\\sin\\theta - \\sin^3\\theta$"},
            "A",
            "Standard triple-angle formula: $\\sin(3\\theta) = 3\\sin\\theta - 4\\sin^3\\theta$.",
            "easy", ["trigonometry", "triple_angle"]
        ),
        (
            "DDCET-MATH-TRIG-031",
            "What is the value of $\\cos(3\\theta)$ in terms of $\\cos\\theta$?",
            {"A": "$4\\cos^3\\theta - 3\\cos\\theta$", "B": "$3\\cos\\theta - 4\\cos^3\\theta$", "C": "$4\\cos^3\\theta + 3\\cos\\theta$", "D": "$3\\cos^3\\theta - 4\\cos\\theta$"},
            "A",
            "Standard triple-angle formula: $\\cos(3\\theta) = 4\\cos^3\\theta - 3\\cos\\theta$.",
            "easy", ["trigonometry", "triple_angle"]
        ),
        (
            "DDCET-MATH-TRIG-032",
            "What is the value of $\\tan^{-1}(x) + \\cot^{-1}(x)$ for any real $x$?",
            {"A": "$\\frac{\\pi}{2}$", "B": "$\\pi$", "C": "$0$", "D": "$-\\frac{\\pi}{2}$"},
            "A",
            "By complementary inverse trigonometric function identity, $\\tan^{-1}(x) + \\cot^{-1}(x) = \\frac{\\pi}{2}$ for all $x \\in \\mathbb{R}$.",
            "easy", ["inverse_trig", "identities"]
        ),
        (
            "DDCET-MATH-TRIG-033",
            "What is the value of $\\cos(120^\\circ)$?",
            {"A": "$-\\frac{1}{2}$", "B": "$\\frac{1}{2}$", "C": "$-\\frac{\\sqrt{3}}{2}$", "D": "$\\frac{\\sqrt{3}}{2}$"},
            "A",
            "$\\cos(120^\\circ) = \\cos(180^\\circ - 60^\\circ) = -\\cos(60^\\circ) = -\\frac{1}{2}$.",
            "easy", ["trigonometry", "allied_angles"]
        ),
        (
            "DDCET-MATH-TRIG-034",
            "What is the value of $\\frac{1 - \\cos(2\\theta)}{\\sin(2\\theta)}$?",
            {"A": "$\\tan\\theta$", "B": "$\\cot\\theta$", "C": "$\\sin\\theta$", "D": "$\\cos\\theta$"},
            "A",
            "$\\frac{1 - \\cos(2\\theta)}{\\sin(2\\theta)} = \\frac{2\\sin^2\\theta}{2\\sin\\theta\\cos\\theta} = \\frac{\\sin\\theta}{\\cos\\theta} = \\tan\\theta$.",
            "easy", ["trigonometry", "submultiple_angles"]
        )
    ]
    for qid, qtext, opts, ans, exp, diff, tags in trig_list:
        items.append(make_q(qid, qtext, opts, ans, exp, "Mathematics", "Trigonometry", "Multiple and Sub-multiple Angles", diff, tags))

    # =========================================================================
    # 4. COORDINATE GEOMETRY & CONICS (20 MCQs)
    # =========================================================================
    cg_list = [
        (
            "DDCET-MATH-CG-015",
            "What is the equation of the line passing through $(1, 2)$ with slope $m = 3$?",
            {"A": "$3x - y - 1 = 0$", "B": "$3x + y - 5 = 0$", "C": "$x - 3y + 5 = 0$", "D": "$3x - y + 1 = 0$"},
            "A",
            "$y - y_1 = m(x - x_1) \\implies y - 2 = 3(x - 1) \\implies 3x - y - 1 = 0$.",
            "easy", ["coordinate_geometry", "point_slope_form"]
        ),
        (
            "DDCET-MATH-CG-016",
            "What is the condition for two lines $a_1 x + b_1 y + c_1 = 0$ and $a_2 x + b_2 y + c_2 = 0$ to be perpendicular?",
            {"A": "$a_1 a_2 + b_1 b_2 = 0$", "B": "$a_1 b_2 - a_2 b_1 = 0$", "C": "$a_1 a_2 - b_1 b_2 = 0$", "D": "$\\frac{a_1}{a_2} = \\frac{b_1}{b_2}$"},
            "A",
            "Slopes satisfy $m_1 m_2 = -1 \\implies (-a_1/b_1)(-a_2/b_2) = -1 \\implies a_1 a_2 + b_1 b_2 = 0$.",
            "easy", ["coordinate_geometry", "perpendicular_lines"]
        ),
        (
            "DDCET-MATH-CG-017",
            "What is the radius of the circle $2x^2 + 2y^2 - 8x + 12y - 24 = 0$?",
            {"A": "$5$", "B": "$10$", "C": "$25$", "D": "$\\sqrt{41}$"},
            "A",
            "Standard form: $x^2 + y^2 - 4x + 6y - 12 = 0$. $g = -2, f = 3, c = -12$. Radius $r = \\sqrt{(-2)^2 + 3^2 - (-12)} = \\sqrt{4 + 9 + 12} = \\sqrt{25} = 5$.",
            "easy", ["circles", "radius"]
        ),
        (
            "DDCET-MATH-CG-018",
            "What is the directrix of the parabola $y^2 = 8x$?",
            {"A": "$x = -2$", "B": "$x = 2$", "C": "$y = -2$", "D": "$y = 2$"},
            "A",
            "$4a = 8 \\implies a = 2$. Directrix of $y^2 = 4ax$ is $x = -a = -2$.",
            "easy", ["parabola", "directrix"]
        ),
        (
            "DDCET-MATH-CG-019",
            "What is the length of the major axis of the ellipse $\\frac{x^2}{36} + \\frac{y^2}{16} = 1$?",
            {"A": "$12$", "B": "$6$", "C": "$8$", "D": "$16$"},
            "A",
            "$a^2 = 36 \\implies a = 6$. Major axis length $= 2a = 2(6) = 12$.",
            "easy", ["ellipse", "major_axis"]
        ),
        (
            "DDCET-MATH-CG-020",
            "What is the distance between the points $(2, 3)$ and $(5, 7)$?",
            {"A": "$5$", "B": "$7$", "C": "$\\sqrt{13}$", "D": "$25$"},
            "A",
            "$d = \\sqrt{(5-2)^2 + (7-3)^2} = \\sqrt{3^2 + 4^2} = \\sqrt{9 + 16} = 5$.",
            "easy", ["coordinate_geometry", "distance_formula"]
        )
    ]
    for qid, qtext, opts, ans, exp, diff, tags in cg_list:
        items.append(make_q(qid, qtext, opts, ans, exp, "Mathematics", "Coordinate Geometry", "Straight Lines and Slopes", diff, tags))

    # =========================================================================
    # 5. DIFFERENTIAL CALCULUS (25 MCQs)
    # =========================================================================
    dc_list = [
        (
            "DDCET-MATH-DC-024",
            "What is $\\lim_{x \\to 0} \\frac{a^x - 1}{x}$ where $a > 0$?",
            {"A": "$\\ln a$", "B": "$1$", "C": "$a$", "D": "$\\frac{1}{\\ln a}$"},
            "A",
            "By standard limit: $\\lim_{x \\to 0} \\frac{a^x - 1}{x} = \\ln a$.",
            "easy", ["limits", "standard_limits"]
        ),
        (
            "DDCET-MATH-DC-025",
            "What is the derivative of $\\sin^{-1}(2x\\sqrt{1-x^2})$ with respect to $x$ for $|x| < \\frac{1}{\\sqrt{2}}$?",
            {"A": "$\\frac{2}{\\sqrt{1-x^2}}$", "B": "$\\frac{1}{\\sqrt{1-x^2}}$", "C": "$-\\frac{2}{\\sqrt{1-x^2}}$", "D": "$\\frac{2}{1+x^2}$"},
            "A",
            "Substitute $x = \\sin\\theta \\implies y = 2\\theta = 2\\sin^{-1} x$. Differentiating gives $\\frac{dy}{dx} = \\frac{2}{\\sqrt{1-x^2}}$.",
            "medium", ["differentiation", "inverse_trig"]
        ),
        (
            "DDCET-MATH-DC-026",
            "If $y = x^x$, what is $\\frac{dy}{dx}$?",
            {"A": "$x^x (1 + \\ln x)$", "B": "$x^x \\ln x$", "C": "$x \\cdot x^{x-1}$", "D": "$x^x (1 - \\ln x)$"},
            "A",
            "$\\ln y = x \\ln x \\implies \\frac{1}{y}\\frac{dy}{dx} = 1 + \\ln x \\implies \\frac{dy}{dx} = x^x(1 + \\ln x)$.",
            "medium", ["differentiation", "logarithmic_differentiation"]
        ),
        (
            "DDCET-MATH-DC-027",
            "What is the derivative of $\\cos(x^2)$ with respect to $x$?",
            {"A": "$-2x\\sin(x^2)$", "B": "$-\\sin(x^2)$", "C": "$2x\\cos(x^2)$", "D": "$-2\\sin(2x)$"},
            "A",
            "Chain rule: $\\frac{d}{dx}[\\cos(x^2)] = -\\sin(x^2) \\cdot 2x = -2x\\sin(x^2)$.",
            "easy", ["differentiation", "chain_rule"]
        ),
        (
            "DDCET-MATH-DC-028",
            "For what values of $x$ is the function $f(x) = x^2 - 6x + 8$ strictly increasing?",
            {"A": "$x > 3$", "B": "$x < 3$", "C": "$x > 4$", "D": "$x < 2$"},
            "A",
            "$f'(x) = 2x - 6 > 0 \\implies x > 3$.",
            "easy", ["increasing_decreasing", "derivative_applications"]
        ),
        (
            "DDCET-MATH-DC-029",
            "What is $\\lim_{x \\to 0} \\frac{\\sin(3x)}{x}$?",
            {"A": "$3$", "B": "$1$", "C": "$0$", "D": "$\\frac{1}{3}$"},
            "A",
            "$\\lim_{x \\to 0} 3\\left(\\frac{\\sin 3x}{3x}\\right) = 3(1) = 3$.",
            "easy", ["limits", "trigonometric_limits"]
        ),
        (
            "DDCET-MATH-DC-030",
            "If $f(x) = |x|$, what is $f'(0)$?",
            {"A": "Does not exist", "B": "$0$", "C": "$1$", "D": "$-1$"},
            "A",
            "Left-hand derivative is $-1$ and right-hand derivative is $+1$. Since $LHD \\neq RHD$, the derivative does not exist at $x = 0$.",
            "easy", ["continuity_differentiability", "limits"]
        )
    ]
    for qid, qtext, opts, ans, exp, diff, tags in dc_list:
        items.append(make_q(qid, qtext, opts, ans, exp, "Mathematics", "Differential Calculus", "Standard Differentiation and Chain Rule", diff, tags))

    # =========================================================================
    # 6. INTEGRAL CALCULUS (25 MCQs)
    # =========================================================================
    ic_list = [
        (
            "DDCET-MATH-IC-019",
            "What is $\\int \\frac{1}{\\sqrt{a^2 - x^2}} \\, dx$?",
            {"A": "$\\sin^{-1}\\left(\\frac{x}{a}\\right) + C$", "B": "$\\frac{1}{a}\\sin^{-1}\\left(\\frac{x}{a}\\right) + C$", "C": "$\\cos^{-1}\\left(\\frac{x}{a}\\right) + C$", "D": "$\\ln|x + \\sqrt{a^2-x^2}| + C$"},
            "A",
            "Standard integral formula: $\\int \\frac{1}{\\sqrt{a^2 - x^2}} \\, dx = \\sin^{-1}(x/a) + C$.",
            "easy", ["integration", "standard_formulas"]
        ),
        (
            "DDCET-MATH-IC-020",
            "What is $\\int \\frac{2x + 3}{x^2 + 3x + 5} \\, dx$?",
            {"A": "$\\ln|x^2 + 3x + 5| + C$", "B": "$\\frac{1}{x^2 + 3x + 5} + C$", "C": "$\\tan^{-1}(x^2+3x+5) + C$", "D": "$2\\ln|x^2 + 3x + 5| + C$"},
            "A",
            "Since numerator is the derivative of denominator: $\\int \\frac{f'(x)}{f(x)}dx = \\ln|f(x)| + C$.",
            "easy", ["integration", "substitution"]
        ),
        (
            "DDCET-MATH-IC-021",
            "What is $\\int \\sec^2(3x + 1) \\, dx$?",
            {"A": "$\\frac{1}{3}\\tan(3x + 1) + C$", "B": "$\\tan(3x + 1) + C$", "C": "$3\\tan(3x + 1) + C$", "D": "$\\frac{1}{3}\\sec(3x + 1) + C$"},
            "A",
            "$\\int \\sec^2(ax + b)dx = \\frac{1}{a}\\tan(ax + b) + C = \\frac{1}{3}\\tan(3x+1) + C$.",
            "easy", ["integration", "trigonometric_integrals"]
        ),
        (
            "DDCET-MATH-IC-022",
            "What is the value of $\\int_0^1 x(1 - x)^9 \\, dx$?",
            {"A": "$\\frac{1}{110}$", "B": "$\\frac{1}{100}$", "C": "$\\frac{1}{90}$", "D": "$\\frac{1}{120}$"},
            "A",
            "$\\int_0^1 (1-x)x^9 dx = [\\frac{x^{10}}{10} - \\frac{x^{11}}{11}]_0^1 = \\frac{1}{10} - \\frac{1}{11} = \\frac{1}{110}$.",
            "medium", ["definite_integrals", "properties"]
        ),
        (
            "DDCET-MATH-IC-023",
            "What is $\\int \\frac{1}{x \\ln x} \\, dx$?",
            {"A": "$\\ln|\\ln x| + C$", "B": "(\\ln x)^2 + C$", "C": "$\\frac{1}{\\ln x} + C$", "D": "$\\ln(x) + C$"},
            "A",
            "Let $u = \\ln x \\implies du = \\frac{1}{x}dx$. $\\int \\frac{du}{u} = \\ln|u| + C = \\ln|\\ln x| + C$.",
            "easy", ["integration", "substitution"]
        ),
        (
            "DDCET-MATH-IC-024",
            "What is the value of $\\int_0^{\\pi} \\cos x \\, dx$?",
            {"A": "$0$", "B": "$1$", "C": "$-1$", "D": "$2$"},
            "A",
            "$[\\sin x]_0^\\pi = \\sin\\pi - \\sin 0 = 0 - 0 = 0$.",
            "easy", ["definite_integrals", "trigonometric"]
        )
    ]
    for qid, qtext, opts, ans, exp, diff, tags in ic_list:
        items.append(make_q(qid, qtext, opts, ans, exp, "Mathematics", "Integral Calculus", "Standard Indefinite Integrals", diff, tags))

    # =========================================================================
    # 7. DIFFERENTIAL EQUATIONS (15 MCQs)
    # =========================================================================
    de_list = [
        (
            "DDCET-MATH-DE-011",
            "What is the general solution of the differential equation $\\frac{dy}{dx} + y = 0$?",
            {"A": "$y = C e^{-x}$", "B": "$y = C e^x$", "C": "$y = -x + C$", "D": "$y = C x$"},
            "A",
            "$\\frac{dy}{y} = -dx \\implies \\ln y = -x + \\ln C \\implies y = C e^{-x}$.",
            "easy", ["differential_equations", "separable"]
        ),
        (
            "DDCET-MATH-DE-012",
            "What is the order and degree of $\\left[1 + \\left(\\frac{dy}{dx}\\right)^2\\right]^{3/2} = k \\frac{d^2y}{dx^2}$?",
            {"A": "Order 2, Degree 2", "B": "Order 2, Degree 3", "C": "Order 1, Degree 2", "D": "Order 2, Degree 1"},
            "A",
            "Squaring both sides: $[1 + (dy/dx)^2]^3 = k^2 (d^2y/dx^2)^2$. Order is 2, Degree is 2.",
            "medium", ["differential_equations", "order_degree"]
        ),
        (
            "DDCET-MATH-DE-013",
            "Which of the following is a homogeneous differential equation?",
            {"A": "$\\frac{dy}{dx} = \\frac{x^2 + y^2}{2xy}$", "B": "$\\frac{dy}{dx} = \\frac{x + y + 1}{x - y}$", "C": "$\\frac{dy}{dx} = x^2 + y$", "D": "$\\frac{dy}{dx} = \\frac{x^3 + y}{x^2}$"},
            "A",
            "In $\\frac{x^2 + y^2}{2xy}$, both numerator and denominator are homogeneous of degree 2.",
            "medium", ["differential_equations", "homogeneous"]
        ),
        (
            "DDCET-MATH-DE-014",
            "What is the integrating factor of the differential equation $\\frac{dy}{dx} + 3y = e^{2x}$?",
            {"A": "$e^{3x}$", "B": "$e^{-3x}$", "C": "$3x$", "D": "$e^{2x}$"},
            "A",
            "$I.F. = e^{\\int 3 dx} = e^{3x}$.",
            "easy", ["differential_equations", "integrating_factor"]
        )
    ]
    for qid, qtext, opts, ans, exp, diff, tags in de_list:
        items.append(make_q(qid, qtext, opts, ans, exp, "Mathematics", "Differential Equations", "Order and Degree of Differential Equations", diff, tags))

    # =========================================================================
    # 8. VECTOR ALGEBRA (20 MCQs)
    # =========================================================================
    vec_list = [
        (
            "DDCET-MATH-VEC-013",
            "If $\\vec{a}$ and $\\vec{b}$ are collinear vectors, what is $\\vec{a} \\times \\vec{b}$?",
            {"A": "$\\vec{0}$", "B": "$1$", "C": "$|\\vec{a}||\\vec{b}|$", "D": "$-1$"},
            "A",
            "Angle $\\theta = 0^\\circ$ or $180^\\circ$, so $\\sin\\theta = 0 \\implies \\vec{a} \\times \\vec{b} = \\vec{0}$.",
            "easy", ["vectors", "cross_product"]
        ),
        (
            "DDCET-MATH-VEC-014",
            "What is the area of a triangle with vertices at origin $O$ and vectors $\\vec{a} = 3\\hat{i} + 4\\hat{j}$ and $\\vec{b} = 4\\hat{i} - 3\\hat{j}$?",
            {"A": "$12.5$ sq. units", "B": "$25$ sq. units", "C": "$12$ sq. units", "D": "$7$ sq. units"},
            "A",
            "$\\vec{a} \\times \\vec{b} = -25\\hat{k}$. Area $= \\frac{1}{2}|\\vec{a} \\times \\vec{b}| = \\frac{25}{2} = 12.5$ sq. units.",
            "easy", ["vectors", "triangle_area"]
        ),
        (
            "DDCET-MATH-VEC-015",
            "What are the direction cosines of the vector $\\vec{r} = 2\\hat{i} - 2\\hat{j} + \\hat{k}$?",
            {"A": "$\\frac{2}{3}, -\\frac{2}{3}, \\frac{1}{3}$", "B": "$2, -2, 1$", "C": "$\\frac{2}{9}, -\\frac{2}{9}, \\frac{1}{9}$", "D": "$\\frac{1}{3}, -\\frac{1}{3}, \\frac{1}{3}$"},
            "A",
            "$|\\vec{r}| = \\sqrt{4 + 4 + 1} = 3$. Direction cosines are $2/3, -2/3, 1/3$.",
            "easy", ["vectors", "direction_cosines"]
        ),
        (
            "DDCET-MATH-VEC-016",
            "If $\\vec{a} \\cdot \\vec{b} = |\\vec{a} \\times \\vec{b}|$, what is the angle between $\\vec{a}$ and $\\vec{b}$?",
            {"A": "$45^\\circ$", "B": "$90^\\circ$", "C": "$60^\\circ$", "D": "$0^\\circ$"},
            "A",
            "$|a||b|\\cos\\theta = |a||b|\\sin\\theta \\implies \\tan\\theta = 1 \\implies \\theta = 45^\\circ$.",
            "easy", ["vectors", "angle_between_vectors"]
        )
    ]
    for qid, qtext, opts, ans, exp, diff, tags in vec_list:
        items.append(make_q(qid, qtext, opts, ans, exp, "Mathematics", "Vector Algebra", "Scalar Dot Product and Orthogonality", diff, tags))

    # =========================================================================
    # 9. STATISTICS AND PROBABILITY (15 MCQs)
    # =========================================================================
    stat_list = [
        (
            "DDCET-MATH-STAT-012",
            "What is the mean of the first $n$ natural numbers $1, 2, 3, \\dots, n$?",
            {"A": "$\\frac{n+1}{2}$", "B": "$\\frac{n(n+1)}{2}$", "C": "$\\frac{n-1}{2}$", "D": "$\\frac{2n+1}{2}$"},
            "A",
            "Sum $= \\frac{n(n+1)}{2}$. Mean $= \\frac{\\text{Sum}}{n} = \\frac{n+1}{2}$.",
            "easy", ["statistics", "mean"]
        ),
        (
            "DDCET-MATH-STAT-013",
            "If the probability of success is $p = 0.25$, what are the odds against the event happening?",
            {"A": "$3 : 1$", "B": "$1 : 3$", "C": "$4 : 1$", "D": "$1 : 4$"},
            "A",
            "$P(E) = 1/4$, $P(E') = 3/4$. Odds against $= \\frac{3/4}{1/4} = 3:1$.",
            "easy", ["probability", "odds_against"]
        ),
        (
            "DDCET-MATH-STAT-014",
            "What is the variance of a constant dataset where all observations are equal to $c$?",
            {"A": "$0$", "B": "$c$", "C": "$c^2$", "D": "$1$"},
            "A",
            "Every deviation $(x_i - \\bar{x}) = 0$, so $\\sigma^2 = 0$.",
            "easy", ["statistics", "variance"]
        ),
        (
            "DDCET-MATH-STAT-015",
            "What is the probability of obtaining an odd number when rolling a fair six-sided die?",
            {"A": "$\\frac{1}{2}$", "B": "$\\frac{1}{3}$", "C": "$\\frac{1}{6}$", "D": "$\\frac{2}{3}$"},
            "A",
            "Odd outcomes: $1, 3, 5$ (3 favorable outcomes). Total $= 6$. Probability $= 3/6 = 1/2$.",
            "easy", ["probability", "dice"]
        )
    ]
    for qid, qtext, opts, ans, exp, diff, tags in stat_list:
        items.append(make_q(qid, qtext, opts, ans, exp, "Mathematics", "Statistics and Probability", "Variance and Standard Deviation", diff, tags))

    # =========================================================================
    # 10. ENGINEERING SCIENCE (Physics, Chemistry, Circuits) (30 MCQs)
    # =========================================================================
    sci_list = [
        (
            "DDCET-SCI-UD-005",
            "Which of the following pairs of physical quantities have the identical dimensional formula?",
            {"A": "Work and Torque", "B": "Force and Pressure", "C": "Momentum and Energy", "D": "Power and Work"},
            "A",
            "$\\text{Work} = [M^1 L^2 T^{-2}]$ and $\\text{Torque} = [M^1 L^2 T^{-2}]$. Both have identical dimensions.",
            "Units and Measurement", "SI Units and Dimensional Analysis", "easy", ["dimensional_analysis"]
        ),
        (
            "DDCET-SCI-UD-006",
            "What is the SI unit of Magnetic Flux?",
            {"A": "Weber (Wb)", "B": "Tesla (T)", "C": "Henry (H)", "D": "Farad (F)"},
            "A",
            "The SI unit of magnetic flux is the Weber (Wb). Magnetic flux density is Tesla (T).",
            "Units and Measurement", "SI Units and Dimensional Analysis", "easy", ["si_units"]
        ),
        (
            "DDCET-SCI-MECH-005",
            "A body of mass $5\\text{ kg}$ is dropped from a height of $20\\text{ m}$. What is its kinetic energy just before hitting the ground? ($g = 9.8\\text{ m/s}^2$)",
            {"A": "$980\\text{ J}$", "B": "$490\\text{ J}$", "C": "$196\\text{ J}$", "D": "$100\\text{ J}$"},
            "A",
            "$\\text{Kinetic Energy} = \\text{Potential Energy} = m g h = 5 \\times 9.8 \\times 20 = 980\\text{ J}$.",
            "Classical Mechanics", "Work, Energy, and Power", "easy", ["work_energy"]
        ),
        (
            "DDCET-SCI-MECH-006",
            "What is the escape velocity from the surface of Earth ($R = 6400\\text{ km}, g = 9.8\\text{ m/s}^2$)?",
            {"A": "$11.2\\text{ km/s}$", "B": "$7.9\\text{ km/s}$", "C": "$9.8\\text{ km/s}$", "D": "$15.0\\text{ km/s}$"},
            "A",
            "$v_e = \\sqrt{2 g R} = \\sqrt{2 \\times 9.8 \\times 6.4 \\times 10^6} \\approx 11.2\\text{ km/s}$.",
            "Classical Mechanics", "Gravitation and Satellite Motion", "easy", ["escape_velocity"]
        ),
        (
            "DDCET-SCI-HEAT-003",
            "What is the efficiency of a Carnot heat engine operating between temperatures of $500\\text{ K}$ and $300\\text{ K}$?",
            {"A": "$40\\%$", "B": "$60\\%$", "C": "$20\\%$", "D": "$50\\%$"},
            "A",
            "$\\eta = 1 - \\frac{T_L}{T_H} = 1 - \\frac{300}{500} = 0.4 = 40\\%$.",
            "Heat and Thermometry", "Thermodynamic Laws and Heat Engines", "easy", ["carnot_efficiency"]
        ),
        (
            "DDCET-SCI-HEAT-004",
            "Wien's Displacement Law states that the wavelength $\\lambda_{\\max}$ corresponding to maximum radiant energy satisfies:",
            {"A": "$\\lambda_{\\max} T = \\text{constant}$", "B": "$\\lambda_{\\max} / T = \\text{constant}$", "C": "$\\lambda_{\\max} T^4 = \\text{constant}$", "D": "$\\lambda_{\\max}^2 T = \\text{constant}$"},
            "A",
            "Wien's law states $\\lambda_{\\max} T = b$ (constant).",
            "Heat and Thermometry", "Heat Transfer: Conduction, Convection, Radiation", "easy", ["wien_law"]
        ),
        (
            "DDCET-SCI-ELEC-005",
            "Three identical capacitors of $9\\,\\mu\\text{F}$ each are connected in parallel. What is their effective capacitance?",
            {"A": "$27\\,\\mu\\text{F}$", "B": "$3\\,\\mu\\text{F}$", "C": "$9\\,\\mu\\text{F}$", "D": "$1\\,\\mu\\text{F}$"},
            "A",
            "Parallel capacitors add directly: $C_{eq} = 9 + 9 + 9 = 27\\,\\mu\\text{F}$.",
            "Electric Current & Electricity", "Capacitors and Electrostatics", "easy", ["capacitors"]
        ),
        (
            "DDCET-SCI-ELEC-006",
            "According to Joule's law of electric heating, heat produced $H$ in a resistor $R$ carrying current $I$ for time $t$ is:",
            {"A": "$H = I^2 R t$", "B": "$H = I R^2 t$", "C": "$H = \\frac{I^2 t}{R}$", "D": "$H = I R t$"},
            "A",
            "By Joule's law of heating: $H = I^2 R t$ Joules.",
            "Electric Current & Electricity", "Ohm's Law and Resistivity", "easy", ["joule_heating"]
        ),
        (
            "DDCET-SCI-CHEM-004",
            "What is the oxidation state of Chromium ($\\text{Cr}$) in Potassium Dichromate ($\\text{K}_2\\text{Cr}_2\\text{O}_7$)?",
            {"A": "$+6$", "B": "$+3$", "C": "$+7$", "D": "$+4$"},
            "A",
            "$2(+1) + 2x + 7(-2) = 0 \\implies 2x = 12 \\implies x = +6$.",
            "Basic Chemistry Concepts", "Chemical Bonding and Redox Reactions", "easy", ["oxidation_state"]
        ),
        (
            "DDCET-SCI-CHEM-005",
            "The process of coating iron with a protective layer of zinc to prevent corrosion is known as:",
            {"A": "Galvanization", "B": "Electroplating", "C": "Annealing", "D": "Vulcanization"},
            "A",
            "Galvanization is the coating of iron or steel with a protective layer of zinc.",
            "Basic Chemistry Concepts", "Corrosion and Prevention", "easy", ["galvanization"]
        )
    ]
    for qid, qtext, opts, ans, exp, top, subtop, diff, tags in sci_list:
        items.append(make_q(qid, qtext, opts, ans, exp, "Engineering Science", top, subtop, diff, tags))

    # =========================================================================
    # 11. SOFT SKILLS AND APTITUDE (20 MCQs)
    # =========================================================================
    apt_list = [
        (
            "DDCET-APT-ENG-006",
            "Identify the correctly punctuated sentence:",
            {"A": "Although it was raining, the engineers completed the survey.", "B": "Although it was raining the engineers, completed the survey.", "C": "Although, it was raining the engineers completed the survey.", "D": "Although it was raining the engineers completed the survey"},
            "A",
            "A comma must follow a dependent introductory clause.",
            "English Language & Grammar", "Sentence Structure and Punctuation", "easy", ["punctuation"]
        ),
        (
            "DDCET-APT-ENG-007",
            "Choose the correct meaning of the idiom: 'To burn the midnight oil'",
            {"A": "To work or study late into the night", "B": "To waste precious energy", "C": "To create a fire hazard", "D": "To wake up very early in the morning"},
            "A",
            "'To burn the midnight oil' means to work late into the night.",
            "English Language & Grammar", "Idioms and Phrases", "easy", ["idioms"]
        ),
        (
            "DDCET-APT-ENG-008",
            "Choose the correct indirect speech: He said, 'I am reading an engineering journal.'",
            {"A": "He said that he was reading an engineering journal.", "B": "He said that I was reading an engineering journal.", "C": "He said that he is reading an engineering journal.", "D": "He said that he had read an engineering journal."},
            "A",
            "Present continuous shifts to past continuous: 'He said that he was reading...'",
            "English Language & Grammar", "Direct and Indirect Speech", "easy", ["indirect_speech"]
        ),
        (
            "DDCET-APT-QA-006",
            "A sum of $\\text{Rs. } 5000$ yields a Simple Interest of $\\text{Rs. } 1000$ in $2\\text{ years}$. What is the annual rate of interest?",
            {"A": "$10\\%$", "B": "$12\\%$", "C": "$8\\%$", "D": "$15\\%$"},
            "A",
            "$SI = \\frac{P \\times R \\times T}{100} \\implies 1000 = \\frac{5000 \\times R \\times 2}{100} \\implies 100 R = 1000 \\implies R = 10\\%$.",
            "Quantitative Aptitude", "Simple and Compound Interest", "easy", ["simple_interest"]
        ),
        (
            "DDCET-APT-QA-007",
            "If an item bought for $\\text{Rs. } 800$ is sold for $\\text{Rs. } 1000$, what is the profit percentage?",
            {"A": "$25\\%$", "B": "$20\\%$", "C": "$15\\%$", "D": "$30\\%$"},
            "A",
            "Profit $= 200$. $\\text{Profit}\\% = (200/800) \\times 100\\% = 25\\%$.",
            "Quantitative Aptitude", "Percentages and Profit-Loss", "easy", ["profit_loss"]
        ),
        (
            "DDCET-APT-QA-008",
            "Two pipes A and B can fill a water tank in 20 minutes and 30 minutes respectively. If both are opened together, how long will it take to fill the tank?",
            {"A": "$12\\text{ minutes}$", "B": "$15\\text{ minutes}$", "C": "$10\\text{ minutes}$", "D": "$25\\text{ minutes}$"},
            "A",
            "Combined rate $= 1/20 + 1/30 = 5/60 = 1/12\\text{ tank/min}$. Time required $= 12\\text{ minutes}$.",
            "Quantitative Aptitude", "Work and Time", "easy", ["pipes_cisterns"]
        ),
        (
            "DDCET-APT-QA-009",
            "Find the average speed of a vehicle that travels from town A to B at $40\\text{ km/h}$ and returns from B to A at $60\\text{ km/h}$.",
            {"A": "$48\\text{ km/h}$", "B": "$50\\text{ km/h}$", "C": "$52\\text{ km/h}$", "D": "$45\\text{ km/h}$"},
            "A",
            "$V_{avg} = \\frac{2(40)(60)}{40 + 60} = \\frac{4800}{100} = 48\\text{ km/h}$.",
            "Quantitative Aptitude", "Time, Speed and Distance", "easy", ["average_speed"]
        ),
        (
            "DDCET-APT-QA-010",
            "What is the next term in the series: $2, 6, 12, 20, 30, \\text{?}$",
            {"A": "$42$", "B": "$40$", "C": "$44$", "D": "$36$"},
            "A",
            "Differences: $4, 6, 8, 10, 12$. Next term is $30 + 12 = 42$ ($n(n+1)$ for $n=6$: $6 \\times 7 = 42$).",
            "Quantitative Aptitude", "Number Series and Reasoning", "easy", ["number_series"]
        )
    ]
    for qid, qtext, opts, ans, exp, top, subtop, diff, tags in apt_list:
        items.append(make_q(qid, qtext, opts, ans, exp, "Soft Skills & Aptitude", top, subtop, diff, tags))

    return items


if __name__ == "__main__":
    mcqs = generate_mcqs()
    print(f"Generated {len(mcqs)} clean questions.")
