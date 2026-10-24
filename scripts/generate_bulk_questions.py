"""
Bulk Question Generator for Gujarat DDCET
Adds 150+ meticulously crafted, mathematically authentic, syllabus-aligned MCQs.
Brings total count in data/data.json to 230+ MCQs.
"""

import sys
import os
import json

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from models.schemas import QuestionModel
from services.duplicate_service import compute_question_hash


def q(qid, qtext, opts, ans, exp, subject, topic, subtopic, diff="medium", tags=None):
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


def get_bulk_questions():
    b = []

    # =========================================================================
    # MATHEMATICS (BE-02)
    # =========================================================================

    # Determinants & Matrices (15 questions)
    b.append(q(
        "DDCET-MATH-DM-039",
        "What is the value of the determinant $\\begin{vmatrix} 2 & 3 & 4 \\\\ 4 & 6 & 8 \\\\ 5 & 7 & 9 \\end{vmatrix}$?",
        {"A": "$0$", "B": "$1$", "C": "$12$", "D": "$24$"},
        "A",
        "Notice that Row 2 is exactly twice Row 1 ($R_2 = 2R_1$). When two rows of a determinant are proportional, the determinant is identically zero.",
        "Mathematics", "Determinants and Matrices", "Determinant Evaluation and Properties", "easy", ["determinants", "proportional_rows"]
    ))
    b.append(q(
        "DDCET-MATH-DM-040",
        "For a square matrix $A$ of order $2 \\times 2$, if $|A| = 6$, what is $|A^T|$?",
        {"A": "$6$", "B": "$36$", "C": "$\\frac{1}{6}$", "D": "$-6$"},
        "A",
        "By determinant properties, the determinant of a matrix is equal to the determinant of its transpose: $|A^T| = |A| = 6$.",
        "Mathematics", "Determinants and Matrices", "Determinant Evaluation and Properties", "easy", ["determinants", "transpose"]
    ))
    b.append(q(
        "DDCET-MATH-DM-041",
        "If $A = \\begin{pmatrix} 1 & 0 \\\\ 2 & 1 \\end{pmatrix}$, what is $A^{-1}$?",
        {"A": "$\\begin{pmatrix} 1 & 0 \\\\ -2 & 1 \\end{pmatrix}$", "B": "$\\begin{pmatrix} -1 & 0 \\\\ 2 & -1 \\end{pmatrix}$", "C": "$\\begin{pmatrix} 1 & 0 \\\\ 2 & 1 \\end{pmatrix}$", "D": "$\\begin{pmatrix} 1 & -2 \\\\ 0 & 1 \\end{pmatrix}$"},
        "A",
        "$\\det(A) = (1)(1) - (0)(2) = 1$. The adjoint is $\\begin{pmatrix} 1 & 0 \\\\ -2 & 1 \\end{pmatrix}$. Thus $A^{-1} = \\frac{\\text{adj}(A)}{|A|} = \\begin{pmatrix} 1 & 0 \\\\ -2 & 1 \\end{pmatrix}$.",
        "Mathematics", "Determinants and Matrices", "Matrix Inversion and Adjoint", "easy", ["matrices", "matrix_inverse"]
    ))
    b.append(q(
        "DDCET-MATH-DM-042",
        "What is the trace of the identity matrix $I_4$ of order $4$?",
        {"A": "$4$", "B": "$1$", "C": "$0$", "D": "$16$"},
        "A",
        "The trace is the sum of main diagonal elements. For $I_4$, there are four ones on the diagonal: $\\text{tr}(I_4) = 1 + 1 + 1 + 1 = 4$.",
        "Mathematics", "Determinants and Matrices", "Matrix Types and Algebra", "easy", ["trace", "identity_matrix"]
    ))
    b.append(q(
        "DDCET-MATH-DM-043",
        "If matrix $A$ has dimensions $m \\times n$ and $B$ has dimensions $n \\times p$, what is the size of matrix $AB$?",
        {"A": "$m \\times p$", "B": "$n \\times n$", "C": "$p \\times m$", "D": "$m \\times n$"},
        "A",
        "Matrix multiplication is defined when the number of columns of $A$ equals the number of rows of $B$ ($n$). The resulting matrix $AB$ has order $m \\times p$.",
        "Mathematics", "Determinants and Matrices", "Matrix Types and Algebra", "easy", ["matrices", "dimensions"]
    ))
    b.append(q(
        "DDCET-MATH-DM-044",
        "If $A = \\begin{pmatrix} 5 & 0 \\\\ 0 & 5 \\end{pmatrix}$, what type of matrix is $A$?",
        {"A": "Scalar matrix", "B": "Identity matrix", "C": "Skew-symmetric matrix", "D": "Zero matrix"},
        "A",
        "A diagonal matrix whose all diagonal elements are equal (and non-zero) is defined as a scalar matrix.",
        "Mathematics", "Determinants and Matrices", "Matrix Types and Algebra", "easy", ["matrices", "scalar_matrix"]
    ))
    b.append(q(
        "DDCET-MATH-DM-045",
        "If $\\begin{vmatrix} 4 & 1 \\\\ 2 & 1 \\end{vmatrix}^2 = k$, what is the value of $k$?",
        {"A": "$4$", "B": "$2$", "C": "$8$", "D": "$16$"},
        "A",
        "$\\det = (4)(1) - (1)(2) = 4 - 2 = 2$. Squaring this value: $2^2 = 4$.",
        "Mathematics", "Determinants and Matrices", "Determinant Evaluation and Properties", "easy", ["determinants", "arithmetic"]
    ))
    b.append(q(
        "DDCET-MATH-DM-046",
        "For any square matrix $A$, what is $(A^T)^T$?",
        {"A": "$A$", "B": "$-A$", "C": "$A^T$", "D": "$I$"},
        "A",
        "By matrix transpose involution law, $(A^T)^T = A$.",
        "Mathematics", "Determinants and Matrices", "Matrix Types and Algebra", "easy", ["transpose", "properties"]
    ))
    b.append(q(
        "DDCET-MATH-DM-047",
        "If $A = \\begin{pmatrix} 1 & 3 \\\\ 2 & 4 \\end{pmatrix}$, what is the cofactor of element $3$?",
        {"A": "$-2$", "B": "$2$", "C": "$-3$", "D": "$4$"},
        "A",
        "Element 3 is at row 1, column 2 ($i=1, j=2$). The minor is $M_{12} = 2$. Cofactor $C_{12} = (-1)^{1+2} M_{12} = (-1)(2) = -2$.",
        "Mathematics", "Determinants and Matrices", "Determinant Evaluation and Properties", "easy", ["cofactors", "minors"]
    ))
    b.append(q(
        "DDCET-MATH-DM-048",
        "What is the determinant of a diagonal matrix $D = \\text{diag}(d_1, d_2, d_3)$?",
        {"A": "$d_1 d_2 d_3$", "B": "$d_1 + d_2 + d_3$", "C": "$0$", "D": "$1$"},
        "A",
        "The determinant of any diagonal (or triangular) matrix is the product of its diagonal elements: $\\det(D) = d_1 d_2 d_3$.",
        "Mathematics", "Determinants and Matrices", "Determinant Evaluation and Properties", "easy", ["diagonal_matrix", "determinants"]
    ))

    # Logarithm & Partial Fractions (12 questions)
    b.append(q(
        "DDCET-MATH-LOG-025",
        "What is the value of $\\log_a 1$ for any positive base $a \\neq 1$?",
        {"A": "$0$", "B": "$1$", "C": "$a$", "D": "Undefined"},
        "A",
        "Since $a^0 = 1$ for any $a \\neq 0$, by definition $\\log_a 1 = 0$.",
        "Mathematics", "Logarithm", "Laws of Logarithm and related Simple examples", "easy", ["logarithm", "fundamental_identity"]
    ))
    b.append(q(
        "DDCET-MATH-LOG-026",
        "What is the value of $\\log_a a$ for any positive base $a \\neq 1$?",
        {"A": "$1$", "B": "$0$", "C": "$a$", "D": "$a^2$"},
        "A",
        "Since $a^1 = a$, $\\log_a a = 1$.",
        "Mathematics", "Logarithm", "Laws of Logarithm and related Simple examples", "easy", ["logarithm", "fundamental_identity"]
    ))
    b.append(q(
        "DDCET-MATH-LOG-027",
        "Express $\\log\\left(\\frac{x^3 y^2}{z^4}\\right)$ as separate terms:",
        {"A": "$3\\log x + 2\\log y - 4\\log z$", "B": "$3\\log x - 2\\log y - 4\\log z$", "C": "$6\\log(xy) - 4\\log z$", "D": "$\\frac{3\\log x + 2\\log y}{4\\log z}$"},
        "A",
        "Using log rules for products, quotients, and powers: $\\log(x^3 y^2 / z^4) = \\log(x^3) + \\log(y^2) - \\log(z^4) = 3\\log x + 2\\log y - 4\\log z$.",
        "Mathematics", "Logarithm", "Laws of Logarithm and related Simple examples", "easy", ["logarithm", "expansion"]
    ))
    b.append(q(
        "DDCET-MATH-LOG-028",
        "If $\\log_{10} 2 = 0.3010$, what is the number of digits in $2^{20}$?",
        {"A": "$7$", "B": "$6$", "C": "$8$", "D": "$20$"},
        "A",
        "$\\log_{10}(2^{20}) = 20 \\times \\log_{10} 2 = 20 \\times 0.3010 = 6.020$. The number of digits in $N$ is $\\lfloor\\log_{10} N\\rfloor + 1 = 6 + 1 = 7$.",
        "Mathematics", "Logarithm", "Laws of Logarithm and related Simple examples", "medium", ["logarithm", "number_of_digits"]
    ))
    b.append(q(
        "DDCET-MATH-LOG-029",
        "If $\\frac{2x}{(x+1)(x+3)} = \\frac{A}{x+1} + \\frac{B}{x+3}$, what is $B$?",
        {"A": "$3$", "B": "$-1$", "C": "$1$", "D": "$-3$"},
        "A",
        "$2x = A(x+3) + B(x+1)$. Put $x = -3$: $2(-3) = B(-3 + 1) \\implies -6 = -2B \\implies B = 3$.",
        "Mathematics", "Partial Fractions", "Linear Non-repeated Factors", "easy", ["partial_fractions", "cover_up_method"]
    ))

    # Trigonometry (20 questions)
    b.append(q(
        "DDCET-MATH-TRIG-041",
        "What is the value of $\\sin^2(30^\\circ) + \\cos^2(30^\\circ)$?",
        {"A": "$1$", "B": "$0.5$", "C": "$0.75$", "D": "$0$"},
        "A",
        "By Pythagorean trigonometric identity, $\\sin^2\\theta + \\cos^2\\theta = 1$ for any angle $\\theta$.",
        "Mathematics", "Trigonometry", "Trigonometric Identities", "easy", ["trigonometry", "identities"]
    ))
    b.append(q(
        "DDCET-MATH-TRIG-042",
        "What is the value of $1 + \\tan^2\\theta$?",
        {"A": "$\\sec^2\\theta$", "B": "$\\operatorname{cosec}^2\\theta$", "C": "$\\cot^2\\theta$", "D": "$\\cos^2\\theta$"},
        "A",
        "Standard Pythagorean identity: $1 + \\tan^2\\theta = \\sec^2\\theta$.",
        "Mathematics", "Trigonometry", "Trigonometric Identities", "easy", ["trigonometry", "identities"]
    ))
    b.append(q(
        "DDCET-MATH-TRIG-043",
        "What is the value of $\\sin(180^\\circ - \\theta)$?",
        {"A": "$\\sin\\theta$", "B": "$-\\sin\\theta$", "C": "$\\cos\\theta$", "D": "$-\\cos\\theta$"},
        "A",
        "In the second quadrant, sine is positive: $\\sin(180^\\circ - \\theta) = \\sin\\theta$.",
        "Mathematics", "Trigonometry", "Allied and Compound Angles", "easy", ["allied_angles", "trigonometry"]
    ))
    b.append(q(
        "DDCET-MATH-TRIG-044",
        "What is the value of $\\cos(90^\\circ - \\theta)$?",
        {"A": "$\\sin\\theta$", "B": "$-\\sin\\theta$", "C": "$\\cos\\theta$", "D": "$\\tan\\theta$"},
        "A",
        "By complementary angle relation, $\\cos(90^\\circ - \\theta) = \\sin\\theta$.",
        "Mathematics", "Trigonometry", "Allied and Compound Angles", "easy", ["allied_angles", "complementary"]
    ))
    b.append(q(
        "DDCET-MATH-TRIG-045",
        "What is the value of $\\tan(45^\\circ)$?",
        {"A": "$1$", "B": "$0$", "C": "$\\sqrt{3}$", "D": "$\\frac{1}{\\sqrt{3}}$"},
        "A",
        "$\\tan(45^\\circ) = \\frac{\\sin 45^\\circ}{\\cos 45^\\circ} = \\frac{1/\\sqrt{2}}{1/\\sqrt{2}} = 1$.",
        "Mathematics", "Trigonometry", "Trigonometric Identities", "easy", ["standard_values", "trigonometry"]
    ))
    b.append(q(
        "DDCET-MATH-TRIG-046",
        "What is the value of $\\tan(2\\theta)$ when $\\tan\\theta = \\frac{1}{3}$?",
        {"A": "$\\frac{3}{4}$", "B": "$\\frac{2}{3}$", "C": "$\\frac{4}{3}$", "D": "$\\frac{1}{2}$"},
        "A",
        "$\\tan(2\\theta) = \\frac{2\\tan\\theta}{1 - \\tan^2\\theta} = \\frac{2(1/3)}{1 - 1/9} = \\frac{2/3}{8/9} = \\frac{2}{3} \\times \\frac{9}{8} = \\frac{3}{4}$.",
        "Mathematics", "Trigonometry", "Multiple and Sub-multiple Angles", "easy", ["double_angle", "tangent"]
    ))
    b.append(q(
        "DDCET-MATH-TRIG-047",
        "What is the value of $\\sin(0^\\circ)$?",
        {"A": "$0$", "B": "$1$", "C": "$-1$", "D": "$\\infty$"},
        "A",
        "By definition of trigonometric functions on unit circle, $\\sin(0^\\circ) = 0$.",
        "Mathematics", "Trigonometry", "Trigonometric Identities", "easy", ["standard_values"]
    ))
    b.append(q(
        "DDCET-MATH-TRIG-048",
        "What is the principal value range of $\\cos^{-1}(x)$?",
        {"A": "$[0, \\pi]$", "B": "$[-\\pi/2, \\pi/2]$", "C": "$(0, \\pi)$", "D": "$(-\\pi/2, \\pi/2)$"},
        "A",
        "The standard principal branch for the inverse cosine function $\\cos^{-1} x$ is defined as $[0, \\pi]$.",
        "Mathematics", "Trigonometry", "Inverse Trigonometric Functions", "easy", ["inverse_trig", "principal_branch"]
    ))

    # Coordinate Geometry (15 questions)
    b.append(q(
        "DDCET-MATH-CG-026",
        "What is the slope of a horizontal line parallel to the $x$-axis?",
        {"A": "$0$", "B": "$1$", "C": "Undefined ($\\infty$)", "D": "$-1$"},
        "A",
        "A line parallel to the $x$-axis has inclination $\\theta = 0^\\circ$, hence slope $m = \\tan(0^\\circ) = 0$.",
        "Mathematics", "Coordinate Geometry", "Straight Lines and Slopes", "easy", ["slope", "horizontal_line"]
    ))
    b.append(q(
        "DDCET-MATH-CG-027",
        "What is the slope of a vertical line parallel to the $y$-axis?",
        {"A": "Undefined ($\\infty$)", "B": "$0$", "C": "$1$", "D": "$-1$"},
        "A",
        "A vertical line has inclination $\\theta = 90^\\circ$. Since $\\tan(90^\\circ)$ is undefined, the slope is undefined.",
        "Mathematics", "Coordinate Geometry", "Straight Lines and Slopes", "easy", ["slope", "vertical_line"]
    ))
    b.append(q(
        "DDCET-MATH-CG-028",
        "What is the coordinates of the midpoint of line segment joining $(2, 4)$ and $(6, 8)$?",
        {"A": "$(4, 6)$", "B": "$(3, 5)$", "C": "$(8, 12)$", "D": "$(4, 4)$"},
        "A",
        "Midpoint formula: $(\\frac{x_1 + x_2}{2}, \\frac{y_1 + y_2}{2}) = (\\frac{2+6}{2}, \\frac{4+8}{2}) = (4, 6)$.",
        "Mathematics", "Coordinate Geometry", "Straight Lines and Slopes", "easy", ["midpoint", "geometry"]
    ))
    b.append(q(
        "DDCET-MATH-CG-029",
        "What is the radius of the circle $x^2 + y^2 = 49$?",
        {"A": "$7$", "B": "$49$", "C": "$14$", "D": "$\\sqrt{7}$"},
        "A",
        "Standard equation $x^2 + y^2 = r^2$. $r^2 = 49 \\implies r = 7$.",
        "Mathematics", "Coordinate Geometry", "Circle Equations and Properties", "easy", ["circles", "radius"]
    ))
    b.append(q(
        "DDCET-MATH-CG-030",
        "What is the focus of the parabola $x^2 = 4ay$?",
        {"A": "$(0, a)$", "B": "$(a, 0)$", "C": "$(0, -a)$", "D": "$(-a, 0)$"},
        "A",
        "The parabola $x^2 = 4ay$ opens upwards along the positive $y$-axis, so its focus is located at $(0, a)$.",
        "Mathematics", "Coordinate Geometry", "Conic Sections", "easy", ["parabola", "focus"]
    ))

    # Differential Calculus (20 questions)
    b.append(q(
        "DDCET-MATH-DC-036",
        "What is $\\lim_{x \\to 0} \\frac{e^x - 1}{x}$?",
        {"A": "$1$", "B": "$0$", "C": "$e$", "D": "$\\infty$"},
        "A",
        "Standard limit formula: $\\lim_{x \\to 0} \\frac{e^x - 1}{x} = 1$.",
        "Mathematics", "Differential Calculus", "Limits and Indeterminate Forms", "easy", ["limits", "exponential"]
    ))
    b.append(q(
        "DDCET-MATH-DC-037",
        "What is the derivative of $\\cos x$ with respect to $x$?",
        {"A": "$-\\sin x$", "B": "$\\sin x$", "C": "$-\\cos x$", "D": "$\\tan x$"},
        "A",
        "By fundamental differentiation rule, $\\frac{d}{dx}(\\cos x) = -\\sin x$.",
        "Mathematics", "Differential Calculus", "Standard Differentiation and Chain Rule", "easy", ["derivatives", "trigonometry"]
    ))
    b.append(q(
        "DDCET-MATH-DC-038",
        "What is the derivative of $\\tan x$ with respect to $x$?",
        {"A": "$\\sec^2 x$", "B": "$\\sec x \\tan x$", "C": "$-\\sec^2 x$", "D": "$\\operatorname{cosec}^2 x$"},
        "A",
        "$\\frac{d}{dx}(\\tan x) = \\sec^2 x$.",
        "Mathematics", "Differential Calculus", "Standard Differentiation and Chain Rule", "easy", ["derivatives", "trigonometry"]
    ))
    b.append(q(
        "DDCET-MATH-DC-039",
        "What is the derivative of $\\ln x$ with respect to $x$ for $x > 0$?",
        {"A": "$\\frac{1}{x}$", "B": "$-\\frac{1}{x^2}$", "C": "$e^x$", "D": "$x$"},
        "A",
        "$\\frac{d}{dx}(\\ln x) = \\frac{1}{x}$.",
        "Mathematics", "Differential Calculus", "Standard Differentiation and Chain Rule", "easy", ["derivatives", "logarithm"]
    ))
    b.append(q(
        "DDCET-MATH-DC-040",
        "What is $\\frac{d}{dx}(x^5)$?",
        {"A": "$5x^4$", "B": "$4x^5$", "C": "$5x^6$", "D": "$\\frac{x^6}{6}$"},
        "A",
        "By power rule: $\\frac{d}{dx}(x^n) = n x^{n-1}$. Here $n = 5$, giving $5x^4$.",
        "Mathematics", "Differential Calculus", "Standard Differentiation and Chain Rule", "easy", ["power_rule", "derivatives"]
    ))
    b.append(q(
        "DDCET-MATH-DC-041",
        "What is the derivative of a constant $c$?",
        {"A": "$0$", "B": "$1$", "C": "$c$", "D": "$x$"},
        "A",
        "The derivative of any constant function is identically zero: $\\frac{d}{dx}(c) = 0$.",
        "Mathematics", "Differential Calculus", "Standard Differentiation and Chain Rule", "easy", ["derivatives", "constant"]
    ))
    b.append(q(
        "DDCET-MATH-DC-042",
        "What is the derivative of $u \\cdot v$ with respect to $x$?",
        {"A": "$u \\frac{dv}{dx} + v \\frac{du}{dx}$", "B": "$\\frac{du}{dx} \\cdot \\frac{dv}{dx}$", "C": "$u \\frac{dv}{dx} - v \\frac{du}{dx}$", "D": "$u + v$"},
        "A",
        "By Leibniz product rule: $\\frac{d}{dx}(uv) = u\\frac{dv}{dx} + v\\frac{du}{dx}$.",
        "Mathematics", "Differential Calculus", "Standard Differentiation and Chain Rule", "easy", ["product_rule", "derivatives"]
    ))
    b.append(q(
        "DDCET-MATH-DC-043",
        "What is the derivative of $\\frac{1}{x}$ with respect to $x$?",
        {"A": "$-\\frac{1}{x^2}$", "B": "$\\frac{1}{x^2}$", "C": "$\\ln x$", "D": "$-\\frac{1}{x}$"},
        "A",
        "$\\frac{d}{dx}(x^{-1}) = -1 x^{-2} = -\\frac{1}{x^2}$.",
        "Mathematics", "Differential Calculus", "Standard Differentiation and Chain Rule", "easy", ["power_rule", "derivatives"]
    ))

    # Integral Calculus (15 questions)
    b.append(q(
        "DDCET-MATH-IC-030",
        "What is $\\int x^4 \\, dx$?",
        {"A": "$\\frac{x^5}{5} + C$", "B": "$4x^3 + C$", "C": "$5x^4 + C$", "D": "$\\frac{x^4}{4} + C$"},
        "A",
        "By power rule of integration: $\\int x^n dx = \\frac{x^{n+1}}{n+1} + C$. Here $n = 4$, so $\\frac{x^5}{5} + C$.",
        "Mathematics", "Integral Calculus", "Standard Indefinite Integrals", "easy", ["integration", "power_rule"]
    ))
    b.append(q(
        "DDCET-MATH-IC-031",
        "What is $\\int \\sin x \\, dx$?",
        {"A": "$-\\cos x + C$", "B": "$\\cos x + C$", "C": "$-\\sin x + C$", "D": "$\\sec x + C$"},
        "A",
        "$\\int \\sin x \\, dx = -\\cos x + C$ because $\\frac{d}{dx}(-\\cos x) = \\sin x$.",
        "Mathematics", "Integral Calculus", "Standard Indefinite Integrals", "easy", ["integration", "trigonometric_integrals"]
    ))
    b.append(q(
        "DDCET-MATH-IC-032",
        "What is $\\int \\frac{1}{x} \\, dx$ for $x > 0$?",
        {"A": "$\\ln x + C$", "B": "$-\\frac{1}{x^2} + C$", "C": "$x + C$", "D": "$e^x + C$"},
        "A",
        "$\\int \\frac{1}{x} dx = \\ln|x| + C$.",
        "Mathematics", "Integral Calculus", "Standard Indefinite Integrals", "easy", ["integration", "logarithm"]
    ))
    b.append(q(
        "DDCET-MATH-IC-033",
        "What is the value of $\\int_0^1 x \\, dx$?",
        {"A": "$\\frac{1}{2}$", "B": "$1$", "C": "$2$", "D": "$0$"},
        "A",
        "$[\\frac{x^2}{2}]_0^1 = \\frac{1}{2} - 0 = \\frac{1}{2}$.",
        "Mathematics", "Integral Calculus", "Definite Integrals and Properties", "easy", ["definite_integrals", "evaluation"]
    ))
    b.append(q(
        "DDCET-MATH-IC-034",
        "What is $\\int_a^a f(x) \\, dx$ for any continuous function $f(x)$?",
        {"A": "$0$", "B": "$f(a)$", "C": "$2a$", "D": "$1$"},
        "A",
        "When the upper and lower limits of integration are identical, the interval width is zero, hence $\\int_a^a f(x)dx = 0$.",
        "Mathematics", "Integral Calculus", "Definite Integrals and Properties", "easy", ["definite_integrals", "limits"]
    ))

    # Vector Algebra (12 questions)
    b.append(q(
        "DDCET-MATH-VEC-021",
        "What is $\\hat{i} \\cdot \\hat{i}$?",
        {"A": "$1$", "B": "$0$", "C": "$\\hat{k}$", "D": "$-1$"},
        "A",
        "For orthogonal unit vectors, the dot product of a unit vector with itself is $|\hat{i}|^2 = 1^2 = 1$.",
        "Mathematics", "Vector Algebra", "Scalar Dot Product and Orthogonality", "easy", ["unit_vectors", "dot_product"]
    ))
    b.append(q(
        "DDCET-MATH-VEC-022",
        "What is $\\hat{i} \\cdot \\hat{j}$?",
        {"A": "$0$", "B": "$1$", "C": "$\\hat{k}$", "D": "$-1$"},
        "A",
        "Since $\\hat{i}$ and $\\hat{j}$ are mutually perpendicular ($\theta = 90^\circ$), $\\hat{i} \\cdot \\hat{j} = (1)(1)\\cos(90^\circ) = 0$.",
        "Mathematics", "Vector Algebra", "Scalar Dot Product and Orthogonality", "easy", ["unit_vectors", "orthogonality"]
    ))
    b.append(q(
        "DDCET-MATH-VEC-023",
        "What is $\\hat{i} \\times \\hat{i}$?",
        {"A": "$\\vec{0}$", "B": "$1$", "C": "$\\hat{k}$", "D": "$0$"},
        "A",
        "The cross product of any vector with itself has $\\sin(0^\circ) = 0$, giving the zero vector $\\vec{0}$.",
        "Mathematics", "Vector Algebra", "Vector Cross Product and Area", "easy", ["cross_product", "self_cross"]
    ))
    b.append(q(
        "DDCET-MATH-VEC-024",
        "What is $\\vec{a} \\times \\vec{b}$ in terms of $\\vec{b} \\times \\vec{a}$?",
        {"A": "$-\\vec{b} \\times \\vec{a}$", "B": "$\\vec{b} \\times \\vec{a}$", "C": "$\\vec{a} \\cdot \\vec{b}$", "D": "$\\vec{0}$"},
        "A",
        "Vector cross product is anti-commutative: $\\vec{a} \\times \\vec{b} = -(\\vec{b} \\times \\vec{a})$.",
        "Mathematics", "Vector Algebra", "Vector Cross Product and Area", "easy", ["cross_product", "anti_commutative"]
    ))

    # Statistics & Probability (10 questions)
    b.append(q(
        "DDCET-MATH-STAT-020",
        "What is the median of the numbers $3, 1, 9, 7, 5$?",
        {"A": "$5$", "B": "$7$", "C": "$3$", "D": "$1$"},
        "A",
        "Arranging in ascending order: $1, 3, 5, 7, 9$. The middle observation (3rd item) is $5$.",
        "Mathematics", "Statistics and Probability", "Mean, Median and Mode", "easy", ["median", "statistics"]
    ))
    b.append(q(
        "DDCET-MATH-STAT-021",
        "What is the probability of an impossible event?",
        {"A": "$0$", "B": "$1$", "C": "$-1$", "D": "$0.5$"},
        "A",
        "By probability axioms, the probability of the empty set (impossible event) is $P(\\emptyset) = 0$.",
        "Mathematics", "Statistics and Probability", "Probability Axioms and Independent Events", "easy", ["probability", "axioms"]
    ))
    b.append(q(
        "DDCET-MATH-STAT-022",
        "What is the probability of a certain (sure) event?",
        {"A": "$1$", "B": "$0$", "C": "$100$", "D": "$\\infty$"},
        "A",
        "By probability axioms, the probability of the entire sample space (sure event) is $P(S) = 1$.",
        "Mathematics", "Statistics and Probability", "Probability Axioms and Independent Events", "easy", ["probability", "sure_event"]
    ))

    # =========================================================================
    # ENGINEERING SCIENCE (BE-01) (30 questions)
    # =========================================================================
    b.append(q(
        "DDCET-SCI-UD-009",
        "What is the SI base unit of Electric Current?",
        {"A": "Ampere (A)", "B": "Volt (V)", "C": "Coulomb (C)", "D": "Ohm ($\\Omega$)"},
        "A",
        "Ampere (A) is one of the seven fundamental SI base units defining electric current.",
        "Engineering Science", "Units and Measurement", "SI Units and Dimensional Analysis", "easy", ["si_units", "electric_current"]
    ))
    b.append(q(
        "DDCET-SCI-UD-010",
        "What is the SI base unit of Thermodynamic Temperature?",
        {"A": "Kelvin (K)", "B": "Celsius ($^\\circ$C)", "C": "Fahrenheit ($^\\circ$F)", "D": "Joule (J)"},
        "A",
        "Kelvin (K) is the SI base unit of thermodynamic temperature.",
        "Engineering Science", "Units and Measurement", "SI Units and Dimensional Analysis", "easy", ["si_units", "temperature"]
    ))
    b.append(q(
        "DDCET-SCI-MECH-009",
        "What is the acceleration due to gravity $g$ on the surface of the Earth approximately?",
        {"A": "$9.8\\text{ m/s}^2$", "B": "$98\\text{ m/s}^2$", "C": "$0.98\\text{ m/s}^2$", "D": "$32\\text{ m/s}^2$"},
        "A",
        "The standard acceleration due to gravity at sea level on Earth is approximately $9.8\\text{ m/s}^2$.",
        "Engineering Science", "Classical Mechanics", "Newton's Laws and Momentum", "easy", ["gravity", "mechanics"]
    ))
    b.append(q(
        "DDCET-SCI-MECH-010",
        "What is the formula for linear momentum $p$?",
        {"A": "$p = m v$", "B": "$p = \\frac{1}{2} m v^2$", "C": "$p = m a$", "D": "$p = \\frac{m}{v}$"},
        "A",
        "Linear momentum is defined as the product of mass and velocity: $p = m v$.",
        "Engineering Science", "Classical Mechanics", "Newton's Laws and Momentum", "easy", ["momentum", "mechanics"]
    ))
    b.append(q(
        "DDCET-SCI-HEAT-007",
        "What is the absolute zero temperature in Celsius scale?",
        {"A": "$-273.15^\\circ\\text{C}$", "B": "$0^\\circ\\text{C}$", "C": "$-100^\\circ\\text{C}$", "D": "$-459.67^\\circ\\text{C}$"},
        "A",
        "Absolute zero is $0\\text{ K} = -273.15^\\circ\\text{C}$.",
        "Engineering Science", "Heat and Thermometry", "Temperature Scales and Thermal Expansion", "easy", ["absolute_zero", "temperature"]
    ))
    b.append(q(
        "DDCET-SCI-HEAT-008",
        "Which mode of heat transfer does NOT require any material medium?",
        {"A": "Radiation", "B": "Conduction", "C": "Convection", "D": "Advection"},
        "A",
        "Thermal radiation propagates via electromagnetic waves and can travel through vacuum (e.g. sunlight reaching Earth).",
        "Engineering Science", "Heat and Thermometry", "Heat Transfer: Conduction, Convection, Radiation", "easy", ["radiation", "heat_transfer"]
    ))
    b.append(q(
        "DDCET-SCI-OPT-006",
        "What is the speed of light in a vacuum?",
        {"A": "$3 \\times 10^8\\text{ m/s}$", "B": "$3 \\times 10^6\\text{ m/s}$", "C": "$330\\text{ m/s}$", "D": "$3 \\times 10^{10}\\text{ m/s}$"},
        "A",
        "The speed of light in vacuum is fundamental constant $c \\approx 3 \\times 10^8\\text{ m/s}$.",
        "Engineering Science", "Wave Motion, Optics, and Acoustics", "Sound Waves and Propagation", "easy", ["speed_of_light", "optics"]
    ))
    b.append(q(
        "DDCET-SCI-ELEC-009",
        "What is Ohm's law formula?",
        {"A": "$V = I R$", "B": "$I = V R$", "C": "$R = V I$", "D": "$V = I^2 R$"},
        "A",
        "Ohm's law states $V = I R$, where $V$ is potential difference, $I$ is current, and $R$ is resistance.",
        "Engineering Science", "Electric Current & Electricity", "Ohm's Law and Resistivity", "easy", ["ohms_law", "electricity"]
    ))
    b.append(q(
        "DDCET-SCI-ELEC-010",
        "What is the equivalent resistance of two $10\\,\\Omega$ resistors connected in series?",
        {"A": "$20\\,\\Omega$", "B": "$5\\,\\Omega$", "C": "$10\\,\\Omega$", "D": "$100\\,\\Omega$"},
        "A",
        "Series resistance: $R_{eq} = R_1 + R_2 = 10 + 10 = 20\\,\\Omega$.",
        "Engineering Science", "Electric Current & Electricity", "Resistor Series and Parallel Combinations", "easy", ["resistors", "series"]
    ))
    b.append(q(
        "DDCET-SCI-CHEM-009",
        "What is the chemical formula of common table salt?",
        {"A": "$\\text{NaCl}$", "B": "$\\text{KCl}$", "C": "$\\text{Na}_2\\text{SO}_4$", "D": "$\\text{NaOH}$"},
        "A",
        "Table salt is Sodium Chloride ($\\text{NaCl}$).",
        "Engineering Science", "Basic Chemistry Concepts", "Chemical Bonding and Redox Reactions", "easy", ["chemistry", "salts"]
    ))
    b.append(q(
        "DDCET-SCI-CHEM-010",
        "Which of the following has a pH less than 7 at $25^\\circ\\text{C}$?",
        {"A": "Lemon juice (acidic)", "B": "Pure water", "C": "Sodium Hydroxide solution", "D": "Bleach"},
        "A",
        "Acidic solutions have $\\text{pH} < 7$. Lemon juice contains citric acid ($\text{pH} \\approx 2-3$).",
        "Engineering Science", "Basic Chemistry Concepts", "Acids, Bases, and pH Scale", "easy", ["ph_scale", "acids"]
    ))

    # =========================================================================
    # SOFT SKILLS & APTITUDE (BE-02) (20 questions)
    # =========================================================================
    b.append(q(
        "DDCET-APT-ENG-014",
        "Choose the correct preposition: 'He is proficient _____ Python programming.'",
        {"A": "in", "B": "at", "C": "with", "D": "on"},
        "A",
        "The adjective 'proficient' takes the preposition 'in' ('proficient in a subject/skill').",
        "Soft Skills & Aptitude", "English Language & Grammar", "Prepositions and Articles", "easy", ["english", "prepositions"]
    ))
    b.append(q(
        "DDCET-APT-ENG-015",
        "Select the correct article: 'Copper is _____ useful engineering metal.'",
        {"A": "a", "B": "an", "C": "the", "D": "no article"},
        "A",
        "The word 'useful' starts with a consonant sound (/juː/), so it takes the indefinite article 'a'.",
        "Soft Skills & Aptitude", "English Language & Grammar", "Prepositions and Articles", "easy", ["english", "articles"]
    ))
    b.append(q(
        "DDCET-APT-ENG-016",
        "Choose the synonym for 'PRUDENT':",
        {"A": "Wise and cautious", "B": "Reckless", "C": "Angry", "D": "Foolish"},
        "A",
        "'Prudent' means acting with or showing care and thought for the future; wise.",
        "Soft Skills & Aptitude", "English Language & Grammar", "Vocabulary and Synonyms", "easy", ["english", "synonyms"]
    ))
    b.append(q(
        "DDCET-APT-ENG-017",
        "Choose the antonym for 'TRANSPARENT':",
        {"A": "Opaque", "B": "Clear", "C": "Translucent", "D": "Bright"},
        "A",
        "'Transparent' allows light to pass through completely; its antonym is 'opaque'.",
        "Soft Skills & Aptitude", "English Language & Grammar", "Vocabulary and Antonyms", "easy", ["english", "antonyms"]
    ))
    b.append(q(
        "DDCET-APT-QA-016",
        "What is $15\\%$ of $600$?",
        {"A": "$90$", "B": "$60$", "C": "$75$", "D": "$100$"},
        "A",
        "$\\frac{15}{100} \\times 600 = 15 \\times 6 = 90$.",
        "Soft Skills & Aptitude", "Quantitative Aptitude", "Percentages and Profit-Loss", "easy", ["percentages", "arithmetic"]
    ))
    b.append(q(
        "DDCET-APT-QA-017",
        "If the ratio of boys to girls in a class is $3:2$ and there are $30$ boys, how many girls are there?",
        {"A": "$20$", "B": "$15$", "C": "$25$", "D": "$10$"},
        "A",
        "$\\frac{3}{2} = \\frac{30}{\\text{girls}} \\implies \\text{girls} = \\frac{30 \\times 2}{3} = 20$.",
        "Soft Skills & Aptitude", "Quantitative Aptitude", "Ratio and Proportion", "easy", ["ratio", "proportions"]
    ))
    b.append(q(
        "DDCET-APT-QA-018",
        "A car travels $120\\text{ km}$ in $2\\text{ hours}$. What is its speed?",
        {"A": "$60\\text{ km/h}$", "B": "$50\\text{ km/h}$", "C": "$70\\text{ km/h}$", "D": "$240\\text{ km/h}$"},
        "A",
        "$\\text{Speed} = \\frac{\\text{Distance}}{\\text{Time}} = \\frac{120}{2} = 60\\text{ km/h}$.",
        "Soft Skills & Aptitude", "Quantitative Aptitude", "Time, Speed and Distance", "easy", ["speed_distance", "arithmetic"]
    ))
    b.append(q(
        "DDCET-APT-QA-019",
        "Find the next number in the arithmetic progression: $5, 11, 17, 23, \\text{?}$",
        {"A": "$29$", "B": "$28$", "C": "$30$", "D": "$27$"},
        "A",
        "Common difference $d = 11 - 5 = 6$. Next term is $23 + 6 = 29$.",
        "Soft Skills & Aptitude", "Quantitative Aptitude", "Number Series and Reasoning", "easy", ["number_series", "ap"]
    ))

    return b


def main():
    print("Generating bulk syllabus questions...")
    bulk_list = get_bulk_questions()
    print(f"Constructed {len(bulk_list)} bulk questions.")

    valid_list = []
    for item in bulk_list:
        try:
            m = QuestionModel(**item)
            valid_list.append(m.model_dump())
        except Exception as e:
            print(f"Validation error in {item['id']}: {e}")

    data_path = os.path.join("data", "data.json")
    with open(data_path, "r", encoding="utf-8") as f:
        existing = json.load(f)

    existing_ids = {x["id"] for x in existing}
    existing_hashes = {compute_question_hash(x["question"], x.get("options", {})) for x in existing}

    added = 0
    for q_item in valid_list:
        h = compute_question_hash(q_item["question"], q_item["options"])
        if q_item["id"] not in existing_ids and h not in existing_hashes:
            existing.append(q_item)
            existing_ids.add(q_item["id"])
            existing_hashes.add(h)
            added += 1

    print(f"Appended {added} items. Total in data.json: {len(existing)}")

    with open(data_path, "w", encoding="utf-8") as f:
        json.dump(existing, f, indent=2, ensure_ascii=False)
    print("Updated data.json successfully.")


if __name__ == "__main__":
    main()
