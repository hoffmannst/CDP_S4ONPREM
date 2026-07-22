# Product Requirements Document (PRD)

**Title:** S/4_SP03_I_PRODUCT — Custom Data Product for SAP Business Data Cloud  
**Date:** 2026-07-20  
**Owner:** Data Product Owner / Data Steward  
**Solution Category:** Data Product (DPD), SAP Datasphere (Replication Flows, Transformation Flows, Dimensions, Analytical Dataset)

---

## Product Purpose & Value Proposition

**Elevator Pitch:**  
S/4HANA on-premise customers on SP03 cannot use the SAP managed BDC Product data product — it targets the cloud edition only. This solution extracts all CDS views reachable via `I_Product` associations, transforms them inside HDLFS, and assembles them into a governed, BDC-registered data product that mirrors the SAP managed structure — unlocking analytics-ready product master data for the entire enterprise.

**Business Need:**  
Product master data is locked inside S/4HANA SP03 across 20+ CDS views (`I_Product` and all its associations). Without a structured extraction, HDLFS-based transformation, and BDC registration process, downstream analytics, data mesh use cases, and Datasphere consumers cannot rely on governed, semantically consistent product data.

**Expected Value:**  
- Single governed source of product master data for all analytics consumers in Datasphere and BDC.  
- Elimination of ad-hoc, ungoverned extracts from S/4HANA.  
- Reusable HDLFS persistency layer that decouples S/4HANA source changes from Datasphere consumption models.  
- Alignment with SAP managed BDC Product DP structure — enabling a future migration to the cloud edition with minimal rework.

**Product Objectives (Prioritized):**
1. Extract every CDS view in the `I_Product` association tree into a dedicated HDLFS raw-zone table via Datasphere Replication Flows (initial + delta).
2. Transform each raw-zone table into a semantically enriched refined-zone table via Datasphere Transformation Flows — all compute inside HDLFS.
3. Assemble the refined-zone entities into the `S/4_SP03_I_PRODUCT` data product by declaring associations in a BDC-compliant DPD file.
4. Expose all refined-zone entities as Datasphere Dimension views and a central Analytical Dataset — Datasphere is a pure consumption layer.
5. Mirror the field labels, descriptions, and association structure of the SAP managed BDC Product data product.

---

## User Profiles & Personas

### Primary Persona: Data Product Owner / Data Steward

Maria is a 42-year-old data governance lead responsible for the quality and availability of master data products across the enterprise. She owns the product master data domain and needs to ensure that any analytics consumer gets a consistent, governed view of product data. She is frustrated that S/4HANA product data is consumed in dozens of different ways by different teams, each with their own field mappings and extraction logic. She wants one governed data product that everyone can rely on, aligned to SAP best practices.

### Secondary Persona: SAP Datasphere Administrator

Jonas is a 35-year-old Datasphere platform administrator. He configures replication flows, transformation flows, and manages HDLFS spaces. He needs clear naming conventions, partition strategies, and flow configurations so he can set up and maintain the extraction pipeline without reverse-engineering it from scratch.

### Secondary Persona: Analytics / BI Engineer

Priya is a 30-year-old BI engineer who builds reports and dashboards on top of Datasphere. She consumes the Dimension views and Analytical Dataset exposed by this data product. She needs clean, semantically labelled data with clear associations — she must not have to write transformation logic herself.

### Other User Types

- **S/4HANA Basis / Integration Consultant** — configures Cloud Connector, ODP extractors, RFC destinations.  
- **SAP BDC Platform Administrator** — registers the DPD file in BDC and manages data product lifecycle.

---

## User Goals & Tasks

### For Maria (Data Product Owner):

**Goals:**
- Register `S/4_SP03_I_PRODUCT` as a governed data product in BDC aligned to the SAP managed Product DP structure.
- Ensure all product master data associations are covered and no CDS view is missed.

**Key Tasks:**
- Review and sign off on the entity catalogue (association map of `I_Product`).
- Review and approve the DPD file before BDC registration.
- Monitor data product health and lineage in BDC.

### For Jonas (Datasphere Administrator):

