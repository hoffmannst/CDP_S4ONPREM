# Specification: s4-sp03-i-product-data-product

> **Guidelines**: Read [guidelines.md](../guidelines.md) and [guidelines-data-product-generation.md](../guidelines-data-product-generation.md) before executing ANY tasks below. Follow all constraints described there throughout execution.

---

## Phase 1 — Association Map & Entity Catalogue

- [ ] Read `product-requirements-document.md` and `intent.md` in full; store working directory via `pwd`
- [ ] Confirm the 22 associated CDS views listed below are the complete extraction scope for S/4HANA SP03 (2023/02/00):

| # | CDS View | Zone Table Name (Raw) | Zone Table Name (Refined) | Datasphere Dimension |
|---|----------|-----------------------|--------------------------|----------------------|
| 1 | `I_Product` | `RAW_I_PRODUCT` | `REF_PRODUCT` | `DIM_PRODUCT` |
| 2 | `I_ProductText` | `RAW_I_PRODUCTTEXT` | `REF_PRODUCTTEXT` | `DIM_PRODUCTTEXT` |
| 3 | `I_ProductUoM` | `RAW_I_PRODUCTUOM` | `REF_PRODUCTUOM` | `DIM_PRODUCTUOM` |
| 4 | `I_ProductPlant` | `RAW_I_PRODUCTPLANT` | `REF_PRODUCTPLANT` | `DIM_PRODUCTPLANT` |
| 5 | `I_ProductStorageLocation` | `RAW_I_PRODUCTSTORAGELOC` | `REF_PRODUCTSTORAGELOC` | `DIM_PRODUCTSTORAGELOC` |
| 6 | `I_ProductValuation` | `RAW_I_PRODUCTVALUATION` | `REF_PRODUCTVALUATION` | `DIM_PRODUCTVALUATION` |
| 7 | `I_ProductSalesDelivery` | `RAW_I_PRODUCTSALESDELIVERY` | `REF_PRODUCTSALESDELIVERY` | `DIM_PRODUCTSALESDELIVERY` |
| 8 | `I_ProdSalesDeliverySalesOrg` | `RAW_I_PRODSALESDELIVERYSALESORG` | `REF_PRODSALESDELIVERYSALESORG` | `DIM_PRODSALESDELIVERYSALESORG` |
| 9 | `I_ProductPurchasing` | `RAW_I_PRODUCTPURCHASING` | `REF_PRODUCTPURCHASING` | `DIM_PRODUCTPURCHASING` |
| 10 | `I_ProductBasicText` | `RAW_I_PRODUCTBASICTEXT` | `REF_PRODUCTBASICTEXT` | `DIM_PRODUCTBASICTEXT` |
| 11 | `I_ProductInspectionText` | `RAW_I_PRODUCTINSPECTIONTEXT` | `REF_PRODUCTINSPECTIONTEXT` | `DIM_PRODUCTINSPECTIONTEXT` |
| 12 | `I_ProductQualityMgmt` | `RAW_I_PRODUCTQUALITYMGMT` | `REF_PRODUCTQUALITYMGMT` | `DIM_PRODUCTQUALITYMGMT` |
| 13 | `I_ProductPlantMRPArea` | `RAW_I_PRODUCTPLANTMRPAREA` | `REF_PRODUCTPLANTMRPAREA` | `DIM_PRODUCTPLANTMRPAREA` |
| 14 | `I_ProductPlantCosting` | `RAW_I_PRODUCTPLANTCOSTING` | `REF_PRODUCTPLANTCOSTING` | `DIM_PRODUCTPLANTCOSTING` |
| 15 | `I_ProductPlantForecast` | `RAW_I_PRODUCTPLANTFORECAST` | `REF_PRODUCTPLANTFORECAST` | `DIM_PRODUCTPLANTFORECAST` |
| 16 | `I_ProductPlantIntlTrade` | `RAW_I_PRODUCTPLANTINTLTRADE` | `REF_PRODUCTPLANTINTLTRADE` | `DIM_PRODUCTPLANTINTLTRADE` |
| 17 | `I_ProductPlantProcurement` | `RAW_I_PRODUCTPLANTPROCUREMENT` | `REF_PRODUCTPLANTPROCUREMENT` | `DIM_PRODUCTPLANTPROCUREMENT` |
| 18 | `I_ProductPlantQualityMgmt` | `RAW_I_PRODUCTPLANTQUALITYMGMT` | `REF_PRODUCTPLANTQUALITYMGMT` | `DIM_PRODUCTPLANTQUALITYMGMT` |
| 19 | `I_ProductPlantSales` | `RAW_I_PRODUCTPLANTSALES` | `REF_PRODUCTPLANTSALES` | `DIM_PRODUCTPLANTSALES` |
| 20 | `I_ProductPlantStorage` | `RAW_I_PRODUCTPLANTSTORAGE` | `REF_PRODUCTPLANTSTORAGE` | `DIM_PRODUCTPLANTSTORAGE` |
| 21 | `I_ProductPlantWorkScheduling` | `RAW_I_PRODUCTPLANTWORKSCHEDULING` | `REF_PRODUCTPLANTWORKSCHEDULING` | `DIM_PRODUCTPLANTWORKSCHEDULING` |
| 22 | `I_ProductMLAccount` | `RAW_I_PRODUCTMLACCOUNT` | `REF_PRODUCTMLACCOUNT` | `DIM_PRODUCTMLACCOUNT` |

