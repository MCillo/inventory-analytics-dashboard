"""
test_queries.py

Purpose:
Test queries against the database to ensure they work
before implementing GUI and reports
"""

# Import modules needed for program operation

# Module for handling file paths and directories
from pathlib import Path
# Module to work with SQLite
import sqlite3
# Module to work with Python datetime
from datetime import datetime

# Establish the root path for the file tree
root_path = Path(__file__).resolve().parents[2]

# Establish the location for the database file
database_file = root_path / "database" / "inventory.db"

# Function to create a connection to the database file
def create_connection():
    try:
        connection = sqlite3.connect(database_file)
        connection.execute("PRAGMA foreign_keys = ON;")
        return connection

    except sqlite3.Error as error:
        print(f"Database connection error: {error}")
        raise


# Function to show All the tables in the Database
def show_tables(connection):
    cursor = connection.cursor()

    cursor.execute("""
        SELECT name 
        FROM sqlite_master
        WHERE type = 'table'
        ORDER BY name;
    """)

    results = cursor.fetchall()

    print("\nTables in Database")
    for row in results:
        print(row)

# Function to show the Import Batch Count
def show_import_batch_count(connection):
    cursor = connection.cursor()

    cursor.execute("""
        SELECT COUNT(*)
        FROM ImportBatch
    """)

    results = cursor.fetchone()

    print("\nBatch Count")
    print(results)

# Function to show the latest Import Batch Id
def show_latest_import_batch_id(connection):
    cursor = connection.cursor()

    cursor.execute("""
        SELECT 
            ImportBatchID,
            ImportType,
            Status
        FROM ImportBatch
        ORDER BY ImportBatchID DESC
        LIMIT 1;
    """)

    results = cursor.fetchone()

    print("\nLatest Import Batch")
    print(results)

# Function to show Product Count
def show_product_count(connection):
    cursor = connection.cursor()
        
    cursor.execute("""
        SELECT COUNT (*)
        FROM Product
    """)

    results = cursor.fetchone()
    product_count = results[0]
    print("\nTotal Number of Products:")
    print(product_count)

# Function to show duplicate SKU's
def show_duplicate_skus(connection):
    cursor = connection.cursor()

    cursor.execute("""
        SELECT
            Product.ProductId,
            Product.SKU,
            Product.ProductName
        FROM Product
        WHERE Product.SKU IN (
            SELECT SKU
            FROM Product
            WHERE SKU IS NOT NULL
            GROUP BY SKU
            HAVING COUNT(*) > 1
        )
        ORDER BY Product.SKU, Product.ProductId;
    """)

    results = cursor.fetchall()

    if results:
        print("\nDuplicate SKUs Found:")
        print(f"{'ProductId':<12} {'SKU':<10} {'ProductName':<40}")
        print("-" * 70)

        for row in results:
            product_id, sku, product_name = row
            print(f"{product_id:<12} {sku:<10} {product_name:<40}")

    else:
        print("\nNo duplicate SKUs found.")

# Function to show missing sales products
def show_products_without_sales_history(connection):
    cursor = connection.cursor()

    cursor.execute("""
        SELECT
            Product.ProductId,
            Product.SKU,
            Product.ProductName
        FROM Product
        LEFT JOIN SalesHistory
            ON Product.ProductId = SalesHistory.ProductId
        WHERE SalesHistory.ProductId IS NULL
        ORDER BY Product.ProductName
        LIMIT 20;
    """)

    results = cursor.fetchall()

    if results:
        print("\nProducts Without Sales History:")
        print(f"{'ProductId':<12} {'SKU':<12} {'ProductName':<45}")
        print("-" * 75)

        for row in results:
            product_id, sku, product_name = row

            sku = "No SKU" if sku is None else str(sku)
            product_name = "No Product Name" if product_name is None else product_name

            if len(product_name) > 45:
                product_name = product_name[:42] + "..."

            print(f"{product_id:<12} {sku:<12} {product_name:<45}")

    else:
        print("\nAll products have sales history.")