**Goals:**
- Set up all replication flows (raw zone) and transformation flows (refined zone) reliably.
- Maintain clear HDLFS naming conventions and partition strategies.

**Key Tasks:**
- Configure S/4HANA on-premise source connection (Cloud Connector, RFC destination, ODP context).
- Create one Replication Flow per associated CDS view.
- Create one Transformation Flow per raw-zone entity.
- Validate initial load completeness and delta processing.

### For Priya (BI Engineer):

**Goals:**
- Consume clean, labelled product master data from Datasphere without writing transformation logic.

**Key Tasks:**
- Use Datasphere Dimension views and the central Analytical Dataset as sources for reports and dashboards.
- Validate field labels and association navigation in Datasphere.

---

## Goals and Non-Goals

### Goals (In Scope)

- Trace and document all CDS views in the `I_Product` association tree for S/4HANA SP03 (2023/02/00).
- Create HDLFS raw-zone tables for each associated CDS view.
- Create Datasphere Replication Flows (initial + delta) from S/4HANA on-premise for each CDS view.
- Create Datasphere Transformation Flows (HDLFS raw → HDLFS refined) for each entity.
- Create Datasphere Dimension views and a central ProductAnalyticalDataset reading from HDLFS refined zone.
- Author the `S/4_SP03_I_PRODUCT` DPD file with ORD-compliant structure, business semantics, output ports, and associations.
- Register the data product in BDC.
- Provide step-by-step setup instructions.

### Non-Goals (Out of Scope)

- Transformation logic inside Datasphere models (all compute stays in HDLFS Transformation Flows).
- S/4HANA Cloud or BTP-based extraction (scope is on-premise SP03 only).
- Extension of the data product to non-product master data domains (e.g., customer, vendor, finance).
- Real-time/streaming replication (batch replication with delta is sufficient).
- Custom UI or reporting layer (consumers use Datasphere and their own BI tools).

---

## Requirements

### Must-Have Requirements

**R01: Association Map — Complete Entity Catalogue**

- **Problem to Solve:** Without a complete map of all CDS views associated with `I_Product` in SP03, the extraction will be incomplete and the data product will miss entities.
- **User Story:** As a Data Product Owner, I need a complete catalogue of all CDS views reachable via `I_Product` associations so that no product master data entity is left out of the data product.
- **Acceptance Criteria:**
  - Given S/4HANA SP03 (2023/02/00), when the association tree of `I_Product` is traced, then a document lists every associated CDS view with its key fields, delta-enablement status, and ODP extractor context.
- **Maps to Objective:** 1
- **Priority Rank:** 1

**R02: HDLFS Raw Zone — One Table per Associated CDS View**

- **Problem to Solve:** Without a dedicated raw-zone table per CDS view, transformation flows cannot be independently managed and re-loaded.
- **User Story:** As a Datasphere Administrator, I need one HDLFS raw-zone table per associated CDS view so that each entity can be replicated, monitored, and re-loaded independently.
- **Acceptance Criteria:**
  - Given the entity catalogue from R01, when HDLFS raw-zone tables are created, then each table matches the source CDS view's key fields and column structure, named with the convention `RAW_<CDS_VIEW_NAME>`.
- **Maps to Objective:** 1
- **Priority Rank:** 2

**R03: Replication Flows — S/4HANA On-Premise to HDLFS Raw Zone**

- **Problem to Solve:** Product master data must be continuously replicated from S/4HANA into HDLFS to keep the data product current.
- **User Story:** As a Datasphere Administrator, I need Replication Flows for each associated CDS view so that product master data is available in the HDLFS raw zone with initial load and ongoing delta updates.
- **Acceptance Criteria:**
  - Given a configured S/4HANA on-premise source (Cloud Connector, ODP context `CDS_EXTRACTION`), when Replication Flows are activated, then initial load completes without errors and delta records are processed within the agreed schedule.
- **Maps to Objective:** 1
- **Priority Rank:** 3

**R04: Transformation Flows — HDLFS Raw to HDLFS Refined**