- [ ] Verify in the source S/4HANA SP03 system (transaction `SE11` or `RODPS_REPL_TEST`) that each CDS view carries `@Analytics.dataExtraction.enabled: true`; document any exceptions
- [ ] For any CDS view without ODP delta support, flag it and record the fallback extraction method (SLT or table replication)
- [ ] Document key fields per CDS view (minimum: `Product` / `MATNR`, `Client` / `MANDT`, plus entity-specific keys such as `Plant`, `StorageLocation`, `ValuationType`, `SalesOrganization`, `Language`)
- [ ] Save the completed entity catalogue as `assets/s4-sp03-i-product-data-product/entity-catalogue.md`

---

## Phase 2 — HDLFS Space & Naming Convention

- [ ] Confirm the HDLFS space name with the Datasphere Administrator and record it in `assets/s4-sp03-i-product-data-product/hdlfs-config.md`
- [ ] Define partition strategy for all raw-zone tables: partition by `MANDT` (primary) and `EXTRACTION_DATE` (secondary); record in `hdlfs-config.md`
- [ ] Define HDLFS folder/path structure:
  - Raw zone path:     `<hdlfs-space>/product-master/raw/<CDS_VIEW_NAME>/`
  - Refined zone path: `<hdlfs-space>/product-master/refined/<ENTITY_NAME>/`
- [ ] Document HDLFS storage estimate per entity (row count × average row size) in `hdlfs-config.md`
- [ ] Save `assets/s4-sp03-i-product-data-product/hdlfs-config.md` with all of the above

---

## Phase 3 — S/4HANA Source Connection & ODP Configuration

- [ ] Verify that SAP Cloud Connector is installed and running in the customer on-premise network and is registered in the SAP BTP subaccount linked to Datasphere
- [ ] Create/validate RFC destination in Datasphere pointing to S/4HANA SP03 via Cloud Connector; name convention: `S4H_SP03_RFC`
- [ ] In S/4HANA, activate ODP replication for all 22 CDS views using transaction `RODPS_REPL_TEST`; ODP context: `CDS_EXTRACTION`
- [ ] Validate connectivity: run a test extraction for `I_Product` (limit 100 rows) from Datasphere; confirm records arrive in HDLFS raw zone
- [ ] Document the source connection configuration in `assets/s4-sp03-i-product-data-product/source-connection-config.md`

---

## Phase 4 — Replication Flows (HDLFS Raw Zone)

Create one Datasphere Replication Flow per CDS view group. Group depth-2 plant sub-entities together where Datasphere supports multi-target flows; otherwise create individual flows.

### RF-01: Product Header & Core Associations
- [ ] Create Replication Flow `RF_S4SP03_PRODUCT_CORE`:
  - Source: S/4HANA SP03, ODP context `CDS_EXTRACTION`
  - Targets: `RAW_I_PRODUCT`, `RAW_I_PRODUCTTEXT`, `RAW_I_PRODUCTUOM`, `RAW_I_PRODUCTVALUATION`, `RAW_I_PRODUCTMLACCOUNT`
  - Load type: Initial load + Delta
  - Partition: by `MANDT`
- [ ] Run initial load; validate row counts against S/4HANA source for each target table
- [ ] Activate delta replication; confirm first delta cycle processes correctly