# Function to show Products without a SKU - new potential items
def show_products_without_sku(connection):
    cursor = connection.cursor()

    cursor.execute("""
        SELECT
            ProductName
        FROM 
            Product
        WHERE SKU IS NULL
    """)

    results = cursor.fetchall()
    if results:
        print("\nProducts Without a SKU:")
        print(f"{'ProductName':<45}")
        print("-" * 50)

        for row in results:
            print("f{row:<45}")
    else:
        print("\nAll Products Have a Matching SKU")

# Function to show products listed as Not In POS - for new items
def show_products_not_in_pos(connection):
    cursor = connection.cursor()

    cursor.execute("""
        SELECT
            SKU,
            ProductName,
            IsInPOS
        FROM
            Product
        WHERE 
            IsInPOS = '0'
    """)

    results = cursor.fetchall()

    if results:
        print("\nProducts Not in POS:")
        print(f"{'ProductName':<45}")
        print("-" * 50)

        for row in results:
            print(f"{row:<45}")
    else:
        print("\nAll Products are in POS.")

# Function to show products listed as In POS
def show_products_in_pos(connection):
    cursor = connection.cursor()

    cursor.execute("""
        SELECT
            SKU,
            ProductName,
            IsInPOS
        FROM
            Product
        WHERE 
            IsInPOS = '1'
    """)

    results = cursor.fetchall()

    if results:
        print("\nProducts in POS:")
        print(f"{'ProductName':<45}")
        print("-" * 50)

        for row in results:
            print(f"{row:<45}")
    else:
        print("\nAll Products are in POS.")

# Function to show latest Inventory Batch Summary
def show_latest_inventory_batch_summary(connection):
    cursor = connection.cursor()

    cursor.execute("""
        SELECT
            ImportBatch.ImportBatchId,
            ImportBatch.ImportDate,
            ImportBatch.FileName,
            ImportBatch.Status,

            (
                SELECT COUNT(*)
                FROM InventorySnapshot
                WHERE InventorySnapshot.ImportBatchId = ImportBatch.ImportBatchId
            ) AS SnapshotRowCount,

            (
                SELECT COUNT(DISTINCT ProductId)
                FROM InventorySnapshot
                WHERE InventorySnapshot.ImportBatchId = ImportBatch.ImportBatchId
            ) AS DistinctProductCount,

            (
                SELECT COUNT(*)
                FROM ProductFinancial
                WHERE ProductFinancial.ImportBatchId = ImportBatch.ImportBatchId
            ) AS FinancialRowCount,

            (
                SELECT SUM(QuantityOnHand)
                FROM InventorySnapshot
                WHERE InventorySnapshot.ImportBatchId = ImportBatch.ImportBatchId
            ) AS TotalQuantityOnHand,

            (
                SELECT MIN(QuantityOnHand)
                FROM InventorySnapshot
                WHERE InventorySnapshot.ImportBatchId = ImportBatch.ImportBatchId
            ) AS LowestQuantityOnHand,

            (
                SELECT MAX(QuantityOnHand)
                FROM InventorySnapshot
                WHERE InventorySnapshot.ImportBatchId = ImportBatch.ImportBatchId
            ) AS HighestQuantityOnHand

        FROM ImportBatch
        WHERE ImportBatch.ImportType = 'Inventory'
        ORDER BY ImportBatch.ImportBatchId DESC
        LIMIT 1;
    """)

    result = cursor.fetchone()

    if result:
        (
            import_batch_id,
            import_date,
            file_name,
            status,
            snapshot_row_count,
            distinct_product_count,
            financial_row_count,
            total_quantity_on_hand,
            lowest_quantity_on_hand,
            highest_quantity_on_hand
        ) = result

        if import_date is not None:
            formatted_import_date = datetime.fromisoformat(import_date).strftime("%d/%m/%Y %H:%M")
        else:
            formatted_import_date = "No Import Date"

        print("\nLatest Inventory Batch Summary:")
        print(f"Batch ID: {import_batch_id}")
        print(f"Import Date: {formatted_import_date}")
        print(f"Import Date: {import_date}")
        print(f"File Name: {file_name}")
        print(f"Status: {status}")
        print()
        print(f"Snapshot Rows: {snapshot_row_count}")
        print(f"Distinct Products: {distinct_product_count}")
        print(f"Financial Rows: {financial_row_count}")
        print(f"Total Qty On Hand: {total_quantity_on_hand}")
        print(f"Lowest Qty On Hand: {lowest_quantity_on_hand}")
        print(f"Highest Qty On Hand: {highest_quantity_on_hand}")

    else:
        print("\nNo inventory import batches found.")

