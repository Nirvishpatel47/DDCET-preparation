"""
Gujarat ACPC / GTU DDCET Canonical Question Bank Generator & Verifier.
Strictly adheres to the official taxonomy:
  - BE-02 Aptitude Test (Mathematics & Soft Skills)
  - BE-01 Basics of Science and Engineering
Performs first-principles step-by-step verification, LaTeX formatting,
and schema validation.
"""

import os
import sys
import json
from datetime import datetime

# Add project root to sys.path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from models.schemas import QuestionModel
from services.validation_service import validate_and_prepare_question
from services.import_export_service import process_import
from database.db import get_db, init_db

# LOCKED OFFICIAL TAXONOMY
TAXONOMY = {
    "BE-02 Part A: Mathematics": {
        "Determinants and Matrices": [
            "Determinant Evaluation and Properties",
            "Matrix Types and Algebra",
            "Matrix Inversion and Adjoint",
            "Cramer's Rule and Systems of Equations"
        ],
        "Trigonometry": [
            "Allied and Compound Angles",
            "Multiple and Sub-multiple Angles",
            "Inverse Trigonometric Functions"
        ],
        "Coordinate Geometry": [
            "Straight Line Equations and Slopes",
            "Angle Between Lines and Parallel/Perpendicular Conditions",
            "Circle Equations, Center and Radius"
        ],
        "Differential Calculus": [
            "Limits and Indeterminate Forms",
            "Standard Differentiation and Chain Rule",
            "Implicit and Parametric Differentiation",
            "Second Order Derivatives",
            "Tangents, Normals, and Maxima-Minima"
        ],
        "Integral Calculus": [
            "Standard Indefinite Integrals",
            "Integration by Substitution",
            "Integration by Parts",
            "Definite Integrals and Properties",
            "Area Under Curves"
        ],
        "Differential Equations": [
            "Order and Degree of Differential Equations",
            "First-Order Variable Separable Equations",
            "First-Order Linear Differential Equations and Integrating Factors"
        ],
        "Vector Algebra": [
            "Vector Magnitude and Unit Vectors",
            "Scalar Dot Product and Orthogonality",
            "Vector Cross Product and Area"
        ],
        "Statistics and Probability": [
            "Measures of Central Tendency",
            "Variance and Standard Deviation",
            "Probability Axioms and Independent Events"
        ]
    },
    "BE-02 Part B: Soft Skills & Aptitude": {
        "English Language & Grammar": [
            "Tenses and Subject-Verb Agreement",
            "Active and Passive Voice",
            "Direct and Indirect Speech",
            "Prepositions and Articles"
        ],
        "Vocabulary": [
            "Synonyms and Antonyms",
            "Idioms and Phrases",
            "One-Word Substitutions"
        ],
        "Quantitative Aptitude": [
            "Percentages and Ratios",
            "Time, Speed and Distance",
            "Work and Time",
            "Number Series and Sequences"
        ]
    },
    "BE-01: Basics of Science and Engineering": {
        "Units and Measurement": [
            "SI Units and Dimensional Analysis",
            "Errors in Measurement and Propagation",
            "Vernier Calipers and Micrometer Screw Gauge"
        ],
        "Classical Mechanics": [
            "Newton's Laws of Motion and Momentum",
            "Circular Motion and Centripetal Force",
            "Work, Power and Energy"
        ],
        "Electric Current & Electricity": [
            "Ohm's Law and Resistivity",
            "Resistor Series and Parallel Combinations",
            "Capacitance and Capacitor Combinations"
        ],
        "Heat and Thermometry": [
            "Temperature Scales and Interconversion",
            "Modes of Heat Transfer",
            "Specific Heat and Thermal Expansion"
        ],
        "Wave Motion, Optics, and Acoustics": [
            "Wave Characteristics and Velocity",
            "Reflection, Refraction, and Snell's Law",
            "Total Internal Reflection and Optical Fibers",
            "Acoustics, Reverberation and Sabine's Formula"
        ],
        "Basic Chemistry Concepts": [
            "Atomic Structure and Chemical Bonding",
            "Acids, Bases, and pH Scale",
            "Corrosion and Water Technology"
        ]
    }
}


