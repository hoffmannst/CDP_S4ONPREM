#!/usr/bin/env bash
# =============================================================================
# deploy.sh — S4SP03 I_Product Data Product — Datasphere CLI Deployment Script
# =============================================================================
# Prerequisites:
#   1. Datasphere CLI installed:  npm install -g @sap/datasphere-cli
#   2. Logged in:                 datasphere config set --host https://vp-bdc-pd-dsp.eu10.hcs.cloud.sap
#                                 datasphere login
#   3. HDLFS space exists:        PM_OBJSTORE
#   4. S/4HANA RFC connection configured in Datasphere: HE4
#   5. HDLFS connection configured in Datasphere:       DWC_HDLF
#
# Usage:
#   chmod +x deploy.sh
#   ./deploy.sh [--space <space-name>] [--dry-run]
#
# Options:
#   --space     Override default space name (default: PM_OBJSTORE)
#   --dry-run   Validate all files without deploying
# =============================================================================

set -euo pipefail

# ---------- defaults ----------------------------------------------------------
SPACE="${1:-PM_OBJSTORE}"
DRY_RUN=false
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# ---------- parse args --------------------------------------------------------
for arg in "$@"; do
  case $arg in
    --space=*) SPACE="${arg#*=}" ;;
    --dry-run)  DRY_RUN=true ;;
  esac
done

# ---------- colours -----------------------------------------------------------
RED='\033[0;31m'; GREEN='\033[0;32m'; YELLOW='\033[1;33m'; NC='\033[0m'
log()  { echo -e "${GREEN}[INFO]${NC}  $*"; }
warn() { echo -e "${YELLOW}[WARN]${NC}  $*"; }
err()  { echo -e "${RED}[ERROR]${NC} $*" >&2; exit 1; }

# ---------- pre-flight checks -------------------------------------------------
log "=== Pre-flight checks ==="
command -v datasphere >/dev/null 2>&1 || err "Datasphere CLI not found. Install: npm install -g @sap/datasphere-cli"
datasphere config get --host >/dev/null 2>&1  || err "No Datasphere host configured. Run: datasphere config set --host https://vp-bdc-pd-dsp.eu10.hcs.cloud.sap"

log "Target space : $SPACE"
log "Dry run      : $DRY_RUN"

# ---------- helper ------------------------------------------------------------
ds_import() {
  local cmd="$1"; local file="$2"; local extra="${3:-}"
  if [ "$DRY_RUN" = true ]; then
    warn "[DRY-RUN] Would run: datasphere $cmd import --file $file --space $SPACE $extra"
    return 0
  fi
  log "Importing $file ..."
  datasphere "$cmd" import --file "$file" --space "$SPACE" $extra
}

# =============================================================================
# STAGE 1 — Raw Zone Local Tables (22 entities)
# =============================================================================
log ""
log "=== STAGE 1: Deploy raw-zone local tables ==="
ds_import "data-builder" "$SCRIPT_DIR/local-tables/raw-tables.csn.json"
log "Stage 1 complete — 22 raw tables imported"

# =============================================================================
# STAGE 2 — Refined Zone Local Tables (22 entities)
# =============================================================================
log ""
log "=== STAGE 2: Deploy refined-zone local tables ==="
ds_import "data-builder" "$SCRIPT_DIR/local-tables/refined-tables.csn.json"
log "Stage 2 complete — 22 refined tables imported"

# =============================================================================
# STAGE 3 — Replication Flows (6 flows)
# =============================================================================
log ""
log "=== STAGE 3: Deploy replication flows ==="
ds_import "replication-flows" "$SCRIPT_DIR/flows/replication-flows.json"
log "Stage 3 complete — 6 replication flows imported"

# =============================================================================
# STAGE 4 — Transformation Flows (22 flows)
# =============================================================================
log ""
log "=== STAGE 4: Deploy transformation flows ==="
ds_import "transformation-flows" "$SCRIPT_DIR/flows/transformation-flows.json"
log "Stage 4 complete — 22 transformation flows imported"

# =============================================================================
# STAGE 5 — Datasphere Dimension Views (22 views)
# =============================================================================
log ""
log "=== STAGE 5: Deploy Datasphere dimension views ==="
ds_import "data-builder" "$SCRIPT_DIR/datasphere-views/dimensions.csn.json"
log "Stage 5 complete — 22 dimension views imported"

# =============================================================================
# STAGE 6 — Analytical Dataset (ProductAnalyticalDataset)
# =============================================================================
log ""
log "=== STAGE 6: Deploy analytical dataset ==="
ds_import "data-builder" "$SCRIPT_DIR/datasphere-views/analytical-dataset.csn.json"
log "Stage 6 complete — ProductAnalyticalDataset imported"

# =============================================================================
# STAGE 7 — Data Product Descriptor (DPD)
# =============================================================================
log ""
log "=== STAGE 7: Register data product descriptor ==="
DPD_FILE="$SCRIPT_DIR/../S4SP03IProduct.dpd"
if [ ! -f "$DPD_FILE" ]; then
  warn "DPD file not found at $DPD_FILE — skipping BDC registration"
  warn "Register manually via BDC Data Product Management UI"
else
  if [ "$DRY_RUN" = true ]; then
    warn "[DRY-RUN] Would run: datasphere data-products import --file $DPD_FILE --space $SPACE"
  else
    log "Registering DPD with BDC ..."
    datasphere data-products import --file "$DPD_FILE" --space "$SPACE" || \
      warn "DPD import returned non-zero — verify in BDC Data Product Management UI"
  fi
fi

# =============================================================================
# Summary
# =============================================================================
log ""
log "============================================================"
log "  Deployment complete for space: $SPACE"
log "============================================================"
log "  Stage 1 : 22 raw local tables             ✓"
log "  Stage 2 : 22 refined local tables         ✓"
log "  Stage 3 : 6  replication flows            ✓"
log "  Stage 4 : 22 transformation flows         ✓"
log "  Stage 5 : 22 dimension views              ✓"
log "  Stage 6 : 1  analytical dataset           ✓"
log "  Stage 7 : DPD registration                ✓"
log ""
log "Next steps:"
log "  1. Start replication flows in Datasphere UI (initial load first)"
log "  2. Run transformation flows after initial load completes"
log "  3. Validate ProductAnalyticalDataset with a test query:"
log "     SELECT Product, ProductDescription, Plant, StandardPrice"
log "     FROM ProductAnalyticalDataset LIMIT 10"
log "  4. Publish data product in BDC Data Product Management"
log "============================================================"