# Function to show Latest Sales Batch Summary
def show_latest_sales_batch_summary(connection):
    cursor = connection.cursor()

    cursor.execute("""
        SELECT
            ImportBatch.ImportBatchId,
            ImportBatch.ImportDate,
            ImportBatch.FileName,
            ImportBatch.Status,

            (
                SELECT COUNT(*)
                FROM SalesHistory
                WHERE SalesHistory.ImportBatchId = ImportBatch.ImportBatchId
            ) AS SalesRowCount,

            (
                SELECT COUNT(DISTINCT ProductId)
                FROM SalesHistory
                WHERE SalesHistory.ImportBatchId = ImportBatch.ImportBatchId
            ) AS DistinctProductCount,

            (
                SELECT SUM(UnitsSold)
                FROM SalesHistory
                WHERE SalesHistory.ImportBatchId = ImportBatch.ImportBatchId
            ) AS TotalUnitsSold,

            (
                SELECT COUNT(*)
                FROM SalesHistory
                WHERE SalesHistory.ImportBatchId = ImportBatch.ImportBatchId
                    AND UnitsSold < 0
            ) AS ReturnCorrectionRowCount,

            (
                SELECT MIN(UnitsSold)
                FROM SalesHistory
                WHERE SalesHistory.ImportBatchId = ImportBatch.ImportBatchId
            ) AS LowestUnitsSold,

            (
                SELECT MAX(UnitsSold)
                FROM SalesHistory
                WHERE SalesHistory.ImportBatchId = ImportBatch.ImportBatchId
            ) AS HighestUnitsSold,

            (
                SELECT MIN(PeriodStartDate)
                FROM SalesHistory
                WHERE SalesHistory.ImportBatchId = ImportBatch.ImportBatchId
            ) AS PeriodStartDate,

            (
                SELECT MAX(PeriodEndDate)
                FROM SalesHistory
                WHERE SalesHistory.ImportBatchId = ImportBatch.ImportBatchId
            ) AS PeriodEndDate

        FROM ImportBatch
        WHERE ImportBatch.ImportType = 'SalesHistory'
        ORDER BY ImportBatch.ImportBatchId DESC
        LIMIT 1;
    """)

    result = cursor.fetchone()

    if result:
        (
            import_batch_id,
            import_date,
            file_name,
            status,
            sales_row_count,
            distinct_product_count,
            total_units_sold,
            return_correction_row_count,
            lowest_units_sold,
            highest_units_sold,
            period_start_date,
            period_end_date
        ) = result
        if import_date is not None:
            formatted_import_date = datetime.fromisoformat(import_date).strftime("%m/%d/%Y %H:%M")
        else:
            formatted_import_date = "No Import Date"
        print("\nLatest Sales Batch Summary:")
        print(f"Batch ID: {import_batch_id}")
        print(f"Import Date: {formatted_import_date}")
        print(f"File Name: {file_name}")
        print(f"Status: {status}")
        print()
        print(f"Sales Rows: {sales_row_count}")
        print(f"Distinct Products: {distinct_product_count}")
        print(f"Total Units Sold: {total_units_sold}")
        print(f"Return/Correction Rows: {return_correction_row_count}")
        print(f"Lowest Units Sold: {lowest_units_sold}")
        print(f"Highest Units Sold: {highest_units_sold}")
        print(f"Period Start: {period_start_date}")
        print(f"Period End: {period_end_date}")

    else:
        print("\nNo sales history import batches found.")