### RF-02: Sales & Purchasing
- [ ] Create Replication Flow `RF_S4SP03_PRODUCT_SALES_PURCH`:
  - Targets: `RAW_I_PRODUCTSALESDELIVERY`, `RAW_I_PRODSALESDELIVERYSALESORG`, `RAW_I_PRODUCTPURCHASING`
  - Load type: Initial load + Delta
- [ ] Run initial load and validate row counts
- [ ] Activate delta replication

### RF-03: Plant-Level Data (Core)
- [ ] Create Replication Flow `RF_S4SP03_PRODUCT_PLANT_CORE`:
  - Targets: `RAW_I_PRODUCTPLANT`, `RAW_I_PRODUCTSTORAGELOC`
  - Load type: Initial load + Delta
- [ ] Run initial load and validate
- [ ] Activate delta replication

### RF-04: Plant Sub-Entities (MRP, Costing, Forecast, Intl Trade)
- [ ] Create Replication Flow `RF_S4SP03_PRODUCT_PLANT_EXT1`:
  - Targets: `RAW_I_PRODUCTPLANTMRPAREA`, `RAW_I_PRODUCTPLANTCOSTING`, `RAW_I_PRODUCTPLANTFORECAST`, `RAW_I_PRODUCTPLANTINTLTRADE`
  - Load type: Initial load + Delta
- [ ] Run initial load and validate
- [ ] Activate delta replication

### RF-05: Plant Sub-Entities (Procurement, Quality, Sales, Storage, Work Scheduling)
- [ ] Create Replication Flow `RF_S4SP03_PRODUCT_PLANT_EXT2`:
  - Targets: `RAW_I_PRODUCTPLANTPROCUREMENT`, `RAW_I_PRODUCTPLANTQUALITYMGMT`, `RAW_I_PRODUCTPLANTSALES`, `RAW_I_PRODUCTPLANTSTORAGE`, `RAW_I_PRODUCTPLANTWORKSCHEDULING`
  - Load type: Initial load + Delta
- [ ] Run initial load and validate
- [ ] Activate delta replication

### RF-06: Quality, Inspection & Basic Texts
- [ ] Create Replication Flow `RF_S4SP03_PRODUCT_TEXTS`:
  - Targets: `RAW_I_PRODUCTBASICTEXT`, `RAW_I_PRODUCTINSPECTIONTEXT`, `RAW_I_PRODUCTQUALITYMGMT`
  - Load type: Initial load + Delta
- [ ] Run initial load and validate
- [ ] Activate delta replication

- [ ] Confirm all 6 Replication Flows are green (initial load complete, delta active)
- [ ] Save Replication Flow configuration summary to `assets/s4-sp03-i-product-data-product/replication-flows.md`

---

## Phase 5 — Transformation Flows (HDLFS Refined Zone)

Create one Datasphere Transformation Flow per raw-zone entity. All flows execute entirely within HDLFS (raw → refined). No transformation logic may reside in Datasphere views.

### Common transformation rules to apply in every flow:
- Cast `MANDT` (Client) as string key; exclude from output if single-client landscape
- Resolve `SPRAS` (language key) to ISO language code in all text views
- Convert SAP internal unit codes to ISO unit codes using `T006` mapping where applicable
- Apply `ERSDA` / `LAEDA` (creation / last change date) type casting to `DATE`
- Trim trailing spaces from all CHAR fields
- Map `MTART` (Material Type) to business-readable label using `T134T` mapping for `REF_PRODUCT`
- Map `MATKL` (Material Group) to description using `T023T` for `REF_PRODUCT`
- Add `EXTRACTION_TIMESTAMP` column (load time) to all refined-zone tables

