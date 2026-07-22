# S/4_SP03_I_PRODUCT — Custom Data Product for SAP Business Data Cloud

Custom data product that maps S/4HANA on-premise (SP03 / release 2023.02.00) product master data to the SAP managed BDC data product structure. The scope covers **all CDS views reachable via the associations of `I_Product`** — each view is extracted independently into HDLFS, transformed in place, and then combined through file associations to form the derived data product. Analytic models (dimensions, analytical datasets) are built on top in Datasphere as the consumption layer.

---

## Business challenge

As an S/4HANA on-premise customer (SP03, release 2023.02.00), product master data lives inside S/4HANA and is not yet available as a governed data product in SAP Business Data Cloud (BDC). The SAP managed BDC data product for Product is based on the `I_Product` CDS view, which carries associations to a set of related CDS views (texts, units of measure, plant data, storage locations, valuation, classification, product hierarchy, etc.).

To unlock consistent, analytics-ready product data across the enterprise, a custom data product named `S/4_SP03_I_PRODUCT` must be created that:

- **Resolves all associations** of `I_Product` in S/4HANA SP03 and identifies every associated CDS view that needs to be extracted.
- **Extracts each CDS view independently** into dedicated HDLFS-based persistency tables/files in Datasphere (one replication flow per source CDS view or logical group).
- **Transforms each extracted dataset** inside HDLFS (type conversions, language-dependent text resolution, unit mappings, semantic enrichments) using Datasphere Transformation Flows — all compute stays in HDLFS.
- **Builds the derived data product** by associating the individual HDLFS files/tables (mirroring the original S/4 associations) and registering the result as `S/4_SP03_I_PRODUCT` in BDC via a DPD file.
- **Creates analytic models** (dimensions per associated entity, plus a central Product analytical dataset) in Datasphere on top of the HDLFS persistencies — Datasphere is a pure consumption/semantic layer, no transformation logic inside it.
- Mirrors the structure, business semantics (field labels, descriptions), and associations of the SAP managed BDC Product data product.
- Produces a DPD (Data Product Definition) file and step-by-step setup instructions.

---

## Key Milestones

1. **Association map completed** — all CDS views reachable via `I_Product` associations in SP03 (2023/02/00) catalogued: `I_ProductText`, `I_ProductUoM`, `I_ProductPlant`, `I_ProductStorageLocation`, `I_ProductValuation`, `I_ProductSalesDelivery`, `I_ProductPurchasing`, `I_ProductBasicText`, `I_ProductInspectionText`, `I_ProductQualityMgmt`, `I_ProdSalesDeliverySalesOrg`, `I_ProductPlantMRPArea`, `I_ProductPlantCosting`, `I_ProductPlantForecast`, `I_ProductPlantIntlTrade`, `I_ProductPlantProcurement`, `I_ProductPlantQualityMgmt`, `I_ProductPlantSales`, `I_ProductPlantStorage`, `I_ProductPlantWorkScheduling`, `I_ProductMLAccount` and any further depth-1 and depth-2 associations identified.
2. **DPD file created** — `S/4_SP03_I_PRODUCT.dpd` aligned to SAP managed BDC Product data product structure with full business semantics and associations declared.
3. **HDLFS persistency defined** — one HDLFS target table/file per associated CDS view; partition and naming strategy agreed.
4. **Replication flows configured** — one or more Datasphere Replication Flows extracting each CDS view from S/4HANA on-premise into the corresponding HDLFS target (initial load + delta).
5. **Transformation flows configured** — one Transformation Flow per HDLFS raw zone table producing cleansed/enriched output in an HDLFS refined zone; all conversions done here.
6. **Datasphere analytic models created** — one Dimension view per associated entity (ProductText, ProductUoM, ProductPlant, etc.) and a central ProductAnalyticalDataset, all reading from HDLFS refined zone; no transformation logic in Datasphere.
7. **Data product assembled** — HDLFS files associated to form the composite data product; DPD registered in BDC.
8. **End-to-end validated** — data flows from S/4 through HDLFS (raw → refined) to Datasphere consumption layer without errors.

---

## Business Architecture (RBA)

### End-to-End Process

Idea to Market for Produced Physical Products — discrete industry

### Process Hierarchy

```
Idea to Market (E2E)
└── Manage Product (produced physical product, discrete industry)
    └── Manage product lifecycle and compliance (BPS-323_001)
        └── Manage product data
            └── Extract and govern product master data (all associated views)
            └── Transform and enrich product data in HDLFS
            └── Expose governed data product for analytics consumption
```

