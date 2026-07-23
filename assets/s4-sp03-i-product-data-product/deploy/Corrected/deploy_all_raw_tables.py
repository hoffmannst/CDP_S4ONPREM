#!/usr/bin/env python3
"""
deploy_all_raw_tables.py
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Deploys ALL 22 delta-enabled local table definitions from raw-tables.csn.json
to Datasphere space PM_OBJSTORE.

For each entity:
  1. Builds a delta-enabled payload (main entity + _Delta companion)
  2. Checks if it already exists in the tenant
     • New      → creates directly
     • Existing → prompts for overwrite confirmation; skips if declined
  3. On success → persists corrected JSON to deploy/Corrected/<NAME>.json

Payload format confirmed working:
  objects local-tables create --space PM_OBJSTORE --file-path <file> --deploy
  Payload: { "definitions": { "<NAME>": {...}, "<NAME>_Delta": {...} } }

Usage:
  python3 deploy_all_raw_tables.py

  # Auto-confirm all overwrites (non-interactive):
  OVERWRITE_ALL=1 python3 deploy_all_raw_tables.py
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"""
import copy
import json
import os
import subprocess
import sys
import tempfile

# ── Config ────────────────────────────────────────────────────────────────────
BASE_DIR = "/Users/D026118/Desktop/CDP_S4ONPREM/assets/s4-sp03-i-product-data-product/deploy"
CSN_FILE = f"{BASE_DIR}/local-tables/raw-tables.csn.json"
OUT_DIR  = f"{BASE_DIR}/Corrected"
SPACE    = "PM_OBJSTORE"
OVERWRITE_ALL = os.environ.get("OVERWRITE_ALL", "").strip() == "1"
FAIL_DIR      = os.path.join(OUT_DIR, "Failed")

os.makedirs(OUT_DIR, exist_ok=True)
os.makedirs(FAIL_DIR, exist_ok=True)

# ── Payload builder ───────────────────────────────────────────────────────────
def build_payload(name: str, entity_def: dict) -> dict:
    """
    Returns a definitions dict with both the main entity and its _Delta
    companion, fully annotated for delta-enabled HDLFS / DELTA_LAKE tables.
    """
    delta_name = f"{name}_Delta"
    label      = entity_def.get("@EndUserText.label", name)
    quickinfo  = entity_def.get("@EndUserText.quickInfo", "")
    elements   = copy.deepcopy(entity_def.get("elements", {}))

    # ── _Delta companion: main columns + CDC control columns ─────────────────
    delta_elements = copy.deepcopy(elements)
    delta_elements["Change_Type"] = {
        "@EndUserText.label": "Change Type",
        "type": "cds.String",
        "length": 1,
        "notNull": True,
        "default": {"val": "I"},
    }
    delta_elements["Change_Date"] = {
        "@EndUserText.label": "Change Date",
        "type": "cds.Timestamp",
        "notNull": True,
        "default": {"func": "CURRENT_UTCTIMESTAMP"},
    }

    base_annotations = {
        "kind": "entity",
        "@EndUserText.label": label,
        "@EndUserText.quickInfo": quickinfo,
        "@ObjectModel.modelingPattern": {"#": "DATA_STRUCTURE"},
        "@ObjectModel.supportedCapabilities": [{"#": "DATA_STRUCTURE"}],
        "@DataWarehouse.persistence.hdlf.tableFormat": {"#": "DELTA_LAKE"},
        "@DataWarehouse.delta.changeDataCapture": {"#": "DELTA"},
        "@DataWarehouse.persistence.hdlf.enableDeletionVectors": False,
    }

    delta_entity = {
        **base_annotations,
        "@DataWarehouse.enclosingObject": name,
        "@cds.persistence.udf": True,
        "@Semantics.interval": [
            {
                "qualifier": "changeTime",
                "lowerBoundaryParameter": {"=": "FROM_CHANGE_TIME"},
                "lowerBoundaryIncluded": False,
                "upperBoundaryParameter": {"=": "TILL_CHANGE_TIME"},
                "upperBoundaryIncluded": True,
            }
        ],
        "@DataWarehouse.delta": {
            "type": {"#": "UPSERT"},
            "dateTimeElement": {"=": "Change_Date"},
            "modeElement": {"=": "Change_Type"},
        },
        "elements": delta_elements,
        "params": {
            "EXTRACTION_MODE": {
                "@EndUserText.label": "Extraction Mode",
                "type": "cds.String",
                "length": 10,
                "default": "FULL",
                "@DataWarehouse.bw.extractionMode": True,
            },
            "FROM_CHANGE_TIME": {
                "@EndUserText.label": "From Change Time",
                "type": "cds.Timestamp",
                "default": "0001-01-01 00:00:00",
            },
            "TILL_CHANGE_TIME": {
                "@EndUserText.label": "Till Change Time",
                "type": "cds.Timestamp",
                "default": "9999-12-31 23:59:59",
            },
        },
        "_meta": {"dependencies": {"folderAssignment": None}},
    }

    main_entity = {
        **base_annotations,
        "@DataWarehouse.delta": {
            "type": {"#": "ACTIVE"},
            "deltaFromEntities": [delta_name],
        },
        "elements": elements,
        "_meta": {"dependencies": {"folderAssignment": None}},
    }

    return {delta_name: delta_entity, name: main_entity}


