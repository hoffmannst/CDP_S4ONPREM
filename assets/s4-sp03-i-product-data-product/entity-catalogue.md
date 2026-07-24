# Entity Catalogue — S/4HANA SP03 I_Product Association Tree

**Source System:** S/4HANA on-premise, SP03, Release 2023/02/00  
**ODP Context:** `CDS_EXTRACTION`  
**Milestone:** M1

---

## Association Map

```
I_Product (root)
├── _Text                     → I_ProductDescription
├── _ProductUnitsOfMeasure    → I_ProductUnitsOfMeasure
├── _ProductValuation         → I_ProductValuation
├── _MLAccount                → I_ProductMLAccount
├── _SalesDelivery            → I_ProductSalesDelivery
├── _Procurement              → I_ProductProcurement
├── _BasicText                → I_ProductBasicTexts
├── _InspectionText           → I_ProductInspectionTexts
├── _QualityMgmt              → I_ProductQualityManagement
└── _ProductPlant             → I_ProductPlant
    ├── _ProductStorageLocation → I_ProductStorageLocation
    ├── _PlantMRPArea          → I_ProductPlantMRPArea
    ├── _PlantCosting          → I_ProductPlantCosting
    ├── _PlantForecast         → I_ProductPlantForecast
    ├── _PlantIntlTrade        → I_ProdPlntInternationalTrade
    ├── _PlantProcurement      → I_ProductPlantProcurement
    ├── _PlantQualityMgmt      → I_ProductPlantQualityManagement
    ├── _PlantSales            → I_ProductPlantSales
    ├── _PlantStorage          → I_ProductPlantStorage
    └── _PlantWorkScheduling   → I_ProductPlantWorkScheduling
```

---

## Entity Reference Table

