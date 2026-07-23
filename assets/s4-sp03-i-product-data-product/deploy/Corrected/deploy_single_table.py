#!/usr/bin/env python3
"""
deploy_single_table.py
Deploys a single RAW_* entity from raw-tables.csn.json with full delta-enabled structure.

Change ENTITY_NAME below to target a different entity.

What the script does per entity:
  - Applies mandatory HDLFS annotations to the main entity
  - Generates the companion <NAME>_Delta entity (required for delta feature)
  - Checks whether the entity already exists in the space
      - New entity    → objects local-tables create
      - Existing      → asks for overwrite confirmation, uses objects local-tables update
  - On success, persists the corrected payload to deploy/Corrected/<NAME>.json
"""
import copy
import json
import os
import subprocess
import sys
import tempfile

CSN_FILE    = "/Users/D026118/Desktop/CDP_S4ONPREM/assets/s4-sp03-i-product-data-product/deploy/local-tables/raw-tables.csn.json"
SPACE       = "PM_OBJSTORE"
OUT_DIR     = "/Users/D026118/Desktop/CDP_S4ONPREM/assets/s4-sp03-i-product-data-product/deploy/Corrected"
ENTITY_NAME = "RAW_I_PRODUCTDESCRIPTION"   # ← change to target a different entity

os.makedirs(OUT_DIR, exist_ok=True)


# ─────────────────────────────────────────────────────────────────────────────
# Payload builder
# ─────────────────────────────────────────────────────────────────────────────

def build_delta_companion(name: str, main_def: dict) -> dict:
    """Build the <NAME>_Delta companion entity required for delta-enabled tables."""
    delta_name = f"{name}_Delta"
    elements   = copy.deepcopy(main_def.get("elements", {}))

    # Add the two CDC control columns
    elements["Change_Type"] = {
        "@EndUserText.label": "Change Type",
        "type": "cds.String",
        "length": 1,
        "notNull": True,
        "default": {"val": "I"}
    }
    elements["Change_Date"] = {
        "@EndUserText.label": "Change Date",
        "type": "cds.Timestamp",
        "notNull": True,
        "default": {"func": "CURRENT_UTCTIMESTAMP"}
    }

    return {
        "kind": "entity",
        "@EndUserText.label": main_def.get("@EndUserText.label", name),
        "@EndUserText.quickInfo": main_def.get("@EndUserText.quickInfo", ""),
        "@ObjectModel.modelingPattern": {"#": "DATA_STRUCTURE"},
        "@ObjectModel.supportedCapabilities": [{"#": "DATA_STRUCTURE"}],
        "@DataWarehouse.persistence.hdlf.tableFormat": {"#": "DELTA_LAKE"},
        "@DataWarehouse.delta.changeDataCapture": {"#": "DELTA"},
        "@DataWarehouse.persistence.hdlf.enableDeletionVectors": False,
        "@DataWarehouse.enclosingObject": name,
        "@cds.persistence.udf": True,
        "@Semantics.interval": [
            {
                "qualifier": "changeTime",
                "lowerBoundaryParameter": {"=": "FROM_CHANGE_TIME"},
                "lowerBoundaryIncluded": False,
                "upperBoundaryParameter": {"=": "TILL_CHANGE_TIME"},
                "upperBoundaryIncluded": True
            }
        ],
        "@DataWarehouse.delta": {
            "type": {"#": "UPSERT"},
            "dateTimeElement": {"=": "Change_Date"},
            "modeElement":     {"=": "Change_Type"}
        },
        "elements": elements,
        "params": {
            "EXTRACTION_MODE": {
                "@EndUserText.label": "Extraction Mode",
                "type": "cds.String",
                "length": 10,
                "default": "FULL",
                "@DataWarehouse.bw.extractionMode": True
            },
            "FROM_CHANGE_TIME": {
                "@EndUserText.label": "From Change Time",
                "type": "cds.Timestamp",
                "default": "0001-01-01 00:00:00"
            },
            "TILL_CHANGE_TIME": {
                "@EndUserText.label": "Till Change Time",
                "type": "cds.Timestamp",
                "default": "9999-12-31 23:59:59"
            }
        },
        "_meta": {"dependencies": {"folderAssignment": None}}
    }


def build_payload(name: str, raw_def: dict) -> dict:
    """
    Return a definitions dict with the corrected main entity + _Delta companion.
    All HDLFS/delta annotations are injected; @ObjectModel.modelingPattern is
    forced to DATA_STRUCTURE regardless of what the source CSN contains.
    """
    main = copy.deepcopy(raw_def)
    delta_name = f"{name}_Delta"

    # ── Mandatory annotations on the main entity ──────────────────────────────
    main["@ObjectModel.modelingPattern"]       = {"#": "DATA_STRUCTURE"}
    main["@ObjectModel.supportedCapabilities"] = [{"#": "DATA_STRUCTURE"}]
    main["@DataWarehouse.persistence.hdlf.tableFormat"]         = {"#": "DELTA_LAKE"}
    main["@DataWarehouse.delta.changeDataCapture"]               = {"#": "DELTA"}
    main["@DataWarehouse.persistence.hdlf.enableDeletionVectors"] = False
    main["@DataWarehouse.delta"] = {
        "type": {"#": "ACTIVE"},
        "deltaFromEntities": [delta_name]
    }
    main["_meta"] = {"dependencies": {"folderAssignment": None}}

    # ── Explicit key:false on non-key elements ─────────────────────────────────
    for col_def in main.get("elements", {}).values():
        if "key" not in col_def:
            col_def["key"] = False

    return {
        name: main,
        delta_name: build_delta_companion(name, main)
    }


# ─────────────────────────────────────────────────────────────────────────────
# CLI helpers
# ─────────────────────────────────────────────────────────────────────────────

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


# ─────────────────────────────────────────────────────────────────────────────
# Main
# ─────────────────────────────────────────────────────────────────────────────

with open(CSN_FILE) as f:
    csn = json.load(f)

if ENTITY_NAME not in csn["definitions"]:
    print(f"ERROR: '{ENTITY_NAME}' not found in {CSN_FILE}")
    print(f"Available: {', '.join(csn['definitions'].keys())}")
    sys.exit(1)

definitions = build_payload(ENTITY_NAME, csn["definitions"][ENTITY_NAME])
payload     = {"definitions": definitions}

print(f"Entity  : {ENTITY_NAME}")
print(f"Space   : {SPACE}")
print(f"Payload : main + {ENTITY_NAME}_Delta\n")

exists = entity_exists(ENTITY_NAME)

if exists:
    print(f"'{ENTITY_NAME}' already exists in '{SPACE}'.")
    if not confirm_overwrite(ENTITY_NAME):
        print("Skipped.")
        sys.exit(0)
    cli_verb = ["objects", "local-tables", "update",
                "--space", SPACE,
                "--technical-name", ENTITY_NAME,
                "--file-path", None,   # filled in below
                "--deploy"]
else:
    print(f"'{ENTITY_NAME}' does not exist yet — will create.")
    cli_verb = ["objects", "local-tables", "create",
                "--space", SPACE,
                "--file-path", None,
                "--deploy"]

with tempfile.TemporaryDirectory() as tmp:
    tmp_file = os.path.join(tmp, f"{ENTITY_NAME}.json")
    with open(tmp_file, "w") as f:
        json.dump(payload, f, indent=2)

    # Inject the actual tmp_file path
    cmd = ["datasphere"] + [tmp_file if arg is None else arg for arg in cli_verb]

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