### TF-01 through TF-22: One flow per entity
- [ ] Create `TF_PRODUCT` (raw: `RAW_I_PRODUCT` → refined: `REF_PRODUCT`): apply all common rules + material type/group label mapping
- [ ] Create `TF_PRODUCTTEXT` (raw: `RAW_I_PRODUCTTEXT` → refined: `REF_PRODUCTTEXT`): resolve language key; keep `Product`, `Language`, `ProductDescription`, `ProductOldID` columns
- [ ] Create `TF_PRODUCTUOM` (raw: `RAW_I_PRODUCTUOM` → refined: `REF_PRODUCTUOM`): convert unit codes; keep `Product`, `AlternativeUnit`, `QuantityNumerator`, `QuantityDenominator`, `GlobalTradeItemNumber`, `GlobalTradeItemNumberCategory`
- [ ] Create `TF_PRODUCTPLANT` (raw: `RAW_I_PRODUCTPLANT` → refined: `REF_PRODUCTPLANT`): cast date fields; keep all MRP, availability check, and planning fields
- [ ] Create `TF_PRODUCTSTORAGELOC` (raw: `RAW_I_PRODUCTSTORAGELOC` → refined: `REF_PRODUCTSTORAGELOC`): key = `Product + Plant + StorageLocation`
- [ ] Create `TF_PRODUCTVALUATION` (raw: `RAW_I_PRODUCTVALUATION` → refined: `REF_PRODUCTVALUATION`): cast price/cost amount fields to DECIMAL(23,2); keep `ValuationClass`, `PriceControlIndicator`, `MovingAveragePrice`, `StandardPrice`
- [ ] Create `TF_PRODUCTSALESDELIVERY` (raw: `RAW_I_PRODUCTSALESDELIVERY` → refined: `REF_PRODUCTSALESDELIVERY`): keep sales-relevant fields; cast weight/volume fields
- [ ] Create `TF_PRODSALESDELIVERYSALESORG` (raw: `RAW_I_PRODSALESDELIVERYSALESORG` → refined: `REF_PRODSALESDELIVERYSALESORG`): key = `Product + SalesOrganization + DistributionChannel`
- [ ] Create `TF_PRODUCTPURCHASING` (raw: `RAW_I_PRODUCTPURCHASING` → refined: `REF_PRODUCTPURCHASING`): key = `Product + Plant`; cast planned delivery time
- [ ] Create `TF_PRODUCTBASICTEXT` (raw: `RAW_I_PRODUCTBASICTEXT` → refined: `REF_PRODUCTBASICTEXT`): language-resolved text; key = `Product + Language`
- [ ] Create `TF_PRODUCTINSPECTIONTEXT` (raw: `RAW_I_PRODUCTINSPECTIONTEXT` → refined: `REF_PRODUCTINSPECTIONTEXT`): language-resolved; key = `Product + Language`
- [ ] Create `TF_PRODUCTQUALITYMGMT` (raw: `RAW_I_PRODUCTQUALITYMGMT` → refined: `REF_PRODUCTQUALITYMGMT`): key = `Product + Plant`
- [ ] Create `TF_PRODUCTPLANTMRPAREA` (raw: `RAW_I_PRODUCTPLANTMRPAREA` → refined: `REF_PRODUCTPLANTMRPAREA`): key = `Product + Plant + MRPArea`
- [ ] Create `TF_PRODUCTPLANTCOSTING` (raw: `RAW_I_PRODUCTPLANTCOSTING` → refined: `REF_PRODUCTPLANTCOSTING`): key = `Product + Plant + CostingVariant`
- [ ] Create `TF_PRODUCTPLANTFORECAST` (raw: `RAW_I_PRODUCTPLANTFORECAST` → refined: `REF_PRODUCTPLANTFORECAST`): key = `Product + Plant`
- [ ] Create `TF_PRODUCTPLANTINTLTRADE` (raw: `RAW_I_PRODUCTPLANTINTLTRADE` → refined: `REF_PRODUCTPLANTINTLTRADE`): key = `Product + Plant`; keep commodity code, country of origin fields
- [ ] Create `TF_PRODUCTPLANTPROCUREMENT` (raw: `RAW_I_PRODUCTPLANTPROCUREMENT` → refined: `REF_PRODUCTPLANTPROCUREMENT`): key = `Product + Plant`
- [ ] Create `TF_PRODUCTPLANTQUALITYMGMT` (raw: `RAW_I_PRODUCTPLANTQUALITYMGMT` → refined: `REF_PRODUCTPLANTQUALITYMGMT`): key = `Product + Plant`
- [ ] Create `TF_PRODUCTPLANTSALES` (raw: `RAW_I_PRODUCTPLANTSALES` → refined: `REF_PRODUCTPLANTSALES`): key = `Product + Plant`
- [ ] Create `TF_PRODUCTPLANTSTORAGE` (raw: `RAW_I_PRODUCTPLANTSTORAGE` → refined: `REF_PRODUCTPLANTSTORAGE`): key = `Product + Plant`; keep temperature, storage conditions fields
- [ ] Create `TF_PRODUCTPLANTWORKSCHEDULING` (raw: `RAW_I_PRODUCTPLANTWORKSCHEDULING` → refined: `REF_PRODUCTPLANTWORKSCHEDULING`): key = `Product + Plant`; keep production scheduler, underdelivery/overdelivery tolerance fields
- [ ] Create `TF_PRODUCTMLACCOUNT` (raw: `RAW_I_PRODUCTMLACCOUNT` → refined: `REF_PRODUCTMLACCOUNT`): key = `Product + ValuationArea + ValuationType + CurrencyType`; cast all amount/price fields to DECIMAL(23,2)

