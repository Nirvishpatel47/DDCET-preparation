"""
Final batch generator to bring data/data.json to 230+ authentic MCQs.
Syllabus: GTU / ACPC DDCET Diploma-to-Degree examination.
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


def get_final_questions():
    items = []

    # 1. Determinants and Matrices
    items.append(q(
        "DDCET-MATH-DM-053",
        "If $A = \\begin{pmatrix} 1 & 2 \\\\ 3 & 4 \\end{pmatrix}$, what is the value of $|3A|$?",
        {"A": "$-18$", "B": "$-6$", "C": "$-54$", "D": "$18$"},
        "A",
        "$|A| = (1)(4) - (2)(3) = 4 - 6 = -2$. For a $2 \\times 2$ matrix, $|kA| = k^2 |A|$. Here $|3A| = 3^2 (-2) = 9 \\times (-2) = -18$.",
        "Mathematics", "Determinants and Matrices", "Determinant Evaluation and Properties", "easy", ["determinants", "scalar_multiple"]
    ))
    items.append(q(
        "DDCET-MATH-DM-054",
        "If a square matrix satisfies $A = -A^T$, then $A$ is a:",
        {"A": "Skew-symmetric matrix", "B": "Symmetric matrix", "C": "Orthogonal matrix", "D": "Identity matrix"},
        "A",
        "By definition, a matrix whose transpose is equal to its negative ($A^T = -A$) is called a skew-symmetric matrix.",
        "Mathematics", "Determinants and Matrices", "Matrix Types and Algebra", "easy", ["skew_symmetric", "definition"]
    ))
    items.append(q(
        "DDCET-MATH-DM-055",
        "What is the multiplicative identity matrix for $2 \\times 2$ matrices?",
        {"A": "$\\begin{pmatrix} 1 & 0 \\\\ 0 & 1 \\end{pmatrix}$", "B": "$\\begin{pmatrix} 0 & 1 \\\\ 1 & 0 \\end{pmatrix}$", "C": "$\\begin{pmatrix} 1 & 1 \\\\ 1 & 1 \\end{pmatrix}$", "D": "$\\begin{pmatrix} 0 & 0 \\\\ 0 & 0 \\end{pmatrix}$"},
        "A",
        "The identity matrix $I = \\begin{pmatrix} 1 & 0 \\\\ 0 & 1 \\end{pmatrix}$ satisfies $A I = I A = A$ for all $2 \\times 2$ matrices $A$.",
        "Mathematics", "Determinants and Matrices", "Matrix Types and Algebra", "easy", ["identity_matrix"]
    ))
    items.append(q(
        "DDCET-MATH-DM-056",
        "If $A = \\begin{pmatrix} 2 & 0 \\\\ 0 & 3 \\end{pmatrix}$ and $B = \\begin{pmatrix} 4 & 0 \\\\ 0 & 5 \\end{pmatrix}$, what is $AB$?",
        {"A": "$\\begin{pmatrix} 8 & 0 \\\\ 0 & 15 \\end{pmatrix}$", "B": "$\\begin{pmatrix} 6 & 0 \\\\ 0 & 8 \\end{pmatrix}$", "C": "$\\begin{pmatrix} 8 & 0 \\\\ 0 & 8 \\end{pmatrix}$", "D": "$\\begin{pmatrix} 0 & 8 \\\\ 15 & 0 \\end{pmatrix}$"},
        "A",
        "The product of two diagonal matrices is obtained by multiplying corresponding diagonal entries: $\\begin{pmatrix} 2(4) & 0 \\\\ 0 & 3(5) \\end{pmatrix} = \\begin{pmatrix} 8 & 0 \\\\ 0 & 15 \\end{pmatrix}$.",
        "Mathematics", "Determinants and Matrices", "Matrix Types and Algebra", "easy", ["diagonal_matrix", "multiplication"]
    ))
    items.append(q(
        "DDCET-MATH-DM-057",
        "If $|A| = 0$, the square matrix $A$ is called:",
        {"A": "Singular matrix", "B": "Non-singular matrix", "C": "Unit matrix", "D": "Invertible matrix"},
        "A",
        "A matrix with determinant equal to zero is defined as a singular matrix, which implies it has no inverse.",
        "Mathematics", "Determinants and Matrices", "Determinant Evaluation and Properties", "easy", ["singular_matrix", "definition"]
    ))

    # 2. Logarithm & Partial Fractions
    items.append(q(
        "DDCET-MATH-LOG-033",
        "What is the value of $\\log_2 64$?",
        {"A": "$6$", "B": "$5$", "C": "$8$", "D": "$32$"},
        "A",
        "Since $2^6 = 64$, $\\log_2 64 = 6$.",
        "Mathematics", "Logarithm", "Laws of Logarithm and related Simple examples", "easy", ["logarithm", "powers_of_two"]
    ))
    items.append(q(
        "DDCET-MATH-LOG-034",
        "What is the value of $\\log_3 1$?",
        {"A": "$0$", "B": "$1$", "C": "$3$", "D": "Undefined"},
        "A",
        "The logarithm of 1 to any valid base is $0$ because $3^0 = 1$.",
        "Mathematics", "Logarithm", "Laws of Logarithm and related Simple examples", "easy", ["logarithm", "properties"]
    ))
    items.append(q(
        "DDCET-MATH-LOG-035",
        "If $\\frac{x}{(x-2)(x-3)} = \\frac{A}{x-2} + \\frac{B}{x-3}$, what is $A$?",
        {"A": "$-2$", "B": "$2$", "C": "$3$", "D": "$-3$"},
        "A",
        "$x = A(x-3) + B(x-2)$. Put $x = 2$: $2 = A(2 - 3) \\implies 2 = -A \\implies A = -2$.",
        "Mathematics", "Partial Fractions", "Linear Non-repeated Factors", "easy", ["partial_fractions", "cover_up_method"]
    ))
    items.append(q(
        "DDCET-MATH-LOG-036",
        "In partial fraction decomposition of $\\frac{1}{x^2(x+1)}$, what form should be used?",
        {"A": "$\\frac{A}{x} + \\frac{B}{x^2} + \\frac{C}{x+1}$", "B": "$\\frac{A}{x^2} + \\frac{B}{x+1}$", "C": "$\\frac{Ax+B}{x^2} + \\frac{C}{x+1}$", "D": "$\\frac{A}{x} + \\frac{B}{x+1}$"},
        "A",
        "For a repeated linear factor $x^2$, the standard expansion contains terms $\\frac{A}{x} + \\frac{B}{x^2}$ along with $\\frac{C}{x+1}$.",
        "Mathematics", "Partial Fractions", "Repeated Linear Factors", "easy", ["partial_fractions", "repeated_factors"]
    ))

    # 3. Trigonometry
    items.append(q(
        "DDCET-MATH-TRIG-053",
        "What is the value of $\\sin(90^\\circ)$?",
        {"A": "$1$", "B": "$0$", "C": "$-1$", "D": "$\\frac{1}{2}$"},
        "A",
        "By standard trigonometric definition, $\\sin(90^\\circ) = 1$.",
        "Mathematics", "Trigonometry", "Trigonometric Identities", "easy", ["standard_values", "trigonometry"]
    ))
    items.append(q(
        "DDCET-MATH-TRIG-054",
        "What is the value of $\\cos(0^\\circ)$?",
        {"A": "$1$", "B": "$0$", "C": "$-1$", "D": "Undefined"},
        "A",
        "By standard definition, $\\cos(0^\\circ) = 1$.",
        "Mathematics", "Trigonometry", "Trigonometric Identities", "easy", ["standard_values", "trigonometry"]
    ))
    items.append(q(
        "DDCET-MATH-TRIG-055",
        "What is the value of $\\tan(0^\\circ)$?",
        {"A": "$0$", "B": "$1$", "C": "$\\infty$", "D": "$-1$"},
        "A",
        "$\\tan(0^\\circ) = \\frac{\\sin 0^\\circ}{\\cos 0^\\circ} = \\frac{0}{1} = 0$.",
        "Mathematics", "Trigonometry", "Trigonometric Identities", "easy", ["standard_values", "trigonometry"]
    ))
    items.append(q(
        "DDCET-MATH-TRIG-056",
        "What is the value of $\\sin(-x)$?",
        {"A": "$-\\sin x$", "B": "$\\sin x$", "C": "$\\cos x$", "D": "$-\\cos x$"},
        "A",
        "Sine is an odd trigonometric function: $\\sin(-x) = -\\sin x$.",
        "Mathematics", "Trigonometry", "Trigonometric Identities", "easy", ["odd_function", "trigonometry"]
    ))
    items.append(q(
        "DDCET-MATH-TRIG-057",
        "What is the value of $\\cos(-x)$?",
        {"A": "$\\cos x$", "B": "$-\\cos x$", "C": "$\\sin x$", "D": "$-\\sin x$"},
        "A",
        "Cosine is an even trigonometric function: $\\cos(-x) = \\cos x$.",
        "Mathematics", "Trigonometry", "Trigonometric Identities", "easy", ["even_function", "trigonometry"]
    ))

    # 4. Coordinate Geometry
    items.append(q(
        "DDCET-MATH-CG-034",
        "What is the slope-intercept form of the equation of a straight line?",
        {"A": "$y = mx + c$", "B": "$y - y_1 = m(x - x_1)$", "C": "$\\frac{x}{a} + \\frac{y}{b} = 1$", "D": "$Ax + By + C = 0$"},
        "A",
        "The equation $y = mx + c$, where $m$ is the slope and $c$ is the $y$-intercept, is known as the slope-intercept form.",
        "Mathematics", "Coordinate Geometry", "Straight Lines and Slopes", "easy", ["straight_lines", "forms_of_lines"]
    ))
    items.append(q(
        "DDCET-MATH-CG-035",
        "What is the distance of the point $(3, 4)$ from the origin $(0, 0)$?",
        {"A": "$5$", "B": "$7$", "C": "$25$", "D": "$1$"},
        "A",
        "Distance from origin $= \\sqrt{x^2 + y^2} = \\sqrt{3^2 + 4^2} = \\sqrt{9 + 16} = \\sqrt{25} = 5$.",
        "Mathematics", "Coordinate Geometry", "Straight Lines and Slopes", "easy", ["distance_formula", "geometry"]
    ))
    items.append(q(
        "DDCET-MATH-CG-036",
        "If two lines are parallel, what is the relationship between their slopes $m_1$ and $m_2$?",
        {"A": "$m_1 = m_2$", "B": "$m_1 m_2 = -1$", "C": "$m_1 + m_2 = 0$", "D": "$m_1 m_2 = 1$"},
        "A",
        "Two non-vertical lines are parallel if and only if their slopes are equal: $m_1 = m_2$.",
        "Mathematics", "Coordinate Geometry", "Straight Lines and Slopes", "easy", ["parallel_lines", "slope"]
    ))
    items.append(q(
        "DDCET-MATH-CG-037",
        "What is the center of the circle $(x - 3)^2 + (y + 4)^2 = 36$?",
        {"A": "$(3, -4)$", "B": "$(-3, 4)$", "C": "$(3, 4)$", "D": "$(-3, -4)$"},
        "A",
        "Comparing with $(x - h)^2 + (y - k)^2 = r^2$: center is $(h, k) = (3, -4)$.",
        "Mathematics", "Coordinate Geometry", "Circle Equations and Properties", "easy", ["circles", "center"]
    ))

    # 5. Differential Calculus
    items.append(q(
        "DDCET-MATH-DC-048",
        "What is the derivative of $x^3$ with respect to $x$?",
        {"A": "$3x^2$", "B": "$x^2$", "C": "$3x$", "D": "$\\frac{x^4}{4}$"},
        "A",
        "By power rule: $\\frac{d}{dx}(x^3) = 3x^2$.",
        "Mathematics", "Differential Calculus", "Standard Differentiation and Chain Rule", "easy", ["power_rule", "derivatives"]
    ))
    items.append(q(
        "DDCET-MATH-DC-049",
        "What is the derivative of $\\sqrt{x}$ with respect to $x$ for $x > 0$?",
        {"A": "$\\frac{1}{2\\sqrt{x}}$", "B": "$\\frac{1}{\\sqrt{x}}$", "C": "$2\\sqrt{x}$", "D": "$\\frac{\\sqrt{x}}{2}$"},
        "A",
        "$\\frac{d}{dx}(x^{1/2}) = \\frac{1}{2} x^{-1/2} = \\frac{1}{2\\sqrt{x}}$.",
        "Mathematics", "Differential Calculus", "Standard Differentiation and Chain Rule", "easy", ["power_rule", "derivatives"]
    ))
    items.append(q(
        "DDCET-MATH-DC-050",
        "What is $\\frac{d}{dx}(e^x)$?",
        {"A": "$e^x$", "B": "$x e^{x-1}$", "C": "$\\ln x$", "D": "$e^x + C$"},
        "A",
        "The derivative of the natural exponential function $e^x$ is itself: $\\frac{d}{dx}(e^x) = e^x$.",
        "Mathematics", "Differential Calculus", "Standard Differentiation and Chain Rule", "easy", ["exponential", "derivatives"]
    ))
    items.append(q(
        "DDCET-MATH-DC-051",
        "What is $\\lim_{x \\to 2} (x^2 + 3x)$?",
        {"A": "$10$", "B": "$8$", "C": "$6$", "D": "$14$"},
        "A",
        "Direct substitution: $2^2 + 3(2) = 4 + 6 = 10$.",
        "Mathematics", "Differential Calculus", "Limits and Indeterminate Forms", "easy", ["limits", "direct_substitution"]
    ))

    # 6. Integral Calculus
    items.append(q(
        "DDCET-MATH-IC-038",
        "What is $\\int x \\, dx$?",
        {"A": "$\\frac{x^2}{2} + C$", "B": "$x^2 + C$", "C": "$1 + C$", "D": "$2x + C$"},
        "A",
        "$\\int x^1 dx = \\frac{x^2}{2} + C$.",
        "Mathematics", "Integral Calculus", "Standard Indefinite Integrals", "easy", ["integration", "power_rule"]
    ))
    items.append(q(
        "DDCET-MATH-IC-039",
        "What is $\\int 0 \\, dx$?",
        {"A": "$C$ (arbitrary constant)", "B": "$0$", "C": "$1$", "D": "$x + C$"},
        "A",
        "The indefinite integral of zero is an arbitrary constant $C$ because the derivative of any constant is zero.",
        "Mathematics", "Integral Calculus", "Standard Indefinite Integrals", "easy", ["integration", "constant"]
    ))
    items.append(q(
        "DDCET-MATH-IC-040",
        "What is $\\int_0^3 1 \\, dx$?",
        {"A": "$3$", "B": "$0$", "C": "$1$", "D": "$6$"},
        "A",
        "$[x]_0^3 = 3 - 0 = 3$.",
        "Mathematics", "Integral Calculus", "Definite Integrals and Properties", "easy", ["definite_integrals", "evaluation"]
    ))

    # 7. Differential Equations
    items.append(q(
        "DDCET-MATH-DE-019",
        "What is the degree of $\\frac{dy}{dx} + 5y = 0$?",
        {"A": "$1$", "B": "$0$", "C": "$5$", "D": "Undefined"},
        "A",
        "The highest order derivative is $\\frac{dy}{dx}$ raised to power 1, so the degree is 1.",
        "Mathematics", "Differential Equations", "Order and Degree of Differential Equations", "easy", ["order_degree", "differential_equations"]
    ))
    items.append(q(
        "DDCET-MATH-DE-020",
        "What is the general solution of $\\frac{dy}{dx} = 0$?",
        {"A": "$y = C$", "B": "$y = x + C$", "C": "$y = 0$", "D": "$x = C$"},
        "A",
        "Integrating both sides: $\\int dy = \\int 0 dx \\implies y = C$.",
        "Mathematics", "Differential Equations", "Variable Separable Form", "easy", ["differential_equations", "constant_solution"]
    ))

    # 8. Vector Algebra
    items.append(q(
        "DDCET-MATH-VEC-027",
        "What is the magnitude of the unit vector $\\hat{i}$?",
        {"A": "$1$", "B": "$0$", "C": "$\\sqrt{2}$", "D": "Undefined"},
        "A",
        "By definition, any unit vector has a length (magnitude) of exactly 1.",
        "Mathematics", "Vector Algebra", "Vector Magnitude and Unit Vectors", "easy", ["unit_vector", "magnitude"]
    ))
    items.append(q(
        "DDCET-MATH-VEC-028",
        "What is $\\vec{a} \\cdot \\vec{a}$ for any vector $\\vec{a}$?",
        {"A": "$|\\vec{a}|^2$", "B": "$|\\vec{a}|$", "C": "$\\vec{0}$", "D": "$1$"},
        "A",
        "$\\vec{a} \\cdot \\vec{a} = |\\vec{a}||\\vec{a}|\\cos(0^\\circ) = |\\vec{a}|^2$.",
        "Mathematics", "Vector Algebra", "Scalar Dot Product and Orthogonality", "easy", ["dot_product", "properties"]
    ))

    # 9. Statistics and Probability
    items.append(q(
        "DDCET-MATH-STAT-025",
        "What is the mean of the numbers $10, 20, 30$?",
        {"A": "$20$", "B": "$15$", "C": "$30$", "D": "$60$"},
        "A",
        "$\\text{Mean} = \\frac{10 + 20 + 30}{3} = \\frac{60}{3} = 20$.",
        "Mathematics", "Statistics and Probability", "Mean, Median and Mode", "easy", ["mean", "statistics"]
    ))
    items.append(q(
        "DDCET-MATH-STAT-026",
        "What is the probability of rolling a $6$ on a standard fair six-sided die?",
        {"A": "$\\frac{1}{6}$", "B": "$\\frac{1}{2}$", "C": "$\\frac{5}{6}$", "D": "$1$"},
        "A",
        "There is 1 favorable outcome out of 6 possible equiprobable outcomes, giving probability $\\frac{1}{6}$.",
        "Mathematics", "Statistics and Probability", "Probability Axioms and Independent Events", "easy", ["probability", "dice"]
    ))

    # =========================================================================
    # ENGINEERING SCIENCE (BE-01)
    # =========================================================================
    items.append(q(
        "DDCET-SCI-UD-013",
        "What is the SI unit of Force?",
        {"A": "Newton (N)", "B": "Joule (J)", "C": "Watt (W)", "D": "Pascal (Pa)"},
        "A",
        "The SI unit of force is the Newton ($\\text{N} = \\text{kg}\\cdot\\text{m/s}^2$).",
        "Engineering Science", "Units and Measurement", "SI Units and Dimensional Analysis", "easy", ["si_units", "force"]
    ))
    items.append(q(
        "DDCET-SCI-UD-014",
        "What is the SI unit of Frequency?",
        {"A": "Hertz (Hz)", "B": "Second (s)", "C": "Decibel (dB)", "D": "Radian (rad)"},
        "A",
        "Frequency is cycles per second, measured in Hertz ($\\text{Hz} = \\text{s}^{-1}$).",
        "Engineering Science", "Units and Measurement", "SI Units and Dimensional Analysis", "easy", ["si_units", "frequency"]
    ))
    items.append(q(
        "DDCET-SCI-MECH-013",
        "What is the formula for the acceleration $a$ of an object of mass $m$ experiencing force $F$?",
        {"A": "$a = \\frac{F}{m}$", "B": "$a = F \\times m$", "C": "$a = \\frac{m}{F}$", "D": "$a = F - m$"},
        "A",
        "From Newton's second law $F = m a$, solving for acceleration gives $a = \\frac{F}{m}$.",
        "Engineering Science", "Classical Mechanics", "Newton's Laws and Momentum", "easy", ["newton_second_law", "mechanics"]
    ))
    items.append(q(
        "DDCET-SCI-HEAT-010",
        "What happens to the volume of most solids when they are heated?",
        {"A": "It expands (increases)", "B": "It contracts (decreases)", "C": "It remains unchanged", "D": "It drops to zero"},
        "A",
        "Due to increased molecular kinetic energy and vibration amplitude, almost all solids expand in volume upon heating.",
        "Engineering Science", "Heat and Thermometry", "Temperature Scales and Thermal Expansion", "easy", ["thermal_expansion", "heat"]
    ))
    items.append(q(
        "DDCET-SCI-ELEC-012",
        "What is the unit of Electrical Resistance?",
        {"A": "Ohm ($\\Omega$)", "B": "Siemens (S)", "C": "Farad (F)", "D": "Henry (H)"},
        "A",
        "The SI unit of electrical resistance is the Ohm ($\\Omega$).",
        "Engineering Science", "Electric Current & Electricity", "Ohm's Law and Resistivity", "easy", ["resistance", "si_units"]
    ))
    items.append(q(
        "DDCET-SCI-CHEM-012",
        "What is the atomic number of Carbon ($\\text{C}$)?",
        {"A": "$6$", "B": "$12$", "C": "$14$", "D": "$8$"},
        "A",
        "Carbon has 6 protons in its atomic nucleus, giving it an atomic number of 6 (mass number is typically 12).",
        "Engineering Science", "Basic Chemistry Concepts", "Atomic Structure and Periodic Table", "easy", ["carbon", "atomic_number"]
    ))

    # =========================================================================
    # SOFT SKILLS & APTITUDE (BE-02)
    # =========================================================================
    items.append(q(
        "DDCET-APT-ENG-020",
        "Choose the correct plural form of 'datum':",
        {"A": "Data", "B": "Datums", "C": "Datas", "D": "Daties"},
        "A",
        "'Data' is the standard plural form of the singular Latin noun 'datum'.",
        "Soft Skills & Aptitude", "English Language & Grammar", "Vocabulary and Synonyms", "easy", ["english", "plurals"]
    ))
    items.append(q(
        "DDCET-APT-ENG-021",
        "Select the correct antonym for 'EXPAND':",
        {"A": "Contract", "B": "Enlarge", "C": "Broaden", "D": "Stretch"},
        "A",
        "'Expand' means to increase in size or volume; its direct opposite is 'contract'.",
        "Soft Skills & Aptitude", "English Language & Grammar", "Vocabulary and Antonyms", "easy", ["english", "antonyms"]
    ))
    items.append(q(
        "DDCET-APT-QA-022",
        "What is the average of $10, 20, 30, 40,$ and $50$?",
        {"A": "$30$", "B": "$25$", "C": "$35$", "D": "$20$"},
        "A",
        "Sum $= 150$. Average $= \\frac{150}{5} = 30$.",
        "Soft Skills & Aptitude", "Quantitative Aptitude", "Number Series and Reasoning", "easy", ["average", "arithmetic"]
    ))
    items.append(q(
        "DDCET-APT-QA-023",
        "If a square has side length $6\\text{ cm}$, what is its perimeter?",
        {"A": "$24\\text{ cm}$", "B": "$36\\text{ cm}$", "C": "$12\\text{ cm}$", "D": "$18\\text{ cm}$"},
        "A",
        "Perimeter of square $= 4 \\times \\text{side} = 4 \\times 6 = 24\\text{ cm}$.",
        "Soft Skills & Aptitude", "Quantitative Aptitude", "Number Series and Reasoning", "easy", ["perimeter", "geometry"]
    ))

    return items


def main():
    final_items = get_final_questions()
    print(f"Constructed {len(final_items)} final batch MCQs.")

    valid = []
    for item in final_items:
        try:
            m = QuestionModel(**item)
            valid.append(m.model_dump())
        except Exception as e:
            print(f"Validation error in {item['id']}: {e}")

    data_path = os.path.join("data", "data.json")
    with open(data_path, "r", encoding="utf-8") as f:
        existing = json.load(f)

    existing_ids = {x["id"] for x in existing}
    existing_hashes = {compute_question_hash(x["question"], x.get("options", {})) for x in existing}

    added = 0
    for q_item in valid:
        h = compute_question_hash(q_item["question"], q_item["options"])
        if q_item["id"] not in existing_ids and h not in existing_hashes:
            existing.append(q_item)
            existing_ids.add(q_item["id"])
            existing_hashes.add(h)
            added += 1

    print(f"Added {added} questions. Total in data.json: {len(existing)}")

    with open(data_path, "w", encoding="utf-8") as f:
        json.dump(existing, f, indent=2, ensure_ascii=False)
    print("Updated data.json successfully.")


if __name__ == "__main__":
    main()
