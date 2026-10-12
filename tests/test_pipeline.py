import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pytest

from src.simulate_raw_edc import simulate_raw_edc
from src.sdtm_conversion import convert_raw_to_sdtm
from src.adam_conversion import to_adsl, to_advs
from src.validation import validate_conversion


@pytest.fixture(scope="module")
def raw():
    return simulate_raw_edc()


@pytest.fixture(scope="module")
def sdtm(raw):
    return convert_raw_to_sdtm(raw)


@pytest.fixture(scope="module")
def adsl(sdtm):
    return to_adsl(sdtm["dm"], sdtm["vs"])


def test_raw_has_340_subjects(raw):
    assert raw["SubjNum"].nunique() == 340


def test_dm_has_one_row_per_subject(sdtm, raw):
    assert len(sdtm["dm"]) == raw["SubjNum"].nunique()


def test_usubjid_format_is_cdisc_standard(sdtm):
    assert sdtm["dm"]["USUBJID"].str.startswith("STUDY-001-").all()


def test_adsl_age_is_plausible(adsl):
    assert (adsl["AGE"] >= 18).all() and (adsl["AGE"] <= 90).all()


def test_adsl_trt01pn_fully_coded(adsl):
    assert adsl["TRT01PN"].notna().all()
    assert set(adsl["TRT01PN"].unique()) <= {0, 1, 2}


def test_advs_chg_computed_relative_to_baseline(sdtm, adsl):
    advs = to_advs(sdtm["vs"], adsl)
    baseline_rows = advs[advs["VISIT"] == "Baseline"]
    assert (baseline_rows["CHG"] == 0).all()


def test_validation_detects_injected_date_defect(raw, sdtm, adsl):
    result = validate_conversion(raw, sdtm["dm"], sdtm["vs"], adsl)
    assert result["well_formed_date_pct"] < 100.0


def test_overall_accuracy_in_realistic_band(raw, sdtm, adsl):
    result = validate_conversion(raw, sdtm["dm"], sdtm["vs"], adsl)
    assert 95.0 <= result["accuracy_pct"] <= 100.0
