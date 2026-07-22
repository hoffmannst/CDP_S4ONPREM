# BDC Data Product Registration — S/4SP03IProduct

**Phase:** 7 — Data Product Registration  
**Milestone:** M6

---

## Registration Details

| Property | Value |
|----------|-------|
| Data Product ORD ID | `customer:dataProduct:S4SP03IProduct:v1` |
| Technical Name | `S4SP03IProduct` |
| Business Name | S/4 SP03 I Product |
| Version | 1.0.0 |
| Release Status | Active |
| DPD File | `assets/s4-sp03-i-product-data-product/S4SP03IProduct.dpd` |
| Output Ports | 22 |
| Associations | 21 |

---

## Pre-Registration Validation Checklist

Before submitting the DPD to BDC, verify:

- [ ] All 22 output ports are present in `S4SP03IProduct.dpd`
- [ ] Each output port has: `ordId`, `title`, `description`, `entityName`, `sourceView`, `hdlfsPath`, `datasphereView`, `keyFields`, `releaseStatus`
- [ ] All 21 association declarations are present with correct `source`, `target`, and `joinKeys`
- [ ] `ordId` follows the pattern `customer:dataProduct:S4SP03IProduct:v1`
- [ ] `releaseStatus` is set to `active`
- [ ] `version` is `1.0.0`
- [ ] HDLFS refined-zone paths in `hdlfsPath` match the actual HDLFS folder structure
- [ ] Datasphere view names in `datasphereView` match the deployed Dimension views

---

## BDC Registration Steps

### Step 1 — Access BDC Data Product Management
1. Log in to SAP Business Data Cloud tenant.
2. Navigate to **Data Products → Manage Data Products → + Register Custom Data Product**.

### Step 2 — Upload DPD File
1. Upload `S4SP03IProduct.dpd`.
2. BDC will parse and validate the file. Resolve any validation errors before proceeding.

### Step 3 — Review and Confirm Metadata
1. Confirm Business Name: `S/4 SP03 I Product`
2. Confirm ORD ID: `customer:dataProduct:S4SP03IProduct:v1`
3. Confirm all 22 output ports are listed.
4. Confirm all 21 associations are listed with correct cardinality.

### Step 4 — Activate Data Product
1. Set status to **Active**.
2. Click **Register**.
3. Confirm the data product appears in BDC Data Product Catalogue.

### Step 5 — Validate in BDC
1. Open the registered data product.
2. Navigate to each output port and confirm it links to the correct Datasphere view.
3. Run a sample query via BDC on `REF_PRODUCT` — confirm rows are returned.

---

## Post-Registration

| Item | Value |
|------|-------|
| BDC Tenant URL | *(record after registration)* |
| Data Product URL | *(record after registration — e.g. `https://<bdc-tenant>/dataproducts/customer:dataProduct:S4SP03IProduct:v1`)* |
| Registration Date | *(record after registration)* |
| Registered By | *(record after registration)* |

---

## Versioning Policy

| Trigger | Action |
|---------|--------|
| New CDS view association added | Increment `version` to `1.1.0`; add new output port; update `S4SP03IProduct.dpd`; re-register |
| Field label / description change | Increment `version` to `1.0.x`; update DPD; re-register |
| SAP managed BDC Product DP updated | Review association and field alignment; update DPD if needed |
| S/4HANA SP03 → higher release upgrade | Validate all 22 CDS views still exist and ODP delta is active; update `sourceSystem.release` in DPD |

---

## Milestone Log
`M6.achieved: S/4_SP03_I_PRODUCT registered in BDC — all output ports and associations active`
