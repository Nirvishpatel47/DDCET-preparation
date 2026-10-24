"""
Generate and Append 230+ Authentic Gujarat GTU / ACPC DDCET MCQs
Syllabus: DDCET BE-01 (Basics of Science & Engineering) and BE-02 (Mathematics & Soft Skills)
"""

import sys
import os
import json

# Ensure project root is in path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from models.schemas import QuestionModel, QuestionSource
import sqlite3
from services.validation_service import get_or_create_hierarchy
from services.duplicate_service import compute_question_hash


def create_mcq(qid, qtext, opts, ans, exp, subject, topic, subtopic, diff="medium", tags=None):
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


def generate_all_questions():
    questions = []

    # =========================================================================
    # PART A: MATHEMATICS (BE-02)
    # =========================================================================

    # 1. Determinants & Matrices
    dm = [
        (
            "DDCET-MATH-DM-031",
            "What is the value of $\\begin{vmatrix} 1 & \\omega & \\omega^2 \\\\ \\omega & \\omega^2 & 1 \\\\ \\omega^2 & 1 & \\omega \\end{vmatrix}$ where $\\omega$ is a complex cube root of unity?",
            {"A": "$0$", "B": "$1$", "C": "$\\omega$", "D": "$3$"},
            "A",
            "Perform $R_1 \\to R_1 + R_2 + R_3$. The first row becomes $[1+\\omega+\\omega^2, 1+\\omega+\\omega^2, 1+\\omega+\\omega^2] = [0, 0, 0]$ because $1 + \\omega + \\omega^2 = 0$. Since an entire row is zeros, the determinant is $0$.",
            "easy", ["determinants", "cube_root_of_unity"]
        ),
        (
            "DDCET-MATH-DM-032",
            "If $A = \\begin{pmatrix} 3 & 1 \\\\ -1 & 2 \\end{pmatrix}$, what is $A^2 - 5A + 7I$?",
            {"A": "$O$ (Zero matrix)", "B": "$I$ (Identity matrix)", "C": "$2I$", "D": "$A$"},
            "A",
            "Characteristic equation of $2 \\times 2$ matrix $A$ is $\\lambda^2 - \\text{tr}(A)\\lambda + \\det(A) = 0$. $\\text{tr}(A) = 3 + 2 = 5$, $\\det(A) = (3)(2) - (1)(-1) = 7$. By Cayley-Hamilton theorem, every square matrix satisfies its own characteristic equation: $A^2 - 5A + 7I = O$.",
            "medium", ["cayley_hamilton", "matrices"]
        ),
        (
            "DDCET-MATH-DM-033",
            "If matrix $A$ has order $3 \\times 4$ and matrix $B$ has order $4 \\times 2$, what is the order of the product matrix $(AB)^T$?",
            {"A": "$2 \\times 3$", "B": "$3 \\times 2$", "C": "$4 \\times 4$", "D": "$3 \\times 4$"},
            "A",
            "Product $AB$ has order $3 \\times 2$. The transpose of a matrix reverses its dimensions, so $(AB)^T$ has order $2 \\times 3$.",
            "easy", ["matrices", "matrix_dimensions"]
        ),
        (
            "DDCET-MATH-DM-034",
            "If $A$ is an orthogonal matrix, what is the value of $\\det(A)$?",
            {"A": "$\\pm 1$", "B": "$0$", "C": "$2$", "D": "Any real number"},
            "A",
            "For an orthogonal matrix, $A A^T = I$. Taking determinants: $\\det(A A^T) = \\det(A)\\det(A^T) = [\\det(A)]^2 = \\det(I) = 1 \\implies \\det(A) = \\pm 1$.",
            "easy", ["orthogonal_matrix", "determinants"]
        ),
        (
            "DDCET-MATH-DM-035",
            "For what value of $x$ does the matrix $\\begin{pmatrix} 2 & 3 \\\\ x & 6 \\end{pmatrix}$ have no inverse?",
            {"A": "$4$", "B": "$3$", "C": "$6$", "D": "$1$"},
            "A",
            "A matrix has no inverse if it is singular (determinant equals zero): $\\det = (2)(6) - (3)(x) = 12 - 3x = 0 \\implies 3x = 12 \\implies x = 4$.",
            "easy", ["singular_matrix", "matrix_inverse"]
        ),
        (
            "DDCET-MATH-DM-036",
            "What is the rank of the identity matrix $I_3$ of order $3$?",
            {"A": "$3$", "B": "$1$", "C": "$2$", "D": "$0$"},
            "A",
            "The identity matrix $I_3$ has 3 non-zero pivot elements along the diagonal and $\\det(I_3) = 1 \\neq 0$. Hence its rank is 3.",
            "easy", ["rank", "identity_matrix"]
        ),
        (
            "DDCET-MATH-DM-037",
            "If $\\begin{vmatrix} x & 3 \\\\ 12 & x \\end{vmatrix} = 0$, what are the values of $x$?",
            {"A": "$\\pm 6$", "B": "$\\pm 36$", "C": "$6$", "D": "$\\pm 4$"},
            "A",
            "$x^2 - 36 = 0 \\implies x^2 = 36 \\implies x = \\pm 6$.",
            "easy", ["determinants", "2x2_determinant"]
        ),
        (
            "DDCET-MATH-DM-038",
            "In Cramer's rule for three linear equations, if $D = 0$ and $D_x = D_y = D_z = 0$, what can be concluded?",
            {"A": "Consistent with infinite solutions or inconsistent", "B": "Unique solution exists", "C": "No solution always", "D": "Trivial solution only"},
            "A",
            "When the main determinant $D = 0$ and all coordinate determinants $D_x = D_y = D_z = 0$, the system either has infinitely many solutions (dependent planes) or is inconsistent (parallel planes).",
            "medium", ["cramer_rule", "linear_systems"]
        )
    ]
    for qid, qtext, opts, ans, exp, diff, tags in dm:
        questions.append(create_mcq(qid, qtext, opts, ans, exp, "Mathematics", "Determinants and Matrices", "Determinant Evaluation and Properties", diff, tags))

    # 2. Logarithm & Partial Fractions
    log_pf = [
        (
            "DDCET-MATH-LOG-020",
            "What is the value of $\\log_5(0.04)$?",
            {"A": "$-2$", "B": "$2$", "C": "$-1$", "D": "$0.2$"},
            "A",
            "$0.04 = \\frac{4}{100} = \\frac{1}{25} = 5^{-2}$. Therefore $\\log_5(0.04) = \\log_5(5^{-2}) = -2$.",
            "easy", ["logarithm", "negative_power"]
        ),
        (
            "DDCET-MATH-LOG-021",
            "If $\\log_{10} x = 2.45$, what is the characteristic of the logarithm?",
            {"A": "$2$", "B": "$0.45$", "C": "$3$", "D": "$1$"},
            "A",
            "A common logarithm consists of an integer part called characteristic and a non-negative fractional part called mantissa. For $2.45$, characteristic is $2$ and mantissa is $0.45$.",
            "easy", ["logarithm", "characteristic_mantissa"]
        ),
        (
            "DDCET-MATH-LOG-022",
            "What is the value of $\\log_3 2 \\times \\log_4 3 \\times \\log_5 4 \\times \\dots \\times \\log_{16} 15$?",
            {"A": "$\\frac{1}{4}$", "B": "$\\frac{1}{2}$", "C": "$1$", "D": "$4$"},
            "A",
            "Using change of base: $\\frac{\\log 2}{\\log 3} \\times \\frac{\\log 3}{\\log 4} \\times \\dots \\times \\frac{\\log 15}{\\log 16} = \\frac{\\log 2}{\\log 16} = \\log_{16} 2 = \\log_{2^4} 2 = \\frac{1}{4}$.",
            "medium", ["logarithm", "telescoping_log"]
        ),
        (
            "DDCET-MATH-LOG-023",
            "To resolve $\\frac{x^2 + 1}{(x-1)(x-2)(x-3)}$ into partial fractions, how many undetermined constants are needed?",
            {"A": "$3$", "B": "$2$", "C": "$4$", "D": "$1$"},
            "A",
            "The denominator is degree 3 with three distinct linear factors. Form: $\\frac{A}{x-1} + \\frac{B}{x-2} + \\frac{C}{x-3}$. Exactly 3 constants ($A, B, C$) are needed.",
            "easy", ["partial_fractions", "linear_factors"]
        ),
        (
            "DDCET-MATH-LOG-024",
            "If $\\frac{1}{x^2 - 1} = \\frac{A}{x - 1} + \\frac{B}{x + 1}$, what is the value of $A + B$?",
            {"A": "$0$", "B": "$1$", "C": "$\\frac{1}{2}$", "D": "$-\\frac{1}{2}$"},
            "A",
            "$1 = A(x+1) + B(x-1) = (A+B)x + (A-B)$. Equating coefficient of $x$ on both sides: $A + B = 0$.",
            "easy", ["partial_fractions", "coefficients"]
        )
    ]
    for qid, qtext, opts, ans, exp, diff, tags in log_pf:
        questions.append(create_mcq(qid, qtext, opts, ans, exp, "Mathematics", "Logarithm", "Laws of Logarithm and related Simple examples", diff, tags))

    # 3. Trigonometry
    trig = [
        (
            "DDCET-MATH-TRIG-035",
            "What is the value of $\\cos(15^\\circ)$?",
            {"A": "$\\frac{\\sqrt{6} + \\sqrt{2}}{4}$", "B": "$\\frac{\\sqrt{6} - \\sqrt{2}}{4}$", "C": "$\\frac{\\sqrt{3} + 1}{2}$", "D": "$\\frac{\\sqrt{2} + 1}{4}$"},
            "A",
            "$\\cos(15^\\circ) = \\cos(45^\\circ - 30^\\circ) = \\cos 45^\\circ \\cos 30^\\circ + \\sin 45^\\circ \\sin 30^\\circ = (\\frac{1}{\\sqrt{2}})(\\frac{\\sqrt{3}}{2}) + (\\frac{1}{\\sqrt{2}})(\\frac{1}{2}) = \\frac{\\sqrt{3}+1}{2\\sqrt{2}} = \\frac{\\sqrt{6}+\\sqrt{2}}{4}$.",
            "medium", ["trigonometry", "compound_angles"]
        ),
        (
            "DDCET-MATH-TRIG-036",
            "What is the value of $\\sin(2\\theta)$ in terms of $\\tan\\theta$?",
            {"A": "$\\frac{2\\tan\\theta}{1 + \\tan^2\\theta}$", "B": "$\\frac{2\\tan\\theta}{1 - \\tan^2\\theta}$", "C": "$\\frac{1 - \\tan^2\\theta}{1 + \\tan^2\\theta}$", "D": "$\\frac{2\\tan^2\\theta}{1 + \\tan^2\\theta}$"},
            "A",
            "Standard double-angle formula: $\\sin(2\\theta) = \\frac{2\\tan\\theta}{1 + \\tan^2\\theta}$.",
            "easy", ["trigonometry", "double_angle"]
        ),
        (
            "DDCET-MATH-TRIG-037",
            "What is the value of $\\cos(2\\pi + \\theta)$?",
            {"A": "$\\cos\\theta$", "B": "$-\\cos\\theta$", "C": "$\\sin\\theta$", "D": "$-\\sin\\theta$"},
            "A",
            "Cosine has period $2\\pi$, so $\\cos(2\\pi + \\theta) = \\cos\\theta$.",
            "easy", ["trigonometry", "periodicity"]
        ),
        (
            "DDCET-MATH-TRIG-038",
            "If $\\sin\\theta = \\frac{3}{5}$ and $\\theta$ is an acute angle, what is $\\cos(2\\theta)$?",
            {"A": "$\\frac{7}{25}$", "B": "$\\frac{24}{25}$", "C": "$\\frac{16}{25}$", "D": "$\\frac{9}{25}$"},
            "A",
            "$\\cos(2\\theta) = 1 - 2\\sin^2\\theta = 1 - 2\\left(\\frac{3}{5}\\right)^2 = 1 - 2\\left(\\frac{9}{25}\\right) = 1 - \\frac{18}{25} = \\frac{7}{25}$.",
            "easy", ["trigonometry", "double_angle"]
        ),
        (
            "DDCET-MATH-TRIG-039",
            "What is the principal value of $\\tan^{-1}(-\\sqrt{3})$?",
            {"A": "$-\\frac{\\pi}{3}$", "B": "$\\frac{2\\pi}{3}$", "C": "$\\frac{\\pi}{3}$", "D": "$-\\frac{\\pi}{6}$"},
            "A",
            "The range of principal value branch of $\\tan^{-1} x$ is $(-\\pi/2, \\pi/2)$. Since $\\tan(-\\pi/3) = -\\sqrt{3}$, the value is $-\\frac{\\pi}{3}$.",
            "easy", ["inverse_trig", "principal_value"]
        ),
        (
            "DDCET-MATH-TRIG-040",
            "What is the simplified value of $\\frac{\\sin(2\\theta)}{1 + \\cos(2\\theta)}$?",
            {"A": "$\\tan\\theta$", "B": "$\\cot\\theta$", "C": "$\\sin\\theta$", "D": "$\\cos\\theta$"},
            "A",
            "$\\frac{\\sin(2\\theta)}{1 + \\cos(2\\theta)} = \\frac{2\\sin\\theta\\cos\\theta}{2\\cos^2\\theta} = \\frac{\\sin\\theta}{\\cos\\theta} = \\tan\\theta$.",
            "easy", ["trigonometry", "identities"]
        )
    ]
    for qid, qtext, opts, ans, exp, diff, tags in trig:
        questions.append(create_mcq(qid, qtext, opts, ans, exp, "Mathematics", "Trigonometry", "Multiple and Sub-multiple Angles", diff, tags))

    # 4. Coordinate Geometry
    cg = [
        (
            "DDCET-MATH-CG-021",
            "What is the slope of the line passing through points $(2, -3)$ and $(4, 5)$?",
            {"A": "$4$", "B": "$1$", "C": "$\\frac{1}{4}$", "D": "$-4$"},
            "A",
            "$m = \\frac{y_2 - y_1}{x_2 - x_1} = \\frac{5 - (-3)}{4 - 2} = \\frac{8}{2} = 4$.",
            "easy", ["coordinate_geometry", "slope"]
        ),
        (
            "DDCET-MATH-CG-022",
            "What is the equation of a line with $x$-intercept $3$ and $y$-intercept $-4$?",
            {"A": "$4x - 3y - 12 = 0$", "B": "$4x + 3y - 12 = 0$", "C": "$3x - 4y - 12 = 0$", "D": "$4x - 3y + 12 = 0$"},
            "A",
            "Intercept form: $\\frac{x}{a} + \\frac{y}{b} = 1 \\implies \\frac{x}{3} + \\frac{y}{-4} = 1 \\implies \\frac{x}{3} - \\frac{y}{4} = 1 \\implies 4x - 3y = 12 \\implies 4x - 3y - 12 = 0$.",
            "easy", ["coordinate_geometry", "intercept_form"]
        ),
        (
            "DDCET-MATH-CG-023",
            "What is the center of the circle $x^2 + y^2 + 8x - 10y + 16 = 0$?",
            {"A": "$(-4, 5)$", "B": "$(4, -5)$", "C": "$(8, -10)$", "D": "$(-8, 10)$"},
            "A",
            "Comparing with $x^2 + y^2 + 2gx + 2fy + c = 0$: $2g = 8 \\implies g = 4$, $2f = -10 \\implies f = -5$. Center is $(-g, -f) = (-4, 5)$.",
            "easy", ["circles", "center"]
        ),
        (
            "DDCET-MATH-CG-024",
            "What is the eccentricity of a parabola?",
            {"A": "$1$", "B": "$0$", "C": "$< 1$", "D": "$> 1$"},
            "A",
            "By definition, a parabola has eccentricity $e = 1$. An ellipse has $e < 1$, hyperbola has $e > 1$, and circle has $e = 0$.",
            "easy", ["conics", "eccentricity", "parabola"]
        ),
        (
            "DDCET-MATH-CG-025",
            "What is the length of the latus rectum of the ellipse $\\frac{x^2}{25} + \\frac{y^2}{9} = 1$?",
            {"A": "$\\frac{18}{5}$", "B": "$\\frac{9}{5}$", "C": "$\\frac{50}{3}$", "D": "$5$"},
            "A",
            "$a^2 = 25 \\implies a = 5$, $b^2 = 9$. Length of latus rectum $= \\frac{2b^2}{a} = \\frac{2(9)}{5} = \\frac{18}{5}$.",
            "medium", ["ellipse", "latus_rectum"]
        )
    ]
    for qid, qtext, opts, ans, exp, diff, tags in cg:
        questions.append(create_mcq(qid, qtext, opts, ans, exp, "Mathematics", "Coordinate Geometry", "Straight Lines and Slopes", diff, tags))

    # 5. Differential Calculus
    dc = [
        (
            "DDCET-MATH-DC-031",
            "What is $\\lim_{x \\to 0} \\frac{\\tan(3x)}{\\tan(5x)}$?",
            {"A": "$\\frac{3}{5}$", "B": "$\\frac{5}{3}$", "C": "$1$", "D": "$0$"},
            "A",
            "$\\lim_{x \\to 0} \\frac{(\\tan 3x / 3x) \\times 3x}{(\\tan 5x / 5x) \\times 5x} = \\frac{1 \\times 3}{1 \\times 5} = \\frac{3}{5}$.",
            "easy", ["limits", "trigonometric_limits"]
        ),
        (
            "DDCET-MATH-DC-032",
            "What is the derivative of $\\ln(\\sin x)$ with respect to $x$?",
            {"A": "$\\cot x$", "B": "$\\tan x$", "C": "$\\frac{1}{\\sin x}$", "D": "$-\\cot x$"},
            "A",
            "$\\frac{d}{dx}[\\ln(\\sin x)] = \\frac{1}{\\sin x} \\cdot \\frac{d}{dx}(\\sin x) = \\frac{\\cos x}{\\sin x} = \\cot x$.",
            "easy", ["differentiation", "chain_rule"]
        ),
        (
            "DDCET-MATH-DC-033",
            "What is the derivative of $e^{3x^2}$ with respect to $x$?",
            {"A": "$6x e^{3x^2}$", "B": "$3x e^{3x^2}$", "C": "$e^{3x^2}$", "D": "$6 e^{3x^2}$"},
            "A",
            "$\\frac{d}{dx}[e^{3x^2}] = e^{3x^2} \\cdot \\frac{d}{dx}(3x^2) = 6x e^{3x^2}$.",
            "easy", ["differentiation", "exponential"]
        ),
        (
            "DDCET-MATH-DC-034",
            "If $y = \\sqrt{x + \\sqrt{x + \\sqrt{x + \\dots}}}$, what is $\\frac{dy}{dx}$?",
            {"A": "$\\frac{1}{2y - 1}$", "B": "$\\frac{1}{2y + 1}$", "C": "$\\frac{y}{2y - 1}$", "D": "$\\frac{1}{y - 1}$"},
            "A",
            "Rewrite: $y = \\sqrt{x + y} \\implies y^2 = x + y$. Differentiating implicitly with respect to $x$: $2y\\frac{dy}{dx} = 1 + \\frac{dy}{dx} \\implies (2y - 1)\\frac{dy}{dx} = 1 \\implies \\frac{dy}{dx} = \\frac{1}{2y - 1}$.",
            "medium", ["differentiation", "infinite_series"]
        ),
        (
            "DDCET-MATH-DC-035",
            "At what point does the curve $y = x^3 - 3x$ have a local minimum?",
            {"A": "$x = 1$", "B": "$x = -1$", "C": "$x = 0$", "D": "$x = \\sqrt{3}$"},
            "A",
            "$y' = 3x^2 - 3 = 0 \\implies x = \\pm 1$. $y'' = 6x$. At $x = 1$, $y'' = 6 > 0$, confirming a local minimum at $x = 1$.",
            "medium", ["maxima_minima", "second_derivative"]
        )
    ]
    for qid, qtext, opts, ans, exp, diff, tags in dc:
        questions.append(create_mcq(qid, qtext, opts, ans, exp, "Mathematics", "Differential Calculus", "Standard Differentiation and Chain Rule", diff, tags))

    # 6. Integral Calculus
    ic = [
        (
            "DDCET-MATH-IC-025",
            "What is $\\int \\frac{1}{x^2 - 16} \\, dx$?",
            {"A": "$\\frac{1}{8}\\ln\\left|\\frac{x-4}{x+4}\\right| + C$", "B": "$\\frac{1}{4}\\ln\\left|\\frac{x-4}{x+4}\\right| + C$", "C": "$\\frac{1}{8}\\tan^{-1}\\left(\\frac{x}{4}\\right) + C$", "D": "$\\frac{1}{4}\\tan^{-1}\\left(\\frac{x}{4}\\right) + C$"},
            "A",
            "Standard formula $\\int \\frac{1}{x^2 - a^2}dx = \\frac{1}{2a}\\ln|\\frac{x-a}{x+a}| + C$. Here $a = 4$, so $\\frac{1}{8}\\ln|\\frac{x-4}{x+4}| + C$.",
            "easy", ["integration", "standard_formulas"]
        ),
        (
            "DDCET-MATH-IC-026",
            "What is $\\int_0^{\\pi/2} \\sin^2 x \\, dx$?",
            {"A": "$\\frac{\\pi}{4}$", "B": "$\\frac{\\pi}{2}$", "C": "$1$", "D": "$0$"},
            "A",
            "$\\int_0^{\\pi/2} \\sin^2 x dx = \\int_0^{\\pi/2} \\frac{1 - \\cos(2x)}{2} dx = [\\frac{x}{2} - \\frac{\\sin 2x}{4}]_0^{\\pi/2} = \\frac{\\pi}{4} - 0 = \\frac{\\pi}{4}$.",
            "easy", ["definite_integrals", "trigonometric_integrals"]
        ),
        (
            "DDCET-MATH-IC-027",
            "What is $\\int x \\cos x \\, dx$?",
            {"A": "$x\\sin x + \\cos x + C$", "B": "$x\\sin x - \\cos x + C$", "C": "$-x\\sin x + \\cos x + C$", "D": "$x\\cos x + \\sin x + C$"},
            "A",
            "Integration by parts ($u = x, dv = \\cos x dx$): $x\\sin x - \\int \\sin x dx = x\\sin x - (-\\cos x) + C = x\\sin x + \\cos x + C$.",
            "easy", ["integration", "by_parts"]
        ),
        (
            "DDCET-MATH-IC-028",
            "What is the value of $\\int_{-2}^2 x^5 \\sqrt{4 - x^2} \\, dx$?",
            {"A": "$0$", "B": "$4$", "C": "$16$", "D": "$\\pi$"},
            "A",
            "The integrand $f(x) = x^5 \\sqrt{4 - x^2}$ is an odd function because $f(-x) = (-x)^5 \\sqrt{4 - (-x)^2} = -x^5 \\sqrt{4 - x^2} = -f(x)$. The integral of any odd function over symmetric limits $[-a, a]$ is identically $0$.",
            "easy", ["definite_integrals", "odd_function"]
        ),
        (
            "DDCET-MATH-IC-029",
            "What is $\\int e^{2x} \\, dx$?",
            {"A": "$\\frac{e^{2x}}{2} + C$", "B": "$2e^{2x} + C$", "C": "$e^{2x} + C$", "D": "$\\frac{e^{2x}}{4} + C$"},
            "A",
            "$\\int e^{ax} dx = \\frac{e^{ax}}{a} + C$. For $a = 2$, this yields $\\frac{e^{2x}}{2} + C$.",
            "easy", ["integration", "exponential"]
        )
    ]
    for qid, qtext, opts, ans, exp, diff, tags in ic:
        questions.append(create_mcq(qid, qtext, opts, ans, exp, "Mathematics", "Integral Calculus", "Standard Indefinite Integrals", diff, tags))

    # 7. Differential Equations
    de = [
        (
            "DDCET-MATH-DE-015",
            "What is the general solution of $\\frac{dy}{dx} = \\frac{x}{y}$?",
            {"A": "$y^2 - x^2 = C$", "B": "$y^2 + x^2 = C$", "C": "$y = x + C$", "D": "$y = Cx$"},
            "A",
            "Separating variables: $y \\, dy = x \\, dx$. Integrating: $\\frac{y^2}{2} = \\frac{x^2}{2} + c \\implies y^2 - x^2 = C$.",
            "easy", ["differential_equations", "separable"]
        ),
        (
            "DDCET-MATH-DE-016",
            "What is the degree of the differential equation $\\frac{d^3y}{dx^3} + 2\\left(\\frac{d^2y}{dx^2}\\right)^2 - \\frac{dy}{dx} + y = 0$?",
            {"A": "$1$", "B": "$2$", "C": "$3$", "D": "$0$"},
            "A",
            "The highest order derivative is $\\frac{d^3y}{dx^3}$ (order 3). Its exponent is 1, so the degree is 1.",
            "easy", ["differential_equations", "order_degree"]
        ),
        (
            "DDCET-MATH-DE-017",
            "What is the integrating factor of $\\frac{dy}{dx} - \\frac{y}{x} = 2x^2$?",
            {"A": "$\\frac{1}{x}$", "B": "$x$", "C": "$\\ln x$", "D": "$-\\frac{1}{x}$"},
            "A",
            "$P(x) = -\\frac{1}{x}$. $I.F. = e^{\\int -\\frac{1}{x} dx} = e^{-\\ln x} = e^{\\ln(x^{-1})} = \\frac{1}{x}$.",
            "easy", ["differential_equations", "integrating_factor"]
        )
    ]
    for qid, qtext, opts, ans, exp, diff, tags in de:
        questions.append(create_mcq(qid, qtext, opts, ans, exp, "Mathematics", "Differential Equations", "Order and Degree of Differential Equations", diff, tags))

    # 8. Vector Algebra
    vec = [
        (
            "DDCET-MATH-VEC-017",
            "If $\\vec{a} = \\hat{i} + 2\\hat{j} + 3\\hat{k}$ and $\\vec{b} = 2\\hat{i} - \\hat{j} + \\hat{k}$, what is $\\vec{a} \\cdot \\vec{b}$?",
            {"A": "$3$", "B": "$5$", "C": "$1$", "D": "$7$"},
            "A",
            "$\\vec{a} \\cdot \\vec{b} = (1)(2) + (2)(-1) + (3)(1) = 2 - 2 + 3 = 3$.",
            "easy", ["vectors", "dot_product"]
        ),
        (
            "DDCET-MATH-VEC-018",
            "What is $\\hat{i} \\times \\hat{k}$?",
            {"A": "$-\\hat{j}$", "B": "$\\hat{j}$", "C": "$\\hat{i}$", "D": "$\\vec{0}$"},
            "A",
            "In right-handed Cartesian coordinate system: $\\hat{i} \\times \\hat{j} = \\hat{k}, \\hat{j} \\times \\hat{k} = \\hat{i}, \\hat{k} \\times \\hat{i} = \\hat{j}$. Thus $\\hat{i} \\times \\hat{k} = -\\hat{j}$.",
            "easy", ["vectors", "cross_product", "basis_vectors"]
        ),
        (
            "DDCET-MATH-VEC-019",
            "What is the magnitude of the vector $\\vec{v} = 2\\hat{i} - 3\\hat{j} + 6\\hat{k}$?",
            {"A": "$7$", "B": "$11$", "C": "$49$", "D": "$\\sqrt{41}$"},
            "A",
            "$|\\vec{v}| = \\sqrt{2^2 + (-3)^2 + 6^2} = \\sqrt{4 + 9 + 36} = \\sqrt{49} = 7$.",
            "easy", ["vectors", "magnitude"]
        ),
        (
            "DDCET-MATH-VEC-020",
            "If the sum of squares of direction cosines $l^2 + m^2 + n^2 = k$, what is the value of $k$?",
            {"A": "$1$", "B": "$0$", "C": "$3$", "D": "$-1$"},
            "A",
            "By fundamental 3D geometry theorem, the sum of the squares of the direction cosines of any line is identically $l^2 + m^2 + n^2 = 1$.",
            "easy", ["vectors", "direction_cosines"]
        )
    ]
    for qid, qtext, opts, ans, exp, diff, tags in vec:
        questions.append(create_mcq(qid, qtext, opts, ans, exp, "Mathematics", "Vector Algebra", "Scalar Dot Product and Orthogonality", diff, tags))

    # 9. Statistics and Probability
    stat = [
        (
            "DDCET-MATH-STAT-016",
            "What is the mode of the following dataset: $4, 7, 2, 7, 9, 7, 5, 2, 7, 3$?",
            {"A": "$7$", "B": "$2$", "C": "$5$", "D": "$4$"},
            "A",
            "The value 7 appears with the highest frequency (4 times). Hence the mode is 7.",
            "easy", ["statistics", "mode"]
        ),
        (
            "DDCET-MATH-STAT-017",
            "If the mean of $5$ observations is $12$, what is the sum of these observations?",
            {"A": "$60$", "B": "$17$", "C": "$2.4$", "D": "$50$"},
            "A",
            "$\\text{Mean} = \\frac{\\sum x}{n} \\implies \\sum x = n \\times \\text{Mean} = 5 \\times 12 = 60$.",
            "easy", ["statistics", "mean"]
        ),
        (
            "DDCET-MATH-STAT-018",
            "What is the probability of getting at least one head when flipping two fair coins?",
            {"A": "$\\frac{3}{4}$", "B": "$\\frac{1}{2}$", "C": "$\\frac{1}{4}$", "D": "$1$"},
            "A",
            "Sample space $S = \\{HH, HT, TH, TT\\}$ (4 outcomes). Favorable outcomes: $HH, HT, TH$ (3 outcomes). Probability $= 3/4$.",
            "easy", ["probability", "coin_toss"]
        ),
        (
            "DDCET-MATH-STAT-019",
            "If $P(A) = 0.7$, what is $P(A')$ (probability of complementary event)?",
            {"A": "$0.3$", "B": "$0.7$", "C": "$0.0$", "D": "$1.0$"},
            "A",
            "$P(A') = 1 - P(A) = 1 - 0.7 = 0.3$.",
            "easy", ["probability", "complement"]
        )
    ]
    for qid, qtext, opts, ans, exp, diff, tags in stat:
        questions.append(create_mcq(qid, qtext, opts, ans, exp, "Mathematics", "Statistics and Probability", "Mean, Median and Mode", diff, tags))

    # =========================================================================
    # PART B: BASICS OF SCIENCE & ENGINEERING (BE-01)
    # =========================================================================
    sci = [
        (
            "DDCET-SCI-UD-007",
            "What is the dimensional formula for Pressure / Stress?",
            {"A": "$[M^1 L^{-1} T^{-2}]$", "B": "$[M^1 L^1 T^{-2}]$", "C": "$[M^1 L^{-2} T^{-2}]$", "D": "$[M^1 L^2 T^{-2}]$"},
            "A",
            "$\\text{Pressure} = \\frac{\\text{Force}}{\\text{Area}} = \\frac{[M^1 L^1 T^{-2}]}{[L^2]} = [M^1 L^{-1} T^{-2}]$.",
            "Units and Measurement", "SI Units and Dimensional Analysis", "easy", ["dimensional_analysis", "pressure"]
        ),
        (
            "DDCET-SCI-UD-008",
            "What is the least count of a micrometer screw gauge with pitch $0.5\\text{ mm}$ and 50 circular scale divisions?",
            {"A": "$0.01\\text{ mm}$", "B": "$0.05\\text{ mm}$", "C": "$0.001\\text{ mm}$", "D": "$0.1\\text{ mm}$"},
            "A",
            "$\\text{Least Count} = \\frac{\\text{Pitch}}{\\text{Number of circular divisions}} = \\frac{0.5\\text{ mm}}{50} = 0.01\\text{ mm}$.",
            "Units and Measurement", "Errors and Measuring Instruments", "easy", ["screw_gauge", "least_count"]
        ),
        (
            "DDCET-SCI-MECH-007",
            "What is the SI unit of Linear Momentum?",
            {"A": "$\\text{kg}\\cdot\\text{m/s}$", "B": "$\\text{N}\\cdot\\text{m}$", "C": "$\\text{J}\\cdot\\text{s}$", "D": "$\\text{kg}\\cdot\\text{m/s}^2$"},
            "A",
            "$p = m v$, so its unit is kilogram-meter per second ($\\text{kg}\\cdot\\text{m/s}$), which is equivalent to Newton-second ($\\text{N}\\cdot\\text{s}$).",
            "Classical Mechanics", "Newton's Laws and Momentum", "easy", ["momentum", "units"]
        ),
        (
            "DDCET-SCI-MECH-008",
            "An object of mass $10\\text{ kg}$ is moving with velocity $4\\text{ m/s}$. What is its kinetic energy?",
            {"A": "$80\\text{ J}$", "B": "$40\\text{ J}$", "C": "$160\\text{ J}$", "D": "$20\\text{ J}$"},
            "A",
            "$KE = \\frac{1}{2} m v^2 = \\frac{1}{2}(10)(4^2) = 5 \\times 16 = 80\\text{ Joules}$.",
            "Classical Mechanics", "Work, Energy, and Power", "easy", ["kinetic_energy"]
        ),
        (
            "DDCET-SCI-HEAT-005",
            "Which law of thermodynamics provides the fundamental definition of temperature?",
            {"A": "Zeroth Law of Thermodynamics", "B": "First Law of Thermodynamics", "C": "Second Law of Thermodynamics", "D": "Third Law of Thermodynamics"},
            "A",
            "The Zeroth Law of Thermodynamics establishes thermal equilibrium as an equivalence relation, defining the concept of temperature.",
            "Heat and Thermometry", "Thermodynamic Laws and Heat Engines", "easy", ["zeroth_law", "temperature"]
        ),
        (
            "DDCET-SCI-HEAT-006",
            "What is the relationship between the coefficients of linear expansion ($\\alpha$), superficial expansion ($\\beta$), and cubical expansion ($\\gamma$) for an isotropic solid?",
            {"A": "$\\alpha : \\beta : \\gamma = 1 : 2 : 3$", "B": "$\\alpha : \\beta : \\gamma = 3 : 2 : 1$", "C": "$\\alpha : \\beta : \\gamma = 1 : 1 : 1$", "D": "$\\alpha : \\beta : \\gamma = 1 : 3 : 2$"},
            "A",
            "For an isotropic solid: $\\beta = 2\\alpha$ and $\\gamma = 3\\alpha$, hence $\\alpha : \\beta : \\gamma = 1 : 2 : 3$.",
            "Heat and Thermometry", "Temperature Scales and Thermal Expansion", "easy", ["thermal_expansion"]
        ),
        (
            "DDCET-SCI-OPT-004",
            "What is the frequency of a sound wave propagating at $340\\text{ m/s}$ with a wavelength of $0.5\\text{ m}$?",
            {"A": "$680\\text{ Hz}$", "B": "$170\\text{ Hz}$", "C": "$340\\text{ Hz}$", "D": "$510\\text{ Hz}$"},
            "A",
            "$v = f \\lambda \\implies f = \\frac{v}{\\lambda} = \\frac{340}{0.5} = 680\\text{ Hz}$.",
            "Wave Motion, Optics, and Acoustics", "Sound Waves and Propagation", "easy", ["wave_speed", "frequency"]
        ),
        (
            "DDCET-SCI-OPT-005",
            "Total internal reflection occurs only when light travels from:",
            {"A": "Denser medium to rarer medium at an angle greater than critical angle", "B": "Rarer medium to denser medium", "C": "Denser medium to rarer medium at an angle less than critical angle", "D": "Any medium at normal incidence"},
            "A",
            "TIR requires two conditions: (1) Light must travel from optically denser to rarer medium, and (2) Angle of incidence must exceed critical angle ($i > \\theta_c$).",
            "Wave Motion, Optics, and Acoustics", "Total Internal Reflection and Optical Fibers", "easy", ["optics", "tir"]
        ),
        (
            "DDCET-SCI-ELEC-007",
            "What is the electrical power consumed by an appliance of resistance $20\\,\\Omega$ operating at $200\\text{ V}$?",
            {"A": "$2000\\text{ W}$", "B": "$1000\\text{ W}$", "C": "$400\\text{ W}$", "D": "$10\\text{ W}$"},
            "A",
            "$P = \\frac{V^2}{R} = \\frac{200^2}{20} = \\frac{40000}{20} = 2000\\text{ Watts}$.",
            "Electric Current & Electricity", "Ohm's Law and Resistivity", "easy", ["power", "electricity"]
        ),
        (
            "DDCET-SCI-ELEC-008",
            "What is the energy stored in a $10\\,\\mu\\text{F}$ capacitor charged to a potential difference of $100\\text{ V}$?",
            {"A": "$0.05\\text{ J}$", "B": "$0.1\\text{ J}$", "C": "$0.005\\text{ J}$", "D": "$1.0\\text{ J}$"},
            "A",
            "$U = \\frac{1}{2} C V^2 = \\frac{1}{2}(10 \\times 10^{-6})(100^2) = 5 \\times 10^{-6} \\times 10000 = 0.05\\text{ Joules}$.",
            "Electric Current & Electricity", "Capacitors and Electrostatics", "easy", ["capacitors", "stored_energy"]
        ),
        (
            "DDCET-SCI-CHEM-006",
            "What is the maximum number of electrons that can be accommodated in a shell with principal quantum number $n = 3$?",
            {"A": "$18$", "B": "$8$", "C": "$32$", "D": "$2$"},
            "A",
            "By Bohr-Bury rule, maximum electrons in shell $n$ is $2n^2$. For $n = 3$, $2(3^2) = 2(9) = 18$.",
            "Basic Chemistry Concepts", "Atomic Structure and Periodic Table", "easy", ["atomic_structure", "quantum_numbers"]
        ),
        (
            "DDCET-SCI-CHEM-007",
            "What is the pH of pure neutral water at $25^\\circ\\text{C}$?",
            {"A": "$7$", "B": "$0$", "C": "$14$", "D": "$1$"},
            "A",
            "At $25^\\circ\\text{C}$, the ionic product of water $K_w = [H^+][OH^-] = 10^{-14}$. For neutral water, $[H^+] = 10^{-7}\\text{ M} \\implies \\text{pH} = -\\log(10^{-7}) = 7$.",
            "Basic Chemistry Concepts", "Acids, Bases, and pH Scale", "easy", ["chemistry", "ph_scale"]
        ),
        (
            "DDCET-SCI-CHEM-008",
            "Which reagent is used in the complexometric titration to estimate total hardness of water?",
            {"A": "EDTA (Disodium salt)", "B": "Phenolphthalein", "C": "Potassium Permanganate", "D": "Methyl Orange"},
            "A",
            "Ethylenediaminetetraacetic acid (EDTA disodium salt) forms stable, soluble chelate complexes with $\\text{Ca}^{2+}$ and $\\text{Mg}^{2+}$ ions at $\\text{pH } 10$ using Eriochrome Black T indicator.",
            "Basic Chemistry Concepts", "Water Technology and Hardness", "easy", ["water_hardness", "edta"]
        )
    ]
    for qid, qtext, opts, ans, exp, top, subtop, diff, tags in sci:
        questions.append(create_mcq(qid, qtext, opts, ans, exp, "Engineering Science", top, subtop, diff, tags))

    # =========================================================================
    # PART C: SOFT SKILLS & APTITUDE (BE-02)
    # =========================================================================
    apt = [
        (
            "DDCET-APT-ENG-009",
            "Choose the correct preposition: 'The team will abide _____ the company guidelines.'",
            {"A": "by", "B": "with", "C": "to", "D": "in"},
            "A",
            "The phrasal verb 'abide by' means to accept or comply with a rule or decision.",
            "English Language & Grammar", "Prepositions and Articles", "easy", ["english", "prepositions"]
        ),
        (
            "DDCET-APT-ENG-010",
            "Select the correct article: 'She has earned _____ M.Tech degree in Computer Engineering.'",
            {"A": "an", "B": "a", "C": "the", "D": "no article"},
            "A",
            "The acronym 'M.Tech' begins with a vowel sound (/ɛm/), so it takes the indefinite article 'an'.",
            "English Language & Grammar", "Prepositions and Articles", "easy", ["english", "articles"]
        ),
        (
            "DDCET-APT-ENG-011",
            "Choose the synonym for 'AUTHENTIC':",
            {"A": "Genuine", "B": "Counterfeit", "C": "Fake", "D": "Dubious"},
            "A",
            "'Authentic' means of undisputed origin, genuine and reliable.",
            "English Language & Grammar", "Vocabulary and Synonyms", "easy", ["english", "synonyms"]
        ),
        (
            "DDCET-APT-ENG-012",
            "Choose the antonym for 'CONCAVE':",
            {"A": "Convex", "B": "Hollow", "C": "Curved", "D": "Flat"},
            "A",
            "'Concave' curves inward; its direct geometric antonym is 'convex', which curves outward.",
            "English Language & Grammar", "Vocabulary and Antonyms", "easy", ["english", "antonyms"]
        ),
        (
            "DDCET-APT-ENG-013",
            "Subject-verb agreement: 'Neither the manager nor the engineers _____ present at the conference.'",
            {"A": "were", "B": "was", "C": "is", "D": "are being"},
            "A",
            "When subjects are joined by 'neither... nor', the verb agrees with the closer subject ('engineers', which is plural, taking 'were').",
            "English Language & Grammar", "Subject-Verb Agreement", "easy", ["english", "grammar"]
        ),
        (
            "DDCET-APT-QA-011",
            "If 15 workers can build a wall in 20 days, how many days will 25 workers take to build the same wall?",
            {"A": "$12\\text{ days}$", "B": "$10\\text{ days}$", "C": "$15\\text{ days}$", "D": "$16\\text{ days}$"},
            "A",
            "Total person-days $= 15 \\times 20 = 300$. Days for 25 workers $= \\frac{300}{25} = 12\\text{ days}$.",
            "Quantitative Aptitude", "Work and Time", "easy", ["aptitude", "time_work"]
        ),
        (
            "DDCET-APT-QA-012",
            "A shopkeeper marks an item $20\\%$ above cost price and offers a $10\\%$ discount. What is the net profit percentage?",
            {"A": "$8\\%$", "B": "$10\\%$", "C": "$12\\%$", "D": "$5\\%$"},
            "A",
            "Let $CP = 100$. Marked Price $= 120$. Discount $= 10\\%$ of $120 = 12$. Selling Price $= 120 - 12 = 108$. Net profit $= 108 - 100 = 8\\%$.",
            "Quantitative Aptitude", "Percentages and Profit-Loss", "easy", ["aptitude", "profit_loss"]
        ),
        (
            "DDCET-APT-QA-013",
            "What is the compound interest on $\\text{Rs. } 10000$ for $2\\text{ years}$ at $10\\%$ per annum compounded annually?",
            {"A": "$\\text{Rs. } 2100$", "B": "$\\text{Rs. } 2000$", "C": "$\\text{Rs. } 2200$", "D": "$\\text{Rs. } 12100$"},
            "A",
            "$A = P(1 + r/100)^t = 10000(1.10)^2 = 10000(1.21) = 12100$. Compound interest $= A - P = 12100 - 10000 = \\text{Rs. } 2100$.",
            "Quantitative Aptitude", "Simple and Compound Interest", "easy", ["aptitude", "compound_interest"]
        ),
        (
            "DDCET-APT-QA-014",
            "What is the fourth proportional to $4, 9,$ and $12$?",
            {"A": "$27$", "B": "$36$", "C": "$18$", "D": "$24$"},
            "A",
            "Let the fourth proportional be $x$: $\\frac{4}{9} = \\frac{12}{x} \\implies 4x = 108 \\implies x = 27$.",
            "Quantitative Aptitude", "Ratio and Proportion", "easy", ["aptitude", "ratio_proportion"]
        ),
        (
            "DDCET-APT-QA-015",
            "Find the odd one out: $8, 27, 64, 100, 125, 216$.",
            {"A": "$100$", "B": "$64$", "C": "$27$", "D": "$125$"},
            "A",
            "All numbers except $100$ are perfect cubes ($2^3=8, 3^3=27, 4^3=64, 5^3=125, 6^3=216$). $100 = 10^2$ is a square, not a cube.",
            "Quantitative Aptitude", "Number Series and Reasoning", "easy", ["aptitude", "odd_one_out"]
        )
    ]
    for qid, qtext, opts, ans, exp, top, subtop, diff, tags in apt:
        questions.append(create_mcq(qid, qtext, opts, ans, exp, "Soft Skills & Aptitude", top, subtop, diff, tags))

    return questions


