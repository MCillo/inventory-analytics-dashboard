# Inventory-Analytics Data-Dictionary

***

## Category Table
| Field Name | Data Type | Description | Source | Required |
|------------|-----------|-------------|--------|----------|
|CategoryId | int | Category table primary key | Database| Yes |
|CategoryName | varchar(50) | Category Name | Database| Yes|


## SubCategory Table
| Field Name | Data Type | Description | Source | Required |
|------------|-----------|-------------|--------|----------|
|SubCategoryId | int | Subcategory table primary key | Database| Yes |
|SubCategoryName | varchar(50) | SubCategory Name | Database| Yes |
|CategoryId | int | Foreign key for Category Table | Database| Yes |


### Vendor Table
| Field Name | Data Type | Description | Source | Required |
|------------|-----------|-------------|--------|----------|
|VendorId | int | Vendor table primary key | Database| Yes |
|VendorName | varchar(150)| vendors name| Database| Yes |

### SalesRep Table
| Field Name | Data Type | Description | Source | Required |
|------------|-----------|-------------|--------|----------|
|SalesRepId | int | SalesRep table primary key | Database | Yes |
|ContactFirstName | varchar(50) | sales reps first name | Database| No |
|ContactLastName | varchar(50) | sales reps last name | Database| No |
|ContactPhone | varchar(25)| sales reps phone number | Database| No |
|ContactEmail | varchar(255) | sales reps email | Database| No |
|SalesRepPosition | varchar(50) | sales reps position | Database | No |
|VendorId | int | foreign key for Vendor table | Database | Yes |


### Product Table
| Field Name | Data Type | Description | Source | Required |
|------------|-----------|-------------|--------|----------|
|ProductId | int | Product table primary key | Database| Yes |
|SKU | int | Store SKU number| Sales Report | No |
|ProductName| varchar(200) | general description of product | Database| Yes |
|Size| varchar(50)| product size | Database| No |
|CasePack | int | case or pack size | Database| No |
|IsSeasonal | boolean | Products Seasonal Status | Database | No |
|IsDiscontinued | boolean | Products status | Database | No |
|DealLevel | int | the deal level of the product | Database | No |
|SubCategoryId | int | the subcategory of the product | Database | No |
|VendorId  | int | foreign key for the vendor table | No |
|SalesRepId | int | foreign key for the SalesRep table | No |


### InventorySnapshot Table
| Field Name | Data Type | Description | Source | Required |
|------------|-----------|-------------|--------|----------|
|InventorySnapshotId | int | InventorySnapshot table primary key | Database | Yes |
|QuantityOnHand | int | quantity of product on hand| Inventory Report| Yes |
|SnapshotDate | datetime | date the inventory snapshot was generated | Spreadsheet | Yes |
|ImportBatchId| int | foreign key for ImportBatch table | Database| Yes |
|ProductId | int | foreign key for Product table | Database| Yes |


### SalesHistory Table
| Field Name | Data Type | Description | Source | Required |
|------------|-----------|-------------|--------|----------|
|SalesHistoryId | int | SalesHistory table primary key | Database | Yes |
|UnitsSold | int | number of units sold | Sales Report| Yes |
|PeriodStartDate | datetime | start date of sales report | Sales Report| Yes |
|PeriodEndDate | datetime | end date of sales report| Sales Report| Yes |
|ImportBatchId| int | foreign key for ImportBatch table | Database| Yes |
|ProductId | int | foreign key for Products table | Database| Yes |


### OrderScenario Table
| Field Name | Data Type | Description | Source | Required |
|------------|-----------|-------------|--------|----------|
|OrderScenarioId | int | OrderScenario table primary key | Database | Yes |
|ScenarioName | varchar(100) | order scenario description | Dashboard Entry | Yes |
|ScenarioDate | datetime | scenario date | Dashboard Entry | Yes |
|DealDescription | varchar(150) | description of deal | Dasboard Entry | Yes |
|TotalDealCases | int | total number of cases in deal | Dashboard Entry | Yes |
|Notes | varchar(255) | notes | Dashboard Entry | No |
|VendorId | int | foreign key for Vendor table | Database | Yes |
|SalesRepID | int | foreign key for SalesRep table | Database | Yes |
|UserID | int | foreign key for User Table | Database | Yes |


### OrderScenarioItem Table
| Field Name | Data Type | Description | Source | Required |
|------------|-----------|-------------|--------|----------|
|OrderScenarioItemId | int | OrderScenarioItem table primary key | Database | Yes |
|OrderScenarioId | int | foreign key for OrderScenario table | Database | Yes |
|ProductId | int | foreign key for Product table | Database | Yes |
|ProposedCases | int | the number of cases to be ordered | No |
|ProposedBottles | int | the number of bottles to be ordered | Yes |


### ImportBatch Table
| Field Name | Data Type | Description | Source | Required |
|------------|-----------|-------------|--------|----------|
|ImportBatchId | int | ImportBatch table primary key | Database| Yes |
|ImportDate | datetime | date of import batch | System Date | Yes |
|FileName| varchar(255) | name of the import file| System Filename| Yes |
|ImportType| varchar(50) | type of file imported, mostly excel | System file metadata | Yes |
|Status | varchar(50) | status of report | System file metadata | Yes |


### Role Table
| Field Name | Data Type | Description | Source | Required |
|------------|-----------|-------------|--------|----------|
|RoleId | int | Role table primary key | Database| Yes |
|RoleName | varchar(50) | name of role | Database| Yes |


### User Table
| Field Name | Data Type | Description | Source | Required |
|------------|-----------|-------------|--------|----------|
|UserId | int | User table primary key | Database| Yes |
|UserFirstName | varchar(50) | users first name | Database| Yes |
|UserLastName | varchar(50) | users last name | Database| Yes |
|UserEmail | varchar(255) | users email | Database| Yes |
|RoleId | int | foreign key for Role table | Database| Yes | 

 
### ProductFinancial Table
| Field Name | Data Type | Description | Source | Required |
|------------|-----------|-------------|--------|----------|
|ProductFinancialId | int | ProductFinancial table primary key | Database| Yes |
|ProductId | int | foreign key for Product table | Database| Yes |
|RetailPrice | decimal | products retail price | Inventory Report| No |
|CostPrice | decimal | products cost | Inventory Report| No |
|MarginDollars | decimal | product margin in dollars | Inventory Report | No |
|MarginPercent | decimal | product margin percentage | Inventory Report | No |
|ImportBatchId | int | foreign key for ImportBatch table | Database | Yes |
|EffectiveDate | datetime | date financial record became effective | Inventory Report/System | Yes |

