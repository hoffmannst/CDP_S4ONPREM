# Transformation Flow Configurations — HDLFS Raw → HDLFS Refined

**Phase:** 5 — Transformation Flows  
**Milestone:** M4  
**All flows execute entirely within HDLFS. No transformation logic resides in Datasphere views.**

---

## Common Transformation Rules (apply to every flow)

| Rule | Detail |
|------|--------|
| Client field | Cast `MANDT` as `NVARCHAR(3)`; exclude from output if single-client landscape |
| Language resolution | Convert SAP `SPRAS` language key (e.g. `E`) to ISO 639-1 code (e.g. `EN`) using mapping table `T002` |
| Unit code conversion | Convert SAP internal unit codes to ISO units using `T006`/`T006A` mapping where applicable |
| Date casting | Cast `ERSDA` (creation date) and `LAEDA` (last change date) from `DATS` string to `DATE` type |
| CHAR field trimming | Apply `RTRIM` to all `CHAR`/`NCHAR` fields to remove trailing spaces |
| Extraction timestamp | Add column `EXTRACTION_TIMESTAMP TIMESTAMP DEFAULT CURRENT_TIMESTAMP` to all refined-zone tables |
| Deletion flag | Map `LVORM` (`X` / blank) to `BOOLEAN` `IsMarkedForDeletion` |

---

## TF-01: Product Header

**Flow:** `TF_PRODUCT`  
**Source:** `RAW_I_PRODUCT` → **Target:** `REF_PRODUCT`

### Additional Transformations
| Source Field | Target Field | Transformation |
|-------------|-------------|----------------|
| `MTART` | `ProductType` + `ProductTypeText` | Join `T134T` (language-resolved) for business label |
| `MATKL` | `ProductGroup` + `ProductGroupText` | Join `T023T` for business label |
| `MEINS` | `BaseUnit` | Convert using `T006` ISO unit mapping |
| `GEWEI` | `WeightUnit` | Convert using `T006` |
| `VOLEH` | `VolumeUnit` | Convert using `T006` |
| `MSTAE` | `CrossPlantStatus` | Map to BDC-aligned label |
| `MSTDE` | `CrossPlantStatusValidityDate` | Cast to `DATE` |
| `ERSDA` | `CreationDate` | Cast to `DATE` |
| `LAEDA` | `LastChangeDate` | Cast to `DATE` |
| `LVORM` | `IsMarkedForDeletion` | `X` → `TRUE`, blank → `FALSE` |

### Key Output Fields
`Product`, `ProductType`, `ProductTypeText`, `ProductGroup`, `ProductGroupText`, `BaseUnit`, `WeightUnit`, `GrossWeight`, `NetWeight`, `VolumeUnit`, `Volume`, `Division`, `ProductHierarchy`, `SizeOrDimensionText`, `IndustrySector`, `CrossPlantStatus`, `CrossPlantStatusValidityDate`, `CreationDate`, `LastChangeDate`, `IsMarkedForDeletion`, `EXTRACTION_TIMESTAMP`

---

## TF-02: Product Text

**Flow:** `TF_PRODUCTTEXT`  
**Source:** `RAW_I_PRODUCTDESCRIPTION` → **Target:** `REF_PRODUCTTEXT`

| Source Field | Target Field | Transformation |
|-------------|-------------|----------------|
| `SPRAS` | `Language` | ISO 639-1 via `T002` mapping |
| `MAKTX` | `ProductDescription` | `RTRIM` |
| `MAKTG` | `ProductDescriptionUpperCase` | `RTRIM` |

**Key:** `Product`, `Language`

---

## TF-03: Product Unit of Measure

**Flow:** `TF_PRODUCTUOM`  
**Source:** `RAW_I_PRODUCTUOM` → **Target:** `REF_PRODUCTUOM`

| Source Field | Target Field | Transformation |
|-------------|-------------|----------------|
| `MEINH` | `AlternativeUnit` | ISO unit via `T006` |
| `UMREZ` | `QuantityNumerator` | Cast to `DECIMAL(13,3)` |
| `UMREN` | `QuantityDenominator` | Cast to `DECIMAL(13,3)` |
| `EAN11` | `GlobalTradeItemNumber` | `RTRIM` |
| `NUMTP` | `GlobalTradeItemNumberCategory` | `RTRIM` |

