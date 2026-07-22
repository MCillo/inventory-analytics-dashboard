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
        #print("\nConnection Succesful")
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
        FROM ImportBatch;
    """)

    import_batch_count = cursor.fetchone()[0]

    print("\nBatch Count")
    print("-" * 20)
    print(f"Total Import Batches: {import_batch_count}")

    cursor.execute("""
        SELECT
            ImportBatchId,
            ImportDate,
            ReportDate,
            FileName,
            ImportType,
            Status
        FROM ImportBatch
        ORDER BY ImportBatchId DESC
        LIMIT 10;
    """)

    recent_batches = cursor.fetchall()

    print("\nRecent Import History")
    print(
        f"{'Batch ID':<10}"
        f"{'Import Type':<16}"
        f"{'Report Date':<20}"
        f"{'Status':<12}"
        f"{'File Name'}"
    )

    print("-" * 80)

    for batch in recent_batches:
        (
            import_batch_id,
            import_date,
            report_date,
            file_name,
            import_type,
            status
        ) = batch

        print(
            f"{import_batch_id:<10}"
            f"{import_type:<16}"
            f"{report_date:<20}"
            f"{status:<12}"
            f"{file_name}"
        )

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
    import_batch_id, import_type, status = results
    print(f"{'Import Batch Id':<20} {'Import Type':<25} {'Status':<15}")
    print("-" * 60)
    print(f"{import_batch_id:<20} {import_type:<25} {status:<15}")
    #print(results)

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
    print("-" * 25)
    print(f"{product_count:>15}")

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
            print(f"{row:<45}")
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


# Function to show latest Inventory Batch Summary
def show_latest_inventory_batch_summary(connection):
    cursor = connection.cursor()

    cursor.execute("""
        SELECT
            ImportBatch.ImportBatchId,
            ImportBatch.ImportDate,
            ImportBatch.ReportDate,
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
            report_date,
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

        if report_date is not None:
            formatted_report_date = datetime.fromisoformat(report_date).strftime("%d/%m/%Y %H:%M")
        else:
            formatted_report_date = "No Report Date"

        print("\nLatest Inventory Batch Summary:")
        print(f"Batch ID: {import_batch_id}")
        print(f"Import Date: {formatted_import_date}")
        print(f"Report Date: {formatted_report_date}")
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
    snapshot_date = results[0][3]

    print("\nProduct Quantities:")
    print(f"Snapshot Date: {snapshot_date}")
    print(f"{'SKU':<10} {'Product Name':<35} {'Quantity on Hand':<15}")
    print("-" * 75)

    for row in results:
        sku, product_name, quantity_on_hand, snapshot_date = row

        sku = "No SKU" if sku is None else str(sku)
        product_name = "No Product Name" if product_name is None else product_name
        quantity_on_hand = "No Quantity on Hand" if quantity_on_hand is None else str(quantity_on_hand)

        if len(product_name) > 35:
            product_name = product_name[:32] + "..."

        print(f"{sku:<10} {product_name:<35} {quantity_on_hand:>15}")
    

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

    print("\nLow Weeks On Hand Report:")
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
        print("\nNegative Sales")
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
        print("\nNo Negative Sales Found.")

