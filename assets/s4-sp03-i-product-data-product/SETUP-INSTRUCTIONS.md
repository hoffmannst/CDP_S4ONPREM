# Setup Instructions — S/4_SP03_I_PRODUCT Custom Data Product

**Version:** 1.0.0  
**Target Audience:** SAP Datasphere Administrator, S/4HANA Basis / Integration Consultant, BDC Platform Administrator  
**Source System:** S/4HANA on-premise SP03 (Release 2023/02/00)  
**Target Platform:** SAP Datasphere (HDLFS space) + SAP Business Data Cloud

---

## Overview

This guide walks through the complete setup of the `S/4_SP03_I_PRODUCT` custom data product. The setup has seven stages:

```
Stage 1: Prerequisites
Stage 2: HDLFS Raw Zone — Create Tables
Stage 3: Replication Flows — Extract from S/4HANA to HDLFS Raw Zone
Stage 4: Transformation Flows — HDLFS Raw to HDLFS Refined
Stage 5: Datasphere Semantic Layer — Dimension Views & Analytical Dataset
Stage 6: DPD Registration in BDC
Stage 7: End-to-End Validation
```

Estimated total setup time: **2–4 days** depending on S/4HANA connectivity readiness and data volumes.

---

## Stage 1: Prerequisites

### 1.1 Verify Cloud Connector

1. Log in to SAP BTP Cockpit → your subaccount → **Connectivity → Cloud Connectors**.
2. Confirm the Cloud Connector shows **Connected** with Location ID noted.
3. Confirm the S/4HANA SP03 system is mapped with protocol `RFC`, virtual host `S4H-SP03-RFC`, virtual port `3300`.

