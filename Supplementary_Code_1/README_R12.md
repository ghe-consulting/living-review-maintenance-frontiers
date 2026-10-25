# Supplementary Code 1: revision-stage displays and analytical checks

Associated manuscript: **When should a systematic review remain living? Decision frontiers for maintenance under shared synthesis infrastructure**. Authors: Joseph B. Babigumira and Rogers Nsubuga. Correspondence: babijo@ghe-insights.com. Prepared 2026-09-17.

## Scope

This is an **addendum**, not the full original reproducibility archive. The original model, synthetic protocol, simulation source data, R/Python implementations and archived validation are in [release v1.0.1](https://github.com/ghe-consulting/living-review-maintenance-frontiers/tree/v1.0.1).

The supplied script reconstructs seven displays from the original equations and prespecified display constants. It reconciles the three synthetic workflow configurations with their reported summaries, explains their decisions at the previously specified boundary value rho=0.01, and checks the additional cadence-optimization corollary introduced in the revised manuscript (equation 10; Supplementary Proposition S11).

The corollary and its numerical checks were added **after the original numerical protocol**. They are not represented as prespecified simulation results. This addendum neither re-estimates the original 32,768-point experiment nor changes its reported outputs, random seeds, structural designs or thresholds. It does not execute R, and successful execution is not a claim that the complete original cross-language validation has been rerun.

## Run

Python 3.10 or later is required; the recorded successful execution used Python 3.13.5. Install the packages in a suitable environment and run:

```bash
python -m pip install -r requirements.txt
python reconstruct_displays_and_checks.py --output ./generated
```

The analytical script requires no internet access. Installing dependencies may require access to the package index. It writes PNG and vector-PDF figures, CSV source data, and a JSON verification report. Running it again overwrites files in the specified output directory; use a different directory to retain the supplied outputs unchanged.

## Contents

`reconstruct_displays_and_checks.py` contains the equations, input checks, frozen configuration constants, numerical checks and figure generation. `generated/` contains all executed outputs, including `revision_verification.json` and `corollary_checks.csv`.

Main figures are `Figure_1_architectures`, `Figure_2_cadence` and `Figure_3_portfolio`. Supplementary figures are `Figure_S1_exact_interval`, `Figure_S2_approximation_error`, `Figure_S3_Weibull` and `Figure_S4_release_overhead`. Each has a vector PDF, a PNG preview, and source data. The PNGs are intended for inspection and embedded review documents; the vector PDFs preserve publication-quality line art.

Compared with the earlier displays, the revision changes ordering and presentation, separates compound panels, lets unbounded cadence curves leave the plot rather than flattening them at its limit, and displays portfolio thresholds as curves at the prespecified shared-burden constants. No new empirical parameter calibration is implied.

## Source provenance

Original configuration values and reported numerical summaries: `results/numerical_summary.json`, Git blob `07f790c4fe0456b52173f0c4b67c32daf3c05b5e`.

Original display constants: `protocol/figure_constants.json`, Git blob `dd5a007fce93e4221ed0675683a9abb4861c1b45`.

Original reference implementation consulted: `model/python/routeb_reference.py`, Git blob `b845e95d03f81d69f048d85775c04ca9330a8eac`.

Those paths are relative to the original v1.0.1 repository. The existing architecture labels are construction rules, not names of real organizations. Negative incremental living burden represents savings relative to the removed scheduled-processing baseline, not negative total expenditure.

## Verification

The supplied run reconciled configuration values with the archive to within 5.56e-17 (tolerance 2e-12). Across 239 distinct values, the largest discrepancy between the exact minimum and separate bounded minimization on the log interval was 1.56e-15 (tolerance 2e-9). Exact machine-readable results and environment versions are in `generated/revision_verification.json`.

Figures S3 and S4 are reference curves, not reproductions of the entire structural experiment. Figure S4 holds living cadence fixed; it does not display the new optimized-cadence corollary. Approximation first-exceedance values in the paper remain the original frozen-grid values, not estimates from the reconstructed graph.

## Attribution and assistance

The paper's two-author contributions are stated in the manuscript. Code preparation and revision used AI assistance under author direction. The manuscript reports the tool roles; numerical outputs are produced by the executable script. This statement does not attribute an independent computational audit to either author.

Original archive licensing and citation metadata remain attached to that archive. The authors should confirm licensing and persistent citation metadata for the addendum when archiving the final submission release. No new DOI is claimed here.