- [ ] Run all 22 Transformation Flows; validate refined-zone row counts equal raw-zone row counts (no record loss)
- [ ] Spot-check 5 products end-to-end: verify field values, language resolution, and unit conversions are correct
- [ ] Save Transformation Flow configuration summary to `assets/s4-sp03-i-product-data-product/transformation-flows.md`

---

## Phase 6 — Datasphere Semantic Layer (Dimensions & Analytical Dataset)

All Datasphere objects read from HDLFS refined zone. No SQL transformation logic in any Datasphere view.

### 6a — Dimension Views (one per refined-zone entity)
- [ ] Create Dimension `DIM_PRODUCT` on `REF_PRODUCT`: key = `Product`; set semantic type = Dimension; apply field business labels from SAP managed BDC Product DP field list (see label mapping table below)
- [ ] Create Dimension `DIM_PRODUCTTEXT` on `REF_PRODUCTTEXT`: key = `Product + Language`; semantic type = Text; associate to `DIM_PRODUCT` via `Product`
- [ ] Create Dimension `DIM_PRODUCTUOM` on `REF_PRODUCTUOM`: key = `Product + AlternativeUnit`; associate to `DIM_PRODUCT`
- [ ] Create Dimension `DIM_PRODUCTPLANT` on `REF_PRODUCTPLANT`: key = `Product + Plant`; associate to `DIM_PRODUCT`
- [ ] Create Dimension `DIM_PRODUCTSTORAGELOC` on `REF_PRODUCTSTORAGELOC`: key = `Product + Plant + StorageLocation`; associate to `DIM_PRODUCTPLANT`
- [ ] Create Dimension `DIM_PRODUCTVALUATION` on `REF_PRODUCTVALUATION`: key = `Product + ValuationArea + ValuationType`; associate to `DIM_PRODUCT`
- [ ] Create Dimension `DIM_PRODUCTSALESDELIVERY` on `REF_PRODUCTSALESDELIVERY`: key = `Product`; associate to `DIM_PRODUCT`
- [ ] Create Dimension `DIM_PRODSALESDELIVERYSALESORG` on `REF_PRODSALESDELIVERYSALESORG`: key = `Product + SalesOrganization + DistributionChannel`; associate to `DIM_PRODUCTSALESDELIVERY`
- [ ] Create Dimension `DIM_PRODUCTPURCHASING` on `REF_PRODUCTPURCHASING`: key = `Product + Plant`; associate to `DIM_PRODUCTPLANT`
- [ ] Create Dimension `DIM_PRODUCTBASICTEXT` on `REF_PRODUCTBASICTEXT`: key = `Product + Language`; associate to `DIM_PRODUCT`
- [ ] Create Dimension `DIM_PRODUCTINSPECTIONTEXT` on `REF_PRODUCTINSPECTIONTEXT`: key = `Product + Language`; associate to `DIM_PRODUCT`
- [ ] Create Dimension `DIM_PRODUCTQUALITYMGMT` on `REF_PRODUCTQUALITYMGMT`: key = `Product + Plant`; associate to `DIM_PRODUCTPLANT`
- [ ] Create Dimension `DIM_PRODUCTPLANTMRPAREA` on `REF_PRODUCTPLANTMRPAREA`: key = `Product + Plant + MRPArea`; associate to `DIM_PRODUCTPLANT`
- [ ] Create Dimension `DIM_PRODUCTPLANTCOSTING` on `REF_PRODUCTPLANTCOSTING`: key = `Product + Plant + CostingVariant`; associate to `DIM_PRODUCTPLANT`
- [ ] Create Dimension `DIM_PRODUCTPLANTFORECAST` on `REF_PRODUCTPLANTFORECAST`: key = `Product + Plant`; associate to `DIM_PRODUCTPLANT`
- [ ] Create Dimension `DIM_PRODUCTPLANTINTLTRADE` on `REF_PRODUCTPLANTINTLTRADE`: key = `Product + Plant`; associate to `DIM_PRODUCTPLANT`
- [ ] Create Dimension `DIM_PRODUCTPLANTPROCUREMENT` on `REF_PRODUCTPLANTPROCUREMENT`: key = `Product + Plant`; associate to `DIM_PRODUCTPLANT`
- [ ] Create Dimension `DIM_PRODUCTPLANTQUALITYMGMT` on `REF_PRODUCTPLANTQUALITYMGMT`: key = `Product + Plant`; associate to `DIM_PRODUCTPLANT`
- [ ] Create Dimension `DIM_PRODUCTPLANTSALES` on `REF_PRODUCTPLANTSALES`: key = `Product + Plant`; associate to `DIM_PRODUCTPLANT`
- [ ] Create Dimension `DIM_PRODUCTPLANTSTORAGE` on `REF_PRODUCTPLANTSTORAGE`: key = `Product + Plant`; associate to `DIM_PRODUCTPLANT`
- [ ] Create Dimension `DIM_PRODUCTPLANTWORKSCHEDULING` on `REF_PRODUCTPLANTWORKSCHEDULING`: key = `Product + Plant`; associate to `DIM_PRODUCTPLANT`
- [ ] Create Dimension `DIM_PRODUCTMLACCOUNT` on `REF_PRODUCTMLACCOUNT`: key = `Product + ValuationArea + ValuationType + CurrencyType`; associate to `DIM_PRODUCTVALUATION`

