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
    for row in results:
        print(row)

# Function to show latest inventory snapshot
def show_latest_inventory_snapshot(connection):
    cursor = connection.cursor()

    cursor.execute("""
        SELECT
            Product.SKU,
            Product.ProductName,
            InventorySnapshot.QuantityOnHand,
            ROUND(ProductFinancial.CostPrice, 2),
            ROUND(ProductFinancial.RetailPrice, 2),
            ROUND(ProductFinancial.MarginPercent, 2),
            ROUND(ProductFinancial.MarginDollars, 2)
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
    for row in results:
        print(row)

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
    print(f"{'SKU':<10} {'ProductName':<35} {'QtyOnHand':<10} {'UnitsSold':<10} {'EstWOH':<10}")
    print("-" * 80)

    for row in results:
        sku, product_name, qty_on_hand, units_sold, estimated_woh = row

        print(f"{sku:<10} {product_name:<35} {qty_on_hand:<10} {units_sold:<10} {estimated_woh:<10}")

# Main Function
def main():
    
    connection = create_connection()

    show_product_quantity(connection)
    show_latest_inventory_snapshot(connection)
    get_sales_history(connection)

    connection.close()

if __name__ == "__main__":
    main()