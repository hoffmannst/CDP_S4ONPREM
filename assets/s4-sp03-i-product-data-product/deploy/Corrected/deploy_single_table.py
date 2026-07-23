#!/usr/bin/env python3
"""
deploy_single_table.py
Deploys a single RAW_* entity from raw-tables.csn.json.

Change ENTITY_NAME below to target a different entity.
"""
import json
import os
import subprocess
import sys
import tempfile

CSN_FILE    = "/Users/D026118/Desktop/CDP_S4ONPREM/assets/s4-sp03-i-product-data-product/deploy/local-tables/raw-tables.csn.json"
SPACE       = "PM_OBJSTORE"
OUT_DIR     = "/Users/D026118/Desktop/CDP_S4ONPREM/assets/s4-sp03-i-product-data-product/deploy/Corrected"
ENTITY_NAME = "RAW_I_PRODUCTDESCRIPTION"   # ← change this to target a different entity

os.makedirs(OUT_DIR, exist_ok=True)


def fix_entity(entity_def: dict) -> dict:
    fixed = dict(entity_def)
    fixed["@ObjectModel.modelingPattern"]       = {"#": "DATA_STRUCTURE"}
    fixed["@ObjectModel.supportedCapabilities"] = [{"#": "DATA_STRUCTURE"}]
    fixed["@DataWarehouse.persistence.hdlf.tableFormat"] = {"#": "DELTA_LAKE"}
    for col_def in fixed.get("elements", {}).values():
        if "key" not in col_def:
            col_def["key"] = False
    return fixed


def entity_exists(name: str) -> bool:
    result = subprocess.run(
        ["datasphere", "objects", "local-tables", "read",
         "--space", SPACE, "--technical-name", name],
        capture_output=True, text=True,
    )
    return result.returncode == 0


def confirm_overwrite(name: str) -> bool:
    try:
        answer = input(f"  ⚠️  '{name}' already exists in '{SPACE}'. Overwrite? [y/N] ").strip().lower()
    except (EOFError, KeyboardInterrupt):
        print()
        return False
    return answer in ("y", "yes")


# ── Load CSN ─────────────────────────────────────────────────────────────────
with open(CSN_FILE) as f:
    csn = json.load(f)

if ENTITY_NAME not in csn["definitions"]:
    print(f"ERROR: '{ENTITY_NAME}' not found in {CSN_FILE}")
    print(f"Available entities: {', '.join(csn['definitions'].keys())}")
    sys.exit(1)

payload = {"definitions": {ENTITY_NAME: fix_entity(csn["definitions"][ENTITY_NAME])}}

print(f"Entity : {ENTITY_NAME}")
print(f"Space  : {SPACE}\n")

# ── Existence check ───────────────────────────────────────────────────────────
exists = entity_exists(ENTITY_NAME)

if exists:
    print(f"'{ENTITY_NAME}' already exists in '{SPACE}'.")
    if not confirm_overwrite(ENTITY_NAME):
        print("Skipped.")
        sys.exit(0)
    cli_action = ["objects", "local-tables", "update",
                  "--space", SPACE,
                  "--technical-name", ENTITY_NAME,
                  "--file-path", "{tmp_file}",
                  "--deploy"]
else:
    print(f"'{ENTITY_NAME}' does not exist yet — will create.")
    cli_action = ["objects", "local-tables", "create",
                  "--space", SPACE,
                  "--file-path", "{tmp_file}",
                  "--deploy"]

# ── Deploy ────────────────────────────────────────────────────────────────────
with tempfile.TemporaryDirectory() as tmp:
    tmp_file = os.path.join(tmp, f"{ENTITY_NAME}.json")
    with open(tmp_file, "w") as f:
        json.dump(payload, f, indent=2)

    cmd = ["datasphere"] + [arg.replace("{tmp_file}", tmp_file) for arg in cli_action]

    print(f"\nRunning: {' '.join(cmd)}\n")
    result = subprocess.run(cmd, capture_output=True, text=True)

    print("=== stdout ===")
    print(result.stdout or "(empty)")
    print("=== stderr ===")
    print(result.stderr or "(empty)")

    if result.returncode == 0:
        out_file = os.path.join(OUT_DIR, f"{ENTITY_NAME}.json")
        with open(out_file, "w") as f:
            json.dump(payload, f, indent=2)
        print(f"\n✓ Deployed and saved to Corrected/{ENTITY_NAME}.json")
    else:
        print(f"\n✗ Deployment failed (exit code {result.returncode})")
        sys.exit(1)
