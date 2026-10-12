# ARS Standards & GxP Validation Documentation

**Status: an authored conceptual mapping and validation framework for this
portfolio build — not a submission to a real ARS (Analysis Results
Standard) registry or a GxP-audited system.**

## ARS (Analysis Results Standard) mapping
CDISC's Analysis Results Standard defines a machine-readable structure
linking an analysis result (e.g., a derived AGE value) back to its exact
source variables, derivation logic, and the analysis dataset it populates
— the same traceability principle this pipeline implements directly in
code:

| ARS concept | This pipeline's implementation |
|---|---|
| Analysis Result | Each derived ADaM variable (AGE, TRT01PN, SAFFL, CHG) |
| Data Definition | `src/adam_conversion.py`'s derivation functions, each with one clear, named purpose |
| Reportable Variable | ADSL/ADVS output columns |
| Validation | `src/validation.py`, re-deriving each value independently and comparing |

## GxP validation framework
1. **Installation qualification (IQ) equivalent**: the pipeline's
   dependencies and Python version are pinned in `requirements.txt`.
2. **Operational qualification (OQ) equivalent**: `tests/test_pipeline.py`
   exercises every conversion step against known inputs with expected
   outputs.
3. **Performance qualification (PQ) equivalent**: `src/validation.py`
   re-derives key values (AGE, SAFFL, VSDY) independently from source data
   and confirms they match the pipeline's own output — this is the
   core GxP principle of independent verification, not just "the code
   ran without an error."
4. **Audit trail**: every derivation function is named, documented, and
   the validation report records exactly which checks passed/failed with
   the real measured pass rate — see `results/summary.json` after running
   `run_all.py`.

## Honest disclosure
This is a Python-implemented demonstration of the raw-to-SDTM-to-ADaM
conversion methodology and its validation principles — not a SAS-executed,
regulatory-submitted, or GxP-audited production system. See `sas/
convert_sdtm_adam.sas` for an authored (not executed, no SAS license
available) SAS mirror of the same conversion logic.
