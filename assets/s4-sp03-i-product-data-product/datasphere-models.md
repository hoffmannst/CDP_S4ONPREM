# Datasphere Semantic Layer — Dimension Views & Analytical Dataset

**Phase:** 6 — Datasphere Semantic Layer  
**Milestone:** M5  
**All views are read-only consumers of HDLFS refined zone. No transformation logic in any Datasphere view.**

---

## Design Principles

- Each Datasphere Dimension view maps 1:1 to one HDLFS refined-zone table.
- Dimensions carry business field labels aligned to the SAP managed BDC Product data product.
- Associations between dimensions are declared at the Datasphere model level (not in HDLFS).
- The central `ProductAnalyticalDataset` assembles all dimensions into a star schema.
- Semantic type for header: `#ANALYTICAL_CUBE` on the Analytical Dataset.
- All Dimension views use semantic type `Dimension`.

---

## Dimension Views (21 total)

### DIM_PRODUCT
**Source:** `REF_PRODUCT` | **Semantic Type:** Dimension | **Key:** `Product`

| Column | Business Label | Type |
|--------|---------------|------|
| `Product` | Product | Key (NVARCHAR 40) |
| `ProductType` | Product Type | NVARCHAR 4 |
| `ProductTypeText` | Product Type Description | NVARCHAR 20 |
| `ProductGroup` | Product Group | NVARCHAR 9 |
| `ProductGroupText` | Product Group Description | NVARCHAR 20 |
| `BaseUnit` | Base Unit of Measure | NVARCHAR 3 |
| `WeightUnit` | Weight Unit | NVARCHAR 3 |
| `GrossWeight` | Gross Weight | DECIMAL 13,3 |
| `NetWeight` | Net Weight | DECIMAL 13,3 |
| `VolumeUnit` | Volume Unit | NVARCHAR 3 |
| `Volume` | Volume | DECIMAL 13,3 |
| `Division` | Division | NVARCHAR 2 |
| `ProductHierarchy` | Product Hierarchy | NVARCHAR 18 |
| `SizeOrDimensionText` | Size / Dimension | NVARCHAR 32 |
| `IndustrySector` | Industry Sector | NVARCHAR 1 |
| `CrossPlantStatus` | Cross-Plant Material Status | NVARCHAR 2 |
| `CrossPlantStatusValidityDate` | Cross-Plant Status Valid From | DATE |
| `CreationDate` | Created On | DATE |
| `LastChangeDate` | Last Changed On | DATE |
| `IsMarkedForDeletion` | Deletion Flag | BOOLEAN |

**Associations declared on DIM_PRODUCT:**
- `_Text` → `DIM_PRODUCTTEXT` (via `Product`)
- `_ProductUnitsOfMeasure` → `DIM_PRODUCTUNITSOFMEASURE` (via `Product`)
- `_ProductValuation` → `DIM_PRODUCTVALUATION` (via `Product`)
- `_MLAccount` → `DIM_PRODUCTMLACCOUNT` (via `Product`)
- `_SalesDelivery` → `DIM_PRODUCTSALESDELIVERY` (via `Product`, `SalesOrganization`, `DistributionChannel`)
- `_Procurement` → `DIM_PRODUCTPROCUREMENT` (via `Product`)
- `_BasicText` → `DIM_PRODUCTBASICTEXTS` (via `Product`)
- `_InspectionText` → `DIM_PRODUCTINSPECTIONTEXTS` (via `Product`)
- `_QualityMgmt` → `DIM_PRODUCTQUALITYMANAGEMENT` (via `Product`)
- `_ProductPlant` → `DIM_PRODUCTPLANT` (via `Product`)

---

### DIM_PRODUCTTEXT
**Source:** `REF_PRODUCTTEXT` | **Key:** `Product`, `Language`  
**Columns:** `Product`, `Language` (Business Label: Language), `ProductDescription`, `ProductDescriptionUpperCase`  
**Association:** `_Product` → `DIM_PRODUCT` (via `Product`) — text association

---

