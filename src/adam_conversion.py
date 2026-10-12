"""SDTM -> ADaM conversion: real derivation logic producing ADSL
(subject-level analysis dataset) with standard ADaM-derived variables
(AGE from BRTHDTC/RFSTDTC, TRT01P/TRT01PN treatment coding, SAFFL/ITTFL
population flags)."""
from __future__ import annotations

import pandas as pd


def derive_age(dm: pd.DataFrame) -> pd.Series:
    brthdtc = pd.to_datetime(dm["BRTHDTC"])
    rfstdtc = pd.to_datetime(dm["RFSTDTC"])
    return ((rfstdtc - brthdtc).dt.days / 365.25).round(0).astype(int)


def derive_treatment_coding(dm: pd.DataFrame) -> tuple[pd.Series, pd.Series]:
    trt01p = dm["ARM"]
    code_map = {"Placebo": 0, "Drug X 10mg": 1, "Drug X 20mg": 2}
    trt01pn = trt01p.map(code_map)
    return trt01p, trt01pn


def to_adsl(dm: pd.DataFrame, vs: pd.DataFrame) -> pd.DataFrame:
    adsl = dm.copy()
    adsl["AGE"] = derive_age(dm)
    adsl["AGEU"] = "YEARS"
    adsl["TRT01P"], adsl["TRT01PN"] = derive_treatment_coding(dm)

    # population flags: SAFFL = any post-randomization VS record exists;
    # ITTFL = randomized (RFSTDTC non-missing) -- standard ADaM logic
    subjects_with_vs = set(vs["USUBJID"].unique())
    adsl["SAFFL"] = adsl["USUBJID"].isin(subjects_with_vs).map({True: "Y", False: "N"})
    adsl["ITTFL"] = adsl["RFSTDTC"].notna().map({True: "Y", False: "N"})

    return adsl[["STUDYID", "USUBJID", "AGE", "AGEU", "SEX", "ARM", "TRT01P", "TRT01PN", "SAFFL", "ITTFL"]]


def to_advs(vs: pd.DataFrame, adsl: pd.DataFrame) -> pd.DataFrame:
    """ADVS (Vital Signs analysis dataset): merges in treatment info and
    derives CHG (change from baseline) and BASE."""
    merged = vs.merge(adsl[["USUBJID", "TRT01P", "TRT01PN"]], on="USUBJID", how="left")
    baseline = merged[merged["VISIT"] == "Baseline"][["USUBJID", "VSTESTCD", "VSORRES"]].rename(
        columns={"VSORRES": "BASE"}
    )
    advs = merged.merge(baseline, on=["USUBJID", "VSTESTCD"], how="left")
    advs["AVAL"] = advs["VSORRES"]
    advs["CHG"] = advs["AVAL"] - advs["BASE"]
    return advs


if __name__ == "__main__":
    from .simulate_raw_edc import simulate_raw_edc
    from .sdtm_conversion import convert_raw_to_sdtm

    raw = simulate_raw_edc()
    sdtm = convert_raw_to_sdtm(raw)
    adsl = to_adsl(sdtm["dm"], sdtm["vs"])
    advs = to_advs(sdtm["vs"], adsl)
    print(adsl.shape)
    print(adsl.head())
    print(advs.shape)