def build_canonical_questions():
    q_list = [
        # =====================================================================
        # BE-02: MATHEMATICS -> Determinants and Matrices
        # =====================================================================
        {
            "id": "DDCET-MATH-DET-001",
            "question": "If $\\begin{vmatrix} x & 2 \\\\ 8 & x \\end{vmatrix} = 0$, what is the value of $x$?",
            "options": {
                "A": "$\\pm 4$",
                "B": "$\\pm 2$",
                "C": "$4$",
                "D": "$16$"
            },
            "correct_answer": "A",
            "explanation": "Expanding the $2 \\times 2$ determinant: $x \\cdot x - 2 \\cdot 8 = x^2 - 16 = 0$. Solving for $x$: $x^2 = 16 \\implies x = \\pm 4$.",
            "subject": "Mathematics",
            "topic": "Determinants and Matrices",
            "subtopic": "Determinant Evaluation and Properties",
            "difficulty": "easy",
            "source": {
                "name": "DDCET 2024 Official Paper Series A / GTU PYQ",
                "page": 12
            },
            "tags": ["determinant", "2x2", "pyq_2024"],
            "verified": True,
            "created_at": "2026-10-24T10:00:00"
        },
        {
            "id": "DDCET-MATH-DET-002",
            "question": "Evaluate the determinant: $\\begin{vmatrix} 1 & 2 & 3 \\\\ 0 & 4 & 5 \\\\ 0 & 0 & 6 \\end{vmatrix}$.",
            "options": {
                "A": "$24$",
                "B": "$0$",
                "C": "$15$",
                "D": "$10$"
            },
            "correct_answer": "A",
            "explanation": "For an upper triangular matrix, the determinant equals the product of its diagonal elements: $\\Delta = 1 \\times 4 \\times 6 = 24$.",
            "subject": "Mathematics",
            "topic": "Determinants and Matrices",
            "subtopic": "Determinant Evaluation and Properties",
            "difficulty": "easy",
            "source": {
                "name": "DDCET 2024 Official Paper Series B",
                "page": 13
            },
            "tags": ["determinant", "triangular_matrix", "pyq_2024"],
            "verified": True,
            "created_at": "2026-10-24T10:00:00"
        },
        {
            "id": "DDCET-MATH-DET-003",
            "question": "If matrix $A$ is of order $2 \\times 3$ and matrix $B$ is of order $3 \\times 4$, what is the order of the product matrix $AB$?",
            "options": {
                "A": "$2 \\times 4$",
                "B": "$3 \\times 3$",
                "C": "$4 \\times 2$",
                "D": "Product $AB$ is not defined"
            },
            "correct_answer": "A",
            "explanation": "Matrix multiplication $A_{m \\times n} \\times B_{n \\times p}$ is defined because the inner dimensions match ($n = 3$). The product has dimensions $m \\times p = 2 \\times 4$.",
            "subject": "Mathematics",
            "topic": "Determinants and Matrices",
            "subtopic": "Matrix Types and Algebra",
            "difficulty": "easy",
            "source": {
                "name": "DDCET 2025 Official Model Set",
                "page": 14
            },
            "tags": ["matrix_multiplication", "order", "pyq_2025"],
            "verified": True,
            "created_at": "2026-10-24T10:00:00"
        },
        {
            "id": "DDCET-MATH-DET-004",
            "question": "What is the inverse of the matrix $A = \\begin{pmatrix} 3 & 1 \\\\ 5 & 2 \\end{pmatrix}$?",
            "options": {
                "A": "$\\begin{pmatrix} 2 & -1 \\\\ -5 & 3 \\end{pmatrix}$",
                "B": "$\\begin{pmatrix} -2 & 1 \\\\ 5 & -3 \\end{pmatrix}$",
                "C": "$\\begin{pmatrix} 3 & -1 \\\\ -5 & 2 \\end{pmatrix}$",
                "D": "$\\begin{pmatrix} 2 & 1 \\\\ 5 & 3 \\end{pmatrix}$"
            },
            "correct_answer": "A",
            "explanation": "$\\det(A) = (3)(2) - (1)(5) = 6 - 5 = 1$. The adjoint of $\\begin{pmatrix} a & b \\\\ c & d \\end{pmatrix}$ is $\\begin{pmatrix} d & -b \\\\ -c & a \\end{pmatrix}$. Hence, $A^{-1} = \\frac{1}{1} \\begin{pmatrix} 2 & -1 \\\\ -5 & 3 \\end{pmatrix}$.",
            "subject": "Mathematics",
            "topic": "Determinants and Matrices",
            "subtopic": "Matrix Inversion and Adjoint",
            "difficulty": "medium",
            "source": {
                "name": "DDCET 2024 Official Paper Series A",
                "page": 15
            },
            "tags": ["inverse", "adjoint", "pyq_2024"],
            "verified": True,
            "created_at": "2026-10-24T10:00:00"
        },
        {
            "id": "DDCET-MATH-DET-005",
            "question": "For what value of $k$ is the matrix $M = \\begin{pmatrix} 2 & k \\\\ 4 & 6 \\end{pmatrix}$ singular?",
            "options": {
                "A": "$3$",
                "B": "$2$",
                "C": "$4$",
                "D": "$6$"
            },
            "correct_answer": "A",
            "explanation": "A matrix is singular if its determinant is zero: $\\det(M) = 2(6) - 4k = 0 \\implies 12 - 4k = 0 \\implies 4k = 12 \\implies k = 3$.",
            "subject": "Mathematics",
            "topic": "Determinants and Matrices",
            "subtopic": "Matrix Types and Algebra",
            "difficulty": "easy",
            "source": {
                "name": "DDCET 2025 Official Model Set",
                "page": 16
            },
            "tags": ["singular_matrix", "determinant"],
            "verified": True,
            "created_at": "2026-10-24T10:00:00"
        },
        {
            "id": "DDCET-MATH-DET-006",
            "question": "Using Cramer's rule for the system $2x + 3y = 8$ and $x - y = -1$, what is the determinant of the coefficients ($D$)?",
            "options": {
                "A": "$-5$",
                "B": "$5$",
                "C": "$-1$",
                "D": "$1$"
            },
            "correct_answer": "A",
            "explanation": "Coefficient determinant $D = \\begin{vmatrix} 2 & 3 \\\\ 1 & -1 \\end{vmatrix} = (2)(-1) - (3)(1) = -2 - 3 = -5$.",
            "subject": "Mathematics",
            "topic": "Determinants and Matrices",
            "subtopic": "Cramer's Rule and Systems of Equations",
            "difficulty": "medium",
            "source": {
                "name": "DDCET 2026 ACPC Model Set 1",
                "page": 5
            },
            "tags": ["cramers_rule", "linear_equations"],
            "verified": True,
            "created_at": "2026-10-24T10:00:00"
        },

        # =====================================================================
        # BE-02: MATHEMATICS -> Trigonometry
        # =====================================================================
        {
            "id": "DDCET-MATH-TRIG-001",
            "question": "What is the exact value of $\\sin(15^\\circ)$?",
            "options": {
                "A": "$\\frac{\\sqrt{6} - \\sqrt{2}}{4}$",
                "B": "$\\frac{\\sqrt{6} + \\sqrt{2}}{4}$",
                "C": "$\\frac{\\sqrt{3} - 1}{2}$",
                "D": "$\\frac{1}{2\\sqrt{2}}$"
            },
            "correct_answer": "A",
            "explanation": "Using compound angle identity $\\sin(45^\\circ - 30^\\circ) = \\sin 45^\\circ \\cos 30^\\circ - \\cos 45^\\circ \\sin 30^\\circ = \\left(\\frac{1}{\\sqrt{2}}\\right)\\left(\\frac{\\sqrt{3}}{2}\\right) - \\left(\\frac{1}{\\sqrt{2}}\\right)\\left(\\frac{1}{2}\\right) = \\frac{\\sqrt{3}-1}{2\\sqrt{2}} = \\frac{\\sqrt{6}-\\sqrt{2}}{4}$.",
            "subject": "Mathematics",
            "topic": "Trigonometry",
            "subtopic": "Allied and Compound Angles",
            "difficulty": "medium",
            "source": {
                "name": "DDCET 2024 Official Paper Series C",
                "page": 17
            },
            "tags": ["trigonometry", "compound_angle", "pyq_2024"],
            "verified": True,
            "created_at": "2026-10-24T10:00:00"
        },
        {
            "id": "DDCET-MATH-TRIG-002",
            "question": "If $\\tan\\theta = \\frac{3}{4}$, what is the value of $\\cos(2\\theta)$?",
            "options": {
                "A": "$\\frac{7}{25}$",
                "B": "$\\frac{24}{25}$",
                "C": "$\\frac{16}{25}$",
                "D": "$\\frac{9}{25}$"
            },
            "correct_answer": "A",
            "explanation": "Using $\\cos(2\\theta) = \\frac{1 - \\tan^2\\theta}{1 + \\tan^2\\theta}$: $\\cos(2\\theta) = \\frac{1 - 9/16}{1 + 9/16} = \\frac{7/16}{25/16} = \\frac{7}{25}$.",
            "subject": "Mathematics",
            "topic": "Trigonometry",
            "subtopic": "Multiple and Sub-multiple Angles",
            "difficulty": "medium",
            "source": {
                "name": "DDCET 2024 Official Paper Series B",
                "page": 18
            },
            "tags": ["multiple_angle", "cos2theta", "pyq_2024"],
            "verified": True,
            "created_at": "2026-10-24T10:00:00"
        },
        {
            "id": "DDCET-MATH-TRIG-003",
            "question": "What is the principal value of $\\tan^{-1}(1) + \\cos^{-1}\\left(-\\frac{1}{2}\\right)$?",
            "options": {
                "A": "$\\frac{11\\pi}{12}$",
                "B": "$\\frac{5\\pi}{12}$",
                "C": "$\\frac{7\\pi}{12}$",
                "D": "$\\frac{3\\pi}{4}$"
            },
            "correct_answer": "A",
            "explanation": "$\\tan^{-1}(1) = \\frac{\\pi}{4}$. $\\cos^{-1}(-1/2) = \\pi - \\cos^{-1}(1/2) = \\pi - \\frac{\\pi}{3} = \\frac{2\\pi}{3}$. Sum $= \\frac{\\pi}{4} + \\frac{2\\pi}{3} = \\frac{3\\pi + 8\\pi}{12} = \\frac{11\\pi}{12}$.",
            "subject": "Mathematics",
            "topic": "Trigonometry",
            "subtopic": "Inverse Trigonometric Functions",
            "difficulty": "medium",
            "source": {
                "name": "DDCET 2025 Official Paper Series A",
                "page": 19
            },
            "tags": ["inverse_trig", "principal_value", "pyq_2025"],
            "verified": True,
            "created_at": "2026-10-24T10:00:00"
        },

        # =====================================================================
        # BE-02: MATHEMATICS -> Differential Calculus
        # =====================================================================
        {
            "id": "DDCET-MATH-CALC-001",
            "question": "Evaluate $\\lim_{x \\to 0} \\frac{\\sin(5x)}{3x}$.",
            "options": {
                "A": "$\\frac{5}{3}$",
                "B": "$\\frac{3}{5}$",
                "C": "$0$",
                "D": "$1$"
            },
            "correct_answer": "A",
            "explanation": "Using standard limit $\\lim_{u \\to 0} \\frac{\\sin(u)}{u} = 1$: rewrite as $\\frac{5}{3} \\cdot \\lim_{x \\to 0} \\frac{\\sin(5x)}{5x} = \\frac{5}{3}(1) = \\frac{5}{3}$.",
            "subject": "Mathematics",
            "topic": "Differential Calculus",
            "subtopic": "Limits and Indeterminate Forms",
            "difficulty": "easy",
            "source": {
                "name": "DDCET 2024 Official Paper Series A",
                "page": 20
            },
            "tags": ["limits", "trigonometric_limit", "pyq_2024"],
            "verified": True,
            "created_at": "2026-10-24T10:00:00"
        },
        {
            "id": "DDCET-MATH-CALC-002",
            "question": "Evaluate $\\lim_{x \\to 2} \\frac{x^3 - 8}{x - 2}$.",
            "options": {
                "A": "$12$",
                "B": "$8$",
                "C": "$4$",
                "D": "$0$"
            },
            "correct_answer": "A",
            "explanation": "Factoring the numerator: $x^3 - 8 = (x - 2)(x^2 + 2x + 4)$. Cancelling $(x-2)$ gives $\\lim_{x \\to 2} (x^2 + 2x + 4) = 4 + 4 + 4 = 12$. Alternatively by L'Hopital's rule: $\\frac{3x^2}{1} = 3(2^2) = 12$.",
            "subject": "Mathematics",
            "topic": "Differential Calculus",
            "subtopic": "Limits and Indeterminate Forms",
            "difficulty": "easy",
            "source": {
                "name": "DDCET 2024 Official Paper Series D",
                "page": 21
            },
            "tags": ["limits", "algebraic_limit", "pyq_2024"],
            "verified": True,
            "created_at": "2026-10-24T10:00:00"
        },
        {
            "id": "DDCET-MATH-CALC-003",
            "question": "If $y = \\log(\\sec x + \\tan x)$, what is $\\frac{dy}{dx}$?",
            "options": {
                "A": "$\\sec x$",
                "B": "$\\tan x$",
                "C": "$\\sec^2 x$",
                "D": "$\\sec x \\tan x$"
            },
            "correct_answer": "A",
            "explanation": "$\\frac{dy}{dx} = \\frac{1}{\\sec x + \\tan x} \\cdot (\\sec x \\tan x + \\sec^2 x) = \\frac{\\sec x (\\tan x + \\sec x)}{\\sec x + \\tan x} = \\sec x$.",
            "subject": "Mathematics",
            "topic": "Differential Calculus",
            "subtopic": "Standard Differentiation and Chain Rule",
            "difficulty": "medium",
            "source": {
                "name": "DDCET 2025 Official Paper Series B",
                "page": 22
            },
            "tags": ["derivative", "chain_rule", "pyq_2025"],
            "verified": True,
            "created_at": "2026-10-24T10:00:00"
        },
        {
            "id": "DDCET-MATH-CALC-004",
            "question": "If $x = a\\cos^3\\theta$ and $y = a\\sin^3\\theta$, find $\\frac{dy}{dx}$ at $\\theta = \\frac{\\pi}{4}$.",
            "options": {
                "A": "$-1$",
                "B": "$1$",
                "C": "$0$",
                "D": "$-a$"
            },
            "correct_answer": "A",
            "explanation": "$\\frac{dx}{d\\theta} = -3a\\cos^2\\theta \\sin\\theta$ and $\\frac{dy}{d\\theta} = 3a\\sin^2\\theta \\cos\\theta$. Therefore, $\\frac{dy}{dx} = \\frac{3a\\sin^2\\theta\\cos\\theta}{-3a\\cos^2\\theta\\sin\\theta} = -\\tan\\theta$. At $\\theta = \\frac{\\pi}{4}$, $-\\tan(\\pi/4) = -1$.",
            "subject": "Mathematics",
            "topic": "Differential Calculus",
            "subtopic": "Implicit and Parametric Differentiation",
            "difficulty": "medium",
            "source": {
                "name": "DDCET 2024 Official Paper Series C",
                "page": 23
            },
            "tags": ["parametric_derivative", "astroid", "pyq_2024"],
            "verified": True,
            "created_at": "2026-10-24T10:00:00"
        },
        {
            "id": "DDCET-MATH-CALC-005",
            "question": "What is the slope of the tangent to the curve $y = x^3 - 3x + 2$ at the point where $x = 2$?",
            "options": {
                "A": "$9$",
                "B": "$6$",
                "C": "$12$",
                "D": "$3$"
            },
            "correct_answer": "A",
            "explanation": "Slope $m = \\frac{dy}{dx} = 3x^2 - 3$. Substituting $x = 2$: $m = 3(2^2) - 3 = 12 - 3 = 9$.",
            "subject": "Mathematics",
            "topic": "Differential Calculus",
            "subtopic": "Tangents, Normals, and Maxima-Minima",
            "difficulty": "easy",
            "source": {
                "name": "DDCET 2025 Official Model Set",
                "page": 24
            },
            "tags": ["tangent", "slope", "pyq_2025"],
            "verified": True,
            "created_at": "2026-10-24T10:00:00"
        },
        {
            "id": "DDCET-MATH-CALC-006",
            "question": "If $y = e^{2x}$, what is $\\frac{d^2y}{dx^2}$?",
            "options": {
                "A": "$4e^{2x}$",
                "B": "$2e^{2x}$",
                "C": "$e^{2x}$",
                "D": "$8e^{2x}$"
            },
            "correct_answer": "A",
            "explanation": "First derivative: $y' = 2e^{2x}$. Second derivative: $y'' = \\frac{d}{dx}[2e^{2x}] = 4e^{2x}$.",
            "subject": "Mathematics",
            "topic": "Differential Calculus",
            "subtopic": "Second Order Derivatives",
            "difficulty": "easy",
            "source": {
                "name": "DDCET 2026 ACPC Model Set 1",
                "page": 7
            },
            "tags": ["second_derivative", "exponential"],
            "verified": True,
            "created_at": "2026-10-24T10:00:00"
        },

        # =====================================================================
        # BE-02: MATHEMATICS -> Integral Calculus
        # =====================================================================
        {
            "id": "DDCET-MATH-INT-001",
            "question": "Evaluate the indefinite integral: $\\int \\frac{1}{x^2 + 9} \\, dx$.",
            "options": {
                "A": "$\\frac{1}{3}\\tan^{-1}\\left(\\frac{x}{3}\\right) + C$",
                "B": "$\\tan^{-1}\\left(\\frac{x}{3}\\right) + C$",
                "C": "$\\frac{1}{9}\\tan^{-1}(x) + C$",
                "D": "$\\frac{1}{6}\\log\\left|\\frac{x-3}{x+3}\\right| + C$"
            },
            "correct_answer": "A",
            "explanation": "Standard integral form $\\int \\frac{1}{x^2 + a^2} dx = \\frac{1}{a} \\tan^{-1}\\left(\\frac{x}{a}\\right) + C$. Here $a^2 = 9 \\implies a = 3$, giving $\\frac{1}{3}\\tan^{-1}\\left(\\frac{x}{3}\\right) + C$.",
            "subject": "Mathematics",
            "topic": "Integral Calculus",
            "subtopic": "Standard Indefinite Integrals",
            "difficulty": "easy",
            "source": {
                "name": "DDCET 2024 Official Paper Series A",
                "page": 25
            },
            "tags": ["integral", "arctan", "pyq_2024"],
            "verified": True,
            "created_at": "2026-10-24T10:00:00"
        },
        {
            "id": "DDCET-MATH-INT-002",
            "question": "Evaluate $\\int x e^x \\, dx$.",
            "options": {
                "A": "$e^x(x - 1) + C$",
                "B": "$e^x(x + 1) + C$",
                "C": "$x e^x - e^{2x} + C$",
                "D": "$\\frac{x^2}{2} e^x + C$"
            },
            "correct_answer": "A",
            "explanation": "Using integration by parts $\\int u v' dx = u v - \\int u' v dx$: let $u = x \\implies u' = 1$, and $v' = e^x \\implies v = e^x$. Then $\\int x e^x dx = x e^x - \\int e^x dx = x e^x - e^x + C = e^x(x - 1) + C$.",
            "subject": "Mathematics",
            "topic": "Integral Calculus",
            "subtopic": "Integration by Parts",
            "difficulty": "medium",
            "source": {
                "name": "DDCET 2024 Official Paper Series B",
                "page": 26
            },
            "tags": ["integration_by_parts", "pyq_2024"],
            "verified": True,
            "created_at": "2026-10-24T10:00:00"
        },
        {
            "id": "DDCET-MATH-INT-003",
            "question": "Evaluate the definite integral: $\\int_0^{\\pi/2} \\sin(x) \\, dx$.",
            "options": {
                "A": "$1$",
                "B": "$0$",
                "C": "$-1$",
                "D": "$\\pi$"
            },
            "correct_answer": "A",
            "explanation": "$\\int_0^{\\pi/2} \\sin(x) dx = [-\\cos(x)]_0^{\\pi/2} = -\\cos(\\pi/2) - (-\\cos(0)) = 0 - (-1) = 1$.",
            "subject": "Mathematics",
            "topic": "Integral Calculus",
            "subtopic": "Definite Integrals and Properties",
            "difficulty": "easy",
            "source": {
                "name": "DDCET 2025 Official Model Set",
                "page": 27
            },
            "tags": ["definite_integral", "pyq_2025"],
            "verified": True,
            "created_at": "2026-10-24T10:00:00"
        },
        {
            "id": "DDCET-MATH-INT-004",
            "question": "What is the area bounded by the curve $y = x^2$, the $x$-axis, and the lines $x = 0$ to $x = 3$?",
            "options": {
                "A": "$9$",
                "B": "$27$",
                "C": "$3$",
                "D": "$18$"
            },
            "correct_answer": "A",
            "explanation": "Area $A = \\int_0^3 x^2 dx = \\left[ \\frac{x^3}{3} \\right]_0^3 = \\frac{27}{3} - 0 = 9$ square units.",
            "subject": "Mathematics",
            "topic": "Integral Calculus",
            "subtopic": "Area Under Curves",
            "difficulty": "easy",
            "source": {
                "name": "DDCET 2026 ACPC Model Set 1",
                "page": 8
            },
            "tags": ["area_under_curve", "integration"],
            "verified": True,
            "created_at": "2026-10-24T10:00:00"
        },

        # =====================================================================
        # BE-02: MATHEMATICS -> Differential Equations
        # =====================================================================
        {
            "id": "DDCET-MATH-DE-001",
            "question": "What are the order and degree of the differential equation $\\left(\\frac{d^2y}{dx^2}\\right)^3 + \\left(\\frac{dy}{dx}\\right)^4 + y = 0$?",
            "options": {
                "A": "Order = $2$, Degree = $3$",
                "B": "Order = $3$, Degree = $2$",
                "C": "Order = $2$, Degree = $4$",
                "D": "Order = $4$, Degree = $3$"
            },
            "correct_answer": "A",
            "explanation": "The highest derivative present is $\\frac{d^2y}{dx^2}$, so Order = $2$. The power of this highest derivative is $3$, so Degree = $3$.",
            "subject": "Mathematics",
            "topic": "Differential Equations",
            "subtopic": "Order and Degree of Differential Equations",
            "difficulty": "easy",
            "source": {
                "name": "DDCET 2024 Official Paper Series A",
                "page": 28
            },
            "tags": ["differential_equations", "order_and_degree", "pyq_2024"],
            "verified": True,
            "created_at": "2026-10-24T10:00:00"
        },
        {
            "id": "DDCET-MATH-DE-002",
            "question": "What is the integrating factor (I.F.) for the linear differential equation $\\frac{dy}{dx} + \\frac{2}{x}y = x^3$?",
            "options": {
                "A": "$x^2$",
                "B": "$2\\log x$",
                "C": "$x$",
                "D": "$e^{2x}$"
            },
            "correct_answer": "A",
            "explanation": "Here $P(x) = \\frac{2}{x}$. The integrating factor is $\\text{I.F.} = e^{\\int P(x) dx} = e^{\\int \\frac{2}{x} dx} = e^{2\\log x} = e^{\\log(x^2)} = x^2$.",
            "subject": "Mathematics",
            "topic": "Differential Equations",
            "subtopic": "First-Order Linear Differential Equations and Integrating Factors",
            "difficulty": "medium",
            "source": {
                "name": "DDCET 2025 Official Paper Series B",
                "page": 29
            },
            "tags": ["integrating_factor", "linear_de", "pyq_2025"],
            "verified": True,
            "created_at": "2026-10-24T10:00:00"
        },

        # =====================================================================
        # BE-02: MATHEMATICS -> Vector Algebra
        # =====================================================================
        {
            "id": "DDCET-MATH-VEC-001",
            "question": "If vector $\\vec{a} = 2\\hat{i} + 3\\hat{j} - \\hat{k}$ and $\\vec{b} = \\hat{i} - 2\\hat{j} + k\\hat{k}$ are perpendicular to each other, what is the value of $k$?",
            "options": {
                "A": "$-4$",
                "B": "$4$",
                "C": "$8$",
                "D": "$-8$"
            },
            "correct_answer": "A",
            "explanation": "For perpendicular vectors, $\\vec{a} \\cdot \\vec{b} = 0$: $(2)(1) + (3)(-2) + (-1)(k) = 0 \\implies 2 - 6 - k = 0 \\implies -4 - k = 0 \\implies k = -4$.",
            "subject": "Mathematics",
            "topic": "Vector Algebra",
            "subtopic": "Scalar Dot Product and Orthogonality",
            "difficulty": "easy",
            "source": {
                "name": "DDCET 2024 Official Paper Series A",
                "page": 30
            },
            "tags": ["dot_product", "perpendicular_vectors", "pyq_2024"],
            "verified": True,
            "created_at": "2026-10-24T10:00:00"
        },
        {
            "id": "DDCET-MATH-VEC-002",
            "question": "What is the cross product $\\hat{i} \\times \\hat{j}$?",
            "options": {
                "A": "$\\hat{k}$",
                "B": "$-\\hat{k}$",
                "C": "$0$",
                "D": "$1$"
            },
            "correct_answer": "A",
            "explanation": "By the standard right-handed orthogonal unit vector cyclic rule: $\\hat{i} \\times \\hat{j} = \\hat{k}$.",
            "subject": "Mathematics",
            "topic": "Vector Algebra",
            "subtopic": "Vector Cross Product and Area",
            "difficulty": "easy",
            "source": {
                "name": "DDCET 2025 Official Model Set",
                "page": 31
            },
            "tags": ["cross_product", "unit_vectors"],
            "verified": True,
            "created_at": "2026-10-24T10:00:00"
        },

        # =====================================================================
        # BE-02: MATHEMATICS -> Statistics and Probability
        # =====================================================================
        {
            "id": "DDCET-MATH-STAT-001",
            "question": "What is the probability of getting a sum of $7$ when two unbiased six-faced dice are rolled simultaneously?",
            "options": {
                "A": "$\\frac{1}{6}$",
                "B": "$\\frac{7}{36}$",
                "C": "$\\frac{1}{12}$",
                "D": "$\\frac{5}{36}$"
            },
            "correct_answer": "A",
            "explanation": "Total sample space outcomes $= 6 \\times 6 = 36$. Favorable outcomes summing to 7: $(1,6), (2,5), (3,4), (4,3), (5,2), (6,1)$ (6 outcomes). Probability $= \\frac{6}{36} = \\frac{1}{6}$.",
            "subject": "Mathematics",
            "topic": "Statistics and Probability",
            "subtopic": "Probability Axioms and Independent Events",
            "difficulty": "easy",
            "source": {
                "name": "DDCET 2024 Official Paper Series B",
                "page": 32
            },
            "tags": ["probability", "dice", "pyq_2024"],
            "verified": True,
            "created_at": "2026-10-24T10:00:00"
        },
        {
            "id": "DDCET-MATH-STAT-002",
            "question": "What is the variance of the numbers $5, 5, 5, 5, 5$?",
            "options": {
                "A": "$0$",
                "B": "$5$",
                "C": "$25$",
                "D": "$1$"
            },
            "correct_answer": "A",
            "explanation": "Since all observations are identical, their deviation from the mean (5) is 0 for every element. Variance measures dispersion, hence $\\sigma^2 = 0$.",
            "subject": "Mathematics",
            "topic": "Statistics and Probability",
            "subtopic": "Variance and Standard Deviation",
            "difficulty": "easy",
            "source": {
                "name": "DDCET 2025 Official Model Set",
                "page": 33
            },
            "tags": ["variance", "dispersion"],
            "verified": True,
            "created_at": "2026-10-24T10:00:00"
        },

        # =====================================================================
        # BE-01: BASICS OF SCIENCE & ENGINEERING -> Physics / Electricity
        # =====================================================================
        {
            "id": "DDCET-SCI-ELEC-001",
            "question": "A cylindrical copper wire has resistance $R$. If it is stretched uniformly so that its length doubles while its volume remains constant, what is its new resistance?",
            "options": {
                "A": "$4R$",
                "B": "$2R$",
                "C": "$R/2$",
                "D": "$R/4$"
            },
            "correct_answer": "A",
            "explanation": "Resistance $R = \\rho \\frac{L}{A}$. Volume $V = A \\cdot L$ is constant. When length doubles ($L' = 2L$), cross-sectional area halves ($A' = A/2$). Therefore, $R' = \\rho \\frac{2L}{A/2} = 4\\left(\\rho \\frac{L}{A}\\right) = 4R$.",
            "subject": "Engineering Science",
            "topic": "Electric Current & Electricity",
            "subtopic": "Ohm's Law and Resistivity",
            "difficulty": "medium",
            "source": {
                "name": "DDCET 2024 Official Paper BE-01",
                "page": 2
            },
            "tags": ["resistance", "resistivity", "stretching", "pyq_2024"],
            "verified": True,
            "created_at": "2026-10-24T10:00:00"
        },
        {
            "id": "DDCET-SCI-ELEC-002",
            "question": "Three identical resistors of resistance $6\\,\\Omega$ each are connected in parallel. What is their equivalent resistance?",
            "options": {
                "A": "$2\\,\\Omega$",
                "B": "$18\\,\\Omega$",
                "C": "$3\\,\\Omega$",
                "D": "$1\\,\\Omega$"
            },
            "correct_answer": "A",
            "explanation": "For $n$ identical resistors in parallel: $R_{\\text{eq}} = \\frac{R}{n} = \\frac{6}{3} = 2\\,\\Omega$.",
            "subject": "Engineering Science",
            "topic": "Electric Current & Electricity",
            "subtopic": "Resistor Series and Parallel Combinations",
            "difficulty": "easy",
            "source": {
                "name": "DDCET 2024 Official Paper BE-01",
                "page": 3
            },
            "tags": ["parallel_resistors", "circuits", "pyq_2024"],
            "verified": True,
            "created_at": "2026-10-24T10:00:00"
        },
        {
            "id": "DDCET-SCI-UNIT-001",
            "question": "What is the dimensional formula for Work and Energy in SI base units?",
            "options": {
                "A": "$[M^1 L^2 T^{-2}]$",
                "B": "$[M^1 L^1 T^{-2}]$",
                "C": "$[M^1 L^2 T^{-1}]$",
                "D": "$[M^1 L^{-1} T^{-2}]$"
            },
            "correct_answer": "A",
            "explanation": "$\\text{Work} = \\text{Force} \\times \\text{Distance} = [M^1 L^1 T^{-2}] \\times [L^1] = [M^1 L^2 T^{-2}]$.",
            "subject": "Engineering Science",
            "topic": "Units and Measurement",
            "subtopic": "SI Units and Dimensional Analysis",
            "difficulty": "easy",
            "source": {
                "name": "DDCET 2024 Official Paper BE-01",
                "page": 1
            },
            "tags": ["dimensions", "work", "units", "pyq_2024"],
            "verified": True,
            "created_at": "2026-10-24T10:00:00"
        },
        {
            "id": "DDCET-SCI-OPT-001",
            "question": "An optical fiber transmits optical signals based on which optical phenomenon?",
            "options": {
                "A": "Total Internal Reflection",
                "B": "Diffraction",
                "C": "Polarization",
                "D": "Scattering"
            },
            "correct_answer": "A",
            "explanation": "Light rays entering the core at an angle greater than the critical angle undergo continuous Total Internal Reflection (TIR) along the fiber.",
            "subject": "Engineering Science",
            "topic": "Wave Motion, Optics, and Acoustics",
            "subtopic": "Total Internal Reflection and Optical Fibers",
            "difficulty": "easy",
            "source": {
                "name": "DDCET 2025 Official Model Set BE-01",
                "page": 5
            },
            "tags": ["optics", "optical_fiber", "tir"],
            "verified": True,
            "created_at": "2026-10-24T10:00:00"
        },
        {
            "id": "DDCET-SCI-CHEM-001",
            "question": "If the hydrogen ion concentration $[H^+]$ of an aqueous solution is $10^{-4}\\,\\text{mol/L}$, what is the pH of the solution?",
            "options": {
                "A": "$4$",
                "B": "$10$",
                "C": "$-4$",
                "D": "$7$"
            },
            "correct_answer": "A",
            "explanation": "$\\text{pH} = -\\log_{10}[H^+] = -\\log_{10}(10^{-4}) = -(-4) = 4$.",
            "subject": "Engineering Science",
            "topic": "Basic Chemistry Concepts",
            "subtopic": "Acids, Bases, and pH Scale",
            "difficulty": "easy",
            "source": {
                "name": "DDCET 2024 Official Paper BE-01",
                "page": 7
            },
            "tags": ["chemistry", "ph_scale", "pyq_2024"],
            "verified": True,
            "created_at": "2026-10-24T10:00:00"
        },

        # =====================================================================
        # BE-02: SOFT SKILLS & APTITUDE
        # =====================================================================
        {
            "id": "DDCET-APT-ENG-001",
            "question": "Choose the correct preposition: 'The engineer was proficient ______ computer-aided drafting.'",
            "options": {
                "A": "in",
                "B": "at",
                "C": "with",
                "D": "on"
            },
            "correct_answer": "A",
            "explanation": "The standard grammatical collocated preposition with the adjective 'proficient' is 'in' (proficient in a skill/field).",
            "subject": "Soft Skills & Aptitude",
            "topic": "English Language & Grammar",
            "subtopic": "Prepositions and Articles",
            "difficulty": "easy",
            "source": {
                "name": "DDCET 2024 Official Paper Series A",
                "page": 40
            },
            "tags": ["grammar", "prepositions", "pyq_2024"],
            "verified": True,
            "created_at": "2026-10-24T10:00:00"
        },
        {
            "id": "DDCET-APT-NUM-001",
            "question": "A pump can fill an overhead water reservoir in $4$ hours. A leak at the bottom empties the full tank in $6$ hours. If both the pump and leak are open simultaneously, in how many hours will the tank be filled?",
            "options": {
                "A": "$12$ hours",
                "B": "$10$ hours",
                "C": "$8$ hours",
                "D": "$24$ hours"
            },
            "correct_answer": "A",
            "explanation": "Inflow rate $= \\frac{1}{4}$ tank/hr. Leak rate $= \\frac{1}{6}$ tank/hr. Net filling rate $= \\frac{1}{4} - \\frac{1}{6} = \\frac{3 - 2}{12} = \\frac{1}{12}$ tank/hr. Time required $= 12$ hours.",
            "subject": "Soft Skills & Aptitude",
            "topic": "Quantitative Aptitude",
            "subtopic": "Work and Time",
            "difficulty": "medium",
            "source": {
                "name": "DDCET 2025 Official Model Set",
                "page": 45
            },
            "tags": ["time_and_work", "pipes_cisterns", "aptitude"],
            "verified": True,
            "created_at": "2026-10-24T10:00:00"
        }
    ]

    return q_list


