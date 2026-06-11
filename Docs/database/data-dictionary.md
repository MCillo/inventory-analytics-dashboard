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
|SubCategoryId | int | Subcategory table primary key | Database|
|SubCategoryName | varchar(50) | SubCategory Name | Database|
|CategoryId | int | Foreign key for Category Table | Database|


### Vendor Table
| Field Name | Data Type | Description | Source | Required |
|------------|-----------|-------------|--------|----------|
|VendorId | int | Vendor table primary key | database|
|VendorName | varchar(150)| vendors name| database|
|ContactFirstName | varchar(50) | sales reps first name | database|
|ContactLastName | varchar(50) | sales reps last name | database|
|ContactPhone | varchar(25)| sales reps phone number | database|
|ContactEmail | varchar(255) | sales reps email | database|


### Product Table
| Field Name | Data Type | Description | Source | Required |
|------------|-----------|-------------|--------|----------|
|ProductId | int | Product table primary key | Database|
|SKU | int | Store SKU number| Sales Report |
|ProductName| varchar(200) | general description of product | Database|
|Size| varchar(50)| product size | Database|
|CasePack|int| case or pack size| Database|
|IsSeasonal | boolean | Products Seasonal Status | Database |
|IsDiscontinued | boolean | Products status | Database |


### InventorySnapshot Table
| Field Name | Data Type | Description | Source | Required |
|------------|-----------|-------------|--------|----------|
|InventorySnapshotId | int | InventorySnapshot table primary key | database|
|QuantityOnHand | int | quantity of product on hand| Inventory Report|
|SnapshotDate | datetime | date of inventory snapshot | Inventory Report|
|ImportBatchId| int | foreign key for ImportBatch table | database|
|ProductId | int | foreign key for Product table | database|


### SalesHistory Table
| Field Name | Data Type | Description | Source | Required |
|------------|-----------|-------------|--------|----------|
|SalesHistoryId | int | SalesHistory table primary key | database|
|UnitsSold | int | number of units sold | Sales Report|
|PeriodStartDate | datetime | start date of sales report | Sales Report|
|PeriodEndDate | datetime | end date of sales report| Sales Report|
|ImportBatchId| int | foreign key for ImportBatch table | database|
|ProductId | int | foreign key for Products table | database|


### ImportBatch Table
| Field Name | Data Type | Description | Source | Required |
|------------|-----------|-------------|--------|----------|
|ImportBatchId | int | ImportBatch table primary key | database|
|ImportDate | datetime | date of import batch | Report |
|FileName| varchar(255) | name of the import file| Report|
|ImportType| varchar(50) | type of file imported, mostly excel | Report|
|Status | varchar(50) | status of report | database|


### Role Table
| Field Name | Data Type | Description | Source | Required |
|------------|-----------|-------------|--------|----------|
|RoleId | int | Role table primary key | database|
|RoleName | varchar(50) | name of role | database|


### User Table
| Field Name | Data Type | Description | Source | Required |
|------------|-----------|-------------|--------|----------|
|UserId | int | User table primary key | database|
|UserFirstName | varchar(50) | users first name | database|
|UserLastName | varchar(50) | users last name | database|
|UserEmail | varchar(255) | users email | database|
|RoleId | int | foreign key for Role table | database|

 
### ProductFinancial Table
| Field Name | Data Type | Description | Source | Required |
|------------|-----------|-------------|--------|----------|
|ProductFinancialId | int | ProductFinancial table primary key | database|
|ProductId | int | foreign key for Product table | database|
|RetailPrice | decimal | products retail price | Inventory Report|
|CostPrice | decimal | products cost | Inventory Report|
|MarginPercent | decimal | products margin in percentage | database |