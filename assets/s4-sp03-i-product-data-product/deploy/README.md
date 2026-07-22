# Deploy Package — S4SP03 I_Product Data Product

This folder contains all deployable artifacts for the `S/4_SP03_I_PRODUCT` custom data product. Every file is ready to be consumed by the **Datasphere CLI** (`datasphere` command).

---

## Folder Structure

```
deploy/
├── README.md                              ← this file
├── deploy.sh                              ← master deployment script (runs all 7 stages)
├── local-tables/
│   ├── raw-tables.csn.json                ← 22 RAW_* entities (HDLFS raw zone)
│   └── refined-tables.csn.json           ← 22 REF_* entities (HDLFS refined zone)
├── flows/
│   ├── replication-flows.json             ← 6 Replication Flows (S/4 ODP → HDLFS raw)
│   └── transformation-flows.json         ← 22 Transformation Flows (raw → refined)
└── datasphere-views/
    ├── dimensions.csn.json                ← 22 DIM_* Dimension views (Datasphere semantic layer)
    └── analytical-dataset.csn.json       ← ProductAnalyticalDataset (ANALYTICAL_CUBE)
```

The DPD file (`S4SP03IProduct.dpd`) is one level up in `assets/s4-sp03-i-product-data-product/`.

---

## Prerequisites

| Requirement | Command / Notes |
|-------------|----------------|
| Datasphere CLI | `npm install -g @sap/datasphere-cli` |
| CLI login | `datasphere config set --host https://vp-bdc-pd-dsp.eu10.hcs.cloud.sap` then `datasphere login` |
| HDLFS space | Must exist: `PM_OBJSTORE` |
| S/4 RFC connection | Must be configured in Datasphere: `HE4` |
| HDLFS connection | Must be configured in Datasphere: `DWC_HDLF` |

---

## Deployment

### Option A — Full automated deployment (recommended)

```bash
cd deploy/
chmod +x deploy.sh
./deploy.sh
```

Override the space name if needed:

```bash
./deploy.sh --space MY_CUSTOM_SPACE
```

Validate without deploying (dry run):

```bash
./deploy.sh --dry-run
```

### Option B — Stage-by-stage manual deployment

Run each stage independently using the Datasphere CLI:

**Stage 1 — Raw tables (HDLFS raw zone)**
```bash
datasphere data-builder import \
  --file local-tables/raw-tables.csn.json \
  --space PM_OBJSTORE
```

**Stage 2 — Refined tables (HDLFS refined zone)**
```bash
datasphere data-builder import \
  --file local-tables/refined-tables.csn.json \
  --space PM_OBJSTORE
```

**Stage 3 — Replication Flows (6 flows)**
```bash
datasphere replication-flows import \
  --file flows/replication-flows.json \
  --space PM_OBJSTORE
```

**Stage 4 — Transformation Flows (22 flows)**
```bash
datasphere transformation-flows import \
  --file flows/transformation-flows.json \
  --space PM_OBJSTORE
```

**Stage 5 — Dimension views (22 DIM_* views)**
```bash
datasphere data-builder import \
  --file datasphere-views/dimensions.csn.json \
  --space PM_OBJSTORE
```

**Stage 6 — Analytical Dataset**
```bash
datasphere data-builder import \
  --file datasphere-views/analytical-dataset.csn.json \
  --space PM_OBJSTORE
```

**Stage 7 — Data Product Descriptor (BDC)**
```bash
datasphere data-products import \
  --file ../S4SP03IProduct.dpd \
  --space PM_OBJSTORE
```

---

## Deployment Order — Why It Matters

The stages must be run in order because of dependencies:

```
[Stage 1] RAW tables ──► [Stage 3] Replication Flows (write to RAW)
[Stage 2] REF tables ──► [Stage 4] Transformation Flows (read RAW, write REF)
[Stage 5] DIM views  ──► depend on REF tables existing
[Stage 6] Analytical Dataset ──► depends on all 22 DIM views
[Stage 7] DPD ──► registers the dataset as a BDC data product
```

---

## Post-Deployment Validation

Run this test query in Datasphere's SQL console after all stages complete:

```sql
SELECT
  p.Product,
  t.ProductDescription,
  pp.Plant,
  v.StandardPrice,
  v.Currency,
  sl.StorageLocation
FROM ProductAnalyticalDataset p
LEFT JOIN DIM_PRODUCTTEXT    t  ON t.Product = p.Product AND t.Language = 'E'
LEFT JOIN DIM_PRODUCTPLANT   pp ON pp.Product = p.Product
LEFT JOIN DIM_PRODUCTVALUATION v ON v.Product = p.Product
LEFT JOIN DIM_PRODUCTSTORAGELOC sl ON sl.Product = p.Product AND sl.Plant = pp.Plant
LIMIT 10;
```

---

## Field Naming Convention

All refined and view names follow the SAP-aligned semantic naming used in the SAP managed BDC Product data product:

| Layer | Prefix | Example |
|-------|--------|---------|
| Raw zone (HDLFS) | `RAW_` | `RAW_I_PRODUCT` |
| Refined zone (HDLFS) | `REF_` | `REF_PRODUCT` |
| Datasphere Dimension | `DIM_` | `DIM_PRODUCT` |
| Datasphere Analytical Dataset | *(none)* | `ProductAnalyticalDataset` |

ABAP field names (e.g. `MATNR`, `WERKS`, `BWKEY`) are fully converted to semantic names (e.g. `Product`, `Plant`, `ValuationArea`) during the transformation flows (Stage 4).

---

## Troubleshooting

| Symptom | Likely cause | Resolution |
|---------|-------------|------------|
| `connection refused` on RF run | RFC destination not active | Check Cloud Connector + SM59 in S/4 |
| `ODP object not found` | CDS view not ODP-activated | Run `RODPS_REPL_TEST` in S/4, activate extraction |
| `target table not found` | Stage 2 not yet deployed | Run stages in order |
| DPD import fails | BDC not connected | Register via BDC Data Product Management UI manually |