**Key:** `Product`, `AlternativeUnit`

---

## TF-04: Product Plant

**Flow:** `TF_PRODUCTPLANT`  
**Source:** `RAW_I_PRODUCTPLANT` → **Target:** `REF_PRODUCTPLANT`

| Source Field | Target Field | Transformation |
|-------------|-------------|----------------|
| `PSTAT` | `MaintenanceStatusOfObject` | `RTRIM` |
| `MMSTA` | `PlantSpecificMaterialStatus` | `RTRIM` |
| `MMSTD` | `PlantSpecificStatusValidityDate` | Cast to `DATE` |
| `MTVFP` | `AvailabilityCheckType` | `RTRIM` |
| `MHDRZ` | `MinimumRemainingShelfLife` | Cast to `INTEGER` |
| `MHDLP` | `TotalShelfLife` | Cast to `INTEGER` |
| `DISGR` | `MRPGroup` | `RTRIM` |
| `DISPO` | `MRPResponsible` | `RTRIM` |

**Key:** `Product`, `Plant`

---

## TF-05: Product Storage Location

**Flow:** `TF_PRODUCTSTORAGELOC`  
**Source:** `RAW_I_PRODUCTSTORAGELOC` → **Target:** `REF_PRODUCTSTORAGELOC`

Key fields retained: `Product`, `Plant`, `StorageLocation`, `WarehouseStorageBin`, `MaximumStoragePeriod`, `EXTRACTION_TIMESTAMP`

**Key:** `Product`, `Plant`, `StorageLocation`

---

## TF-06: Product Valuation

**Flow:** `TF_PRODUCTVALUATION`  
**Source:** `RAW_I_PRODUCTVALUATION` → **Target:** `REF_PRODUCTVALUATION`

| Source Field | Target Field | Transformation |
|-------------|-------------|----------------|
| `STPRS` | `StandardPrice` | Cast to `DECIMAL(23,2)` |
| `VERPR` | `MovingAveragePrice` | Cast to `DECIMAL(23,2)` |
| `LAEPR` | `FuturePrice` | Cast to `DECIMAL(23,2)` |
| `SALK3` | `TotalStockValue` | Cast to `DECIMAL(23,2)` |
| `VPRSV` | `PriceControlIndicator` | `S` → `Standard Price`, `V` → `Moving Average Price` |
| `WAERS` | `Currency` | ISO 4217 currency code |

**Key:** `Product`, `ValuationArea`, `ValuationType`

---

## TF-07: Product Sales Delivery

**Flow:** `TF_PRODUCTSALESDELIVERY`  
**Source:** `RAW_I_PRODUCTSALESDELIVERY` → **Target:** `REF_PRODUCTSALESDELIVERY`

Key fields: `Product`, `SalesStatus`, `SalesStatusValidityDate` (cast to DATE), `TransportationGroup`, `LoadingGroup`, `GrossWeight` (DECIMAL), `NetWeight` (DECIMAL), `WeightUnit` (ISO), `Volume` (DECIMAL), `VolumeUnit` (ISO), `EXTRACTION_TIMESTAMP`

**Key:** `Product`

---

## TF-08: Product Sales Delivery Sales Org

**Flow:** `TF_PRODSALESDELIVERYSALESORG`  
**Source:** `RAW_I_PRODSALESDELIVERYSALESORG` → **Target:** `REF_PRODSALESDELIVERYSALESORG`

Key fields: `Product`, `SalesOrganization`, `DistributionChannel`, `SalesMaterialStatus`, `SalesMaterialStatusValidityDate` (cast to DATE), `MinimumOrderQuantity` (DECIMAL), `MinimumDeliveryQuantity` (DECIMAL), `EXTRACTION_TIMESTAMP`

**Key:** `Product`, `SalesOrganization`, `DistributionChannel`

---

## TF-09: Product Purchasing

**Flow:** `TF_PRODUCTPURCHASING`  
**Source:** `RAW_I_PRODUCTPURCHASING` → **Target:** `REF_PRODUCTPURCHASING`

Key fields: `Product`, `Plant`, `PurchasingGroup`, `PlannedDeliveryDurationInDays` (cast to INTEGER), `UnderdelivToleranceLevel` (DECIMAL), `OverdelivToleranceLevel` (DECIMAL), `IsAutomaticallyPurchased`, `EXTRACTION_TIMESTAMP`

