#!/usr/bin/env python3
"""
deploy_raw_tables.py
Fixes raw-tables.csn.json payload and deploys all 22 RAW_* entities to Datasphere.

Behaviour:
  - If the entity does NOT exist  → create it
  - If the entity ALREADY EXISTS  → prompt for overwrite confirmation
      y / yes  → overwrite using 'objects local-tables update'
      n / no / <Enter>  → skip
  - On success, persists the corrected JSON to deploy/Corrected/<NAME>.json

Fixes applied per entity:
  1. @ObjectModel.modelingPattern       → DATA_STRUCTURE
  2. @ObjectModel.supportedCapabilities → [DATA_STRUCTURE]
  3. @DataWarehouse.persistence.hdlf.tableFormat → DELTA_LAKE
  4. "key": false added explicitly to all non-key elements
"""
import json
import os
import subprocess
import sys
import tempfile

CSN_FILE = "/Users/D026118/Desktop/CDP_S4ONPREM/assets/s4-sp03-i-product-data-product/deploy/local-tables/raw-tables.csn.json"
SPACE    = "PM_OBJSTORE"
OUT_DIR  = "/Users/D026118/Desktop/CDP_S4ONPREM/assets/s4-sp03-i-product-data-product/deploy/Corrected"

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
    """Returns True if the entity already exists in the space."""
    result = subprocess.run(
        [
            "datasphere", "objects", "local-tables", "read",
            "--space",          SPACE,
            "--technical-name", name,
        ],
        capture_output=True,
        text=True,
    )
    return result.returncode == 0


def confirm_overwrite(name: str) -> bool:
    """Prompt the user for overwrite confirmation. Default is No."""
    try:
        answer = input(f"  ⚠️  '{name}' already exists in '{SPACE}'. Overwrite? [y/N] ").strip().lower()
    except (EOFError, KeyboardInterrupt):
        print()
        return False
    return answer in ("y", "yes")


with open(CSN_FILE) as f:
    csn = json.load(f)

definitions = csn.get("definitions", {})
entities    = list(definitions.keys())
print(f"Found {len(entities)} entities — space: {SPACE}\n")

failed    = []
skipped   = []
persisted = []

with tempfile.TemporaryDirectory() as tmp:
    for i, name in enumerate(entities, 1):
        payload  = {"definitions": {name: fix_entity(definitions[name])}}
        tmp_file = os.path.join(tmp, f"{name}.json")
        with open(tmp_file, "w") as f:
            json.dump(payload, f, indent=2)

        print(f"[{i:02d}/{len(entities)}] {name}", end=" ", flush=True)

        # ── Existence check ──────────────────────────────────────────────────
        exists = entity_exists(name)

        if exists:
            print("(exists)", end=" ", flush=True)
            if not confirm_overwrite(name):
                print(f"  → skipped")
                skipped.append(name)
                continue
            # Overwrite with update
            cli_action = ["objects", "local-tables", "update",
                          "--space", SPACE,
                          "--technical-name", name,
                          "--file-path", tmp_file,
                          "--deploy"]
        else:
            print("(new)", end=" ", flush=True)
            cli_action = ["objects", "local-tables", "create",
                          "--space", SPACE,
                          "--file-path", tmp_file,
                          "--deploy"]

        # ── Deploy ───────────────────────────────────────────────────────────
        result = subprocess.run(
            ["datasphere"] + cli_action,
            capture_output=True,
            text=True,
        )

        if result.returncode == 0:
            out_file = os.path.join(OUT_DIR, f"{name}.json")
            with open(out_file, "w") as f:
                json.dump(payload, f, indent=2)
            persisted.append(name)
            print(f"✓  → saved to Corrected/{name}.json")
        else:
            print("✗ FAILED")
            print(f"    stdout: {result.stdout.strip()}")
            print(f"    stderr: {result.stderr.strip()}")
            failed.append(name)

# ── Summary ──────────────────────────────────────────────────────────────────
print(f"\n{'='*55}")
print(f"Deployed & persisted : {len(persisted)}/{len(entities)}")
print(f"Skipped (no overwrite): {len(skipped)}")
if skipped:
    print(f"  {', '.join(skipped)}")
if persisted:
    print(f"Saved to             : {OUT_DIR}")
if failed:
    print(f"Failed               : {', '.join(failed)}")
    sys.exit(1)
else:
    print("Done.")