# Function to show each product with it qty on hand
def show_product_quantity(connection):
    cursor = connection.cursor()

    cursor.execute("""
        SELECT 
            Product.SKU,
            Product.ProductName,
            InventorySnapshot.QuantityOnHand,
            InventorySnapshot.SnapshotDate
        FROM Product
        JOIN InventorySnapshot
            ON Product.ProductId = InventorySnapshot.ProductId
        LIMIT 10;
    """)

    results = cursor.fetchall()

    print("\nProduct Quantities:")
    print(results)

# Function to show latest inventory snapshot
def show_latest_inventory_snapshot(connection):
    cursor = connection.cursor()

    cursor.execute("""
        SELECT
            Product.SKU,
            Product.ProductName,
            InventorySnapshot.QuantityOnHand,
            ROUND(ProductFinancial.CostPrice, 2) AS CostPrice,
            ROUND(ProductFinancial.RetailPrice, 2) AS RetailPrice,
            ROUND(ProductFinancial.MarginPercent, 2) AS MarginPercent,
            ROUND(ProductFinancial.MarginDollars, 2) AS MarginDollars
        FROM Product
        JOIN InventorySnapshot
            ON Product.ProductId = InventorySnapshot.ProductId
        JOIN ProductFinancial
            ON Product.ProductId = ProductFinancial.ProductId
        WHERE InventorySnapshot.ImportBatchId = (
            SELECT MAX(ImportBatchId)
            FROM ImportBatch
            WHERE ImportType = 'Inventory'
        )
        AND ProductFinancial.ImportBatchId = (
            SELECT MAX(ImportBatchId)
            FROM ImportBatch
            WHERE ImportType = 'Inventory'
        )
        LIMIT 10;            
    """)

    results = cursor.fetchall()

    print("\nLatest Inventory Snapshot:")

    print(
        f"{'SKU':<10} "
        f"{'ProductName':<40} "
        f"{'QTY':>8} "
        f"{'Cost':>10} "
        f"{'Retail':>10} "
        f"{'Margin %':>10} "
        f"{'Margin $':>10}"
    )

    print("-" * 105)

    for row in results:
        sku, product_name, quantity_on_hand, cost_price, retail_price, margin_percent, margin_dollars = row

        print(
            f"{sku:<10} "
            f"{product_name:<40} "
            f"{quantity_on_hand:>8} "
            f"{cost_price:>10.2f} "
            f"{retail_price:>10.2f} "
            f"{margin_percent:>10.2f} "
            f"{margin_dollars:>10.2f}"
        )

# Function for Show Weeks On Hand Report
def show_weeks_on_hand_report(connection):
    cursor = connection.cursor()

    cursor.execute("""
        SELECT
            Product.SKU,
            Product.ProductName,
            InventorySnapshot.QuantityOnHand,
            ROUND(AVG(SalesHistory.UnitsSold), 2) AS AvgWeeklyUnitsSold,
            CASE
                WHEN AVG(SalesHistory.UnitsSold) > 0
                THEN ROUND(InventorySnapshot.QuantityOnHand * 1.0 / AVG(SalesHistory.UnitsSold), 2)
                ELSE NULL
            END AS EstimatedWeeksOnHand
        FROM Product
        JOIN InventorySnapshot
            ON Product.ProductId = InventorySnapshot.ProductId
        JOIN SalesHistory
            ON Product.ProductId = SalesHistory.ProductId
        WHERE InventorySnapshot.ImportBatchId = (
            SELECT MAX(ImportBatchId)
            FROM ImportBatch
            WHERE ImportType = 'Inventory'
        )
        GROUP BY
            Product.ProductId,
            Product.SKU,
            Product.ProductName,
            InventorySnapshot.QuantityOnHand
        HAVING AVG(SalesHistory.UnitsSold) > 0
        ORDER BY EstimatedWeeksOnHand ASC
        LIMIT 20;
    """)

    results = cursor.fetchall()

    print("\nWeeks On Hand Report:")
    print(
        f"{'SKU':<10} "
        f"{'ProductName':<40} "
        f"{'QTY':>8} "
        f"{'Avg Sold/Wk':>12} "
        f"{'Est WOH':>10}"
    )
    print("-" * 90)

    for row in results:
        sku, product_name, quantity_on_hand, avg_weekly_units_sold, estimated_weeks_on_hand = row

        sku = "No SKU" if sku is None else str(sku)
        product_name = "No Product Name" if product_name is None else product_name

        if len(product_name) > 40:
            product_name = product_name[:37] + "..."

        print(
            f"{sku:<10} "
            f"{product_name:<40} "
            f"{quantity_on_hand:>8} "
            f"{avg_weekly_units_sold:>12.2f} "
            f"{estimated_weeks_on_hand:>10.2f}"
        )