### DIM_PRODUCTUNITSOFMEASURE
**Source:** `REF_PRODUCTUNITSOFMEASURE` | **Key:** `Product`, `AlternativeUnit`  
**Columns:** `Product`, `AlternativeUnit` (Alternative Unit of Measure), `QuantityNumerator`, `QuantityDenominator`, `GlobalTradeItemNumber`, `GlobalTradeItemNumberCategory`  
**Association:** `_Product` → `DIM_PRODUCT`

---

### DIM_PRODUCTPLANT
**Source:** `REF_PRODUCTPLANT` | **Key:** `Product`, `Plant`  
**Key Columns:** `Product`, `Plant`, `MaintenanceStatusOfObject`, `PlantSpecificMaterialStatus`, `PlantSpecificStatusValidityDate`, `AvailabilityCheckType`, `MRPGroup`, `MRPResponsible`, `MinimumRemainingShelfLife`, `TotalShelfLife`  
**Associations:**
- `_Product` → `DIM_PRODUCT`
- `_ProductStorageLocation` → `DIM_PRODUCTSTORAGELOC` (via `Product`, `Plant`)
- `_PlantMRPArea` → `DIM_PRODUCTPLANTMRPAREA`
- `_PlantCosting` → `DIM_PRODUCTPLANTCOSTING`
- `_PlantForecast` → `DIM_PRODUCTPLANTFORECAST`
- `_PlantIntlTrade` → `DIM_PRODPLNTINTERNATIONALTRADE`
- `_PlantProcurement` → `DIM_PRODUCTPLANTPROCUREMENT`
- `_PlantQualityMgmt` → `DIM_PRODUCTPLANTQUALITYMANAGEMENT`
- `_PlantSales` → `DIM_PRODUCTPLANTSALES`
- `_PlantStorage` → `DIM_PRODUCTPLANTSTORAGE`
- `_PlantWorkScheduling` → `DIM_PRODUCTPLANTWORKSCHEDULING`

---

### DIM_PRODUCTSTORAGELOC
**Source:** `REF_PRODUCTSTORAGELOC` | **Key:** `Product`, `Plant`, `StorageLocation`  
**Association:** `_ProductPlant` → `DIM_PRODUCTPLANT`

---

### DIM_PRODUCTVALUATION
**Source:** `REF_PRODUCTVALUATION` | **Key:** `Product`, `ValuationArea`, `ValuationType`  
**Key Columns:** `Product`, `ValuationArea`, `ValuationType`, `ValuationClass`, `PriceControlIndicator`, `StandardPrice`, `MovingAveragePrice`, `FuturePrice`, `TotalStockValue`, `Currency`  
**Association:** `_Product` → `DIM_PRODUCT`

---

### DIM_PRODUCTSALESDELIVERY
**Source:** `REF_PRODUCTSALESDELIVERY` | **Key:** `Product`, `SalesOrganization`, `DistributionChannel`  
**Columns:** `Product`, `SalesOrganization`, `DistributionChannel`, `SalesStatus`, `SalesStatusValidityDate`, `TransportationGroup`, `LoadingGroup`, `GrossWeight`, `NetWeight`, `WeightUnit`, `Volume`, `VolumeUnit`  
**Association:** `_Product` → `DIM_PRODUCT`

---

### DIM_PRODUCTPROCUREMENT
**Source:** `REF_PRODUCTPROCUREMENT` | **Key:** `Product`  
**Columns:** `Product`, `PurchaseOrderQuantityUnit`, `VarblPurOrdUnitStatus`, `PurchasingAcknProfile`  
**Association:** `_Product` → `DIM_PRODUCT`

---

### DIM_PRODUCTBASICTEXTS
**Source:** `REF_PRODUCTBASICTEXTS` | **Key:** `Product`, `Language`, `TextObjectType`  
**Association:** `_Product` → `DIM_PRODUCT`

---

### DIM_PRODUCTINSPECTIONTEXTS
**Source:** `REF_PRODUCTINSPECTIONTEXTS` | **Key:** `Product`, `Language`, `TextObjectType`  
**Association:** `_Product` → `DIM_PRODUCT`

---

