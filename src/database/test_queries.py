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
            ProductFinancial.CostPrice,
            ProductFinancial.RetailPrice,
            ProductFinancial.MarginPercent,
            ProductFinancial.MarginDollars
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

    print("\nProduct Quantities:")
    for row in results:
        print(row)

# Main Function
def main():
    
    connection = create_connection()

    show_product_quantity(connection)
    show_latest_inventory_snapshot(connection)

    connection.close()

if __name__ == "__main__":
    main()