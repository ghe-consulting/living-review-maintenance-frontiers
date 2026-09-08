# Synthetic design and simulation protocol

**Prespecified before simulation:** 2026-09-06
**Input provenance:** All inputs used by this analysis are synthetic mathematical design values or public literature sources.

## 1. Purpose

This document specifies the complete synthetic numerical experiment used to interpret the exact living-review maintenance model. The primary analysis is a **dimensionless design-space exploration**, not an empirical estimate of how often living review maintenance is economically preferred in real programmes. All scenario values below are mathematical design inputs chosen before simulation execution.

The primary exponential model uses

\[
A = m(\rho)-\{g(d)+\phi+\eta+\Delta c\},
\qquad
\phi=\frac{\alpha\omega}{n},\quad \omega=F/Q,
\]

where \(A>0\) indicates lower normalized long-run burden under living maintenance.

## 2. Primary global exploration

Use a scrambled Latin-hypercube design with **32,768** points and the frozen `primary_lhs` seed. Seven dimensions are generated independently on \([0,1]\) and transformed as follows.

| Input | Transform | Frozen domain | Rationale |
|---|---|---|---|
| `rho` | linear in logit(rho) | 1e-4 to 0.999 | Densifies both finite-optimum boundaries without assigning probability mass. |
| `d` | log10 | 1e-4 to 10 | Spans near-continuous refresh through severe staleness. |
| `n` | round(2^(8u)) | 1 to 256 reviews | Covers single-review through large shared portfolios on a scale-neutral axis. |
| `alpha` | linear | 0 to 1 | Full causal attributable-share domain. |
| `omega=F/Q` | log10 | 1e-3 to 10 | Four orders of magnitude for shared operating burden relative to full-staleness consequence rate. |
| `eta=f/Q` | linear | 0 to 0.5 | Covers negligible to material review-specific readiness burden. |
| `Delta c=(C_L-C_S)/Q` | linear | -0.5 to +0.5 | Symmetric processing advantage/disadvantage; no strategy is privileged ex ante. |

The LHS is a **coverage device**, not a joint prior. Therefore design-space proportions are labelled *coverage fractions*, never prevalence or probability.

## 3. Deterministic boundary design

In addition to the LHS, evaluate an explicit boundary set so conclusions do not depend on space-filling randomness:

- `rho`: 1e-6, 1e-4, 0.01, 0.1, 0.5, 0.9, 0.99, 0.999999
- `d`: 0, 1e-4, 0.01, 0.1, 1, 10
- `n`: 1, 2, 8, 32, 128, 256
- `alpha`: 0, 0.5, 1
- `omega`: 0, 1e-3, 0.1, 1, 10
- `eta`: 0, 0.1, 0.5
- `Delta c`: -0.5, 0, +0.5

Boundary calculations are deterministic and are not pooled with the LHS for coverage fractions.

## 4. Three independently specified illustrative architectures

The architectures are abstractions of increasing shared-workflow maturity. They are **not empirical programme estimates** and are never used to support the primary claim. Each architecture is evaluated across the same full `rho` grid rather than at a selected topic value.

1. **Small isolated/manual workflow:** `n=2`, `alpha=0.90`, `omega=0.30`, `eta=0.10`, `Delta c=+0.10`, `d=0.30`.
2. **Shared balanced workflow:** `n=24`, `alpha=0.50`, `omega=1.00`, `eta=0.05`, `Delta c=0`, `d=0.10`.
3. **Large automation-assisted workflow:** `n=128`, `alpha=0.20`, `omega=3.00`, `eta=0.02`, `Delta c=-0.10`, `d=0.03`.

Names describe the abstract rule used to construct each architecture; they do not correspond to any real consortium or institution.

## 5. Structural sensitivity

### 5.1 Hazard shape
Use Weibull survival \(r_k(x)=e^{-x^k}\) for `k = 0.5, 0.75, 1, 1.5, 2`.

Two comparisons are prespecified:

