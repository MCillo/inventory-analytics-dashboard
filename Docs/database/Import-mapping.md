# Import Mapping
This file will describe the process of mapping data as it is read from external spreadsheets into the database for the Program. 

## Sales History Map

### Source File
Sales Report by Item generated from POS System

### Import Process
1. Download Sales Report from POS System
2. Read Spreadsheet
3. Create ImportBatch
4. Match Product: Item No. on spreadsheet = SKU in Product Table
5. Import Sales History data into Sales History Table
6. Import Financial information into ProductFinancial Table
7. Update ImportBatch status to Success or Failed.
---
### Import Map
| Spreadsheet Column Name | Spreadsheet Column | Database Table | Database Field | Source Type | Action | Notes |
|-------------------------|--------------------|----------------|----------------|-------------|--------|-------|
| File name | File metadata | ImportBatch | FileName | System/File | Create | Store uploaded spreadsheet filename |
| Valuation Date / Period End Date | System generated | ProductFinancial | EffectiveDate | System DateTime | Insert | Use PeriodEndDate as EffectiveDate for imported sales financials |
| Import type | System generated | ImportBatch | ImportType | Default Value | Create | Set to "Sales History" |
| Import status | System generated | ImportBatch | Status | System Generated | Update | Set to Success or Failed |
| Valuation date | Cell B3 | SalesHistory | PeriodStartDate / PeriodEndDate | Spreadsheet | Parse | Extract start and end dates from report header |
| Department | Column A | Product | Category Mapping | Spreadsheet/Lookup | Reference Only | Used only for reference during product review. Category/SubCategory maintained manually in database |
| Description | Column B | Product | ProductName | Spreadsheet | Verify/Update if changed | Do not overwrite cleaned names automatically |
| Item No. | Column C | Product | SKU | Spreadsheet | Match | Use SKU to find ProductId |
| Item No. | Column C | SalesHistory | ProductId | Lookup | Insert | ProductId is found by matching SKU |
| Qty Sold | Column D | SalesHistory | UnitsSold | Spreadsheet | Insert | Units sold for reporting period |
| Total | Column G | ProductFinancial | RetailPrice | Calculated | Insert/Update | RetailPrice = Total / QtySold |
| Total Cost | Column I | ProductFinancial | CostPrice | Calculated | Insert/Update | CostPrice = TotalCost / QtySold |
| Profit | Column J | ProductFinancial | MarginPercent | Calculated | Insert/Update | MarginPercent = Profit / Total * 100 |
| ImportBatchId | System generated | SalesHistory | ImportBatchId | Lookup | Insert | Use ImportBatchId created at start of import |
| ImportBatchId | System generated | ProductFinancial | ImportBatchId | Lookup | Insert | ProductFinancial table includes ImportBatchId |
| Import date | System generated | ImportBatch | ImportDate | System DateTime | Create | Date/time file was imported |
| Item No. | Column C | ProductFinancial | ProductId | Lookup | Insert | ProductId found by matching SKU |



---

## Product Inventory Map

### Source File
Inventory Report generated from POS System
### Import Process
1. Download Inventory Report from POS System
2. Read Spreadsheet
3. Create Import Batch
4. Match Product: Item No. on spreadsheet = SKU in Product Table
5. Import Inventory data into InventorySnapshot table
6. Import New products into Product table 


| Spreadsheet Column Name | Spreadsheet Column | Database Table | Database Field | Source Type | Action | Notes |
|---|---|---|---|---|---|---|
| File Name | File metadata | ImportBatch | FileName | System/File | Create | Store uploaded spreadsheet filename |
| Import Date | System generated | ImportBatch | ImportDate | System DateTime | Create | Date/time of file import |
| Import Type | System generated | ImportBatch | ImportType | Default Value | Create | Set to Inventory |
| Import Status | System generated | ImportBatch | Status | System Generated | Update | Set to Success or Failed |
| Item No. | Column A | Product | SKU | Spreadsheet | Match/Insert | Match existing product or create new product |
| Description | Column B | Product | ProductName | Spreadsheet | Verify/Insert | Do not overwrite cleaned names automatically |
| Subdep/Department | Column C/A | Product | Category Review Flag | Spreadsheet/Reference | Do Not Import Directly | Used only to help identify possible category; database category/subcategory maintained manually |
| Qty On Hand | Column D | InventorySnapshot | QuantityOnHand | Spreadsheet | Insert | Quantity on hand at snapshot date |
| Snapshot Date | Cell A 1 | InventorySnapshot | SnapshotDate | Spreadsheet | Insert | Date/time inventory snapshot was created |
| ImportBatchId | System generated | ProductFinancial | ImportBatchId | Lookup | Insert | Use ImportBatchId created at start of import |
| Item No. | Column A | InventorySnapshot | ProductId | Lookup | Insert | ProductId found by matching SKU |
| Avg Cost | Column E | ProductFinancial | CostPrice | Spreadsheet | Insert/Update | Current average cost |
| Base Price | Column F | ProductFinancial | RetailPrice | Spreadsheet | Insert/Update | Current retail/base price |
| Gross M | Column G | ProductFinancial | MarginDollars | Spreadsheet | Insert/Update | Current gross margin dollars |
| Gross M % | Column H | ProductFinancial | MarginPercent | Spreadsheet | Insert/Update | Current gross margin percent |
| Snapshot Date | Cell A1 | ProductFinancial | EffectiveDate | Spreadsheet | Insert | Financial values effective as of inventory snapshot date |
| Item No. | Column A | ProductFinancial | ProductId | Lookup | Insert | ProductId found by matching SKU |
| ImportBatchId | System generated | InventorySnapshot | ImportBatchId | Lookup | Insert | Use ImportBatchId created at start of import |





