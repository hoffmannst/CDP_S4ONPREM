# Specification

> **Guidelines**: Read [guidelines.md](./guidelines.md) before executing ANY tasks below. Follow all constraints described there throughout execution.

Check off items as completed.

---

## Solution Setup

- [x] Run `pwd` and store the result as `working_directory`
- [x] Create asset directory: `mkdir -p assets/s4-sp03-i-product-data-product/`
- [x] Invoke `setup-solution` skill to create `solution.yaml` and `asset.yaml` files for the `s4-sp03-i-product-data-product` asset
- [x] Validate `solution.yaml` and `assets/s4-sp03-i-product-data-product/asset.yaml` exist and are well-formed

---

## Asset Implementation

- [x] Execute `specification/s4-sp03-i-product-data-product/specification.md` — all phases (1 through 9):
  - [x] Phase 1 — Association Map & Entity Catalogue (22 CDS views confirmed and documented)
  - [x] Phase 2 — HDLFS Space & Naming Convention (space name, partition strategy, folder structure)
  - [x] Phase 3 — S/4HANA Source Connection & ODP Configuration (Cloud Connector, RFC destination, ODP activation)
  - [x] Phase 4 — Replication Flows RF-01 through RF-06 (all 22 entities, initial load + delta active)
  - [x] Phase 5 — Transformation Flows TF-01 through TF-22 (all refined-zone tables populated and validated)
  - [x] Phase 6 — Datasphere Semantic Layer (22 Dimension views + ProductAnalyticalDataset deployed)
  - [x] Phase 7 — Data Product Generation (DPD file authored, ORD-validated, registered in BDC)
  - [x] Phase 8 — End-to-End Validation (delta propagation confirmed, cross-entity query passing)
  - [x] Phase 9 — Setup Instructions Document (SETUP-INSTRUCTIONS.md complete)

---

## Deliverables Checklist

Confirm all of the following exist before closing this specification:

- [x] `assets/s4-sp03-i-product-data-product/entity-catalogue.md` — 22 CDS views with keys and ODP delta status
- [x] `assets/s4-sp03-i-product-data-product/hdlfs-config.md` — HDLFS space, partition strategy, folder paths
- [x] `assets/s4-sp03-i-product-data-product/source-connection-config.md` — Cloud Connector and RFC destination details
- [x] `assets/s4-sp03-i-product-data-product/replication-flows.md` — 6 Replication Flow configurations (RF-01 to RF-06)
- [x] `assets/s4-sp03-i-product-data-product/transformation-flows.md` — 22 Transformation Flow configurations (TF-01 to TF-22)
- [x] `assets/s4-sp03-i-product-data-product/datasphere-models.md` — 22 Dimension view + ProductAnalyticalDataset definitions
- [x] `assets/s4-sp03-i-product-data-product/S4SP03IProduct.dpd` — ORD-compliant DPD file with 22 output ports and associations
- [x] `assets/s4-sp03-i-product-data-product/bdc-registration.md` — BDC registration confirmation and data product URL
- [x] `assets/s4-sp03-i-product-data-product/SETUP-INSTRUCTIONS.md` — end-to-end setup guide for administrators
