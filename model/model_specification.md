# Formal model specification

This document states the mathematical model used by the archived analysis. All numerical design inputs are synthetic mathematical values.

## 1. Scalar objective and units

Let all burdens be measured on a common cardinal objective scale per unit time. Define

\[
Q=DH,
\]

where `D` is decision opportunities per unit time and `H` is expected consequence per decision if the review conclusion is materially stale. `Q` therefore has burden/time units.

For the exponential base model, the time to the first material conclusion change after a completed refresh is exponential with rate \(\mu\). The average probability that the conclusion is stale when decisions occur uniformly in time over a refresh interval \(t\) is

\[
\bar p_\mu(t)=g(\mu t),\qquad
g(z)=1-\frac{1-e^{-z}}{z},\quad g(0)=0.
\]

The dimensional strategy burdens are

\[
K_S(T)=\frac{S}{T}+C_S+Q g(\mu T),
\]

\[
K_L(n,\delta,\alpha)=\frac{\alpha F}{n}+f+C_L+Q g(\mu\delta).
\]

\(\delta\) is the interval between completed decision-relevant living conclusion refreshes, and \(F\) is recurring shared operating burden per unit time.

## 2. Dimensionless form

Define

\[
x=\mu T,\quad d=\mu\delta,\quad
\rho=\frac{S\mu}{Q},\quad
c_S=\frac{C_S}{Q},\quad c_L=\frac{C_L}{Q},
\]

\[
\eta=\frac{f}{Q},\qquad
\phi=\frac{\alpha F}{nQ},\qquad
\Delta c=c_L-c_S.
\]

Normalized burdens are

\[
\kappa_S(x)=c_S+\frac{\rho}{x}+g(x),
\]

\[
\kappa_L=c_S+\phi+\eta+\Delta c+g(d).
\]

Hence only \(\rho,d,\phi,\eta,\Delta c\) determine the living-versus-scheduled decision in the base model.

## 3. Exact scheduled optimum

Let

\[
h(x)=1-(1+x)e^{-x}=\int_0^x u e^{-u}\,du.
\]

Then

\[
\frac{d\kappa_S}{dx}=\frac{h(x)-\rho}{x^2}.
\]

