# When should a systematic review remain living? Balancing resources, timeliness and shared infrastructure

Reproducibility materials for the methodological study by 
**Joseph B. Babigumira** (Global Health Economics (GHE) Consulting, Kampala, Uganda; ORCID: https://orcid.org/0000-0003-3834-7141) and 
**Rogers Nsubuga** (Infectious Diseases Institute, Makerere University, Kampala, Uganda; ORCID: https://orcid.org/0000-0002-2674-7052).

- Correspondence: babijo@ghe-insights.com
- Repository: https://github.com/ghe-consulting/living-review-maintenance-frontiers

This repository contains the materials needed to reproduce and verify the mathematical and synthetic computational analysis.

## Revision (v1.1.0)

The original simulation results and historical validation reports from v1.0.1 are preserved unchanged. This revision adds the `Supplementary_Code_1/` folder, containing explanatory calculations, displays, a dimensional-input calculator and additional checks. The files `R13_explanatory_checks.json`, `r16_calculator_checks.json` and `revision_verification.json` in `Supplementary_Code_1/generated/` are outputs of the newly executed checks and are distinct from the original validation reports in `validation/`.

## Repository structure

- `model/` — R and independent Python implementations, formal specification, parameter dictionary, proofs, and symbolic checks.
- `protocol/` — prespecified synthetic parameter domains, architectures, seeds, analysis plan, and figure constants.
- `analysis/` — scripts that regenerate the numerical results, tables, figures, and R/Python validation grids.
- `tests/` — executable R and Python model tests and the cross-implementation comparator.
- `results/` — frozen synthetic source data, tables, figures, and numerical summary.
- `validation/` — cross-language, independent numerical, and simulation-validation summaries.
- `environment/` — software/runtime requirements and environment-capture utilities.
- `checksums/` — integrity manifests for the frozen results and distributed release.
- `Supplementary_Code_1/` — revision addendum: explanatory workflows, display reconstruction scripts, the dimensional-input calculator, its tests, and generated figures and checks.

## Software

Python dependencies are locked in `requirements.lock.txt`:

```bash
python -m pip install -r requirements.lock.txt
```

The primary R implementation uses **base R >= 4.3** and requires no contributed R packages.

## Run the model tests

```bash
python tests/test_reference.py
Rscript tests/test_model.R
```

## Reproduce the independent R/Python comparison

```bash
Rscript analysis/run_r_grid.R tests/r_grid.csv
python analysis/run_python_grid.py tests/python_grid.csv
python tests/compare_implementations.py tests/r_grid.csv tests/python_grid.csv
```

The frozen absolute and scaled-relative comparison tolerances are both `2e-9`.

## Reproduce the symbolic checks

```bash
python model/verify_symbolic.py
```

## Reproduce the full synthetic analysis

```bash
python scripts/verify_reproduction.py
```

The verifier regenerates the analysis in an isolated temporary copy and compares structured numerical outputs at the same `2e-9` absolute/scale-aware tolerance used for the independent R/Python check. This avoids treating machine-level floating-point serialization differences as scientific failures while retaining exact checksums for the archived frozen files. Figures must regenerate successfully and be non-empty; their source data are compared numerically. The Latin-hypercube living/scheduled fractions are design-space coverage summaries, not real-world probabilities or prevalence estimates.

## Verify the distributed release

```bash
python scripts/verify_release.py
```

## Citation

Citation metadata are provided in `CITATION.cff`. The Zenodo DOI for the current archived release should be used as the persistent citation once minted.

## Licensing

- Source code: **MIT License** (`LICENSE`).
- Documentation, synthetic datasets, tables, and figures: **CC BY 4.0** (`LICENSE-CONTENT.md`).