- **Problem to Solve:** Raw extracted data requires type conversions, language-dependent text resolution, unit mappings, and semantic enrichment before it can be consumed as a governed data product.
- **User Story:** As a Data Product Owner, I need Transformation Flows that convert raw HDLFS data into semantically enriched refined-zone tables so that all business logic is applied consistently before consumers access the data.
- **Acceptance Criteria:**
  - Given a populated raw-zone table, when the Transformation Flow runs, then the refined-zone table (`REF_<ENTITY_NAME>`) contains correctly typed, language-resolved, and labelled records; no transformation logic exists in Datasphere models.
- **Maps to Objective:** 2
- **Priority Rank:** 4

**R05: Datasphere Dimension Views and Central Analytical Dataset**

- **Problem to Solve:** BI engineers need semantically labelled, ready-to-use Datasphere models without writing transformation logic.
- **User Story:** As a BI Engineer, I need Datasphere Dimension views per entity and a central ProductAnalyticalDataset so that I can build reports directly on governed, labelled product master data.
- **Acceptance Criteria:**
  - Given refined-zone tables in HDLFS, when Dimension views are created in Datasphere, then each dimension has correct field labels, a defined key, and an association to the central ProductAnalyticalDataset; no SQL transformation logic is embedded in any Datasphere view.
- **Maps to Objective:** 4
- **Priority Rank:** 5

**R06: DPD File — BDC-Compliant Data Product Descriptor**

- **Problem to Solve:** Without a valid DPD file, the data product cannot be registered in BDC and remains ungoverned.
- **User Story:** As a Data Product Owner, I need an ORD-compliant DPD file for `S/4_SP03_I_PRODUCT` so that the data product is registered in BDC with correct business semantics, output ports, and associations.
- **Acceptance Criteria:**
  - Given the refined-zone entity catalogue, when the DPD file is validated and submitted to BDC, then the data product appears in BDC with all output ports, field descriptions, and associations matching the structure of the SAP managed BDC Product data product.
- **Maps to Objective:** 3, 5
- **Priority Rank:** 6

**R07: Setup Instructions**

- **Problem to Solve:** Without documented setup instructions, the pipeline cannot be reliably reproduced or maintained.
- **User Story:** As a Datasphere Administrator, I need step-by-step setup instructions covering source configuration, replication flows, transformation flows, Datasphere model creation, and BDC registration so that the full pipeline can be set up and maintained without undocumented tribal knowledge.
- **Acceptance Criteria:**
  - Given the solution artifacts (DPD, flow configurations, Datasphere models), when the setup instructions are followed by a new Datasphere Administrator, then the complete pipeline is operational end-to-end.
- **Maps to Objective:** 1–5
- **Priority Rank:** 7

---

## Solution Architecture

**Architecture Overview:**  
Five-layer architecture: S/4HANA on-premise (source) → HDLFS Raw Zone (replication) → HDLFS Refined Zone (transformation) → Datasphere Semantic Layer (consumption models) → BDC Data Product (governance & registration).

**Key Components:**

- **S/4HANA SP03 on-premise** — source system; CDS views with ODP delta-enabled annotations provide the extraction interface.
- **SAP Cloud Connector** — secure tunnel between S/4HANA on-premise and SAP BTP / Datasphere.
- **SAP Datasphere Replication Flow** — one per associated CDS view; loads raw data into HDLFS raw zone (initial + delta).
- **HDLFS Raw Zone** — landing area; one table per CDS view; named `RAW_<CDS_VIEW_NAME>`; partitioned by `MANDT` and extraction date.
- **SAP Datasphere Transformation Flow** — one per raw-zone entity; runs entirely inside HDLFS; outputs to refined zone; named `REF_<ENTITY_NAME>`.
- **HDLFS Refined Zone** — cleansed, semantically enriched tables; one per entity; named `REF_<ENTITY_NAME>`.
- **SAP Datasphere Dimension Views** — one per refined-zone entity (e.g., `DIM_PRODUCT`, `DIM_PRODUCTTEXT`, `DIM_PRODUCTUOM`, `DIM_PRODUCTPLANT`, `DIM_PRODUCTPLANT_*` sub-entities, `DIM_PRODUCTSTORAGELOC`, `DIM_PRODUCTVALUATION`, `DIM_PRODUCTSALESDELIVERY`, `DIM_PRODUCTPURCHASING`); no transformation logic.
- **SAP Datasphere Analytical Dataset** — `ProductAnalyticalDataset`; central star-schema node referencing all Dimension views.
- **DPD File** — `S/4_SP03_I_PRODUCT.dpd`; ORD-compliant; declares output ports (one per refined-zone entity) and associations; registered in BDC.

