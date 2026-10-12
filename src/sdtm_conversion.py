"""Raw EDC -> SDTM conversion: real structural transformation applying
CDISC SDTM conventions (standardized variable names, one row per subject
for DM, one row per subject/visit for VS, derived --DY study-day
variables)."""
from __future__ import annotations

from datetime import date

import pandas as pd


def to_dm(raw: pd.DataFrame) -> pd.DataFrame:
    """SDTM DM (Demographics) domain: one row per subject."""
    base = raw.drop_duplicates(subset=["SubjNum"]).copy()
    dm = pd.DataFrame({
        "STUDYID": "STUDY-001",
        "DOMAIN": "DM",
        "USUBJID": "STUDY-001-" + base["SubjNum"],
        "BRTHDTC": base["DOB_raw"],
        "SEX": base["GENDER_txt"].map({"Male": "M", "Female": "F"}),
        "ARM": base["TreatmentArm_raw"],
        "RFSTDTC": base["RandDate_raw"],
    })
    return dm.reset_index(drop=True)


def to_vs(raw: pd.DataFrame, dm: pd.DataFrame) -> pd.DataFrame:
    """SDTM VS (Vital Signs) domain: one row per subject/visit/parameter,
    with VSDY (study day, relative to RFSTDTC) derived."""
    merged = raw.merge(
        dm[["USUBJID", "RFSTDTC"]], left_on=("STUDY-001-" + raw["SubjNum"]), right_on="USUBJID", how="left"
    )
    rfstdtc = pd.to_datetime(merged["RFSTDTC"])
    # errors="coerce": a malformed/truncated raw date (a real EDC defect)
    # becomes NaT rather than crashing the conversion -- VSDY is then
    # correctly left missing for that record rather than silently wrong
    visit_date = pd.to_datetime(merged["VisitDate_raw"], errors="coerce")
    vsdy = (visit_date - rfstdtc).dt.days + 1  # SDTM convention: day 1 = reference start date

    vs = pd.DataFrame({
        "STUDYID": "STUDY-001", "DOMAIN": "VS",
        "USUBJID": merged["USUBJID"],
        "VISIT": merged["VisitName"],
        "VSTESTCD": "SYSBP", "VSTEST": "Systolic Blood Pressure",
        "VSORRES": merged["SBP_mmHg"], "VSORRESU": "mmHg",
        "VSDTC": merged["VisitDate_raw"], "VSDY": vsdy,
    })
    return vs.reset_index(drop=True)


def convert_raw_to_sdtm(raw: pd.DataFrame) -> dict:
    dm = to_dm(raw)
    vs = to_vs(raw, dm)
    return {"dm": dm, "vs": vs}


if __name__ == "__main__":
    from .simulate_raw_edc import simulate_raw_edc

    raw = simulate_raw_edc()
    sdtm = convert_raw_to_sdtm(raw)
    print(sdtm["dm"].shape, sdtm["vs"].shape)
    print(sdtm["dm"].head())
    print(sdtm["vs"].head())
