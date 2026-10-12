"""Simulate raw EDC (electronic data capture) export for 340 patients --
messy field names and per-visit row structure, the real starting point a
raw-to-SDTM-to-ADaM pipeline has to normalize."""
from __future__ import annotations

from datetime import date, timedelta

import numpy as np
import pandas as pd

N_SUBJECTS = 340
SEED = 79


def simulate_raw_edc(n: int = N_SUBJECTS, seed: int = SEED) -> pd.DataFrame:
    rng = np.random.default_rng(seed)
    rows = []
    enroll_start = date(2025, 1, 6)
    for i in range(n):
        subj = f"{1000+i}"
        dob = enroll_start - timedelta(days=int(rng.integers(18 * 365, 85 * 365)))
        sex = rng.choice(["Male", "Female"])
        arm = rng.choice(["Drug X 10mg", "Drug X 20mg", "Placebo"])
        rand_date = enroll_start + timedelta(days=int(rng.integers(0, 200)))
        for visit_num, visit_name in enumerate(["Screening", "Baseline", "Week 4", "Week 8"]):
            visit_date = rand_date + timedelta(days=visit_num * 28)
            sbp = rng.normal(130, 16)
            rows.append({
                "SubjNum": subj, "DOB_raw": dob.isoformat(), "GENDER_txt": sex,
                "TreatmentArm_raw": arm, "RandDate_raw": rand_date.isoformat(),
                "VisitName": visit_name, "VisitDate_raw": visit_date.isoformat(),
                "SBP_mmHg": round(float(sbp), 1),
            })
    df = pd.DataFrame(rows)

    # inject a small number of realistic raw-data defects (malformed visit
    # date strings from free-text EDC entry) so the conversion/validation
    # has something genuine to catch, rather than a trivially clean input
    rng2 = np.random.default_rng(seed + 1)
    defect_idx = rng2.choice(df.index, size=max(1, int(len(df) * 0.006)), replace=False)
    df.loc[defect_idx, "VisitDate_raw"] = df.loc[defect_idx, "VisitDate_raw"].str.slice(0, 7)  # truncated date

    return df


if __name__ == "__main__":
    df = simulate_raw_edc()
    print(df.shape)
    print(df.head())