# Function to show actively stocked skus
def show_active_stocked_skus(connection):
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
        AND InventorySnapshot.QuantityOnHand > 0
        ORDER BY InventorySnapshot.QuantityOnHand DESC; 
    """)

    results = cursor.fetchall()

    if results:
        active_sku_count = len(results)
        total_qty_on_hand = sum(row[2] for row in results)

        print("\nActive SKU's")
        print(f"Active Stocked SKUs Returned: {active_sku_count}")
        print(f"Total Quantity On Hand: {total_qty_on_hand}")
        print()

        print(
            f"{'SKU':<10} "
            f"{'ProductName':<40} "
            f"{'QTY On Hand':>12}"
        )
        print("-" * 68)

        for row in results:
            sku, product_name, quantity_on_hand = row

            sku = "No SKU" if sku is None else str(sku)
            product_name = "No Product Name" if product_name is None else product_name

            if len(product_name) > 40:
                product_name = product_name[:37] + "..."

            print(
                f"{sku:<10} "
                f"{product_name:<40} "
                f"{quantity_on_hand:>12}"
            )

    else:
        print("\nNo active stocked SKUs found.")

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

        if len(product_name) > 35:
            product_name = product_name[:32] + "..."

        print(f"{sku:<10} {product_name:<35} {qty_on_hand:>10} {units_sold:>10} {estimated_woh:>10}")

# Function to Get Latest Sales History
def get_latest_sales_history(connection):
    cursor = connection.cursor()

    cursor.execute("""
        SELECT
            Product.SKU,
            Product.ProductName,
            SalesHistory.UnitsSold,
            SalesHistory.PeriodStartDate,
            SalesHistory.PeriodEndDate
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
        ORDER BY UnitsSold DESC
        ;
    """)

    results = cursor.fetchall()

    print("\nLatest Sales History:")

    if results:
        first_row = results[0]
        period_start_date = first_row[3]
        period_end_date = first_row[4]

        formatted_start_date = datetime.fromisoformat(period_start_date).strftime("%B %d")
        formatted_end_date = datetime.fromisoformat(period_end_date).strftime("%d, %Y")

        print(f"Sales Period: Week of {formatted_start_date} - {formatted_end_date}")
        print()

        print(
            f"{'SKU':<10}"
            f"{'Product Name':<40}"
            f"{'Units Sold':>10}"
        )
        print("-" * 60)

        for row in results:
            sku, product_name, units_sold, period_start_date, period_end_date = row

            sku = "No SKU" if sku is None else str(sku)
            product_name = "No Product Name" if product_name is None else product_name

            if len(product_name) > 35:
                product_name = product_name[:32] + "..."

            print(
                f"{sku:<10}"
                f"{product_name:<40}"
                f"{units_sold:>10}"
            )

    else:
        print("No sales history records found.")

# Function to Show Latest Product Financials
def show_latest_product_financials(connection):
    cursor = connection.cursor()

    cursor.execute("""
        SELECT
            Product.SKU,
            Product.ProductName,
            ProductFinancial.CostPrice,
            ProductFinancial.RetailPrice,
            ProductFinancial.MarginDollars,
            ProductFinancial.MarginPercent,
            ProductFinancial.EffectiveDate
        FROM
            Product
        JOIN ProductFinancial
            ON ProductFinancial.ProductId = Product.ProductId
        WHERE ProductFinancial.ImportBatchId = (
            SELECT MAX(ImportBatchId)
            FROM ImportBatch
            WHERE ImportType = 'Inventory'
        )
        ORDER BY SKU ASC
        LIMIT 15;
    """)

    results = cursor.fetchall()

    print("\nLatest Product Financials.")

    if results:
        first_row = results[0]
        effective_date = first_row[6]

        formatted_effective_date = datetime.fromisoformat(effective_date).strftime("%B %d")

        print(f"Financial Information as of: {formatted_effective_date}")
        print()

        print(
            f"{'SKU':<10}"
            f"{'Product Name':<40}"
            f"{'Cost':>12}"
            f"{'Retail':>12}"
            f"{'Margin Dollars':>18}"
            f"{'Margin Percent':>18}"

        )
        print("-" * 110)

        for row in results:
            sku, product_name, cost_price, retail_price, margin_dollars, margin_percent, effective_date = row

            sku = "No SKU" if sku is None else str(sku)
            product_name = "No Product Name" if product_name is None else product_name
            cost_price = "N/A" if cost_price is None else f"$ {cost_price:.2f}"
            retail_price = "N/A" if retail_price is None else f"$ {retail_price:.2f}"
            margin_dollars = "N/A" if margin_dollars is None else f"$ {margin_dollars:.2f}"
            margin_percent = "N/A" if margin_percent is None else f"{margin_percent:.2f} %"

            if len(product_name) > 35:
                product_name = product_name[:32] + "..."

            print(
                f"{sku:<10}"
                f"{product_name:<40}"
                f"{cost_price:>12}"
                f"{retail_price:>12}"
                f"{margin_dollars:>18}"
                f"{margin_percent:>18}"
            )

    else:
        print("No Financial History Records Found.")

# Function to Show Top 300 by Profit
def show_top_300_by_profit(connection):
    cursor = connection.cursor()

    cursor.execute("""
        SELECT
            Product.SKU,
            Product.ProductName,
            SalesHistory.UnitsSold,
            ProductFinancial.MarginDollars,
            SalesHistory.UnitsSold * ProductFinancial.MarginDollars AS TotalProfit,
            SalesHistory.PeriodStartDate,
            SalesHistory.PeriodEndDate
        FROM
            Product
        JOIN SalesHistory
            ON SalesHistory.ProductId = Product.ProductId
        JOIN ProductFinancial
            ON ProductFinancial.ProductId = Product.ProductId
         WHERE SalesHistory.ImportBatchId = (
            SELECT MAX(ImportBatchId)
            FROM ImportBatch
            WHERE ImportType = 'SalesHistory'
        )
        AND ProductFinancial.ImportBatchId = (
            SELECT MAX(ImportBatchId)
            FROM ImportBatch
            WHERE ImportType = 'Inventory'
        )
        ORDER BY TotalProfit DESC
        LIMIT 20
        ;
    """)

    results = cursor.fetchall()

    #print("\nTop 300 Products by Profit Dollars")

    if results:
        first_row = results[0]
        period_start_date = first_row[5]
        period_end_date = first_row[6]
        formatted_start_date = datetime.fromisoformat(period_start_date).strftime("%B %d")
        formatted_end_date = datetime.fromisoformat(period_end_date).strftime("%d, %Y")

        print(f"\nTop 300 by Profit for the week of: {formatted_start_date} - {formatted_end_date}")
        print()

        print(
            f"{'SKU':<10}"
            f"{'Product Name':<40}"
            f"{'Units Sold':>12}"
            f"{'Margin Dollars Per Unit':>25}"
            f"{'Total Profit':>20}"

        )
        print("-" * 107)

        for row in results:
            sku, product_name, units_sold, margin_dollars, total_profit, period_start_date, period_end_date = row

            sku = "No SKU" if sku is None else str(sku)
            product_name = "No Product Name" if product_name is None else product_name
            units_sold = "No Units Sold" if units_sold is None else units_sold
            margin_dollars = "N/A" if margin_dollars is None else f"$ {margin_dollars:.2f}"
            total_profit = "N/A" if total_profit is None else f"$ {total_profit:.2f}"

            if len(product_name) > 35:
                product_name = product_name[:32] + "..."

            print(
                f"{sku:<10}"
                f"{product_name:<40}"
                f"{units_sold:>12}"
                f"{margin_dollars:>25}"
                f"{total_profit:>20}"
            )

    else:
        print("No Financial History Records Found.")

# Function to Show Top 300 by Units Sold
def show_top_300_by_units(connection):
    cursor = connection.cursor()

    cursor.execute("""
        SELECT
            Product.SKU,
            Product.ProductName,
            SalesHistory.UnitsSold,
            SalesHistory.PeriodStartDate,
            SalesHistory.PeriodEndDate
        FROM
            Product
        JOIN SalesHistory
            ON SalesHistory.ProductId = Product.ProductId
        JOIN ProductFinancial
            ON ProductFinancial.ProductId = Product.ProductId
         WHERE SalesHistory.ImportBatchId = (
            SELECT MAX(ImportBatchId)
            FROM ImportBatch
            WHERE ImportType = 'SalesHistory'
        )
        AND ProductFinancial.ImportBatchId = (
            SELECT MAX(ImportBatchId)
            FROM ImportBatch
            WHERE ImportType = 'Inventory'
        )
        ORDER BY UnitsSold DESC
        LIMIT 20
        ;
    """)

    results = cursor.fetchall()

    print("\nTop 300 Products by Units")

    if results:
        first_row = results[0]
        period_start_date = first_row[3]
        period_end_date = first_row[4]
        formatted_start_date = datetime.fromisoformat(period_start_date).strftime("%B %d")
        formatted_end_date = datetime.fromisoformat(period_end_date).strftime("%d, %Y")

        print(f"Top 300 by Units Sold for the week of: {formatted_start_date} - {formatted_end_date}")
        print()

        print(
            f"{'SKU':<10}"
            f"{'Product Name':<40}"
            f"{'Units Sold':>12}"

        )
        print("-" * 62)

        for row in results:
            sku, product_name, units_sold, period_start_date, period_end_date = row

            sku = "No SKU" if sku is None else str(sku)
            product_name = "No Product Name" if product_name is None else product_name
            units_sold = "No Units Sold" if units_sold is None else units_sold

            if len(product_name) > 35:
                product_name = product_name[:32] + "..."

            print(
                f"{sku:<10}"
                f"{product_name:<40}"
                f"{units_sold:>12}"
            )

    else:
        print("No Financial History Records Found.")

# Function to Show Low Margin Items
def show_low_margin_items(connection):
    cursor = connection.cursor()

    cursor.execute("""
        SELECT
            Product.Sku,
            Product.ProductName,
            ProductFinancial.MarginPercent
        FROM
            Product
        JOIN ProductFinancial 
            ON Product.ProductId = ProductFinancial.ProductId
        ORDER BY MarginPercent ASC
        LIMIT 30
        ;
    """)

    results = cursor.fetchall()

    print("\nLow Margin Items")
    print()
    print(
        f"{'SKU':<10}"
        f"{'Product Name':<45}"
        f"{'Margin Percent':>15}"
    )

    print("-" * 70)

    for row in results:
        sku, product_name, margin_percent = row

        sku = "No SKU" if sku is None else str(sku)
        product_name = "No Product Name" if product_name is None else product_name
        margin_percent = "N/A" if margin_percent is None else f"{margin_percent:.2f} %"

        if len(product_name) > 35:
            product_name = product_name[:32] + "..."

        print(
            f"{sku:<10}"
            f"{product_name:<45}"
            f"{margin_percent:>15}"
        )


# Function to Show Price or Cost Changes
def show_price_changes(connection):
    cursor = connection.cursor()
    
    cursor.execute("""
        WITH LatestInventoryBatch AS (
            SELECT MAX(ImportBatchId) AS LatestBatchId
            FROM ImportBatch
            WHERE ImportType = 'Inventory'
        ),

        PreviousInventoryBatch AS (
            SELECT MAX(ImportBatchId) AS PreviousBatchId
            FROM ImportBatch
            WHERE ImportType = 'Inventory'
              AND ImportBatchId < (
                  SELECT LatestBatchId
                  FROM LatestInventoryBatch
              )
        )

        SELECT
            Product.SKU,
            Product.ProductName,

            ROUND(PreviousFinancial.CostPrice, 2) AS PreviousCost,
            ROUND(LatestFinancial.CostPrice, 2) AS LatestCost,
            ROUND(LatestFinancial.CostPrice - PreviousFinancial.CostPrice, 2) AS CostChange,

            ROUND(PreviousFinancial.RetailPrice, 2) AS PreviousRetail,
            ROUND(LatestFinancial.RetailPrice, 2) AS LatestRetail,
            ROUND(LatestFinancial.RetailPrice - PreviousFinancial.RetailPrice, 2) AS RetailChange,

            ROUND(PreviousFinancial.MarginPercent, 2) AS PreviousMarginPercent,
            ROUND(LatestFinancial.MarginPercent, 2) AS LatestMarginPercent,
            ROUND(LatestFinancial.MarginPercent - PreviousFinancial.MarginPercent, 2) AS MarginPercentChange

        FROM Product

        JOIN ProductFinancial AS LatestFinancial
            ON Product.ProductId = LatestFinancial.ProductId

        JOIN ProductFinancial AS PreviousFinancial
            ON Product.ProductId = PreviousFinancial.ProductId

        WHERE LatestFinancial.ImportBatchId = (
            SELECT LatestBatchId
            FROM LatestInventoryBatch
        )
        AND PreviousFinancial.ImportBatchId = (
            SELECT PreviousBatchId
            FROM PreviousInventoryBatch
        )
        AND (
            LatestFinancial.CostPrice != PreviousFinancial.CostPrice
            OR LatestFinancial.RetailPrice != PreviousFinancial.RetailPrice
            OR LatestFinancial.MarginPercent != PreviousFinancial.MarginPercent
            OR LatestFinancial.MarginDollars != PreviousFinancial.MarginDollars
        )

        ORDER BY ABS(CostChange) DESC
        LIMIT 20;
    """)

    results = cursor.fetchall()

    if results:
        print("\nPrice or Cost Changes:")
        print(
            f"{'SKU':<10} "
            f"{'ProductName':<35} "
            f"{'Old Cost':>10} "
            f"{'New Cost':>10} "
            f"{'Cost +/-':>10} "
            f"{'Old Retail':>12} "
            f"{'New Retail':>12} "
            f"{'Retail +/-':>12} "
            f"{'Margin +/-':>12}"
        )
        print("-" * 135)

        for row in results:
            (
                sku,
                product_name,
                previous_cost,
                latest_cost,
                cost_change,
                previous_retail,
                latest_retail,
                retail_change,
                previous_margin_percent,
                latest_margin_percent,
                margin_percent_change
            ) = row

            sku = "No SKU" if sku is None else str(sku)
            product_name = "No Product Name" if product_name is None else product_name

            if len(product_name) > 35:
                product_name = product_name[:32] + "..."

            print(
                f"{sku:<10} "
                f"{product_name:<35} "
                f"{previous_cost:>10.2f} "
                f"{latest_cost:>10.2f} "
                f"{cost_change:>10.2f} "
                f"{previous_retail:>12.2f} "
                f"{latest_retail:>12.2f} "
                f"{retail_change:>12.2f} "
                f"{margin_percent_change:>12.2f}"
            )

    else:
        print("\nNo price or cost changes found.")


# Main Function
def main():
    
    connection = create_connection()

    # Query Foundation and Sanity Checks
    
    #show_tables(connection)
    #show_import_batch_count(connection)
    #show_latest_import_batch_id(connection)
    #show_product_count(connection)

    # Import Quality and Data Validation Queries
    
    #show_duplicate_skus(connection)
    #show_products_without_sales_history(connection)
    #show_products_without_sku(connection)
    #show_products_not_in_pos(connection)
    #show_latest_inventory_batch_summary(connection)
    #show_latest_sales_batch_summary(connection)

    # Inventory and Stock Health Reports

    #show_latest_inventory_snapshot(connection)
    #show_weeks_on_hand_report(connection)
    #show_low_weeks_on_hand(connection)
    #show_inventory_exceptions(connection)
    #show_zero_stock_negative_sales(connection)
    #show_active_stocked_skus(connection)

    # Sales History Reports
    
    #show_product_quantity(connection)
    #get_sales_history(connection) #same as get_latest_sales_history but includes QTY on Hand and EstWOH
    #get_latest_sales_history(connection)

    # Financial Performance Reports
    
    #show_latest_product_financials(connection)
    #show_top_300_by_profit(connection)
    #show_top_300_by_units(connection)
    show_low_margin_items(connection)

    connection.close()

if __name__ == "__main__":
    main()