### DIM_PRODUCTQUALITYMANAGEMENT
**Source:** `REF_PRODUCTQUALITYMANAGEMENT` | **Key:** `Product`  
**Association:** `_Product` → `DIM_PRODUCT`

---

### DIM_PRODUCTPLANTMRPAREA
**Source:** `REF_PRODUCTPLANTMRPAREA` | **Key:** `Product`, `Plant`, `MRPArea`  
**Columns:** `Product`, `Plant`, `MRPArea`, `MRPType`, `ReorderPoint`, `PlanningTimeFence`, `SafetyStockQuantity`  
**Association:** `_ProductPlant` → `DIM_PRODUCTPLANT`

---

### DIM_PRODUCTPLANTCOSTING
**Source:** `REF_PRODUCTPLANTCOSTING` | **Key:** `Product`, `Plant`, `CostingVariant`  
**Association:** `_ProductPlant` → `DIM_PRODUCTPLANT`

---

### DIM_PRODUCTPLANTFORECAST
**Source:** `REF_PRODUCTPLANTFORECAST` | **Key:** `Product`, `Plant`  
**Columns:** `Product`, `Plant`, `ForecastModel`, `ForecastPeriodType`, `NumberOfPeriodsForBasicValue`  
**Association:** `_ProductPlant` → `DIM_PRODUCTPLANT`

---

### DIM_PRODPLNTINTERNATIONALTRADE
**Source:** `REF_PRODPLNTINTERNATIONALTRADE` | **Key:** `Product`, `Plant`  
**Columns:** `Product`, `Plant`, `CountryOfOrigin`, `RegionOfOrigin`, `CommodityCode`, `ExportAndImportProductGroup`, `ProductCASNumber`, `ProdIntlTradeClassification`  
**Association:** `_ProductPlant` → `DIM_PRODUCTPLANT`

---

### DIM_PRODUCTPLANTPROCUREMENT
**Source:** `REF_PRODUCTPLANTPROCUREMENT` | **Key:** `Product`, `Plant`  
**Columns:** `Product`, `Plant`, `ProcurementType`, `SpecialProcurementType`, `IsPhantomItem`, `IsAutomaticallyPurchased`  
**Association:** `_ProductPlant` → `DIM_PRODUCTPLANT`

---

### DIM_PRODUCTPLANTQUALITYMANAGEMENT
**Source:** `REF_PRODUCTPLANTQUALITYMANAGEMENT` | **Key:** `Product`, `Plant`  
**Columns:** `Product`, `Plant`, `QMControlKey`, `HasPostToInspectionStock`, `InspLotDocumentationIsRequired`, `RecrrgInspIntervalTimeInDays`, `ProductQualityCertificateType`  
**Association:** `_ProductPlant` → `DIM_PRODUCTPLANT`

---

### DIM_PRODUCTPLANTSALES
**Source:** `REF_PRODUCTPLANTSALES` | **Key:** `Product`, `Plant`  
**Columns:** `Product`, `Plant`, `LoadingGroup`, `AvailabilityCheckType`, `ReplacementPartType`  
**Association:** `_ProductPlant` → `DIM_PRODUCTPLANT`

---

### DIM_PRODUCTPLANTSTORAGE
**Source:** `REF_PRODUCTPLANTSTORAGE` | **Key:** `Product`, `Plant`  
**Columns:** `Product`, `Plant`, `StorageConditions`, `TemperatureConditionIndicator`, `HazardousMaterialNumber`, `NecessaryPackagingMaterialType`  
**Association:** `_ProductPlant` → `DIM_PRODUCTPLANT`

---

### DIM_PRODUCTPLANTWORKSCHEDULING
**Source:** `REF_PRODUCTPLANTWORKSCHEDULING` | **Key:** `Product`, `Plant`  
**Columns:** `Product`, `Plant`, `ProductionSchedulerGroup`, `ProductionSupervisor`, `UnderDelivToleranceLevel`, `OverDelivToleranceLevel`, `SetupAndTeardownTime`  
**Association:** `_ProductPlant` → `DIM_PRODUCTPLANT`