**Integration Points:**

- **S/4HANA → HDLFS Raw Zone**: ODP extractor (`CDS_EXTRACTION` context) via Datasphere Replication Flow over Cloud Connector; scheduled delta (frequency TBD with Datasphere Administrator).
- **HDLFS Raw → HDLFS Refined**: Datasphere Transformation Flow; triggered after Replication Flow completion.
- **HDLFS Refined → Datasphere Dimensions**: Read-only virtual access; no data movement.
- **DPD → BDC**: Manual registration via BDC data product management UI; versioned on each DPD update.

**Associated CDS Views (Entity Catalogue — SP03 / 2023.02.00):**

| # | CDS View | Description | Association from |
|---|----------|-------------|-----------------|
| 1 | `I_Product` | Product master header | Root |
| 2 | `I_ProductText` | Language-dependent product descriptions | `I_Product._Text` |
| 3 | `I_ProductUoM` | Units of measure per product | `I_Product._ProductUoM` |
| 4 | `I_ProductPlant` | Plant-level product data (MRP, storage, scheduling) | `I_Product._ProductPlant` |
| 5 | `I_ProductStorageLocation` | Storage location data | `I_ProductPlant._ProductStorageLocation` |
| 6 | `I_ProductValuation` | Valuation data (price, costing) | `I_Product._ProductValuation` |
| 7 | `I_ProductSalesDelivery` | Sales/delivery data (general) | `I_Product._SalesDelivery` |
| 8 | `I_ProdSalesDeliverySalesOrg` | Sales org-level sales/delivery data | `I_ProductSalesDelivery._SalesOrg` |
| 9 | `I_ProductPurchasing` | Purchasing data | `I_Product._Purchasing` |
| 10 | `I_ProductBasicText` | Basic texts (purchasing, sales info) | `I_Product._BasicText` |
| 11 | `I_ProductInspectionText` | Inspection texts | `I_Product._InspectionText` |
| 12 | `I_ProductQualityMgmt` | Quality management data | `I_Product._QualityMgmt` |
| 13 | `I_ProductPlantMRPArea` | MRP area data per plant | `I_ProductPlant._PlantMRPArea` |
| 14 | `I_ProductPlantCosting` | Plant costing data | `I_ProductPlant._PlantCosting` |
| 15 | `I_ProductPlantForecast` | Plant forecast data | `I_ProductPlant._PlantForecast` |
| 16 | `I_ProductPlantIntlTrade` | International trade data per plant | `I_ProductPlant._PlantIntlTrade` |
| 17 | `I_ProductPlantProcurement` | Plant procurement data | `I_ProductPlant._PlantProcurement` |
| 18 | `I_ProductPlantQualityMgmt` | Plant quality management data | `I_ProductPlant._PlantQualityMgmt` |
| 19 | `I_ProductPlantSales` | Plant sales data | `I_ProductPlant._PlantSales` |
| 20 | `I_ProductPlantStorage` | Plant storage data | `I_ProductPlant._PlantStorage` |
| 21 | `I_ProductPlantWorkScheduling` | Work scheduling per plant | `I_ProductPlant._PlantWorkScheduling` |
| 22 | `I_ProductMLAccount` | Material ledger / account assignment | `I_Product._MLAccount` |

**Deployment:**

- All HDLFS spaces and Datasphere assets reside in the customer's SAP Datasphere tenant.
- Cloud Connector runs in the customer's on-premise network.
- BDC registration targets the customer's BDC tenant linked to the Datasphere tenant.

---

## Configuration & Data

