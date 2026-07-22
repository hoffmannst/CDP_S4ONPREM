# Entity Catalogue — S/4HANA SP03 I_Product Association Tree

**Source System:** S/4HANA on-premise, SP03, Release 2023/02/00  
**ODP Context:** `CDS_EXTRACTION`  
**Milestone:** M1

---

## Association Map

```
I_Product (root)
├── _Text                     → I_ProductText
├── _ProductUoM               → I_ProductUoM
├── _ProductValuation         → I_ProductValuation
├── _MLAccount                → I_ProductMLAccount
├── _SalesDelivery            → I_ProductSalesDelivery
│   └── _SalesOrg             → I_ProdSalesDeliverySalesOrg
├── _Purchasing               → I_ProductPurchasing
├── _BasicText                → I_ProductBasicText
├── _InspectionText           → I_ProductInspectionText
├── _QualityMgmt              → I_ProductQualityMgmt
└── _ProductPlant             → I_ProductPlant
    ├── _ProductStorageLocation → I_ProductStorageLocation
    ├── _PlantMRPArea          → I_ProductPlantMRPArea
    ├── _PlantCosting          → I_ProductPlantCosting
    ├── _PlantForecast         → I_ProductPlantForecast
    ├── _PlantIntlTrade        → I_ProductPlantIntlTrade
    ├── _PlantProcurement      → I_ProductPlantProcurement
    ├── _PlantQualityMgmt      → I_ProductPlantQualityMgmt
    ├── _PlantSales            → I_ProductPlantSales
    ├── _PlantStorage          → I_ProductPlantStorage
    └── _PlantWorkScheduling   → I_ProductPlantWorkScheduling
```

---

## Entity Reference Table