# Function to Show Low Weeks on Hand
def show_low_weeks_on_hand(connetion):
    cursor = connetion.cursor()

    cursor.execute("""
        SELECT
            Product.SKU,
            Product.ProductName,
            InventorySnapshot.QuantityOnHand,
            ROUND(AVG(SalesHistory.UnitsSold), 2) AS AvgWeeklyUnitsSold,
            CASE
                WHEN AVG(SalesHistory.UnitsSold) > 0
                THEN ROUND(InventorySnapshot.QuantityOnHand * 1.0 / AVG(SalesHistory.UnitsSold), 2)
                ELSE NULL
            END AS EstimatedWeeksOnHand
        FROM Product
        JOIN InventorySnapshot
            ON Product.ProductId = InventorySnapshot.ProductId
        JOIN SalesHistory
            ON Product.ProductId = SalesHistory.ProductId
        WHERE InventorySnapshot.ImportBatchId = (
            SELECT MAX(ImportBatchId)
            FROM ImportBatch
            WHERE ImportType = 'Inventory'
        )
        GROUP BY
            Product.ProductId,
            Product.SKU,
            Product.ProductName,
            InventorySnapshot.QuantityOnHand
        HAVING AVG(SalesHistory.UnitsSold) > 0
        ORDER BY EstimatedWeeksOnHand ASC
        LIMIT 20;
    """)

    results = cursor.fetchall()

    print("\nWeeks On Hand Report:")
    print(
        f"{'SKU':<10} "
        f"{'ProductName':<40} "
        f"{'QTY':>8} "
        f"{'Avg Sold/Wk':>12} "
        f"{'Est WOH':>10}"
    )
    print("-" * 90)

    for row in results:
        sku, product_name, quantity_on_hand, avg_weekly_units_sold, estimated_weeks_on_hand = row

        sku = "No SKU" if sku is None else str(sku)
        product_name = "No Product Name" if product_name is None else product_name

        if len(product_name) > 40:
            product_name = product_name[:37] + "..."

        print(
            f"{sku:<10} "
            f"{product_name:<40} "
            f"{quantity_on_hand:>8} "
            f"{avg_weekly_units_sold:>12.2f} "
            f"{estimated_weeks_on_hand:>10.2f}"
        )