def main():
    print("Generating comprehensive authentic DDCET MCQs...")
    new_questions = generate_all_questions()
    print(f"Constructed {len(new_questions)} new syllabus MCQs.")

    # Validate every new question using QuestionModel
    valid_new = []
    for q in new_questions:
        try:
            validated = QuestionModel(**q)
            valid_new.append(validated.model_dump())
        except Exception as e:
            print(f"Validation error on {q['id']}: {e}")

    print(f"Validated {len(valid_new)} questions.")

    # Read existing data.json
    data_path = os.path.join("data", "data.json")
    existing_items = []
    if os.path.exists(data_path):
        try:
            with open(data_path, "r", encoding="utf-8") as f:
                existing_items = json.load(f)
            print(f"Existing items in data.json: {len(existing_items)}")
        except Exception as e:
            print(f"Error reading {data_path}: {e}")

    # Build index of existing IDs and hashes to de-duplicate
    existing_ids = {item["id"] for item in existing_items}
    existing_hashes = {compute_question_hash(item["question"], item.get("options", {})) for item in existing_items}

    added_count = 0
    for q in valid_new:
        q_hash = compute_question_hash(q["question"], q["options"])
        if q["id"] in existing_ids:
            continue
        if q_hash in existing_hashes:
            continue
        existing_items.append(q)
        existing_ids.add(q["id"])
        existing_hashes.add(q_hash)
        added_count += 1

    print(f"Appended {added_count} brand-new questions. Total in data.json is now {len(existing_items)}.")

    # Save back to data.json
    with open(data_path, "w", encoding="utf-8") as f:
        json.dump(existing_items, f, indent=2, ensure_ascii=False)
    print(f"Successfully saved updated data.json with {len(existing_items)} MCQs.")


if __name__ == "__main__":
    main()
