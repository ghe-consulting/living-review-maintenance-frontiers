# Propositions and proofs

## Proposition 1 - Average stale probability
If the time to material conclusion change after a refresh is exponential with rate \(\mu\), and downstream decision opportunities are independent of age within an update cycle of length \(t\), the average probability that a decision encounters a stale conclusion is
\[
\bar p_\mu(t)=1-\frac{1-e^{-\mu t}}{\mu t}.
\]

**Proof.** At review age \(u\), stale probability is \(1-e^{-\mu u}\). Averaging over \(u\in[0,t]\) gives the expression. \(\square\)

## Proposition 2 - Unique finite scheduled optimum
Let \(j(x)=\rho/x+g(x)\) for \(x>0\). A unique finite minimizer exists iff \(0<\rho<1\).

**Proof.** Differentiation yields
\[
j'(x)=\frac{h(x)-\rho}{x^2},\qquad h(x)=1-(1+x)e^{-x}.
\]
Now \(h(0)=0\), \(\lim_{x\to\infty}h(x)=1\), and \(h'(x)=xe^{-x}>0\). Hence exactly one root exists for \(0<\rho<1\), and the sign of \(j'\) changes from negative to positive there. For \(\rho\ge1\), \(h(x)-\rho<0\) at every finite \(x\), so no finite minimizer exists and \(j(x)\downarrow1\). At \(\rho=0\), the boundary infimum occurs at \(x\downarrow0\). \(\square\)

## Proposition 3 - Lambert-W branch
For \(0<\rho<1\),
\[
x^*=-1-W_{-1}\left(-\frac{1-\rho}{e}\right).
\]

**Proof.** The FOC is \((1+x)e^{-x}=1-\rho\). Put \(y=-(1+x)\). Then \(ye^y=-(1-\rho)/e\), whose argument lies in \((-1/e,0)\). The principal branch \(W_0\in(-1,0)\) implies \(-1-W_0\in(-1,0)\), which is inadmissible for \(x>0\). The lower branch \(W_{-1}\le-1\) gives the unique nonnegative physical solution, strictly positive for \(\rho>0\). \(\square\)

## Proposition 4 - Exact minimum identity
At the finite optimum,
\[
j(x^*)=1-e^{-x^*}.
\]

**Proof.** The FOC gives \(\rho=1-(1+x^*)e^{-x^*}\). Substitution into \(\rho/x^*+1-(1-e^{-x^*})/x^*\) cancels all ratio terms and leaves \(1-e^{-x^*}\). \(\square\)

## Proposition 5 - Living-dominance rule
With \(b=\phi+\eta+\Delta c\), living maintenance strictly dominates optimized scheduled updating iff
\[
b+g(d)<m(\rho),\qquad m(\rho)=1-e^{-x^*(\rho)}.
\]

**Proof.** Subtract the common \(c_S\) from both normalized strategy burdens and use Proposition 4. \(\square\)

## Proposition 6 - Portfolio and attribution frontiers
Let \(B=m(\rho)-g(d)-\eta-\Delta c\). If \(B>0\), living maintenance dominates iff
\[
\frac{\alpha F}{nQ}<B.
\]
Thus the continuous break-even portfolio size is \(n_{BE}=\alpha F/(QB)\), and, for \(F>0\), the attribution frontier is \(\alpha_{BE}=nQB/F\). If \(B\le0\), no finite portfolio scaling can overcome the non-shared living burden. \(\square\)

## Proposition 7 - Exact positive cadence frontier
If \(z=m(\rho)-\phi-\eta-\Delta c\in(0,1)\), the unique positive solution of \(g(d)=z\) is
\[
d_{BE}=\frac1a+W_0\left(-\frac{e^{-1/a}}a\right),\qquad a=1-z.
\]

**Proof.** For \(d>0\), \(g(d)=z\) is equivalent to \(e^{-d}=1-ad\). Let \(y=1-ad\). Then \((-y/a)e^{-y/a}=-e^{-1/a}/a\). The \(W_{-1}\) branch yields \(y=1\), hence the algebraic boundary root \(d=0\); the principal branch gives the unique positive root. Strict monotonicity follows from \(g'(d)=h(d)/d^2>0\). \(\square\)

## Proposition 8 - Dimensionless topic/reset frontier
If \(c=g(d)+\phi+\eta+\Delta c\in(0,1)\), the unique break-even \(\rho\) is
\[
\rho_{BE}=c+(1-c)\log(1-c).
\]

**Proof.** Break-even requires \(m(\rho)=c\). Since \(m=1-e^{-x}\), \(x=-\log(1-c)\). Substituting into \(h(x)=1-(1+x)e^{-x}\) yields the result. Since \(m'(\rho)>0\), living dominates for \(\rho>\rho_{BE}\). \(\square\)

## Proposition 9 - Square-root approximation direction
For every \(0<\rho<1\),
\[
\sqrt{2\rho}<x^*(\rho).
\]

**Proof.** Since \(h(x)=\int_0^x u e^{-u}du<\int_0^x udu=x^2/2\) for \(x>0\), \(\rho=h(x^*)<(x^*)^2/2\). \(\square\)

## Proposition 10 - General survival-family optimum
Let \(r(x)\) be differentiable, strictly decreasing, \(r(0)=1\), and define
\[
G_r(x)=1-\frac1x\int_0^x r(u)du.
\]
For \(j_r(x)=\rho/x+G_r(x)\),
\[
j_r'(x)=\frac{H_r(x)-\rho}{x^2},\quad H_r(x)=\int_0^x r(u)du-xr(x),
\]
and \(H_r'(x)=-xr'(x)>0\). Thus a unique finite optimum exists whenever \(\rho\) lies strictly between 0 and the limiting value of \(H_r\). At the optimum,
\[
j_r(x^*)=1-r(x^*).
\]

**Proof.** Differentiate directly. Monotonicity of \(H_r\) gives uniqueness. Substitution of \(\rho=H_r(x^*)\) into \(j_r\) cancels the integral terms and yields \(1-r(x^*)\). \(\square\)

## Corollary - Weibull family
For \(r_k(x)=e^{-x^k}\), \(k>0\), \(\lim_{x\to\infty}H_k(x)=\int_0^\infty e^{-u^k}du=\Gamma(1+1/k)\). Therefore a finite optimum exists iff
\[
0<\rho<\Gamma\left(1+\frac1k\right).
\]
The exponential case is \(k=1\). \(\square\)