Because \(h(0)=0\), \(h(x)\uparrow 1\), and \(h'(x)=xe^{-x}>0\), a unique finite optimum exists iff \(0<\rho<1\). It is the unique positive solution of

\[
h(x^*)=\rho.
\]

The exact closed form is

\[
\boxed{x^*=-1-W_{-1}\!\left(-\frac{1-\rho}{e}\right)},\qquad 0<\rho<1.
\]

The principal branch \(W_0\) yields a negative \(x\) and is inadmissible; \(W_{-1}\) yields the unique nonnegative physical solution.

The dimensional optimum is \(T^*=x^*/\mu\).

### Boundary cases

- \(\rho=0\): the infimum is at \(x=0\), corresponding to vanishing reset burden.
- \(0<\rho<1\): unique finite optimum.
- \(\rho\ge1\): no finite scheduled optimum; \(\kappa_S\) decreases toward \(c_S+1\) as \(x\to\infty\). This is a **no-finite-periodic-optimum boundary**, not automatically identical to operational retirement.

## 4. Exact minimum scheduled burden

At the optimum, substitute \(\rho=h(x^*)\):

\[
\frac{\rho}{x^*}+g(x^*)=1-e^{-x^*}.
\]

Thus

\[
\boxed{\kappa_S^*(\rho)=c_S+m(\rho)},\qquad
m(\rho)=1-e^{-x^*(\rho)},\quad 0<\rho<1.
\]

Moreover,

\[
\frac{dm}{d\rho}=\frac{1}{x^*}>0,
\qquad
\frac{d^2m}{d\rho^2}=-\frac{e^{x^*}}{(x^*)^3}<0.
\]

So the optimized variable scheduled burden rises monotonically but concavely with \(\rho\).

## 5. Exact living-dominance rule

Define the living-specific non-timeliness burden relative to scheduled throughput:

\[
b=\phi+\eta+\Delta c.
\]

Living maintenance has lower normalized burden than optimally scheduled updating iff

\[
\boxed{b+g(d)<m(\rho)}.
\]

This compact inequality is the primary decision rule.

## 6. Exact break-even frontiers

Let

\[
B=m(\rho)-g(d)-\eta-\Delta c.
\]

### Portfolio frontier
If \(B>0\) and \(\alpha F>0\),

\[
\boxed{n_{BE}=\frac{\alpha F}{QB}},
\]

with living maintenance preferred for \(n>n_{BE}\). For integer portfolios the minimum strictly dominating portfolio is the smallest integer greater than \(n_{BE}\). If \(B\le0\), increasing portfolio size alone cannot make living maintenance dominate.

### Shared-cost attribution frontier
If \(F>0\),

\[
\boxed{\alpha_{BE}=\frac{nQB}{F}},
\]

with living maintenance preferred for \(\alpha<\alpha_{BE}\), subject to \(0\le\alpha\le1\).

### Cadence frontier
Let

\[
z=m(\rho)-\phi-\eta-\Delta c.
\]

Because \(g(d)\) increases from 0 to 1, a unique positive cadence frontier exists for \(0<z<1\). Put \(a=1-z\). The positive solution to \(g(d_{BE})=z\) is

\[
\boxed{d_{BE}=\frac{1}{a}+W_0\!\left(-\frac{e^{-1/a}}{a}\right)}.
\]

The \(W_{-1}\) branch returns the spurious \(d=0\) root introduced when the defining equation is multiplied by \(d\). Living maintenance dominates on timeliness grounds for \(d<d_{BE}\), conditional on the base assumption that \(C_L\) is locally cadence-invariant. Cadence-dependent release costs are a planned robustness extension.

### Dimensionless topic/reset frontier
For fixed \(d,\phi,\eta,\Delta c\), define

\[
c=g(d)+\phi+\eta+\Delta c.
\]

If \(0<c<1\), break-even in \(\rho\) is exact. Since \(m(\rho)=c\) implies \(x_c=-\log(1-c)\),

\[
\boxed{\rho_{BE}=c+(1-c)\log(1-c)}.
\]

Living maintenance is preferred for \(\rho>\rho_{BE}\) within \(0<\rho<1\). This is a **dimensionless composite frontier**. It must not be misread as the effect of changing only \(D\), \(H\), or \(\mu\) while holding dimensional quantities fixed, because those changes also alter other dimensionless terms.

## 7. Comparative statics

For \(0<\rho<1\),

\[
\frac{dx^*}{d\rho}=\frac{e^{x^*}}{x^*}>0.
\]

Holding \(\mu,Q\) fixed, larger scheduled reset burden \(S\) lengthens \(T^*\):

\[
\frac{\partial T^*}{\partial S}=\frac{e^{x^*}}{x^*Q}>0.
\]

Holding \(S,\mu\) fixed, larger stale-decision consequence rate \(Q\) shortens \(T^*\):

\[
\frac{\partial T^*}{\partial Q}=-\frac{\rho e^{x^*}}{\mu x^*Q}<0.
\]

Holding \(S,Q\) fixed, the physical effect of \(\mu\) is non-monotone:

\[
\frac{\partial T^*}{\partial\mu}
=\frac{e^{x^*}-1-x^*-(x^*)^2}{\mu^2x^*}.
\]

The sign changes at \(x\approx1.793282\) (\(\rho\approx0.535161\)). For lower \(\rho\), higher material-change intensity shortens the optimal interval; near the \(\rho=1\) no-finite-optimum boundary, the optimal finite interval lengthens because repeated resetting can no longer keep pace with rapid obsolescence.

## 8. Square-root approximation

Since

\[
h(x)=\frac{x^2}{2}-\frac{x^3}{3}+\frac{x^4}{8}-\frac{x^5}{30}+O(x^6),
\]

letting \(s=\sqrt{2\rho}\), inversion gives

\[
\boxed{x^*=s+\frac{s^2}{3}+\frac{11s^3}{72}+\frac{43s^4}{540}+O(s^5)}.
\]

Also \(h(x)=\int_0^x u e^{-u}du<x^2/2\) for all \(x>0\), so

\[
\sqrt{2\rho}<x^*\quad (0<\rho<1).
\]

Therefore the leading square-root formula **always underestimates** the exact dimensionless scheduled interval. Its quantitative error over the prespecified domain is evaluated in the archived analysis.

## 9. Non-exponential extension

Let \(r(x)\) be a dimensionless survival function for time to material conclusion change, strictly decreasing with \(r(0)=1\). Define

\[
G_r(x)=1-\frac{1}{x}\int_0^x r(u)\,du.
\]

The normalized scheduled variable burden is \(\rho/x+G_r(x)\), and the first-order condition is

\[
\boxed{\rho=H_r(x)=\int_0^x r(u)\,du-xr(x)}.
\]

Because

\[
H_r'(x)=-xr'(x)>0,
\]

there is at most one finite optimum. If \(xr(x)\to0\) and

\[
M_r=\int_0^\infty r(u)\,du<\infty,
\]

then a unique finite optimum exists iff \(0<\rho<M_r\). At that optimum,

\[
\boxed{\min_x\{\rho/x+G_r(x)\}=1-r(x^*)}.
\]

This minimum identity is not specific to the exponential case.

### Weibull robustness family
For

\[
r_k(x)=e^{-x^k},\qquad k>0,
\]

\[
M_k=\Gamma\left(1+\frac1k\right),
\]

and the finite-optimum condition becomes

\[
0<\rho<\Gamma\left(1+\frac1k\right).
\]

The exponential base model is \(k=1\). Values \(k<1\) represent a decreasing hazard of material change and \(k>1\) an increasing hazard. Except for special cases, \(x^*\) is obtained numerically from \(H_k(x)=\rho\).

## 10. Interpretation limits

1. A material-change event is a latent decision-relevant state change, not every new publication.
2. Decision opportunities are assumed independent of time since refresh in the base model.
3. Resource and decision consequences must be commensurate.
4. The long-run model is not a finite-horizon funding model.
5. alpha is causal/avoidable shared-cost attribution, not an arbitrary accounting allocation.
6. A fixed per-living-release cost that scales with cadence must be represented explicitly in robustness analyses.
7. No-finite-periodic-optimum is a mathematical boundary; operational retirement also depends on relevance, certainty, expected research and resources.