---

### DIM_PRODUCTMLACCOUNT
**Source:** `REF_PRODUCTMLACCOUNT` | **Key:** `Product`, `ValuationArea`, `ValuationType`, `CurrencyType`  
**Columns:** `Product`, `ValuationArea`, `ValuationType`, `CurrencyType`, `MaterialOrigin`, `CostingGroup`, `TotalStockValue`, `Currency`, `PriceUnitQty`  
**Association:** `_ProductValuation` → `DIM_PRODUCTVALUATION`

---

## Central Analytical Dataset

### ProductAnalyticalDataset
**Semantic Type:** `#ANALYTICAL_CUBE`  
**Label:** Product Master — S/4HANA SP03  
**Description:** Star-schema analytical dataset assembling all 22 product master dimension views sourced from S/4HANA on-premise SP03 via HDLFS. No transactional measures — use this dataset as the dimension hub for product analytics.

**Central Node:** `DIM_PRODUCT`

**Associated Dimensions (spokes — 20 total):**

| Association Name | Target Dimension | Join Keys |
|-----------------|-----------------|-----------|
| `_Text` | `DIM_PRODUCTTEXT` | `Product` |
| `_ProductUnitsOfMeasure` | `DIM_PRODUCTUNITSOFMEASURE` | `Product` |
| `_ProductValuation` | `DIM_PRODUCTVALUATION` | `Product` |
| `_MLAccount` | `DIM_PRODUCTMLACCOUNT` | `Product`, `ValuationArea`, `ValuationType` |
| `_SalesDelivery` | `DIM_PRODUCTSALESDELIVERY` | `Product`, `SalesOrganization`, `DistributionChannel` |
| `_Procurement` | `DIM_PRODUCTPROCUREMENT` | `Product` |
| `_BasicText` | `DIM_PRODUCTBASICTEXTS` | `Product`, `Language`, `TextObjectType` |
| `_InspectionText` | `DIM_PRODUCTINSPECTIONTEXTS` | `Product`, `Language`, `TextObjectType` |
| `_QualityMgmt` | `DIM_PRODUCTQUALITYMANAGEMENT` | `Product` |
| `_ProductPlant` | `DIM_PRODUCTPLANT` | `Product`, `Plant` |
| `_ProductStorageLocation` | `DIM_PRODUCTSTORAGELOC` | `Product`, `Plant`, `StorageLocation` |
| `_PlantMRPArea` | `DIM_PRODUCTPLANTMRPAREA` | `Product`, `Plant`, `MRPArea` |
| `_PlantCosting` | `DIM_PRODUCTPLANTCOSTING` | `Product`, `Plant`, `CostingVariant` |
| `_PlantForecast` | `DIM_PRODUCTPLANTFORECAST` | `Product`, `Plant` |
| `_PlantIntlTrade` | `DIM_PRODPLNTINTERNATIONALTRADE` | `Product`, `Plant` |
| `_PlantProcurement` | `DIM_PRODUCTPLANTPROCUREMENT` | `Product`, `Plant` |
| `_PlantQualityMgmt` | `DIM_PRODUCTPLANTQUALITYMANAGEMENT` | `Product`, `Plant` |
| `_PlantSales` | `DIM_PRODUCTPLANTSALES` | `Product`, `Plant` |
| `_PlantStorage` | `DIM_PRODUCTPLANTSTORAGE` | `Product`, `Plant` |
| `_PlantWorkScheduling` | `DIM_PRODUCTPLANTWORKSCHEDULING` | `Product`, `Plant` |

---

## Deployment Sequence

1. Deploy all 22 Dimension views (parallel deployment OK within same group)
2. Validate each dimension: key fields non-null, at least 1 row returned in test query
3. Deploy `ProductAnalyticalDataset` after all dimensions are active
4. Run validation query: `SELECT Product, ProductDescription, Plant, StorageLocation, StandardPrice FROM ProductAnalyticalDataset LIMIT 10`

---

## Milestone Log
`M5.achieved: Datasphere semantic layer complete — 21 dimensions and 1 analytical dataset deployed`