**Configuration Scope:**  
Cloud Connector must be configured with a valid RFC destination to S/4HANA SP03. ODP extractors must be activated in S/4HANA for all 22 CDS views listed above (transaction `RODPS_REPL_TEST` for validation). HDLFS space must be provisioned in Datasphere with sufficient storage.

**Organisational & Master Data:**
- HDLFS space name and capacity must be agreed before replication flows are created.
- HDLFS partition strategy: partition by `MANDT` (client) and extraction date for all raw-zone tables.
- Naming convention: `RAW_<CDS_VIEW_NAME>` for raw zone; `REF_<ENTITY_NAME>` for refined zone; `DIM_<ENTITY_NAME>` for Datasphere dimensions.

**Data Migration & Cutover:**
- Initial full load for all 22 CDS views before delta replication is activated.
- Full load sequence: header first (`I_Product`), then direct associations, then depth-2 associations (plant sub-entities).
- Delta replication activated per entity after initial load validation.

---

## Milestones

### M1: Association Map Completed

- **Description:** All CDS views reachable via `I_Product` associations in SP03 (2023/02/00) have been catalogued with key fields and ODP delta status.
- **Achieved when:** The entity catalogue document lists all 22 (or more) associated CDS views, each validated against the source S/4HANA system.
- **Log on achievement:** `M1.achieved: I_Product association map complete — <N> CDS views catalogued`
- **Log on miss:** `M1.missed: association map incomplete — some CDS views could not be validated against source system`

### M2: HDLFS Raw Zone Provisioned

- **Description:** HDLFS space is provisioned and all raw-zone tables are created per entity catalogue.
- **Achieved when:** All `RAW_<CDS_VIEW_NAME>` tables exist in HDLFS with correct schema and partition configuration.
- **Log on achievement:** `M2.achieved: HDLFS raw zone provisioned — <N> tables created`
- **Log on miss:** `M2.missed: HDLFS raw zone setup incomplete — check space provisioning and table creation errors`

### M3: Replication Flows Active — Initial Load Complete

- **Description:** All Replication Flows have completed their initial full load into the HDLFS raw zone.
- **Achieved when:** Each Replication Flow reports a successful initial load with zero error records; row counts validated against S/4HANA source.
- **Log on achievement:** `M3.achieved: initial load complete for all <N> replication flows`
- **Log on miss:** `M3.missed: initial load failed or incomplete — check flow error logs and ODP extractor status`

### M4: Transformation Flows Complete — Refined Zone Populated

- **Description:** All Transformation Flows have run successfully and HDLFS refined-zone tables are populated.
- **Achieved when:** Each `REF_<ENTITY_NAME>` table contains correctly typed, language-resolved, and enriched records; no null keys; transformation flow status is green.
- **Log on achievement:** `M4.achieved: refined zone populated for all <N> entities — transformation flows complete`
- **Log on miss:** `M4.missed: transformation flow errors detected — check type conversion logic and text join completeness`

### M5: Datasphere Semantic Layer Created

- **Description:** All Dimension views and the central ProductAnalyticalDataset are created and validated in Datasphere.
- **Achieved when:** All `DIM_<ENTITY_NAME>` views deploy without errors; `ProductAnalyticalDataset` references all dimensions; a test query returns labelled product data.
- **Log on achievement:** `M5.achieved: Datasphere semantic layer complete — <N> dimensions and 1 analytical dataset deployed`
- **Log on miss:** `M5.missed: Datasphere model deployment errors — check HDLFS connection and view definitions`

### M6: DPD File Registered in BDC

- **Description:** The `S/4_SP03_I_PRODUCT.dpd` file is validated and registered as a governed data product in BDC.
- **Achieved when:** The data product appears in BDC with all output ports, field descriptions, and associations; status is active.
- **Log on achievement:** `M6.achieved: S/4_SP03_I_PRODUCT registered in BDC — all output ports and associations active`
- **Log on miss:** `M6.missed: BDC registration failed — check DPD ORD compliance and output port definitions`

### M7: End-to-End Validated