- **Common-rho comparison:** `rho` in 1e-4 to 0.85 so a finite scheduled optimum exists for every frozen shape.
- **Boundary-scaled comparison:** \(q=\rho/M_k\) in 1e-4 to 0.999, where \(M_k=\Gamma(1+1/k)\), to compare equal relative distance from each shape-specific no-finite-optimum boundary.

Use 8,192 LHS points for the structural sample and cross the same points with all five shapes.

### 5.2 Automation symmetry
At identical values of all other inputs, evaluate paired processing differentials:

`Delta c = 0, ±0.05, ±0.15, ±0.30`.

Report effects symmetrically as living-favoured (`Delta c<0`) versus scheduled-favoured (`Delta c>0`). Do not report only one side.

### 5.3 Cadence-dependent living release overhead
As a workflow robustness extension, add

\[
\psi/d
\]

to normalized living burden, where \(\psi=R_L\mu/Q\) is fixed burden per living conclusion release scaled to the model. Evaluate `psi = 0, 0.0025, 0.01, 0.04`. This extension is reported separately from the base model.

### 5.4 Shared-cost attribution
Evaluate `alpha=0`, `0.25`, `0.5`, `0.75`, `1` on common surfaces to show how a causal attribution assumption—not accounting allocation—moves the portfolio frontier.

## 6. Dimensional interpretation experiment

The main paper remains dimensionless. To translate \(x^*\) and \(d\) into calendar time, use synthetic change intensities

`mu = 0.10, 0.25, 0.50, 1.00, 2.00 per year`.

Set `Q=1` arbitrary burden-unit/year for the mapping only. Then

\[
T^*=x^*/\mu,\qquad \delta=d/\mu,\qquad S=\rho/\mu.
\]

No absolute cost or monetary interpretation is attached to this experiment.

## 7. Prespecified estimands

Primary exact outputs:

- `x_star(rho)` and `m(rho)`;
- living advantage `A`;
- policy classification `living` if `A>0`, `scheduled` otherwise;
- `n_BE`, `alpha_BE`, `d_BE`, and `rho_BE`;
- no-finite-scheduled-optimum flag.

Design summaries:

- LHS **coverage fraction** classified living versus scheduled;
- distribution of continuous `n_BE` among points with positive portfolio margin;
- architecture-specific `rho_BE` and full frontier curves;
- classification switch rate under structural scenarios relative to the base exponential model;
- shift in `rho_BE` and `d_BE` under hazard and workflow extensions.

Approximation summaries:

- absolute and relative error of \(\sqrt{2\rho}\) versus exact \(x^*\);
- normalized cost regret from using the approximate interval rather than \(x^*\);
- thresholds of `rho` at which interval relative error first exceeds 1%, 5%, 10%, and 25%.

## 8. Prespecified figures

1. Exact scheduled optimum \(x^*(\rho)\), square-root approximation, and relative error.
2. Base \((\rho,d)\) policy-region surface at several fixed non-timeliness burdens.
3. Portfolio break-even surface `n_BE` versus `rho` and attributable shared burden.
4. Three architecture frontier curves across `rho`.
5. Structural sensitivity: Weibull shape and cadence-dependent release overhead.

## 9. Prespecified tables

1. Parameter definitions/domains/provenance.
2. Exact frontier and approximation-error summary.
3. Structural-sensitivity decision-switch summary.

## 10. Resolution and convergence checks

- Recompute each two-dimensional policy surface at 256x256 and 512x512.
- Require no classification disagreement at shared grid coordinates other than floating-point ties within `1e-12` of the exact decision boundary.
- Require frontier locations to agree within 0.25% of the plotted axis span.
- LHS coverage fractions are recomputed with an independently seeded 32,768-point replicate; absolute difference must be <=0.01. Coverage fractions are descriptive only.

## 11. Prohibitions

- No scenario may be changed after viewing simulation results.
- Parameter domains are independently specified synthetic mathematical design values.
- No architecture may be replaced because its result looks uninteresting.
- No design-space coverage fraction may be described as a real-world probability.
- No empirical cost estimate is inferred from the dimensionless model.