# ── CLI helpers ───────────────────────────────────────────────────────────────
def entity_exists(name: str) -> bool:
    r = subprocess.run(
        ["datasphere", "objects", "local-tables", "read",
         "--space", SPACE, "--technical-name", name],
        capture_output=True, text=True,
    )
    return r.returncode == 0


def confirm_overwrite(name: str) -> bool:
    if OVERWRITE_ALL:
        return True
    try:
        ans = input(f"    ⚠️  '{name}' already exists. Overwrite? [y/N] ").strip().lower()
    except (EOFError, KeyboardInterrupt):
        print()
        return False
    return ans in ("y", "yes")


def deploy_entity(name: str, definitions: dict, exists: bool) -> subprocess.CompletedProcess:
    payload = {"definitions": definitions}
    with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
        json.dump(payload, f, indent=2)
        tmp_path = f.name
    try:
        if exists:
            cmd = ["datasphere", "objects", "local-tables", "update",
                   "--space", SPACE, "--technical-name", name,
                   "--file-path", tmp_path, "--deploy"]
        else:
            cmd = ["datasphere", "objects", "local-tables", "create",
                   "--space", SPACE, "--file-path", tmp_path, "--deploy"]
        return subprocess.run(cmd, capture_output=True, text=True)
    finally:
        os.unlink(tmp_path)


# ── Main ──────────────────────────────────────────────────────────────────────
with open(CSN_FILE) as f:
    csn = json.load(f)

entities = list(csn.get("definitions", {}).items())
total    = len(entities)

print(f"Source  : {CSN_FILE}")
print(f"Space   : {SPACE}")
print(f"Entities: {total}")
print(f"Output  : {OUT_DIR}")
if OVERWRITE_ALL:
    print("Mode    : OVERWRITE_ALL=1 (no prompts)")
print()

deployed = []
skipped  = []
failed   = []

for i, (name, entity_def) in enumerate(entities, 1):
    prefix = f"[{i:02d}/{total}] {name}"
    print(f"{prefix}", end=" ... ", flush=True)

    exists = entity_exists(name)
    tag    = "(exists)" if exists else "(new)"

    if exists:
        print(f"\n    {tag}", end=" ")
        if not confirm_overwrite(name):
            print(f"    → skipped")
            skipped.append(name)
            continue

    definitions = build_payload(name, entity_def)
    result      = deploy_entity(name, definitions, exists)

    if result.returncode == 0:
        # Persist corrected JSON
        out_file = os.path.join(OUT_DIR, f"{name}.json")
        with open(out_file, "w") as f:
            json.dump({"definitions": definitions}, f, indent=2)
        print(f"✓  → saved {name}.json")
        deployed.append(name)
    else:
        msg = (result.stdout or result.stderr or "unknown error").strip()
        print(f"✗  FAILED")
        print(f"    {msg}")
        fail_file = os.path.join(FAIL_DIR, f"{name}.json")
        with open(fail_file, "w") as f:
            json.dump({"definitions": definitions}, f, indent=2)
        print(f"    → payload saved to Failed/{name}.json")
        failed.append(name)

# ── Summary ───────────────────────────────────────────────────────────────────
print()
print("=" * 60)
print(f"  Results  ({total} entities)")
print("=" * 60)
print(f"  ✓ Deployed : {len(deployed)}")
print(f"  ⏭ Skipped  : {len(skipped)}")
print(f"  ✗ Failed   : {len(failed)}")
if failed:
    print(f"\n  Failed entities:")
    for n in failed:
        print(f"    • {n}")
print("=" * 60)

if failed:
    sys.exit(1)
