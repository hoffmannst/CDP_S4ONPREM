#!/usr/bin/env python3
"""
deploy_rf_productdescription.py
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Builds and deploys a Datasphere Replication Flow:
  Source : I_PRODUCTDESCRIPTION  (S/4HANA HE4 — CDS extraction)
  Target : RAW_I_PRODUCTDESCRIPTION_Delta  (HDLFS PM_OBJSTORE — DWC_HDLF)

Correct API: POST /dwaas-core/api/v1/spaces/{space}/replicationflows
Correct CLI: datasphere objects replication-flows create --space --file-path
Correct payload format (diagnostic confirmed):
  { "replicationflows": {...}, "version": {...}, "meta": {...}, "$version" }
  ← NO "definitions" block (local tables deployed separately)

Inputs
  raw-tables.csn.json       – entity column definitions
  replication-flows.json    – key-field reference per source object

Output (on success)
  deploy/Corrected/RF_RAW_I_PRODUCTDESCRIPTION.json

Usage
  python3 deploy_rf_productdescription.py
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"""
import copy
import json
import os
import subprocess
import sys
import tempfile

# ── Config ────────────────────────────────────────────────────────────────────
BASE_DIR      = "/Users/D026118/Desktop/CDP_S4ONPREM/assets/s4-sp03-i-product-data-product/deploy"
CSN_FILE      = f"{BASE_DIR}/local-tables/raw-tables.csn.json"
RF_SRC_FILE   = f"{BASE_DIR}/flows/replication-flows.json"
OUT_DIR       = f"{BASE_DIR}/Corrected"

SPACE         = "PM_OBJSTORE"
SOURCE_OBJECT = "I_PRODUCTDESCRIPTION"
TARGET_ENTITY = "RAW_I_PRODUCTDESCRIPTION"
FLOW_NAME     = "RF_RAW_I_PRODUCTDESCRIPTION"

os.makedirs(OUT_DIR, exist_ok=True)


# ── CDS type → vflow vtype-ID ─────────────────────────────────────────────────
def cds_to_vtype(col_def: dict) -> str:
    t = col_def.get("type", "cds.String")
    n = col_def.get("length")
    if t == "cds.String" and n:
        return f"$DYNAMIC.string_{n}"
    if t == "cds.Date":
        return "com.sap.core.date"
    if t == "cds.Timestamp":
        return "com.sap.core.timestamp"
    if t == "cds.Decimal":
        return f"com.sap.core.decimal({col_def.get('precision', 15)},{col_def.get('scale', 2)})"
    if t == "cds.Integer":
        return "com.sap.core.int32"
    if t == "cds.Boolean":
        return "com.sap.core.boolean"
    if t == "cds.LargeString":
        return "com.sap.core.clob"
    return "com.sap.core.string"


def build_vtypes(elements: dict) -> dict:
    out = {}
    for col in elements.values():
        vt = cds_to_vtype(col)
        if vt.startswith("$DYNAMIC.string_"):
            n   = vt.split("_")[-1]
            key = f"string_{n}"
            out[key] = {
                "name": key,
                "description": f"String({n})",
                "vflow.type": "scalar",
                "template": "string",
                "value.length": int(n),
            }
    return out


def to_rf_col(name: str, col_def: dict, key: bool = False) -> dict:
    entry = {
        "name": name,
        "vflow.type": "scalar",
        "vtype-ID": cds_to_vtype(col_def),
        "businessName": col_def.get("@EndUserText.label", name),
        "metadata": {},
    }
    if key:
        entry["key"] = True
    return entry


# ── Load inputs ───────────────────────────────────────────────────────────────
with open(CSN_FILE) as f:
    csn = json.load(f)

with open(RF_SRC_FILE) as f:
    rf_src = json.load(f)

if TARGET_ENTITY not in csn["definitions"]:
    print(f"ERROR: '{TARGET_ENTITY}' not found in {CSN_FILE}")
    print(f"Available: {', '.join(csn['definitions'].keys())}")
    sys.exit(1)

entity_def = csn["definitions"][TARGET_ENTITY]
elements   = entity_def.get("elements", {})
label      = entity_def.get("@EndUserText.label", TARGET_ENTITY)
quickinfo  = entity_def.get("@EndUserText.quickInfo", "")

# Key fields from replication-flows.json
key_fields: list[str] = []
for flow in rf_src.get("replicationFlows", []):
    for obj in flow.get("objects", []):
        if obj.get("sourceObject") == SOURCE_OBJECT:
            key_fields = obj.get("keyFields", [])
            break
    if key_fields:
        break

if not key_fields:
    print(f"WARNING: '{SOURCE_OBJECT}' not in replication-flows.json — defaulting to MANDT/MATNR/SPRAS")
    key_fields = ["MANDT", "MATNR", "SPRAS"]

print(f"Source  : {SOURCE_OBJECT}")
print(f"Target  : {TARGET_ENTITY}_Delta")
print(f"Keys    : {key_fields}")
print(f"Flow    : {FLOW_NAME}\n")

# ── Build delta element set ───────────────────────────────────────────────────
delta_name     = f"{TARGET_ENTITY}_Delta"
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

source_cols = [to_rf_col(n, d, key=(n in key_fields)) for n, d in elements.items()]
source_keys = [c["name"] for c in source_cols if c.get("key")]
target_cols = [to_rf_col(n, d, key=(n in key_fields)) for n, d in delta_elements.items()]
vtypes      = build_vtypes(delta_elements)