### 6b — Field Business Label Mapping (apply to DIM_PRODUCT)

| Technical Field | Business Label (EN) |
|-----------------|---------------------|
| `Product` | Product |
| `ProductType` | Product Type |
| `ProductGroup` | Product Group |
| `BaseUnit` | Base Unit of Measure |
| `WeightUnit` | Weight Unit |
| `GrossWeight` | Gross Weight |
| `NetWeight` | Net Weight |
| `VolumeUnit` | Volume Unit |
| `Volume` | Volume |
| `Division` | Division |
| `ProductHierarchy` | Product Hierarchy |
| `SizeOrDimensionText` | Size / Dimension |
| `IndustrySector` | Industry Sector |
| `IndustrySectorCode` | Industry Sector Code |
| `CrossPlantStatus` | Cross-Plant Material Status |
| `CrossPlantStatusValidityDate` | Cross-Plant Status Valid From |
| `CreationDate` | Created On |
| `LastChangeDate` | Last Changed On |
| `IsMarkedForDeletion` | Deletion Flag |

### 6c — Central Analytical Dataset
- [ ] Create Analytical Dataset `ProductAnalyticalDataset`:
  - Central node: `DIM_PRODUCT`
  - Measure: none (product master is dimension-only; measures come from transactional data)
  - Associations (star-schema spokes): link all 22 Dimension views via their respective foreign key associations as defined in 6a above
  - Semantic usage: `#ANALYTICAL_CUBE`
  - Set label: "Product Master — S/4HANA SP03"
- [ ] Deploy all Dimension views; confirm zero deployment errors
- [ ] Deploy `ProductAnalyticalDataset`; run a test query returning Product, ProductType, BaseUnit, Language-resolved description, Plant, StorageLocation — confirm results
- [ ] Save Datasphere model configuration summary to `assets/s4-sp03-i-product-data-product/datasphere-models.md`

---

## Phase 7 — Data Product Generation (DPD File & BDC Registration)

- [ ] Invoke the `data-product-generation` skill to execute the full workflow (Steps 1–11) using the following pre-resolved inputs:

  **Metadata (pre-approved — no further user input needed):**
  - Technical Name (`name`): `S4SP03IProduct`
  - Business Name (`title`): `S/4 SP03 I Product`
  - Description: `Custom derived data product for S/4HANA on-premise SP03 (release 2023/02/00). Resolves all associations of the I_Product CDS view, extracts each associated entity into HDLFS, transforms in place, and exposes governed product master data via Datasphere Dimension views and a central Analytical Dataset. Mirrors the structure, business semantics, and associations of the SAP managed BDC Product data product.`
  - Short description: `S/4HANA SP03 product master data product — all I_Product associations extracted into HDLFS and exposed via Datasphere.`
  - Folder name: `s4-sp03-i-product-data-product`
  - ORD ID (target): `customer:dataProduct:S4SP03IProduct:v1`

  **Output Ports (one per refined-zone entity — 22 total):**
  - Each output port corresponds to one `REF_<ENTITY_NAME>` HDLFS refined-zone table
  - Output port type: HDLFS file reference
  - Association declarations mirror the S/4 `I_Product` association tree as documented in the entity catalogue

  **DPD file location:** `assets/s4-sp03-i-product-data-product/S4SP03IProduct.dpd`