- **Description:** Data flows end-to-end from S/4HANA through HDLFS to the Datasphere consumption layer without errors; delta replication is active.
- **Achieved when:** A record changed in S/4HANA propagates through the replication flow, transformation flow, and appears updated in the Datasphere Analytical Dataset within the agreed delta schedule.
- **Log on achievement:** `M7.achieved: end-to-end validation passed — delta replication active for all <N> entities`
- **Log on miss:** `M7.missed: end-to-end validation failed — check delta extractor status and transformation flow scheduling`

---

## Risks, Assumptions, and Dependencies

### Risks

- **ODP extractor availability:** Not all associated CDS views in SP03 may have `@Analytics.dataExtraction.enabled: true`. Views without this annotation cannot be replicated via ODP and require an alternative extraction approach (e.g., SLT or table replication).
- **Association depth and custom appends:** SP03 installations may include customer-specific extension includes or custom association targets not covered by the standard entity catalogue.
- **HDLFS space sizing:** Product master data volumes (especially plant-level and text views) can be large. Under-provisioning HDLFS will cause replication failures.
- **Semantic drift:** The SAP managed BDC Product DP evolves with BDC releases. The custom DPD must be reviewed and updated whenever the SAP managed DP changes.

### Assumptions

- S/4HANA SP03 (2023/02/00) is accessible from the Datasphere tenant via a configured Cloud Connector.
- All 22 associated CDS views listed in the entity catalogue are present and ODP-enabled in the source system.
- HDLFS space can be provisioned in the existing Datasphere tenant without additional licensing steps.
- The customer's BDC tenant is linked to their Datasphere tenant and accepts custom DPD registrations.
- Language-dependent texts are extracted for the primary language initially; multi-language support is a later iteration.

### Dependencies

- Cloud Connector setup and network approval (Basis / Integration Consultant).
- ODP extractor activation in S/4HANA (S/4HANA Basis team).
- HDLFS space provisioning in Datasphere (Datasphere Administrator).
- BDC tenant linkage to Datasphere (BDC Platform Administrator).

---

## Open Questions

1. Which languages must be supported in the initial extraction of `I_ProductText` and other text views?
2. What is the agreed delta replication frequency (hourly, daily, near-real-time)?
3. Are there customer-specific extension includes on `I_Product` or any associated view that must be added to the entity catalogue?
4. What is the HDLFS space name and storage quota available for this data product?
5. Is the BDC tenant already linked to the Datasphere tenant, or does this linkage need to be established as part of this project?

---

## Appendix

### Glossary

- **BDC** — SAP Business Data Cloud; the governed data product platform.
- **DPD** — Data Product Definition; the ORD-compliant descriptor file that registers a data product in BDC.
- **HDLFS** — HANA Data Lake File Store; the file-based storage layer in SAP Datasphere used for large-volume persistency.
- **ODP** — Operational Data Provisioning; the S/4HANA extraction framework used by Datasphere Replication Flows.
- **ORD** — Open Resource Discovery; the SAP standard for describing and discovering data and API resources.
- **CDS View** — Core Data Services view; the primary abstraction layer for data access in S/4HANA.
- **Raw Zone** — HDLFS area containing unmodified replicated data from S/4HANA.
- **Refined Zone** — HDLFS area containing transformed, semantically enriched data produced by Transformation Flows.
- **Dimension View** — A Datasphere entity type representing a master data dimension in a star-schema model.
- **Analytical Dataset** — A Datasphere entity type representing the central node of a star-schema analytical model.

### References

- SAP Datasphere Replication Flows documentation: https://help.sap.com/docs/SAP_DATASPHERE/c8a54ee704e94e15926551293243fd1d/e49a1b00d1f24843817e0d8a6db0b06b.html
- SAP Datasphere Transformation Flows documentation: https://help.sap.com/docs/SAP_DATASPHERE
- SAP Business Data Cloud — Data Product Management: https://help.sap.com/docs/business-data-cloud
- SAP S/4HANA CDS View Catalogue (SP03): https://api.sap.com/package/SAPS4HANACloud/overview
- ODP Extractor Configuration Guide: https://help.sap.com/docs/SAP_S4HANA_ON-PREMISE