# ── RF-only payload (diagnostic confirmed this is the correct format) ─────────
rf_payload = {
    "replicationflows": {
        FLOW_NAME: {
            "kind": "sap.dis.replicationflow",
            "@EndUserText.label": FLOW_NAME,
            "contents": {
                "description": FLOW_NAME,
                "sourceSystem": [
                    {
                        "connectionId": "HE4",
                        "connectionType": "SAPS4HANAOP",
                        "container": "/CDS_EXTRACTION",
                        "maxConnections": 10,
                        "metadata": {},
                    }
                ],
                "targetSystem": [
                    {
                        "connectionId": "DWC_HDLF",
                        "connectionType": "HDL_FILES",
                        "container": "",
                        "maxConnections": 10,
                        "metadata": {
                            "connectionMetaschema": {"sources": ["SAP"]}
                        },
                        "properties": {
                            "compression": "SNAPPY",
                            "format": "PARQUET",
                            "groupDeltaFilesBy": "NONE",
                            "com.sap.rms.write.forceDecfloatsToTargetValueRange": "false",
                            "objectstore.write.useDuplicateSuppressionInitialLoad": "false",
                            "objectstore.write.parquet.compatibilityMode": "SPARK",
                            "objectstore.write.createLargePartFiles": "false",
                        },
                    }
                ],
                "vTypes": {"scalar": vtypes},
                "replicationTasks": [
                    {
                        "name": "replicationtask1",
                        "loadType": "REPLICATE",
                        "priority": 50,
                        "truncate": False,
                        "sourceObject": {
                            "name": SOURCE_OBJECT,
                            "definition": {
                                "columns": source_cols,
                                "keys": source_keys,
                            },
                            "metadata": {
                                "type": "tabular",
                                "invalidColumns": ["/1DH/OPERATION"],
                            },
                            "businessName": label,
                        },
                        "targetObject": {
                            "name": delta_name,
                            "definition": {"columns": target_cols},
                            "metadata": {"isNew": False},
                            "properties": {
                                "com.sap.datasuite.cdc.mode.column": "Change_Type",
                                "com.sap.datasuite.cdc.timestamp.column": "Change_Date",
                                "com.sap.datasuite.tableCategory": "DELTA",
                            },
                            "businessName": label,
                        },
                        "deltaCheckInterval": 3600,
                    }
                ],
                "replicationTaskSetting": {
                    "globalDeltaPartitionValue": 1,
                    "hasSkipMappingCapability": True,
                },
                "replicationFlowSetting": {
                    "ABAPcontentTypeDisabled": False,
                    "ABAPcontentType": "Native Type",
                    "isAutoMergeEnabledForTarget": False,
                },
                "deltaLoadTrigger": "ON_DELTA_INTERVAL",
            },
            "sources": {},
            "targets": {
                delta_name: {
                    "elements": {c["name"]: {} for c in target_cols}
                }
            },
            "connections": {"HE4": {}},
        }
    },
    "version": {"csn": "1.0"},
    "meta": {"creator": "CDS Compiler v1.19.2"},
    "$version": "1.0",
}


# ── Existence check + overwrite confirmation ──────────────────────────────────
def flow_exists(name: str) -> bool:
    r = subprocess.run(
        ["datasphere", "objects", "replication-flows", "read",
         "--space", SPACE, "--technical-name", name],
        capture_output=True, text=True,
    )
    return r.returncode == 0


def confirm_overwrite(name: str) -> bool:
    try:
        ans = input(f"  ⚠️  '{name}' already exists in '{SPACE}'. Overwrite? [y/N] ").strip().lower()
    except (EOFError, KeyboardInterrupt):
        print()
        return False
    return ans in ("y", "yes")


exists = flow_exists(FLOW_NAME)
if exists:
    print(f"'{FLOW_NAME}' already exists in '{SPACE}'.")
    if not confirm_overwrite(FLOW_NAME):
        print("Skipped.")
        sys.exit(0)
    action = ["objects", "replication-flows", "update",
              "--space", SPACE, "--technical-name", FLOW_NAME,
              "--file-path", None, "--deploy"]
else:
    print(f"'{FLOW_NAME}' does not exist yet — will create.")
    action = ["objects", "replication-flows", "create",
              "--space", SPACE, "--file-path", None, "--deploy"]


# ── Deploy ────────────────────────────────────────────────────────────────────
with tempfile.TemporaryDirectory() as tmp:
    tmp_file = os.path.join(tmp, f"{FLOW_NAME}.json")
    with open(tmp_file, "w") as f:
        json.dump(rf_payload, f, indent=2)

    cmd = ["datasphere"] + [tmp_file if a is None else a for a in action]
    print(f"\nRunning: {' '.join(cmd)}\n")
    result = subprocess.run(cmd, capture_output=True, text=True)

    print("=== stdout ===")
    print(result.stdout or "(empty)")
    if result.stderr:
        print("=== stderr ===")
        print(result.stderr)

    if result.returncode == 0:
        out_file = os.path.join(OUT_DIR, f"{FLOW_NAME}.json")
        with open(out_file, "w") as f:
            json.dump(rf_payload, f, indent=2)
        print(f"\n✓  Deployed and saved to Corrected/{FLOW_NAME}.json")
    else:
        print(f"\n✗  Deployment failed (exit code {result.returncode})")
        sys.exit(1)
