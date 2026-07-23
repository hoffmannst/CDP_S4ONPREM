#!/usr/bin/env python3
"""
deploy_all_replication_flows.py
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Deploys ALL 6 Replication Flows from replication-flows.json to Datasphere
space PM_OBJSTORE.

Inputs:
  replication-flows.json   – flow definitions (names, objects, key fields)
  raw-tables.csn.json      – entity column definitions for target _Delta tables

For each flow:
  1. Builds RF payload following confirmed working format (Option B from diag):
       { "replicationflows": {...}, "version": {...}, "meta": {...}, "$version" }
     Each flow contains one replicationTask per source-target object pair.
  2. Checks if the flow already exists in the tenant
     • New      → creates directly
     • Existing → prompts for overwrite confirmation; skips if declined
  3. On success → deploys + persists Corrected/<FLOW_NAME>.json

CLI command (confirmed 200 OK):
  datasphere objects replication-flows create --space PM_OBJSTORE --file-path <file> --deploy

Usage:
  python3 deploy_all_replication_flows.py

  # Auto-confirm all overwrites (non-interactive):
  OVERWRITE_ALL=1 python3 deploy_all_replication_flows.py
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"""
import copy
import json
import os
import subprocess
import sys
import tempfile

# ── Config ────────────────────────────────────────────────────────────────────
BASE_DIR     = "/Users/D026118/Desktop/CDP_S4ONPREM/assets/s4-sp03-i-product-data-product/deploy"
CSN_FILE     = f"{BASE_DIR}/local-tables/raw-tables.csn.json"
RF_SRC_FILE  = f"{BASE_DIR}/flows/replication-flows.json"
OUT_DIR      = f"{BASE_DIR}/Corrected"
SPACE        = "PM_OBJSTORE"
OVERWRITE_ALL = os.environ.get("OVERWRITE_ALL", "").strip() == "1"

SOURCE_CONNECTION  = "HE4"
SOURCE_TYPE        = "SAPS4HANAOP"
SOURCE_CONTAINER   = "/CDS_EXTRACTION"
TARGET_CONNECTION  = "DWC_HDLF"
TARGET_TYPE        = "HDL_FILES"

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
    """Collect all $DYNAMIC.string_N vtypes used across the element set."""
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


# ── Delta element set (main elements + CDC control columns) ───────────────────
def make_delta_elements(elements: dict) -> dict:
    delta = copy.deepcopy(elements)
    delta["Change_Type"] = {
        "@EndUserText.label": "Change Type",
        "type": "cds.String",
        "length": 1,
        "notNull": True,
        "default": {"val": "I"},
    }
    delta["Change_Date"] = {
        "@EndUserText.label": "Change Date",
        "type": "cds.Timestamp",
        "notNull": True,
        "default": {"func": "CURRENT_UTCTIMESTAMP"},
    }
    return delta