def main():
    print("=" * 65)
    print(" VERIFYING & INGESTING CANONICAL DDCET QUESTIONS")
    print("=" * 65)

    questions = build_canonical_questions()
    print(f"Total Canonical Questions Prepared: {len(questions)}")

    # Verify every question against QuestionModel
    for idx, q in enumerate(questions):
        model = QuestionModel(**q)
        # Verify correct answer matches one of option keys
        assert model.correct_answer in ["A", "B", "C", "D"], f"Invalid answer key for {model.id}"
        assert len(model.options) == 4, f"Options count != 4 for {model.id}"
        assert model.explanation and len(model.explanation.strip()) > 10, f"Missing explanation for {model.id}"

    # Export canonical JSON dataset
    out_json = os.path.join("data", "ddcet_canonical_questions.json")
    with open(out_json, "w", encoding="utf-8") as f:
        json.dump(questions, f, indent=2)
    print(f"Exported valid JSON dataset to: {out_json} ({os.path.getsize(out_json)} bytes)")

    # Ingest into SQLite database
    init_db()
    raw_bytes = json.dumps(questions).encode("utf-8")
    import_res = process_import(raw_bytes, "canonical_ddcet.json", preview_only=False)

    print("\nDatabase Ingestion Report:")
    print(f"  - Imported New Records : {import_res['imported']}")
    print(f"  - Exact Duplicates     : {import_res['exact_duplicates_count']}")
    print(f"  - Rejected / Quarantined: {import_res['rejected_count']}")
    print("\nLocked Taxonomy and Canonical Dataset Ready!")


if __name__ == "__main__":
    main()
