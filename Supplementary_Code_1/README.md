# Supplementary Code 1 — revision addendum (R16)

For **When should a systematic review remain living? Balancing resources, timeliness and shared infrastructure**, by Joseph B. Babigumira and Rogers Nsubuga.

This addendum implements explanatory calculations and displays from the existing model. It is **not** the complete original study archive. The original model, R/Python implementations, prespecified protocol, simulations and validation records are in:

https://github.com/ghe-consulting/living-review-maintenance-frontiers/tree/v1.0.1

Original release commit: `5c586e07a99381a5011ba8685ac1bc08ecc90cb2`.

## Start with the dimensional calculator

The calculator uses only the Python standard library. From this directory:

```bash
python maintenance_calculator.py example_B_base.json --output calculated_B.json
python maintenance_calculator.py example_B_release.json --output calculated_B_release.json
python maintenance_calculator.py example_B_base.json --sweep-loss 0.5 1 2 --output discrete_scenarios.json
```

The first example is a dimensional rescaling of the original synthetic configuration B. The second adds the existing structural fixed-release ratio 0.0025 and reports the post-protocol optimized-living comparison. The inputs are **synthetic**, not recommended costs, consequences or update schedules. The common scheduled-processing baseline of 0.2 is an arbitrary nonnegative baseline used only to display total rates; it does not change the ranking.

### Input meanings and units

Choose one time unit and one defensible common burden scale. `mu` is the material-change rate per time; `scheduled_reset` and `living_release` are burdens per update/release. `shared_rate`, `readiness_rate`, `processing_scheduled` and `processing_living` are burdens per time. `decision_rate` is relevant decision opportunities per time and `loss_per_stale_decision` is additional burden per stale decision. Their product is Q. `living_interval` is time between completed updates. `attributable_fraction` lies in [0,1]; `portfolio_size` is an integer at least 1.

For an individual review on an existing platform, add `incremental_shared_rate` to the parameter object. It replaces the equal-share charge and disables the portfolio-size threshold. This increment includes opportunity costs of scarce capacity, not just changes in cash expenditure. Do not count the same resource twice. The calculator's shared-input domain is nonnegative, as in the stated base model.

The model requires Q and mu to be positive and a positive specified living interval. Resource inputs must be finite and nonnegative. Zero fixed costs and no-finite-optimum cases are reported as **unattained boundary limits**, not recommendations to update instantly or permanently stop. When an optimum is unattained the output does not label the resulting infimum comparison as an implementable policy choice. A numerical tie uses an explicit 1e-12 normalized display tolerance; the mathematical rule remains a strict inequality.

### Scope

The model assumes stationary resource rates, a common loss scale, complete freshness at release, the stated time-to-change process, comparable quality and the specified user-consequence assumptions. The equal-sharing portfolio additionally assumes comparable reviews, fixed shared capacity and additive consequences without duplicate attribution. It does not solve adaptive policies, evidence-cutoff-to-release lag, uncertain or finite funding horizons, heterogeneous portfolio selection or affordability. Scenario grids evaluate only the supplied points; they do not prove robustness over a continuous range or represent probabilities.

## Run the fresh checks

```bash
python -m pip install -r requirements.txt
python test_maintenance_calculator.py
```

This writes `generated/r16_calculator_checks.json` and the two synthetic example outputs. The tests reconcile configurations A–C, compare first-order solutions with separate numerical minimization at 299 ratios, compare average staleness with quadrature at 301 intervals, check currency/time rescaling, inspect 12-versus-13-review thresholds and single-review increments, test equal reset/release costs, handle unattained boundaries and reject invalid inputs.

These are fresh **Python** checks, not an R re-execution, not a rerun of the original Latin-hypercube/structural experiments and not empirical validation. The environment and tolerances are recorded in the JSON report.

## Reconstruct the existing displays

```bash
python reconstruct_displays_and_checks.py
python explain_workflows.py
```

Read each script's command-line options/entry point before choosing an output directory. The scripts preserve their existing generation behavior. `generated/` includes both legacy display names and the current figure names; use the mapping below for manuscript uploads. R16 does not change the figures or their scientific source data.

| Manuscript display | Current generated filename stem |
|---|---|
| Figure 1 | Figure_1_balance |
| Figure 2 | Figure_2_cadence |
| Figure 3 | Figure_3_portfolio |
| Figure S1 | Figure_S1_exact_interval |
| Figure S2 | Figure_S2_approximation_error |
| Figure S3 | Figure_S3_Weibull |
| Figure S4 | Figure_S4_release_overhead |
| Figure S5 | Figure_S5_architectures |

## Provenance and licensing

`README_R12.md` preserves the earlier addendum description. Original configuration summaries were reconciled with repository `results/numerical_summary.json`, Git blob `07f790c4fe0456b52173f0c4b67c32daf3c05b5e`; original display constants with `protocol/figure_constants.json`, Git blob `dd5a007fce93e4221ed0675683a9abb4861c1b45`. Original simulation outputs are not overwritten by this addendum.

The original source code is MIT-licensed; its copyright and permission notice are retained in `LICENSE`. This revision addendum follows the same source-code license. The historical archive's citation metadata and the two-author paper metadata should be reconciled when preserving the final submission snapshot. No new DOI is asserted here.