| # | CDS View | Association Path | Key Fields | ODP Delta Enabled | Raw Zone Table | Refined Zone Table | Datasphere Dimension |
|---|----------|-----------------|------------|-------------------|----------------|-------------------|----------------------|
| 1 | `I_Product` | Root | `Product` (MATNR), `Client` (MANDT) | ✅ `@Analytics.dataExtraction.enabled: true` | `RAW_I_PRODUCT` | `REF_PRODUCT` | `DIM_PRODUCT` |
| 2 | `I_ProductText` | `_Text` | `Product`, `Language` (SPRAS) | ✅ | `RAW_I_PRODUCTTEXT` | `REF_PRODUCTTEXT` | `DIM_PRODUCTTEXT` |
| 3 | `I_ProductUoM` | `_ProductUoM` | `Product`, `AlternativeUnit` | ✅ | `RAW_I_PRODUCTUOM` | `REF_PRODUCTUOM` | `DIM_PRODUCTUOM` |
| 4 | `I_ProductPlant` | `_ProductPlant` | `Product`, `Plant` | ✅ | `RAW_I_PRODUCTPLANT` | `REF_PRODUCTPLANT` | `DIM_PRODUCTPLANT` |
| 5 | `I_ProductStorageLocation` | `_ProductPlant._ProductStorageLocation` | `Product`, `Plant`, `StorageLocation` | ✅ | `RAW_I_PRODUCTSTORAGELOC` | `REF_PRODUCTSTORAGELOC` | `DIM_PRODUCTSTORAGELOC` |
| 6 | `I_ProductValuation` | `_ProductValuation` | `Product`, `ValuationArea`, `ValuationType` | ✅ | `RAW_I_PRODUCTVALUATION` | `REF_PRODUCTVALUATION` | `DIM_PRODUCTVALUATION` |
| 7 | `I_ProductSalesDelivery` | `_SalesDelivery` | `Product` | ✅ | `RAW_I_PRODUCTSALESDELIVERY` | `REF_PRODUCTSALESDELIVERY` | `DIM_PRODUCTSALESDELIVERY` |
| 8 | `I_ProdSalesDeliverySalesOrg` | `_SalesDelivery._SalesOrg` | `Product`, `SalesOrganization`, `DistributionChannel` | ✅ | `RAW_I_PRODSALESDELIVERYSALESORG` | `REF_PRODSALESDELIVERYSALESORG` | `DIM_PRODSALESDELIVERYSALESORG` |
| 9 | `I_ProductPurchasing` | `_Purchasing` | `Product`, `Plant` | ✅ | `RAW_I_PRODUCTPURCHASING` | `REF_PRODUCTPURCHASING` | `DIM_PRODUCTPURCHASING` |
| 10 | `I_ProductBasicText` | `_BasicText` | `Product`, `Language` | ✅ | `RAW_I_PRODUCTBASICTEXT` | `REF_PRODUCTBASICTEXT` | `DIM_PRODUCTBASICTEXT` |
| 11 | `I_ProductInspectionText` | `_InspectionText` | `Product`, `Language` | ✅ | `RAW_I_PRODUCTINSPECTIONTEXT` | `REF_PRODUCTINSPECTIONTEXT` | `DIM_PRODUCTINSPECTIONTEXT` |
| 12 | `I_ProductQualityMgmt` | `_QualityMgmt` | `Product`, `Plant` | ✅ | `RAW_I_PRODUCTQUALITYMGMT` | `REF_PRODUCTQUALITYMGMT` | `DIM_PRODUCTQUALITYMGMT` |
| 13 | `I_ProductPlantMRPArea` | `_ProductPlant._PlantMRPArea` | `Product`, `Plant`, `MRPArea` | ✅ | `RAW_I_PRODUCTPLANTMRPAREA` | `REF_PRODUCTPLANTMRPAREA` | `DIM_PRODUCTPLANTMRPAREA` |
| 14 | `I_ProductPlantCosting` | `_ProductPlant._PlantCosting` | `Product`, `Plant`, `CostingVariant` | ✅ | `RAW_I_PRODUCTPLANTCOSTING` | `REF_PRODUCTPLANTCOSTING` | `DIM_PRODUCTPLANTCOSTING` |
| 15 | `I_ProductPlantForecast` | `_ProductPlant._PlantForecast` | `Product`, `Plant` | ✅ | `RAW_I_PRODUCTPLANTFORECAST` | `REF_PRODUCTPLANTFORECAST` | `DIM_PRODUCTPLANTFORECAST` |
| 16 | `I_ProductPlantIntlTrade` | `_ProductPlant._PlantIntlTrade` | `Product`, `Plant` | ✅ | `RAW_I_PRODUCTPLANTINTLTRADE` | `REF_PRODUCTPLANTINTLTRADE` | `DIM_PRODUCTPLANTINTLTRADE` |
| 17 | `I_ProductPlantProcurement` | `_ProductPlant._PlantProcurement` | `Product`, `Plant` | ✅ | `RAW_I_PRODUCTPLANTPROCUREMENT` | `REF_PRODUCTPLANTPROCUREMENT` | `DIM_PRODUCTPLANTPROCUREMENT` |
| 18 | `I_ProductPlantQualityMgmt` | `_ProductPlant._PlantQualityMgmt` | `Product`, `Plant` | ✅ | `RAW_I_PRODUCTPLANTQUALITYMGMT` | `REF_PRODUCTPLANTQUALITYMGMT` | `DIM_PRODUCTPLANTQUALITYMGMT` |
| 19 | `I_ProductPlantSales` | `_ProductPlant._PlantSales` | `Product`, `Plant` | ✅ | `RAW_I_PRODUCTPLANTSALES` | `REF_PRODUCTPLANTSALES` | `DIM_PRODUCTPLANTSALES` |
| 20 | `I_ProductPlantStorage` | `_ProductPlant._PlantStorage` | `Product`, `Plant` | ✅ | `RAW_I_PRODUCTPLANTSTORAGE` | `REF_PRODUCTPLANTSTORAGE` | `DIM_PRODUCTPLANTSTORAGE` |
| 21 | `I_ProductPlantWorkScheduling` | `_ProductPlant._PlantWorkScheduling` | `Product`, `Plant` | ✅ | `RAW_I_PRODUCTPLANTWORKSCHEDULING` | `REF_PRODUCTPLANTWORKSCHEDULING` | `DIM_PRODUCTPLANTWORKSCHEDULING` |
| 22 | `I_ProductMLAccount` | `_MLAccount` | `Product`, `ValuationArea`, `ValuationType`, `CurrencyType` | ✅ | `RAW_I_PRODUCTMLACCOUNT` | `REF_PRODUCTMLACCOUNT` | `DIM_PRODUCTMLACCOUNT` |

---

## ODP Validation Notes

- All 22 CDS views carry `@Analytics.dataExtraction.enabled: true` in S/4HANA SP03 as per SAP standard delivery.
- Validate using transaction `RODPS_REPL_TEST` in the source system before activating replication flows.
- ODP context for all views: `CDS_EXTRACTION`.
- Delta mode: `@Analytics.dataExtraction.delta.changeDataCapture.mapping` is present on all header and item-level views.
- If any view is found without ODP delta support in the customer system, fall back to **SLT (SAP Landscape Transformation)** for that entity.

---

## Milestone Log
`M1.achieved: I_Product association map complete — 22 CDS views catalogued`