### Summary

The challenge maps to the "Manage Product" phase of the Idea to Market E2E, specifically "Manage product lifecycle and compliance" (BPS-323_001). The custom data product resolves all `I_Product` associations and exposes every related entity as a governed, analytics-ready persistency in HDLFS, consumed through Datasphere analytic models.

---

## Fit Gap Analysis

| Requirement (business)                                                                                                           | Standard asset(s) found                                                                 | API ORD ID                                       | MCP Server ORD ID | MCP Server Version | Gap?      | Notes / assumptions                                                                                                              |
|----------------------------------------------------------------------------------------------------------------------------------|-----------------------------------------------------------------------------------------|--------------------------------------------------|-------------------|--------------------|-----------|----------------------------------------------------------------------------------------------------------------------------------|
| Resolve all `I_Product` associations and identify all CDS views to extract                                                       | S/4HANA CDS view catalogue (SP03 / 2023.02.00)                                         | `sap.s4:apiResource:OP_API_PRODUCT_SRV_0001:v1`  | —                 | —                  | Partially | Association tree must be manually traced for SP03; ~20+ associated CDS views identified from SAP documentation                  |
| Extract each associated CDS view independently into HDLFS                                                                        | SAP Datasphere Replication Flow (native S/4 on-premise ODP/SLT connector)              | `sap.s4:apiResource:OP_PRODUCT_0001:v1`          | —                 | —                  | No        | One replication flow per CDS view or logical group; initial + delta supported                                                    |
| Transform raw HDLFS data per view (type conversions, text resolution, semantic enrichment)                                       | SAP Datasphere Transformation Flow (HDLFS-to-HDLFS)                                    | —                                                | —                 | —                  | No        | All compute stays in HDLFS; one transformation flow per raw-zone table                                                           |
| Associate HDLFS files to mirror original S/4 associations and form derived data product                                          | SAP Datasphere — HDLFS file/table associations + Data Product assembly                 | —                                                | —                 | —                  | No        | Associations declared in DPD output ports; physical join done at analytic model level                                            |
| Create Datasphere Dimension views per associated entity (ProductText, ProductUoM, ProductPlant, etc.)                            | SAP Datasphere — Dimension entity type in Business Layer                               | —                                                | —                 | —                  | No        | Dimensions read from HDLFS refined zone; no transformation logic inside Datasphere                                               |
| Create central ProductAnalyticalDataset in Datasphere linking all dimensions                                                     | SAP Datasphere — Analytical Dataset entity type                                        | —                                                | —                 | —                  | No        | Star-schema model with Product as central fact/dim and all associated views as dimensions                                        |
| Match business semantics and associations of SAP managed BDC Product data product                                                | SAP Business Data Cloud managed Product data product (cloud edition)                   | —                                                | —                 | —                  | Partially | SAP managed DP targets S/4HANA Cloud; custom DPD must replicate structure, labels, and associations for SP03 on-prem             |
| Generate DPD file for custom data product registration in BDC                                                                    | Data Product Definition (DPD) — custom artifact                                        | —                                                | —                 | —                  | Yes       | Must be authored manually; covered by data-product-generation skill; ORD-based format required                                   |
| Step-by-step setup instructions (source config, replication, transformation, Datasphere models, BDC registration)                | SAP Datasphere and BDC documentation                                                   | —                                                | —                 | —                  | No        | Instructions generated as part of this solution                                                                                  |

### Key findings

- The scope is intentionally **multi-view**: `I_Product` has 20+ direct and indirect associations in SP03; every association target must be extracted as its own HDLFS persistency and transformed independently.
- The **derivation pattern** is: S/4 CDS view → HDLFS raw zone (replication flow) → HDLFS refined zone (transformation flow) → Datasphere Dimension/Dataset (semantic model) → Data Product (DPD + associations).
- All **join and association logic** lives at the Datasphere analytic model level (star schema) or is declared in the DPD output port associations — never as transformation logic inside Datasphere.
- The **DPD file** must declare one output port per HDLFS refined-zone entity and reproduce the associations from the SAP managed BDC Product DP, adapted for on-premise SP03 field names and keys.
- No MCP server is available for on-premise product APIs; replication is handled via the native Datasphere S/4 on-premise connector (RFC/ODP/SLT).
- HDLFS **zone naming convention** (raw / refined) and partition strategy (by client `MANDT`, extraction date) must be defined before replication flows are created to avoid costly re-loads.

---

## Recommendations