# Function to Show Inventory Exceptions
def show_inventory_exceptions(connection):
    cursor = connection.cursor()

    cursor.execute("""
        SELECT
            Product.SKU,
            Product.ProductName,
            InventorySnapshot.QuantityOnHand
        FROM Product
        JOIN InventorySnapshot
            ON Product.ProductId = InventorySnapshot.ProductId
        WHERE InventorySnapshot.ImportBatchId = (
            SELECT MAX(ImportBatchId)
            FROM ImportBatch
            WHERE ImportType = 'Inventory'
        )
        AND InventorySnapshot.QuantityOnHand < 0
        ORDER BY InventorySnapshot.QuantityOnHand ASC;
    """)

    results = cursor.fetchall()

    if results:
        print("\nInventory Exceptions")
        print(
            f"{'SKU':<10}"
            f"{'ProductName':<40}"
            f"{'QTY On Hand':>12}"
        )
        print("-" * 62)

        for row in results:
            sku, product_name, quantity_on_hand = row

            sku = "No SKU" if sku is None else str(sku)
            product_name = (
                "No Product Name"
                if product_name is None
                else product_name
            )

            if len(product_name) > 40:
                product_name = product_name[:37] + "..."

            print(
                f"{sku:<10}"
                f"{product_name:<40}"
                f"{quantity_on_hand:>12}"
            )

    else:
        print("\nNo negative inventory exceptions found.")

# Function to Show Zero or Negative stock With Sales
def show_zero_stock_negative_sales(connection):
    cursor = connection.cursor()

    cursor.execute("""
        SELECT
            Product.SKU AS SKU,
            Product.ProductName AS ProductName,
            InventorySnapshot.QuantityOnHand AS QTYOnHand
        FROM
            Product
        JOIN InventorySnapshot
        ON Product.ProductId = InventorySnapshot.ProductId
        HAVING QTYOnHand < 0
        ORDER BY QTYOnHand ASC; 
    """)

# Function to Get Sales History
def get_sales_history(connection):
    cursor = connection.cursor()

    cursor.execute("""
        SELECT
            Product.SKU,
            Product.ProductName,
            InventorySnapshot.QuantityOnHand,
            SalesHistory.UnitsSold,
            CASE
                WHEN SalesHistory.UnitsSold > 0
                THEN ROUND(InventorySnapshot.QuantityOnHand * 1.0 / SalesHistory.UnitsSold, 2)
                ELSE NULL
            END AS EstimatedWeeksOnHand
        FROM Product
        JOIN InventorySnapshot
            ON Product.ProductId = InventorySnapshot.ProductId
        JOIN SalesHistory
            ON Product.ProductId = SalesHistory.ProductId
        WHERE InventorySnapshot.ImportBatchId = (
            SELECT MAX(ImportBatchId)
            FROM ImportBatch
            WHERE ImportType = 'Inventory'
        )
        AND SalesHistory.ImportBatchId = (
            SELECT MAX(ImportBatchId)
            FROM ImportBatch
            WHERE ImportType = 'SalesHistory'
        )
        AND SalesHistory.UnitsSold > 0
        ORDER BY EstimatedWeeksOnHand ASC
        LIMIT 20;
    """)

    results = cursor.fetchall()

    print("\nLatest Estimated Weeks on Hand:")
    print(f"{'SKU':<10} {'ProductName':<35} {'QtyOnHand':>10} {'UnitsSold':>10} {'EstWOH':>10}")
    print("-" * 80)

    for row in results:
        sku, product_name, qty_on_hand, units_sold, estimated_woh = row

        print(f"{sku:<10} {product_name:<35} {qty_on_hand:>10} {units_sold:>10} {estimated_woh:>10}")

# Main Function
def main():
    
    connection = create_connection()

    #show_tables(connection)
    #show_import_batch_count(connection)
    #show_latest_import_batch_id(connection)
    #show_product_count(connection)
    #show_duplicate_skus(connection)
    #show_products_without_sales_history(connection)
    #show_products_without_sku(connection)
    #show_products_not_in_pos(connection)
    #show_products_in_pos(connection)
    #show_latest_inventory_batch_summary(connection)
    #show_latest_sales_batch_summary(connection)
    #show_weeks_on_hand_report(connection)
    #show_low_weeks_on_hand(connection)
    show_inventory_exceptions(connection)
    #show_product_quantity(connection)
    #show_latest_inventory_snapshot(connection)
    #get_sales_history(connection)

    connection.close()

if __name__ == "__main__":
    main()