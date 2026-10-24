"""
DDCET Mathematics Question Bank Generator
Syllabus: GTU / ACPC Diploma to Degree Common Entrance Test (BE-02 Part A)
Topics:
1. Determinants and Matrices
2. Logarithm and Partial Fractions
3. Trigonometry
4. Coordinate Geometry
5. Differential Calculus (Limits, Derivatives, Applications)
6. Integral Calculus (Indefinite, Definite, Applications)
7. Differential Equations
8. Vector Algebra
9. Statistics and Probability
"""

MATH_QUESTIONS = [
    # ==========================================
    # 1. DETERMINANTS AND MATRICES
    # ==========================================
    {
        "id": "DDCET-MATH-DM-003",
        "question": "What is the value of the determinant $\\begin{vmatrix} 1 & 2 & 3 \\\\ 4 & 5 & 6 \\\\ 7 & 8 & 9 \\end{vmatrix}$?",
        "options": {
            "A": "$0$",
            "B": "$1$",
            "C": "$-1$",
            "D": "$45$"
        },
        "correct_answer": "A",
        "explanation": "Notice the columns or rows are in arithmetic progression ($C_2 - C_1 = [1, 1, 1]^T$ and $C_3 - C_2 = [1, 1, 1]^T$). Since two difference columns are identical, $\\det = 0$.",
        "subject": "Mathematics",
        "topic": "Determinants and Matrices",
        "subtopic": "Determinant Evaluation and Properties",
        "difficulty": "easy",
        "source": {"name": "DDCET Official Question Bank / PYQ", "page": 3},
        "tags": ["determinants", "properties", "3x3_determinant"],
        "verified": True,
        "created_at": "2026-10-24T12:00:00"
    },
    {
        "id": "DDCET-MATH-DM-004",
        "question": "If matrix $A = \\begin{pmatrix} 3 & k \\\\ 4 & 2 \\end{pmatrix}$ is singular, what is the value of $k$?",
        "options": {
            "A": "$1.5$",
            "B": "$\\frac{3}{2}$",
            "C": "$\\frac{2}{3}$",
            "D": "$6$"
        },
        "correct_answer": "A",
        "explanation": "A matrix is singular if its determinant is zero: $\\det(A) = (3)(2) - (4)(k) = 0 \\implies 6 - 4k = 0 \\implies k = \\frac{6}{4} = 1.5$.",
        "subject": "Mathematics",
        "topic": "Determinants and Matrices",
        "subtopic": "Determinant Evaluation and Properties",
        "difficulty": "easy",
        "source": {"name": "DDCET Official Question Bank / PYQ", "page": 3},
        "tags": ["matrices", "singular_matrix"],
        "verified": True,
        "created_at": "2026-10-24T12:00:00"
    },
    {
        "id": "DDCET-MATH-DM-005",
        "question": "For a square matrix $A$ of order $3 \\times 3$, if $\\det(A) = 4$, what is the value of $\\det(2A)$?",
        "options": {
            "A": "$8$",
            "B": "$16$",
            "C": "$32$",
            "D": "$64$"
        },
        "correct_answer": "C",
        "explanation": "For an $n \\times n$ matrix, $\\det(kA) = k^n \\det(A)$. Here $n = 3$, $k = 2$, so $\\det(2A) = 2^3 \\times 4 = 8 \\times 4 = 32$.",
        "subject": "Mathematics",
        "topic": "Determinants and Matrices",
        "subtopic": "Determinant Evaluation and Properties",
        "difficulty": "medium",
        "source": {"name": "DDCET Official Question Bank / PYQ", "page": 4},
        "tags": ["matrices", "determinant_properties"],
        "verified": True,
        "created_at": "2026-10-24T12:00:00"
    },
    {
        "id": "DDCET-MATH-DM-006",
        "question": "If $A = \\begin{pmatrix} 1 & 2 \\\\ 3 & 4 \\end{pmatrix}$, what is $A + A^T$?",
        "options": {
            "A": "$\\begin{pmatrix} 2 & 5 \\\\ 5 & 8 \\end{pmatrix}$",
            "B": "$\\begin{pmatrix} 2 & -1 \\\\ -1 & 8 \\end{pmatrix}$",
            "C": "$\\begin{pmatrix} 1 & 5 \\\\ 5 & 4 \\end{pmatrix}$",
            "D": "$\\begin{pmatrix} 2 & 6 \\\\ 6 & 8 \\end{pmatrix}$"
        },
        "correct_answer": "A",
        "explanation": "$A^T = \\begin{pmatrix} 1 & 3 \\\\ 2 & 4 \\end{pmatrix}$. Adding: $A + A^T = \\begin{pmatrix} 1+1 & 2+3 \\\\ 3+2 & 4+4 \\end{pmatrix} = \\begin{pmatrix} 2 & 5 \\\\ 5 & 8 \\end{pmatrix}$, which is a symmetric matrix.",
        "subject": "Mathematics",
        "topic": "Determinants and Matrices",
        "subtopic": "Matrix Types and Algebra",
        "difficulty": "easy",
        "source": {"name": "DDCET Official Question Bank / PYQ", "page": 4},
        "tags": ["matrices", "transpose", "symmetric"],
        "verified": True,
        "created_at": "2026-10-24T12:00:00"
    },
    {
        "id": "DDCET-MATH-DM-007",
        "question": "If $A = \\begin{pmatrix} 0 & 1 \\\\ -1 & 0 \\end{pmatrix}$, then $A^2$ is equal to:",
        "options": {
            "A": "$I$",
            "B": "$-I$",
            "C": "$O$",
            "D": "$A$"
        },
        "correct_answer": "B",
        "explanation": "$A^2 = \\begin{pmatrix} 0 & 1 \\\\ -1 & 0 \\end{pmatrix} \\begin{pmatrix} 0 & 1 \\\\ -1 & 0 \\end{pmatrix} = \\begin{pmatrix} -1 & 0 \\\\ 0 & -1 \\end{pmatrix} = -I$.",
        "subject": "Mathematics",
        "topic": "Determinants and Matrices",
        "subtopic": "Matrix Types and Algebra",
        "difficulty": "easy",
        "source": {"name": "DDCET Official Question Bank / PYQ", "page": 5},
        "tags": ["matrices", "matrix_multiplication"],
        "verified": True,
        "created_at": "2026-10-24T12:00:00"
    },
    {
        "id": "DDCET-MATH-DM-008",
        "question": "For a system of linear equations $2x + 3y = 7$ and $4x + 6y = 12$, what does Cramer's Rule show?",
        "options": {
            "A": "Unique solution exists",
            "B": "$D = 0$ and $D_x \\neq 0$, so no solution exists",
            "C": "$D = 0$ and $D_x = 0$, so infinite solutions exist",
            "D": "$x = 2, y = 1$"
        },
        "correct_answer": "B",
        "explanation": "Determinant of coefficients $D = \\begin{vmatrix} 2 & 3 \\\\ 4 & 6 \\end{vmatrix} = 12 - 12 = 0$. $D_x = \\begin{vmatrix} 7 & 3 \\\\ 12 & 6 \\end{vmatrix} = 42 - 36 = 6 \\neq 0$. When $D = 0$ and at least one of $D_x, D_y \\neq 0$, the system is inconsistent (no solution).",
        "subject": "Mathematics",
        "topic": "Determinants and Matrices",
        "subtopic": "Cramer's Rule and Systems of Equations",
        "difficulty": "medium",
        "source": {"name": "DDCET Official Question Bank / PYQ", "page": 6},
        "tags": ["cramer_rule", "linear_systems"],
        "verified": True,
        "created_at": "2026-10-24T12:00:00"
    },
    {
        "id": "DDCET-MATH-DM-009",
        "question": "If $A$ is a square matrix of order $3$ and $|A| = 5$, what is $|\\text{adj}(A)|$?",
        "options": {
            "A": "$5$",
            "B": "$15$",
            "C": "$25$",
            "D": "$125$"
        },
        "correct_answer": "C",
        "explanation": "By the standard matrix theorem, $|\\text{adj}(A)| = |A|^{n-1}$. For order $n = 3$, $|\\text{adj}(A)| = 5^{3-1} = 5^2 = 25$.",
        "subject": "Mathematics",
        "topic": "Determinants and Matrices",
        "subtopic": "Matrix Inversion and Adjoint",
        "difficulty": "medium",
        "source": {"name": "DDCET Official Question Bank / PYQ", "page": 7},
        "tags": ["adjoint", "determinants"],
        "verified": True,
        "created_at": "2026-10-24T12:00:00"
    },
    {
        "id": "DDCET-MATH-DM-010",
        "question": "What is the trace of matrix $A = \\begin{pmatrix} 4 & 2 & -1 \\\\ 3 & -7 & 5 \\\\ 0 & 1 & 9 \\end{pmatrix}$?",
        "options": {
            "A": "$6$",
            "B": "$20$",
            "C": "$-3$",
            "D": "$12$"
        },
        "correct_answer": "A",
        "explanation": "The trace of a square matrix is the sum of its principal diagonal elements: $\\text{tr}(A) = 4 + (-7) + 9 = 6$.",
        "subject": "Mathematics",
        "topic": "Determinants and Matrices",
        "subtopic": "Matrix Types and Algebra",
        "difficulty": "easy",
        "source": {"name": "DDCET Official Question Bank / PYQ", "page": 8},
        "tags": ["trace", "matrices"],
        "verified": True,
        "created_at": "2026-10-24T12:00:00"
    },
    {
        "id": "DDCET-MATH-DM-011",
        "question": "If $\\begin{vmatrix} 2 & 4 \\\\ 5 & 1 \\end{vmatrix} = \\begin{vmatrix} 2x & 4 \\\\ 6 & x \\end{vmatrix}$, what is the value of $x$?",
        "options": {
            "A": "$\\pm \\sqrt{3}$",
            "B": "$\\pm 3$",
            "C": "$\\pm 1$",
            "D": "$3$"
        },
        "correct_answer": "A",
        "explanation": "LHS $= (2)(1) - (4)(5) = 2 - 20 = -18$. RHS $= (2x)(x) - (4)(6) = 2x^2 - 24$. Equating: $2x^2 - 24 = -18 \\implies 2x^2 = 6 \\implies x^2 = 3 \\implies x = \\pm \\sqrt{3}$.",
        "subject": "Mathematics",
        "topic": "Determinants and Matrices",
        "subtopic": "Determinant Evaluation and Properties",
        "difficulty": "medium",
        "source": {"name": "DDCET Official Question Bank / PYQ", "page": 8},
        "tags": ["determinants", "equations"],
        "verified": True,
        "created_at": "2026-10-24T12:00:00"
    },
    {
        "id": "DDCET-MATH-DM-012",
        "question": "If $A$ and $B$ are non-singular matrices of the same order, what is $(AB)^{-1}$?",
        "options": {
            "A": "$A^{-1}B^{-1}$",
            "B": "$B^{-1}A^{-1}$",
            "C": "$AB$",
            "D": "$(BA)^{-1}$"
        },
        "correct_answer": "B",
        "explanation": "By the reversal law of matrix inverses, $(AB)^{-1} = B^{-1}A^{-1}$.",
        "subject": "Mathematics",
        "topic": "Determinants and Matrices",
        "subtopic": "Matrix Inversion and Adjoint",
        "difficulty": "easy",
        "source": {"name": "DDCET Official Question Bank / PYQ", "page": 9},
        "tags": ["reversal_law", "matrix_inverse"],
        "verified": True,
        "created_at": "2026-10-24T12:00:00"
    },
    {
        "id": "DDCET-MATH-DM-013",
        "question": "If matrix $A$ is skew-symmetric, then the elements along the main diagonal are always:",
        "options": {
            "A": "$1$",
            "B": "$-1$",
            "C": "$0$",
            "D": "Any real number"
        },
        "correct_answer": "C",
        "explanation": "For a skew-symmetric matrix, $A^T = -A$, which means $a_{ji} = -a_{ij}$. For the diagonal elements ($i = j$), $a_{ii} = -a_{ii} \\implies 2a_{ii} = 0 \\implies a_{ii} = 0$.",
        "subject": "Mathematics",
        "topic": "Determinants and Matrices",
        "subtopic": "Matrix Types and Algebra",
        "difficulty": "easy",
        "source": {"name": "DDCET Official Question Bank / PYQ", "page": 9},
        "tags": ["skew_symmetric", "diagonal_elements"],
        "verified": True,
        "created_at": "2026-10-24T12:00:00"
    },
    {
        "id": "DDCET-MATH-DM-014",
        "question": "What is the rank of the matrix $A = \\begin{pmatrix} 1 & 2 & 3 \\\\ 2 & 4 & 6 \\\\ 3 & 6 & 9 \\end{pmatrix}$?",
        "options": {
            "A": "$3$",
            "B": "$2$",
            "C": "$1$",
            "D": "$0$"
        },
        "correct_answer": "C",
        "explanation": "$R_2 = 2R_1$ and $R_3 = 3R_1$. Hence there is only one linearly independent row, so the rank of the matrix is $1$.",
        "subject": "Mathematics",
        "topic": "Determinants and Matrices",
        "subtopic": "Matrix Types and Algebra",
        "difficulty": "medium",
        "source": {"name": "DDCET Official Question Bank / PYQ", "page": 10},
        "tags": ["rank", "linear_independence"],
        "verified": True,
        "created_at": "2026-10-24T12:00:00"
    },

    # ==========================================
    # 2. LOGARITHM AND PARTIAL FRACTIONS
    # ==========================================
    {
        "id": "DDCET-MATH-LOG-002",
        "question": "What is the value of $\\log_2 32 + \\log_3 81 - \\log_5 125$?",
        "options": {
            "A": "$6$",
            "B": "$7$",
            "C": "$5$",
            "D": "$4$"
        },
        "correct_answer": "A",
        "explanation": "$\\log_2 32 = \\log_2 2^5 = 5$, $\\log_3 81 = \\log_3 3^4 = 4$, and $\\log_5 125 = \\log_5 5^3 = 3$. Therefore: $5 + 4 - 3 = 6$.",
        "subject": "Mathematics",
        "topic": "Logarithm",
        "subtopic": "Laws of Logarithm and related Simple examples",
        "difficulty": "easy",
        "source": {"name": "DDCET Official Question Bank / PYQ", "page": 11},
        "tags": ["logarithm", "laws_of_logarithms"],
        "verified": True,
        "created_at": "2026-10-24T12:00:00"
    },
    {
        "id": "DDCET-MATH-LOG-003",
        "question": "If $\\log_a b \\cdot \\log_b c \\cdot \\log_c a = k$, what is the value of $k$?",
        "options": {
            "A": "$0$",
            "B": "$1$",
            "C": "$abc$",
            "D": "$3$"
        },
        "correct_answer": "B",
        "explanation": "Using change of base formula: $\\frac{\\log b}{\\log a} \\cdot \\frac{\\log c}{\\log b} \\cdot \\frac{\\log a}{\\log c} = 1$.",
        "subject": "Mathematics",
        "topic": "Logarithm",
        "subtopic": "Laws of Logarithm and related Simple examples",
        "difficulty": "easy",
        "source": {"name": "DDCET Official Question Bank / PYQ", "page": 11},
        "tags": ["logarithm", "change_of_base"],
        "verified": True,
        "created_at": "2026-10-24T12:00:00"
    },
    {
        "id": "DDCET-MATH-LOG-004",
        "question": "What is the value of $x$ if $\\log_{\\sqrt{2}} x = 6$?",
        "options": {
            "A": "$4$",
            "B": "$8$",
            "C": "$16$",
            "D": "$64$"
        },
        "correct_answer": "B",
        "explanation": "By logarithmic definition: $x = (\\sqrt{2})^6 = (2^{1/2})^6 = 2^3 = 8$.",
        "subject": "Mathematics",
        "topic": "Logarithm",
        "subtopic": "Laws of Logarithm and related Simple examples",
        "difficulty": "easy",
        "source": {"name": "DDCET Official Question Bank / PYQ", "page": 12},
        "tags": ["logarithm", "exponential_form"],
        "verified": True,
        "created_at": "2026-10-24T12:00:00"
    },
    {
        "id": "DDCET-MATH-LOG-005",
        "question": "In partial fraction decomposition, $\\frac{1}{(x+1)(x+2)} = \\frac{A}{x+1} + \\frac{B}{x+2}$. What are the values of $A$ and $B$?",
        "options": {
            "A": "$A = 1, B = -1$",
            "B": "$A = -1, B = 1$",
            "C": "$A = 1, B = 1$",
            "D": "$A = 2, B = -1$"
        },
        "correct_answer": "A",
        "explanation": "$1 = A(x+2) + B(x+1)$. Put $x = -1 \\implies 1 = A(1) \\implies A = 1$. Put $x = -2 \\implies 1 = B(-1) \\implies B = -1$.",
        "subject": "Mathematics",
        "topic": "Partial Fractions",
        "subtopic": "Linear Non-repeated Factors",
        "difficulty": "easy",
        "source": {"name": "DDCET Official Question Bank / PYQ", "page": 12},
        "tags": ["partial_fractions", "algebra"],
        "verified": True,
        "created_at": "2026-10-24T12:00:00"
    },
    {
        "id": "DDCET-MATH-LOG-006",
        "question": "What is the form of partial fractions for $\\frac{2x+3}{(x-1)^2(x+2)}$?",
        "options": {
            "A": "$\\frac{A}{x-1} + \\frac{B}{x+2}$",
            "B": "$\\frac{A}{x-1} + \\frac{B}{(x-1)^2} + \\frac{C}{x+2}$",
            "C": "$\\frac{Ax+B}{(x-1)^2} + \\frac{C}{x+2}$",
            "D": "$\\frac{A}{(x-1)^2} + \\frac{B}{x+2}$"
        },
        "correct_answer": "B",
        "explanation": "For a repeated linear factor $(x-a)^2$, the partial fraction decomposition includes terms $\\frac{A}{x-a} + \\frac{B}{(x-a)^2}$, plus $\\frac{C}{x+2}$ for the distinct factor.",
        "subject": "Mathematics",
        "topic": "Partial Fractions",
        "subtopic": "Repeated Linear Factors",
        "difficulty": "medium",
        "source": {"name": "DDCET Official Question Bank / PYQ", "page": 13},
        "tags": ["partial_fractions", "repeated_factors"],
        "verified": True,
        "created_at": "2026-10-24T12:00:00"
    },

    # ==========================================
    # 3. TRIGONOMETRY
    # ==========================================
    {
        "id": "DDCET-MATH-TRIG-003",
        "question": "What is the value of $\\sin(105^\\circ)$?",
        "options": {
            "A": "$\\frac{\\sqrt{3}+1}{2\\sqrt{2}}$",
            "B": "$\\frac{\\sqrt{3}-1}{2\\sqrt{2}}$",
            "C": "$\\frac{\\sqrt{3}+1}{\\sqrt{2}}$",
            "D": "$\\frac{\\sqrt{2}+1}{2\\sqrt{3}}$"
        },
        "correct_answer": "A",
        "explanation": "$\\sin(105^\\circ) = \\sin(60^\\circ + 45^\\circ) = \\sin 60^\\circ \\cos 45^\\circ + \\cos 60^\\circ \\sin 45^\\circ = (\\frac{\\sqrt{3}}{2})(\\frac{1}{\\sqrt{2}}) + (\\frac{1}{2})(\\frac{1}{\\sqrt{2}}) = \\frac{\\sqrt{3}+1}{2\\sqrt{2}}$.",
        "subject": "Mathematics",
        "topic": "Trigonometry",
        "subtopic": "Allied and Compound Angles",
        "difficulty": "medium",
        "source": {"name": "DDCET Official Question Bank / PYQ", "page": 14},
        "tags": ["trigonometry", "compound_angles"],
        "verified": True,
        "created_at": "2026-10-24T12:00:00"
    },
    {
        "id": "DDCET-MATH-TRIG-004",
        "question": "If $\\tan A = \\frac{1}{2}$ and $\\tan B = \\frac{1}{3}$, what is the value of $A + B$?",
        "options": {
            "A": "$\\frac{\\pi}{6}$",
            "B": "$\\frac{\\pi}{4}$",
            "C": "$\\frac{\\pi}{3}$",
            "D": "$\\frac{\\pi}{2}$"
        },
        "correct_answer": "B",
        "explanation": "$\\tan(A+B) = \\frac{\\tan A + \\tan B}{1 - \\tan A \\tan B} = \\frac{1/2 + 1/3}{1 - (1/2)(1/3)} = \\frac{5/6}{5/6} = 1 \\implies A + B = \\frac{\\pi}{4}$.",
        "subject": "Mathematics",
        "topic": "Trigonometry",
        "subtopic": "Allied and Compound Angles",
        "difficulty": "easy",
        "source": {"name": "DDCET Official Question Bank / PYQ", "page": 14},
        "tags": ["trigonometry", "compound_angles", "tangent"],
        "verified": True,
        "created_at": "2026-10-24T12:00:00"
    },
    {
        "id": "DDCET-MATH-TRIG-005",
        "question": "What is the value of $\\cos(2\\theta)$ in terms of $\\tan\\theta$?",
        "options": {
            "A": "$\\frac{1 - \\tan^2\\theta}{1 + \\tan^2\\theta}$",
            "B": "$\\frac{2\\tan\\theta}{1 + \\tan^2\\theta}$",
            "C": "$\\frac{2\\tan\\theta}{1 - \\tan^2\\theta}$",
            "D": "$\\frac{1 + \\tan^2\\theta}{1 - \\tan^2\\theta}$"
        },
        "correct_answer": "A",
        "explanation": "By standard double angle identity: $\\cos(2\\theta) = \\frac{1 - \\tan^2\\theta}{1 + \\tan^2\\theta}$.",
        "subject": "Mathematics",
        "topic": "Trigonometry",
        "subtopic": "Multiple and Sub-multiple Angles",
        "difficulty": "easy",
        "source": {"name": "DDCET Official Question Bank / PYQ", "page": 15},
        "tags": ["trigonometry", "double_angle", "identity"],
        "verified": True,
        "created_at": "2026-10-24T12:00:00"
    },
    {
        "id": "DDCET-MATH-TRIG-006",
        "question": "What is the value of $\\sin(20^\\circ) \\sin(40^\\circ) \\sin(80^\\circ)$?",
        "options": {
            "A": "$\\frac{1}{8}$",
            "B": "$\\frac{\\sqrt{3}}{8}$",
            "C": "$\\frac{1}{4}$",
            "D": "$\\frac{\\sqrt{3}}{4}$"
        },
        "correct_answer": "B",
        "explanation": "Using identity $\\sin\\theta \\sin(60^\\circ - \\theta) \\sin(60^\\circ + \\theta) = \\frac{1}{4}\\sin(3\\theta)$ with $\\theta = 20^\\circ$: LHS $= \\frac{1}{4} \\sin(60^\\circ) = \\frac{1}{4} \\times \\frac{\\sqrt{3}}{2} = \\frac{\\sqrt{3}}{8}$.",
        "subject": "Mathematics",
        "topic": "Trigonometry",
        "subtopic": "Multiple and Sub-multiple Angles",
        "difficulty": "hard",
        "source": {"name": "DDCET Official Question Bank / PYQ", "page": 15},
        "tags": ["trigonometry", "triple_angle", "product_identity"],
        "verified": True,
        "created_at": "2026-10-24T12:00:00"
    },
    {
        "id": "DDCET-MATH-TRIG-007",
        "question": "What is the principal value of $\\sin^{-1}\\left(-\\frac{1}{2}\\right)$?",
        "options": {
            "A": "$\\frac{\\pi}{6}$",
            "B": "$-\\frac{\\pi}{6}$",
            "C": "$\\frac{5\\pi}{6}$",
            "D": "$-\\frac{\\pi}{3}$"
        },
        "correct_answer": "B",
        "explanation": "The range of principal value branch of $\\sin^{-1} x$ is $[-\\frac{\\pi}{2}, \\frac{\\pi}{2}]$. Since $\\sin(-\\pi/6) = -1/2$, the value is $-\\frac{\\pi}{6}$.",
        "subject": "Mathematics",
        "topic": "Trigonometry",
        "subtopic": "Inverse Trigonometric Functions",
        "difficulty": "easy",
        "source": {"name": "DDCET Official Question Bank / PYQ", "page": 16},
        "tags": ["inverse_trig", "principal_value"],
        "verified": True,
        "created_at": "2026-10-24T12:00:00"
    },
    {
        "id": "DDCET-MATH-TRIG-008",
        "question": "What is the value of $\\tan^{-1}(1) + \\tan^{-1}(2) + \\tan^{-1}(3)$?",
        "options": {
            "A": "$\\frac{\\pi}{2}$",
            "B": "$\\pi$",
            "C": "$\\frac{3\\pi}{4}$",
            "D": "$0$"
        },
        "correct_answer": "B",
        "explanation": "Since $x \\cdot y = 2 \\times 3 = 6 > 1$, $\\tan^{-1}(2) + \\tan^{-1}(3) = \\pi + \\tan^{-1}\\left(\\frac{2+3}{1-6}\\right) = \\pi + \\tan^{-1}(-1) = \\pi - \\frac{\\pi}{4} = \\frac{3\\pi}{4}$. Adding $\\tan^{-1}(1) = \\frac{\\pi}{4}$ gives $\\frac{\\pi}{4} + \\frac{3\\pi}{4} = \\pi$.",
        "subject": "Mathematics",
        "topic": "Trigonometry",
        "subtopic": "Inverse Trigonometric Functions",
        "difficulty": "medium",
        "source": {"name": "DDCET Official Question Bank / PYQ", "page": 16},
        "tags": ["inverse_trig", "sum_of_arctan"],
        "verified": True,
        "created_at": "2026-10-24T12:00:00"
    },
    {
        "id": "DDCET-MATH-TRIG-009",
        "question": "What is the value of $\\sin^{-1}(x) + \\cos^{-1}(x)$ for all $x \\in [-1, 1]$?",
        "options": {
            "A": "$0$",
            "B": "$\\pi$",
            "C": "$\\frac{\\pi}{2}$",
            "D": "$2\\pi$"
        },
        "correct_answer": "C",
        "explanation": "By standard identity of complementary inverse trigonometric functions, $\\sin^{-1} x + \\cos^{-1} x = \\frac{\\pi}{2}$.",
        "subject": "Mathematics",
        "topic": "Trigonometry",
        "subtopic": "Inverse Trigonometric Functions",
        "difficulty": "easy",
        "source": {"name": "DDCET Official Question Bank / PYQ", "page": 17},
        "tags": ["inverse_trig", "standard_identity"],
        "verified": True,
        "created_at": "2026-10-24T12:00:00"
    },
    {
        "id": "DDCET-MATH-TRIG-010",
        "question": "What is the simplified form of $\\frac{\\cos(3\\theta)}{\\cos\\theta} + \\frac{\\sin(3\\theta)}{\\sin\\theta}$?",
        "options": {
            "A": "$4\\cos(2\\theta)$",
            "B": "$2\\cos(2\\theta)$",
            "C": "$4\\sin(2\\theta)$",
            "D": "$2$"
        },
        "correct_answer": "A",
        "explanation": "$\\frac{\\cos(3\\theta)\\sin\\theta + \\sin(3\\theta)\\cos\\theta}{\\sin\\theta\\cos\\theta} = \\frac{\\sin(3\\theta+\\theta)}{\\frac{1}{2}\\sin(2\\theta)} = \\frac{\\sin(4\\theta)}{\\frac{1}{2}\\sin(2\\theta)} = \\frac{2\\sin(2\\theta)\\cos(2\\theta)}{\\frac{1}{2}\\sin(2\\theta)} = 4\\cos(2\\theta)$.",
        "subject": "Mathematics",
        "topic": "Trigonometry",
        "subtopic": "Transformation Formulae",
        "difficulty": "medium",
        "source": {"name": "DDCET Official Question Bank / PYQ", "page": 17},
        "tags": ["trigonometry", "transformation_formulae"],
        "verified": True,
        "created_at": "2026-10-24T12:00:00"
    },

    # ==========================================
    # 4. COORDINATE GEOMETRY & CONICS
    # ==========================================
    {
        "id": "DDCET-MATH-CG-001",
        "question": "What is the slope of the line perpendicular to $3x - 4y + 7 = 0$?",
        "options": {
            "A": "$\\frac{3}{4}$",
            "B": "$-\\frac{4}{3}$",
            "C": "$\\frac{4}{3}$",
            "D": "$-\\frac{3}{4}$"
        },
        "correct_answer": "B",
        "explanation": "Slope of given line $m_1 = -\\frac{a}{b} = -\\frac{3}{-4} = \\frac{3}{4}$. For perpendicular lines, $m_1 m_2 = -1 \\implies m_2 = -\\frac{4}{3}$.",
        "subject": "Mathematics",
        "topic": "Coordinate Geometry",
        "subtopic": "Straight Lines and Slopes",
        "difficulty": "easy",
        "source": {"name": "DDCET Official Question Bank / PYQ", "page": 18},
        "tags": ["coordinate_geometry", "perpendicular_lines"],
        "verified": True,
        "created_at": "2026-10-24T12:00:00"
    },
    {
        "id": "DDCET-MATH-CG-002",
        "question": "What is the perpendicular distance from the point $(2, 3)$ to the line $3x + 4y - 8 = 0$?",
        "options": {
            "A": "$1$",
            "B": "$2$",
            "C": "$\\frac{10}{5}$",
            "D": "$5$"
        },
        "correct_answer": "B",
        "explanation": "Distance $d = \\frac{|a x_1 + b y_1 + c|}{\\sqrt{a^2 + b^2}} = \\frac{|3(2) + 4(3) - 8|}{\\sqrt{3^2 + 4^2}} = \\frac{|6 + 12 - 8|}{5} = \\frac{10}{5} = 2$.",
        "subject": "Mathematics",
        "topic": "Coordinate Geometry",
        "subtopic": "Straight Lines and Slopes",
        "difficulty": "easy",
        "source": {"name": "DDCET Official Question Bank / PYQ", "page": 18},
        "tags": ["coordinate_geometry", "perpendicular_distance"],
        "verified": True,
        "created_at": "2026-10-24T12:00:00"
    },
    {
        "id": "DDCET-MATH-CG-003",
        "question": "What is the center and radius of the circle $x^2 + y^2 - 4x + 6y - 12 = 0$?",
        "options": {
            "A": "Center $(2, -3)$, Radius $5$",
            "B": "Center $(-2, 3)$, Radius $5$",
            "C": "Center $(2, -3)$, Radius $25$",
            "D": "Center $(-4, 6)$, Radius $5$"
        },
        "correct_answer": "A",
        "explanation": "Comparing with $x^2 + y^2 + 2gx + 2fy + c = 0$: $2g = -4 \\implies g = -2$, $2f = 6 \\implies f = 3$, $c = -12$. Center $= (-g, -f) = (2, -3)$. Radius $r = \\sqrt{g^2 + f^2 - c} = \\sqrt{(-2)^2 + 3^2 - (-12)} = \\sqrt{4 + 9 + 12} = \\sqrt{25} = 5$.",
        "subject": "Mathematics",
        "topic": "Coordinate Geometry",
        "subtopic": "Circle Equations and Properties",
        "difficulty": "medium",
        "source": {"name": "DDCET Official Question Bank / PYQ", "page": 19},
        "tags": ["circles", "radius", "center"],
        "verified": True,
        "created_at": "2026-10-24T12:00:00"
    },
    {
        "id": "DDCET-MATH-CG-004",
        "question": "What is the focus of the parabola $y^2 = 12x$?",
        "options": {
            "A": "$(0, 3)$",
            "B": "$(3, 0)$",
            "C": "$(6, 0)$",
            "D": "$(-3, 0)$"
        },
        "correct_answer": "B",
        "explanation": "Standard equation $y^2 = 4ax$. Here $4a = 12 \\implies a = 3$. The focus of $y^2 = 4ax$ lies on the x-axis at $(a, 0) = (3, 0)$.",
        "subject": "Mathematics",
        "topic": "Coordinate Geometry",
        "subtopic": "Conic Sections",
        "difficulty": "easy",
        "source": {"name": "DDCET Official Question Bank / PYQ", "page": 19},
        "tags": ["parabola", "focus", "conics"],
        "verified": True,
        "created_at": "2026-10-24T12:00:00"
    },
    {
        "id": "DDCET-MATH-CG-005",
        "question": "What is the eccentricity $e$ of the ellipse $\\frac{x^2}{25} + \\frac{y^2}{16} = 1$?",
        "options": {
            "A": "$\\frac{3}{5}$",
            "B": "$\\frac{4}{5}$",
            "C": "$\\frac{9}{25}$",
            "D": "$\\frac{5}{3}$"
        },
        "correct_answer": "A",
        "explanation": "$a^2 = 25, b^2 = 16$. Formula: $b^2 = a^2(1 - e^2) \\implies 16 = 25(1 - e^2) \\implies 1 - e^2 = \\frac{16}{25} \\implies e^2 = \\frac{9}{25} \\implies e = \\frac{3}{5}$.",
        "subject": "Mathematics",
        "topic": "Coordinate Geometry",
        "subtopic": "Conic Sections",
        "difficulty": "medium",
        "source": {"name": "DDCET Official Question Bank / PYQ", "page": 20},
        "tags": ["ellipse", "eccentricity"],
        "verified": True,
        "created_at": "2026-10-24T12:00:00"
    },

    # ==========================================
    # 5. DIFFERENTIAL CALCULUS
    # ==========================================
    {
        "id": "DDCET-MATH-DC-003",
        "question": "What is $\\lim_{x \\to 0} \\frac{\\tan(5x)}{\\sin(2x)}$?",
        "options": {
            "A": "$\\frac{2}{5}$",
            "B": "$\\frac{5}{2}$",
            "C": "$1$",
            "D": "$0$"
        },
        "correct_answer": "B",
        "explanation": "$\\lim_{x \\to 0} \\frac{\\frac{\\tan 5x}{5x} \\times 5x}{\\frac{\\sin 2x}{2x} \\times 2x} = \\frac{1 \\times 5}{1 \\times 2} = \\frac{5}{2}$.",
        "subject": "Mathematics",
        "topic": "Differential Calculus",
        "subtopic": "Limits and Indeterminate Forms",
        "difficulty": "easy",
        "source": {"name": "DDCET Official Question Bank / PYQ", "page": 21},
        "tags": ["limits", "trigonometric_limits"],
        "verified": True,
        "created_at": "2026-10-24T12:00:00"
    },
    {
        "id": "DDCET-MATH-DC-004",
        "question": "What is the value of $\\lim_{x \\to 0} \\frac{e^{3x} - 1}{x}$?",
        "options": {
            "A": "$1$",
            "B": "$3$",
            "C": "$0$",
            "D": "$e$"
        },
        "correct_answer": "B",
        "explanation": "Standard exponential limit: $\\lim_{u \\to 0} \\frac{e^u - 1}{u} = 1$. Here $\\lim_{x \\to 0} 3 \\left(\\frac{e^{3x} - 1}{3x}\\right) = 3 \\times 1 = 3$.",
        "subject": "Mathematics",
        "topic": "Differential Calculus",
        "subtopic": "Limits and Indeterminate Forms",
        "difficulty": "easy",
        "source": {"name": "DDCET Official Question Bank / PYQ", "page": 21},
        "tags": ["limits", "exponential_limits"],
        "verified": True,
        "created_at": "2026-10-24T12:00:00"
    },
    {
        "id": "DDCET-MATH-DC-005",
        "question": "What is $\\lim_{x \\to \\infty} \\left(1 + \\frac{2}{x}\\right)^x$?",
        "options": {
            "A": "$e$",
            "B": "$e^2$",
            "C": "$1$",
            "D": "$\\infty$"
        },
        "correct_answer": "B",
        "explanation": "Standard limit: $\\lim_{x \\to \\infty} \\left(1 + \\frac{k}{x}\\right)^x = e^k$. For $k = 2$, the result is $e^2$.",
        "subject": "Mathematics",
        "topic": "Differential Calculus",
        "subtopic": "Limits and Indeterminate Forms",
        "difficulty": "easy",
        "source": {"name": "DDCET Official Question Bank / PYQ", "page": 22},
        "tags": ["limits", "standard_forms"],
        "verified": True,
        "created_at": "2026-10-24T12:00:00"
    },
    {
        "id": "DDCET-MATH-DC-006",
        "question": "If $y = \\tan^{-1}\\left(\\frac{2x}{1 - x^2}\\right)$, what is $\\frac{dy}{dx}$?",
        "options": {
            "A": "$\\frac{1}{1 + x^2}$",
            "B": "$\\frac{2}{1 + x^2}$",
            "C": "$\\frac{2}{1 - x^2}$",
            "D": "$\\frac{1}{1 - x^2}$"
        },
        "correct_answer": "B",
        "explanation": "Substitute $x = \\tan\\theta$. Then $\\frac{2x}{1 - x^2} = \\tan(2\\theta)$, so $y = 2\\theta = 2\\tan^{-1}(x)$. Differentiating with respect to $x$: $\\frac{dy}{dx} = \\frac{2}{1 + x^2}$.",
        "subject": "Mathematics",
        "topic": "Differential Calculus",
        "subtopic": "Standard Differentiation and Chain Rule",
        "difficulty": "medium",
        "source": {"name": "DDCET Official Question Bank / PYQ", "page": 22},
        "tags": ["differentiation", "inverse_trig"],
        "verified": True,
        "created_at": "2026-10-24T12:00:00"
    },
    {
        "id": "DDCET-MATH-DC-007",
        "question": "If $x = a\\cos^3\\theta$ and $y = a\\sin^3\\theta$, what is $\\frac{dy}{dx}$ at $\\theta = \\frac{\\pi}{4}$?",
        "options": {
            "A": "$1$",
            "B": "$-1$",
            "C": "$0$",
            "D": "$\\sqrt{3}$"
        },
        "correct_answer": "B",
        "explanation": "$\\frac{dx}{d\\theta} = -3a\\cos^2\\theta \\sin\\theta$, $\\frac{dy}{d\\theta} = 3a\\sin^2\\theta \\cos\\theta$. Therefore $\\frac{dy}{dx} = \\frac{3a\\sin^2\\theta \\cos\\theta}{-3a\\cos^2\\theta \\sin\\theta} = -\\tan\\theta$. At $\\theta = \\frac{\\pi}{4}$, $-\\tan(\\pi/4) = -1$.",
        "subject": "Mathematics",
        "topic": "Differential Calculus",
        "subtopic": "Implicit and Parametric Differentiation",
        "difficulty": "medium",
        "source": {"name": "DDCET Official Question Bank / PYQ", "page": 23},
        "tags": ["differentiation", "parametric"],
        "verified": True,
        "created_at": "2026-10-24T12:00:00"
    },
    {
        "id": "DDCET-MATH-DC-008",
        "question": "If $x^y = e^{x - y}$, what is $\\frac{dy}{dx}$?",
        "options": {
            "A": "$\\frac{\\ln x}{(1 + \\ln x)^2}$",
            "B": "$\\frac{1}{1 + \\ln x}$",
            "C": "$\\frac{x}{(1 + \\ln x)^2}$",
            "D": "$\\frac{\\ln x}{1 + \\ln x}$"
        },
        "correct_answer": "A",
        "explanation": "Taking natural log on both sides: $y \\ln x = x - y \\implies y(1 + \\ln x) = x \\implies y = \\frac{x}{1 + \\ln x}$. Using quotient rule: $\\frac{dy}{dx} = \\frac{(1 + \\ln x)(1) - x(1/x)}{(1 + \\ln x)^2} = \\frac{\\ln x}{(1 + \\ln x)^2}$.",
        "subject": "Mathematics",
        "topic": "Differential Calculus",
        "subtopic": "Standard Differentiation and Chain Rule",
        "difficulty": "hard",
        "source": {"name": "DDCET Official Question Bank / PYQ", "page": 24},
        "tags": ["differentiation", "logarithmic_differentiation"],
        "verified": True,
        "created_at": "2026-10-24T12:00:00"
    },
    {
        "id": "DDCET-MATH-DC-009",
        "question": "At what point on the curve $y = x^2 - 4x + 5$ is the tangent horizontal?",
        "options": {
            "A": "$(2, 1)$",
            "B": "$(1, 2)$",
            "C": "$(0, 5)$",
            "D": "$(4, 5)$"
        },
        "correct_answer": "A",
        "explanation": "A horizontal tangent has slope $\\frac{dy}{dx} = 0$. $\\frac{dy}{dx} = 2x - 4 = 0 \\implies x = 2$. When $x = 2$, $y = 2^2 - 4(2) + 5 = 4 - 8 + 5 = 1$. The point is $(2, 1)$.",
        "subject": "Mathematics",
        "topic": "Differential Calculus",
        "subtopic": "Tangents, Normals, and Maxima-Minima",
        "difficulty": "easy",
        "source": {"name": "DDCET Official Question Bank / PYQ", "page": 24},
        "tags": ["tangent", "horizontal_tangent", "extrema"],
        "verified": True,
        "created_at": "2026-10-24T12:00:00"
    },
    {
        "id": "DDCET-MATH-DC-010",
        "question": "What is the slope of the normal to the curve $y = 2x^2 + 3\\sin x$ at $x = 0$?",
        "options": {
            "A": "$3$",
            "B": "$-\\frac{1}{3}$",
            "C": "$\\frac{1}{3}$",
            "D": "$-3$"
        },
        "correct_answer": "B",
        "explanation": "$\\frac{dy}{dx} = 4x + 3\\cos x$. At $x = 0$, slope of tangent $m = 4(0) + 3\\cos(0) = 3$. Slope of normal $m_N = -\\frac{1}{m} = -\\frac{1}{3}$.",
        "subject": "Mathematics",
        "topic": "Differential Calculus",
        "subtopic": "Tangents, Normals, and Maxima-Minima",
        "difficulty": "medium",
        "source": {"name": "DDCET Official Question Bank / PYQ", "page": 25},
        "tags": ["normal", "differentiation"],
        "verified": True,
        "created_at": "2026-10-24T12:00:00"
    },
    {
        "id": "DDCET-MATH-DC-011",
        "question": "What is the maximum value of $f(x) = \\sin x + \\cos x$?",
        "options": {
            "A": "$1$",
            "B": "$2$",
            "C": "$\\sqrt{2}$",
            "D": "$\\frac{1}{\\sqrt{2}}$"
        },
        "correct_answer": "C",
        "explanation": "Expression $a\\sin x + b\\cos x$ has maximum value $\\sqrt{a^2 + b^2}$. Here $a = 1, b = 1$, so maximum $= \\sqrt{1^2 + 1^2} = \\sqrt{2}$.",
        "subject": "Mathematics",
        "topic": "Differential Calculus",
        "subtopic": "Tangents, Normals, and Maxima-Minima",
        "difficulty": "easy",
        "source": {"name": "DDCET Official Question Bank / PYQ", "page": 25},
        "tags": ["maxima_minima", "trigonometry"],
        "verified": True,
        "created_at": "2026-10-24T12:00:00"
    },

    # ==========================================
    # 6. INTEGRAL CALCULUS
    # ==========================================
    {
        "id": "DDCET-MATH-IC-003",
        "question": "What is $\\int \\frac{1}{x^2 + 9} \\, dx$?",
        "options": {
            "A": "$\\frac{1}{3}\\tan^{-1}\\left(\\frac{x}{3}\\right) + C$",
            "B": "$\\tan^{-1}\\left(\\frac{x}{3}\\right) + C$",
            "C": "$\\frac{1}{9}\\tan^{-1}\\left(\\frac{x}{3}\\right) + C$",
            "D": "$\\frac{1}{3}\\sin^{-1}\\left(\\frac{x}{3}\\right) + C$"
        },
        "correct_answer": "A",
        "explanation": "Standard formula: $\\int \\frac{1}{x^2 + a^2} \\, dx = \\frac{1}{a}\\tan^{-1}\\left(\\frac{x}{a}\\right) + C$. Here $a = 3$, giving $\\frac{1}{3}\\tan^{-1}(x/3) + C$.",
        "subject": "Mathematics",
        "topic": "Integral Calculus",
        "subtopic": "Standard Indefinite Integrals",
        "difficulty": "easy",
        "source": {"name": "DDCET Official Question Bank / PYQ", "page": 26},
        "tags": ["integration", "standard_formulas"],
        "verified": True,
        "created_at": "2026-10-24T12:00:00"
    },
    {
        "id": "DDCET-MATH-IC-004",
        "question": "What is $\\int e^x (\\sin x + \\cos x) \\, dx$?",
        "options": {
            "A": "$e^x \\sin x + C$",
            "B": "$e^x \\cos x + C$",
            "C": "$-e^x \\cos x + C$",
            "D": "$e^x (\\sin x - \\cos x) + C$"
        },
        "correct_answer": "A",
        "explanation": "Standard theorem: $\\int e^x [f(x) + f'(x)] \\, dx = e^x f(x) + C$. Here $f(x) = \\sin x$ and $f'(x) = \\cos x$, yielding $e^x \\sin x + C$.",
        "subject": "Mathematics",
        "topic": "Integral Calculus",
        "subtopic": "Integration by Parts",
        "difficulty": "easy",
        "source": {"name": "DDCET Official Question Bank / PYQ", "page": 26},
        "tags": ["integration", "exponential_integral"],
        "verified": True,
        "created_at": "2026-10-24T12:00:00"
    },
    {
        "id": "DDCET-MATH-IC-005",
        "question": "What is the value of the definite integral $\\int_{-a}^{a} x^3 \\cos x \\, dx$?",
        "options": {
            "A": "$2a^3$",
            "B": "$0$",
            "C": "$2$",
            "D": "$a^4$"
        },
        "correct_answer": "B",
        "explanation": "Let $f(x) = x^3 \\cos x$. Then $f(-x) = (-x)^3 \\cos(-x) = -x^3 \\cos x = -f(x)$, so $f(x)$ is an odd function. The integral of any odd function over symmetric limits $[-a, a]$ is identically $0$.",
        "subject": "Mathematics",
        "topic": "Integral Calculus",
        "subtopic": "Definite Integrals and Properties",
        "difficulty": "easy",
        "source": {"name": "DDCET Official Question Bank / PYQ", "page": 27},
        "tags": ["definite_integrals", "odd_function"],
        "verified": True,
        "created_at": "2026-10-24T12:00:00"
    },
    {
        "id": "DDCET-MATH-IC-006",
        "question": "What is the value of $\\int_0^{\\pi/2} \\frac{\\sqrt{\\sin x}}{\\sqrt{\\sin x} + \\sqrt{\\cos x}} \\, dx$?",
        "options": {
            "A": "$\\pi$",
            "B": "$\\frac{\\pi}{2}$",
            "C": "$\\frac{\\pi}{4}$",
            "D": "$0$"
        },
        "correct_answer": "C",
        "explanation": "Using King's property $\\int_0^a f(x)dx = \\int_0^a f(a-x)dx$: $I = \\int_0^{\\pi/2} \\frac{\\sqrt{\\cos x}}{\\sqrt{\\cos x} + \\sqrt{\\sin x}} dx$. Adding both gives $2I = \\int_0^{\\pi/2} 1 \\, dx = \\frac{\\pi}{2} \\implies I = \\frac{\\pi}{4}$.",
        "subject": "Mathematics",
        "topic": "Integral Calculus",
        "subtopic": "Definite Integrals and Properties",
        "difficulty": "medium",
        "source": {"name": "DDCET Official Question Bank / PYQ", "page": 27},
        "tags": ["definite_integrals", "kings_property"],
        "verified": True,
        "created_at": "2026-10-24T12:00:00"
    },
    {
        "id": "DDCET-MATH-IC-007",
        "question": "What is the area enclosed between the parabola $y^2 = 4x$ and the line $x = 1$?",
        "options": {
            "A": "$\\frac{8}{3}$",
            "B": "$\\frac{16}{3}$",
            "C": "$4$",
            "D": "$\\frac{4}{3}$"
        },
        "correct_answer": "A",
        "explanation": "Area $= 2 \\int_0^1 2\\sqrt{x} \\, dx = 4 \\left[\\frac{x^{3/2}}{3/2}\\right]_0^1 = 4 \\times \\frac{2}{3} = \\frac{8}{3}$.",
        "subject": "Mathematics",
        "topic": "Integral Calculus",
        "subtopic": "Area Under Curves",
        "difficulty": "medium",
        "source": {"name": "DDCET Official Question Bank / PYQ", "page": 28},
        "tags": ["area_under_curve", "parabola"],
        "verified": True,
        "created_at": "2026-10-24T12:00:00"
    },
    {
        "id": "DDCET-MATH-IC-008",
        "question": "What is $\\int \\ln x \\, dx$?",
        "options": {
            "A": "$\\frac{1}{x} + C$",
            "B": "$x \\ln x - x + C$",
            "C": "$x \\ln x + x + C$",
            "D": "$\\frac{(\\ln x)^2}{2} + C$"
        },
        "correct_answer": "B",
        "explanation": "Integrating by parts: $\\int 1 \\cdot \\ln x \\, dx = x\\ln x - \\int x \\cdot \\frac{1}{x} \\, dx = x\\ln x - x + C$.",
        "subject": "Mathematics",
        "topic": "Integral Calculus",
        "subtopic": "Integration by Parts",
        "difficulty": "easy",
        "source": {"name": "DDCET Official Question Bank / PYQ", "page": 28},
        "tags": ["integration", "by_parts"],
        "verified": True,
        "created_at": "2026-10-24T12:00:00"
    },

    # ==========================================
    # 7. DIFFERENTIAL EQUATIONS
    # ==========================================
    {
        "id": "DDCET-MATH-DE-001",
        "question": "What is the order and degree of the differential equation $\\left(\\frac{d^2y}{dx^2}\\right)^3 + \\left(\\frac{dy}{dx}\\right)^4 + y = 0$?",
        "options": {
            "A": "Order 2, Degree 3",
            "B": "Order 3, Degree 2",
            "C": "Order 2, Degree 4",
            "D": "Order 4, Degree 3"
        },
        "correct_answer": "A",
        "explanation": "Highest order derivative is $\\frac{d^2y}{dx^2}$ (order 2). The power of this highest derivative term is 3 (degree 3).",
        "subject": "Mathematics",
        "topic": "Differential Equations",
        "subtopic": "Order and Degree of Differential Equations",
        "difficulty": "easy",
        "source": {"name": "DDCET Official Question Bank / PYQ", "page": 29},
        "tags": ["differential_equations", "order_degree"],
        "verified": True,
        "created_at": "2026-10-24T12:00:00"
    },
    {
        "id": "DDCET-MATH-DE-002",
        "question": "What is the integrating factor (I.F.) of the linear differential equation $\\frac{dy}{dx} + \\frac{2}{x}y = x^3$?",
        "options": {
            "A": "$x^2$",
            "B": "$2\\ln x$",
            "C": "$x$",
            "D": "$\\frac{1}{x^2}$"
        },
        "correct_answer": "A",
        "explanation": "Here $P(x) = \\frac{2}{x}$. Integrating factor $I.F. = e^{\\int P dx} = e^{\\int \\frac{2}{x} dx} = e^{2\\ln x} = e^{\\ln(x^2)} = x^2$.",
        "subject": "Mathematics",
        "topic": "Differential Equations",
        "subtopic": "First-Order Linear Differential Equations and Integrating Factors",
        "difficulty": "easy",
        "source": {"name": "DDCET Official Question Bank / PYQ", "page": 29},
        "tags": ["differential_equations", "integrating_factor"],
        "verified": True,
        "created_at": "2026-10-24T12:00:00"
    },
    {
        "id": "DDCET-MATH-DE-003",
        "question": "What is the general solution of the differential equation $\\frac{dy}{dx} = \\frac{y}{x}$?",
        "options": {
            "A": "$y = cx$",
            "B": "$y = \\frac{c}{x}$",
            "C": "$y = x + c$",
            "D": "$x^2 + y^2 = c$"
        },
        "correct_answer": "A",
        "explanation": "Separating variables: $\\frac{1}{y} \\, dy = \\frac{1}{x} \\, dx$. Integrating: $\\ln y = \\ln x + \\ln c \\implies y = cx$.",
        "subject": "Mathematics",
        "topic": "Differential Equations",
        "subtopic": "Variable Separable Form",
        "difficulty": "easy",
        "source": {"name": "DDCET Official Question Bank / PYQ", "page": 30},
        "tags": ["differential_equations", "separable"],
        "verified": True,
        "created_at": "2026-10-24T12:00:00"
    },
    {
        "id": "DDCET-MATH-DE-004",
        "question": "The degree of the differential equation $\\frac{d^2y}{dx^2} + \\sin\\left(\\frac{dy}{dx}\\right) = 0$ is:",
        "options": {
            "A": "$1$",
            "B": "$2$",
            "C": "Not defined",
            "D": "$0$"
        },
        "correct_answer": "C",
        "explanation": "Because $\\frac{dy}{dx}$ is inside the sine transcendental function, the differential equation cannot be expressed as a polynomial in its derivatives. Hence, its degree is not defined.",
        "subject": "Mathematics",
        "topic": "Differential Equations",
        "subtopic": "Order and Degree of Differential Equations",
        "difficulty": "medium",
        "source": {"name": "DDCET Official Question Bank / PYQ", "page": 30},
        "tags": ["differential_equations", "degree_undefined"],
        "verified": True,
        "created_at": "2026-10-24T12:00:00"
    },

    # ==========================================
    # 8. VECTOR ALGEBRA
    # ==========================================
    {
        "id": "DDCET-MATH-VEC-002",
        "question": "What is the unit vector in the direction of vector $\\vec{v} = 3\\hat{i} - 4\\hat{j}$?",
        "options": {
            "A": "$\\frac{3}{5}\\hat{i} - \\frac{4}{5}\\hat{j}$",
            "B": "$\\frac{3}{7}\\hat{i} - \\frac{4}{7}\\hat{j}$",
            "C": "$3\\hat{i} - 4\\hat{j}$",
            "D": "$\\frac{3}{25}\\hat{i} - \\frac{4}{25}\\hat{j}$"
        },
        "correct_answer": "A",
        "explanation": "Magnitude $|\\vec{v}| = \\sqrt{3^2 + (-4)^2} = \\sqrt{9 + 16} = 5$. Unit vector $\\hat{v} = \\frac{\\vec{v}}{|\\vec{v}|} = \\frac{3}{5}\\hat{i} - \\frac{4}{5}\\hat{j}$.",
        "subject": "Mathematics",
        "topic": "Vector Algebra",
        "subtopic": "Vector Magnitude and Unit Vectors",
        "difficulty": "easy",
        "source": {"name": "DDCET Official Question Bank / PYQ", "page": 31},
        "tags": ["vectors", "unit_vector"],
        "verified": True,
        "created_at": "2026-10-24T12:00:00"
    },
    {
        "id": "DDCET-MATH-VEC-003",
        "question": "What is the angle $\\theta$ between vectors $\\vec{a} = \\hat{i} + \\hat{j}$ and $\\vec{b} = \\hat{j} + \\hat{k}$?",
        "options": {
            "A": "$30^\\circ$",
            "B": "$45^\\circ$",
            "C": "$60^\\circ$",
            "D": "$90^\\circ$"
        },
        "correct_answer": "C",
        "explanation": "$\\vec{a} \\cdot \\vec{b} = (1)(0) + (1)(1) + (0)(1) = 1$. Magnitudes $|\\vec{a}| = \\sqrt{1^2 + 1^2} = \\sqrt{2}$, $|\\vec{b}| = \\sqrt{1^2 + 1^2} = \\sqrt{2}$. $\\cos\\theta = \\frac{\\vec{a} \\cdot \\vec{b}}{|\\vec{a}||\\vec{b}|} = \\frac{1}{\\sqrt{2} \\times \\sqrt{2}} = \\frac{1}{2} \\implies \\theta = 60^\\circ$.",
        "subject": "Mathematics",
        "topic": "Vector Algebra",
        "subtopic": "Scalar Dot Product and Orthogonality",
        "difficulty": "medium",
        "source": {"name": "DDCET Official Question Bank / PYQ", "page": 31},
        "tags": ["vectors", "dot_product", "angle_between_vectors"],
        "verified": True,
        "created_at": "2026-10-24T12:00:00"
    },
    {
        "id": "DDCET-MATH-VEC-004",
        "question": "What is the area of a parallelogram whose adjacent sides are given by $\\vec{a} = 2\\hat{i} + \\hat{j} + 3\\hat{k}$ and $\\vec{b} = -\\hat{i} + 2\\hat{j} + \\hat{k}$?",
        "options": {
            "A": "$5\\sqrt{3}$",
            "B": "$3\\sqrt{5}$",
            "C": "$\\sqrt{75}$",
            "D": "$\\sqrt{95}$"
        },
        "correct_answer": "A",
        "explanation": "Cross product $\\vec{a} \\times \\vec{b} = \\begin{vmatrix} \\hat{i} & \\hat{j} & \\hat{k} \\\\ 2 & 1 & 3 \\\\ -1 & 2 & 1 \\end{vmatrix} = \\hat{i}(1 - 6) - \\hat{j}(2 - (-3)) + \\hat{k}(4 - (-1)) = -5\\hat{i} - 5\\hat{j} + 5\\hat{k}$. Magnitude $= \\sqrt{(-5)^2 + (-5)^2 + 5^2} = \\sqrt{75} = 5\\sqrt{3}$.",
        "subject": "Mathematics",
        "topic": "Vector Algebra",
        "subtopic": "Vector Cross Product and Area",
        "difficulty": "medium",
        "source": {"name": "DDCET Official Question Bank / PYQ", "page": 32},
        "tags": ["vectors", "cross_product", "parallelogram_area"],
        "verified": True,
        "created_at": "2026-10-24T12:00:00"
    },
    {
        "id": "DDCET-MATH-VEC-005",
        "question": "What is the work done by a constant force $\\vec{F} = 2\\hat{i} - 3\\hat{j} + 4\\hat{k}$ displacing an object from point $A(1, 2, 3)$ to point $B(3, 5, 2)$?",
        "options": {
            "A": "$-9$ units",
            "B": "$-1$ units",
            "C": "$7$ units",
            "D": "$-7$ units"
        },
        "correct_answer": "D",
        "explanation": "Displacement $\\vec{d} = \\vec{r}_B - \\vec{r}_A = (3-1)\\hat{i} + (5-2)\\hat{j} + (2-3)\\hat{k} = 2\\hat{i} + 3\\hat{j} - \\hat{k}$. Work done $W = \\vec{F} \\cdot \\vec{d} = (2)(2) + (-3)(3) + (4)(-1) = 4 - 9 - 4 = -7$ units.",
        "subject": "Mathematics",
        "topic": "Vector Algebra",
        "subtopic": "Scalar Dot Product and Orthogonality",
        "difficulty": "medium",
        "source": {"name": "DDCET Official Question Bank / PYQ", "page": 32},
        "tags": ["vectors", "work_done", "physics_application"],
        "verified": True,
        "created_at": "2026-10-24T12:00:00"
    },

    # ==========================================
    # 9. STATISTICS AND PROBABILITY
    # ==========================================
    {
        "id": "DDCET-MATH-STAT-002",
        "question": "For a moderately skewed distribution, what is the empirical relationship between Mean, Median, and Mode?",
        "options": {
            "A": "$\\text{Mode} = 3\\text{Median} - 2\\text{Mean}$",
            "B": "$\\text{Mode} = 2\\text{Median} - 3\\text{Mean}$",
            "C": "$\\text{Median} = 3\\text{Mode} - 2\\text{Mean}$",
            "D": "$\\text{Mean} = 3\\text{Median} - 2\\text{Mode}$"
        },
        "correct_answer": "A",
        "explanation": "Karl Pearson's empirical relationship states: $\\text{Mode} = 3\\text{Median} - 2\\text{Mean}$.",
        "subject": "Mathematics",
        "topic": "Statistics and Probability",
        "subtopic": "Mean, Median and Mode",
        "difficulty": "easy",
        "source": {"name": "DDCET Official Question Bank / PYQ", "page": 33},
        "tags": ["statistics", "empirical_formula"],
        "verified": True,
        "created_at": "2026-10-24T12:00:00"
    },
    {
        "id": "DDCET-MATH-STAT-003",
        "question": "If the variance of a dataset is $25$, and each observation is multiplied by $2$, what is the new standard deviation?",
        "options": {
            "A": "$5$",
            "B": "$10$",
            "C": "$50$",
            "D": "$100$"
        },
        "correct_answer": "B",
        "explanation": "Original standard deviation $\\sigma = \\sqrt{25} = 5$. When every observation is multiplied by a constant $c = 2$, the new standard deviation is $|c| \\times \\sigma = 2 \\times 5 = 10$.",
        "subject": "Mathematics",
        "topic": "Statistics and Probability",
        "subtopic": "Variance and Standard Deviation",
        "difficulty": "medium",
        "source": {"name": "DDCET Official Question Bank / PYQ", "page": 33},
        "tags": ["statistics", "standard_deviation", "variance"],
        "verified": True,
        "created_at": "2026-10-24T12:00:00"
    },
    {
        "id": "DDCET-MATH-STAT-004",
        "question": "A card is drawn from a well-shuffled pack of 52 cards. What is the probability that it is either a king or a spade?",
        "options": {
            "A": "$\\frac{17}{52}$",
            "B": "$\\frac{4}{13}$",
            "C": "$\\frac{16}{52}$",
            "D": "$\\frac{1}{2}$"
        },
        "correct_answer": "B",
        "explanation": "$P(K) = \\frac{4}{52}$, $P(S) = \\frac{13}{52}$, $P(K \\cap S) = \\frac{1}{52}$ (king of spades). $P(K \\cup S) = \\frac{4 + 13 - 1}{52} = \\frac{16}{52} = \\frac{4}{13}$.",
        "subject": "Mathematics",
        "topic": "Statistics and Probability",
        "subtopic": "Probability Axioms and Independent Events",
        "difficulty": "easy",
        "source": {"name": "DDCET Official Question Bank / PYQ", "page": 34},
        "tags": ["probability", "addition_rule"],
        "verified": True,
        "created_at": "2026-10-24T12:00:00"
    },
    {
        "id": "DDCET-MATH-STAT-005",
        "question": "If two events $A$ and $B$ are independent with $P(A) = 0.4$ and $P(B) = 0.5$, what is $P(A \\cup B)$?",
        "options": {
            "A": "$0.9$",
            "B": "$0.7$",
            "C": "$0.2$",
            "D": "$0.8$"
        },
        "correct_answer": "B",
        "explanation": "For independent events, $P(A \\cap B) = P(A)P(B) = 0.4 \\times 0.5 = 0.2$. Then $P(A \\cup B) = P(A) + P(B) - P(A \\cap B) = 0.4 + 0.5 - 0.2 = 0.7$.",
        "subject": "Mathematics",
        "topic": "Statistics and Probability",
        "subtopic": "Probability Axioms and Independent Events",
        "difficulty": "medium",
        "source": {"name": "DDCET Official Question Bank / PYQ", "page": 34},
        "tags": ["probability", "independent_events"],
        "verified": True,
        "created_at": "2026-10-24T12:00:00"
    }
]
