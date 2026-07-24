# Replication Flow Configurations — S/4HANA SP03 → HDLFS Raw Zone

**Phase:** 4 — Replication Flows  
**Milestone:** M3  
**Source Connection:** `HE4`  
**HDLFS Space:** `PRODUCT_MASTER_HDLFS`  
**ODP Context:** `CDS_EXTRACTION`  
**Load Type:** Initial Load + Delta (After Image)

---

## Overview

| Flow ID | Flow Name | Entities Covered | CDS Views |
|---------|-----------|-----------------|-----------|
| RF-01 | `RF_S4SP03_PRODUCT_CORE` | Product header, texts, units of measure, valuation, ML account | 5 |
| RF-02 | `RF_S4SP03_PRODUCT_SALES_PURCH` | Sales delivery, procurement | 2 |
| RF-03 | `RF_S4SP03_PRODUCT_PLANT_CORE` | Plant data, storage locations | 2 |
| RF-04 | `RF_S4SP03_PRODUCT_PLANT_EXT1` | MRP area, costing, forecast, intl trade | 4 |
| RF-05 | `RF_S4SP03_PRODUCT_PLANT_EXT2` | Procurement, quality, plant sales, storage, work scheduling | 5 |
| RF-06 | `RF_S4SP03_PRODUCT_DESCRIPTIONS` | Basic texts, inspection texts, quality management | 3 |

---

## RF-01: Product Core

**Flow Name:** `RF_S4SP03_PRODUCT_CORE`  
**Description:** Extracts the product master header and its primary non-plant associations.

| Property | Value |
|----------|-------|
| Source Connection | `HE4` |
| ODP Context | `CDS_EXTRACTION` |
| Load Type | Initial + Delta |
| Partition Key | `MANDT` |
| Delta Mode | After Image |

### Target Mappings

| Source CDS View | Target HDLFS Table | HDLFS Path |
|----------------|-------------------|-----------|
| `I_PRODUCT` | `RAW_I_PRODUCT` | `product-master/raw/I_PRODUCT/` |
| `I_PRODUCTDESCRIPTION` | `RAW_I_PRODUCTDESCRIPTION` | `product-master/raw/I_PRODUCTDESCRIPTION/` |
| `I_PRODUCTUNITSOFMEASURE` | `RAW_I_PRODUCTUNITSOFMEASURE` | `product-master/raw/I_PRODUCTUNITSOFMEASURE/` |
| `I_PRODUCTVALUATION` | `RAW_I_PRODUCTVALUATION` | `product-master/raw/I_PRODUCTVALUATION/` |
| `I_PRODUCTMLACCOUNT` | `RAW_I_PRODUCTMLACCOUNT` | `product-master/raw/I_PRODUCTMLACCOUNT/` |

### Key Fields (filter / partition)
- `I_PRODUCT`: key = `MANDT`, `MATNR`
- `I_PRODUCTDESCRIPTION`: key = `MANDT`, `MATNR`, `SPRAS`
- `I_PRODUCTUNITSOFMEASURE`: key = `MANDT`, `MATNR`, `MEINH`
- `I_PRODUCTVALUATION`: key = `MANDT`, `MATNR`, `BWKEY`, `BWTAR`
- `I_PRODUCTMLACCOUNT`: key = `MANDT`, `MATNR`, `BWKEY`, `BWTAR`, `PEINH`

### Validation
- Row count `RAW_I_PRODUCT` ≥ number of materials in `MARA` table in S/4HANA
- Row count `RAW_I_PRODUCTDESCRIPTION` ≥ `RAW_I_PRODUCT` rows × number of active languages
- Delta test: update `MAKTX` on one material; confirm change arrives in `RAW_I_PRODUCTDESCRIPTION` within delta cycle
- Delta test: update a unit of measure conversion on one material; confirm change arrives in `RAW_I_PRODUCTUNITSOFMEASURE` within delta cycle

---

## RF-02: Sales & Purchasing

**Flow Name:** `RF_S4SP03_PRODUCT_SALES_PURCH`

| Target HDLFS Table | Source CDS View | Key Fields |
|--------------------|----------------|-----------|
| `RAW_I_PRODUCTSALESDELIVERY` | `I_PRODUCTSALESDELIVERY` | `MANDT`, `MATNR`, `VKORG`, `VTWEG` |
| `RAW_I_PRODUCTPROCUREMENT` | `I_PRODUCTPROCUREMENT` | `MANDT`, `MATNR` |

### Validation
- Row count `RAW_I_PRODUCTSALESDELIVERY` = number of product × sales org × distribution channel combinations active in the source system

---

## RF-03: Plant Core

