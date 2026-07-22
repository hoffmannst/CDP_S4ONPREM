# Source Connection Configuration — S/4HANA SP03 to Datasphere

**Phase:** 3 — S/4HANA Source Connection & ODP Configuration

---

## Prerequisites

| Component | Requirement |
|-----------|-------------|
| SAP Cloud Connector | Version 2.15 or higher; installed in the on-premise network segment that can reach S/4HANA SP03 |
| SAP BTP Subaccount | Linked to the customer Datasphere tenant |
| S/4HANA SP03 user | RFC-enabled user with authorisation objects: `S_RFC`, `S_TABU_DIS` (for ODP), `S_ODP_READ` |
| S/4HANA ODP activations | All 22 CDS views activated in ODP via transaction `RODPS_REPL_TEST` |
| Datasphere RFC connection | Configured in Datasphere → System → Connections → New Connection (type: SAP S/4HANA) |

---

## Cloud Connector Setup

### Step 1 — Register Cloud Connector in BTP Subaccount
1. Log in to SAP BTP Cockpit → your subaccount.
2. Navigate to **Connectivity → Cloud Connectors**.
3. Confirm the Cloud Connector appears with status **Connected**.
4. Note the **Location ID** (leave blank for default, or set a unique ID for multi-CC environments).

### Step 2 — Add S/4HANA System in Cloud Connector
1. In Cloud Connector Administration UI → **Cloud To On-Premise → Access Control**.
2. Add a new mapping:
   - **Back-end Type:** SAP ABAP
   - **Protocol:** RFC
   - **Internal Host:** `<S4HANA_HOST>` (internal hostname or IP)
   - **Internal Port:** `33<instance_number>` (e.g. `3300` for instance 00)
   - **Virtual Host:** `S4H-SP03-RFC`
   - **Virtual Port:** `3300`
3. Add the following resources under the mapping:
   - `FUNCTION_GROUP=RSODP*` (ODP extraction function modules)
   - `FUNCTION_GROUP=RFC1` (RFC connectivity test)

### Step 3 — Test Cloud Connector Connectivity
- In Cloud Connector, select the mapping and click **Check Availability**.
- Expected result: **Reachable**.

---

## RFC Destination in Datasphere

### Step 4 — Create RFC Connection in Datasphere
1. In Datasphere → **System → Connections → + (New Connection)**.
2. Select connection type: **SAP S/4HANA**.
3. Fill in:
   - **Connection Name:** `HE4`
   - **Description:** `S/4HANA on-premise SP03 — product master extraction`
   - **Host:** `S4H-SP03-RFC` (virtual host from Cloud Connector)
   - **Instance Number:** `<instance_number>` (e.g. `00`)
   - **Client:** `<MANDT>` (e.g. `100`)
   - **Language:** `EN`
   - **User:** `<RFC_USER>`
   - **Password:** `<RFC_PASSWORD>`
   - **Cloud Connector Location ID:** *(leave blank if default, or enter Location ID)*
4. Click **Test Connection** — expected result: **Successful**.
5. Save as `HE4`.

---

## ODP Extractor Activation in S/4HANA

### Step 5 — Activate ODP Replication for All 22 CDS Views

Run transaction `RODPS_REPL_TEST` (or use SE38 to run program `RODPS_REPLICATION_TEST`) for each CDS view:

```
ODP Context: CDS_EXTRACTION
Provider:    <CDS_VIEW_NAME>   (e.g. I_PRODUCT)
Mode:        Full
```

Verify:
- Status: **Active**
- Delta method: **After Image** or **AIM** (for most S/4HANA CDS views)
- No errors in the extraction test log

Repeat for all 22 views listed in `entity-catalogue.md`.

### Step 6 — Authorisation Check

Ensure the RFC user has the following authorisation objects in S/4HANA:

| Auth Object | Field | Value |
|-------------|-------|-------|
| `S_RFC` | `RFC_TYPE` | `FUGR` |
| `S_RFC` | `RFC_NAME` | `RSODP*`, `RFC1` |
| `S_RFC` | `ACTVT` | `16` (Execute) |
| `S_ODP_READ` | `ODP_CONTX` | `CDS_EXTRACTION` |
| `S_ODP_READ` | `ODP_NAME` | `I_PRODUCT*` (wildcard covering all 22 views) |
| `S_ODP_READ` | `ACTVT` | `03` (Read) |

---

## Connection Validation Checklist

- [ ] Cloud Connector shows S/4HANA system as **Reachable**
- [ ] Datasphere connection `HE4` shows **Test Connection: Successful**
- [ ] ODP activated for all 22 CDS views (`RODPS_REPL_TEST` — no errors)
- [ ] RFC user authorisations verified
- [ ] Test extraction of `I_Product` (100 rows limit) returns records in HDLFS raw zone

---

## Notes

- The connection name `HE4` is referenced in all 6 Replication Flow configurations (see `replication-flows.md`).
- If multiple S/4HANA clients exist, create one connection per client and adjust the `MANDT` partition accordingly.
- Keep RFC user password in a Datasphere credential store; do not hardcode in flow configurations.