# ── Build one replicationTask for a single source-target object pair ──────────
def build_replication_task(
    task_idx: int,
    source_object: str,
    target_entity: str,
    key_fields: list,
    csn_definitions: dict,
) -> dict | None:
    """
    Returns a replicationTask dict or None if the target entity is not found
    in raw-tables.csn.json.
    """
    if target_entity not in csn_definitions:
        print(f"    WARNING: '{target_entity}' not found in raw-tables.csn.json — skipping object")
        return None

    entity_def     = csn_definitions[target_entity]
    elements       = entity_def.get("elements", {})
    label          = entity_def.get("@EndUserText.label", target_entity)
    delta_name     = f"{target_entity}_Delta"
    delta_elements = make_delta_elements(elements)

    source_cols = [to_rf_col(n, d, key=(n in key_fields)) for n, d in elements.items()]
    source_keys = [c["name"] for c in source_cols if c.get("key")]
    target_cols = [to_rf_col(n, d, key=(n in key_fields)) for n, d in delta_elements.items()]

    return {
        "name": f"replicationtask{task_idx}",
        "loadType": "REPLICATE",
        "priority": 50,
        "truncate": False,
        "sourceObject": {
            "name": source_object,
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


# ── Collect all $DYNAMIC vtypes across all tasks in a flow ────────────────────
def collect_vtypes(tasks: list, csn_definitions: dict) -> dict:
    all_vtypes = {}
    for task in tasks:
        target_name  = task["targetObject"]["name"]
        entity_name  = target_name.replace("_Delta", "")
        if entity_name in csn_definitions:
            elements = csn_definitions[entity_name].get("elements", {})
            all_vtypes.update(build_vtypes(make_delta_elements(elements)))
    return all_vtypes


# ── Build the full RF payload for one flow ────────────────────────────────────
def build_rf_payload(
    flow_name: str,
    flow_description: str,
    tasks: list,
    vtypes: dict,
    csn_definitions: dict,
) -> dict:
    # Build targets map: { "<delta_name>": { "elements": { col: {} ... } } }
    targets = {}
    for task in tasks:
        delta_name = task["targetObject"]["name"]
        targets[delta_name] = {
            "elements": {c["name"]: {} for c in task["targetObject"]["definition"]["columns"]}
        }

    return {
        "replicationflows": {
            flow_name: {
                "kind": "sap.dis.replicationflow",
                "@EndUserText.label": flow_name,
                "contents": {
                    "description": flow_description,
                    "sourceSystem": [
                        {
                            "connectionId": SOURCE_CONNECTION,
                            "connectionType": SOURCE_TYPE,
                            "container": SOURCE_CONTAINER,
                            "maxConnections": 10,
                            "metadata": {},
                        }
                    ],
                    "targetSystem": [
                        {
                            "connectionId": TARGET_CONNECTION,
                            "connectionType": TARGET_TYPE,
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
                    "replicationTasks": tasks,
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
                "targets": targets,
                "connections": {SOURCE_CONNECTION: {}},
            }
        },
        "version": {"csn": "1.0"},
        "meta": {"creator": "CDS Compiler v1.19.2"},
        "$version": "1.0",
    }


# ── CLI helpers ───────────────────────────────────────────────────────────────
def flow_exists(name: str) -> bool:
    r = subprocess.run(
        ["datasphere", "objects", "replication-flows", "read",
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


def deploy_flow(flow_name: str, payload: dict, exists: bool) -> subprocess.CompletedProcess:
    with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
        json.dump(payload, f, indent=2)
        tmp_path = f.name
    try:
        if exists:
            cmd = ["datasphere", "objects", "replication-flows", "update",
                   "--space", SPACE, "--technical-name", flow_name,
                   "--file-path", tmp_path, "--deploy"]
        else:
            cmd = ["datasphere", "objects", "replication-flows", "create",
                   "--space", SPACE, "--file-path", tmp_path, "--deploy"]
        return subprocess.run(cmd, capture_output=True, text=True)
    finally:
        os.unlink(tmp_path)


# ── Main ──────────────────────────────────────────────────────────────────────
with open(CSN_FILE) as f:
    csn = json.load(f)
csn_defs = csn.get("definitions", {})

with open(RF_SRC_FILE) as f:
    rf_src = json.load(f)
flows = rf_src.get("replicationFlows", [])

print(f"Source CSN : {CSN_FILE}")
print(f"Source RF  : {RF_SRC_FILE}")
print(f"Space      : {SPACE}")
print(f"Flows      : {len(flows)}")
if OVERWRITE_ALL:
    print("Mode       : OVERWRITE_ALL=1 (no prompts)")
print()

deployed = []
skipped  = []
failed   = []

for i, flow_def in enumerate(flows, 1):
    flow_name = flow_def.get("name", f"RF_{i:02d}")
    flow_desc = flow_def.get("description", flow_name)
    objects   = flow_def.get("objects", [])

    print(f"[{i:02d}/{len(flows)}] {flow_name}  ({len(objects)} object(s))")

    # Build replication tasks
    tasks = []
    for j, obj in enumerate(objects, 1):
        source_obj    = obj.get("sourceObject", "")
        target_entity = obj.get("targetObject", "")
        key_fields    = obj.get("keyFields", [])
        task = build_replication_task(j, source_obj, target_entity, key_fields, csn_defs)
        if task:
            tasks.append(task)

    if not tasks:
        print(f"    ✗  No valid tasks — skipping (check target entity names in CSN)\n")
        failed.append(flow_name)
        continue

    vtypes  = collect_vtypes(tasks, csn_defs)
    payload = build_rf_payload(flow_name, flow_desc, tasks, vtypes, csn_defs)

    exists = flow_exists(flow_name)
    if exists:
        print(f"    (exists)", end=" ")
        if not confirm_overwrite(flow_name):
            print(f"    → skipped\n")
            skipped.append(flow_name)
            continue

    result = deploy_flow(flow_name, payload, exists)

    if result.returncode == 0:
        out_file = os.path.join(OUT_DIR, f"{flow_name}.json")
        with open(out_file, "w") as f:
            json.dump(payload, f, indent=2)
        print(f"    ✓  deployed + saved {flow_name}.json")
        deployed.append(flow_name)
    else:
        msg = (result.stdout or result.stderr or "unknown error").strip()
        print(f"    ✗  FAILED")
        print(f"       {msg}")
        failed.append(flow_name)
    print()

# ── Summary ───────────────────────────────────────────────────────────────────
print("=" * 60)
print(f"  Results  ({len(flows)} flows)")
print("=" * 60)
print(f"  ✓ Deployed : {len(deployed)}")
print(f"  ⏭ Skipped  : {len(skipped)}")
print(f"  ✗ Failed   : {len(failed)}")
if failed:
    print(f"\n  Failed flows:")
    for n in failed:
        print(f"    • {n}")
print("=" * 60)

if failed:
    sys.exit(1)
