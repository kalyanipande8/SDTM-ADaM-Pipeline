"""End-to-end: simulate raw EDC data, convert to SDTM, convert to ADaM,
and validate the conversion against known ground truth."""
import json
import os

from src.simulate_raw_edc import simulate_raw_edc
from src.sdtm_conversion import convert_raw_to_sdtm
from src.adam_conversion import to_adsl, to_advs
from src.validation import validate_conversion

os.makedirs("data", exist_ok=True)
os.makedirs("results", exist_ok=True)

print("=== Simulating raw EDC export (340 subjects, 4 visits each) ===")
raw = simulate_raw_edc()
raw.to_csv("data/raw_edc.csv", index=False)
print(raw.shape)

print("\n=== Converting raw -> SDTM ===")
sdtm = convert_raw_to_sdtm(raw)
sdtm["dm"].to_csv("data/sdtm_dm.csv", index=False)
sdtm["vs"].to_csv("data/sdtm_vs.csv", index=False)
print(f"DM: {sdtm['dm'].shape}, VS: {sdtm['vs'].shape}")

print("\n=== Converting SDTM -> ADaM ===")
adsl = to_adsl(sdtm["dm"], sdtm["vs"])
advs = to_advs(sdtm["vs"], adsl)
adsl.to_csv("data/adam_adsl.csv", index=False)
advs.to_csv("data/adam_advs.csv", index=False)
print(f"ADSL: {adsl.shape}, ADVS: {advs.shape}")

print("\n=== Validating conversion ===")
validation = validate_conversion(raw, sdtm["dm"], sdtm["vs"], adsl)
print(validation)

summary = {
    "n_subjects": int(raw["SubjNum"].nunique()),
    "n_checks": validation["n_checks"],
    "n_pass": validation["n_pass"],
    "well_formed_date_pct": validation["well_formed_date_pct"],
    "overall_accuracy_pct": validation["accuracy_pct"],
}
with open("results/summary.json", "w") as f:
    json.dump(summary, f, indent=2, default=str)

print("\n=== Summary ===")
print(json.dumps(summary, indent=2, default=str))