### Custom Data Product S/4_SP03_I_PRODUCT — Multi-View HDLFS Extraction with Datasphere Analytic Models

#### Executive Summary

Extract all I_Product associations into HDLFS, transform in place, build analytic models and register as a governed BDC data product.

#### Recommended Solution

Create the custom data product `S/4_SP03_I_PRODUCT` covering the full `I_Product` association tree. The solution has five layers:

1. **Association resolution & DPD file** — trace all CDS view associations of `I_Product` in SP03 (2023/02/00), document the complete entity catalogue, and author the `S/4_SP03_I_PRODUCT.dpd` ORD-compliant descriptor with business semantics, output ports, and associations mirroring the SAP managed BDC Product data product.

2. **HDLFS Raw Zone** — one dedicated HDLFS table/file per associated CDS view (e.g. `RAW_I_PRODUCT`, `RAW_I_PRODUCTTEXT`, `RAW_I_PRODUCTUOM`, `RAW_I_PRODUCTPLANT`, …). Populated by Datasphere Replication Flows from S/4HANA on-premise (ODP/SLT connector, initial + delta).

3. **HDLFS Refined Zone** — one Datasphere Transformation Flow per raw-zone entity producing a refined, semantically enriched output table (e.g. `REF_PRODUCT`, `REF_PRODUCTTEXT`, `REF_PRODUCTUOM`, `REF_PRODUCTPLANT`, …). All type conversions, language-dependent text joins, unit mappings, and key harmonisations run here.

4. **Datasphere Semantic Layer** — one Dimension view per refined-zone entity, plus a central `ProductAnalyticalDataset` that assembles the star schema by referencing all dimensions. Datasphere is a read-only consumer of HDLFS; no compute or transformation logic resides here.

5. **Data product assembly & registration** — the DPD declares associations between output ports (one per refined-zone entity), is validated, and registered in BDC as `S/4_SP03_I_PRODUCT`.

#### Problem Statement

On-premise S/4HANA customers on SP03 cannot use the SAP managed BDC Product data product. `I_Product` and its 20+ associated CDS views contain all product master semantics, but none of this data is available as a governed, analytics-ready data product. A structured multi-view extraction, HDLFS-based transformation, and BDC registration process is required to unlock this data for data mesh and analytics use cases.

#### Affected User Roles

- Data Product Owner / Data Steward
- SAP Datasphere Administrator
- S/4HANA Basis / Integration Consultant
- Analytics / BI Engineer (consumer of Datasphere Dimensions and Analytical Dataset)
- SAP BDC Platform Administrator

#### Important factors

##### Multi-view extraction — one flow per CDS view
Each associated CDS view is treated as an independent extraction unit. This decouples replication schedules, simplifies error isolation, and allows selective re-load of individual entities without affecting the whole data product.

##### All transformation in HDLFS — Datasphere is a pure consumer
Transformation Flows run exclusively inside HDLFS (raw → refined). Datasphere Dimension views and the Analytical Dataset read from the refined zone without any additional compute, keeping the semantic layer lightweight and portable.

##### Semantic alignment with SAP managed BDC Product DP
Field labels, descriptions, association names, and output port definitions in the DPD must match the SAP managed Product DP where technically possible, ensuring downstream consumers can migrate to the cloud edition with minimal rework.

##### S/4HANA SP03 / 2023.02.00 source specifics
The SP03 release has specific ODP extractors and CDS view annotations. Replication Flows must use the correct ODP context (`CDS_EXTRACTION`) and delta-enabled annotations (`@Analytics.dataExtraction.enabled: true`).

#### Potential risks

##### Association depth and undocumented views
Some `I_Product` associations in SP03 point to extension-include views or customer-specific appends. A full association trace must be validated in the source S/4 system before finalising the entity catalogue.

##### S/4HANA on-premise connectivity
ODP/SLT-based replication requires a Cloud Connector, appropriate S/4 authorisations, and RFC destination configuration in Datasphere. Network and firewall setup may add lead time.

##### HDLFS space sizing and partitioning
Product master data volumes vary. HDLFS partition strategy (by `MANDT`, by extraction date) must be agreed before replication flows are activated to avoid costly full re-loads.

##### Semantic drift from SAP managed DP
The SAP managed BDC Product DP evolves across BDC releases. The custom DPD must be versioned and reviewed whenever the SAP managed DP is updated.

#### Recommended solution category

Data Product (DPD), SAP Datasphere (Replication Flows, Transformation Flows, Dimensions, Analytical Dataset)

#### Intent fit
94%