**Flow Name:** `RF_S4SP03_PRODUCT_PLANT_CORE`

| Target HDLFS Table | Source CDS View | Key Fields |
|--------------------|----------------|-----------|
| `RAW_I_PRODUCTPLANT` | `I_PRODUCTPLANT` | `MANDT`, `MATNR`, `WERKS` |
| `RAW_I_PRODUCTSTORAGELOC` | `I_PRODUCTSTORAGELOC` | `MANDT`, `MATNR`, `WERKS`, `LGORT` |

### Validation
- Row count `RAW_I_PRODUCTPLANT` = number of `MARC` records in S/4HANA
- Row count `RAW_I_PRODUCTSTORAGELOC` = number of `MARD` records

---

## RF-04: Plant Extensions 1

**Flow Name:** `RF_S4SP03_PRODUCT_PLANT_EXT1`

| Target HDLFS Table | Source CDS View | Key Fields |
|--------------------|----------------|-----------|
| `RAW_I_PRODUCTPLANTMRPAREA` | `I_PRODUCTPLANTMRPAREA` | `MANDT`, `MATNR`, `WERKS`, `BERID` |
| `RAW_I_PRODUCTPLANTCOSTING` | `I_PRODUCTPLANTCOSTING` | `MANDT`, `MATNR`, `WERKS`, `KLVAR` |
| `RAW_I_PRODUCTPLANTFORECAST` | `I_PRODUCTPLANTFORECAST` | `MANDT`, `MATNR`, `WERKS` |
| `RAW_I_PRODPLNTINTERNATIONALTRADE` | `I_PRODPLNTINTERNATIONALTRADE` | `MANDT`, `MATNR`, `WERKS` |

---

## RF-05: Plant Extensions 2

**Flow Name:** `RF_S4SP03_PRODUCT_PLANT_EXT2`

| Target HDLFS Table | Source CDS View | Key Fields |
|--------------------|----------------|-----------|
| `RAW_I_PRODUCTPLANTPROCUREMENT` | `I_PRODUCTPLANTPROCUREMENT` | `MANDT`, `MATNR`, `WERKS` |
| `RAW_I_PRODUCTPLANTQUALITYMANAGEMENT` | `I_PRODUCTPLANTQUALITYMANAGEMENT` | `MANDT`, `MATNR`, `WERKS` |
| `RAW_I_PRODUCTPLANTSALES` | `I_PRODUCTPLANTSALES` | `MANDT`, `MATNR`, `WERKS` |
| `RAW_I_PRODUCTPLANTSTORAGE` | `I_PRODUCTPLANTSTORAGE` | `MANDT`, `MATNR`, `WERKS` |
| `RAW_I_PRODUCTPLANTWORKSCHEDULING` | `I_PRODUCTPLANTWORKSCHEDULING` | `MANDT`, `MATNR`, `WERKS` |

---

## RF-06: Texts & Quality

**Flow Name:** `RF_S4SP03_PRODUCT_DESCRIPTIONS`

| Target HDLFS Table | Source CDS View | Key Fields |
|--------------------|----------------|-----------|
| `RAW_I_PRODUCTBASICTEXTS` | `I_PRODUCTBASICTEXTS` | `MANDT`, `MATNR`, `SPRAS`, `TXTTYPCODE` |
| `RAW_I_PRODUCTINSPECTIONTEXTS` | `I_PRODUCTINSPECTIONTEXTS` | `MANDT`, `MATNR`, `SPRAS`, `TXTTYPCODE` |
| `RAW_I_PRODUCTQUALITYMANAGEMENT` | `I_PRODUCTQUALITYMANAGEMENT` | `MANDT`, `MATNR` |

---

## Activation Sequence

Run flows in this order to respect referential integrity during initial load:

1. RF-01 (header first)
2. RF-02, RF-06 (non-plant associations — parallel OK)
3. RF-03 (plant core)
4. RF-04, RF-05 (plant sub-entities — parallel OK, only after RF-03 initial load completes)

---

## Delta Schedule (Recommended)

| Flow | Recommended Delta Frequency |
|------|-----------------------------|
| RF-01 (`I_PRODUCT` header) | Every 15 minutes |
| RF-01 (`I_PRODUCTDESCRIPTION`) | Every 60 minutes |
| RF-02 (Sales/Purchasing) | Every 60 minutes |
| RF-03 (Plant core) | Every 30 minutes |
| RF-04, RF-05 (Plant sub) | Every 60 minutes |
| RF-06 (Texts) | Every 60 minutes |

> Adjust based on S/4HANA system load and business requirements.

---

## Milestone Log
`M3.achieved: initial load complete for all 6 replication flows — 21 entities`
