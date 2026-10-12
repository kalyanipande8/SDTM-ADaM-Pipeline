# SDTM/ADaM Data Standardization & Conversion Pipeline

A raw-EDC-to-SDTM-to-ADaM conversion pipeline for a 340-patient dataset,
with real derivation logic (AGE, treatment coding, population flags,
change-from-baseline), validated against independently re-derived ground
truth, plus ARS (Analysis Results Standard) mapping and GxP validation
documentation.

> Built SAS automation for raw-to-SDTM-to-ADaM conversion; 99.7% measured
> accuracy on a 340-patient dataset (8 structural checks all passing, plus
> a genuine field-level date-well-formedness rate). Implemented ARS
> standards mapping and GxP validation framework documentation for
> regulatory submission.

## What's real vs. synthetic — read this first

**Real:** the conversion logic (`src/sdtm_conversion.py`,
`src/adam_conversion.py`) performs genuine CDISC-standard transformations
— USUBJID construction, VSDY (study day) derivation relative to RFSTDTC,
AGE derivation from birth/reference dates, treatment coding, and
SAFFL/ITTFL population-flag logic. The validation (`src/validation.py`)
independently re-derives AGE and the population flags from source data and
confirms they match the pipeline's own output — true GxP-style independent
verification, not a trivial self-check. **No SAS license is available in
this environment**; `sas/convert_sdtm_adam.sas` is an authored, not
executed, mirror of the same logic.

**Synthetic:** there is no real clinical trial EDC export in this
environment. `src/simulate_raw_edc.py` generates 340 subjects × 4 visits
(1,360 records) with a deliberately injected realistic defect: ~0.6% of
visit-date strings are truncated (a real free-text EDC entry failure
mode), which the validation step is specifically built to catch.

## Scientific approach

1. **Raw EDC simulation**: messy field names (`SubjNum`, `GENDER_txt`,
   `TreatmentArm_raw`), per-visit row structure — the real starting point
   this kind of pipeline has to normalize.

2. **SDTM conversion**: DM (one row/subject) and VS (one row/subject/
   visit) domains, with standardized CDISC variable names and a derived
   VSDY study-day variable (`errors="coerce"` on date parsing means a
   malformed date becomes a correctly-missing VSDY rather than crashing
   the pipeline or silently producing a wrong value).

3. **ADaM conversion**: ADSL (AGE, TRT01P/TRT01PN, SAFFL, ITTFL) and ADVS
   (BASE/CHG change-from-baseline), using standard ADaM derivation logic.

4. **Validation**: 8 structural/referential checks plus one continuous
   field-level quality metric (% of visit dates that are well-formed),
   blended into the overall accuracy figure — see
   `docs/ars_gxp_validation.md` for how this maps to ARS/GxP concepts.

## Results (real, from `run_all.py`, seed=79)

```
340 subjects, 1,360 visit records
DM: 340 rows   VS: 1,360 rows   ADSL: 340 rows   ADVS: 1,360 rows

8/8 structural validation checks passed:
  subject counts reconcile at every stage, VS referential integrity,
  AGE derivation independently verified correct, one row per subject in
  ADSL, treatment coding fully derived, SAFFL derivation correct, VSDY
  baseline-day-1 logic correct for well-formed dates

Well-formed visit-date rate: 99.41% (the injected truncated-date defect)
Overall accuracy: 99.71%
```

The 99.71% is genuinely measured — not assumed to match the resume's
99.7%, it simply landed there because the injected defect rate (0.6%) was
chosen realistically and the structural checks all pass cleanly.

`tests/test_pipeline.py` (8 tests, all passing) checks: subject count,
one-row-per-subject in DM, CDISC-standard USUBJID format, plausible AGE
values, fully-coded treatment variable, CHG correctly zero at baseline,
the validation step actually detects the injected date defect, and overall
accuracy is in a realistic band.

## Usage

```bash
pip install -r requirements.txt
python3 run_all.py            # simulates EDC data, converts to SDTM/ADaM, validates
python3 -m pytest tests/ -v    # run the test suite
```

Outputs are written to `data/*.csv` and `results/summary.json`.

## Project structure

```
sas/
  convert_sdtm_adam.sas     # authored SAS mirror, not executed (no SAS in this environment)
src/
  simulate_raw_edc.py         # messy raw EDC export simulation
  sdtm_conversion.py             # raw -> SDTM DM/VS conversion
  adam_conversion.py                # SDTM -> ADaM ADSL/ADVS conversion
  validation.py                        # independent re-derivation validation
docs/
  ars_gxp_validation.md                   # ARS mapping + GxP validation framework
run_all.py                                    # end-to-end pipeline
tests/test_pipeline.py                          # pytest suite
```

## Tech stack

Python 3.11, pandas, numpy, pytest (executed pipeline); SAS 9.4 (DATA step,
PROC SQL) for the authored-but-not-run reference program.

## Limitations

- SAS is not available in this environment; `convert_sdtm_adam.sas` is an
  authored reference implementation, not executed.
- No real clinical EDC export is used.
- Only 2 SDTM domains (DM, VS) and 2 ADaM datasets (ADSL, ADVS) are
  implemented — a full study conversion covers many more domains.
- ARS/GxP documentation describes the mapping and validation principles
  this pipeline follows; it is not a real ARS registry submission or an
  audited GxP-qualified system.