**Key:** `Product`, `Plant`

---

## TF-10: Product Basic Text

**Flow:** `TF_PRODUCTBASICTEXT`  
**Source:** `RAW_I_PRODUCTBASICTEXT` → **Target:** `REF_PRODUCTBASICTEXT`

Transformations: ISO language resolution (`SPRAS` → `Language`); `RTRIM` on all text fields.

**Key:** `Product`, `Language`

---

## TF-11: Product Inspection Text

**Flow:** `TF_PRODUCTINSPECTIONTEXT`  
**Source:** `RAW_I_PRODUCTINSPECTIONTEXT` → **Target:** `REF_PRODUCTINSPECTIONTEXT`

Transformations: ISO language resolution; `RTRIM` on text fields.

**Key:** `Product`, `Language`

---

## TF-12: Product Quality Management

**Flow:** `TF_PRODUCTQUALITYMGMT`  
**Source:** `RAW_I_PRODUCTQUALITYMGMT` → **Target:** `REF_PRODUCTQUALITYMGMT`

Key fields: `Product`, `Plant`, `HasPostToInspectionStock`, `QualityInspectionGroup`, `ReorderPoint` (DECIMAL), `MaximumStockQuantity` (DECIMAL), `EXTRACTION_TIMESTAMP`

**Key:** `Product`, `Plant`

---

## TF-13: Product Plant MRP Area

**Flow:** `TF_PRODUCTPLANTMRPAREA`  
**Source:** `RAW_I_PRODUCTPLANTMRPAREA` → **Target:** `REF_PRODUCTPLANTMRPAREA`

Key fields: `Product`, `Plant`, `MRPArea`, `MRPType`, `ReorderPoint` (DECIMAL), `PlanningTimeFence` (INTEGER), `SafetyStockQuantity` (DECIMAL), `EXTRACTION_TIMESTAMP`

**Key:** `Product`, `Plant`, `MRPArea`

---

## TF-14: Product Plant Costing

**Flow:** `TF_PRODUCTPLANTCOSTING`  
**Source:** `RAW_I_PRODUCTPLANTCOSTING` → **Target:** `REF_PRODUCTPLANTCOSTING`

Key fields: `Product`, `Plant`, `CostingVariant`, `CostingLotSize` (DECIMAL), `IsCoProducedProduct`, `EXTRACTION_TIMESTAMP`

**Key:** `Product`, `Plant`, `CostingVariant`

---

## TF-15: Product Plant Forecast

**Flow:** `TF_PRODUCTPLANTFORECAST`  
**Source:** `RAW_I_PRODUCTPLANTFORECAST` → **Target:** `REF_PRODUCTPLANTFORECAST`

Key fields: `Product`, `Plant`, `ForecastModel`, `ForecastPeriodType`, `NumberOfPeriodsForBasicValue` (INTEGER), `EXTRACTION_TIMESTAMP`

**Key:** `Product`, `Plant`

---

## TF-16: Product Plant International Trade

**Flow:** `TF_PRODUCTPLANTINTLTRADE`  
**Source:** `RAW_I_PRODUCTPLANTINTLTRADE` → **Target:** `REF_PRODUCTPLANTINTLTRADE`

Key fields: `Product`, `Plant`, `CountryOfOrigin`, `RegionOfOrigin`, `CommodityCode`, `ExportAndImportProcedureCode`, `EXTRACTION_TIMESTAMP`

**Key:** `Product`, `Plant`

---

## TF-17: Product Plant Procurement

**Flow:** `TF_PRODUCTPLANTPROCUREMENT`  
**Source:** `RAW_I_PRODUCTPLANTPROCUREMENT` → **Target:** `REF_PRODUCTPLANTPROCUREMENT`

Key fields: `Product`, `Plant`, `ProcurementType`, `SpecialProcurementType`, `IsPhantomItem`, `IsAutomaticallyPurchased`, `EXTRACTION_TIMESTAMP`

**Key:** `Product`, `Plant`

---

## TF-18: Product Plant Quality Management

**Flow:** `TF_PRODUCTPLANTQUALITYMGMT`  
**Source:** `RAW_I_PRODUCTPLANTQUALITYMGMT` → **Target:** `REF_PRODUCTPLANTQUALITYMGMT`

