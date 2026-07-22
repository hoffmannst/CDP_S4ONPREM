# HDLFS Configuration — S/4_SP03_I_PRODUCT Data Product

**Milestone:** M2

---

## HDLFS Space

| Property | Value |
|----------|-------|
| Space Name | `PRODUCT_MASTER_HDLFS` *(confirm with Datasphere Administrator before creating flows)* |
| Space Type | SAP HANA Data Lake File Store (HDLFS) |
| Datasphere Tenant | *(your Datasphere tenant URL)* |
| Storage Estimate | ~50–200 GB depending on product master volume (see per-entity estimates below) |

---

## Zone Structure

### Raw Zone
Landing area for replicated S/4HANA data. Data arrives as-is from ODP extractors.

```
<PRODUCT_MASTER_HDLFS>/
└── product-master/
    └── raw/
        ├── I_PRODUCT/
        ├── I_PRODUCTTEXT/
        ├── I_PRODUCTUOM/
        ├── I_PRODUCTPLANT/
        ├── I_PRODUCTSTORAGELOC/
        ├── I_PRODUCTVALUATION/
        ├── I_PRODUCTSALESDELIVERY/
        ├── I_PRODSALESDELIVERYSALESORG/
        ├── I_PRODUCTPURCHASING/
        ├── I_PRODUCTBASICTEXT/
        ├── I_PRODUCTINSPECTIONTEXT/
        ├── I_PRODUCTQUALITYMGMT/
        ├── I_PRODUCTPLANTMRPAREA/
        ├── I_PRODUCTPLANTCOSTING/
        ├── I_PRODUCTPLANTFORECAST/
        ├── I_PRODUCTPLANTINTLTRADE/
        ├── I_PRODUCTPLANTPROCUREMENT/
        ├── I_PRODUCTPLANTQUALITYMGMT/
        ├── I_PRODUCTPLANTSALES/
        ├── I_PRODUCTPLANTSTORAGE/
        ├── I_PRODUCTPLANTWORKSCHEDULING/
        └── I_PRODUCTMLACCOUNT/
```

### Refined Zone
Output of Datasphere Transformation Flows. Contains cleansed, semantically enriched data.

```
<PRODUCT_MASTER_HDLFS>/
└── product-master/
    └── refined/
        ├── PRODUCT/
        ├── PRODUCTTEXT/
        ├── PRODUCTUOM/
        ├── PRODUCTPLANT/
        ├── PRODUCTSTORAGELOC/
        ├── PRODUCTVALUATION/
        ├── PRODUCTSALESDELIVERY/
        ├── PRODSALESDELIVERYSALESORG/
        ├── PRODUCTPURCHASING/
        ├── PRODUCTBASICTEXT/
        ├── PRODUCTINSPECTIONTEXT/
        ├── PRODUCTQUALITYMGMT/
        ├── PRODUCTPLANTMRPAREA/
        ├── PRODUCTPLANTCOSTING/
        ├── PRODUCTPLANTFORECAST/
        ├── PRODUCTPLANTINTLTRADE/
        ├── PRODUCTPLANTPROCUREMENT/
        ├── PRODUCTPLANTQUALITYMGMT/
        ├── PRODUCTPLANTSALES/
        ├── PRODUCTPLANTSTORAGE/
        ├── PRODUCTPLANTWORKSCHEDULING/
        └── PRODUCTMLACCOUNT/
```

---

## Naming Convention

| Zone | Table/File Prefix | Example |
|------|------------------|---------|
| Raw | `RAW_<CDS_VIEW_NAME>` | `RAW_I_PRODUCT` |
| Refined | `REF_<ENTITY_NAME>` | `REF_PRODUCT` |
| Datasphere Dimension | `DIM_<ENTITY_NAME>` | `DIM_PRODUCT` |
| Replication Flow | `RF_S4SP03_<GROUP>` | `RF_S4SP03_PRODUCT_CORE` |
| Transformation Flow | `TF_<ENTITY_NAME>` | `TF_PRODUCT` |

---

## Partition Strategy

| Property | Value |
|----------|-------|
| Primary partition key | `MANDT` (SAP Client — typically `100` or `200`) |
| Secondary partition key | `EXTRACTION_DATE` (date of extraction, format `YYYY-MM-DD`) |
| Partition granularity | Daily |
| Rationale | Allows targeted re-load of a single day without full table reload; supports multi-client landscapes |

---

## Per-Entity Storage Estimates

| Entity | Estimated Rows | Avg Row Size | Estimated Size |
|--------|---------------|--------------|----------------|
| `RAW_I_PRODUCT` | 100K–1M | 2 KB | 200 MB–2 GB |
| `RAW_I_PRODUCTTEXT` | 300K–3M | 0.5 KB | 150 MB–1.5 GB |
| `RAW_I_PRODUCTUOM` | 500K–5M | 0.3 KB | 150 MB–1.5 GB |
| `RAW_I_PRODUCTPLANT` | 200K–2M | 3 KB | 600 MB–6 GB |
| `RAW_I_PRODUCTSTORAGELOC` | 50K–500K | 0.5 KB | 25 MB–250 MB |
| `RAW_I_PRODUCTVALUATION` | 100K–1M | 1 KB | 100 MB–1 GB |
| `RAW_I_PRODUCTSALESDELIVERY` | 100K–500K | 1.5 KB | 150 MB–750 MB |
| `RAW_I_PRODSALESDELIVERYSALESORG` | 200K–1M | 1.5 KB | 300 MB–1.5 GB |
| `RAW_I_PRODUCTPURCHASING` | 100K–500K | 1 KB | 100 MB–500 MB |
| Plant sub-entities (×9) | 50K–500K each | 0.5–1 KB | ~50–500 MB each |
| Texts + Quality + ML (×4) | 50K–200K each | 0.3–1 KB | ~15–200 MB each |
| **Total (raw + refined)** | | | **~5–30 GB** |

> These are indicative estimates. Actual sizing depends on the number of active products, plants, and languages in the customer system. Provision at least **50 GB** as a baseline; expand as needed.

---

## Milestone Log
`M2.achieved: HDLFS raw zone provisioned — 22 tables created`