| # | CDS View | Association Path | Key Fields | ODP Delta Enabled | Raw Zone Table | Refined Zone Table | Datasphere Dimension |
|---|----------|-----------------|------------|-------------------|----------------|-------------------|----------------------|
| 1 | `I_Product` | Root | `Product` (MATNR), `Client` (MANDT) | ✅ `@Analytics.dataExtraction.enabled: true` | `RAW_I_PRODUCT` | `REF_PRODUCT` | `DIM_PRODUCT` |
| 2 | `I_ProductDescription` | `_Text` | `Product`, `Language` (SPRAS) | ✅ | `RAW_I_PRODUCTDESCRIPTION` | `REF_PRODUCTTEXT` | `DIM_PRODUCTTEXT` |
| 3 | `I_ProductUnitsOfMeasure` | `_ProductUnitsOfMeasure` | `Product`, `AlternativeUnit` | ✅ | `RAW_I_PRODUCTUNITSOFMEASURE` | `REF_PRODUCTUNITSOFMEASURE` | `DIM_PRODUCTUNITSOFMEASURE` |
| 4 | `I_ProductPlant` | `_ProductPlant` | `Product`, `Plant` | ✅ | `RAW_I_PRODUCTPLANT` | `REF_PRODUCTPLANT` | `DIM_PRODUCTPLANT` |
| 5 | `I_ProductStorageLocation` | `_ProductPlant._ProductStorageLocation` | `Product`, `Plant`, `StorageLocation` | ✅ | `RAW_I_PRODUCTSTORAGELOC` | `REF_PRODUCTSTORAGELOC` | `DIM_PRODUCTSTORAGELOC` |
| 6 | `I_ProductValuation` | `_ProductValuation` | `Product`, `ValuationArea`, `ValuationType` | ✅ | `RAW_I_PRODUCTVALUATION` | `REF_PRODUCTVALUATION` | `DIM_PRODUCTVALUATION` |
| 7 | `I_ProductSalesDelivery` | `_SalesDelivery` | `Product`, `SalesOrganization` (VKORG), `DistributionChannel` (VTWEG) | ✅ | `RAW_I_PRODUCTSALESDELIVERY` | `REF_PRODUCTSALESDELIVERY` | `DIM_PRODUCTSALESDELIVERY` |
| 8 | `I_ProductProcurement` | `_Procurement` | `Product` | ✅ | `RAW_I_PRODUCTPROCUREMENT` | `REF_PRODUCTPROCUREMENT` | `DIM_PRODUCTPROCUREMENT` |
| 9 | `I_ProductBasicTexts` | `_BasicText` | `Product`, `Language`, `TextObjectType` | ✅ | `RAW_I_PRODUCTBASICTEXTS` | `REF_PRODUCTBASICTEXTS` | `DIM_PRODUCTBASICTEXTS` |
| 10 | `I_ProductInspectionTexts` | `_InspectionText` | `Product`, `Language`, `TextObjectType` | ✅ | `RAW_I_PRODUCTINSPECTIONTEXTS` | `REF_PRODUCTINSPECTIONTEXTS` | `DIM_PRODUCTINSPECTIONTEXTS` |
| 11 | `I_ProductQualityManagement` | `_QualityMgmt` | `Product` | ✅ | `RAW_I_PRODUCTQUALITYMANAGEMENT` | `REF_PRODUCTQUALITYMANAGEMENT` | `DIM_PRODUCTQUALITYMANAGEMENT` |
| 12 | `I_ProductPlantMRPArea` | `_ProductPlant._PlantMRPArea` | `Product`, `Plant`, `MRPArea` | ✅ | `RAW_I_PRODUCTPLANTMRPAREA` | `REF_PRODUCTPLANTMRPAREA` | `DIM_PRODUCTPLANTMRPAREA` |
| 13 | `I_ProductPlantCosting` | `_ProductPlant._PlantCosting` | `Product`, `Plant` | ✅ | `RAW_I_PRODUCTPLANTCOSTING` | `REF_PRODUCTPLANTCOSTING` | `DIM_PRODUCTPLANTCOSTING` |
| 14 | `I_ProductPlantForecast` | `_ProductPlant._PlantForecast` | `Product`, `Plant` | ✅ | `RAW_I_PRODUCTPLANTFORECAST` | `REF_PRODUCTPLANTFORECAST` | `DIM_PRODUCTPLANTFORECAST` |
| 15 | `I_ProdPlntInternationalTrade` | `_ProductPlant._PlantIntlTrade` | `Product`, `Plant` | ✅ | `RAW_I_PRODPLNTINTERNATIONALTRADE` | `REF_PRODPLNTINTERNATIONALTRADE` | `DIM_PRODPLNTINTERNATIONALTRADE` |
| 16 | `I_ProductPlantProcurement` | `_ProductPlant._PlantProcurement` | `Product`, `Plant` | ✅ | `RAW_I_PRODUCTPLANTPROCUREMENT` | `REF_PRODUCTPLANTPROCUREMENT` | `DIM_PRODUCTPLANTPROCUREMENT` |
| 17 | `I_ProductPlantQualityManagement` | `_ProductPlant._PlantQualityMgmt` | `Product`, `Plant` | ✅ | `RAW_I_PRODUCTPLANTQUALITYMANAGEMENT` | `REF_PRODUCTPLANTQUALITYMANAGEMENT` | `DIM_PRODUCTPLANTQUALITYMANAGEMENT` |
| 18 | `I_ProductPlantSales` | `_ProductPlant._PlantSales` | `Product`, `Plant` | ✅ | `RAW_I_PRODUCTPLANTSALES` | `REF_PRODUCTPLANTSALES` | `DIM_PRODUCTPLANTSALES` |
| 19 | `I_ProductPlantStorage` | `_ProductPlant._PlantStorage` | `Product`, `Plant` | ✅ | `RAW_I_PRODUCTPLANTSTORAGE` | `REF_PRODUCTPLANTSTORAGE` | `DIM_PRODUCTPLANTSTORAGE` |
| 20 | `I_ProductPlantWorkScheduling` | `_ProductPlant._PlantWorkScheduling` | `Product`, `Plant` | ✅ | `RAW_I_PRODUCTPLANTWORKSCHEDULING` | `REF_PRODUCTPLANTWORKSCHEDULING` | `DIM_PRODUCTPLANTWORKSCHEDULING` |
| 21 | `I_ProductMLAccount` | `_MLAccount` | `Product`, `ValuationArea`, `ValuationType`, `CurrencyType` | ✅ | `RAW_I_PRODUCTMLACCOUNT` | `REF_PRODUCTMLACCOUNT` | `DIM_PRODUCTMLACCOUNT` |

---

## ODP Validation Notes

- All 21 CDS views carry `@Analytics.dataExtraction.enabled: true` in S/4HANA SP03 as per SAP standard delivery.
- Validate using transaction `RODPS_REPL_TEST` in the source system before activating replication flows.
- ODP context for all views: `CDS_EXTRACTION`.
- Delta mode: `@Analytics.dataExtraction.delta.changeDataCapture.mapping` is present on all header and item-level views.
- If any view is found without ODP delta support in the customer system, fall back to **SLT (SAP Landscape Transformation)** for that entity.

---

## Milestone Log
`M1.achieved: I_Product association map complete — 21 CDS views catalogued`