> If Cloud Connector is not yet installed, follow the [SAP Cloud Connector Installation Guide](https://help.sap.com/docs/connectivity/sap-btp-connectivity-cf/installation).

### 1.2 Activate ODP Extractors in S/4HANA

On the S/4HANA SP03 system:

1. Log in with a user who has Basis authorisations.
2. Run transaction `RODPS_REPL_TEST` for each of the 21 CDS views listed in `entity-catalogue.md`.
   - ODP Context: `CDS_EXTRACTION`
   - Click **Execute** and verify no errors.
3. Ensure the RFC user has the authorisations described in `source-connection-config.md` (section: Authorisation Check).

### 1.3 Provision HDLFS Space in Datasphere

1. In Datasphere → **System → Administration → HANA Database**.
2. Provision the HDLFS space named `PRODUCT_MASTER_HDLFS` with at least **50 GB** initial storage.
3. Note the HDLFS connection string for use in Replication Flow configuration.

### 1.4 Create RFC Connection in Datasphere

Follow `source-connection-config.md` (Stage 3 instructions) to create connection `HE4` and run a successful test.

### 1.5 Link BDC Tenant to Datasphere

Confirm in BDC → **Settings** that the Datasphere tenant is linked. If not, follow the BDC onboarding guide for tenant linkage before proceeding to Stage 6.

---

## Stage 2: HDLFS Raw Zone — Create Tables

Create the folder/table structure in the HDLFS space before activating replication flows.

### 2.1 Create Raw Zone Folder Structure

In Datasphere → **Data Builder → Files (HDLFS)**, create the following folder hierarchy under `PRODUCT_MASTER_HDLFS`:

```
product-master/
└── raw/
    ├── I_PRODUCT/
    ├── I_PRODUCTDESCRIPTION/
    ├── I_PRODUCTUNITSOFMEASURE/
    ├── I_PRODUCTPLANT/
    ├── I_PRODUCTSTORAGELOC/
    ├── I_PRODUCTVALUATION/
    ├── I_PRODUCTSALESDELIVERY/
    ├── I_PRODUCTPROCUREMENT/
    ├── I_PRODUCTBASICTEXTS/
    ├── I_PRODUCTINSPECTIONTEXTS/
    ├── I_PRODUCTQUALITYMANAGEMENT/
    ├── I_PRODUCTPLANTMRPAREA/
    ├── I_PRODUCTPLANTCOSTING/
    ├── I_PRODUCTPLANTFORECAST/
    ├── I_PRODPLNTINTERNATIONALTRADE/
    ├── I_PRODUCTPLANTPROCUREMENT/
    ├── I_PRODUCTPLANTQUALITYMANAGEMENT/
    ├── I_PRODUCTPLANTSALES/
    ├── I_PRODUCTPLANTSTORAGE/
    ├── I_PRODUCTPLANTWORKSCHEDULING/
    └── I_PRODUCTMLACCOUNT/
```

### 2.2 Create Refined Zone Folder Structure

Create the same structure under `product-master/refined/` using the entity names:
```
product-master/
└── refined/
    ├── PRODUCT/
    ├── PRODUCTTEXT/
    ├── PRODUCTUNITSOFMEASURE/
    ... (all 22 entity folders — see hdlfs-config.md for full list)
```

### 2.3 Configure Partition Settings

For each raw-zone folder:
- **Primary partition:** `MANDT`
- **Secondary partition:** `EXTRACTION_DATE` (format `YYYY-MM-DD`)

> Verify this is configured in the HDLFS space settings before activating replication flows.

---

## Stage 3: Replication Flows — Extract from S/4HANA to HDLFS Raw Zone

Create and activate all 6 Replication Flows. See `replication-flows.md` for full configuration details.

### 3.1 Create RF-01 (Product Core)

1. In Datasphere → **Data Integration → Replication Flows → + New Replication Flow**.
2. Name: `RF_S4SP03_PRODUCT_CORE`
3. Source: select connection `HE4`, ODP context `CDS_EXTRACTION`
4. Add the following source objects and map to targets:

   | Source ODP Object | Target HDLFS Table |
   |------------------|-------------------|
   | `I_PRODUCT` | `RAW_I_PRODUCT` (path: `product-master/raw/I_PRODUCT/`) |
   | `I_PRODUCTDESCRIPTION` | `RAW_I_PRODUCTDESCRIPTION` |
   | `I_PRODUCTUNITSOFMEASURE` | `RAW_I_PRODUCTUNITSOFMEASURE` |
   | `I_PRODUCTVALUATION` | `RAW_I_PRODUCTVALUATION` |
   | `I_PRODUCTMLACCOUNT` | `RAW_I_PRODUCTMLACCOUNT` |

> **Note:** `I_ProductProcurement` (header-level, no plant key), `I_ProductBasicTexts`, `I_ProductInspectionTexts`, `I_ProductQualityManagement`, `I_ProdPlntInternationalTrade`, and `I_ProductPlantQualityManagement` are included in RF-02 and RF-06 respectively. Verify exact ODP view names against your S/4HANA release using `RODPS_REPL_TEST`.

5. Set load type: **Initial and Delta**
6. Set partition key: `MANDT`
7. Save and **Run** (initial load).
8. Monitor in **Data Integration Monitor** until initial load status = **Completed**.
9. Activate delta replication.

### 3.2 Create RF-02 through RF-06

Repeat the steps above for each remaining flow. Use the configurations in `replication-flows.md`:
- RF-02: Sales & Purchasing (2 entities)
- RF-03: Plant Core (2 entities)
- RF-04: Plant Extensions 1 (4 entities)
- RF-05: Plant Extensions 2 (5 entities)
- RF-06: Texts & Quality (3 entities)

### 3.3 Validate Initial Loads

For each flow:
1. In **Data Integration Monitor → Replication Flows**, open the flow.
2. Confirm **Status = Completed** and **Records Failed = 0**.
3. Navigate to the HDLFS raw-zone folder and verify files are present with non-zero size.
4. Spot-check row counts against S/4HANA source tables (see `replication-flows.md` per-flow validation section).

> **Activation sequence:** Start RF-01 first. After RF-01 initial load completes, start RF-02 and RF-06 in parallel. After RF-03 initial load completes, start RF-04 and RF-05 in parallel.

---

## Stage 4: Transformation Flows — HDLFS Raw to HDLFS Refined

Create and run all 22 Transformation Flows. See `transformation-flows.md` for field-level transformation details.

### 4.1 General Flow Structure (repeat for each entity)

1. In Datasphere → **Data Builder → New Transformation Flow**.
2. Source: select the corresponding `RAW_*` HDLFS table.
3. Target: select (or create) the corresponding `REF_*` HDLFS table in the refined zone.
4. Apply the transformation rules from `transformation-flows.md` for the specific entity.
5. Add the `EXTRACTION_TIMESTAMP TIMESTAMP DEFAULT CURRENT_TIMESTAMP` column to all output tables.
6. Save and **Run**.
7. Monitor until status = **Completed**, **Records Failed = 0**.

### 4.2 Common Transformations to Apply in Every Flow

Apply these to every Transformation Flow before entity-specific rules:
- `RTRIM` on all `CHAR`/`NCHAR` fields
- Cast `MANDT` to `NVARCHAR(3)` — exclude from output if single-client
- Cast SAP `DATS` date fields (`ERSDA`, `LAEDA`, etc.) to `DATE`
- Add `EXTRACTION_TIMESTAMP`

### 4.3 Execute Flows in Order

1. Run `TF_PRODUCT` first.
2. Run all direct-association flows in parallel: `TF_PRODUCTTEXT`, `TF_PRODUCTUNITSOFMEASURE`, `TF_PRODUCTVALUATION`, `TF_PRODUCTMLACCOUNT`, `TF_PRODUCTSALESDELIVERY`, `TF_PRODUCTPURCHASING`, `TF_PRODUCTBASICTEXT`, `TF_PRODUCTINSPECTIONTEXT`, `TF_PRODUCTQUALITYMGMT`.
3. Run `TF_PRODUCTPLANT`.
4. Run all plant sub-entity flows in parallel (TF-12 to TF-20): `TF_PRODUCTSTORAGELOC`, `TF_PRODUCTPLANTMRPAREA`, `TF_PRODUCTPLANTCOSTING`, `TF_PRODUCTPLANTFORECAST`, `TF_PRODPLNTINTERNATIONALTRADE`, `TF_PRODUCTPLANTPROCUREMENT`, `TF_PRODUCTPLANTQUALITYMANAGEMENT`, `TF_PRODUCTPLANTSALES`, `TF_PRODUCTPLANTSTORAGE`, `TF_PRODUCTPLANTWORKSCHEDULING`.

### 4.4 Validate Refined Zone

Run these checks after all 22 flows complete:
- Row counts: each `REF_*` table row count equals the corresponding `RAW_*` table row count.
- Null key check: no `NULL` in any key field.
- Date check: no `0001-01-01` or `9999-12-31` SAP default dates leaking through.
- Language check: `REF_PRODUCTTEXT.Language` values are ISO 639-1 (e.g. `EN`, `DE`).
- Amount check: `REF_PRODUCTVALUATION.StandardPrice` is `DECIMAL(23,2)`.

---

## Stage 5: Datasphere Semantic Layer — Dimension Views & Analytical Dataset

See `datasphere-models.md` for the complete column, key, and association definitions.

### 5.1 Create Dimension Views

For each of the 22 entities:

1. In Datasphere → **Data Builder → New Graphical View**.
2. Source: drag the corresponding `REF_*` HDLFS table.
3. Set **Semantic Usage = Dimension**.
4. Define the key field(s) as specified in `datasphere-models.md`.
5. Apply business labels to each column from the label mapping table in `datasphere-models.md` (DIM_PRODUCT section).
6. Define associations to related Dimension views (see association declarations per dimension in `datasphere-models.md`).
7. Save and **Deploy**.
8. Verify deployment status = **Deployed (no errors)**.

### 5.2 Create Central Analytical Dataset

1. In Datasphere → **Data Builder → New Graphical View**.
2. Name: `ProductAnalyticalDataset`
3. Source: drag `DIM_PRODUCT` as the central node.
4. Add all 21 associated Dimension views as spokes (drag-and-drop; Datasphere will detect associations).
5. Set **Semantic Usage = Analytical Dataset**.
6. Set label: `Product Master — S/4HANA SP03`.
7. Save and **Deploy**.

### 5.3 Run Validation Query

In Datasphere → **Data Viewer**, run:

```sql
SELECT
  p.Product,
  pt.ProductDescription,
  pp.Plant,
  ps.StorageLocation,
  pv.StandardPrice,
  pv.Currency
FROM ProductAnalyticalDataset p
LEFT JOIN DIM_PRODUCTTEXT pt ON p.Product = pt.Product AND pt.Language = 'EN'
LEFT JOIN DIM_PRODUCTPLANT pp ON p.Product = pp.Product
LEFT JOIN DIM_PRODUCTSTORAGELOC ps ON pp.Product = ps.Product AND pp.Plant = ps.Plant
LEFT JOIN DIM_PRODUCTVALUATION pv ON p.Product = pv.Product
LIMIT 10
```

Expected: 10 rows with populated `ProductDescription`, `Plant`, and `StandardPrice`.

---

## Stage 6: DPD Registration in BDC

See `bdc-registration.md` for the full step-by-step registration procedure.

**Summary:**
1. Log in to BDC → **Data Products → Manage Data Products → + Register Custom Data Product**.
2. Upload `S4SP03IProduct.dpd`.
3. Resolve any validation errors.
4. Confirm all 21 output ports and 20 associations.
5. Set status **Active** and register.
6. Record the BDC data product URL in `bdc-registration.md`.

---

## Stage 7: End-to-End Validation

1. **Delta propagation test:**
   - In S/4HANA, update the `ProductGroup` field on one test material.
   - Wait for the next delta cycle of RF-01.
   - Confirm the change appears in `RAW_I_PRODUCT`.
   - Trigger (or wait for scheduled run of) `TF_PRODUCT`.
   - Confirm the change appears in `REF_PRODUCT` and in `DIM_PRODUCT`.

2. **Cross-entity query test** (run the SQL in Stage 5.3 above).

3. **BDC access test:**
   - In BDC, open the `S/4 SP03 I Product` data product.
   - Click on the `Product` output port.
   - Run a preview query — confirm rows are returned.

4. Record milestone: `M7.achieved: end-to-end validation passed — delta replication active for all 21 entities`

---

## Maintenance Guide

### Adding a New Associated CDS View

1. Add the new CDS view to `entity-catalogue.md`.
2. Activate ODP for the new view in S/4HANA (`RODPS_REPL_TEST`).
3. Create the raw-zone folder in HDLFS.
4. Add the new entity as a target to the most appropriate Replication Flow (or create a new one).
5. Create the Transformation Flow for the new entity.
6. Create the Dimension view in Datasphere.
7. Add the new Dimension as an association in `ProductAnalyticalDataset`.
8. Add a new output port entry to `S4SP03IProduct.dpd`.
9. Add the new association to the `associations` array in `S4SP03IProduct.dpd`.
10. Increment the DPD version to the next minor version (e.g. `1.1.0`).
11. Re-register the DPD in BDC.

### Updating Field Labels

1. Update the label in the relevant Datasphere Dimension view.
2. Update the label in the `datasphere-models.md` label mapping table.
3. Re-deploy the Dimension view.
4. If the label change also affects the DPD `title` or `description`, update `S4SP03IProduct.dpd` and re-register.

### Versioning the DPD

1. Update `"version"` in `S4SP03IProduct.dpd`.
2. Update `"ordId"` only if the major version changes (e.g. `v1` → `v2`).
3. Re-upload to BDC and confirm the new version is active.

### S/4HANA Release Upgrade

1. After upgrading S/4HANA, re-run `RODPS_REPL_TEST` for all 22 CDS views.
2. Check whether any CDS view has changed keys, field names, or been deprecated.
3. Update the entity catalogue, Transformation Flow, and Dimension view for any changed view.
4. Update `"sourceSystem.release"` in `S4SP03IProduct.dpd` and re-register.

---

## Troubleshooting

| Issue | Likely Cause | Resolution |
|-------|-------------|-----------|
| Replication Flow fails at initial load | ODP extractor not activated / RFC authorisation missing | Run `RODPS_REPL_TEST` in S/4HANA; verify RFC user authorisations |
| Delta records not arriving | Delta queue not active | In S/4HANA, check ODP subscriber status via `RODPS_REPL_CONT` |
| Transformation Flow produces null language codes | `T002` mapping table not replicated | Add `T002` as an auxiliary source in the Transformation Flow |
| Datasphere Dimension view fails to deploy | HDLFS refined-zone table empty or missing | Verify Transformation Flow completed successfully; check for errors in Data Integration Monitor |
| BDC DPD validation fails | Missing required ORD field | Check that `ordId`, `version`, `releaseStatus`, `outputPorts`, and `associations` are all present in `S4SP03IProduct.dpd` |
| Cross-entity query returns no rows | Association join keys mismatched | Verify key field names in Datasphere Dimension views match the key fields in `datasphere-models.md` |