- [ ] Validate the generated DPD file: confirm all 22 output ports are present; confirm association declarations are complete
- [ ] Confirm DPD ORD compliance: `ordId`, `version`, `outputPorts`, `associations`, `title`, `shortDescription`, `description`, `releaseStatus` fields all populated
- [ ] Register `S4SP03IProduct.dpd` in BDC via the BDC data product management UI; confirm status = Active
- [ ] Save registration confirmation and BDC data product URL to `assets/s4-sp03-i-product-data-product/bdc-registration.md`

---

## Phase 8 — End-to-End Validation

- [ ] Change one product record in S/4HANA SP03 (e.g. update `ProductGroup` on a test material)
- [ ] Confirm the change appears in the corresponding raw-zone table (`RAW_I_PRODUCT`) after the next delta replication cycle
- [ ] Confirm the change propagates to the refined-zone table (`REF_PRODUCT`) after the Transformation Flow runs
- [ ] Confirm the change is visible in the `DIM_PRODUCT` Dimension view and in the `ProductAnalyticalDataset` in Datasphere
- [ ] Run a cross-entity query in Datasphere: retrieve `Product`, `ProductDescription` (from `DIM_PRODUCTTEXT`), `Plant`, `StorageLocation` (from `DIM_PRODUCTSTORAGELOC`), `StandardPrice` (from `DIM_PRODUCTVALUATION`) for 10 test materials — confirm all joins resolve correctly
- [ ] Confirm the data product is visible and queryable in BDC with all 22 output ports accessible
- [ ] Mark milestone M7 achieved: log `M7.achieved: end-to-end validation passed — delta replication active for all 22 entities`

---

## Phase 9 — Setup Instructions Document

- [ ] Write `assets/s4-sp03-i-product-data-product/SETUP-INSTRUCTIONS.md` covering:
  1. Prerequisites (Cloud Connector, ODP activation, HDLFS provisioning, BDC–Datasphere tenant linkage)
  2. Step-by-step: create HDLFS raw-zone tables (naming, partition config)
  3. Step-by-step: create and activate all 6 Replication Flows (RF-01 through RF-06)
  4. Step-by-step: create and run all 22 Transformation Flows (TF-01 through TF-22)
  5. Step-by-step: create all 22 Dimension views and the `ProductAnalyticalDataset` in Datasphere
  6. Step-by-step: register the DPD in BDC
  7. Validation checklist (end-to-end test procedure from Phase 8)
  8. Maintenance guide: how to add a new associated CDS view, how to update field labels, how to version the DPD

---

## Milestone Logging Reference

Use the following log statements when each milestone is reached:

| Milestone | Achievement Log | Miss Log |
|-----------|----------------|----------|
| M1 | `M1.achieved: I_Product association map complete — 22 CDS views catalogued` | `M1.missed: association map incomplete — some CDS views could not be validated against source system` |
| M2 | `M2.achieved: HDLFS raw zone provisioned — 22 tables created` | `M2.missed: HDLFS raw zone setup incomplete — check space provisioning and table creation errors` |
| M3 | `M3.achieved: initial load complete for all 6 replication flows` | `M3.missed: initial load failed or incomplete — check flow error logs and ODP extractor status` |
| M4 | `M4.achieved: refined zone populated for all 22 entities — transformation flows complete` | `M4.missed: transformation flow errors detected — check type conversion logic and text join completeness` |
| M5 | `M5.achieved: Datasphere semantic layer complete — 22 dimensions and 1 analytical dataset deployed` | `M5.missed: Datasphere model deployment errors — check HDLFS connection and view definitions` |
| M6 | `M6.achieved: S/4_SP03_I_PRODUCT registered in BDC — all output ports and associations active` | `M6.missed: BDC registration failed — check DPD ORD compliance and output port definitions` |
| M7 | `M7.achieved: end-to-end validation passed — delta replication active for all 22 entities` | `M7.missed: end-to-end validation failed — check delta extractor status and transformation flow scheduling` |
