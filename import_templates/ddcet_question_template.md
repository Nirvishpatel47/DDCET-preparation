# Gujarat DDCET Mathematics Question Bank Template (.md)

---
## Question: DDCET-MATH-001
**Subject**: Mathematics
**Topic**: Calculus
**Subtopic**: Derivatives
**Difficulty**: easy
**Verified**: true

What is the derivative of $\sin(2x)$ with respect to $x$?

- (A) $2\cos(2x)$
- (B) $-2\cos(2x)$
- (C) $\cos(2x)$
- (D) $2\sin(2x)$

**Correct Answer**: A
**Explanation**:
Using the chain rule of differentiation:
$$\frac{d}{dx}[\sin(u)] = \cos(u) \cdot \frac{du}{dx}$$
Here $u = 2x$ and $\frac{du}{dx} = 2$.
Therefore, $\frac{d}{dx}[\sin(2x)] = 2\cos(2x)$.

---
## Question: DDCET-MATH-002
**Subject**: Mathematics
**Topic**: Calculus
**Subtopic**: Definite Integrals
**Difficulty**: medium
**Verified**: true

Evaluate the definite integral:
$$\int_0^{\frac{\pi}{2}} \sin^2(x) \, dx$$

- (A) $\frac{\pi}{4}$
- (B) $\frac{\pi}{2}$
- (C) $1$
- (D) $0$

**Correct Answer**: A
**Explanation**:
Using the half-angle identity $\sin^2(x) = \frac{1 - \cos(2x)}{2}$:
$$\int_0^{\frac{\pi}{2}} \frac{1 - \cos(2x)}{2} \, dx = \left[ \frac{x}{2} - \frac{\sin(2x)}{4} \right]_0^{\frac{\pi}{2}} = \frac{\pi}{4}$$

---
## Question: DDCET-MATH-003
**Subject**: Mathematics
**Topic**: Matrices and Determinants
**Subtopic**: Eigenvalues
**Difficulty**: medium
**Verified**: true

If matrix $A$ is given by:
$$A = \begin{pmatrix} 2 & 0 \\ 0 & 5 \end{pmatrix}$$
What are the eigenvalues of $A$?

- (A) $\lambda = 2, 5$
- (B) $\lambda = 0, 7$
- (C) $\lambda = 10, 1$
- (D) $\lambda = -2, -5$

**Correct Answer**: A
**Explanation**:
For any diagonal matrix, the eigenvalues are simply the diagonal entries:
$$\det(A - \lambda I) = (2 - \lambda)(5 - \lambda) = 0 \implies \lambda = 2, 5$$