Key fields: `Product`, `Plant`, `MaximumStoragePeriod` (INTEGER), `InspectionIntervalInDays` (INTEGER), `HasQualityInspection`, `EXTRACTION_TIMESTAMP`

**Key:** `Product`, `Plant`

---

## TF-19: Product Plant Sales

**Flow:** `TF_PRODUCTPLANTSALES`  
**Source:** `RAW_I_PRODUCTPLANTSALES` → **Target:** `REF_PRODUCTPLANTSALES`

Key fields: `Product`, `Plant`, `LoadingGroup`, `AvailabilityCheckType`, `ReplacementPartType`, `EXTRACTION_TIMESTAMP`

**Key:** `Product`, `Plant`

---

## TF-20: Product Plant Storage

**Flow:** `TF_PRODUCTPLANTSTORAGE`  
**Source:** `RAW_I_PRODUCTPLANTSTORAGE` → **Target:** `REF_PRODUCTPLANTSTORAGE`

Key fields: `Product`, `Plant`, `StorageConditions`, `TemperatureConditionIndicator`, `HazardousMaterialNumber`, `NecessaryPackagingMaterialType`, `EXTRACTION_TIMESTAMP`

**Key:** `Product`, `Plant`

---

## TF-21: Product Plant Work Scheduling

**Flow:** `TF_PRODUCTPLANTWORKSCHEDULING`  
**Source:** `RAW_I_PRODUCTPLANTWORKSCHEDULING` → **Target:** `REF_PRODUCTPLANTWORKSCHEDULING`

Key fields: `Product`, `Plant`, `ProductionSchedulerGroup`, `ProductionSupervisor`, `UnderDelivToleranceLevel` (DECIMAL), `OverDelivToleranceLevel` (DECIMAL), `SetupAndTeardownTime` (DECIMAL), `ProductionInvtryManagedLoc`, `EXTRACTION_TIMESTAMP`

**Key:** `Product`, `Plant`

---

## TF-22: Product ML Account

**Flow:** `TF_PRODUCTMLACCOUNT`  
**Source:** `RAW_I_PRODUCTMLACCOUNT` → **Target:** `REF_PRODUCTMLACCOUNT`

| Source Field | Target Field | Transformation |
|-------------|-------------|----------------|
| `SALK3` | `TotalStockValue` | Cast to `DECIMAL(23,2)` |
| `HKMAT` | `MaterialOrigin` | `RTRIM` |
| `KOSGR` | `CostingGroup` | `RTRIM` |
| `WAERS` | `Currency` | ISO 4217 |
| `PEINH` | `PriceUnitQty` | Cast to `DECIMAL(13,3)` |

**Key:** `Product`, `ValuationArea`, `ValuationType`, `CurrencyType`

---

## Transformation Flow Execution Order

1. `TF_PRODUCT` (always first — downstream flows may reference product keys)
2. `TF_PRODUCTTEXT`, `TF_PRODUCTUOM`, `TF_PRODUCTVALUATION`, `TF_PRODUCTMLACCOUNT` (parallel)
3. `TF_PRODUCTPLANT` (after TF_PRODUCT)
4. All plant sub-entity flows (TF-13 through TF-21) — parallel, after `TF_PRODUCTPLANT`
5. `TF_PRODUCTSALESDELIVERY`, `TF_PRODUCTPURCHASING`, text flows — parallel with step 4

---

## Validation Checks (run after all flows complete)

- Row counts: `REF_*` row count = `RAW_*` row count (no record loss in transformation)
- Null key check: no `NULL` values in any key field across all 22 refined tables
- Date check: all `DATE` fields in `REF_PRODUCT` are valid `YYYY-MM-DD` (no `00000000` SAP default dates leaked)
- Amount check: all `DECIMAL` fields in `REF_PRODUCTVALUATION` and `REF_PRODUCTMLACCOUNT` have 2 decimal places
- Language check: `REF_PRODUCTTEXT.Language` values are ISO 639-1 codes (e.g. `EN`, `DE`), not SAP internal codes (e.g. `E`, `D`)

---

## Milestone Log
`M4.achieved: refined zone populated for all 22 entities — transformation flows complete`
