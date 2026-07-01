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
    show_product_count(connection)
    #show_product_quantity(connection)
    #show_latest_inventory_snapshot(connection)
    #get_sales_history(connection)

    connection.close()

if __name__ == "__main__":
    main()